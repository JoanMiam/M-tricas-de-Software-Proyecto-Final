import os
import requests
from datetime import datetime
from statistics import mean

# 1) Leer token de GitHub
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise RuntimeError("Define la variable de entorno GITHUB_TOKEN con tu token de GitHub")
headers = {"Authorization": f"token {token}"}

# 2) Configuración
owner, repo = "facebook", "react"
url = f"https://api.github.com/repos/{owner}/{repo}/issues"

# Etiquetas que consideraremos como "cambio"
change_labels = {"type: bug", "type: feature request", "type: enhancement"}

# 3) Recoger issues cerrados (hasta 500) y filtrar por etiqueta
all_issues = []
for page in range(1, 6):
    resp = requests.get(
        url,
        headers=headers,
        params={"state": "closed", "per_page": 100, "page": page}
    )
    resp.raise_for_status()
    data = resp.json()
    if not data:
        break
    all_issues.extend(data)

# 4) Filtrar solo los que tienen alguna de las etiquetas de cambio
change_issues = [
    issue for issue in all_issues
    if any(lbl["name"].lower() in change_labels for lbl in issue.get("labels", []))
]

# 5) Calcular duraciones (días)
durations = []
for issue in change_issues:
    created = datetime.fromisoformat(issue["created_at"][:-1])
    closed  = datetime.fromisoformat(issue["closed_at"]  [:-1])
    delta = closed - created
    days = delta.days + delta.seconds/86400
    durations.append(round(days, 2))

# 6) Calcular MTTC
mttc = mean(durations) if durations else 0

# 7) Salida
print(f"🔄 Issues de cambio cerrados: {len(change_issues)}")
print(f"⏳ Lista de duraciones (días): {durations}")
print(f"\n📈 Mean Time to Change (MTTC): {mttc:.2f} días")
