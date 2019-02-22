from flask import Flask, render_template, send_from_directory, request
from lauschgeraet.ifaces import get_ip_config, get_ip_route, iptables_raw
import logging
from flask.logging import default_handler

log = logging.getLogger(__name__)

root = logging.getLogger()
root.addHandler(default_handler)

app = Flask(__name__)


def lgstate():
    return {
        "lgstate": {
            "enabled": True,
            "mode": "passive",
        }
    }


def main():
    #  app.run(debug=True, port=args.LPORT, host=args.LHOST)
    app.run(debug=True, port=1337)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)


@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('static/img', path)


@app.route('/')
def index():
    context = {
        **lgstate(),
        "ipconfig": {
            "iface1": get_ip_config(1),
            "iface2": get_ip_config(2),
            "iproute": get_ip_route(),
        },
    }
    return render_template("index.html", **context)


@app.route('/stats')
def stats():
    context = {**lgstate(), }
    return render_template("stats.html", **context)


@app.route('/mitm')
def mitm():
    context = {
        **lgstate(),
        "iptables_raw": iptables_raw('nat', 'PREROUTING').decode()
    }
    return render_template("mitm.html", **context)


@app.route('/extras')
def extras():
    context = {**lgstate(), }
    return render_template("extras.html", **context)


@app.route('/log')
def log():
    with open('/var/log/lauschgeraet.log') as f:
        log = f.read()
    context = {**lgstate(), "log": log}
    return render_template("log.html", **context)


@app.route('/toggleswitch', methods=["POST"])
def toggle_switch():
    print(request.form["name"])
    return "OK"


@app.route('/addrule', methods=["POST"])
def add_rule():
    print(request.form)
    return "OK"
