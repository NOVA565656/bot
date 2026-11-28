from jnius import autoclass, PythonJavaClass, java_method
from kivy.clock import Clock
from kivy.metrics import dp
import traceback

PythonActivity = autoclass('org.kivy.android.PythonActivity')
WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
CookieManager = autoclass('android.webkit.CookieManager')
FrameLayout = autoclass('android.widget.FrameLayout')
FrameLayoutParams = autoclass('android.widget.FrameLayout$LayoutParams')
Button = autoclass('android.widget.Button')
Color = autoclass('android.graphics.Color')
Gravity = autoclass('android.view.Gravity')
ValueCallback = autoclass('android.webkit.ValueCallback')

_keep_refs = {}

class ButtonListener(PythonJavaClass):
    __javainterfaces__ = ['android/view/View$OnClickListener']
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
    @java_method('(Landroid/view/View;)V')
    def onClick(self, view):
        self.callback()

# ✅ FIX 1: THE DEEP LINK BLOCKER (From your guide)
class MyWebViewClient(PythonJavaClass):
    __javainterfaces__ = ['android/webkit/WebViewClient']
    
    @java_method('(Landroid/webkit/WebView;Ljava/lang/String;)Z')
    def shouldOverrideUrlLoading(self, view, url):
        return self._handle_url(url)
        
    @java_method('(Landroid/webkit/WebView;Landroid/webkit/WebResourceRequest;)Z')
    def shouldOverrideUrlLoading(self, view, request):
        return self._handle_url(request.getUrl().toString())
        
    def _handle_url(self, url):
        # Block intent://, snssdk://, etc., to prevent the app from crashing
        if url.startswith("intent://") or url.startswith("snssdk://") or "onelink.me" in url:
            print(f"[WebView] Blocked deep link: {url}")
            return True # Return True means "I handled it, don't open the native app"
        return False

# ✅ FIX 2: JavaScript Cookie Extractor (From your guide)
class JsCallback(PythonJavaClass):
    __javainterfaces__ = ['android/webkit/ValueCallback']
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @java_method('(Ljava/lang/Object;)V')
    def onReceiveValue(self, value):
        if value:
            # Clean up the JSON quotes Flutter used
            raw = value
            if raw.startswith('"') and raw.endswith('"'):
                raw = raw[1:-1]
            self.callback(raw)

def open_login(on_captured):
    def _open():
        try:
            activity = PythonActivity.mActivity
            
            frame = FrameLayout(activity)
            frame.setBackgroundColor(Color.parseColor("#1E1E24"))
            _keep_refs['frame'] = frame

            web = WebView(activity)
            web.getSettings().setJavaScriptEnabled(True)
            web.getSettings().setDomStorageEnabled(True)
            web.getSettings().setDatabaseEnabled(True)
            # Spoof a standard Chrome browser
            web.getSettings().setUserAgentString("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36")
            
            client = MyWebViewClient()
            web.setWebViewClient(client)
            _keep_refs['client'] = client

            # ✅ FIX 3: Inject JS to kill Cookie/Popup banners
            js_popup_killer = """
            setInterval(function() {
                var btns = document.querySelectorAll('button, div[role="button"]');
                for (var i = 0; i < btns.length; i++) {
                    var txt = btns[i].innerText.toLowerCase();
                    if (txt.includes('accept') || txt.includes('allow') || txt.includes('agree')) {
                        btns[i].click();
                    }
                }
            }, 2000);
            """
            
            # Load the page, then run the popup killer
            web.loadUrl("https://www.tiktok.com/login")
            
            _keep_refs['web'] = web

            lp_web = FrameLayoutParams(-1, -1)
            frame.addView(web, lp_web)

            btn = Button(activity)
            btn.setText("SAVE & CLOSE")
            btn.setBackgroundColor(Color.parseColor("#FE2C55"))
            btn.setTextColor(Color.parseColor("#FFFFFF"))

            def do_save():
                # Run document.cookie via JS to get HttpOnly cookies
                js_extract = "document.cookie"
                
                def on_js_result(cookie_string):
                    if not cookie_string:
                        # Fallback to native CookieManager if JS fails
                        cm = CookieManager.getInstance()
                        cookie_string = cm.getCookie("https://www.tiktok.com") or ""
                    
                    _close(frame)
                    Clock.schedule_once(lambda dt: on_captured(cookie_string), 0)

                js_cb = JsCallback(on_js_result)
                _keep_refs['js_cb'] = js_cb
                web.evaluateJavascript(js_extract, js_cb)

            listener = ButtonListener(do_save)
            _keep_refs['listener'] = listener
            btn.setOnClickListener(listener)

            lp_btn = FrameLayoutParams(-1, -2)
            lp_btn.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL
            margin_px = int(dp(20))
            lp_btn.setMargins(margin_px, margin_px, margin_px, margin_px)
            
            frame.addView(btn, lp_btn)

            activity.addContentView(frame, FrameLayoutParams(-1, -1))
            frame.bringToFront()
            
            # Inject popup killer after a short delay to let the page load
            Clock.schedule_once(lambda dt: web.evaluateJavascript(js_popup_killer, None), 3.0)
            
        except Exception as e:
            Clock.schedule_once(lambda dt: on_captured(f"ERROR: {str(e)}"), 0)

    PythonActivity.mActivity.runOnUiThread(_open)

def _close(frame):
    try:
        frame.setVisibility(8) # View.GONE
        parent = frame.getParent()
        if parent:
            parent.removeView(frame)
        frame.removeAllViews()
    except Exception as e:
        print(f"Close error: {e}")
    _keep_refs.clear()