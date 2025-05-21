# mttr.py
import os, requests
from datetime import datetime
from statistics import mean

# 1) Leer token
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise RuntimeError("Define la variable de entorno GITHUB_TOKEN")

headers = {"Authorization": f"token {token}"}

# 2) Obtener issues de bug cerrados
url = "https://api.github.com/repos/facebook/react/issues"
params = {"labels": "bug", "state": "closed", "per_page": 100}
resp = requests.get(url, headers=headers, params=params)
resp.raise_for_status()
issues = resp.json()

# 3) Calcular tiempo de recuperación (horas)
recovery_hours = []
for i in issues:
    start = datetime.fromisoformat(i["created_at"][:-1])
    end   = datetime.fromisoformat(i["closed_at"]  [:-1])
    hours = (end - start).total_seconds() / 3600
    recovery_hours.append(hours)

# 4) Calcular y mostrar MTTR
mttr = mean(recovery_hours) if recovery_hours else 0
print(f"⏱ MTTR (horas): {mttr:.1f}h")
