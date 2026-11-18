import requests
import time
import random
from config import DELAY_BETWEEN_COMMENTS
from response_generator import generate_naija_response  

def post_comment(video_id, comment_text, session_id):
    """
    Post comment to TikTok video
    NOTE: This requires session cookies from logged-in account
    """
    url = "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/comment/publish"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
        'Referer': 'https://www.tiktok.com/',
        'Cookie': f'sessionid={session_id}'
    }
    
    data = {
        'aweme_id': video_id,
        'text': comment_text,
        'is_self_see': 0
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        return response.status_code == 200
    except Exception as e:
        print(f"Error posting comment: {e}")
        return False

def auto_reply_with_delay(leads, video_id, session_id):
    """Reply to leads with human-like delays"""
    for lead in leads:
        response_text = generate_naija_response(lead['text'], lead['author'])
        
        success = post_comment(video_id, response_text, session_id)
        
        if success:
            print(f"✅ Replied to @{lead['author']}: {response_text[:50]}...")
        
        # Random delay to avoid bot detection
        delay = random.randint(*DELAY_BETWEEN_COMMENTS)
        print(f"⏳ Waiting {delay}s before next comment...")
        time.sleep(delay)