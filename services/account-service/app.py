import os, sqlite3
from flask import Flask, request, jsonify
from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor
from otel_config import init_telemetry

SQLite3Instrumentor().instrument()

app = Flask(__name__)
tracer = init_telemetry(app, "account-service")

DB_PATH = "/tmp/accounts.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS accounts (user_id TEXT PRIMARY KEY, balance REAL)")
        conn.execute("INSERT OR IGNORE INTO accounts VALUES ('user1', 10000.0)")
        conn.execute("INSERT OR IGNORE INTO accounts VALUES ('user2', 500.0)")
        conn.commit()

@app.route("/balance/<user_id>")
def balance(user_id):
    with tracer.start_as_current_span("db-read-balance") as span:
        span.set_attribute("db.user_id", user_id)
        with get_db() as conn:
            row = conn.execute("SELECT balance FROM accounts WHERE user_id=?", (user_id,)).fetchone()
        if not row:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"user_id": user_id, "balance": row["balance"]}), 200

@app.route("/debit", methods=["POST"])
def debit():
    data = request.json or {}
    user_id = data.get("user_id")
    amount  = data.get("amount", 0)
    with tracer.start_as_current_span("db-write-debit") as span:
        span.set_attribute("db.user_id", user_id)
        span.set_attribute("db.amount", amount)
        with get_db() as conn:
            conn.execute("UPDATE accounts SET balance = balance - ? WHERE user_id=?", (amount, user_id))
            conn.commit()
    return jsonify({"status": "debited", "amount": amount}), 200

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/ready")
def ready():
    return jsonify({"status": "ready"}), 200

with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5003)))
