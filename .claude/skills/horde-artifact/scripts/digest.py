"""Digest an unzipped Horde step-saved artifact into DIGEST.md (stdlib only).

Usage: python -I -X utf8 digest.py <unzipped dir | step .log> [--runbook <md>] [--out <md>]
Scans step logs (Saved/Logs[/RunUnreal]/Log.txt), every EditorOutput.log (Pass_N, Retry_N),
EventStreams/*.json and Saved/Automation/Reports/**/index.json, then matches the runbook.
Runbook default: HORDE_RUNBOOK. Project headlines: HORDE_DIGEST_HEADLINES ("name=regex:cap;...").
"""
import argparse, json, re, sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude" / "scripts" / "lib"))
from project_vars import get  # noqa: E402

TS = re.compile(r"^\[(\d{4}\.\d\d\.\d\d-\d\d\.\d\d\.\d\d:\d{3})\]\[\s*\d+\]")
STARTED = re.compile(r"Test Started\. Name=\{.*?\} Path=\{(.+?)\}")
FAILED = re.compile(r"Result=\{Fail\} Name=\{.*?\} Path=\{(.+?)\}")
BEGIN = re.compile(r"LogAutomationController: BeginEvents: (\S+)")
STEP_FAIL = re.compile(r"\* Test '(.+?)' failed\.")
CRASH = re.compile(r"=== Handled ensure|Ensure condition failed|Assertion failed|Fatal error|=== Critical error|"
                   r"Unhandled Exception|EXCEPTION_ACCESS_VIOLATION|DXGI_ERROR_\w+|Out of video memory|"
                   r"Data race detected|EditorCrashDetected|\berror (?:C|LNK)\d{4}")
HEADS = {"asset registry": (re.compile(r"AssetRegistryGather time"), 3),
         "long frame (>= 60 s)": (re.compile(r"Ignoring very large delta of (?:\d{3,}|[6-9]\d)\."), 6)}
STEP_KEEP = re.compile(r"Test Summary:|Editor Role:|Editor (?:completed|failed):|\* \d+ Test\(s\)|ExitCode=|"
                       r"\) result=|\* Log Errors:|TimedOut|No activity observed|Download took")
SECRET = re.compile(r"(?i)token|clientlogin|password|secret|authorization|bearer")


def clip(text, n=220):
    text = TS.sub("", text.strip()).replace("Err0r", "Error").replace("Warn1ng", "Warning").replace("|", "/")
    return "[line redacted: may hold a credential]" if SECRET.search(text) else text[:n]


def project_heads(spec):
    """HORDE_DIGEST_HEADLINES entries `name=regex:cap`, `;`-separated, listed before the generic heads."""
    heads = {}
    for item in filter(None, (s.strip() for s in spec.split(";"))):
        name, rest = item.split("=", 1)
        rx, cap = rest.rsplit(":", 1)
        heads[name.strip()] = (re.compile(rx), int(cap))
    return heads


def load_runbook(path):
    sigs = {}
    for line in path.read_text(encoding="utf-8").splitlines() if path and path.is_file() else []:
        cells = re.split(r"(?<!\\)\|", line.strip().strip("|"))
        if len(cells) > 1 and cells[0].strip() != "Signature" and not set(cells[0].strip()) <= set("-: "):
            for s in re.findall(r"`([^`]+)`", cells[0]):
                sigs[s.replace("\\|", "|")] = clip(cells[1], 60)
    return sigs


class Digest:
    def __init__(self, sigs, has_editor, head_rx):
        self.sigs, self.has_editor, self.hits, self.fails, self.events = sigs, has_editor, {}, {}, {}
        self.head_rx = head_rx
        self.crash, self.step, self.heads = [], [], {k: [] for k in head_rx}

    def common(self, line, label, n, ts, test):
        full = label[0] != "S" or not self.has_editor  # the step log mirrors the editor log
        for s in self.sigs:
            if s in line and (full or s not in self.hits):
                self.hits.setdefault(s, [0, f"{label}:{n} {clip(line, 160)}"])[0] += 1
        if full and len(self.crash) < 15 and CRASH.search(line):
            self.crash.append(f"- `{ts or '-'}` [{test or 'no test'}] {clip(line, 180)} ({label}:{n})")
        for key, (rx, cap) in self.head_rx.items():
            if full and len(self.heads[key]) < cap and rx.search(line):
                self.heads[key].append(f"- `{ts or '-'}` {clip(line, 200)} ({label}:{n})")

    def scan_editor(self, path, label):
        cur = block = None
        ts = ""
        with open(path, encoding="utf-8", errors="replace") as f:
            for n, line in enumerate(f, 1):
                m = TS.match(line)
                ts = m.group(1) if m else ts
                if "LogAutomationController" in line:
                    m, s, b = FAILED.search(line), STARTED.search(line), BEGIN.search(line)
                    if m:
                        self.fails.setdefault((m.group(1), label), {"at": ts, "err": "", "where": ""})
                    rec = self.fails.get((block, label))
                    if rec is not None and not rec["err"] and "Error: " in line:
                        rec["err"], rec["where"] = clip(line.split("Error: ", 1)[1]), f"{label}:{n}"
                    cur = s.group(1) if s else cur
                    block = b.group(1) if b else (None if "EndEvents:" in line else block)
                self.common(line, label, n, ts, cur)

    def scan_step(self, path, label):
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for n, line in enumerate(lines, 1):
            m = STEP_FAIL.search(line)
            if m:
                reason = lines[n] if n < len(lines) and lines[n].startswith("   ") else ""
                self.fails.setdefault((m.group(1), label), {"at": "", "err": clip(reason), "where": f"{label}:{n + 1}"})
            text = clip(line, 200)
            if len(self.step) < 15 and STEP_KEEP.search(line) and not any(x.startswith(f"- {text} (") for x in self.step):
                self.step.append(f"- {text} ({label}:{n})")
            self.common(line, label, n, "", None)

    def scan_events(self, path):
        try:
            for e in json.loads(path.read_text(encoding="utf-8", errors="replace")):
                if e.get("level") == "Error":
                    self.events.setdefault(clip(e.get("message", ""))[:80], e.get("time", ""))
        except (ValueError, AttributeError) as err:
            print(f"warn: skipped {path}: {err}")

    def scan_report(self, path, label):
        for t in json.loads(path.read_text(encoding="utf-8-sig", errors="replace")).get("tests", []):
            if t.get("state") == "Fail":
                first = next((e for e in t.get("entries", []) if e["event"]["type"] == "Error"), None)
                self.fails[(t["fullTestPath"], label)] = {"at": t.get("dateTime", ""), "where": label,
                    "err": clip(first["event"]["message"]) if first else "", "evt": first["timestamp"] if first else ""}

    def fail_rows(self):
        step = {t: r for (t, l), r in self.fails.items() if l[0] == "S"}
        in_editor = {t for (t, l) in self.fails if l[0] != "S"}
        for (test, label), r in self.fails.items():
            if label[0] == "S" and test in in_editor:
                continue
            if not r["err"] and test in step:
                r = dict(r, err=step[test]["err"], where=step[test]["where"])
            evt = r.get("evt") or self.events.get(r["err"][:80], "")
            yield f"| {test} | {r['at'] or '-'} | {r['err'] or '-'} | {evt or '-'} | {r['where'] or label} |"


def write(d, root, files, out, runbook):
    rows = list(d.fail_rows())
    w = [f"# Horde digest: {root.name}", "", f"Generated {datetime.now():%Y-%m-%d %H:%M} by digest.py. "
         f"Runbook: {runbook} ({len(d.sigs)} signatures).", "", "## Result", ""] + (d.step or ["- no step summary found"])
    w += ["", f"## Failing tests ({len(rows)})", "", "| Test | Failed at | First error | Event time | Where |",
          "|---|---|---|---|---|"] + rows
    w += ["", "## Crash / ensure / fatal / compile errors (first 15)", ""] + (d.crash or ["- none"])
    w += ["", "## Runbook signature hits", ""]
    if d.hits:
        w += ["| Signature | Verdict | Hits | First hit |", "|---|---|---|---|"]
        w += [f"| `{s.replace('|', chr(92) + '|')}` | {d.sigs[s]} | {c} | {first} |" for s, (c, first) in d.hits.items()]
    else:
        w.append("- none: no known signature matched; still check threshold rows against Headlines")
    w += ["", "## Headlines", ""]
    for key, lines in d.heads.items():
        w += [f"**{key}**", ""] + (lines or ["- none"]) + [""]
    w += ["## Files", ""] + [f"- {label} = {p} ({p.stat().st_size // 1024} KB)" for label, p in files]
    w.append(f"- EventStreams: {len(d.events)} error events indexed")
    out.write_text("\n".join(w) + "\n", encoding="utf-8")
    return len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--runbook", type=Path)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    root = a.root.resolve()
    if root.is_file():
        steps, editors, reports, events, out = [root], [], [], [], root.with_name(root.stem + "-DIGEST.md")
    else:
        steps = sorted(root.rglob("RunUnreal/Log.txt")) or sorted(root.rglob("Saved/Logs/Log.txt"))
        editors, events = sorted(root.rglob("EditorOutput.log")), sorted(root.rglob("EventStreams/*.json"))
        reports = [p for p in sorted(root.rglob("index.json")) if {"Reports", "TestReport"} & set(p.parts)]
        out = root / "DIGEST.md"
    files = [(f"E{i}", p) for i, p in enumerate(editors, 1)] + [(f"S{i}", p) for i, p in enumerate(steps, 1)]
    files += [(f"R{i}", p) for i, p in enumerate(reports, 1)]
    runbook = a.runbook or (Path(v) if (v := get("HORDE_RUNBOOK", "")) else None)
    if runbook is None:
        print("warn: no --runbook and HORDE_RUNBOOK is not set; no runbook signatures matched")
    heads = {**project_heads(get("HORDE_DIGEST_HEADLINES", "")), **HEADS}
    d = Digest(load_runbook(runbook), bool(editors), heads)
    for p in events:
        d.scan_events(p)
    for label, p in files:
        {"S": d.scan_step, "E": d.scan_editor, "R": d.scan_report}[label[0]](p, label)
    out = a.out or out
    n = write(d, root, files, out, runbook)
    print(f"{out}  ({n} failing, {len(d.crash)} crash lines, {len(d.hits)} runbook hits)")


if __name__ == "__main__":
    main()
