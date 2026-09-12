# Shizuku F-Droid Repo

All Shizuku-enabled Android apps in one place: a browsable catalog now, a real F-Droid-compatible repository you can add in F-Droid / Droid-ify / Neo Store next.

## Browse (works today)

- [CATALOG.md](CATALOG.md) — 354 apps grouped by category
- [apps.json](apps.json) — same data, machine-readable

## Add to F-Droid (in progress)

A signed `index-v1.json` repo (fdroidserver metadata per app: package name, version codes, APKs) is being built next. Until then the catalog above is the way to find apps.

## Sources

- [timschneeb/awesome-shizuku](https://github.com/timschneeb/awesome-shizuku) — curated base list (327 apps)
- GitHub search (`shizuku` in name/description/readme) — extra apps beyond the list, under "Discovered via GitHub search"

## Auto-update

`.github/workflows/update.yml` rebuilds `CATALOG.md` + `apps.json` every Monday via `scripts/build_catalog.py` (stdlib only, no dependencies). Run it manually:

```sh
python3 scripts/build_catalog.py
```

Set `GITHUB_TOKEN` to also merge GitHub search discoveries.
