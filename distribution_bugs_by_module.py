import os
import requests
from collections import Counter
import matplotlib.pyplot as plt

# 1) Leer token
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise RuntimeError("Define la variable de entorno GITHUB_TOKEN")
headers = {"Authorization": f"token {token}"}

owner, repo = "facebook", "react"

# 2) Recoger issues cerrados (hasta 500) y filtrar bugs
all_issues = []
for page in range(1, 6):
    r = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/issues",
        headers=headers,
        params={"state": "closed", "per_page": 100, "page": page}
    )
    r.raise_for_status()
    chunk = r.json()
    if not chunk:
        break
    all_issues.extend(chunk)

bug_issues = [
    i for i in all_issues
    if any("bug" in lbl["name"].lower() for lbl in i.get("labels", []))
]

# 3) Contar “módulos” según labels extra
module_counter = Counter()
for issue in bug_issues:
    # Usamos cualquier etiqueta que no sea “bug” o “type: bug”
    mods = [lbl["name"] for lbl in issue.get("labels", [])
            if "bug" not in lbl["name"].lower()]
    if mods:
        for m in mods:
            module_counter[m] += 1
    else:
        module_counter["Uncategorized"] += 1

top_modules = module_counter.most_common(8)

# 4) Mostrar en consola
print("🏷️ Top módulos por número de bugs:")
for mod, cnt in top_modules:
    print(f"{mod:20s} → {cnt} bugs")

# 5) Graficar
labels, counts = zip(*top_modules)
plt.figure(figsize=(8,5))
plt.barh(labels, counts)
plt.xlabel("Número de Bugs")
plt.title("Distribución de Bugs por Módulo")
plt.tight_layout()
plt.savefig("bugs_by_module.png")
plt.show()
