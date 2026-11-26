import requests
import time
import random

from config import DELAY_BETWEEN_COMMENTS
from response_generator import generate_dm_response

UA = ("com.zhiliaoapp.musically/2022600030 (Linux; U; Android 12; en; "
      "Pixel 5; Build/SQ3A.220705.004; Cronet/58.0.2991.0)")

PUBLISH = "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/comment/publish/"


def post_comment(video_id, comment_text, session_id):
    if "=" in session_id:
        cookie_str = session_id
    else:
        cookie_str = f"sessionid={session_id}"

    headers = {
        "User-Agent": UA,
        "Accept": "application/json",
        "Cookie": cookie_str,
    }
    data = {
        "aweme_id": video_id,
        "text": comment_text,
        "is_self_see": 0,
        "text_extra": "[]",
        "aid": 1128,
    }

    try:
        r = requests.post(PUBLISH, data=data, headers=headers, timeout=25)
    except Exception as e:
        print(f"[post] network error: {e}")
        return False

    if r.status_code != 200:
        print(f"[post] HTTP {r.status_code}")
        return False

    try:
        j = r.json()
    except Exception:
        print("[post] non-JSON response")
        return False

    if j.get("status_code") == 0 and (j.get("comment") or {}).get("cid"):
        return True

    print(f"[post] rejected: status_code={j.get('status_code')} msg={j.get('status_msg')}")
    return False


def auto_reply_with_delay(leads, video_id, session_id):
    for lead in leads:
        text = generate_dm_response(lead["text"], lead["author"])
        if post_comment(video_id, text, session_id):
            print(f"OK @{lead['author']}: {text[:50]}")
        else:
            print(f"FAILED @{lead['author']}")
        time.sleep(random.randint(*DELAY_BETWEEN_COMMENTS))