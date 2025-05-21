import os, requests

# 1) Token y headers
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise RuntimeError("Define GITHUB_TOKEN en tu entorno")
H = {"Authorization": f"token {token}"}

# 2) Llamada a issues “bug” cerrados
url = "https://api.github.com/repos/facebook/react/issues"
params = {"labels": "bug", "state": "closed", "per_page": 100}
issues = requests.get(url, headers=H, params=params).json()

bug_count = len(issues)
hotfix_count = sum(1 for i in issues if "hotfix" in i["title"].lower())

# 3) Cálculo de CFR
cfr = (hotfix_count / bug_count * 100) if bug_count else 0
print(f"🐞 Total bugs cerrados: {bug_count}")
print(f"🔧 Hotfixes detectados: {hotfix_count}")
print(f"📊 Change Failure Rate: {cfr:.1f}%")
