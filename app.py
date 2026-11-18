from flask import Flask, render_template, request, jsonify, redirect
from flask_cors import CORS
import database as db
from response_generator import generate_dm_response
import os

app = Flask(__name__)
CORS(app)

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
    conn = sqlite3.connect(db.DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE accounts SET is_active=0 WHERE id=?", (account_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})

@app.route('/api/test-reply', methods=['POST'])
def test_reply():
    data = request.json
    reply = generate_dm_response(
        data['comment'],
        data['author'],
    )
    return jsonify({"reply": reply})

@app.route('/api/start-bot', methods=['POST'])
def start_bot():
    # Trigger bot run (you'd implement actual bot start here)
    return jsonify({"status": "started"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)