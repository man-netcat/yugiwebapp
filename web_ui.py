import argparse

import requests_cache
from flask import Flask, jsonify, render_template, request

parser = argparse.ArgumentParser(description="Yu-Gi-Oh! Web Application")
parser.add_argument("--debug", action="store_true", help="Enable debug mode")
parser.add_argument("--port", type=int, default=3000, help="Port to run the server on")
args = parser.parse_args()

app = Flask(__name__)

base_url = "http://localhost:5000"
card_map = None
arch_map = None
set_map = None
session = requests_cache.CachedSession("request_cache")


def wait_for_api():
    print("Waiting for the API to be online...")
    available = False
    while not available:
        response = session.get(f"{base_url}/connection")
        available = response.status_code == 200


def setup_maps():
    global card_map, arch_map, set_map
    maps = session.get(f"{base_url}/mappings").json()
    card_map = maps["card_map"]
    arch_map = maps["arch_map"]
    set_map = maps["set_map"]


@app.route("/search_card", methods=["GET", "POST"])
def search_card():
    print(request.method)
    print(request.form)
    if request.method == "POST":
        card_id = request.form["card_id"]
        try:
            res = session.get(f"{base_url}/card_data?id={card_id}")
            card_data = res.json()
            print(card_data)
            return render_template("card_result.html", card=card_data[0])
        except session.exceptions.RequestException as e:
            return jsonify({"error": str(e)})
    return render_template("search.html")


@app.route("/search_archetype", methods=["GET", "POST"])
def search_archetype():
    if request.method == "POST":
        archetype_id = request.form["archetype_id"]
        try:
            res = session.get(f"{base_url}/arch_data?id={archetype_id}")
            arch_data = res.json()
            print(arch_data)
            return render_template("arch_result.html", arch=arch_data[0])
        except session.exceptions.RequestException as e:
            return jsonify({"error": str(e)})
    return render_template("search.html")


@app.route("/search_set", methods=["GET", "POST"])
def search_set():
    if request.method == "POST":
        set_id = request.form["set_id"]
        try:
            res = session.get(f"{base_url}/set_data?id={set_id}")
            set_data = res.json()
            print(set_data)
            return render_template("set_result.html", set=set_data[0])
        except session.exceptions.RequestException as e:
            return jsonify({"error": str(e)})
    return render_template("search.html")


@app.route("/search")
def search():
    global card_map, arch_map, set_map
    return render_template(
        "search.html", card_map=card_map, arch_map=arch_map, set_map=set_map
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    wait_for_api()
    setup_maps()

    if args.debug:
        app.run(debug=args.debug, port=args.port)
    else:
        from waitress import serve

        serve(app, host="0.0.0.0", port=args.port)
