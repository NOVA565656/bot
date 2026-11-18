import sqlite3
import json
from datetime import datetime

DB_PATH = "bot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Accounts table
    c.execute('''CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        session_id TEXT,
        username TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_used TIMESTAMP
    )''')
    
    # Comments replied table (to avoid duplicates)
    c.execute('''CREATE TABLE IF NOT EXISTS replied_comments (
        id INTEGER PRIMARY KEY,
        account_id INTEGER,
        comment_id TEXT,
        video_id TEXT,
        reply_text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (account_id) REFERENCES accounts(id)
    )''')
    
    conn.commit()
    conn.close()

def add_account(name, session_id, username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO accounts (name, session_id, username) VALUES (?, ?, ?)",
              (name, session_id, username))
    conn.commit()
    conn.close()

def get_active_accounts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, session_id, username FROM accounts WHERE is_active=1")
    accounts = [{"id": row[0], "name": row[1], "session_id": row[2], "username": row[3]} 
                for row in c.fetchall()]
    conn.close()
    return accounts

def mark_comment_replied(account_id, comment_id, video_id, reply_text):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO replied_comments (account_id, comment_id, video_id, reply_text) VALUES (?, ?, ?, ?)",
              (account_id, comment_id, video_id, reply_text))
    c.execute("UPDATE accounts SET last_used=? WHERE id=?", (datetime.now(), account_id))
    conn.commit()
    conn.close()

def is_already_replied(comment_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM replied_comments WHERE comment_id=?", (comment_id,))
    result = c.fetchone() is not None
    conn.close()
    return result

# Initialize
init_db()