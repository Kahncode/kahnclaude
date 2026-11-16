"""Build the setup-review artifact page from data.json + the agents' markdown reports.

Usage: python -I build_site.py <data.json> <out.html>
Report "file" paths in data.json resolve relative to data.json's folder.
Exits 2 if anything that looks like a secret is found, so nothing leaks into a published page.
"""
import json
import pathlib
import re
import sys

SECRET_PATTERNS = [
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "PEM private key"),
    (r"PrivateKey\s*=\s*[A-Za-z0-9+/]{40,}={0,2}", "WireGuard PrivateKey"),
    (r"\b(?:sk|pk|rk)-[A-Za-z0-9_-]{20,}", "API key prefix"),
    (r"\bxox[abprs]-[A-Za-z0-9-]{10,}", "Slack token"),
    (r"\bgh[pousr]_[A-Za-z0-9]{30,}", "GitHub token"),
    (r"\bAKIA[0-9A-Z]{16}\b", "AWS access key"),
    (r"(?i)\b(?:bearer|token|api[_-]?key|password|secret)\b\s*[:=]\s*['\"]?[A-Za-z0-9+/_.-]{24,}", "assigned credential"),
    (r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", "JWT"),
]


def scan(name, text):
    hits = []
    for pattern, label in SECRET_PATTERNS:
        for m in re.finditer(pattern, text):
            line = text.count("\n", 0, m.start()) + 1
            hits.append(f"{name}:{line}: looks like a {label}")
    return hits


def main():
    data_path, out_path = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    try:
        data = json.loads(data_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"{data_path.name} is not valid JSON: line {e.lineno}, column {e.colno}: {e.msg}")
    hits = scan(data_path.name, data_path.read_text(encoding="utf-8"))
    for key, rep in data["reports"].items():
        md_path = (data_path.parent / rep["file"]).resolve()
        if not md_path.exists():
            sys.exit(f"missing report for '{key}': {md_path}")
        rep["md"] = md_path.read_text(encoding="utf-8")
        hits += scan(md_path.name, rep["md"])
    if hits:
        print("Secret-like strings found; redact them in the source files and rebuild:", *hits, sep="\n  ")
        sys.exit(2)
    numbers = [it["n"] for b in data["batches"] for it in b["items"]]
    if len(numbers) != len(set(numbers)):
        sys.exit("item numbers 'n' must be unique across batches")
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/").replace("<!--", "<\\!--")
    tpl = (pathlib.Path(__file__).parent.parent / "assets" / "template.html").read_text(encoding="utf-8")
    title = data.get("title", "Claude setup review").replace("<", "&lt;")
    out_path.write_text(tpl.replace("__TITLE__", title, 1).replace("/*__DATA__*/", blob, 1), encoding="utf-8")
    print(f"built {out_path} ({len(blob):,} bytes data, {len(numbers)} items, {len(data['reports'])} subpages)")


if __name__ == "__main__":
    main()
