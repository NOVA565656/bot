import os
import random
from openai import OpenAI
import config
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_naija_response(comment_text, author_username):
    """
    Generate personalized Nigerian-style response
    Uses OpenAI API (you can swap for free local model)
    """
    
    prompt = f"""
    You're a friendly Nigerian entrepreneur who helps people start online side hustles.
    
    Original comment from @{author_username}: "{comment_text}"
    
    {config.TONE_INSTRUCTIONS}
    
    Write a short, engaging reply (max 2 sentences) that:
    1. Acknowledges their interest
    2. Offers value or invites them to learn more
    3. Sounds natural and warm
    4. Optionally includes a soft CTA like "Check my bio" or "Send DM"
    
    Reply:
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or gpt-4 if you have access
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Fallback responses in Nigerian Pidgin
        fallbacks = [
            f"How far @{author_username}! I see say you dey interested. Abeg check my bio, I get something wey fit help you start. No wahala! 🚀",
            f"Omo @{author_username}, I like your energy! If you wan learn how to start, just send DM. Make we chop this money together! 💪",
            f"@{author_username} No worry, e dey possible! I don guide plenty people. Check link for bio if you serious! 🔥"
        ]
        import random
        return random.choice(fallbacks)