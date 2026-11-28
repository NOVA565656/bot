from jnius import autoclass, PythonJavaClass, java_method
from kivy.clock import Clock
import traceback

PythonActivity = autoclass('org.kivy.android.PythonActivity')
WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
CookieManager = autoclass('android.webkit.CookieManager')
Dialog = autoclass('android.app.Dialog')
FrameLayout = autoclass('android.widget.FrameLayout')
FrameLayoutParams = autoclass('android.widget.FrameLayout$LayoutParams')
Button = autoclass('android.widget.Button')
Color = autoclass('android.graphics.Color')
Gravity = autoclass('android.view.Gravity')
Window = autoclass('android.view.Window')

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
            err = traceback.format_exc()
            if "NoneType: None" in err:
                err = "JNI Bridge Error (Check method signatures or arguments)."
            Clock.schedule_once(lambda dt: self.on_error(err), 0)

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
        
    # ✅ FIX: For Android 7.0+ (Your phone is Android 9)
    @java_method('(Landroid/webkit/WebView;Landroid/webkit/WebResourceRequest;)Z')
    def shouldOverrideUrlLoading(self, view, request):
        return False

def open_login(on_captured):
    def _error(msg):
        on_captured(f"ERROR: {msg}")

    def _open():
        # 1. Create Dialog
        dialog = Dialog(PythonActivity.mActivity)
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE) # Remove title bar
        _keep_refs['dialog'] = dialog

        # 2. Create Layout (Using FrameLayout - much simpler than LinearLayout)
        layout = FrameLayout(PythonActivity.mActivity)
        layout.setBackgroundColor(Color.parseColor("#1E1E24"))

        # 3. Create WebView
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

        # Add WebView to fill the screen (MATCH_PARENT = -1)
        lp_web = FrameLayoutParams(-1, -1)
        layout.addView(web, lp_web)

        # 4. Create Save Button
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

        # Put button at the bottom (WRAP_CONTENT = -2)
        lp_btn = FrameLayoutParams(-1, -2)
        lp_btn.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL
        lp_btn.setMargins(50, 50, 50, 50)
        layout.addView(btn, lp_btn)

        # 5. Show Dialog
        dialog.setContentView(layout)
        dialog.show()

        # 6. Force Fullscreen Dialog
        window = dialog.getWindow()
        if window:
            window.setLayout(-1, -1) # MATCH_PARENT for both width and height

    runnable = Runnable(_open, _error)
    _keep_refs['runnable'] = runnable
    PythonActivity.mActivity.runOnUiThread(runnable)