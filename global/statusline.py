import json
import subprocess
import sys

data = json.loads(sys.stdin.read())
cwd = data.get("cwd", "")
model = data.get("model", {}).get("display_name", "")
ctx = data.get("context_window", {}).get("used_percentage") or 0
cost = data.get("cost", {}).get("total_cost_usd") or 0

branch = ""
try:
    result = subprocess.run(
        ["git", "-C", cwd, "--no-optional-locks", "symbolic-ref", "--short", "HEAD"],
        capture_output=True,
        text=True,
    )
    branch = result.stdout.strip()
except Exception:
    pass

limits = data.get("rate_limits", {})
five = limits.get("five_hour", {}).get("used_percentage")
week = limits.get("seven_day", {}).get("used_percentage")

budget = ""
if five is not None and week is not None:
    budget = f" | 5h:{five:.0f}% 7d:{week:.0f}%"
elif five is not None:
    budget = f" | 5h:{five:.0f}%"
elif week is not None:
    budget = f" | 7d:{week:.0f}%"

if branch:
    print(f"{cwd} | {branch} | {model} | {ctx:.0f}% ctx | ${cost:.4f}{budget}", end="")
else:
    print(f"{cwd} | {model} | {ctx:.0f}% ctx | ${cost:.4f}{budget}", end="")
