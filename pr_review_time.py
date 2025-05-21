import os
import requests
import matplotlib.pyplot as plt
from datetime import datetime
from statistics import mean

# 1) Leer token
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise RuntimeError("Define la variable de entorno GITHUB_TOKEN con tu token de GitHub")
headers = {"Authorization": f"token {token}"}

owner, repo = "facebook", "react"

# 2) Obtener las últimas 100 PRs cerradas
resp = requests.get(
    f"https://api.github.com/repos/{owner}/{repo}/pulls",
    headers=headers,
    params={"state": "closed", "per_page": 100}
)
resp.raise_for_status()
prs = resp.json()

# 3) Para cada PR, obtener el primer review y calcular delta
durations = []
for pr in prs:
    pr_created = datetime.fromisoformat(pr["created_at"][:-1])
    revs = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr['number']}/reviews",
        headers=headers
    ).json()
    if revs:
        first = min(revs, key=lambda r: r["submitted_at"] or r["submitted_at"])
        submitted = datetime.fromisoformat(first["submitted_at"][:-1])
        delta = submitted - pr_created
        days = delta.days + delta.seconds/86400
        durations.append(round(days, 2))

# 4) Imprimir lista y promedio
avg = mean(durations) if durations else 0
print("⏳ Lista de tiempos de revisión (días):")
print(durations)
print(f"\n📈 Tiempo medio de revisión: {avg:.2f} días")

# 5) Generar histograma
plt.figure()
plt.hist(durations, bins=10)
plt.xlabel("Tiempo de revisión de PR (días)")
plt.ylabel("Número de PRs")
plt.title("Distribución de Tiempo de Revisión de PRs")
plt.tight_layout()
plt.savefig("pr_review_time_histogram.png")
plt.show()
