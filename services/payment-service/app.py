import os, random, time
import requests
from flask import Flask, request, jsonify
from opentelemetry import trace
from otel_config import init_telemetry

app = Flask(__name__)
tracer = init_telemetry(app, "payment-service")

AUTH_URL    = os.getenv("AUTH_SERVICE_URL", "http://localhost:5002")
ACCOUNT_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://localhost:5003")

@app.route("/payment", methods=["POST"])
def payment():
    data = request.json or {}
    if random.random() < 0.05:
        return jsonify({"error": "Internal error"}), 500
    if random.random() < 0.1:
        time.sleep(random.uniform(0.8, 2.0))

    with tracer.start_as_current_span("validate-token") as span:
        token = data.get("token", "")
        r = requests.post(f"{AUTH_URL}/validate", json={"token": token}, timeout=3)
        span.set_attribute("auth.status", r.status_code)
        if r.status_code != 200:
            return jsonify({"error": "Unauthorized"}), 401

    with tracer.start_as_current_span("check-balance") as span:
        user_id = data.get("user_id", "user1")
        amount  = data.get("amount", 0)
        span.set_attribute("account.user_id", user_id)
        span.set_attribute("account.amount", amount)
        r = requests.get(f"{ACCOUNT_URL}/balance/{user_id}", timeout=3)
        balance = r.json().get("balance", 0)
        if balance < amount:
            return jsonify({"error": "Insufficient funds"}), 422
        requests.post(f"{ACCOUNT_URL}/debit",
                      json={"user_id": user_id, "amount": amount}, timeout=3)

    return jsonify({"status": "success", "amount": amount, "user": user_id}), 200

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/ready")
def ready():
    return jsonify({"status": "ready"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5001)))
