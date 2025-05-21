# release_size_fixed.py

import os
import requests
import matplotlib.pyplot as plt
from datetime import datetime
from statistics import mean

# 1) Leer token
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise RuntimeError("Define tu GITHUB_TOKEN en la variable de entorno")

owner, repo = "facebook", "react"
headers = {"Authorization": f"token {token}"}

# 2) Descargar y ordenar releases estables
releases = []
page = 1
while True:
    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/releases",
        headers=headers,
        params={"per_page": 100, "page": page}
    )
    resp.raise_for_status()
    batch = [r for r in resp.json() if not r.get("prerelease", False)]
    if not batch:
        break
    releases.extend(batch)
    page += 1

releases.sort(key=lambda r: r["published_at"])
dates = [datetime.fromisoformat(r["published_at"][:-1]) for r in releases]

# 3) Descargar merged PRs (hasta N páginas)
merged_prs = []
for page in range(1, 6):
    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/pulls",
        headers=headers,
        params={"state": "closed", "per_page": 100, "page": page}
    )
    resp.raise_for_status()
    for pr in resp.json():
        if pr.get("merged_at"):
            merged_prs.append(datetime.fromisoformat(pr["merged_at"][:-1]))

# 4) Calcular tamaño de cada release
sizes = []
for i in range(1, len(dates)):
    start, end = dates[i-1], dates[i]
    count = sum(1 for m in merged_prs if start < m <= end)
    sizes.append(count)

# 5) Mostrar resultados
print("🔖 Tamaños de release (PRs):", sizes)
print(f"📈 Tamaño promedio de release: {mean(sizes):.1f} PRs")

# 6) Graficar
plt.figure()
plt.hist(sizes, bins=10)
plt.xlabel("Número de PRs por Release")
plt.ylabel("Cantidad de Releases")
plt.title("Distribución del Tamaño de Releases")
plt.tight_layout()
plt.savefig("release_size_histogram.png")
plt.show()
