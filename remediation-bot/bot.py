import os, time, logging, json, threading
from flask import Flask, request, jsonify
from kubernetes import client, config

logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}'
)
log = logging.getLogger("remediation-bot")

app = Flask(__name__)

try:
    config.load_incluster_config()
except:
    config.load_kube_config()

v1   = client.CoreV1Api()
apps = client.AppsV1Api()
NAMESPACE = "banking-obs"

def handle_crash_looping(alert):
    pod_name = alert.get("labels", {}).get("pod")
    if not pod_name:
        return
    log.info(f"Suppression pod en crash: {pod_name}")
    try:
        v1.delete_namespaced_pod(name=pod_name, namespace=NAMESPACE)
        log.info(f"Pod {pod_name} supprimé")
    except Exception as e:
        log.error(f"Erreur: {e}")

def handle_high_error_rate(alert):
    log.info("Scale payment-service à 3 replicas")
    try:
        apps.patch_namespaced_deployment_scale(
            name="payment-service",
            namespace=NAMESPACE,
            body={"spec": {"replicas": 3}}
        )
        log.info("Scale effectué")
    except Exception as e:
        log.error(f"Erreur scale: {e}")

def handle_high_latency(alert):
    log.warning(json.dumps({
        "action": "logged",
        "alert": "HighLatency",
        "labels": alert.get("labels", {})
    }))

ACTION_MAP = {
    "PodCrashLooping": handle_crash_looping,
    "HighErrorRate":   handle_high_error_rate,
    "HighLatency":     handle_high_latency,
}

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.json or {}
    alerts  = payload.get("alerts", [])
    for alert in alerts:
        if alert.get("status") != "firing":
            continue
        name    = alert.get("labels", {}).get("alertname", "unknown")
        handler = ACTION_MAP.get(name)
        log.info(f"Alerte reçue: {name}")
        if handler:
            handler(alert)
    return jsonify({"status": "processed"}), 200

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
