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

_keep_refs = {}

# ✅ Correct Java Interfaces for Android 9+
class ButtonListener(PythonJavaClass):
    __javainterfaces__ = ['android/view/View$OnClickListener']
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
    @java_method('(Landroid/view/View;)V')
    def onClick(self, view):
        self.callback()

class MyWebViewClient(PythonJavaClass):
    __javainterfaces__ = ['android/webkit/WebViewClient']
    
    # For Android < 7.0
    @java_method('(Landroid/webkit/WebView;Ljava/lang/String;)Z')
    def shouldOverrideUrlLoading(self, view, url):
        return False
        
    # For Android 7.0+
    @java_method('(Landroid/webkit/WebView;Landroid/webkit/WebResourceRequest;)Z')
    def shouldOverrideUrlLoading(self, view, request):
        return False

def open_login(on_captured):
    def _open():
        try:
            activity = PythonActivity.mActivity
            
            # 1. Create a full-screen FrameLayout
            frame = FrameLayout(activity)
            frame.setBackgroundColor(Color.parseColor("#1E1E24"))
            _keep_refs['frame'] = frame

            # 2. Create WebView
            web = WebView(activity)
            web.getSettings().setJavaScriptEnabled(True)
            web.getSettings().setDomStorageEnabled(True)
            web.getSettings().setDatabaseEnabled(True)
            web.getSettings().setUserAgentString("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36")
            
            client = MyWebViewClient()
            web.setWebViewClient(client)
            _keep_refs['client'] = client

            web.loadUrl("https://www.tiktok.com/login")
            _keep_refs['web'] = web

            # Fill the screen (-1 is MATCH_PARENT)
            lp_web = FrameLayoutParams(-1, -1)
            frame.addView(web, lp_web)

            # 3. Create Save Button
            btn = Button(activity)
            btn.setText("SAVE & CLOSE")
            btn.setBackgroundColor(Color.parseColor("#FE2C55"))
            btn.setTextColor(Color.parseColor("#FFFFFF"))

            def do_save():
                cm = CookieManager.getInstance()
                cookie = cm.getCookie("https://www.tiktok.com") or ""
                _close(frame)
                Clock.schedule_once(lambda dt: on_captured(cookie), 0)

            listener = ButtonListener(do_save)
            _keep_refs['listener'] = listener
            btn.setOnClickListener(listener)

            # Put button at the bottom (-2 is WRAP_CONTENT)
            lp_btn = FrameLayoutParams(-1, -2)
            lp_btn.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL
            
            # Set margins in PIXELS (converted from dp)
            margin_px = int(dp(20))
            lp_btn.setMargins(margin_px, margin_px, margin_px, margin_px)
            
            frame.addView(btn, lp_btn)

            # 4. Add the overlay to Kivy and force it to the front
            activity.addContentView(frame, FrameLayoutParams(-1, -1))
            frame.bringToFront()
            
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