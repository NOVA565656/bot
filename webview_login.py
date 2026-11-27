from jnius import autoclass, PythonJavaClass, java_method
from kivy.clock import Clock

PythonActivity = autoclass('org.kivy.android.PythonActivity')
WebView = autoclass('android.webkit.WebView')
CookieManager = autoclass('android.webkit.CookieManager')
AlertDialog = autoclass('android.app.AlertDialog')
WindowManager = autoclass('android.view.WindowManager')

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

def open_login(on_captured):
    def _open():
        try:
            activity = PythonActivity.mActivity
            
            web = WebView(activity)
            web.getSettings().setJavaScriptEnabled(True)
            web.getSettings().setDomStorageEnabled(True)
            web.getSettings().setDatabaseEnabled(True)
            web.getSettings().setUserAgentString("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36")
            
            web.loadUrl("https://www.tiktok.com/login")
            
            builder = AlertDialog.Builder(activity)
            builder.setTitle("Log in to TikTok")
            builder.setView(web)
            
            def save_click():
                cm = CookieManager.getInstance()
                cookie = cm.getCookie("https://www.tiktok.com") or ""
                Clock.schedule_once(lambda dt: on_captured(cookie), 0)
                
            save_listener = DialogListener(save_click)
            
            builder.setPositiveButton("SAVE & CLOSE", save_listener)
            builder.setNegativeButton("CANCEL", None) 
            
            dialog = builder.create()
            dialog.show()
            
            window = dialog.getWindow()
            if window:
                window.setLayout(WindowManager.LayoutParams.MATCH_PARENT, WindowManager.LayoutParams.MATCH_PARENT)
                
        except Exception as e:
            Clock.schedule_once(lambda dt: on_captured(f"ERROR: {e}"), 0)

    activity = PythonActivity.mActivity
    activity.runOnUiThread(Runnable(_open))