import requests
import random

BASE = "https://api16-normal-c-useast1a.tiktokv.com"
UA = ("com.zhiliaoapp.musically/2022600030 (Linux; U; Android 12; en; "
      "Pixel 5; Build/SQ3A.220705.004; Cronet/58.0.2991.0)")

def _h(session_id):
    return {
        "User-Agent": UA,
        "Accept": "application/json",
        "Cookie": f"sessionid={session_id}",
    }

def search_videos(keyword, session_id, count=10):
    url = f"{BASE}/aweme/v1/general/search/single/"
    p = {"keyword": keyword, "count": count, "offset": 0, "aid": 1128,
         "version_code": "260103", "device_platform": "android"}
    r = requests.get(url, params=p, headers=_h(session_id), timeout=20)
    data = r.json().get("data") or []
    out = []
    for item in data:
        a = item.get("aweme_info") or {}
        if not a:
            continue
        out.append({
            "id": a.get("aweme_id"),
            "author": (a.get("author") or {}).get("unique_id", ""),
            "desc": a.get("desc", ""),
            "comment_count": (a.get("statistics") or {}).get("comment_count", 0),
        })
    return out

def get_video_comments(video_id, session_id, max_comments=30):
    url = f"{BASE}/aweme/v1/comment/list/"
    p = {"aweme_id": video_id, "count": max_comments, "cursor": 0, "aid": 1128}
    r = requests.get(url, params=p, headers=_h(session_id), timeout=20)
    out = []
    for c in (r.json().get("comments") or []):
        out.append({
            "comment_id": c.get("cid"),
            "text": c.get("text", ""),
            "author": (c.get("user") or {}).get("unique_id", ""),
            "likes": c.get("digg_count", 0),
        })
    return out