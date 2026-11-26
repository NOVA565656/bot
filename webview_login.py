from jnius import autoclass, PythonJavaClass, java_method
from android.runnable import run_on_ui_thread
from kivy.clock import Clock
from kivy.metrics import dp

PythonActivity = autoclass('org.kivy.android.PythonActivity')
WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
CookieManager = autoclass('android.webkit.CookieManager')
FrameLayout = autoclass('android.widget.FrameLayout')
Button = autoclass('android.widget.Button')
LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
View = autoclass('android.view.View')
Color = autoclass('android.graphics.Color')
Gravity = autoclass('android.view.Gravity')

_keep = {}
_cm = None

class _Client(PythonJavaClass):
    __javainterfaces__ = ['android/webkit/WebViewClient']
    @java_method('(Landroid/webkit/WebView;Ljava/lang/String;)Z')
    def shouldOverrideUrlLoading(self, view, url):
        return False

class _Click(PythonJavaClass):
    __javainterfaces__ = ['android/view/View$OnClickListener']
    def __init__(self, cb):
        super().__init__()
        self.cb = cb
    @java_method('(Landroid/view/View;)V')
    def onClick(self, v):
        self.cb()

@run_on_ui_thread
def open_login(on_captured):
    global _cm
    print("[WebView] Button pressed, opening login...")
    try:
        activity = PythonActivity.mActivity

        frame = FrameLayout(activity)
        frame.setBackgroundColor(Color.parseColor("#1E1E24"))

        web = WebView(activity)
        web.getSettings().setJavaScriptEnabled(True)
        web.getSettings().setDomStorageEnabled(True)
        web.getSettings().setDatabaseEnabled(True)
        web.getSettings().setUserAgentString("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36")
        
        web.setWebViewClient(_Client())
        web.loadUrl("https://www.tiktok.com/login")

        _cm = CookieManager.getInstance()
        _cm.setAcceptCookie(True)
        _cm.setAcceptThirdPartyCookies(web, True)

        frame.addView(web, LayoutParams(-1, -1))

        btn = Button(activity)
        btn.setText("SAVE & CLOSE")
        btn.setBackgroundColor(Color.parseColor("#FE2C55"))
        btn.setTextColor(Color.parseColor("#FFFFFF"))
        
        btn_lp = FrameLayout.LayoutParams(-1, LayoutParams.WRAP_CONTENT)
        btn_lp.gravity = Gravity.BOTTOM
        margin = int(dp(20))
        btn_lp.setMargins(margin, margin, margin, margin)
        frame.addView(btn, btn_lp)

        def do_save():
            print("[WebView] Saving cookies...")
            cookie = _cm.getCookie("https://www.tiktok.com") or ""
            _close(frame)
            Clock.schedule_once(lambda dt: on_captured(cookie), 0)

        listener = _Click(do_save)
        btn.setOnClickListener(listener)

        _keep['frame'] = frame
        _keep['web'] = web
        _keep['listener'] = listener
        _keep['client'] = web.getWebViewClient()

        activity.addContentView(frame, LayoutParams(-1, -1))
        print("[WebView] Opened successfully")

    except Exception as e:
        print(f"[WebView] CRITICAL ERROR: {e}")

@run_on_ui_thread
def _close(frame):
    try:
        frame.setVisibility(View.GONE)
        parent = frame.getParent()
        if parent:
            parent.removeView(frame)
        frame.removeAllViews()
        print("[WebView] Closed.")
    except Exception as e:
        print(f"[WebView] close error: {e}")
    _keep.clear()