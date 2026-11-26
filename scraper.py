import requests
import random
import string
from signer import sign_query

BASE = "https://api16-normal-c-useast1a.tiktokv.com"
UA = ("com.zhiliaoapp.musically/2022600030 (Linux; U; Android 12; en; "
      "Pixel 5; Build/SQ3A.220705.004; Cronet/58.0.2991.0)")

def _tok(n=32):
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(n))

def _h(session_id):
    if "=" in session_id:
        cookie_str = session_id
    else:
        cookie_str = f"sessionid={session_id}; msToken={_tok(100)}"
        
    return {"User-Agent": UA, "Accept": "application/json", "Cookie": cookie_str}

def _get(path, params, session_id):
    q = sign_query(path, params, UA)
    r = requests.get(f"{BASE}{path}?{q}", headers=_h(session_id), timeout=25)
    r.raise_for_status()
    return r.json()

def search_videos(keyword, session_id, count=10):
    p = {"keyword": keyword, "count": count, "offset": 0, "aid": 1128,
         "version_code": "260103", "device_platform": "android"}
    out = []
    for item in (_get("/aweme/v1/general/search/single/", p, session_id).get("data") or []):
        a = item.get("aweme_info") or {}
        if not a:
            continue
        out.append({"id": a.get("aweme_id"),
                    "author": (a.get("author") or {}).get("unique_id", ""),
                    "desc": a.get("desc", ""),
                    "comment_count": (a.get("statistics") or {}).get("comment_count", 0)})
    return out

def get_video_comments(video_id, session_id, max_comments=30):
    p = {"aweme_id": video_id, "count": max_comments, "cursor": 0, "aid": 1128}
    out = []
    for c in (_get("/aweme/v1/comment/list/", p, session_id).get("comments") or []):
        out.append({"comment_id": c.get("cid"), "text": c.get("text", ""),
                    "author": (c.get("user") or {}).get("unique_id", ""),
                    "likes": c.get("digg_count", 0)})
    return out