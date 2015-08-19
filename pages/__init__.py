# Copyright (c) 2014-2015  Sam Maloney.
# License: GPL v2.

## Templates:
home_page_content = [\
    b"""<!DOCTYPE html>
<html><head><title>ALL TOGETHER NOW WE SING IN UNISON - MORPHiS Maalstroom UI</title>
<link rel="icon" type="image/png" href="/images/favicon.ico"/>
<link rel="stylesheet" type="text/css" href="morphis://.dmail/css"/>
<style type="text/css">
    div.msection {
        border-width 2px;
        border: dashed;
        padding: 1em; margin-top: 1em;
    }
    body {
        position: absolute;
        top: 0;
        width: 100%;
    }
</style>
</head><body>
<div class="valign_container header_non_fs"><h2 style="display: inline;">MORPHiS Maalstroom UI</h2><span class="valign"><span class="h-3">&nbsp;&nbsp;&nbsp;[v${MORPHIS_VERSION}]&nbsp;[${CONNECTIONS} Connections]</span><span class="right_float"><span class="h-3 bold" style="margin: 0;">(<a href="morphis://.aiwj/explanation">AIWJ</a> - JAVASCRIPT FREE!)</span></span></div>
<div class="msection">
    <h3>MORPHiS Web</h3>
    <p>
        <a href="morphis://sp1nara3xhndtgswh7fznt414we4mi3y6kdwbkz4jmt8ocb6x4w1faqjotjkcrefta11swe3h53dt6oru3r13t667pr7cpe3ocxeuma">MORPHiS Homepage</a><br/>
        <a href="morphis://sp1nara3xhndtgswh7fznt414we4mi3y6kdwbkz4jmt8ocb6x4w1faqjotjkcrefta11swe3h53dt6oru3r13t667pr7cpe3ocxeuma/firefox_plugin">MORPHiS Firefox Plugin</a><br/>
    </p>
</div>
<div class="msection">
    <h3>MORPHiS Interface</h3>
    <p>
        <a href="morphis://.upload/">Upload</a> (Upload data to the network.)<br/>
        <a href="morphis://.dmail/">Dmail</a> (Encrypted Uncensorable Messaging!)<br/>
    </p>
</div>
</body></html>""", None]

favicon_content = [None, None]

dmail_css_content = [\
    b"""* {
    box-sizing: border-box;
}
html, body {
    height: 100%;
    padding: 0;
    margin: 0;
}
.right_float {
    position: fixed;
    right: 0em;
}
.h-1 {
    font-size: 95%;
}
.h-2 {
    font-size: 85%;
}
.h-3 {
    font-size: 75%;
}
body.iframe {
    height: 0%;
}
div.header_non_fs {
    margin-top: 1em;
}
div.header {
    height: 3em;
    padding: 0;
    margin: 0;
    /* FIXME:
       Disgustingly enough (CSS is so), having the border fixes everything.
       We don't actually want a border, so we make it invisible with the
       color. Let this be proof that MORPHiS must deprecate CSS at
       somepoint as well! :) */
    border: solid 1px; /* Doesn't mater as long as not 0 or hidden. */
    border-color: #ffffff #ffffff; /* Invisible without browser knowing. */
}
div.footer {
    height: 3em;
    width: 100%;
    padding: 1em;
    margin: 0;
    bottom: 0px;
    position: absolute;
}
div.section {
    height: calc(100% - 7em);
    border: dashed 0.2em;
    margin-top: 1em;
    padding: 1em;
}
h4 {
    margin: 0 0 1em 0;
    padding: 0;
}
h5 {
    margin: 0;
    padding: 0;
}
div * * span {
    margin-left: 0.5em;
    margin-right: 0.5em;
}
#footer_right {
    right: 0px;
    position: absolute;
}
.nomargin {
    margin: 0;
}
iframe {
    margin: 0;
    margin-bottom: -4px; //FIXME: SOMEONE DEPRECATE HTML/CSS FOR ME PLEASE!
    // Without the above hack there is extra padding after an iframe, breaking
    // calcs and making scrollbars where there shouldn't be.
    padding: 0;
}
label {
    width: 10em;
    display: inline-block;
    text-align: right;
}
form p * {
    vertical-align: top;
}
label:after {
    content: ": ";
}
.valign_container {
    display: table;
}
.valign_container .valign {
    display: table-cell;
    vertical-align: middle;
    height: 100%;
}
body.panel_container {
    background-color: #86CBD2;
    display: table;
    height: 100%;
}
.panel_container .panel {
    display: table-cell;
    vertical-align: middle;
    height: 100%;
    padding-right: 0.75em;
    padding-left: 0.75em;
}
.italic {
    font-style: italic;
}
.bold {
    font-weight: bold;
}
.strikethrough {
    text-decoration: line-through;
}
div.panel span {
    padding-right: 0.25em;
    padding-left: 0.25em;
}
.right_text {
    position: absolute;
    right: 0;
}
.nowrap {
    white-space: nowrap;
}
.tag {
    background-color: #EEEEFF;
}
""", None]

dmail_page_wrapper =\
    b"""<!DOCTYPE html>
<html><head><title>MORPHiS Maalstroom Dmail Client</title>
<link rel="stylesheet" type="text/css" href="morphis://.dmail/css"/>
</head><body>
<div class="header">
    <h2>MORPHiS Maalstroom Dmail Client</h2>
</div>
<div class="footer">
    <h5>
        <span>&lt;- <a href="morphis://">MORPHiS UI</a></span>
        <span id="footer_right">
            <span>[<a href="morphis://.dmail/">List Dmail Addresses</a>]</span>
            <span>[<a href="morphis://.dmail/create_address">Create New Dmail Address</a>]</span>
            <span>[<a href="morphis://.dmail/compose">Send a Dmail</a>]</span>
        </span>
    </h5>
</div>
<div class="section">
    <iframe src="${IFRAME_SRC}" frameborder="0" height="100%" width="100%"></iframe>
</div>
</body></html>"""

dmail_page_content = [None, None]

dmail_frame_start =\
    b"""<!DOCTYPE html>
<html><head><base target="_top" /><link rel="stylesheet" type="text/css" href="morphis://.dmail/css"/></head><body class="iframe">
"""

dmail_frame_end =\
    b"""</body></html>"""

dmail_page_content__f1_start =\
    b"""<!DOCTYPE html>
<html><head><base target="_top" /><link rel="stylesheet" type="text/css" href="morphis://.dmail/css"/></head><body class="iframe">
<h4>Your dmail addresses:</h4>
"""

dmail_page_content__f1_end =\
    b"""</body></html>"""

dmail_address_page_content = [None, None]

dmail_inbox_start =\
    b"""<!DOCTYPE html>
<html><head><base target="_top" /><link rel="stylesheet" type="text/css" href="morphis://.dmail/css"/></head><body class="iframe">
<h4>Dmails for address [<a href="../../addr/${DMAIL_ADDRESS}">${DMAIL_ADDRESS2}</a>]:</h4>
"""

dmail_inbox_end =\
    b"""</body></html>"""

dmail_addr_view_start =\
    b"""<!DOCTYPE html>
<html><head><base target="_top" /><link rel="stylesheet" type="text/css" href="morphis://.dmail/css"/>
<style type="text/css">
</style></head><body class="iframe">
<h4>Dmail Address [${DMAIL_ADDRESS_SHORT}...].</h4>
<p class="nomargin">
    <a href="../../tag/view/Inbox/${DMAIL_ADDRESS}">View Inbox</a>
    [<a href="../../scan/${DMAIL_ADDRESS}">Scan Network for New Messages</a>]
</p>
<p>
    [<a href="../settings/${DMAIL_ADDRESS}">Address Settings</a>]
</p>
"""

dmail_addr_view_end =\
    b"""</body></html>"""

dmail_addr_settings_content = [None, None]

dmail_iframe_body_start =\
    b"""<!DOCTYPE html>
<html><head><base target="_top" /><link rel="stylesheet" type="text/css" href="morphis://.dmail/css"/></head><body class="iframe">"""

dmail_addr_settings_edit_content = [dmail_iframe_body_start\
    + b"""<h4>Dmail Address [<a href="../../${DMAIL_ADDRESS}">${DMAIL_ADDRESS_SHORT}...</a>].</h4>
<p>NOTE: Difficulty is the anti-spam setting that determines how much work it is to send you a Dmail. Its effect is exponential (work=2^difficulty). Do not set it too low -- I would recommend no lower than 20. If 2^difficulty is lower than the amount of nodes in the network, then the network will likely have trouble finding your Dmails.</p>
<p><b>NOTE</b>: At difficulty=20, sending you a Dmail will take ~30 seconds. A setting of 21 will take 1 minute. At 22, it is 2 minutes, 23 = 4 minutes, 24 = 8 minutes, 25 = 16 minutes, 26 = 32 minutes, 27 = 64 minutes, 28 = 128 minutes, 29 = 256 minutes, and 30 = 512 minutes, Etc. <b>Every 10 that you increase it is 1024x more cpu work for the sender.</b> The maximum value of difficulty=512 will take more time than the lifespan of the universe. If you want to receive Dmails anytime soon, don't increase this value much. Also, there is no point in increasing it unless you are going to publish your address and thus expect to be the target of spam. The times here are a rough guide and depend on the processing capability of the sending computer.</p>
<p><b>NOTE</b>: If you turn this up, you will no longer see any new Dmails that were sent to you while you had the lower setting. This is because they won't include enough work to be found. Dmails stored locally already (Inbox) won't be affected. In a future version of Maalstroom this will be solved. For now it is not, because it will take a bunch more UI to allow you to manage properly, and I want to release ASAP :).</p>
<form action="morphis://.dmail/addr/settings/edit/publish" method="get">
    <input type="hidden" name="dmail_address" id="dmail_address" value="${DMAIL_ADDRESS}"/>
    <p>
        <label for="difficulty">Difficulty</label>
        <input type="textfield" name="difficulty" id="difficulty" value="${DIFFICULTY}"/>
    </p>
    <input type="submit" formtarget="_self" id="publish" value="Republish Dmail Site"/>
</form>
<p>NOTE: Do not give out these values! The site private key controls your Dmail address. The DH secret is the key to decrypting your Dmail.</p>
<form action="save" method="post">
    <p>
        <label for="privatekey">Dmail Site Private Key</label>
        <textarea name="privatekey" id="privatekey" rows="26" cols="80" readonly>${PRIVATE_KEY}</textarea>
    </p>
    <p>
        <label for="x">Private Encryption DH Secret</label>
        <textarea name="x" id="x" rows="4" cols="80" readonly>${X}</textarea>
    </p>
    <p>
        <label for="target_key">Dmail Target Key</label>
        <input type="textfield" name="target_key" id="target_key" size="80" readonly value="${TARGET_KEY}"/>
    </p>
</form>
</body></html>""", None]

dmail_addr_settings_edit_success_content = [dmail_iframe_body_start.decode()\
    + """<h4>Dmail Address [<a target="_top" href="../../{}">{}</a>].</h4><p>SUCCESS.</p></body></html>""", None]

dmail_addr_settings_edit_fail_content = [dmail_iframe_body_start.decode()\
    + """<h4>Dmail Address [<a target="_top" href="../../{}">{}</a>].</h4><p>FAIL.</p><p>Try again in a bit.</p></body></html>""", None]

dmail_tag_view_content = [None, None]

dmail_tag_view_list_start =\
    b"""<!DOCTYPE html>
<html><head><base target="_top" /><link rel="stylesheet" type="text/css" href="morphis://.dmail/css"/></head><body class="iframe">
<h4>Dmails for tag [${TAG_NAME}] of address [<a href="../../../../addr/${DMAIL_ADDRESS}">${DMAIL_ADDRESS2}</a>]:</h4>
"""

dmail_tag_view_list_end =\
    b"""</body></html>"""

dmail_fetch_wrapper = [\
    b"""<!DOCTYPE html>
<html><head><base target="_top" /><link rel="stylesheet" type="text/css" href="morphis://.dmail/css"/></head><body>
<iframe src="${IFRAME_SRC}" frameborder="0" style="height: calc(100% - 2em);" width="100%"></iframe>
<iframe src="${IFRAME2_SRC}" frameborder="0" style="height: 2em;" width="100%"></iframe>
</body></html>""", None]

dmail_fetch_panel_content = [\
    b"""<!DOCTYPE html>
<html><head><base target="_top" /><link rel="stylesheet" type="text/css" href="morphis://.dmail/css"/></head><body class="iframe panel_container">
<div class="panel">
    <span>
        [<a target="_self" href="../mark_as_read/${DMAIL_IDS}">Toggle Read</a>]
    </span><span>
        [<a target="_self" href="../trash/${DMAIL_IDS}">Trash Dmail</a>]
    </span>
</div>
</body></html>""", None]

dmail_create_address_content = [None, None]

dmail_create_address_form_content = [\
    b"""<!DOCTYPE html>
<html><head><base target="_top" /><link rel="stylesheet" type="text/css" href="morphis://.dmail/css"/></head><body class="iframe">
<form action="morphis://.dmail/create_address/make_it_so" method="get">
    <h4>Dmail Address Generation</h4>
    <p>To create yourself a new Dmail Address, simply click the Create button below. Changing these values from their defaults is not needed at all.</p>
    <p>
        <label for="difficulty">Difficulty</label>
        <input type="textfield" name="difficulty" id="difficulty" value="20"/>
    </p>
    <p>NOTE: Difficulty is the anti-spam setting that determines how much work it is to send you a Dmail. Its effect is exponential (work=2^difficulty). Do not set it too low -- I would recommend no lower than 20. If 2^difficulty is lower than the amount of nodes in the network, then the network will likely have trouble finding your Dmails.</p>
    <p>
        <label for="prefix">Dmail Prefix</label>
        <input type="textfield" name="prefix" id="prefix"/>&nbsp;<span class="italic">(Optional)</span>
    </p>
    <p>NOTE: Each letter in the prefix will make the address take 32x longer to generate. Three letters takes almost an hour on my test machine.</p>
    <input type="submit" formtarget="_self" id="create" value="Create"/>
</form>
</body></html>""", None]

dmail_compose_dmail_content = [None, None]

dmail_compose_dmail_form_start =\
    b"""<!DOCTYPE html>
<html><head><base target="_top" /><link rel="stylesheet" type="text/css" href="morphis://.dmail/css"/>
<style type="text/css">
</style></head><body class="iframe">
<form action="morphis://.dmail/compose/make_it_so" method="post" accept-charset="UTF-8 ISO-8859-1">
    <p class="nowrap">
        <label for="sender">From</label>
        <select name="sender">"""

dmail_compose_dmail_form_end =\
    b"""</select>
    </p><p>
        <label for="destination">To</label>
        <input type="textfield" name="destination" id="destination" size="70" value="${DEST_ADDR}"/>
    </p><p>
        <label for="subject">Subject</label>
        <input type="textfield" name="subject" id="subject" size="70"/>
    </p><p>
        <label for="content">Message Content</label>
        <textarea name="content" id="content" cols="80" rows="24"></textarea>
    </p>
    <input type="submit" formtarget="_self" id="send" value="Send"/> (This will take at least a few seconds, if not much longer, depending on the difficulty (anti-spam setting) set by the owner of the destination address. Also, there is randomness involved.)
</form>
</body></html>"""

##.

initialized_template = False
if not initialized_template:
    fh = open("favicon.ico", "rb")
    if fh:
        favicon_content[0] = fh.read()

    dmail_page_content[0] =\
        dmail_page_wrapper.replace(b"${IFRAME_SRC}", b"address_list")

    dmail_address_page_content[0] = dmail_page_wrapper

    dmail_addr_settings_content[0] = dmail_page_wrapper

    dmail_create_address_content[0] =\
        dmail_page_wrapper.replace(b"${IFRAME_SRC}", b"create_address/form")

    dmail_compose_dmail_content[0] = dmail_page_wrapper

    dmail_tag_view_content[0] = dmail_page_wrapper

    initialized_template = True
