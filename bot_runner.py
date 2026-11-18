import asyncio
import random
import time
from datetime import datetime
from scraper import get_niche_videos, get_video_comments
from analyzer import extract_potential_leads
from response_generator import generate_dm_response
from commenter import post_comment
import database as db

async def run_multi_account_bot():
    """Run bot across all active accounts with rotation"""
    
    accounts = db.get_active_accounts()
    
    if not accounts:
        print("❌ No active accounts found!")
        return
    
    print(f"🚀 Starting bot with {len(accounts)} accounts")
    
    # Each account gets some of the keywords
    keywords = [
        "online money", "side hustle", "make money online", 
        "remote work", "passive income", "work from home"
    ]
    
    # Rotate through accounts
    for i, account in enumerate(accounts):
        print(f"\n👤 Using account: {account['name']} (@{account['username']})")
        
        # Get subset of keywords for this account
        account_keywords = keywords[i % len(keywords):] + keywords[:i % len(keywords)]
        
        for keyword in account_keywords[:2]:  # 2 keywords per account
            print(f"🔍 Searching: {keyword}")
            
            try:
                videos = await get_niche_videos(keyword, count=3)
                
                for video in videos:
                    comments = await get_video_comments(video['id'], max_comments=20)
                    leads = extract_potential_leads(comments)
                    
                    for lead in leads[:2]:  # Max 2 replies per video
                        # Check if already replied
                        if db.is_already_replied(lead['comment_id']):
                            continue
                        
                        # Generate DM-focused reply
                        reply_text = generate_dm_response(
                            lead['text'], 
                            lead['author']
                        )
                        
                        # Post comment
                        success = post_comment(
                            video['id'], 
                            reply_text, 
                            account['session_id']
                        )
                        
                        if success:
                            db.mark_comment_replied(
                                account['id'],
                                lead['comment_id'],
                                video['id'],
                                reply_text
                            )
                            print(f"✅ Replied to @{lead['author']}: {reply_text[:50]}...")
                            
                            # Random delay between accounts
                            time.sleep(random.randint(60, 180))
                            
            except Exception as e:
                print(f"❌ Error with account {account['name']}: {e}")
                continue
        
        # Delay between account switches
        time.sleep(random.randint(120, 300))
    
    print("✅ Bot run completed")

if __name__ == "__main__":
    asyncio.run(run_multi_account_bot())