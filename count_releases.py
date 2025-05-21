# tags_frequency.py
import os, requests
from collections import Counter
from datetime import datetime


TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise RuntimeError("Define GITHUB_TOKEN en tu entorno")

HEADERS = {"Authorization": f"token {TOKEN}"}
OWNER, REPO = "facebook", "react"

# 1) Traer tags (paging automático si quieres más)
tags = []
page = 1
while True:
    resp = requests.get(
        f"https://api.github.com/repos/{OWNER}/{REPO}/tags",
        headers=HEADERS,
        params={"per_page": 100, "page": page}
    ).json()
    if not resp:
        break
    tags.extend(resp)
    page += 1

# 2) Para cada tag, sacar la fecha del commit (anotado o ligero)
dates = []
for tag in tags:
    commit_url = tag["commit"]["url"]
    c = requests.get(commit_url, headers=HEADERS).json()

    # 1) Annotated tag (API git/commits): tiene 'author' y 'committer' al tope
    if "committer" in c and isinstance(c["committer"], dict) and "date" in c["committer"]:
        date_str = c["committer"]["date"]
    # 2) Lightweight tag via repos/.../commits/:sha → payload bajo 'commit'
    elif "commit" in c and "committer" in c["commit"] and "date" in c["commit"]["committer"]:
        date_str = c["commit"]["committer"]["date"]
    # 3) Fallback a 'author'
    elif "commit" in c and "author" in c["commit"] and "date" in c["commit"]["author"]:
        date_str = c["commit"]["author"]["date"]
    else:
        # si ni siquiera existe, saltar este tag
        continue

    # guardamos sólo YYYY-MM-DD
    dates.append(date_str[:10])


# 3) Contar por día
freq_by_day = Counter(dates)
print("📅 Deployment Frequency por día:")
for day, cnt in sorted(freq_by_day.items()):
    print(f"  {day}: {cnt}")

# 4) (Opcional) Contar por semana ISO
weeks = [ datetime.fromisoformat(d).isocalendar()[1] for d in dates ]
freq_by_week = Counter(weeks)
print("\n🗓 Deployment Frequency por semana ISO:")
for w, cnt in sorted(freq_by_week.items()):
    print(f"  Semana {w}: {cnt}")
