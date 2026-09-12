#!/usr/bin/env python3
"""Rebuild CATALOG.md and apps.json for the Shizuku F-Droid repo.

Sources:
  1. https://github.com/timschneeb/awesome-shizuku (upstream curated list)
  2. GitHub repository search for extra Shizuku apps (needs GITHUB_TOKEN)

Writes CATALOG.md and apps.json into the repo root. Stdlib only.
"""
import datetime
import json
import os
import re
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPSTREAM = "https://raw.githubusercontent.com/timschneeb/awesome-shizuku/master/README.md"


def fetch(url, token=None):
    headers = {"User-Agent": "shizuku-fdroid-repo-updater"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def parse_upstream(md):
    apps, cat, in_apps = [], None, False
    for line in md.splitlines():
        if line.startswith("## Apps"):
            in_apps = True
            continue
        if in_apps and re.match(r"## \S", line):
            break
        if in_apps and line.startswith("### "):
            cat = line[4:].strip()
            continue
        m = re.match(r"\* \[([^\]]+)\]\(([^)]+)\)\s*(?:-\s*(.*))?", line)
        if in_apps and cat and m:
            name = m.group(1).strip()
            url = m.group(2).strip()
            desc = (m.group(3) or "").strip()
            desc = re.sub(r"\s*(`[^`]*`)+\s*$", "", desc).strip()
            repo = ""
            g = re.match(r"https://github\.com/([^/\s]+)/([^/\s)]+)", url)
            if g:
                repo = g.group(1) + "/" + g.group(2)
            apps.append({"name": name, "category": cat, "github": repo,
                         "url": url, "description": desc})
    return apps


def github_extras(token):
    """Find Shizuku app repos beyond the curated list (best-effort)."""
    if not token:
        return []
    found = []
    try:
        q = urllib.parse.quote("shizuku in:name,description,readme")
        url = ("https://api.github.com/search/repositories?q=" + q +
               "&per_page=100&sort=stars&order=desc")
        data = json.loads(fetch(url, token))
        for item in data.get("items", []):
            if item.get("fork") or item.get("archived"):
                continue
            desc = (item.get("description") or "").replace("\n", " ").strip()
            blob = (desc + " " + (item.get("name") or "")).lower()
            if "android" not in blob:
                continue
            found.append({"name": item["name"],
                          "category": "Discovered via GitHub search",
                          "github": item["full_name"],
                          "url": item["html_url"],
                          "description": desc})
    except Exception as e:
        print("GitHub search skipped:", e)
    return found


def main():
    md = fetch(UPSTREAM)
    apps = parse_upstream(md)
    seen = set(a["github"].lower() for a in apps if a["github"])
    for extra in github_extras(os.environ.get("GITHUB_TOKEN")):
        if extra["github"].lower() not in seen:
            seen.add(extra["github"].lower())
            apps.append(extra)
    today = datetime.date.today().isoformat()
    with open(os.path.join(ROOT, "apps.json"), "w", encoding="utf-8") as f:
        json.dump(apps, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(os.path.join(ROOT, "CATALOG.md"), "w", encoding="utf-8") as f:
        f.write("# Shizuku Apps Catalog (%d apps)\n\n" % len(apps))
        f.write("Auto-generated from [timschneeb/awesome-shizuku]"
                "(https://github.com/timschneeb/awesome-shizuku) on %s. "
                "Sorted by category.\n" % today)
        cat = None
        for a in apps:
            if a["category"] != cat:
                cat = a["category"]
                f.write("\n## %s\n\n" % cat)
            link = a["url"] or ("https://github.com/" + a["github"] if a["github"] else "")
            f.write("- [%s](%s)" % (a["name"], link))
            if a["description"]:
                f.write(" \u2014 %s" % a["description"])
            f.write("\n")
    print("wrote %d apps" % len(apps))


if __name__ == "__main__":
    main()
