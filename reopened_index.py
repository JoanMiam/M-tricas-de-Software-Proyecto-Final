# reopened_index.py

import os
import requests
import matplotlib.pyplot as plt

# 1) Leer token de GitHub
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise RuntimeError("Define la variable de entorno GITHUB_TOKEN con tu token de GitH ub")
headers = {"Authorization": f"token {token}"}

owner, repo = "facebook", "react"
issues_url = f"https://api.github.com/repos/{owner}/{repo}/issues"

# 2) Recoger issues cerrados (hasta 500)
closed_issues = []
for page in range(1, 6):
    r = requests.get(
        issues_url,
        headers=headers,
        params={"state": "closed", "per_page": 100, "page": page}
    )
    r.raise_for_status()
    data = r.json()
    if not data:
        break
    closed_issues.extend(data)

# 3) Para cada issue cerrado, consultar sus eventos y ver si tiene "reopened"
reopened_count = 0
for issue in closed_issues:
    # solo issues reales, no PRs
    if "pull_request" in issue:
        continue
    events_url = issue["events_url"]  # API endpoint de eventos
    ev = requests.get(events_url, headers=headers).json()
    # Si hay al menos un evento con .event == "reopened"
    if any(e.get("event") == "reopened" for e in ev):
        reopened_count += 1

total_closed = len([i for i in closed_issues if "pull_request" not in i])

# 4) Calcular índice
reopen_rate = (reopened_count / total_closed * 100) if total_closed else 0

# 5) Mostrar resultados
print(f"🔒 Total issues cerrados:   {total_closed}")
print(f"🔄 Issues reabiertos:       {reopened_count}")
print(f"📈 Índice de Reapertura:    {reopen_rate:.1f}%")

# 6) Graficar
labels = ["No Reabiertos", "Reabiertos"]
counts = [total_closed - reopened_count, reopened_count]

plt.figure()
plt.bar(labels, counts, color=["#4CAF50", "#F44336"])
plt.ylabel("Número de Issues")
plt.title("Índice de Issues Reabiertos")
for i, v in enumerate(counts):
    plt.text(i, v + 1, str(v), ha="center")
plt.tight_layout()
plt.savefig("reopened_index_bar.png")
plt.show()
