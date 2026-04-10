# AppLens

## Problem to solve

Product managers lack a fast, reliable way to keep a pulse on what users are saying in app store reviews. Without it, store rating drops go unnoticed and critical issues flagged by users get missed — slowing down the team's ability to react and fix.

## What this is

AppLens is a web app that pulls reviews from the App Store and Play Store across multiple EU markets, runs them through AI, and surfaces the top issues and strengths in a clean, readable interface — in a few minutes, with no manual work.

Built as the live follow-up to the [exploration notebook](https://github.com/hmalorey/app_reviews_analyzer).

## How it works

1. Select an app and markets in the UI
2. The backend scrapes both stores in real time
3. Reviews are passed to Claude which returns structured insights (top 5 issues, top 3 strengths)
4. Results are streamed back to the UI as they complete — no waiting for a full page reload

## How it works

1. Select an app from the list (or enter custom store IDs) and pick your markets
2. Click "Run analysis" — the backend scrapes both the App Store (via iTunes RSS feed) and Play Store (via `google-play-scraper`) in real time
3. Progress is streamed to the UI step by step via Server-Sent Events — no waiting for a full page reload
4. Reviews are passed to Claude which returns structured JSON: top 5 issues with severity + top 3 strengths
5. Results are injected directly into the UI — ratings, distributions, cards, and the full reviews table

## Stack

- **Scraping** — iTunes RSS feed (App Store) + `google-play-scraper` (Play Store)
- **Analysis** — Claude API (`claude-opus-4-6`) with structured JSON output
- **Backend** — Python + Flask + Server-Sent Events
- **Frontend** — Single HTML file, vanilla JS (`fetch` + `EventSource`)

## Structure

```
applens.html      # UI — HTML + CSS + vanilla JS
server.py         # Flask API — SSE endpoint
config.py         # Markets, defaults, constants
core/
  scraper.py      # App Store + Play Store scraping
  ratings.py      # All-time ratings + distributions
  analyzer.py     # Claude prompt + JSON parsing
```

## Run it

**1. Set up your API key**

Create a `.env` file at the root of the project:
```
ANTHROPIC_API_KEY=your_api_key_here
```
Get your key at [console.anthropic.com](https://console.anthropic.com).

**2. Install and start**

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

Then open `http://127.0.0.1:8080`.
