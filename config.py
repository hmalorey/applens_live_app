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
    {"country": "gb", "language": "en"},  # United Kingdom
    {"country": "es", "language": "es"},  # Spain
    {"country": "it", "language": "it"},  # Italy
    {"country": "nl", "language": "nl"},  # Netherlands
    {"country": "be", "language": "fr"},  # Belgium
    {"country": "pt", "language": "pt"},  # Portugal
    {"country": "pl", "language": "pl"},  # Poland
    {"country": "se", "language": "sv"},  # Sweden
    {"country": "dk", "language": "da"},  # Denmark
    {"country": "fi", "language": "fi"},  # Finland
    {"country": "at", "language": "de"},  # Austria
    {"country": "ch", "language": "fr"},  # Switzerland
]

# Human-readable name → country code mapping (for the HTML → API bridge)
MARKET_NAME_TO_CODE = {
    "France":         "fr",
    "Germany":        "de",
    "United Kingdom": "gb",
    "Spain":          "es",
    "Italy":          "it",
    "Netherlands":    "nl",
    "Belgium":        "be",
    "Portugal":       "pt",
    "Poland":         "pl",
    "Sweden":         "se",
    "Denmark":        "dk",
    "Finland":        "fi",
    "Austria":        "at",
    "Switzerland":    "ch",
}

# ── Known apps ────────────────────────────────────────────────
KNOWN_APPS = {
    "airbnb":   {"app_store_id": "401626263",   "play_store_id": "com.airbnb.android"},
    "linear":   {"app_store_id": "1469439646",  "play_store_id": "io.linear"},
    "revolut":  {"app_store_id": "932493386",   "play_store_id": "com.revolut.revolut"},
    "coinbase": {"app_store_id": "886427730",   "play_store_id": "com.coinbase.android"},
    "bitstack": {"app_store_id": "1608783388",  "play_store_id": "com.bitstack.app"},
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
