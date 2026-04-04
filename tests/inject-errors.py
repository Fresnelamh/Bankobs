import requests, time

BASE_URL = "http://localhost:30001"
print("Injection erreurs — 100 requêtes malformées")
for i in range(100):
    r = requests.post(f"{BASE_URL}/payment",
                      data="not-json",
                      headers={"Content-Type": "application/json"})
    print(f"[{i+1:3d}] status={r.status_code}")
    time.sleep(0.1)
