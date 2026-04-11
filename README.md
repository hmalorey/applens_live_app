# AppLens

## Problem to solve

Product managers lack a fast, reliable way to keep a pulse on what users are saying in app store reviews. Without it, store rating drops go unnoticed and critical issues flagged by users get missed — slowing down the team's ability to react and fix.

## What this is

AppLens is a web app that pulls reviews from the App Store and Play Store across multiple EU markets, runs them through AI, and surfaces the top issues and strengths in a clean, readable interface — in a few minutes, with no manual work.

Built as the live follow-up to the [exploration notebook](https://github.com/hmalorey/app_reviews_analyzer).


<img width="876" height="777" alt="Capture d’écran 2026-04-10 à 22 35 11" src="https://github.com/user-attachments/assets/df0d7251-919a-485a-a864-57f941f0c343" />
<img width="1500" height="787" alt="Capture d’écran 2026-04-10 à 22 44 38" src="https://github.com/user-attachments/assets/4286539b-3d20-4bae-bbce-e7283a37c22e" />
<img width="1490" height="784" alt="Capture d’écran 2026-04-10 à 22 44 45" src="https://github.com/user-attachments/assets/57a104b7-c18b-46e8-ba6e-fecda8bff917" />
<img width="1057" height="582" alt="Capture d’écran 2026-04-10 à 22 45 31" src="https://github.com/user-attachments/assets/57b69a30-f241-4af0-b5aa-5ed1d6dcf296" />
<img width="1076" height="738" alt="Capture d’écran 2026-04-10 à 22 45 49" src="https://github.com/user-attachments/assets/b8f8923c-3d2d-4993-ae63-3fa18906f4d7" />


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
