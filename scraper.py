from TikTokApi import TikTokApi
import asyncio
import random

async def get_niche_videos(keyword, count=10):
    """Fetch videos related to side hustle niche"""
    async with TikTokApi() as api:
        videos = []
        async for video in api.search.search_videos(keyword, count=count):
            videos.append({
                'id': video.id,
                'author': video.author.username,
                'desc': video.desc,
                'comment_count': video.stats.comments
            })
        return videos

async def get_video_comments(video_id, max_comments=50):
    """Fetch comments from a specific video"""
    async with TikTokApi() as api:
        comments = []
        video = api.video(id=video_id)
        
        async for comment in video.comments(count=max_comments):
            comments.append({
                'comment_id': comment.id,
                'text': comment.text,
                'author': comment.author.username,
                'likes': comment.likes_count
            })
        return comments