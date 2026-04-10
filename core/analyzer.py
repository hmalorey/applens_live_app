import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

# ── Prompt ────────────────────────────────────────────────────
# We ask Claude to return strict JSON so the frontend can consume
# it directly without any parsing or regex.

SYSTEM_PROMPT = """You are an expert product analyst. You analyze app store reviews and return structured JSON.
Always respond with valid JSON only — no markdown, no commentary, no code fences."""

def _build_prompt(app_name: str, days_back: int, negative_text: str, positive_text: str, n_neg: int, n_pos: int) -> str:
    return f"""Analyze these app store reviews for "{app_name}" (last {days_back} days).

You have {n_neg} negative reviews (1-2 stars) and {n_pos} positive reviews (4-5 stars).

Return a JSON object with exactly this structure:
{{
  "problems": [
    {{
      "title": "Short issue name",
      "desc": "1-2 sentence description of what users complain about",
      "count": <approximate number of reviews mentioning this>,
      "severity": "Critical" | "High" | "Medium"
    }}
  ],
  "strengths": [
    {{
      "title": "Short strength name",
      "desc": "1-2 sentence description of what users praise",
      "count": <approximate number of reviews mentioning this>
    }}
  ]
}}

Rules:
- Return exactly 5 problems and 3 strengths
- Severity: Critical = affects core functionality or trust, High = significant friction, Medium = annoyance
- counts should be realistic approximations based on the review volume
- Titles should be concise (3-6 words)
- Descriptions should be specific and actionable for a product manager

--- NEGATIVE REVIEWS ({n_neg} total) ---
{negative_text}

--- POSITIVE REVIEWS ({n_pos} total) ---
{positive_text}"""


def _format_reviews(reviews: list[dict], max_chars: int = 80000) -> str:
    lines = []
    for r in reviews:
        lines.append(
            f"[{r['source']} | {r['rating']}★ | {r['country']} | {r['date']}]\n{r['review']}"
        )
    text = "\n\n".join(lines)
    if len(text) > max_chars:
        text = text[:max_chars] + "\n[...truncated]"
    return text


def analyze(app_name: str, reviews: list[dict], days_back: int) -> dict:
    """
    Call Claude to analyze reviews and return problems + strengths as dicts.

    Returns:
        {
            "problems": [...],
            "strengths": [...]
        }
    Falls back to a minimal error dict if the API call fails.
    """
    negative = [r for r in reviews if r["rating"] <= 2]
    positive = [r for r in reviews if r["rating"] >= 4]

    negative_text = _format_reviews(negative)
    positive_text = _format_reviews(positive, max_chars=20000)

    prompt = _build_prompt(
        app_name=app_name,
        days_back=days_back,
        negative_text=negative_text,
        positive_text=positive_text,
        n_neg=len(negative),
        n_pos=len(positive),
    )

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = next(block.text for block in message.content if block.type == "text").strip()

    # Strip code fences if Claude added them despite instructions
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)
