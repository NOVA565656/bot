import asyncio
import schedule
import time
import random 
from datetime import datetime
from scraper import get_niche_videos, get_video_comments
from analyzer import extract_potential_leads
from commenter import auto_reply_with_delay
from config import NICHE_KEYWORDS, MAX_DAILY_COMMENTS

# Track daily limits
daily_comment_count = 0

async def run_bot():
    global daily_comment_count
    
    print(f"🚀 Starting TikTok Side Hustle Bot at {datetime.now()}")
    
    # Rotate through keywords
    for keyword in NICHE_KEYWORDS:
        if daily_comment_count >= MAX_DAILY_COMMENTS:
            print("📊 Daily limit reached. Stopping.")
            break
            
        print(f"\n🔍 Searching for: {keyword}")
        
        # Get videos
        videos = await get_niche_videos(keyword, count=5)
        
        for video in videos:
            if daily_comment_count >= MAX_DAILY_COMMENTS:
                break
                
            print(f"📹 Checking video: {video['desc'][:50]}...")
            
            # Get comments
            comments = await get_video_comments(video['id'], max_comments=30)
            
            # Find interested people
            leads = extract_potential_leads(comments)
            
            if leads:
                print(f"🎯 Found {len(leads)} potential leads!")
                
                # Reply to top leads (limit per video)
                for lead in leads[:3]:
                    if daily_comment_count >= MAX_DAILY_COMMENTS:
                        break
                    
                    # Post reply (you'll need to implement auth)
                    # auto_reply_with_delay([lead], video['id'], SESSION_ID)
                    daily_comment_count += 1
                    
            # Delay between videos
            time.sleep(random.randint(60, 180))

def daily_job():
    """Run the bot daily"""
    global daily_comment_count
    daily_comment_count = 0
    asyncio.run(run_bot())

# Schedule
schedule.every().day.at("09:00").do(daily_job)
schedule.every().day.at("18:00").do(daily_job)

if __name__ == "__main__":
    print("🤖 Bot is running. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(60)