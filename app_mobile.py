import os
import sys
from threading import Thread

# Android storage path
if hasattr(sys, 'getandroidapilevel'):
    DATA_DIR = os.path.join(os.environ['EXTERNAL_STORAGE'], 'TikTokBot')
else:
    DATA_DIR = os.path.dirname(os.path.abspath(__file__))

os.makedirs(DATA_DIR, exist_ok=True)
os.chdir(DATA_DIR)

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import database as db
from response_generator import generate_dm_response

app = Flask(__name__, template_folder='templates')
CORS(app)

# Initialize database
db.DB_PATH = os.path.join(DATA_DIR, 'bot.db')
db.init_db()

@app.route('/')
def dashboard():
    accounts = db.get_active_accounts()
    return render_template('dashboard.html', accounts=len(accounts))

@app.route('/accounts')
def manage_accounts():
    accounts = db.get_active_accounts()
    return render_template('accounts.html', accounts=accounts)

@app.route('/api/account', methods=['POST'])
def add_account():
    data = request.json
    db.add_account(
        name=data['name'],
        session_id=data['session_id'],
        username=data['username']
    )
    return jsonify({"status": "success"})

@app.route('/api/account/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    import sqlite3
    conn = sqlite3.connect(db.DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE accounts SET is_active=0 WHERE id=?", (account_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})

@app.route('/api/test-reply', methods=['POST'])
def test_reply():
    data = request.json
    reply = generate_dm_response(data['comment'], data['author'])
    return jsonify({"reply": reply})

def run_server():
    app.run(host='127.0.0.1', port=5000, debug=False)

if __name__ == '__main__':
    # Start server in background thread
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Keep main thread alive
    import time
    while True:
        time.sleep(1)