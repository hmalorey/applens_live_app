from datetime import datetime, timedelta, timezone

# ── Analysis defaults ─────────────────────────────────────────
DAYS_BACK  = 90
MIN_RATING = 1
MAX_RATING = 5

# ── Review schema ─────────────────────────────────────────────
COLUMNS = ["date", "review", "rating", "source", "language", "country", "answered", "username"]

# ── Markets ───────────────────────────────────────────────────
# Each entry: country code (used in store URLs) + language code (used by Play Store)
MARKETS_ALL = [
    {"country": "fr", "language": "fr"},  # France
    {"country": "de", "language": "de"},  # Germany
    {"country": "es", "language": "es"},  # Spain
    {"country": "it", "language": "it"},  # Italy
    {"country": "us", "language": "en"},  # United States
]

# Human-readable name → country code mapping (for the HTML → API bridge)
MARKET_NAME_TO_CODE = {
    "France":         "fr",
    "Germany":        "de",
    "Spain":          "es",
    "Italy":          "it",
    "United States":  "us",
}

# ── Known apps ────────────────────────────────────────────────
KNOWN_APPS = {
    "revenuecat": {"app_store_id": "6504531798",   "play_store_id": "com.revenuecat.mobile"},
    "airbnb":     {"app_store_id": "401626263",    "play_store_id": "com.airbnb.android"},
    "linear":     {"app_store_id": "1645587184",   "play_store_id": "app.linear"},
    "revolut":    {"app_store_id": "932493382",    "play_store_id": "com.revolut.revolut"},
    "coinbase":   {"app_store_id": "886427730",    "play_store_id": "com.coinbase.android"},
    "bitstack":   {"app_store_id": "1608783388",   "play_store_id": "com.bitstack.app"},
    "alan":       {"app_store_id": "1277025964",   "play_store_id": "com.alanmobile"},
}


def cutoff_date(days_back: int = DAYS_BACK):
    return datetime.now(timezone.utc) - timedelta(days=days_back)


def markets_from_names(names: list[str]) -> list[dict]:
    """Convert a list of human-readable market names to market dicts."""
    result = []
    for name in names:
        code = MARKET_NAME_TO_CODE.get(name)
        if code:
            match = next((m for m in MARKETS_ALL if m["country"] == code), None)
            if match:
                result.append(match)
    return result or [MARKETS_ALL[0]]  # fallback to France
