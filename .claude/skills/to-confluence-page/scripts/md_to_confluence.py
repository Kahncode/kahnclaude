#!/usr/bin/env python3
"""Convert local Markdown docs into Confluence storage bodies that need no local context.

- Links to other mapped docs become links to their Confluence page, with the page title as text.
- Links to unmapped local files become plain text (no dead or local hrefs).
- Mermaid blocks are rendered to PNG (mermaid-cli + installed Chrome), embedded as attachments,
  with the source kept in a collapsed "Diagram source (Mermaid)" expand.
- Fails if anything local or unrenderable is left: '.md' names, relative hrefs, bare Mermaid.

Usage:
  python -I md_to_confluence.py --map pages.json --out <dir> [--only example.md]

pages.json: [{"source": "C:/MyProject/docs/subsystems/example.md", "pageId": "123456789",
              "title": "Example Subsystem"}, ...]
Writes <out>/<stem>/bundle.json = {id, title, source, body, attachments: [{name, b64}]}.
Site and tools folder come from project-vars: CONFLUENCE_URL, CONFLUENCE_SPACE_KEY, TEMP_BASE.
"""
import argparse
import base64
import html
import json
import os
import re
import struct
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude" / "scripts" / "lib"))
from project_vars import get  # noqa: E402

SITE = ""      # set by configure() from CONFLUENCE_URL + CONFLUENCE_SPACE_KEY
TOOLS = Path()  # set by configure() to TEMP_BASE\to-confluence-tools
BROWSERS = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]
MAX_IMAGE_WIDTH = 1800  # Confluence shrinks to the content column; full res stays in the click-to-zoom view
WIDE_WARNING = 1800     # natural px; wider than a full-width page, so text is small until zoomed
# mmdc's default 800 px viewport plus useMaxWidth squeezes wide diagrams to illegible text, so render at
# natural size instead.
MERMAID_CONFIG = {kind: {"useMaxWidth": False} for kind in
                  ("flowchart", "sequence", "class", "state", "er", "gantt", "journey", "graph")}


def configure():
    global SITE, TOOLS
    SITE = f"{get('CONFLUENCE_URL').rstrip('/')}/spaces/{get('CONFLUENCE_SPACE_KEY')}/pages"
    TOOLS = Path(get("TEMP_BASE")) / "to-confluence-tools"


def ensure_tools():
    """Install python-markdown and mermaid-cli into the shared TEMP_BASE tools folder once."""
    TOOLS.mkdir(parents=True, exist_ok=True)
    pylib = TOOLS / "pylib"
    if not (pylib / "markdown").exists():
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "--target", str(pylib), "markdown"],
                       check=True)
    sys.path.insert(0, str(pylib))
    mmdc = TOOLS / "node_modules" / ".bin" / "mmdc.cmd"
    if not mmdc.exists():
        env = dict(os.environ, PUPPETEER_SKIP_DOWNLOAD="1")
        subprocess.run("npm i --silent --no-audit --no-fund @mermaid-js/mermaid-cli@11.4.2",
                       cwd=TOOLS, shell=True, check=True, env=env)
    browser = next((b for b in BROWSERS if Path(b).exists()), None)
    if not browser:
        raise SystemExit("No Chrome/Edge found for Mermaid rendering")
    config = TOOLS / "puppeteer.json"
    config.write_text(json.dumps({"executablePath": browser.replace("\\", "/"), "args": ["--no-sandbox"]}))
    (TOOLS / "mermaid-config.json").write_text(json.dumps(MERMAID_CONFIG))
    return mmdc, config


def page_url(entry):
    return f"{SITE}/{entry['pageId']}/{entry['title'].replace(' ', '+')}"


def heading_texts(md_text):
    """GitHub-style slug -> plain heading text, for anchor rewriting."""
    out = {}
    for m in re.finditer(r"^#{1,6}\s+(.+?)\s*$", md_text, re.M):
        text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", m.group(1))
        text = re.sub(r"[`*_]", "", text).strip()
        slug = re.sub(r"[^\w\- ]", "", text.lower()).replace(" ", "-")
        out[slug] = text
    return out


def doc_title(md_text, fallback):
    m = re.match(r"\A#\s+(.+)", md_text)
    return m.group(1).strip() if m else fallback


class LinkResolver:
    def __init__(self, entries, docs):
        self.by_path = {Path(e["source"]).resolve(): e for e in entries}
        self.docs = docs  # resolved path -> markdown text (mapped + any linked local .md read lazily)

    def _read(self, path):
        if path not in self.docs and path.exists():
            self.docs[path] = path.read_text(encoding="utf-8")
        return self.docs.get(path, "")

    def resolve(self, href, own_path):
        """Return (url or None, display text for a local target, or None to keep the author's text)."""
        if re.match(r"^[a-z]+://|^mailto:", href):
            return href, None
        target, _, frag = href.partition("#")
        path = (own_path.parent / target).resolve() if target else own_path
        heading = heading_texts(self._read(path)).get(frag) if frag else None
        anchor = "#" + re.sub(r"\s+", "-", heading) if heading else ""
        entry = self.by_path.get(path)
        if entry:
            label = entry["title"] + (f" › {heading}" if heading and target else "")
            return (anchor if not target else page_url(entry) + anchor), (heading or label if not target else label)
        if path.suffix == ".md" and path.exists():
            return None, doc_title(self._read(path), path.stem)  # local doc with no page: name it, no link
        return None, None  # source file or other local path: keep author's text, drop the link


def fix_links(xhtml, own_path, resolver):
    def repl(m):
        attrs, text = m.group(1), m.group(2)
        href = html.unescape(re.search(r'href="([^"]*)"', attrs).group(1))
        url, label = resolver.resolve(href, own_path)
        looks_local = re.fullmatch(r"\s*(<code>)?[\w./\\#-]+\.(md|h|cpp|py|ini)(</code>)?\s*", text)
        shown = html.escape(label) if label and (looks_local or not text.strip()) else text
        if url is None:
            return shown  # local target with no Confluence page: keep the words, drop the link
        return f'<a href="{html.escape(url)}">{shown}</a>'
    return re.sub(r"<a ([^>]*)>(.*?)</a>", repl, xhtml, flags=re.S)


def fix_bare_doc_names(xhtml, own_path, resolver):
    """`other-doc.md` mentioned in code or prose (outside links) -> link to its page or its title."""
    def repl(m):
        name = m.group(2)
        url, label = resolver.resolve(name, own_path)
        if url:
            return f'<a href="{html.escape(url)}">{html.escape(label)}</a>'
        return html.escape(label) if label else m.group(0)
    parts = re.split(r"(<a [^>]*>.*?</a>|<!\[CDATA\[.*?\]\]>)", xhtml, flags=re.S)
    pattern = r"(<code>)?\b([\w./-]+\.md)\b(?(1)</code>)"
    return "".join(p if i % 2 else re.sub(pattern, repl, p) for i, p in enumerate(parts))


def png_width(data):
    return struct.unpack(">I", data[16:20])[0]


def render_mermaid(source, png_path, mmdc, config):
    mmd = png_path.with_suffix(".mmd")
    mmd.write_text(source, encoding="utf-8")
    proc = subprocess.run([str(mmdc), "-i", str(mmd), "-o", str(png_path), "-p", str(config),
                           "-c", str(TOOLS / "mermaid-config.json"), "-b", "white", "-s", "2", "-q"],
                          capture_output=True, text=True, shell=False)
    if proc.returncode or not png_path.exists():
        raise SystemExit(f"Mermaid render failed for {png_path.name}:\n{proc.stderr[-1500:]}\n--- source ---\n{source}")
    return png_path.read_bytes()


def cdata(text):
    return "<![CDATA[" + text.replace("]]>", "]]]]><![CDATA[>") + "]]>"


def code_macro(lang, body):
    lang_param = f'<ac:parameter ac:name="language">{lang}</ac:parameter>' if lang else ""
    return (f'<ac:structured-macro ac:name="code" ac:schema-version="1">{lang_param}'
            f"<ac:plain-text-body>{cdata(body)}</ac:plain-text-body></ac:structured-macro>")


def convert_code_blocks(xhtml, stem, out_dir, mmdc, config):
    attachments = []

    def repl(m):
        lang, body = m.group(1) or "", html.unescape(m.group(2)).rstrip("\n")
        if lang != "mermaid":
            return code_macro(lang, body)
        name = f"{stem}-diagram-{len(attachments) + 1}.png"
        data = render_mermaid(body, out_dir / name, mmdc, config)
        attachments.append({"name": name, "b64": base64.b64encode(data).decode()})
        natural = png_width(data) // 2
        if natural > WIDE_WARNING:
            print(f"  WARNING {name}: {natural} px wide, text is small on the page until clicked. "
                  "A top-down layout (graph TD) or splitting the diagram reads better.")
        width = min(natural, MAX_IMAGE_WIDTH)
        return (f'<p><ac:image ac:align="center" ac:width="{width}"><ri:attachment ri:filename="{name}"/>'
                '</ac:image></p><ac:structured-macro ac:name="expand" ac:schema-version="1">'
                '<ac:parameter ac:name="title">Diagram source (Mermaid)</ac:parameter><ac:rich-text-body>'
                + code_macro("text", body) + "</ac:rich-text-body></ac:structured-macro>")

    pattern = r'<pre><code(?: class="language-([\w+-]+)")?>(.*?)</code></pre>'
    return re.sub(pattern, repl, xhtml, flags=re.S), attachments


def verify(xhtml, own_path):
    """Fail on anything that only makes sense on the author's machine or doesn't render."""
    outside_cdata = re.sub(r"<!\[CDATA\[.*?\]\]>", "", xhtml, flags=re.S)
    problems = [f"local doc name visible: {m.group(1)}"
                for m in re.finditer(r"\b([\w./-]+\.md)\b", outside_cdata)
                if (own_path.parent / m.group(1)).exists()]
    for pattern, why in [(r"<a [^>]*>[^<]*\.md\b", "link text is a .md file name"),
                         (r'href="(?!https?://|#|mailto:)[^"]*"', "relative/local href"),
                         (r'ac:name="language">mermaid<', "Mermaid left as a code block"),
                         (r"[A-Za-z]:\\\\|file://", "local filesystem path"),
                         (r"&(?!amp;|lt;|gt;|quot;|#\d+;|#x[0-9a-fA-F]+;)\w+;", "non-XML entity"),
                         (r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "control character")]:
        for m in re.finditer(pattern, outside_cdata):
            problems.append(f"{why}: ...{outside_cdata[max(0, m.start() - 60):m.end() + 20]}...")
    if problems:
        raise SystemExit(f"{own_path.name}: not publishable:\n  " + "\n  ".join(problems[:20]))


def build(entry, resolver, out_root, mmdc, config):
    import markdown
    src = Path(entry["source"]).resolve()
    text = re.sub(r"\A#\s+.+\n+", "", resolver._read(src))  # Confluence shows the page title instead
    xhtml = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"], output_format="xhtml")
    xhtml = fix_links(xhtml, src, resolver)
    out_dir = out_root / src.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    xhtml, attachments = convert_code_blocks(xhtml, src.stem, out_dir, mmdc, config)
    xhtml = fix_bare_doc_names(xhtml, src, resolver)
    verify(xhtml, src)
    bundle = {"id": entry["pageId"], "title": entry["title"], "source": src.name, "body": xhtml,
              "attachments": attachments}
    (out_dir / "body.xhtml").write_text(xhtml, encoding="utf-8")
    (out_dir / "bundle.json").write_text(json.dumps(bundle), encoding="utf-8")
    print(f"{src.name:30} -> {entry['pageId']} {entry['title']!r}: {len(xhtml)} chars, "
          f"{len(attachments)} diagrams -> {out_dir / 'bundle.json'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", required=True, help="JSON list of {source, pageId, title}")
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", help="build just this source file name")
    args = ap.parse_args()
    entries = json.loads(Path(args.map).read_text(encoding="utf-8"))
    configure()
    mmdc, config = ensure_tools()
    resolver = LinkResolver(entries, {})
    for entry in entries:
        if not args.only or Path(entry["source"]).name == args.only:
            build(entry, resolver, Path(args.out), mmdc, config)


if __name__ == "__main__":
    main()
