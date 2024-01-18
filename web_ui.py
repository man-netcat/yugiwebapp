import argparse

from flask import Flask, render_template

parser = argparse.ArgumentParser(description="Yu-Gi-Oh! Web Application")
parser.add_argument("--debug", action="store_true", help="Enable debug mode")
parser.add_argument("--port", type=int, default=3000, help="Port to run the server on")
args = parser.parse_args()

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    if args.debug:
        app.run(debug=args.debug, port=args.port)
    else:
        from waitress import serve

        serve(app, host="0.0.0.0", port=args.port)
