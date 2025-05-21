import os
import requests
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime

# Script para frecuencia de reversión de commits
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise RuntimeError("Define la variable de entorno GITHUB_TOKEN")
headers = {"Authorization": f"token {token}"}

owner, repo = "facebook", "react"

# 1) Obtener últimos 200 commits
commits = []
for page in range(1, 3):  # 2 páginas de 100 cada una
    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/commits",
        headers=headers,
        params={"per_page": 100, "page": page}
    )
    resp.raise_for_status()
    commits.extend(resp.json())

# 2) Filtrar commits de reversión (mensaje contiene "revert")
revert_dates = []
for c in commits:
    msg = c["commit"]["message"].lower()
    if "revert" in msg:
        date_str = c["commit"]["author"]["date"]
        date = datetime.fromisoformat(date_str[:-1])
        # Contar por semana ISO
        week = date.isocalendar()[1]
        revert_dates.append(week)

# 3) Contar frecuencia por semana ISO
freq_by_week = Counter(revert_dates)

# 4) Graficar
weeks = sorted(freq_by_week.keys())
counts = [freq_by_week[w] for w in weeks]

plt.figure(figsize=(8, 4))
plt.bar(weeks, counts)
plt.xlabel("Semana ISO")
plt.ylabel("Número de Reverts")
plt.title("Frecuencia de Reversión de Commits por Semana ISO")
plt.xticks(weeks)
plt.tight_layout()
plt.savefig("revert_frequency_bar.png")
plt.show()
