# SPDX-License-Identifier: LicenseRef-Ultrastable-USL-1.0
# Copyright (c) 2026 Rowan Brad Quni-Gudzinas. Non-commercial use free; commercial use requires a license. See LICENSE.
"""The mantra, as code. Every loop ends by calling this; it is the system talking to itself.

    SHIP ONE VERIFIED THING. MAKE THE NEXT ONE CHEAPER. START IT.

Each clause is a check, not a sentence:
  1. SHIP   - verified deploys in the window > 0           (the reaction is alive)
  2. CHEAPER- k = verified deploys / (human-triggered runs + Actions minutes/100) >= 1,
              and spend projected under budget              (output exceeds what it consumes)
  3. START  - the run names its successor: a next-work item exists in metrics/next.json
              (the output feeds another loop; bootstrapping = the system writes its own next input)
Exit 0 only when all three hold. A nonzero exit is the signal another loop acts on.
Usage: python scripts/mantra.py   (reads metrics/criticality.json from scripts/criticality.py)
"""
import json, sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
m = json.loads((root / "metrics/criticality.json").read_text())
days = m["days"].values()
deploys = sum(d["deploy_ok"] for d in days)
human = sum(d["human_triggered"] for d in days)
spend = m.get("spend", {})
cost_units = human + spend.get("projected_month_minutes", 0) / 100
k = deploys / cost_units if cost_units else float(deploys)
nxt = root / "metrics/next.json"
next_items = json.loads(nxt.read_text()) if nxt.exists() else []
checks = {
    "ship": deploys > 0,
    "cheaper": k >= 1 and not spend.get("over_budget_projected", False),
    "start": len(next_items) > 0,
}
report = {"k": round(k, 2), "deploys": deploys, "human_triggered": human, "checks": checks,
          "next": next_items[:3], "critical": all(checks.values())}
print(json.dumps(report, indent=1))
(root / "metrics/mantra.json").write_text(json.dumps(report, indent=1))
sys.exit(0 if report["critical"] else 1)
