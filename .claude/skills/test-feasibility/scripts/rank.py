"""Score, sort and render test-feasibility items into report.md next to the input JSON.

Usage: python rank.py <out>/items.json [--title "Short title"]
If items.json is missing, every batch_*.json in the same folder is merged into it first.
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

REQUIRED = ["id", "kind", "title", "system", "verdict", "tier", "confidence", "coverage", "reason"]
SCORED_REQUIRED = ["oracle", "suggested_test", "severity", "recurrence", "hours"]
VERDICTS = {"yes", "maybe", "no", "n/a"}
CONFIDENCE_POINTS = {"High": 2, "Medium": 1, "Low": 0}
COVERAGE_POINTS = {"covered": -3, "extend": 1, "new": 0}
VERDICT_ORDER = {"yes": 0, "maybe": 1, "no": 2, "n/a": 3}


def load_items(path: Path) -> list[dict]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    batches = sorted(path.parent.glob("batch_*.json"))
    if not batches:
        sys.exit(f"error: {path} not found and no batch_*.json beside it")
    items = []
    for batch in batches:
        items += json.loads(batch.read_text(encoding="utf-8"))
    path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"merged {len(batches)} batches into {path}")
    return items


def validate(items: list[dict]) -> None:
    problems = []
    for item in items:
        tag = item.get("id", "<no id>")
        missing = [k for k in REQUIRED if k not in item]
        if item.get("verdict") in ("yes", "maybe"):
            missing += [k for k in SCORED_REQUIRED if k not in item]
        if missing:
            problems.append(f"{tag}: missing {', '.join(missing)}")
        if item.get("verdict") not in VERDICTS:
            problems.append(f"{tag}: verdict {item.get('verdict')!r} not in {sorted(VERDICTS)}")
    if problems:
        sys.exit("error: fix these items and re-run:\n  " + "\n  ".join(problems))


def cost_points(hours: float) -> int:
    if hours <= 2:
        return 0
    if hours <= 8:
        return -1
    if hours <= 16:
        return -2
    return -3


def score(item: dict) -> None:
    if item["verdict"] not in ("yes", "maybe"):
        item["score"], item["priority"] = None, "—"
        return
    points = (int(item["severity"]) + int(item["recurrence"])
              + CONFIDENCE_POINTS.get(item["confidence"], 0)
              + cost_points(float(item["hours"]))
              + COVERAGE_POINTS.get(item["coverage"], 0))
    item["score"] = points
    item["priority"] = "P0" if points >= 6 else "P1" if points >= 4 else "P2" if points >= 2 else "P3"


def sort_key(item: dict):
    return (VERDICT_ORDER[item["verdict"]], item["coverage"] == "covered",
            -(item["score"] if item["score"] is not None else -99), float(item.get("hours", 99)))


def cell(text) -> str:
    return str(text if text not in (None, "") else "—").replace("|", "\\|").replace("\n", " ")


def ranked_table(items: list[dict]) -> list[str]:
    rows = ["| # | ID | Item | Verdict | Tier | Confidence | Priority (score) | Coverage | Est. h | Test |",
            "|---|----|------|---------|------|-----------|------------------|----------|--------|------|"]
    for n, it in enumerate(items, 1):
        where = f"{it['coverage']}: {it.get('coverage_where', '')}".rstrip(": ")
        rows.append(f"| {n} | {cell(it['id'])} | {cell(it['title'])} | {it['verdict']} | {cell(it['tier'])} | "
                    f"{it['confidence']} | {it['priority']} ({it['score']}) | {cell(where)} | {cell(it['hours'])} | "
                    f"{cell(it['suggested_test'])} |")
    return rows


def detail_block(it: dict) -> list[str]:
    lines = [f"### {it['id']}: {it['title']}",
             f"- **Verdict** {it['verdict']} · **Tier** {it['tier']} · **Confidence** {it['confidence']} · "
             f"**Priority** {it['priority']} ({it['score']}) · **Est.** {it['hours']} h",
             f"- **Oracle:** {it['oracle']}",
             f"- **Test:** {it['suggested_test']}",
             f"- **Coverage:** {it['coverage']} {it.get('coverage_where', '')}".rstrip(),
             f"- **Why:** {it['reason']}"]
    if it.get("root_cause") and it["root_cause"] != "unknown":
        lines.append(f"- **Root cause:** {it['root_cause']}" + (f" (CL {', '.join(map(str, it['fix_cls']))})" if it.get("fix_cls") else ""))
    if it.get("blocker"):
        lines.append(f"- **Blocker / open question:** {it['blocker']}")
    return lines + [""]


def counts_line(items: list[dict]) -> str:
    by = {v: sum(1 for i in items if i["verdict"] == v) for v in ("yes", "maybe", "no", "n/a")}
    covered = sum(1 for i in items if i["coverage"] == "covered")
    return (f"**{len(items)} items:** {by['yes']} yes · {by['maybe']} maybe · {by['no']} no · {by['n/a']} n/a "
            f"· {covered} already covered")


def render(items: list[dict], title: str) -> str:
    actionable = [i for i in items if i["verdict"] in ("yes", "maybe") and i["coverage"] != "covered"]
    covered = [i for i in items if i["coverage"] == "covered"]
    rejected = [i for i in items if i["verdict"] in ("no", "n/a")]
    top = [i for i in actionable if i["priority"] == "P0"][:3] or actionable[:3]
    out = [f"# {title}", "", f"_{date.today().isoformat()} · judgement from tickets and code; nothing was run._", "",
           "## Start here", ""]
    out += [f"{n}. **{i['id']}** {i['title']}: {i['suggested_test']} (~{i['hours']} h)" for n, i in enumerate(top, 1)]
    out += ["", "## Counts", "", counts_line(items), "", "## Ranked: write these", ""] + ranked_table(actionable)
    if covered:
        out += ["", "## Already covered", ""] + [f"- **{i['id']}** {i['title']}: {i.get('coverage_where', '')}" for i in covered]
    out += ["", "## Not automatable", ""] + [f"- **{i['id']}** ({i['verdict']}) {i['title']}: {i['reason']}" for i in rejected]
    blockers = [i for i in actionable if i.get("blocker")]
    if blockers:
        out += ["", "## Open questions and blockers", ""] + [f"- **{i['id']}**: {i['blocker']}" for i in blockers]
    out += ["", "## Detail", ""]
    for it in actionable + covered:
        out += detail_block(it)
    return "\n".join(out) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("items", type=Path)
    parser.add_argument("--title", default="Test Feasibility")
    args = parser.parse_args()
    items = load_items(args.items)
    validate(items)
    for item in items:
        score(item)
    items.sort(key=sort_key)
    args.items.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    report = args.items.parent / "report.md"
    report.write_text(render(items, args.title), encoding="utf-8")
    print(counts_line(items))
    print(f"report: {report}")


if __name__ == "__main__":
    main()
