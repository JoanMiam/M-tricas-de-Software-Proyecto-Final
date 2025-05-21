import os
import requests
import matplotlib.pyplot as plt
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

# 3) Para cada PR, contar revisores únicos
reviewer_counts = []
for pr in prs:
    reviews = requests.get(
        pr["url"] + "/reviews",
        headers=headers
    ).json()
    # extraer usuarios únicos que hayan hecho review
    reviewers = {r["user"]["login"] for r in reviews if r.get("user")}
    reviewer_counts.append(len(reviewers))

# 4) Mostrar lista y promedio
avg_rev = mean(reviewer_counts) if reviewer_counts else 0
print("👥 Lista de número de revisores por PR:")
print(reviewer_counts)
print(f"\n📈 Revisor(es) promedio por PR: {avg_rev:.2f}")

# 5) Generar histograma
plt.figure()
plt.hist(reviewer_counts, bins=range(0, max(reviewer_counts)+2))
plt.xlabel("Número de revisores por PR")
plt.ylabel("Cantidad de PRs")
plt.title("Distribución de revisores por PR")
plt.xticks(range(0, max(reviewer_counts)+2))
plt.tight_layout()
plt.savefig("reviewers_per_pr_histogram.png")
plt.show()
