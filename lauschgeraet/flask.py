from flask import Flask, render_template, request, Response, redirect, \
        send_from_directory

app = Flask(__name__)


def main():
    #  app.run(debug=True, port=args.LPORT, host=args.LHOST)
    app.run(debug=True)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)


@app.route('/')
def index():
    context = {
        "lgstate": {
            "enabled": True,
            "mode": "passive",
        }
    }
    return render_template("index.html", **context)

@app.route('/stats')
def stats():
    context = {
    }
    return render_template("stats.html", **context)

@app.route('/mitm')
def mitm():
    context = {
    }
    return render_template("mitm.html", **context)

@app.route('/stats')
def extras():
    context = {
    }
    return render_template("extras.html", **context)

