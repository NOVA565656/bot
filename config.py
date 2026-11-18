# Search parameters
NICHE_KEYWORDS = [
    "online money",
    "side hustle",
    "make money online",
    "remote work",
    "passive income",
    "work from home",
    "online business",
    "freelancing",
    "digital nomad"
]

# Comment indicators of interest
INTEREST_SIGNALS = [
    "how", "where", "interested", "want", "start", "learn", 
    "please", "help", "dm", "info", "details", "guide",
    "teach", "show", "beginner", "newbie", "looking for"
]

# Nigeria Pidgin/Tone settings
TONE_INSTRUCTIONS = """
Respond in friendly Nigerian Pidgin English mixed with standard English. 
Use expressions like: "How far", "Abeg", "Omo", "Sha", "Wahala", "No worry".
Be warm, encouraging, and conversational. Keep it authentic but professional enough for business.
"""

# Limits (to avoid ban)
MAX_DAILY_COMMENTS = 20
DELAY_BETWEEN_COMMENTS = (30, 120)  # seconds