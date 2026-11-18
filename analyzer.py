from config import INTEREST_SIGNALS
import re

def is_interested_comment(comment_text):
    """
    Analyze if comment shows interest in making money online
    Returns: (is_interested, confidence_score)
    """
    text_lower = comment_text.lower()
    
    # Check for interest signals
    signal_matches = sum(1 for signal in INTEREST_SIGNALS if signal in text_lower)
    
    # Question indicators
    has_question = '?' in comment_text
    is_asking_how = any(word in text_lower for word in ['how can', 'how do', 'how to'])
    
    # Avoid spam/red flags
    spam_words = ['scam', 'fake', 'impossible', 'lies']
    if any(word in text_lower for word in spam_words):
        return False, 0
    
    # Calculate interest score
    score = signal_matches * 0.3
    if has_question: score += 0.4
    if is_asking_how: score += 0.5
    
    return score >= 0.5, score

def extract_potential_leads(comments):
    """Filter comments to find potential leads"""
    leads = []
    for comment in comments:
        is_interested, score = is_interested_comment(comment['text'])
        if is_interested:
            leads.append({
                **comment,
                'interest_score': score
            })
    return sorted(leads, key=lambda x: x['interest_score'], reverse=True)