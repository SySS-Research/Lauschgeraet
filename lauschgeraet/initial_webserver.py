"""This provides just a very simple web server in case flask is not
installed. It gives further instructions for the installation routine."""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from html import escape
from lauschgeraet.dependencies import install_dependencies, \
        dependency_check
from subprocess import check_output
import logging

log = logging.getLogger(__name__)


def online_status():
    http = check_output("curl -Is clients3.google.com".split())
    if http.startswith(b"HTTP"):
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
    ip = check_output('/bin/ip a'.split()).decode()
    route = check_output('/bin/ip r'.split()).decode()
    dns = check_output('/bin/cat /etc/resolv.conf'.split()).decode()
    response = '''
<html><head><title>SySS Lauschger&auml;t - Network
Details</title></head><body> <h1>SySS Lauschger&auml;t - network
details</h1>
<h2>IP configuration (ip a)</h2> <pre>%s</pre>
<h2>Gateway information (ip r)</h2> <pre>%s</pre>
<h2>DNS information (cat /etc/resolv.conf)</h2> <pre>%s</pre>
</body></html> ''' % tuple(map(escape, (ip, route, dns)))
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
                response = '''
<html><head><title>SySS Lauschger&auml;t</title></head><body> <h1>SySS
Lauschger&auml;t</h1> <p>You are seeing this page because there are unmet
dependencies. The output of the dependency check is shown below.</p> <p>This
device is currently: <strong>%s</strong> (<a href="/netdetails">network
details</a>)</p> <p>Make sure that the device is online (has a route to the
internet and can resolve host names), then press this
button to install all dependencies automatically. The device will reboot
afterwards.</p> <form method="POST" action="/"> <button
type="submit">Install Dependencies</button></form><p>If you tried this
before, check the <a href="/log">log</a>.</p> <hr> <pre> %s
</pre></body></html>
                ''' % (online_status(), escape(dependency_check()))
            self.wfile.write(response.encode())

        elif method == 'POST':
            if install_dependencies():
                self.send_response(200)
                self.end_headers()
            else:
                self.send_error(500, 'fail')
        else:
            self.send_error(500, 'fail')


def run(host, port):
    server = HTTPServer((host, port), RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Exiting")
        pass
