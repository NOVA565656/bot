import urllib.parse

try:
    from TikTokSigner import TikTokSigner
    _S = TikTokSigner()
except Exception:
    _S = None

def available():
    return _S is not None

def sign_query(path, params, ua):
    qs = urllib.parse.urlencode(sorted(params.items()))
    if _S is None:
        return qs
    try:
        xb = _S.sign_x_bogus(f"https://www.tiktok.com{path}?{qs}", ua)
        if xb:
            return qs + "&X-Bogus=" + urllib.parse.quote(xb, safe="")
    except Exception as e:
        print(f"[sign] {e}")
    return qs