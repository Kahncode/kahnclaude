"""Headless Chrome helpers: static figures to PNG (light theme, 2x), and a smoke check of each widget."""
import base64
import html as H
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

CANDIDATES = [os.environ.get('CHROME', ''), r'C:\Program Files\Google\Chrome\Application\chrome.exe',
              r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
              r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', 'google-chrome', 'chromium']
PAD = 8
ERR_HOOK = ('<script>(()=>{const d=document.documentElement,a=m=>d.setAttribute("data-cug-err",(d.getAttribute("data-cug-err")||"")+m+" | ");'
            'addEventListener("error",e=>a(e.message||"resource failed: "+(e.target&&(e.target.src||e.target.href))),true);'
            'addEventListener("unhandledrejection",e=>a(String(e.reason)));})()</script>')


def chrome():
    for c in CANDIDATES:
        if c and (Path(c).is_file() or shutil.which(c)):
            return c
    raise SystemExit('No Chrome/Edge found for rendering; set CHROME or pass --no-render for a dry run')


def run(args, timeout=90):
    with tempfile.TemporaryDirectory() as prof:
        cmd = [chrome(), '--headless=new', '--disable-gpu', '--no-first-run', '--hide-scrollbars',
               f'--user-data-dir={prof}'] + args
        return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)


def page_html(page, body, extra='', base=None):
    links = ''.join(page.head_links)
    base_tag = f'<base href="{Path(base).resolve().as_uri()}/">' if base else ''  # relative <img src> resolve beside the page
    return ('<!doctype html><html lang="en" data-theme="light"><head><meta charset="utf-8">'
            f'{base_tag}{links}<style>\n{page.head_css}\n'
            f'html,body{{margin:0;background:var(--panel,#fff)}} .cug{{padding:{PAD}px;box-sizing:content-box}}'
            '.cug svg{min-width:0;max-width:none;width:100%;height:auto}.cug .shotbox{max-width:none!important}'
            f'</style>{extra}</head><body>{body}</body></html>')


def render_all(jobs, page, page_dir):
    if not jobs:
        return []
    work = Path(tempfile.mkdtemp(prefix='cug-render-', dir=page_dir))
    blocks = ''.join(f'<div class="cug" id="j{k}" style="width:{j["width"]}px">{j["html"]}</div>' for k, j in enumerate(jobs))
    measure = ('<script>document.fonts.ready.then(()=>setTimeout(()=>{document.querySelectorAll(".cug").forEach(d=>'
               'd.setAttribute("data-h",Math.ceil(d.getBoundingClientRect().height)));'
               'document.documentElement.setAttribute("data-done","1")},300))</script>')
    (work / 'measure.html').write_text(page_html(page, blocks + measure, base=page_dir), encoding='utf-8')
    dumped = run(['--virtual-time-budget=8000', '--dump-dom', (work / 'measure.html').as_uri()]).stdout
    heights = {int(a): int(b) for a, b in re.findall(r'id="j(\d+)"[^>]*data-h="(\d+)"', dumped)}
    out = []
    for k, j in enumerate(jobs):
        h = heights.get(k) or int(j['width'] * 0.5)
        f = work / f'{k}.html'
        f.write_text(page_html(page, f'<div class="cug" style="width:{j["width"]}px">{j["html"]}</div>', base=page_dir), encoding='utf-8')
        png = work / f'{k}.png'
        run([f'--force-device-scale-factor={j.get("scale", 2)}', f'--window-size={j["width"] + 2 * PAD},{h}',
             '--virtual-time-budget=5000', f'--screenshot={png}', f.as_uri()])
        if not png.is_file():
            raise SystemExit(f'render failed for {j["name"]}')
        out.append({'name': j['name'] + '.png', 'mediaType': 'image/png', 'b64': base64.b64encode(png.read_bytes()).decode(),
                    'width': j['width'] + 2 * PAD, 'height': h})
    shutil.rmtree(work, ignore_errors=True)
    for o in out:  # placeholders were named without the extension
        o['placeholder'] = o['name'][:-4]
    return out


def check_widgets(built):
    """Load every widget headless; report script errors and widgets that rendered nothing."""
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        for w in built:
            doc = w['doc'].replace('<head>', '<head>' + ERR_HOOK, 1)
            f = Path(tmp, 'w.html')
            f.write_text(doc, encoding='utf-8')
            dumped = run(['--virtual-time-budget=4000', '--dump-dom', f.as_uri()]).stdout
            m = re.search(r'data-cug-err="([^"]*)"', dumped)
            if m:
                problems.append(f'{w["name"]}: {H.unescape(m.group(1))[:300]}')
    return problems
