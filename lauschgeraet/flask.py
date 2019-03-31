from flask import Flask, render_template, send_from_directory, request, \
        flash
from flask.logging import default_handler
from flask_socketio import SocketIO, emit
from lauschgeraet.ifaces import get_ip_config, get_ip_route, iptables_raw, \
        get_ss, list_iptables, add_iptables_rule, replace_iptables_rule, \
        delete_iptables_rule
from lauschgeraet.lgiface import get_lg_status, activate_lg, set_lg_mode
import subprocess
import os
import logging

log = logging.getLogger(__name__)

root = logging.getLogger()
root.addHandler(default_handler)
logging.getLogger("watchdog.observers.inotify_buffer").setLevel(logging.INFO)
logging.getLogger("socket").setLevel(logging.INFO)

app = Flask(__name__)
app.secret_key = os.urandom(16)
socketio = SocketIO(app)


def main():
    #  app.run(debug=True, port=1337)
    socketio.run(app, debug=True, port=1337)


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
        **get_lg_status(),
        "ipconfig": {
            "iface1": get_ip_config(1),
            "iface2": get_ip_config(2),
            "iproute": get_ip_route(),
            "ss": get_ss()
        },
    }
    return render_template("index.html", **context)


@app.route('/setmode', methods=["POST"])
def set_mode():
    mode = request.form["mode"]
    if mode in "passive active wifi".split():
        out = set_lg_mode(mode)
        if out:
            flash('Error while setting mode: %s' % out, "danger")
        else:
            flash('Mode set to %s' % mode, "success")
    else:
        flash('Unknown mode: %s' % mode, "danger")
    return render_template("messages.html")


@app.route('/stats')
def stats():
    context = {**get_lg_status(), }
    return render_template("stats.html", **context)


@app.route('/mitm')
def mitm():
    rules = list_iptables('nat', 'PREROUTING')
    context = {
        **get_lg_status(),
        "rules": rules,
        "iptables_raw": iptables_raw('nat').decode()
    }
    return render_template("mitm.html", **context)


@app.route('/extras')
def extras():
    context = {**get_lg_status(), }
    return render_template("extras.html", **context)


@app.route('/shell')
def shell():
    context = {**get_lg_status(), }
    return render_template("shell.html", **context)


@app.route('/log')
def log():
    with open('/var/log/lauschgeraet.log') as f:
        log = f.read()
    context = {**get_lg_status(), "log": log}
    return render_template("log.html", **context)


@app.route('/settings')
def settings():
    context = {**get_lg_status(), }
    return render_template("settings.html", **context)


@app.route('/help')
def help():
    context = {**get_lg_status(), }
    return render_template("help.html", **context)


@app.route('/toggleswitch', methods=["POST"])
def toggle_switch():
    switch_name = request.form["name"]
    if switch_name == 'lg-status':
        activate_lg()
    return "OK"


@app.route('/addrule', methods=["POST"])
def add_rule():
    return add_iptables_rule(request.form["proto"],
                             request.form["port"],
                             request.form["olddest"],
                             request.form["newdest"]
                             )


@app.route('/editrule', methods=["POST"])
def edit_rule():
    #  print(request.form)
    return replace_iptables_rule(request.form["number"],
                                 request.form["proto"],
                                 request.form["port"],
                                 request.form["olddest"],
                                 request.form["newdest"]
                                 )


@app.route('/deleterule', methods=["POST"])
def delete_rule():
    return delete_iptables_rule(request.form["number"])


@app.route('/stub-newrule', methods=["GET"])
def stub_newrule():
    context = {
        "mode": "add" if 'add' in request.args else 'edit',
        "rule": {
            "number": "",
            "prot": "",
            "port": "",
            "olddest": "",
            "newdest": "",
        }
    }
    return render_template("stub-newrule.html", **context)


@app.route('/stub-editrule', methods=["GET"])
def stub_editrule():
    n = int(request.args["n"])
    rules = list_iptables('nat', 'PREROUTING')
    for r in rules:
        if int(r["num"]) == n:
            rule = r
            break
    rule = {
        "num": rule["num"],
        "proto": rule["prot"],
        "port": "" if ':' not in rule["destination"] else
        rule["destination"].split(':')[1],
        "olddest": rule["destination"].split(':')[0],
        "newdest": rule["extension"],
    }
    context = {
        "mode": "edit",
        "rule": rule,
    }
    return render_template("stub-newrule.html", **context)


@socketio.on('joined', namespace='/shell_socket')
def joined(message):
    emit('status', {'msg': 'SUCCESSFULLY CONNECTED'})


@socketio.on('command', namespace='/shell_socket')
def command(c):
    c = c['msg']
    emit('message', {'msg': '$ %s\n' % c})
    try:
        b = subprocess.check_output(c, shell=True,
                                    stderr=subprocess.STDOUT,).decode()
    except Exception as err:
        b = str(err) + '\n'

    emit('message', {'msg': b})
