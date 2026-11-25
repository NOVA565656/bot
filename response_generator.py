import os
import random
from openai import OpenAI

TONE_INSTRUCTIONS = """
You are a friendly Nigerian entrepreneur who helps people start online side hustles.
Respond in Nigerian Pidgin English mixed with standard English.
Use expressions like: "How far", "Abeg", "Omo", "Sha", "Wahala", "No worry", "Chill".
Be warm, encouraging, and conversational.
"""

DM_WORDS = ["dm", "direct message", "inbox", "message me", "send message", "check your dm"]

def _client():
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    try:
        return OpenAI(api_key=key)
    except Exception:
        return None


def _fallback(comment_text, author):
    c = comment_text.lower()
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


def generate_dm_response(comment_text, author_username):
    client = _client()
    if client is None:
        return _fallback(comment_text, author_username)

    prompt = f"""You are replying to a TikTok comment from someone interested in making money online.

Comment from @{author_username}: "{comment_text}"

{TONE_INSTRUCTIONS}

Craft a reply that:
1. Acknowledges their specific interest/question personally
2. Gives one short teaser that makes them curious
3. Invites them to DM for details
Keep it under 2 sentences. The DM invite is mandatory.

Reply:"""

    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
            temperature=0.9,
        )
        reply = r.choices[0].message.content.strip()
        if not any(w in reply.lower() for w in DM_WORDS):
            reply += " Send DM make I show you the way! \U0001F4E9"
        return reply
    except Exception:
        return _fallback(comment_text, author_username)