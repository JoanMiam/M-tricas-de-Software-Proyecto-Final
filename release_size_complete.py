# release_size_complete.py
import os, requests
import matplotlib.pyplot as plt
from datetime import datetime
from statistics import mean

# 1) Setup
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise RuntimeError("Define GITHUB_TOKEN")
H = {"Authorization": f"token {token}"}
owner, repo = "facebook", "react"

# 2) Obtener y ordenar releases estables
releases = []
p = 1
while True:
    resp = requests.get(f"https://api.github.com/repos/{owner}/{repo}/releases",
                        headers=H, params={"per_page":100,"page":p})
    data = resp.json()
    if not data: break
    for r in data:
        if not r.get("prerelease", False):
            releases.append(r)
    p += 1
releases.sort(key=lambda r: r["published_at"])
dates = [datetime.fromisoformat(r["published_at"][:-1]) for r in releases]

# 3) Bajar **todas** las PRs merged hasta la fecha del primer release
merged = []
page = 1
cutoff = dates[0]
while True:
    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/pulls",
        headers=H,
        params={"state":"closed","per_page":100,"page":page}
    ).json()
    if not resp: break
    stop = False
    for pr in resp:
        if pr.get("merged_at"):
            m = datetime.fromisoformat(pr["merged_at"][:-1])
            if m < cutoff:
                stop = True
                break
            merged.append(m)
    if stop:
        break
    page += 1

# 4) Contar PRs por cada intervalo de release
sizes = [
    sum(1 for m in merged if dates[i-1] < m <= dates[i])
    for i in range(1, len(dates))
]

# 5) Resultados
print("🔖 Tamaños de release (PRs):", sizes)
print(f"📈 Tamaño promedio de release: {mean(sizes):.1f} PRs")

# 6) Histograma
plt.figure()
plt.hist(sizes, bins=10)
plt.xlabel("PRs por release")
plt.ylabel("Número de releases")
plt.title("Distribución del tamaño de releases")
plt.tight_layout()
plt.savefig("release_size_complete.png")
plt.show()
