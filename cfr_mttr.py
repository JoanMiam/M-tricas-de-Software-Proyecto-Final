import os
import requests
from datetime import datetime
from statistics import mean

# 1) Leer token de GitHub
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise RuntimeError("Define la variable de entorno GITHUB_TOKEN con tu token de GitHub")

headers = {"Authorization": f"token {token}"}

# 2) Obtener issues cerrados con paginación (hasta 500 issues)
owner, repo = "facebook", "react"
url = f"https://api.github.com/repos/{owner}/{repo}/issues"
all_issues = []
for page in range(1, 6):  # páginas 1 a 5
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

# 3) Filtrar issues de bug (cualquier etiqueta que contenga "bug")
bug_issues = [
    issue for issue in all_issues
    if any("bug" in lbl["name"].lower() for lbl in issue.get("labels", []))
]
bug_count = len(bug_issues)

# 4) Contar hotfixes (título o etiqueta)
hotfix_count = sum(
    1 for issue in bug_issues
    if "hotfix" in issue["title"].lower()
    or any("hotfix" in lbl["name"].lower() for lbl in issue.get("labels", []))
)

# 5) Calcular Change Failure Rate
cfr = (hotfix_count / bug_count * 100) if bug_count else 0

# 6) Calcular MTTR (horas)
recovery_hours = []
for issue in bug_issues:
    created = datetime.fromisoformat(issue["created_at"][:-1])
    closed  = datetime.fromisoformat(issue["closed_at"][:-1])
    hours = (closed - created).total_seconds() / 3600
    recovery_hours.append(hours)

mttr = mean(recovery_hours) if recovery_hours else 0

# 7) Mostrar resultados
print(f"🐞 Total issues de bug cerrados: {bug_count}")
print(f"🔧 Hotfixes detectados:          {hotfix_count}")
print(f"📊 Change Failure Rate:          {cfr:.1f}%")
print(f"⏱ Mean Time to Recovery (MTTR):  {mttr:.1f} h")
