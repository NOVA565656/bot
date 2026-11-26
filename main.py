import os, threading, time, random, sqlite3
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.core.window import Window

# Import the WebView module
from webview_login import open_login

import database as db
from analyzer import extract_potential_leads
from response_generator import generate_dm_response, provider
from commenter import post_comment
from scraper import search_videos, get_video_comments
from config import NICHE_KEYWORDS

# --- CUSTOM UI WIDGETS ---
class Card(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = dp(15)
        self.spacing = dp(10)
        with self.canvas.before:
            Color(0.12, 0.12, 0.14, 1)
            self.rect = RoundedRectangle(radius=[dp(15)])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class RoundedButton(Button):
    def __init__(self, bg_color=(0, 0.8, 1, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0) 
        self.bg_color = bg_color
        with self.canvas.before:
            self.color_instruction = Color(*self.bg_color)
            self.rect = RoundedRectangle(radius=[dp(10)])
        self.bind(pos=self.update_rect, size=self.update_rect, state=self.on_state)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_state(self, instance, value):
        if value == 'down':
            self.color_instruction.rgba = (0.8, 0.8, 0.8, 1) 
        else:
            self.color_instruction.rgba = self.bg_color

class ModernInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.background_color = (0.18, 0.18, 0.2, 1)
        self.foreground_color = (1, 1, 1, 1)
        self.cursor_color = (0, 0.8, 1, 1)
        self.hint_text_color = (0.6, 0.6, 0.6, 1)
        self.padding = [dp(10), dp(10)]
        self.font_size = sp(14)

# --- BACKEND LOGIC ---
def get_setting(k, d=""):
    con = sqlite3.connect(db.DB_PATH); c = con.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS settings (k TEXT PRIMARY KEY, v TEXT)")
    c.execute("SELECT v FROM settings WHERE k=?", (k,))
    row = c.fetchone(); con.close()
    return row[0] if row else d

def set_setting(k, v):
    con = sqlite3.connect(db.DB_PATH); c = con.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS settings (k TEXT PRIMARY KEY, v TEXT)")
    c.execute("INSERT OR REPLACE INTO settings (k,v) VALUES (?,?)", (k, v))
    con.commit(); con.close()

class Root(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", padding=dp(15), spacing=dp(15), **kw)
        Window.clearcolor = (0.08, 0.08, 0.1, 1)

        header = Label(text="[b]TikTok Bot Automator[/b]", markup=True, size_hint_y=None, height=dp(40), font_size=sp(22), color=(0, 0.8, 1, 1))
        self.add_widget(header)

        main_scroll = ScrollView()
        scroll_layout = BoxLayout(orientation="vertical", spacing=dp(15), size_hint_y=None)
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        # API CARD
        api_card = Card(orientation="vertical", size_hint_y=None, height=dp(160))
        api_card.add_widget(Label(text="API Configuration", size_hint_y=None, height=dp(20), bold=True, color=(0.8, 0.8, 0.8, 1)))
        self.key_in = ModernInput(hint_text="API key (sk-... or AIza...)", password=True, size_hint_y=None, height=dp(45))
        self.key_in.text = get_setting("api_key")
        api_card.add_widget(self.key_in)

        btn_layout = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        self.prov_lbl = Label(text="", color=(0.6, 0.6, 0.6, 1))
        btn_layout.add_widget(self.prov_lbl)
        save_key_btn = RoundedButton(text="Save Key", bg_color=(0, 0.6, 0.8, 1), size_hint_x=0.4)
        save_key_btn.bind(on_release=lambda *a: self.save_key())
        btn_layout.add_widget(save_key_btn)
        api_card.add_widget(btn_layout)
        scroll_layout.add_widget(api_card)

        # ACCOUNT CARD
        acc_card = Card(orientation="vertical", size_hint_y=None, height=dp(340)) # Made taller for the new button
        acc_card.add_widget(Label(text="Account Details", size_hint_y=None, height=dp(20), bold=True, color=(0.8, 0.8, 0.8, 1)))
        
        self.name_in = ModernInput(hint_text="Account label (e.g. MyAccount1)", size_hint_y=None, height=dp(45))
        self.user_in = ModernInput(hint_text="TikTok username", size_hint_y=None, height=dp(45))
        self.sess_in = ModernInput(hint_text="sessionid cookie", size_hint_y=None, height=dp(45))
        
        for w in (self.name_in, self.user_in, self.sess_in):
            acc_card.add_widget(w)
            
        save_acc_btn = RoundedButton(text="Save Manual Account", bg_color=(0.2, 0.6, 0.2, 1), size_hint_y=None, height=dp(45))
        save_acc_btn.bind(on_release=lambda *a: self.save_account())
        acc_card.add_widget(save_acc_btn)
        
        # ✅ THE NEW WEBVIEW BUTTON
        web_login_btn = RoundedButton(text="Add Account via Web Login", bg_color=(0.6, 0.2, 0.8, 1), size_hint_y=None, height=dp(45))
        web_login_btn.bind(on_release=lambda *a: open_login(self.on_captured))
        acc_card.add_widget(web_login_btn)
        
        scroll_layout.add_widget(acc_card)

        # START BUTTON
        self.start_btn = RoundedButton(text="START BOT", bg_color=(0.8, 0.1, 0.3, 1), size_hint_y=None, height=dp(60), font_size=sp(20), bold=True)
        self.start_btn.bind(on_release=lambda *a: self.start())
        scroll_layout.add_widget(self.start_btn)

        # LOG CONSOLE
        log_card = Card(orientation="vertical", size_hint_y=None, height=dp(250))
        log_card.add_widget(Label(text="Console Output", size_hint_y=None, height=dp(20), bold=True, color=(0.8, 0.8, 0.8, 1)))
        log_scroll = ScrollView()
        self.log = Label(text="> System Ready...\n", size_hint_y=None, halign="left", valign="top", font_name="Roboto", color=(0, 1, 0, 1))
        self.log.bind(texture_size=lambda i, v: setattr(i, "height", v[1]))
        self.log.bind(width=lambda instance, value: setattr(instance, "text_size", (value, None)))
        log_scroll.add_widget(self.log)
        self.log.bind(texture_size=lambda *args: setattr(log_scroll, "scroll_y", 0))
        log_card.add_widget(log_scroll)
        scroll_layout.add_widget(log_card)

        main_scroll.add_widget(scroll_layout)
        self.add_widget(main_scroll)
        self.refresh_provider()

    def refresh_provider(self):
        p = provider()
        self.prov_lbl.text = f"Provider: {p.upper()}" if p != "none" else "Provider: none (canned)"

    def say(self, m):
        Clock.schedule_once(lambda dt: setattr(self.log, "text", self.log.text + f"> {m}\n"))

    def save_key(self):
        k = self.key_in.text.strip()
        if not (k.startswith("sk-") or k.startswith("AIza")):
            self.say("Key must start with sk- or AIza"); return
        set_setting("api_key", k)
        os.environ["BOT_API_KEY"] = k
        self.refresh_provider()
        self.say("API key saved successfully")

    def save_account(self):
        if not (self.name_in.text.strip() and self.sess_in.text.strip()):
            self.say("Label and sessionid required"); return
        db.add_account(self.name_in.text.strip(), self.sess_in.text.strip(), self.user_in.text.strip())
        self.say("Account saved manually")
        self.name_in.text = self.user_in.text = self.sess_in.text = ""

    # ✅ NEW FUNCTION FOR WEBVIEW CAPTURE
    def on_captured(self, cookie):
        if "sessionid=" not in cookie:
            self.say("No sessionid found - log in fully, then tap SAVE")
            return
        n = len(db.get_active_accounts()) + 1
        db.add_account(f"acct{n}", cookie, "")
        self.say(f"acct{n} saved from WebView login!")

    def start(self):
        k = get_setting("api_key")
        if not k:
            self.say("Error: Add an API key first"); return
        os.environ["BOT_API_KEY"] = k
        self.say("Starting Bot Thread...")
        threading.Thread(target=self.run_bot, daemon=True).start()

    def run_bot(self):
        accts = db.get_active_accounts()
        if not accts:
            self.say("Error: No accounts saved"); return
        for acct in accts:
            self.say(f"Processing Account: {acct['name']}")
            for kw in NICHE_KEYWORDS[:3]:
                try:
                    for v in search_videos(kw, acct["session_id"], count=3):
                        cs = get_video_comments(v["id"], acct["session_id"])
                        for lead in extract_potential_leads(cs)[:2]:
                            if db.is_already_replied(lead["comment_id"]): continue
                            reply = generate_dm_response(lead["text"], lead["author"])
                            if post_comment(v["id"], reply, acct["session_id"]):
                                db.mark_comment_replied(acct["id"], lead["comment_id"], v["id"], reply)
                                self.say(f"Replied to @{lead['author']}")
                            else:
                                self.say(f"Failed to reply to @{lead['author']}")
                            time.sleep(random.randint(45, 120))
                except Exception as e:
                    self.say(f"Error: {e}")
        self.say("Run complete. Bot is idle.")

class BotApp(App):
    def build(self):
        db.DB_PATH = os.path.join(self.user_data_dir, "bot.db")
        db.init_db()
        return Root()

if __name__ == "__main__":
    BotApp().run()