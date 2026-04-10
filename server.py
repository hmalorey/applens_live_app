import json
import os
import time
from flask import Flask, request, Response

HERE = os.path.dirname(os.path.abspath(__file__))

from config import cutoff_date, markets_from_names, DAYS_BACK, MIN_RATING, MAX_RATING
from core.scraper import scrape_app_store, scrape_play_store
from core.ratings import get_ratings
from core.analyzer import analyze

app = Flask(__name__)


# ── CORS — allow file:// (origin: null) and any localhost ────────
@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


# ── Serve the HTML ────────────────────────────────────────────────
@app.route("/")
def index():
    with open(os.path.join(HERE, "applens.html")) as f:
        return f.read(), 200, {"Content-Type": "text/html"}


# ── SSE helper ────────────────────────────────────────────────────
def sse(event: str, data: str = "") -> str:
    return f"event: {event}\ndata: {data}\n\n"


# ── Main analysis stream ──────────────────────────────────────────
def run_analysis(app_name, app_store_id, play_store_id, markets_raw, days_back, min_rating, max_rating):
    markets = markets_from_names(markets_raw)
    cutoff  = cutoff_date(days_back)

    yield sse("step", "Connecting to App Store")
    time.sleep(0.1)

    try:
        ios_reviews = scrape_app_store(app_store_id, markets, cutoff, min_rating, max_rating)
    except Exception as e:
        yield sse("error", str(e)); return

    yield sse("step", "Fetching Play Store reviews")

    try:
        android_reviews = scrape_play_store(play_store_id, markets, cutoff, min_rating, max_rating)
    except Exception as e:
        yield sse("error", str(e)); return

    all_reviews = ios_reviews + android_reviews

    yield sse("step", "Computing ratings")

    try:
        ratings = get_ratings(app_store_id, play_store_id, markets, all_reviews)
    except Exception as e:
        yield sse("error", str(e)); return

    yield sse("step", "Analyzing sentiment")

    try:
        analysis = analyze(app_name, all_reviews, days_back)
    except Exception as e:
        yield sse("error", str(e)); return

    yield sse("step", "Generating insights")

    result = {
        "app_name":      app_name,
        "markets":       markets_raw,
        "days_back":     days_back,
        "total_reviews": len(all_reviews),
        **ratings,
        "problems":      analysis.get("problems", []),
        "strengths":     analysis.get("strengths", []),
        "reviews":       all_reviews,
    }

    yield sse("result", json.dumps(result))


@app.route("/analyze/stream")
def analyze_stream():
    app_name      = request.args.get("app_name", "")
    app_store_id  = request.args.get("app_store_id", "")
    play_store_id = request.args.get("play_store_id", "")
    markets_raw   = request.args.getlist("markets")
    days_back     = int(request.args.get("days_back",  DAYS_BACK))
    min_rating    = int(request.args.get("min_rating", MIN_RATING))
    max_rating    = int(request.args.get("max_rating", MAX_RATING))

    if not app_store_id or not play_store_id:
        return {"error": "app_store_id and play_store_id are required"}, 400

    return Response(
        run_analysis(app_name, app_store_id, play_store_id, markets_raw, days_back, min_rating, max_rating),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    app.run(debug=True, port=8080, threaded=True)
