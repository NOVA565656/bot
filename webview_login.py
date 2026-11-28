from jnius import autoclass, PythonJavaClass, java_method
from kivy.clock import Clock

PythonActivity = autoclass('org.kivy.android.PythonActivity')
WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
CookieManager = autoclass('android.webkit.CookieManager')
AlertDialog = autoclass('android.app.AlertDialog')
WindowManager = autoclass('android.view.WindowManager')

# ✅ Keep references in memory so Python GC doesn't delete them (prevents instant crash)
_keep_refs = {}

class Runnable(PythonJavaClass):
    __javainterfaces__ = ['java/lang/Runnable']
    def __init__(self, func):
        super().__init__()
        self.func = func
    @java_method('()V')
    def run(self):
        self.func()

class DialogListener(PythonJavaClass):
    __javainterfaces__ = ['android/content/DialogInterface$OnClickListener']
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
    @java_method('(Landroid/content/DialogInterface;I)V')
    def onClick(self, dialog, which):
        self.callback()

class MyWebViewClient(PythonJavaClass):
    __javainterfaces__ = ['android/webkit/WebViewClient']
    @java_method('(Landroid/webkit/WebView;Ljava/lang/String;)Z')
    def shouldOverrideUrlLoading(self, view, url):
        return False

def open_login(on_captured):
    def _open():
        try:
            activity = PythonActivity.mActivity
            
            web = WebView(activity)
            web.getSettings().setJavaScriptEnabled(True)
            web.getSettings().setDomStorageEnabled(True)
            web.getSettings().setDatabaseEnabled(True)
            web.getSettings().setUserAgentString("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36")
            
            # ✅ Prevent redirect crashes
            client = MyWebViewClient()
            web.setWebViewClient(client)
            _keep_refs['client'] = client
            
            web.loadUrl("https://www.tiktok.com/login")
            
            builder = AlertDialog.Builder(activity)
            builder.setTitle("Log in to TikTok")
            builder.setView(web)
            
            def save_click():
                cm = CookieManager.getInstance()
                cookie = cm.getCookie("https://www.tiktok.com") or ""
                Clock.schedule_once(lambda dt: on_captured(cookie), 0)
                
            save_listener = DialogListener(save_click)
            _keep_refs['listener'] = save_listener # ✅ Keep listener in memory
            
            builder.setPositiveButton("SAVE & CLOSE", save_listener)
            builder.setNegativeButton("CANCEL", None) 
            
            dialog = builder.create()
            _keep_refs['dialog'] = dialog # ✅ Keep dialog in memory
            _keep_refs['web'] = web       # ✅ Keep webview in memory
            
            dialog.show()
            
            window = dialog.getWindow()
            if window:
                window.setLayout(WindowManager.LayoutParams.MATCH_PARENT, WindowManager.LayoutParams.MATCH_PARENT)
                
        except Exception as e:
            # If it fails, send the error to Kivy instead of crashing
            Clock.schedule_once(lambda dt: on_captured(f"ERROR: {e}"), 0)

    # ✅ Keep the runnable in memory
    runnable = Runnable(_open)
    _keep_refs['runnable'] = runnable
    
    activity = PythonActivity.mActivity
    activity.runOnUiThread(runnable)