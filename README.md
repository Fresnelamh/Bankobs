# BankObs — Plateforme bancaire observable sur Kubernetes

Projet DevOps personnel démontrant une stack d'observabilité complète sur Kubernetes.

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Orchestration | Kubernetes k3s |
| Langage | Python 3.11 + Flask |
| Télémétrie | OpenTelemetry SDK + Collector |
| Métriques | Prometheus + Grafana |
| Traces | Jaeger |
| Logs | Elasticsearch + Kibana + Fluent Bit |
| Alerting | Alertmanager |
| Auto-remédiation | Python + kubernetes client |
| CI/CD | GitHub Actions |
| Tests de charge | k6 |

## Architecture

    Client HTTP
         |
    Ingress Nginx
         |
    namespace: banking-obs
      payment-service :5001
      auth-service    :5002
      account-service :5003
         |
    OTel Collector
      /     |     \
    Prometheus  Jaeger  Elasticsearch
      |                      |
    Grafana               Kibana
      |
    Alertmanager
      |
    remediation-bot

## Démarrage rapide

    git clone https://github.com/Fresnelamh/Bankobs.git
    cd Bankobs
    kubectl apply -f k8s/namespace.yaml
    kubectl apply -f k8s/configmaps/
    kubectl apply -f k8s/secrets/
    kubectl apply -f k8s/deployments/
    kubectl apply -f k8s/services/
    kubectl apply -f k8s/hpa/
    kubectl apply -f otel-collector/
    kubectl apply -f k8s/jaeger.yaml
    kubectl get pods -n banking-obs

## Tester un paiement

    curl -X POST http://localhost:30001/payment
      -H "Content-Type: application/json"
      -d '{"token":"secret-key-123","user_id":"user1","amount":100}'

## Accès aux UIs

| UI | URL |
|----|-----|
| Grafana | http://localhost:3000 |
| Jaeger | http://localhost:16686 |
| Kibana | http://localhost:5601 |

Les credentials sont dans les secrets Kubernetes.

## Scénarios de démonstration

| Scénario | Commande | Résultat attendu |
|----------|----------|-----------------|
| Stress test | k6 run tests/stress-test.js | HPA scale 2 vers 5 replicas |
| Pod failure | kubectl delete pod pod-name -n banking-obs | Recréation moins de 30s |
| Injection erreurs | python3 tests/inject-errors.py | Alerte HighErrorRate |
| Trace end-to-end | curl /payment puis Jaeger | 3 spans visibles |

## Auto-remédiation

| Alerte | Action automatique |
|--------|-------------------|
| PodCrashLooping | Supprime le pod crashé |
| HighErrorRate | Scale payment-service à 3 replicas |
| HighLatency | Log structuré de l'incident |

## Auteur

Fresnel AMAHOWE — Étudiant Ingénierie Informatique - Cybersécurité & DevOps
ENDOFFILE
