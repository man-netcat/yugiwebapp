import argparse
import os
import time

import requests
import requests_cache
from flask import Flask, redirect, render_template, request

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

if args.debug:
    session = requests.Session()
else:
    session = requests_cache.CachedSession("request_cache")


def wait_for_api():
    max_retries = 30
    retries = 0

    while retries < max_retries:
        try:
            response = requests.get(f"{api_url}/connection")
            response.raise_for_status()
            return
        except requests.exceptions.RequestException as e:
            print(
                f"API not online yet. Retrying in 2 seconds... ({retries + 1}/{max_retries})"
            )
            time.sleep(2)
            retries += 1

    print("Max retries reached. Unable to connect to the API. Exiting.")
    exit(1)


def card_query(ids):
    idstring = "|".join([str(id) for id in ids])
    return session.get(f"{api_url}/card_data?id={idstring}").json()


@app.route("/search_card", methods=["GET", "POST"])
def search_card():
    if request.method == "POST":
        card_name = request.form["card_name"]
        res = session.get(f"{api_url}/card_data?name={card_name}")
        card_data = res.json()[0]
        return render_template(
            "card_result.html",
            api_url=api_url,
            card=card_data,
        )
    return redirect("/")


@app.route("/search_archetype", methods=["GET", "POST"])
def search_archetype():
    if request.method == "POST":
        archetype_name = request.form["archetype_name"]
        res = session.get(f"{api_url}/arch_data?name={archetype_name}")
        arch_data = res.json()[0]
        members = card_query(arch_data["members"]) if arch_data["members"] else []
        support = card_query(arch_data["support"]) if arch_data["support"] else []
        related = card_query(arch_data["related"]) if arch_data["related"] else []
        return render_template(
            "arch_result.html",
            api_url=api_url,
            arch=arch_data,
            members=members,
            support=[card for card in support if card not in members],
            related=[
                card for card in related if card not in members and card not in support
            ],
        )
    return redirect("/")


@app.route("/search_set", methods=["GET", "POST"])
def search_set():
    if request.method == "POST":
        set_name = request.form["set_name"]
        res = session.get(f"{api_url}/set_data?name={set_name}")
        set_data = res.json()[0]
        contents = card_query(set_data["contents"])
        return render_template(
            "set_result.html",
            api_url=api_url,
            set=set_data,
            contents=contents,
        )
    return redirect("/")


@app.route("/")
def index():
    res = session.get(f"{api_url}/names").json()
    card_names = res["card_names"]
    arch_names = res["arch_names"]
    set_names = res["set_names"]
    return render_template(
        "index.html",
        card_names=card_names,
        arch_names=arch_names,
        set_names=set_names,
    )


if __name__ == "__main__":
    wait_for_api()

    if args.debug:
        app.run(debug=args.debug, port=app_port)
    else:
        from waitress import serve

        serve(app, host="0.0.0.0", port=app_port)
