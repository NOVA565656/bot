from jnius import autoclass, PythonJavaClass, java_method
from kivy.clock import Clock
import traceback

PythonActivity = autoclass('org.kivy.android.PythonActivity')
WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
CookieManager = autoclass('android.webkit.CookieManager')
Dialog = autoclass('android.app.Dialog')
WindowManager = autoclass('android.view.WindowManager')
LinearLayout = autoclass('android.widget.LinearLayout')
Button = autoclass('android.widget.Button')
Color = autoclass('android.graphics.Color')

_keep_refs = {}

class Runnable(PythonJavaClass):
    __javainterfaces__ = ['java/lang/Runnable']
    def __init__(self, func, on_error):
        super().__init__()
        self.func = func
        self.on_error = on_error
    @java_method('()V')
    def run(self):
        try:
            self.func()
        except Exception:
            Clock.schedule_once(lambda dt: self.on_error(traceback.format_exc()), 0)

# ✅ FIX: Correct listener for a standard Button (View.OnClickListener)
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
    @java_method('(Landroid/webkit/WebView;Ljava/lang/String;)Z')
    def shouldOverrideUrlLoading(self, view, url):
        return False

def open_login(on_captured):
    def _error(msg):
        on_captured(f"ERROR: {msg}")

    def _open():
        # Create Dialog (Bypasses theme crashes)
        dialog = Dialog(PythonActivity.mActivity)
        dialog.requestWindowFeature(1) # Window.FEATURE_NO_TITLE
        _keep_refs['dialog'] = dialog

        layout = LinearLayout(PythonActivity.mActivity)
        layout.setOrientation(1) # Vertical
        layout.setBackgroundColor(Color.parseColor("#1E1E24"))

        web = WebView(PythonActivity.mActivity)
        web.getSettings().setJavaScriptEnabled(True)
        web.getSettings().setDomStorageEnabled(True)
        web.getSettings().setDatabaseEnabled(True)
        web.getSettings().setUserAgentString("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36")
        
        client = MyWebViewClient()
        web.setWebViewClient(client)
        _keep_refs['client'] = client

        web.loadUrl("https://www.tiktok.com/login")
        _keep_refs['web'] = web

        # Add WebView (weight 1 makes it fill screen)
        lp_web = LinearLayout.LayoutParams(-1, 0, 1.0)
        layout.addView(web, lp_web)

        btn = Button(PythonActivity.mActivity)
        btn.setText("SAVE & CLOSE")
        btn.setBackgroundColor(Color.parseColor("#FE2C55"))
        btn.setTextColor(Color.parseColor("#FFFFFF"))

        def do_save():
            cm = CookieManager.getInstance()
            cookie = cm.getCookie("https://www.tiktok.com") or ""
            dialog.dismiss()
            Clock.schedule_once(lambda dt: on_captured(cookie), 0)

        listener = ButtonListener(do_save)
        _keep_refs['listener'] = listener
        btn.setOnClickListener(listener)

        lp_btn = LinearLayout.LayoutParams(-1, -2)
        lp_btn.setMargins(50, 50, 50, 50)
        layout.addView(btn, lp_btn)

        dialog.setContentView(layout)
        dialog.show()

        window = dialog.getWindow()
        if window:
            window.setLayout(WindowManager.LayoutParams.MATCH_PARENT, WindowManager.LayoutParams.MATCH_PARENT)

    runnable = Runnable(_open, _error)
    _keep_refs['runnable'] = runnable
    PythonActivity.mActivity.runOnUiThread(runnable)