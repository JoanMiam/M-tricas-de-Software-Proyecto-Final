# hotfix_percentage.py

import os
import requests
import matplotlib.pyplot as plt

# 1) Leer token de GitHub
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise RuntimeError("Define tu GITHUB_TOKEN en la variable de entorno")
H = {"Authorization": f"token {token}"}

owner, repo = "facebook", "react"

# 2) Obtener todas las releases
releases = []
page = 1
while True:
    r = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/releases",
        headers=H,
        params={"per_page": 100, "page": page}
    )
    r.raise_for_status()
    batch = r.json()
    if not batch:
        break
    releases.extend(batch)
    page += 1

# 3) Filtrar solo stable releases (prerelease==False)
stable = [r for r in releases if not r.get("prerelease", False)]

# 4) Contar hotfixes: asumimos que el título contiene "hotfix" (case‐insensitive)
hotfixes = [r for r in stable if "hotfix" in r.get("name","").lower()]

total_stable = len(stable)
count_hotfix = len(hotfixes)
percent = (count_hotfix / total_stable * 100) if total_stable else 0

# 5) Mostrar resultado
print(f"🏷️ Total releases estables: {total_stable}")
print(f"🔧 Releases de hotfix:    {count_hotfix}")
print(f"📊 % hotfixes por release: {percent:.2f}%")

# 6) Gráfico de barras
plt.figure(figsize=(4,4))
plt.bar(["Hotfix","No-Hotfix"], [count_hotfix, total_stable-count_hotfix],
        color=["#F44336","#4CAF50"])
plt.ylabel("Cantidad de Releases")
plt.title("Hotfix vs. Non-Hotfix Releases")
for i, v in enumerate([count_hotfix, total_stable-count_hotfix]):
    plt.text(i, v+0.5, str(v), ha="center")
plt.tight_layout()
plt.savefig("hotfix_percentage_bar.png")
plt.show()
