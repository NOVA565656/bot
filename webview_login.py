from jnius import autoclass, PythonJavaClass, java_method
from android.runnable import run_on_ui_thread
from kivy.clock import Clock

PythonActivity = autoclass('org.kivy.android.PythonActivity')
WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
CookieManager = autoclass('android.webkit.CookieManager')
FrameLayout = autoclass('android.widget.FrameLayout')
Button = autoclass('android.widget.Button')
LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
View = autoclass('android.view.View')
Color = autoclass('android.graphics.Color')

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

    activity = PythonActivity.mActivity

    frame = FrameLayout(activity)
    web = WebView(activity)
    web.getSettings().setJavaScriptEnabled(True)
    web.getSettings().setDomStorageEnabled(True)
    web.getSettings().setDatabaseEnabled(True)
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
    lp = LayoutParams(-1, 140)
    lp.gravity = 80  # BOTTOM
    lp.bottomMargin = 30
    lp.leftMargin = 30
    lp.rightMargin = 30
    frame.addView(btn, lp)

    def do_save():
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


@run_on_ui_thread
def _close(frame):
    try:
        frame.setVisibility(View.GONE)
        parent = frame.getParent()
        if parent:
            parent.removeView(frame)
        frame.removeAllViews()
    except Exception as e:
        print(f"[webview] close error: {e}")
    _keep.clear()