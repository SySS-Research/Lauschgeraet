# -*- coding: utf-8 -*-
from flask import Flask, render_template, send_from_directory, request, \
        flash
from flask.logging import default_handler
from flask_socketio import SocketIO, emit
from lauschgeraet.ifaces import get_ip_config, get_ip_route, iptables_raw, \
        get_ss, list_iptables, add_iptables_rule, replace_iptables_rule, \
        delete_iptables_rule
from lauschgeraet.lgiface import get_lg_status, set_lg_mode
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
    socketio.run(app, debug=True, host='0.0.0.0', port=1337)


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
def dashboard():
    context = {
        **get_lg_status(),
        "ipconfig": {
            "iface1": get_ip_config(1),
            "iface2": get_ip_config(2),
            "iproute": get_ip_route(),
            "ss": get_ss()
        },
    }
    return render_template("dashboard.html", **context)


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
    rules = list_iptables('nat', 'LG')
    context = {
        **get_lg_status(),
        "rules": rules,
        "iptables_raw": iptables_raw('nat').decode()
    }
    return render_template("mitm.html", **context)


@app.route('/services')
def services():
    context = {**get_lg_status(), }
    return render_template("services.html", **context)


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
    if switch_name == 'onoffswitch':
        status = get_lg_status()
        if status == 'disabled':
            out = set_lg_mode('passive')
        elif status == 'passive':
            out = set_lg_mode('disable')
        else:
            flash('Lauschgerät can only be disabled if the mode '
                  'is "passive"', "danger")
            return render_template("messages.html")
        if out:
            flash('Error while activating: %s' % out, "danger")
        else:
            flash('Lauschgerät activated', "success")
    return render_template("messages.html")


@app.route('/mitmtable', methods=["GET"])
def mitmtable():
    rules = list_iptables('nat', 'LG')
    context = {
        "rules": rules,
    }
    return render_template("mitm-table.html", **context)


@app.route('/addrule', methods=["POST"])
def add_rule():
    if ':' in request.form["olddest"]:
        oldip, oldport = request.form["olddest"].split(':')
    else:
        flash("Your old destination must be of the form <IP>:<PORT>", "danger")
        return render_template("messages.html")
    if ':' in request.form["newdest"]:
        newip, newport = request.form["newdest"].split(':')
    else:
        newip = request.form["newdest"]
        newport = oldport
    out = add_iptables_rule(
        request.form["proto"],
        oldip, oldport,
        newip, newport,
    )
    if out:
        flash("Error while adding rule: %s" % out, "danger")
        return render_template("messages.html")
    return ""


@app.route('/editrule', methods=["POST"])
def edit_rule():
    if ':' in request.form["olddest"]:
        oldip, oldport = request.form["olddest"].split(':')
    else:
        flash("Your old destination must be of the form <IP>:<PORT>", "danger")
        return render_template("messages.html")
    if ':' in request.form["newdest"]:
        newip, newport = request.form["newdest"].split(':')
    else:
        newip = request.form["newdest"]
        newport = oldport
    out = replace_iptables_rule(request.form["number"],
                                request.form["proto"],
                                oldip, oldport,
                                newip, newport,
                                )
    if out:
        flash("Error while adding rule: %s" % out, "danger")
        return render_template("messages.html")
    return ""


@app.route('/deleterule', methods=["POST"])
def delete_rule():
    out = delete_iptables_rule(request.form["number"])
    if out:
        flash("Error while deleting rule: %s" % out, "danger")
        return render_template("messages.html")
    return ""


@app.route('/stub-newrule', methods=["GET"])
def stub_newrule():
    context = {
        "mode": "add" if 'add' in request.args else 'edit',
        "rule": {
            "number": "",
            "prot": "",
            "olddest": "",
            "newdest": "",
        }
    }
    return render_template("stub-newrule.html", **context)


@app.route('/stub-editrule', methods=["GET"])
def stub_editrule():
    n = int(request.args["n"])
    rules = list_iptables('nat', 'LG')
    for r in rules:
        if int(r["num"]) == n:
            rule = r
            break
    rule = {
        "num": rule["num"],
        "proto": rule["prot"],
        "olddest": rule["destination"],
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
