import threading, time, random, sqlite3, os
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup

import database as db
from analyzer import extract_potential_leads
from response_generator import generate_dm_response
from commenter import post_comment
from scraper import search_videos, get_video_comments
from config import NICHE_KEYWORDS

DB = os.path.join(App.get_running_app().user_data_dir if False else ".", "bot.db")

def get_setting(key, default=""):
    con = sqlite3.connect(db.DB_PATH); c = con.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS settings (k TEXT PRIMARY KEY, v TEXT)")
    c.execute("SELECT v FROM settings WHERE k=?", (key,))
    row = c.fetchone(); con.close()
    return row[0] if row else default

def set_setting(key, val):
    con = sqlite3.connect(db.DB_PATH); c = con.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS settings (k TEXT PRIMARY KEY, v TEXT)")
    c.execute("INSERT OR REPLACE INTO settings (k,v) VALUES (?,?)", (key, val))
    con.commit(); con.close()

class Root(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", **kw)
        db.init_db()

        # API key
        self.api_in = TextInput(hint_text="OpenAI API key", password=True, size_hint_y=None, height=44)
        self.api_in.text = get_setting("api_key")
        self.add_widget(self.api_in)
        self.add_widget(Button(text="Save API key", size_hint_y=None, height=44,
                               on_release=lambda *a: self.save_key()))

        # Add account
        self.name_in = TextInput(hint_text="Account label", size_hint_y=None, height=44)
        self.user_in = TextInput(hint_text="TikTok username", size_hint_y=None, height=44)
        self.sess_in = TextInput(hint_text="sessionid cookie", size_hint_y=None, height=44)
        for w in (self.name_in, self.user_in, self.sess_in):
            self.add_widget(w)
        self.add_widget(Button(text="Save account", size_hint_y=None, height=44,
                               on_release=lambda *a: self.save_account()))

        self.status = Label(text="Ready", size_hint_y=None, height=60)
        self.add_widget(self.status)
        self.add_widget(Button(text="START BOT", size_hint_y=None, height=56,
                               on_release=lambda *a: self.start()))

        sv = ScrollView()
        self.log = Label(size_hint_y=None, halign="left", valign="top")
        self.log.bind(texture_size=lambda i, v: setattr(i, "height", v[1]))
        sv.add_widget(self.log)
        self.add_widget(sv)

    def save_key(self):
        set_setting("api_key", self.api_in.text.strip())
        os.environ["OPENAI_API_KEY"] = self.api_in.text.strip()
        self.say("API key saved")

    def save_account(self):
        if not (self.name_in.text and self.sess_in.text):
            self.say("Label and sessionid required"); return
        db.add_account(self.name_in.text.strip(), self.sess_in.text.strip(), self.user_in.text.strip())
        self.say("Account saved"); self.name_in.text = self.user_in.text = self.sess_in.text = ""

    def say(self, msg):
        Clock.schedule_once(lambda dt: setattr(self.log, "text", self.log.text + "\n" + msg))

    def start(self):
        os.environ["OPENAI_API_KEY"] = get_setting("api_key")
        threading.Thread(target=self.run_bot, daemon=True).start()

    def run_bot(self):
        accts = db.get_active_accounts()
        if not accts:
            self.say("No accounts"); return
        for acct in accts:
            self.say(f"Using {acct['name']}")
            for kw in NICHE_KEYWORDS[:3]:
                try:
                    for v in search_videos(kw, acct["session_id"], count=3):
                        for lead in extract_potential_leads(get_video_comments(v["id"], acct["session_id"]))[:2]:
                            if db.is_already_replied(lead["comment_id"]):
                                continue
                            reply = generate_dm_response(lead["text"], lead["author"])
                            if post_comment(v["id"], reply, acct["session_id"]):
                                db.mark_comment_replied(acct["id"], lead["comment_id"], v["id"], reply)
                                self.say(f"-> @{lead['author']}: {reply[:40]}")
                            time.sleep(random.randint(45, 120))
                except Exception as e:
                    self.say(f"Error: {e}")
        self.say("Run complete")

class BotApp(App):
    def build(self):
        return Root()

if __name__ == "__main__":
    BotApp().run()