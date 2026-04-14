import requests
import pandas as pd
from google_play_scraper import app as play_app


def get_ratings(app_store_id: str, play_store_id: str, markets: list[dict], reviews: list[dict]) -> dict:
    """
    Compute all-time ratings (from store APIs) and 90-day averages + distributions
    (from the scraped reviews dataframe).

    Returns a dict ready to be sent as JSON to the frontend:
    {
        "ios_alltime":  4.2,
        "play_alltime": 4.0,
        "ios_90d":      3.8,
        "play_90d":     4.1,
        "ios_dist":     {"1": 18, "2": 10, "3": 8, "4": 14, "5": 50},
        "play_dist":    {"1": 12, "2": 8,  "3": 10, "4": 20, "5": 50},
    }
    Values can be None if data is unavailable.
    """
    df = pd.DataFrame(reviews) if reviews else pd.DataFrame(columns=["source", "rating", "country"])

    # ── All-time ratings (from store APIs, first available market) ──
    ios_alltime  = None
    play_alltime = None

    # All-time ratings are global — try selected markets first, then fallbacks
    fallback_markets = [{"country": "us", "language": "en"}, {"country": "fr", "language": "fr"}]
    markets_to_try = list(markets) + [m for m in fallback_markets if m not in markets]

    for market in markets_to_try:
        country  = market["country"]
        language = market["language"]

        if ios_alltime is None:
            try:
                lookup      = requests.get(
                    f"https://itunes.apple.com/lookup?id={app_store_id}&country={country}",
                    timeout=5,
                ).json().get("results", [{}])[0]
                score = lookup.get("averageUserRating")
                ios_alltime = round(score, 1) if score is not None else None
            except Exception:
                pass

        if play_alltime is None:
            try:
                data  = play_app(play_store_id, lang=language, country=country)
                score = data.get("score")
                play_alltime = round(score, 1) if score else None
            except Exception:
                pass

        if ios_alltime is not None and play_alltime is not None:
            break

    # ── 90-day averages from scraped data ────────────────────────
    df_ios  = df[df["source"] == "App Store"]  if not df.empty else pd.DataFrame()
    df_play = df[df["source"] == "Play Store"] if not df.empty else pd.DataFrame()

    ios_90d  = round(df_ios["rating"].mean(),  1) if len(df_ios)  > 0 else None
    play_90d = round(df_play["rating"].mean(), 1) if len(df_play) > 0 else None

    # Fall back to scraped average if store API returned nothing valid
    if ios_alltime  is None: ios_alltime  = ios_90d
    if play_alltime is None: play_alltime = play_90d

    # ── Rating distributions (percentage per star, 1–5) ──────────
    def distribution(df_store: pd.DataFrame) -> dict:
        if df_store.empty:
            return {str(s): 0 for s in range(1, 6)}
        total = len(df_store)
        return {
            str(star): round(len(df_store[df_store["rating"] == star]) / total * 100)
            for star in range(1, 6)
        }

    return {
        "ios_alltime":  ios_alltime,
        "play_alltime": play_alltime,
        "ios_90d":      ios_90d,
        "play_90d":     play_90d,
        "ios_dist":     distribution(df_ios),
        "play_dist":    distribution(df_play),
    }
