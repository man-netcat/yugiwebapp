import argparse
import os
from urllib.parse import quote_plus

import requests
import requests_cache
from flask import Flask, redirect, render_template, request
from rapidfuzz import fuzz, process
from retrying import retry

parser = argparse.ArgumentParser(description="Yu-Gi-Oh! Web Application")
parser.add_argument("--debug", action="store_true", help="Enable debug mode")
args = parser.parse_args()

app = Flask(__name__)

api_url = os.environ.get("API_URL", "localhost:5000")

app.jinja_env.filters["quote_plus"] = lambda u: quote_plus(u)

if args.debug:
    session = requests.Session()
else:
    session = requests_cache.CachedSession("request_cache")

card_names = []
arch_names = []
set_names = []


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
def wait_for_api():
    print("trying to connect to api...")
    response = requests.get(f"{api_url}/connection")
    response.raise_for_status()


def fuzzy_search(query, options, threshold=50):
    matches = process.extract(query, options, scorer=fuzz.WRatio, limit=10)
    return [match for match, score, _ in matches if score > threshold]


def card_query(ids):
    idstring = "|".join([str(id) for id in ids])
    return session.get(f"{api_url}/card_data?id={idstring}").json()


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        search_term = request.form["search_term"]
        card_matches = fuzzy_search(search_term, card_names)
        arch_matches = fuzzy_search(search_term, arch_names)
        set_matches = fuzzy_search(search_term, set_names)
        return render_template(
            "search_results.html",
            api_url=api_url,
            card_matches=card_matches,
            arch_matches=arch_matches,
            set_matches=set_matches,
        )
    return redirect("/")


@app.route("/card/<card_name>")
def card_result(card_name):
    res = session.get(f"{api_url}/card_data?name={card_name}")
    card_data = res.json()[0]
    return render_template(
        "card_result.html",
        api_url=api_url,
        card=card_data,
    )


@app.route("/archetype/<arch_name>")
def archetype_result(arch_name):
    res = session.get(f"{api_url}/arch_data?name={arch_name}")
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


@app.route("/set/<set_name>")
def set_result(set_name):
    res = session.get(f"{api_url}/set_data?name={set_name}")
    set_data = res.json()[0]
    contents = card_query(set_data["contents"])
    return render_template(
        "set_result.html",
        api_url=api_url,
        set=set_data,
        contents=contents,
    )


@app.route("/")
def index():
    return render_template(
        "index.html",
        card_names=card_names,
        arch_names=arch_names,
        set_names=set_names,
    )


if __name__ == "__main__":
    wait_for_api()
    print("api ready!")
    res = session.get(f"{api_url}/names").json()
    card_names = res["card_names"]
    arch_names = res["arch_names"]
    set_names = res["set_names"]

    if args.debug:
        app.run(debug=args.debug, port=3000)
    else:
        from waitress import serve

        serve(app, host="0.0.0.0", port=3000)
