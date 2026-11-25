import os
import random
import requests

TONE = """
You are a friendly Nigerian entrepreneur who helps people start online side hustles.
Reply in Nigerian Pidgin English mixed with standard English.
Use expressions like: "How far", "Abeg", "Omo", "Sha", "No worry", "Chill".
Warm, encouraging, conversational.
"""

DM_WORDS = ["dm", "direct message", "inbox", "message me", "send message"]

def provider():
    k = os.getenv("BOT_API_KEY", "").strip()
    if k.startswith("AIza"):
        return "gemini"
    if k.startswith("sk-"):
        return "openai"
    return "none"

def _fallback(text, author):
    c = text.lower()
    if "how" in c or "start" in c:
        return f"How far @{author}! I see say you wan start. Send DM abeg, I go show you step by step. No charge! \U0001F4E9"
    if "money" in c or "pay" in c:
        return f"@{author} Omo, I dey make am daily! Send DM make I show you the platform. No scam, just hustle! \U0001F4B0\U0001F4E9"
    if "help" in c or "please" in c:
        return f"@{author} No worry, I got you! Send DM, I go guide you. Make we chop this money together! \U0001F91D\U0001F4E9"
    return random.choice([
        f"How far @{author}! I like your energy. Send DM make I show you how I dey do am! \U0001F4E9",
        f"@{author} Omo, you sabi! Check your DM, I wan share something with you! \U0001F525\U0001F4E9",
        f"@{author} DM abeg! I get something wey fit help you. No wahala! \U0001F4E9",
    ])

def _prompt(comment, author):
    return f"""Reply to this TikTok comment from someone interested in making money online.

Comment from @{author}: "{comment}"

{TONE}

Rules: acknowledge their point, one short curiosity teaser, invite them to DM. Max 2 sentences. DM invite mandatory."""

def _gemini(key, prompt):
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           f"gemini-2.5-flash:generateContent?key={key}")
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.9, "maxOutputTokens": 200}}
    r = requests.post(url, json=body, timeout=30)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

def _openai(key, prompt):
    from openai import OpenAI
    r = OpenAI(api_key=key).chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=120,
        temperature=0.9,
    )
    return r.choices[0].message.content.strip()

def generate_dm_response(comment_text, author_username):
    key = os.getenv("BOT_API_KEY", "").strip()
    p = provider()
    if p == "none":
        return _fallback(comment_text, author_username)
    try:
        raw = _gemini(key, _prompt(comment_text, author_username)) if p == "gemini" \
              else _openai(key, _prompt(comment_text, author_username))
        if not any(w in raw.lower() for w in DM_WORDS):
            raw += " Send DM make I show you the way! \U0001F4E9"
        return raw
    except Exception as e:
        print(f"[ai] {e}")
        return _fallback(comment_text, author_username)