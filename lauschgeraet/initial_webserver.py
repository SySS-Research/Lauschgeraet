# -*- coding: utf-8 -*-
"""This provides just a very simple web server in case flask is not
installed. It gives further instructions for the set up.

It should run under both python2 and python3.
"""

from html import escape
from lauschgeraet.lgiface import lg_setup
from subprocess import check_output, STDOUT, CalledProcessError
import logging
import sys

if sys.version_info >= (3, 0):
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs
else:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from urlparse import urlparse, parse_qs


log = logging.getLogger(__name__)

HTML = {
    "index": '''
<html><head><title>SySS Lauschger&auml;t</title></head>
<body><h1>SySS Lauschger&auml;t</h1>
<p>You are seeing this page because you haven't set up the Lauschger&auml;t
yet.</p>
<p>This device is currently: <strong>%s</strong> (<a href="/netdetails">network
details</a>)</p>
<p>Make sure that the device is online (has a route to the
internet and can resolve host names), fill out this form and then press this
button to install all dependencies automatically. The device will reboot
afterwards. You can attach the external NICs one by one and use the network
details linked above to figure out which is which. Reload that page after
you attach or detach a NIC. You may want to grab a sharpie and label the
external NICs.</p>
<p>After the device reboots, it will provide its own DHCP service and also
create a wifi network. The WPA2 PSK is the admin password and the
credentials for the webapp at <a
href="http://lauschgeraet:1337">http://lauschgeraet:1337</a> is
<code>syss:&lt;admin password&gt;</code>.</p>
<form method="POST" action="/">
<input type='text' name='atiface'> Name of the attacker interface (the
built-in NIC is recommended)<br/>
<input type='text' name='cliface'> Name of the client interface<br>
<input type='text' name='swiface'> Name of the switch interface<br>
<input type='text' name='wifiiface'> Name of the wifi interface<br>
<input type='text' name='adminpass'> The admin password (equivalent to root
access! Must be at least eight characters long)<br>
<button type="submit">Run Setup</button>
</form>
<p>This may take a while. Do not turn the device off.
If you tried this before, check the <a href="/log">log</a>.</p>
</body></html>''',
    "net_details": '''
<html><head><title>SySS Lauschger&auml;t - Network
Details</title></head><body> <h1>SySS Lauschger&auml;t - network
details</h1>
<h2>IP configuration (ip a)</h2> <pre>%s</pre>
<h2>Gateway information (ip r)</h2> <pre>%s</pre>
<h2>DNS information (cat /etc/resolv.conf)</h2> <pre> %s </pre>
</body></html>''',

}


def online_status():
    try:
        http = check_output("wget -O- --quiet -S clients3.google.com".split(),
                            stderr=STDOUT)
    except CalledProcessError:
        return "Offline"
    if sys.version_info >= (3, 0):
        if http.startswith(b"  HTTP"):
            return "Online"
    else:
        if http.startswith("  HTTP"):
            return "Online"
    return "Offline"


def show_log():
    with open('/var/log/lauschgeraet.log') as f:
        log = f.read()
    response = '''
<html><head><title>SySS Lauschger&auml;t - Log</title></head><body> <h1>SySS
Lauschger&auml;t - log</h1>
<pre>%s</pre>
</body></html> ''' % escape(log)
    return response


def net_details():
    if sys.version_info >= (3, 0):
        ip = check_output('/bin/ip a'.split()).decode()
        route = check_output('/bin/ip r'.split()).decode()
        dns = check_output('/bin/cat /etc/resolv.conf'.split()).decode()
    else:
        ip = check_output('/bin/ip a'.split())
        route = check_output('/bin/ip r'.split())
        dns = check_output('/bin/cat /etc/resolv.conf'.split())
    response = HTML["net_details"] % tuple(map(escape, (ip, route, dns)))
    return response


class RequestHandler(BaseHTTPRequestHandler):

    key = None
    command = []

    def _parse_request(self):
        parsed_req = urlparse(self.path)
        args = parse_qs(parsed_req.query)
        if self.headers.get('content-type', '') \
           == 'application/x-www-form-urlencoded':
            body = self.rfile.read(int(self.headers.get('content-length')))
            args = parse_qs(body)

        return (parsed_req.path, args)

    def do_POST(self):
        path, args = self._parse_request()
        self.do('POST', path, args)

    def do_GET(self):
        path, args = self._parse_request()
        self.do('GET', path, args)

    def do(self, method, path, args):
        if method == 'GET':
            self.send_response(200)
            self.end_headers()

            if path == '/netdetails':
                response = net_details()
            elif path == '/log':
                response = show_log()
            else:
                response = HTML["index"] % (online_status())

            if sys.version_info >= (3, 0):
                self.wfile.write(response.encode())
            else:
                self.wfile.write(response)

        elif method == 'POST' and path == '/':
            script_args = 'atiface cliface swiface wifiiface adminpass'
            if sys.version_info >= (3, 0):
                script_args = [args[k.encode()] for k in script_args.split()]
            else:
                script_args = [args[k] for k in script_args.split()]
            # TODO stream stdout via HTTP
            if lg_setup(*script_args):
                self.send_response(200)
                self.end_headers()
            else:
                self.send_error(500, 'fail, check the logs')
        else:
            self.send_error(404, "You can't do this")


def run(host, port):
    server = HTTPServer((host, port), RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Exiting")
        pass
