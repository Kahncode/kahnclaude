#!/usr/bin/env python3
"""Unpack cug-export-<pageId>.json into files the illustrate agent can read.

  python unpack_export.py cug-export-123.json <workspace>/existing

Writes:
  content.md     the current page as Markdown; images appear as ![KEY](images/KEY.ext), HTML macros as
                 a pointer to macro-N.html
  macro-N.html   each HTML macro's page, with embedded data: images moved to images/ files
  images/        every image the page shows (attachments and images inside HTML macros)
  images.json    manifest the converter reads: key -> source, fileId/collection or file, size, context
  images.md      the same list for people: key, file, where it was, caption
"""
import base64
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import dom  # noqa: E402

GENERATED = re.compile(r'^fig-\d{2}-[\w-]*\.png$')  # names to_adf.py gives rendered figures
EXT = {'image/png': 'png', 'image/jpeg': 'jpg', 'image/webp': 'webp', 'image/gif': 'gif', 'image/svg+xml': 'svg'}


def slug(text, n=32):
    return re.sub(r'[^a-z0-9]+', '-', (text or '').lower()).strip('-')[:n] or 'image'


class Unpacker:
    def __init__(self, export, out):
        self.export, self.out = export, out
        self.images, self.lines, self.heading, self.macros = {}, [], '', 0
        self.attach = {i['fileId']: i for i in export['images']}
        (out / 'images').mkdir(parents=True, exist_ok=True)

    def run(self):
        for block in self.export['adf'].get('content', []):
            self.block(block, '')
        (self.out / 'content.md').write_text('\n'.join(self.lines).strip() + '\n', encoding='utf-8')
        (self.out / 'images.json').write_text(json.dumps(self.images, indent=1, ensure_ascii=False), encoding='utf-8')
        (self.out / 'images.md').write_text(self.image_list(), encoding='utf-8')
        meta = {k: v for k, v in self.export['page'].items()}
        meta['missingImages'] = self.export.get('missingImages', [])
        (self.out / 'page.json').write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding='utf-8')
        return meta

    # ---------- ADF to Markdown ----------
    def text(self, n):
        if n.get('type') == 'text':
            t = n['text']
            for m in n.get('marks', []):
                t = {'strong': f'**{t}**', 'em': f'*{t}*', 'code': f'`{t}`'}.get(m['type'], t)
                if m['type'] == 'link':
                    t = f"[{t}]({m['attrs'].get('href', '')})"
            return t
        if n.get('type') == 'hardBreak':
            return '  \n'
        if n.get('type') == 'status':
            return f"[{n['attrs'].get('text', '')}]"
        return ''.join(self.text(c) for c in n.get('content', []))

    def block(self, n, indent):
        t = n.get('type')
        if t == 'heading':
            self.heading = self.text(n)
            self.lines += ['', '#' * n['attrs']['level'] + ' ' + self.heading, '']
        elif t == 'paragraph':
            self.lines.append(indent + self.text(n))
        elif t in ('bulletList', 'orderedList'):
            for k, item in enumerate(n.get('content', []), 1):
                bullet = f'{k}.' if t == 'orderedList' else '-'
                first, *rest = item.get('content', []) or [{}]
                self.lines.append(f'{indent}{bullet} {self.text(first)}')
                for r in rest:
                    self.block(r, indent + '   ')
        elif t == 'codeBlock':
            self.lines += [indent + '```' + (n.get('attrs', {}).get('language') or ''), self.text(n), indent + '```']
        elif t == 'mediaSingle' or t == 'mediaGroup':
            for m in n.get('content', []):
                if m['type'] == 'media':
                    self.media(m, n, indent)
        elif t == 'extension' or t == 'bodiedExtension':
            self.extension(n)
        elif t == 'table':
            self.table(n)
        elif t in ('panel', 'expand', 'nestedExpand', 'blockquote', 'layoutSection', 'layoutColumn'):
            title = n.get('attrs', {}).get('title') or n.get('attrs', {}).get('panelType') or ''
            if title:
                self.lines.append(f'{indent}> **{title}**')
            for c in n.get('content', []):
                self.block(c, indent + '> ' if t != 'layoutSection' else indent)
        elif t == 'rule':
            self.lines.append('---')
        else:
            for c in n.get('content', []):
                self.block(c, indent)

    def table(self, n):
        for k, row in enumerate(n.get('content', [])):
            cells = [self.text(c).replace('\n', ' ') for c in row.get('content', [])]
            self.lines.append('| ' + ' | '.join(cells) + ' |')
            if k == 0:
                self.lines.append('|' + ' --- |' * len(cells))

    # ---------- images ----------
    def media(self, m, parent, indent):
        a = m['attrs']
        att = self.attach.get(a.get('id'))
        caption = next((self.text(c) for c in parent.get('content', []) if c['type'] == 'caption'), '')
        if att and GENERATED.match(att['title']):
            # A figure this skill rendered from SVG last time: the new page redraws it, so it is not a kept image.
            self.lines.append(f"{indent}[generated figure {att['title']}{': ' + caption if caption else ''}]")
            return
        key = f"att-{len(self.images) + 1:02d}-{slug(a.get('alt') or (att or {}).get('title') or caption)}"
        entry = {'source': 'attachment', 'fileId': a.get('id'), 'collection': a.get('collection', ''),
                 'width': a.get('width'), 'height': a.get('height'), 'section': self.heading, 'caption': caption, 'alt': a.get('alt', '')}
        if att:
            ext = EXT.get(att['mediaType'], 'bin')
            (self.out / 'images' / f'{key}.{ext}').write_bytes(base64.b64decode(att['b64']))
            entry['file'] = f'images/{key}.{ext}'
            entry['title'] = att['title']
        self.images[key] = entry
        self.lines.append(f"{indent}![{key}]({entry.get('file', 'not-downloaded')})" + (f' *{caption}*' if caption else ''))

    def extension(self, n):
        html = n.get('attrs', {}).get('parameters', {}).get('guestParams', {}).get('htmlContent')
        if not html:
            self.lines.append(f"[macro: {n.get('attrs', {}).get('extensionKey', '?')} — not exported]")
            return
        self.macros += 1
        name = f'macro-{self.macros}.html'
        html = self.macro_images(html)
        (self.out / name).write_text(html, encoding='utf-8')
        self.lines += ['', f'[HTML macro {self.macros}: see {name} — the previous illustrated page or widget]', '']

    def macro_images(self, html):
        """Move data: images out of the macro HTML into files, noting the heading/caption around each."""
        root = dom.parse(html)
        context = {}
        heading = ''
        for node in root.iter():
            if node.tag in ('h1', 'h2', 'h3'):
                heading = re.sub(r'\s+', ' ', node.text_content()).strip()
            if node.tag == 'img' and (node.get('src') or '').startswith('data:'):
                fig = node.parent
                while fig is not None and fig.tag != 'figure':
                    fig = fig.parent
                cap = dom.find(fig, lambda x: x.tag == 'figcaption') if fig is not None else None
                context[node.get('src')] = (heading, re.sub(r'\s+', ' ', cap.text_content()).strip() if cap else '', node.get('alt') or '')

        def swap(m):
            mime, data = m.group(1), m.group(2)
            heading_, caption, alt = context.get(m.group(0), ('', '', ''))
            key = f'mac{self.macros}-{len(self.images) + 1:02d}-{slug(alt or caption or heading_)}'
            ext = EXT.get(mime, 'bin')
            (self.out / 'images' / f'{key}.{ext}').write_bytes(base64.b64decode(data))
            self.images[key] = {'source': 'macro', 'file': f'images/{key}.{ext}', 'section': heading_, 'caption': caption, 'alt': alt}
            return f'existing/images/{key}.{ext}'
        return re.sub(r'data:(image/[\w+.-]+);base64,([A-Za-z0-9+/=]+)', swap, html)

    def image_list(self):
        rows = ['# Images on the current page (keep every one)', '',
                '| key | file | section | caption / alt |', '| --- | --- | --- | --- |']
        for k, v in self.images.items():
            rows.append(f"| {k} | existing/{v.get('file', '-')} | {v.get('section', '')} | {v.get('caption') or v.get('alt') or ''} |")
        return '\n'.join(rows) + '\n'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    export = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    out = Path(sys.argv[2])
    meta = Unpacker(export, out).run()
    imgs = json.loads((out / 'images.json').read_text(encoding='utf-8'))
    print(json.dumps({'title': meta['title'], 'version': meta['version'], 'images': len(imgs),
                      'attachments': sum(1 for v in imgs.values() if v['source'] == 'attachment'),
                      'macro_images': sum(1 for v in imgs.values() if v['source'] == 'macro'),
                      'missing': meta['missingImages'], 'out': str(out)}, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
