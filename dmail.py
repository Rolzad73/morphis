# Copyright (c) 2014-2015  Sam Maloney.
# License: GPL v2.

import llog

import asyncio
from datetime import datetime
import json
import logging
import os
import struct
import time

import base58
import brute
import chord
import db
import mbase32
import multipart as mp
import mutil
import dhgroup14
import enc
import sshtype
import rsakey

log = logging.getLogger(__name__)

_dh_method_name = "mdh-v1"

class DmailException(Exception):
    pass

class DmailSite(object):
    def __init__(self, prev=None):
        self.root = json.loads(prev) if prev else {}

        self.dh = None

    def generate_target(self):
        target = os.urandom(chord.NODE_ID_BYTES)

        if log.isEnabledFor(logging.INFO):
            log.info("dmail target=[{}].".format(mbase32.encode(target)))

        self.root["target"] = mbase32.encode(target)

    def generate_ss(self):
        self.dh = dh = dhgroup14.DhGroup14()
        dh.generate_x()
        dh.generate_e()

        if log.isEnabledFor(logging.INFO):
            log.info("dmail e=[{}].".format(dh.e))

        self.root["ssm"] = _dh_method_name
        self.root["sse"] = base58.encode(sshtype.encodeMpint(dh.e))

    def generate(self):
        self.generate_target()
        self.generate_ss()

    def export(self):
        return json.dumps(self.root).encode()

class DmailWrapper(object):
    def __init__(self, buf=None, offset=0):
        self.version = 1
        self.ssm = None
        self.sse = None
        self.ssf = None

        self.signature = None

        self.data = None
        self.data_len = None
        self.data_enc = None

        if buf is not None:
            self.parse_from(buf, offset)

    def encode(self, obuf=None):
        buf = obuf if obuf else bytearray()
        buf += struct.pack(">L", self.version)
        buf += sshtype.encodeString(self.ssm)
        buf += sshtype.encodeMpint(self.sse)
        buf += sshtype.encodeMpint(self.ssf)

        buf += sshtype.encodeBinary(self.signature)

        buf += struct.pack(">L", self.data_len)
        buf += self.data_enc

    def parse_from(self, buf, idx):
        self.version = struct.unpack_from(">L", buf, idx)[0]
        idx += 4
        idx, self.ssm = sshtype.parse_string_from(buf, idx)
        idx, self.sse = sshtype.parse_mpint_from(buf, idx)
        idx, self.ssf = sshtype.parse_mpint_from(buf, idx)

        idx, self.signature = sshtype.parse_binary_from(buf, idx)

        self.data_len = struct.unpack_from(">L", buf, idx)[0]
        idx += 4

        self.data_enc = buf[idx:]

        return idx

class Dmail(object):
    def __init__(self, buf=None, offset=0, length=None):
        self.version = 1
        self.sender_pubkey = None
        self.subject = None
        self.date = None
        self.parts = [] # [DmailPart].

        if buf:
            self.parse_from(buf, offset, length)

    def encode(self, obuf=None):
        buf = obuf if obuf else bytearray()

        buf += struct.pack(">L", self.version)
        buf += sshtype.encodeBinary(self.sender_pubkey)
        buf += sshtype.encodeString(self.subject)
        buf += sshtype.encodeString(self.date)

        for part in self.parts:
            part.encode(buf)

        return buf

    def parse_from(self, buf, idx, length=None):
        if not length:
            length = len(buf)

        self.version = struct.unpack_from(">L", buf, idx)[0]
        idx += 4
        idx, self.sender_pubkey = sshtype.parse_binary_from(buf, idx)
        idx, self.subject = sshtype.parse_string_from(buf, idx)
        idx, self.date = sshtype.parse_string_from(buf, idx)

        while idx < length:
            part = DmailPart()
            idx = part.parse_from(buf, idx)
            self.parts.append(part)

        return idx

class DmailPart(object):
    def __init__(self):
        self.mime_type = None
        self.data = None

    def encode(self, obuf=None):
        buf = obuf if obuf else bytearray()
        buf += sshtype.encodeString(self.mime_type)
        buf += sshtype.encodeBinary(self.data)
        return buf

    def parse_from(self, buf, idx):
        idx, self.mime_type = sshtype.parse_string_from(buf, idx)
        idx, self.data = sshtype.parse_binary_from(buf, idx)
        return idx

class DmailEngine(object):
    def __init__(self, task_engine, db):
        self.task_engine = task_engine
        self.db = db
        self.loop = task_engine.loop

    @asyncio.coroutine
    def generate_dmail_address(self, prefix=None, difficulty=20):
        assert type(difficulty) is int

        if log.isEnabledFor(logging.INFO):
            log.info("Generating dmail address (prefix=[{}].".format(prefix))

        def threadcall():
            if prefix:
                if log.isEnabledFor(logging.INFO):
                    log.info("Brute force generating key with prefix [{}]."\
                        .format(prefix))
                return brute.generate_key(prefix)
            else:
                return rsakey.RsaKey.generate(bits=4096)

        privkey = yield from self.loop.run_in_executor(None, threadcall)

        dms = DmailSite()
        dms.generate()
        dms.root["difficulty"] = difficulty

        data_key = None
        def key_callback(value):
            nonlocal data_key
            data_key = value

        log.info("Uploading dmail site.")

        total_storing = 0
        retry = 0
        while True:
            storing_nodes = yield from\
                self.task_engine.send_store_updateable_key(\
                    dms.export(), privkey, version=int(time.time()*1000),\
                    store_key=True, key_callback=key_callback,\
                    retry_factor=retry * 20)

            total_storing += storing_nodes

            if total_storing >= 3:
                break

            if retry > 32:
                break
            elif retry > 3:
                yield from asyncio.sleep(1)

            retry += 1

        def dbcall():
            with self.db.open_session() as sess:
                dmailaddress = db.DmailAddress()
                dmailaddress.site_key = data_key
                dmailaddress.site_privatekey = privkey._encode_key()

                dmailkey = db.DmailKey()
                dmailkey.x = sshtype.encodeMpint(dms.dh.x)
                dmailkey.target_key = mbase32.decode(dms.root["target"])
                dmailkey.difficulty = difficulty

                dmailaddress.keys.append(dmailkey)

                sess.add(dmailaddress)
                sess.commit()

        log.info("Saving dmail site to the database.")

        yield from self.loop.run_in_executor(None, dbcall)

        return privkey, data_key, dms, total_storing

    @asyncio.coroutine
    def send_dmail_text(self, subject, message_text):
        if message_text.startswith("from: "):
            p0 = message_text.find('\n')
            m_from_asymkey = rsakey.RsaKey(\
                privdata=base58.decode(message_text[6:p0]))
            p0 += 1
        else:
            p0 = 0
            m_from_asymkey = None

        m_dest_ids = []
        while message_text.startswith("to: ", p0):
            p1 = message_text.find('\n')
            m_dest_enc = message_text[p0+4:p1]
            m_dest_id, sig_bits = mutil.decode_key(m_dest_enc)
            m_dest_ids.append((m_dest_enc, m_dest_id, sig_bits))
            p0 = p1 + 1

        date = datetime.today()

        if message_text[p0] == '\n':
            p0 += 1

        message_text = message_text[p0:]

        storing_nodes = yield from self.send_dmail(\
            m_from_asymkey, m_dest_ids, subject, date, message_text)

        return storing_nodes

    @asyncio.coroutine
    def send_dmail(self, from_asymkey, recipients, subject, date,\
            message_text):
        assert from_asymkey is None or type(from_asymkey) is rsakey.RsaKey
        assert type(recipients) is list, type(recipients)
        assert not date or type(date) is datetime

        if type(message_text) is str:
            message_text = message_text.encode()

        if not date:
            date = datetime.today()

        dmail = Dmail()
        dmail.sender_pubkey = from_asymkey.asbytes() if from_asymkey else b""
        dmail.subject = subject
        dmail.date = date.isoformat()

        if message_text:
            part = DmailPart()
            part.mime_type = "text/plain"
            part.data = message_text
            dmail.parts.append(part)

        storing_nodes =\
            yield from self._send_dmail(dmail, from_asymkey, recipients)

        return storing_nodes

    @asyncio.coroutine
    def _send_dmail(self, dmail, from_asymkey, recipients):
        assert type(dmail) is Dmail, type(dmail)

        if len(recipients) == 0:
            raise DmailException("No recipients were specified.")

        if log.isEnabledFor(logging.INFO):
            log.info("len(recipients)=[{}].".format(len(recipients)))

        dmail_bytes = dmail.encode()

        recipients = yield from self.fetch_recipient_dmail_sites(recipients)

        storing_nodes = 0

        for recipient in recipients:
            if recipient.root["ssm"] != _dh_method_name:
                raise DmailException("Unsupported ss method [{}]."\
                    .format(recipient.root["ssm"]))

            storing_nodes =\
                yield from self.__send_dmail(from_asymkey, recipient, dmail)

        return storing_nodes

    @asyncio.coroutine
    def scan_dmail_address(self, addr, significant_bits, key_callback=None):
        addr_enc = mbase32.encode(addr)

        if log.isEnabledFor(logging.INFO):
            log.info("Scanning dmail [{}].".format(addr_enc))

        def dbcall():
            with self.db.open_session() as sess:
                q = sess.query(db.DmailAddress)\
                    .filter(db.DmailAddress.site_key == addr)

                dmail_address = q.first()
                if dmail_address:
                    dmail_address.keys
                    sess.expunge_all()

                return dmail_address

        dmail_address = yield from self.loop.run_in_executor(None, dbcall)

        if dmail_address:
            log.info("Found DmailAddress locally, using local settings.")

            target = dmail_address.keys[0].target_key
            significant_bits = dmail_address.keys[0].difficulty
        else:
            log.info("DmailAddress not found locally, fetching settings from"\
                " the network.")

            dsites = yield from\
                self.fetch_recipient_dmail_sites(\
                    [(addr_enc, addr, significant_bits)])

            if not dsites:
                raise DmailException("Dmail site not found.")

            dsite = dsites[0]

            target = dsite.root["target"]
            significant_bits = dsite.root["difficulty"]

            target = mbase32.decode(target)

        start = target

        while True:
            data_rw = yield from self.task_engine.send_find_key(\
                start, target_key=target, significant_bits=significant_bits,\
                retry_factor=100)

            key = data_rw.data_key

            if not key:
                break

            if log.isEnabledFor(logging.INFO):
                log.info("Found dmail key: [{}].".format(mbase32.encode(key)))

            if key_callback:
                key_callback(key)

            start = key

    @asyncio.coroutine
    def fetch_dmail(self, key, x=None, target_key=None):
        data_rw = yield from self.task_engine.send_get_targeted_data(key)

        data = data_rw.data

        if not data:
            return None, None
        if not x:
            return data, None

        tb = mp.TargetedBlock(data)

        if target_key:
            if tb.target_key != target_key:
                tb_tid_enc = mbase32.encode(tb.target_key)
                tid_enc = mbase32.encode(target_key)
                raise DmailException(\
                    "TargetedBlock->target_key [{}] does not match request"\
                    " [{}]."\
                        .format(tb_tid_enc, tid_enc))

        dw = DmailWrapper(tb.buf, mp.TargetedBlock.BLOCK_OFFSET)

        if dw.ssm != "mdh-v1":
            raise DmailException(\
                "Unrecognized key exchange method in dmail [{}]."\
                    .format(dw.ssm))

        kex = dhgroup14.DhGroup14()
        kex.x = x
        kex.generate_e()
        kex.f = dw.ssf

        if dw.sse != kex.e:
            raise DmailException(\
                "Dmail [{}] is encrypted with a different e [{}] than"\
                " the specified x resulted in [{}]."\
                    .format(mbase32.encode(data_rw.data_key), dw.sse, kex.e))

        kex.calculate_k()

        key = self._generate_encryption_key(tb.target_key, kex.k)

        data = enc.decrypt_data_block(dw.data_enc, key)

        if not data:
            raise DmailException("Dmail data was empty.")

        dmail = Dmail(data, 0, dw.data_len)

        if dw.signature:
            signature = dw.signature
            pubkey = rsakey.RsaKey(dmail.sender_pubkey)
            valid_sig = pubkey.verify_rsassa_pss_sig(dw.data_enc, signature)

            return dmail, valid_sig
        else:
            return dmail, False

    def _generate_encryption_key(self, target_key, k):
        return enc.generate_ID(\
            b"The life forms running github are more retarded than any retard!"\
            + target_key + sshtype.encodeMpint(k)\
            + b"https://github.com/nixxquality/WebMConverter/commit/"\
            + b"c1ac0baac06fa7175677a4a1bf65860a84708d67")

    @asyncio.coroutine
    def __send_dmail(self, from_asymkey, recipient, dmail):
        assert type(recipient) is DmailSite

        root = recipient.root
        sse = sshtype.parseMpint(base58.decode(root["sse"]))[1]
        target = root["target"]
        difficulty = root["difficulty"]

        dh = dhgroup14.DhGroup14()
        dh.generate_x()
        dh.generate_e()
        dh.f = sse

        k = dh.calculate_k()

        target_key = mbase32.decode(target)

        key = self._generate_encryption_key(target_key, k)
        dmail_bytes = dmail.encode()

        m, r = enc.encrypt_data_block(dmail_bytes, key)
        if m:
            if r:
                m = m + r
        else:
            m = r

        dw = DmailWrapper()
        dw.ssm = _dh_method_name
        dw.sse = sse
        dw.ssf = dh.e

        if from_asymkey:
            dw.signature = from_asymkey.calc_rsassa_pss_sig(m)
        else:
            dw.signature = b''

        dw.data_len = len(dmail_bytes)
        dw.data_enc = m

        tb = mp.TargetedBlock()
        tb.target_key = target_key
        tb.noonce = int(0).to_bytes(64, "big")
        tb.block = dw

        tb_data = tb.encode()
        tb_header = tb_data[:mp.TargetedBlock.BLOCK_OFFSET]

        if log.isEnabledFor(logging.INFO):
            log.info(\
                "Attempting work on dmail (target=[{}], difficulty=[{}])."\
                    .format(target, difficulty))

        def threadcall():
            return brute.generate_targeted_block(\
                target_key, difficulty, tb_header,\
                mp.TargetedBlock.NOONCE_OFFSET,\
                mp.TargetedBlock.NOONCE_SIZE)

        noonce_bytes = yield from self.loop.run_in_executor(None, threadcall)

        if log.isEnabledFor(logging.INFO):
            log.info("Work found noonce [{}].".format(noonce_bytes))

        mp.TargetedBlock.set_noonce(tb_data, noonce_bytes)

        if log.isEnabledFor(logging.INFO):
            mp.TargetedBlock.set_noonce(tb_header, noonce_bytes)
            log.info("hash=[{}]."\
                .format(mbase32.encode(enc.generate_ID(tb_header))))

        key = None

        def key_callback(val):
            nonlocal key
            key = val

        log.info("Sending dmail to the network.")

        if log.isEnabledFor(logging.DEBUG):
            log.debug("dmail block data=[\n{}]."\
                .format(mutil.hex_dump(tb_data)))

        total_storing = 0
        retry = 0
        while True:
            storing_nodes = yield from\
                self.task_engine.send_store_targeted_data(\
                    tb_data, store_key=True, key_callback=key_callback,\
                    retry_factor=retry * 10)

            total_storing += storing_nodes

            if total_storing >= 3:
                break

            if retry > 32:
                break
            elif retry > 3:
                yield from asyncio.sleep(1)

            retry += 1

        key_enc = mbase32.encode(key)
        id_enc = mbase32.encode(enc.generate_ID(key))

        if log.isEnabledFor(logging.INFO):
            log.info("Dmail sent; key=[{}], id=[{}], storing_nodes=[{}]."\
                .format(key_enc, id_enc, total_storing))

        return total_storing

    @asyncio.coroutine
    def fetch_recipient_dmail_sites(self, recipients):
        robjs = []

        for entry in recipients:
            if type(entry) in (tuple, list):
                recipient_enc, recipient, significant_bits = entry

                if significant_bits:
                    data_rw = yield from self.task_engine.send_find_key(\
                        recipient, significant_bits=significant_bits)

                    recipient = bytes(data_rw.data_key)

                    if not recipient:
                        log.info("Failed to find key for prefix [{}]."\
                            .format(recipient_enc))
            else:
                recipient = entry

            data_rw = yield from self.task_engine.send_get_data(recipient,\
                retry_factor=100)

            if not data_rw.data:
                if log.isEnabledFor(logging.INFO):
                    log.info("Failed to fetch dmail site [{}]."\
                        .format(mbase32.encode(recipient)))
                continue

            site_data = data_rw.data.decode("UTF-8")

            if log.isEnabledFor(logging.INFO):
                log.info("site_data=[{}].".format(site_data))

            robjs.append(DmailSite(site_data))

        return robjs
