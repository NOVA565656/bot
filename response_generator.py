import os
import random
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TONE_INSTRUCTIONS = """
You are a friendly Nigerian entrepreneur who helps people start online side hustles.
Respond in Nigerian Pidgin English mixed with standard English.
Use expressions like: "How far", "Abeg", "Omo", "Sha", "Wahala", "No worry", "Chill".
Be warm, encouraging, and conversational.
"""

def generate_dm_response(comment_text, author_username, conversation_history=None):
    """
    Generate reply that naturally leads to DM conversation
    """
    
    prompt = f"""You are replying to a TikTok comment from someone interested in making money online.

Comment from @{author_username}: "{comment_text}"

{TONE_INSTRUCTIONS}

Craft a reply that:
1. Acknowledges their specific interest/question PERSONALLY (show you read their comment)
2. Gives a small teaser of value (1 sentence max) - make them curious
3. Naturally invites them to DM for details (e.g., "Send DM make I show you", "DM abeg, too long for here", "Check DM, I don send you tips")
4. Keep it under 2 sentences total
5. MUST include a soft DM invitation - this is critical

Examples of good DM invitations:
- "Send DM, I get the full guide"
- "DM abeg, I wan explain better"
- "Check your DM, I don send am"
- "Too long to explain here, send DM"

Reply:"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
            temperature=0.9
        )
        reply = response.choices[0].message.content.strip()
        
        # Ensure it mentions DM if AI forgot
        dm_keywords = ['dm', 'direct message', 'inbox', 'message me', 'send message']
        if not any(kw in reply.lower() for kw in dm_keywords):
            reply += " Send DM make I show you the way! 📩"
            
        return reply
        
    except Exception as e:
        # Smart fallback based on comment type
        comment_lower = comment_text.lower()
        
        if 'how' in comment_lower or 'start' in comment_lower:
            return f"How far @{author_username}! I see say you wan start. Send DM abeg, I go show you step by step. No charge! 📩"
        elif 'money' in comment_lower or 'pay' in comment_lower:
            return f"@{author_username} Omo, I dey make am daily! Send DM make I show you the platform. No scam, just hustle! 💰📩"
        elif 'help' in comment_lower or 'please' in comment_lower:
            return f"@{author_username} No worry, I got you! Send DM, I go guide you. Make we chop this money together! 🤝📩"
        else:
            fallbacks = [
                f"How far @{author_username}! I like your energy. Send DM make I show you how I dey do am! 📩",
                f"@{author_username} Omo, you sabi! Check your DM, I wan share something with you! 🔥📩",
                f"@{author_username} DM abeg! I get something wey fit help you. No wahala! 📩"
            ]
            return random.choice(fallbacks)