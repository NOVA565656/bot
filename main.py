import os, threading, time, random, sqlite3
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

import database as db
from analyzer import extract_potential_leads
from response_generator import generate_dm_response, provider
from commenter import post_comment
from scraper import search_videos, get_video_comments
from config import NICHE_KEYWORDS

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
        super().__init__(orientation="vertical", **kw)

        self.key_in = TextInput(hint_text="API key - OpenAI (sk-...) or Gemini (AIza...)",
                                password=True, size_hint_y=None, height=44)
        self.key_in.text = get_setting("api_key")
        self.add_widget(self.key_in)

        self.prov_lbl = Label(text="", size_hint_y=None, height=26)
        self.add_widget(self.prov_lbl)

        self.add_widget(Button(text="Save API key", size_hint_y=None, height=44,
                               on_release=lambda *a: self.save_key()))

        self.name_in = TextInput(hint_text="Account label", size_hint_y=None, height=44)
        self.user_in = TextInput(hint_text="TikTok username", size_hint_y=None, height=44)
        self.sess_in = TextInput(hint_text="sessionid cookie", size_hint_y=None, height=44)
        for w in (self.name_in, self.user_in, self.sess_in):
            self.add_widget(w)
        self.add_widget(Button(text="Save account", size_hint_y=None, height=44,
                               on_release=lambda *a: self.save_account()))

        self.add_widget(Button(text="START BOT", size_hint_y=None, height=56,
                               on_release=lambda *a: self.start()))

        sv = ScrollView()
        self.log = Label(text="Ready", size_hint_y=None, halign="left", valign="top")
        self.log.bind(texture_size=lambda i, v: setattr(i, "height", v[1]))
        sv.add_widget(self.log)
        self.add_widget(sv)

        self.refresh_provider()

    def refresh_provider(self):
        p = provider()
        self.prov_lbl.text = f"Provider: {p.upper()}" if p != "none" else "Provider: none (canned replies)"

    def say(self, m):
        Clock.schedule_once(lambda dt: setattr(self.log, "text", self.log.text + "\n" + m))

    def save_key(self):
        k = self.key_in.text.strip()
        if not (k.startswith("sk-") or k.startswith("AIza")):
            self.say("Key must start with sk- or AIza"); return
        set_setting("api_key", k)
        os.environ["BOT_API_KEY"] = k
        self.refresh_provider()
        self.say("API key saved")

    def save_account(self):
        if not (self.name_in.text.strip() and self.sess_in.text.strip()):
            self.say("Label and sessionid required"); return
        db.add_account(self.name_in.text.strip(), self.sess_in.text.strip(),
                       self.user_in.text.strip())
        self.say("Account saved")
        self.name_in.text = self.user_in.text = self.sess_in.text = ""

    def start(self):
        k = get_setting("api_key")
        if not k:
            self.say("Add an API key first"); return
        os.environ["BOT_API_KEY"] = k
        threading.Thread(target=self.run_bot, daemon=True).start()

    def run_bot(self):
        accts = db.get_active_accounts()
        if not accts:
            self.say("No accounts saved"); return
        for acct in accts:
            self.say(f"Account: {acct['name']}")
            for kw in NICHE_KEYWORDS[:3]:
                try:
                    for v in search_videos(kw, acct["session_id"], count=3):
                        cs = get_video_comments(v["id"], acct["session_id"])
                        for lead in extract_potential_leads(cs)[:2]:
                            if db.is_already_replied(lead["comment_id"]):
                                continue
                            reply = generate_dm_response(lead["text"], lead["author"])
                            if post_comment(v["id"], reply, acct["session_id"]):
                                db.mark_comment_replied(acct["id"], lead["comment_id"],
                                                        v["id"], reply)
                                self.say(f"-> @{lead['author']}: {reply[:40]}")
                            else:
                                self.say(f"x @{lead['author']} failed")
                            time.sleep(random.randint(45, 120))
                except Exception as e:
                    self.say(f"Error: {e}")
        self.say("Run complete")

class BotApp(App):
    def build(self):
        db.DB_PATH = os.path.join(self.user_data_dir, "bot.db")
        db.init_db()
        return Root()

if __name__ == "__main__":
    BotApp().run()