import argparse
import os

import requests_cache
from flask import Flask, jsonify, render_template, request

parser = argparse.ArgumentParser(description="Yu-Gi-Oh! Web Application")
parser.add_argument("--debug", action="store_true", help="Enable debug mode")
args = parser.parse_args()

app = Flask(__name__)

api_host = os.environ.get("YUGIAPI_SERVICE_PORT_5000_TCP_ADDR", "localhost")
api_port = os.environ.get("YUGIAPI_SERVICE_PORT_5000_TCP_PORT", 5000)
api_url = f"http://{api_host}:{api_port}"

app_host = os.environ.get("YUGIWEBAPP_SERVICE_PORT_3000_TCP_HOST", "localhost")
app_port = os.environ.get("YUGIWEBAPP_SERVICE_PORT_3000_TCP_PORT", 3000)
app_url = f"http://{app_host}:{app_port}"

card_map = None
arch_map = None
set_map = None

session = requests_cache.CachedSession("request_cache")


def setup_maps():
    global card_map, arch_map, set_map
    maps = session.get(f"{api_url}/mappings").json()
    card_map = maps["card_map"]
    arch_map = maps["arch_map"]
    set_map = maps["set_map"]


def card_query(ids):
    idstring = "|".join([str(id) for id in ids])
    return session.get(f"{api_url}/card_data?id={idstring}").json()


@app.route("/search_card", methods=["GET", "POST"])
def search_card():
    if request.method == "POST":
        card_id = request.form["card_id"]
        try:
            res = session.get(f"{api_url}/card_data?id={card_id}")
            card_data = res.json()
            return render_template("card_result.html", card=card_data[0])
        except Exception as e:
            print(e)
            return jsonify({"error": str(e)})
    return render_template("search.html")


@app.route("/search_archetype", methods=["GET", "POST"])
def search_archetype():
    if request.method == "POST":
        archetype_id = request.form["archetype_id"]
        try:
            res = session.get(f"{api_url}/arch_data?id={archetype_id}")
            arch_data = res.json()[0]
            members = card_query(arch_data["members"]) if arch_data["members"] else []
            support = card_query(arch_data["support"]) if arch_data["support"] else []
            related = card_query(arch_data["related"]) if arch_data["related"] else []
            return render_template(
                "arch_result.html",
                arch=arch_data,
                members=members,
                support=[card for card in support if card not in members],
                related=[
                    card
                    for card in related
                    if card not in members and card not in support
                ],
            )
        except Exception as e:
            print(e)
            return jsonify({"error": str(e)})
    return render_template("search.html")


@app.route("/search_set", methods=["GET", "POST"])
def search_set():
    if request.method == "POST":
        set_id = request.form["set_id"]
        try:
            res = session.get(f"{api_url}/set_data?id={set_id}")
            set_data = res.json()[0]
            contents = card_query(set_data["contents"])
            return render_template(
                "set_result.html",
                set=set_data,
                contents=contents,
            )
        except Exception as e:
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
    setup_maps()

    if args.debug:
        app.run(debug=args.debug, port=app_port)
    else:
        from waitress import serve

        serve(app, host="0.0.0.0", port=app_port)
