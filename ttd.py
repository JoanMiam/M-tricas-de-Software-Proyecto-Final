# ttd_fixed.py
import os
import requests
import matplotlib.pyplot as plt
from datetime import datetime
from bisect import bisect_right

token = os.getenv("GITHUB_TOKEN")
if not token:
    raise RuntimeError("Define la variable de entorno GITHUB_TOKEN")
H = {"Authorization": f"token {token}"}
owner, repo = "facebook", "react"

# 1) Obtener releases ordenadas
rel = requests.get(f"https://api.github.com/repos/{owner}/{repo}/releases?per_page=100", headers=H).json()
rel_dates = sorted(
    datetime.fromisoformat(r["published_at"][:-1])
    for r in rel if r.get("published_at")
)

# 2) Recoger issues cerrados sin filtro
all_issues = []
for page in range(1,6):
    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/issues",
        headers=H,
        params={"state": "closed", "per_page":100, "page":page}
    )
    data = resp.json()
    if not data:
        break
    all_issues.extend(data)

# 3) Filtrar bugs según cualquier label que contenga "bug"
bug_issues = [
    i for i in all_issues
    if any("bug" in lbl["name"].lower() for lbl in i.get("labels", []))
]

# 4) Calcular TTD para cada bug
ttds = []
for issue in bug_issues:
    created = datetime.fromisoformat(issue["created_at"][:-1])
    idx = bisect_right(rel_dates, created) - 1
    if idx >= 0:
        delta = created - rel_dates[idx]
        ttds.append(delta.days + delta.seconds/86400)

# 5) Resultado
if not ttds:
    print("Aún no hay bugs que caigan después de un release en la muestra.")
    exit()

avg_ttd = sum(ttds)/len(ttds)
print("Lista de TTDs (días):", [round(x,2) for x in ttds])
print(f"TTD promedio: {avg_ttd:.2f} días")

# 6) Histograma
plt.figure()
plt.hist(ttds, bins=10)
plt.xlabel("Time To Detect (días)")
plt.ylabel("Número de Bugs")
plt.title("Distribución de TTD")
plt.tight_layout()
plt.savefig("ttd_histogram.png")
plt.show()
