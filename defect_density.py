# defect_density.py
import os
import requests

# 1) Leer token
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise RuntimeError("Define la variable de entorno GITHUB_TOKEN con tu token de GitHub")
headers = {"Authorization": f"token {token}"}

owner, repo = "facebook", "react"

# 2) Contar issues etiquetados “bug”
all_issues = []
for page in range(1, 6):  # hasta 500 issues
    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/issues",
        headers=headers,
        params={"state": "closed", "per_page": 100, "page": page}
    )
    resp.raise_for_status()
    data = resp.json()
    if not data:
        break
    all_issues.extend(data)

bug_issues = [
    i for i in all_issues
    if any("bug" in lbl["name"].lower() for lbl in i.get("labels", []))
]
bug_count = len(bug_issues)

# 3) Obtener métricas de tamaño de código (bytes)
lang_resp = requests.get(
    f"https://api.github.com/repos/{owner}/{repo}/languages",
    headers=headers
).json()
total_bytes = sum(lang_resp.values())

# 4) Estimar LOC (suposición: 50 bytes por línea)
estimated_loc = total_bytes / 50

# 5) Calcular densidad
density = bug_count / estimated_loc if estimated_loc else 0

# 6) Mostrar resultados
print(f"🐞 Bugs cerrados analizados: {bug_count}")
print(f"📦 Código estimado: {estimated_loc:.0f} líneas")
print(f"📊 Densidad de defectos: {density:.6f} bugs/LOC")
