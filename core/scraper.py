import requests
from datetime import datetime, timezone
from google_play_scraper import reviews, Sort


def scrape_app_store(app_store_id: str, markets: list[dict], cutoff_date, min_rating: int, max_rating: int, pages: int = 5) -> list[dict]:
    """
    Scrape App Store reviews via the iTunes public RSS feed.
    Returns a list of review dicts matching COLUMNS schema.
    Title is concatenated into the review field for consistency with Play Store.
    """
    results = []

    for market in markets:
        country  = market["country"]
        language = market["language"]
        count    = 0

        for page in range(1, pages + 1):
            url = (
                f"https://itunes.apple.com/{country}/rss/customerreviews"
                f"/page={page}/id={app_store_id}/sortby=mostrecent/json"
            )
            try:
                resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            except requests.exceptions.Timeout:
                break

            if resp.status_code != 200:
                break

            entries = resp.json().get("feed", {}).get("entry", [])
            if not entries:
                break

            # Apple returns a dict instead of a list when there's only 1 entry
            if isinstance(entries, dict):
                entries = [entries]

            stop = False
            for entry in entries:
                rating   = int(entry.get("im:rating", {}).get("label", 5))
                date_str = entry.get("updated", {}).get("label", "")[:10]

                try:
                    date = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
                except ValueError:
                    continue

                if date < cutoff_date:
                    stop = True
                    break

                if not (min_rating <= rating <= max_rating):
                    continue

                title   = entry.get("title",   {}).get("label", "")
                content = entry.get("content", {}).get("label", "")
                review  = " — ".join(filter(None, [title, content]))

                results.append({
                    "date":     date.strftime("%Y-%m-%d"),
                    "review":   review,
                    "rating":   rating,
                    "source":   "App Store",
                    "language": language,
                    "country":  country.upper(),
                    "answered": False,
                    "username": entry.get("author", {}).get("name", {}).get("label", "anonymous"),
                })
                count += 1

            if stop:
                break

    return results


def scrape_play_store(play_store_id: str, markets: list[dict], cutoff_date, min_rating: int, max_rating: int, count: int = 300) -> list[dict]:
    """
    Scrape Play Store reviews via google-play-scraper.
    Fetches per star rating to get even coverage across ratings.
    Returns a list of review dicts matching COLUMNS schema.
    """
    results = []

    for market in markets:
        country  = market["country"]
        language = market["language"]

        for star in range(min_rating, max_rating + 1):
            try:
                fetched, _ = reviews(
                    play_store_id,
                    lang=language,
                    country=country,
                    sort=Sort.NEWEST,
                    count=count,
                    filter_score_with=star,
                )
            except Exception:
                continue

            for r in fetched:
                date = r["at"]
                if date.tzinfo is None:
                    date = date.replace(tzinfo=timezone.utc)

                if date < cutoff_date:
                    continue

                results.append({
                    "date":     date.strftime("%Y-%m-%d"),
                    "review":   r.get("content", ""),
                    "rating":   r["score"],
                    "source":   "Play Store",
                    "language": language,
                    "country":  country.upper(),
                    "answered": r.get("replyContent") is not None,
                    "username": r.get("userName", "anonymous"),
                })

    return results
