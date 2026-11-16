#!/usr/bin/env python3
"""Turn an /illustrate HTML page into a Confluence publish bundle.

Native ADF for everything static; one "HTML File (Attachment)" macro per interactive widget; static
SVG figures and annotated screenshots rendered to PNG with headless Chrome; kept images reused.

  python to_adf.py page.html --out bundle.json (--page-id ID | --parent-id ID --space-id ID [--title T])
                   [--existing DIR] [--label L ...] [--no-render]

Prints a summary and writes bundle.json (with the browser publisher inside) plus bundle.summary.json.
"""
import argparse
import base64
import json
import re
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import dom  # noqa: E402
import adf  # noqa: E402
import widgets  # noqa: E402
import render  # noqa: E402

CONTROL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')


def heading_anchors(root):
    anchors = {}
    for n in root.iter():
        if not n.get('id'):
            continue
        h = n if n.tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6') else dom.find(n, lambda x: x.tag in ('h2', 'h3', 'h4'))
        if h is not None:
            anchors[n.get('id')] = adf.anchor_of(h.text_content())
    return anchors


class Images:
    """Collects image jobs while the page is converted; returns mediaSingle placeholders."""

    def __init__(self, page_dir, kept, interactive):
        self.page_dir, self.kept, self.interactive = page_dir, kept, interactive
        self.jobs, self.raw, self.reused, self.warnings = [], [], [], []

    def __call__(self, n):
        if n.tag is None or n in self.interactive:
            return None
        if n.tag == 'img':
            return self.img(n)
        if n.tag == 'svg' or n.has_class('svgbox', 'shotwrap', 'shotbox'):
            return self.render_job(n)
        return None

    def name(self, n, prefix):
        label = n.get('aria-label') or n.get('alt') or ''
        if not label:
            inner = dom.find(n, lambda x: x.tag in ('svg', 'img') and (x.get('aria-label') or x.get('alt')))
            label = (inner.get('aria-label') or inner.get('alt')) if inner else ''
        slug = re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')[:40] or 'figure'
        return f'{prefix}-{len(self.jobs) + len(self.raw) + len(self.reused) + 1:02d}-{slug}'

    def render_job(self, n):
        svg = n if n.tag == 'svg' else dom.find(n, lambda x: x.tag == 'svg')
        shot = n if n.has_class('shotbox') else dom.find(n, lambda x: x.has_class('shotbox'))
        if shot is not None:
            width = min(int(shot.get('data-w') or 1100), 1400)  # real pixels: never enlarged, or they blur
        elif svg is not None:
            width = drawing_width(svg)
        else:
            return None
        job = {'name': self.name(n, 'fig'), 'html': n.outer_html(), 'width': max(320, width),
               'scale': 1 if shot is not None else 2}  # screenshots are already real pixels; drawings get 2x
        self.jobs.append(job)
        return [placeholder(job['name'], job['width'], 0)]

    def img(self, n):
        key = n.get('data-keep')
        if key and key in self.kept and self.kept[key].get('source') == 'attachment':
            k = self.kept[key]
            self.reused.append(key)
            w, h = kept_display_size(k, self.page_dir)
            return [media(k['fileId'], k.get('collection', ''), w, h, n.get('alt'))]
        data, mime = self.bytes_of(n.get('src') or '')
        if data is None:
            self.warnings.append(f'image skipped, source not found: {(n.get("src") or "")[:80]}')
            return []
        name = self.name(n, 'img') + ('.' + mime.split('/')[-1].replace('jpeg', 'jpg'))
        self.raw.append({'name': name, 'placeholder': name, 'mediaType': mime, 'b64': base64.b64encode(data).decode(), 'keep': key})
        w, h = int(n.get('width') or 0), int(n.get('height') or 0)
        return [placeholder(name, w or 800, h)]

    def bytes_of(self, src):
        m = re.match(r'data:([\w/+.-]+);base64,(.*)', src, re.S)
        if m:
            return base64.b64decode(m.group(2)), m.group(1)
        p = (self.page_dir / src) if src and not re.match(r'\w+://', src) else None
        if p and p.is_file():
            ext = p.suffix.lower().lstrip('.')
            return p.read_bytes(), {'jpg': 'image/jpeg', 'svg': 'image/svg+xml'}.get(ext, f'image/{ext}')
        return None, None


def kept_not_placed(root, kept):
    """Kept images the new page never shows: no data-keep=KEY and no <img> pointing at the kept file."""
    shown = set()
    for n in root.iter():
        if n.get('data-keep'):
            shown.add(n.get('data-keep'))
        src = (n.get('src') or '').replace('\\', '/')
        shown |= {k for k, v in kept.items() if v.get('file') and src.endswith(v['file'])}
    return sorted(set(kept) - shown)


FIG_MAX_W, FIG_MAX_H, FIG_MAX_SCALE = 1100, 650, 1.6


def drawing_width(svg):
    """Display width for a drawing: as wide as the page allows (the old HTML pages capped figures at 1100 px),
    but a tall drawing stops at about 650 px high and a small one is enlarged at most 1.6x, so its text stays a sane size."""
    vb = [float(v) for v in re.findall(r'[\d.]+', svg.get('viewbox') or '')]
    vw, vh = (vb[2], vb[3]) if len(vb) == 4 and vb[3] > 0 else (760.0, 300.0)
    return int(min(FIG_MAX_W, FIG_MAX_H * vw / vh, vw * FIG_MAX_SCALE))


def png_size(path):
    data = path.read_bytes()[:24] if path.is_file() else b''
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        return None
    return int.from_bytes(data[16:20], 'big'), int.from_bytes(data[20:24], 'big')


def kept_display_size(k, page_dir):
    """A kept PNG with spare pixels (an earlier 2x render) grows like a new drawing; anything else keeps its size."""
    w, h = k.get('width'), k.get('height')
    px = png_size(Path(page_dir, 'existing', k['file'])) if k.get('file') else None
    if not (w and px and px[0] >= 1.4 * w):
        return w, h
    new_w = int(min(FIG_MAX_W, px[0] / 1.4, FIG_MAX_H * px[0] / px[1]))
    return new_w, int(new_w * px[1] / px[0])


def placeholder(name, width, height):
    return media(f'@@IMG:{name}@@', '', width, height, None)


def media(file_id, collection, width, height, alt):
    attrs = {'type': 'file', 'id': file_id, 'collection': collection}
    if width:
        attrs['width'] = int(width)
    if height:
        attrs['height'] = int(height)
    if alt:
        attrs['alt'] = alt[:200]
    single = {'layout': 'center'}
    if width:  # pixel width: Confluence shows the image at this size and shrinks it on narrower screens
        single.update(width=int(width), widthType='pixel')
    return {'type': 'mediaSingle', 'attrs': single, 'content': [{'type': 'media', 'attrs': attrs}]}


def sanitize(x):
    if isinstance(x, str):
        return CONTROL.sub('', x)
    if isinstance(x, list):
        return [sanitize(v) for v in x]
    if isinstance(x, dict):
        return {k: sanitize(v) for k, v in x.items()}
    return x


def fill_sizes(doc, rendered):
    sizes = {r['placeholder']: r for r in rendered}

    def walk(x):
        if x.get('type') == 'mediaSingle':
            m = x['content'][0]['attrs']
            r = sizes.get(m['id'][6:-2]) if m['id'].startswith('@@IMG:') else None
            if r:
                m.update(width=r['width'], height=r['height'])
                x['attrs'].update(width=r['width'], widthType='pixel')
        for c in x.get('content', []):
            walk(c)
    walk(doc)


def title_emoji(title):
    """The emoji leading the <h1>, as Confluence stores a page emoji: hex codepoints joined by "-", variation selector FE0F dropped."""
    lead = re.match(r'^([^\w\s(\[]+)', title.strip())
    if not lead:
        return None
    points = [f'{ord(ch):x}' for ch in lead.group(1) if ord(ch) > 0x2000 and ord(ch) != 0xfe0f]
    return '-'.join(points) or None


def load_scheme(name):
    schemes = json.loads((HERE.parent / 'assets' / 'schemes.json').read_text(encoding='utf-8'))
    if name not in schemes:
        raise SystemExit(f'unknown scheme {name!r}; known: {", ".join(k for k in schemes if not k.startswith("_"))}')
    return schemes[name]


def scheme_css(scheme):
    def block(tokens):
        return ';'.join(f'{k}:{v}' for k, v in tokens.items())
    light, dark = scheme.get('tokens_light') or {}, scheme.get('tokens_dark') or {}
    if not light:
        return ''
    lines = [f':root{{{block(light)}}}']
    if dark:
        lines += [f'@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{{block(dark)}}}}}',
                  f':root[data-theme="dark"]{{{block(dark)}}}']
    return '\n' + '\n'.join(lines) + '\n'


def build(args):
    path = Path(args.page)
    root = dom.parse(path.read_text(encoding='utf-8'))
    page = widgets.Page(root, path.parent)
    scheme = load_scheme(args.scheme)
    page.head_css += scheme_css(scheme)  # figures and widgets both take their colours from the page CSS
    kept = json.loads(Path(args.existing, 'images.json').read_text(encoding='utf-8')) if args.existing else {}
    images = Images(path.parent, kept, page.interactive)
    conv = adf.Converter(page.widget_for, images, heading_anchors(root), scheme.get('native'))
    page.converter = conv
    content = [b for b in conv.children(page.body) if b['type'] != 'paragraph' or b['content']]
    if args.toc_level:
        content = [adf.toc(args.toc_level)] + content
    doc = sanitize({'type': 'doc', 'version': 1, 'content': content})
    rendered = [] if args.no_render else render.render_all(images.jobs, page, path.parent)
    fill_sizes(doc, rendered)
    checks = [] if args.no_render else render.check_widgets(page.built)
    return root, page, images, conv, doc, rendered, checks, kept


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser()
    ap.add_argument('page')
    ap.add_argument('--out', required=True)
    ap.add_argument('--page-id')
    ap.add_argument('--parent-id')
    ap.add_argument('--space-id')
    ap.add_argument('--title')
    ap.add_argument('--existing')
    ap.add_argument('--label', action='append', default=[])
    ap.add_argument('--no-render', action='store_true', help='skip PNG rendering and widget checks (dry run)')
    ap.add_argument('--scheme', default='bluescale', help='colour scheme from assets/schemes.json')
    ap.add_argument('--toc-level', type=int, default=2, help='heading depth of the table of contents at the top; 0 for none')
    args = ap.parse_args()
    root, page, images, conv, doc, rendered, checks, kept = build(args)
    missing = kept_not_placed(root, kept)
    warnings = conv.warnings + page.warnings + images.warnings + [f'widget check: {c}' for c in checks if c]
    target = {'pageId': args.page_id, 'parentId': args.parent_id, 'spaceId': args.space_id,
              'title': args.title or re.sub(r'^[^\w(\[]+', '', conv.title or '').strip(), 'labels': args.label,
              'emoji': title_emoji(conv.title or '')}
    if not target['emoji']:
        conv.warnings.append('no emoji at the start of the <h1>: the page gets no title emoji')
    bundle = {'target': target, 'adf': doc, 'images': rendered + images.raw,
              'widgets': [w['name'] for w in page.built], 'publisher': (HERE / 'publish.js').read_text(encoding='utf-8')}
    out = Path(args.out)
    out.write_text(json.dumps(bundle, ensure_ascii=False), encoding='utf-8')
    summary = summarize(doc, bundle, images, missing, warnings, out)
    out.with_suffix('.summary.json').write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(summary, indent=1, ensure_ascii=False))


def summarize(doc, bundle, images, missing, warnings, out):
    counts = {}

    def walk(x):
        counts[x['type']] = counts.get(x['type'], 0) + 1
        for c in x.get('content', []):
            walk(c)
    walk(doc)
    size = out.stat().st_size
    if size > 9.5 * 1024 * 1024:
        warnings.append(f'bundle is {size // 1024} KB: over the 10 MB browser upload limit, shrink screenshots')
    return {'title': bundle['target']['title'], 'bundle_kb': size // 1024, 'widgets': bundle['widgets'],
            'images_rendered': len(images.jobs), 'images_uploaded_raw': len(images.raw), 'images_reused': len(images.reused),
            'kept_images_not_placed': missing, 'node_counts': {k: counts[k] for k in sorted(counts)}, 'warnings': warnings}


if __name__ == '__main__':
    main()
