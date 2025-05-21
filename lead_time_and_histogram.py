import os
import requests
import matplotlib.pyplot as plt
from datetime import datetime

# 1) Leer tu token de GitHub desde la variable de entorno
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise RuntimeError("Define la variable de entorno GITHUB_TOKEN con tu token de GitHub")

headers = {"Authorization": f"token {token}"}

# 2) Llamada al endpoint de PRs cerradas
url = "https://api.github.com/repos/facebook/react/pulls"
params = {"state": "closed", "per_page": 100}
resp = requests.get(url, headers=headers, params=params)
resp.raise_for_status()
prs = resp.json()

# 3) Calcular Lead Time de cada PR (en días)
durations = []
for pr in prs:
    created = datetime.fromisoformat(pr["created_at"][:-1])
    closed  = datetime.fromisoformat(pr["closed_at"][:-1])
    delta = closed - created
    days = delta.days + delta.seconds / 86400
    durations.append(round(days, 2))

# 4) Mostrar lista y promedio en consola
avg = sum(durations) / len(durations) if durations else 0
print("📋 Lista completa de Lead Times (días):")
print(durations)
print(f"\n📈 Lead Time promedio: {avg:.2f} días")

# 5) Generar histograma
plt.figure()
plt.hist(durations, bins=10)
plt.xlabel("Lead Time (días)")
plt.ylabel("Número de PRs")
plt.title("Distribución de Lead Time for Changes")
plt.tight_layout()
plt.savefig("lead_time_histogram.png")
plt.show()
