# SPDX-License-Identifier: LicenseRef-Ultrastable-USL-1.0
# Copyright (c) 2026 Rowan Brad Quni-Gudzinas. Non-commercial use free; commercial use requires a license. See LICENSE.
"""Criticality scoreboard: verified deploys vs failures per day across the ultrastable org.
Usage: python scripts/criticality.py [days]  (needs gh CLI with org read access)"""
import json, subprocess, sys, datetime as dt, collections
days = int(sys.argv[1]) if len(sys.argv) > 1 else 14
since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).strftime("%Y-%m-%d")
def gh(*a): return json.loads(subprocess.check_output(["gh", *a], text=True) or "[]")
repos = [r["name"] for r in gh("repo", "list", "ultrastable", "--limit", "100", "--json", "name")]
per_day = collections.defaultdict(lambda: {"deploy_ok": 0, "deploy_fail": 0, "human_triggered": 0})
for r in repos:
    try:
        runs = gh("run", "list", "-R", f"ultrastable/{r}", "--limit", "300", "--created", f">={since}",
                  "--json", "name,conclusion,createdAt,event")
    except subprocess.CalledProcessError:
        continue
    for x in runs:
        if not x["name"].startswith(("deploy", "release", "self-hosting")): continue
        d = per_day[x["createdAt"][:10]]
        if x["conclusion"] == "success": d["deploy_ok"] += 1
        elif x["conclusion"] == "failure": d["deploy_fail"] += 1
        if x["event"] == "workflow_dispatch": d["human_triggered"] += 1
out = {"since": since, "days": dict(sorted(per_day.items()))}
out["total_verified_deploys"] = sum(v["deploy_ok"] for v in per_day.values())
s = json.dumps(out, indent=1)
print(s)
open("metrics/criticality.json", "w").write(s)

# --- spend (GitHub billing, current month) ---
FREE_MINUTES = 2000  # GitHub Free org, private-repo Linux minutes/month
items = json.loads(subprocess.check_output(["gh", "api", "orgs/ultrastable/settings/billing/usage"], text=True))["usageItems"]
now = dt.datetime.now(dt.timezone.utc)
month = [i for i in items if i["date"][:7] == now.strftime("%Y-%m")]
mins = sum(i["quantity"] for i in month if i["unitType"] == "Minutes")
proj = mins / now.day * 30
out["spend"] = {"month_minutes": mins, "free_minutes": FREE_MINUTES,
                "projected_month_minutes": round(proj),
                "gross_usd": round(sum(i["grossAmount"] for i in month), 2),
                "net_usd": round(sum(i["netAmount"] for i in month), 2),
                "over_budget_projected": proj > FREE_MINUTES}
s = json.dumps(out, indent=1); print(json.dumps(out["spend"], indent=1))
open("metrics/criticality.json", "w").write(s)
