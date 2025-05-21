import os
import requests
from collections import Counter
import matplotlib.pyplot as plt

# 1) Leer token
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise RuntimeError("Define la variable de entorno GITHUB_TOKEN con tu token de GitHub")
headers = {"Authorization": f"token {token}"}

owner, repo = "facebook", "react"

# 2) Obtener las últimas 100 PRs cerradas
prs = requests.get(
    f"https://api.github.com/repos/{owner}/{repo}/pulls",
    headers=headers,
    params={"state": "closed", "per_page": 100}
).json()

# 3) Para cada PR, contar cambios por archivo
file_counter = Counter()
for pr in prs:
    num = pr["number"]
    files = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/pulls/{num}/files",
        headers=headers
    ).json()
    for f in files:
        # churn = añadidos + eliminados
        churn = f.get("additions",0) + f.get("deletions",0)
        file_counter[f["filename"]] += churn

# 4) Sacar top 10 archivos con más churn
top10 = file_counter.most_common(10)
print("🏆 Top 10 archivos por File Churn (add+del):")
for i,(fname,churn) in enumerate(top10,1):
    print(f"{i}. {fname} → {churn} cambios")

# 5) Graficar en barras
files, counts = zip(*top10)
plt.figure(figsize=(8,6))
plt.barh(files, counts)
plt.xlabel("Churn (líneas añadidas + eliminadas)")
plt.title("Top 10 File Churn en facebook/react")
plt.tight_layout()
plt.savefig("file_churn_bar.png")
plt.show()
