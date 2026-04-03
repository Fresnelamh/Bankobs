import os
from flask import Flask, request, jsonify
from otel_config import init_telemetry

app = Flask(__name__)
tracer = init_telemetry(app, "auth-service")

VALID_TOKEN = os.getenv("JWT_SECRET", "secret-key-123")

@app.route("/validate", methods=["POST"])
def validate():
    with tracer.start_as_current_span("token-validation") as span:
        token = (request.json or {}).get("token", "")
        valid = token == VALID_TOKEN
        span.set_attribute("auth.valid", valid)
        if valid:
            return jsonify({"valid": True}), 200
        return jsonify({"valid": False}), 401

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/ready")
def ready():
    return jsonify({"status": "ready"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5002)))
