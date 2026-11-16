#!/usr/bin/env python3
"""Crop, blur and encode screenshots into embeddable HTML, with highlights as a theme-aware SVG layer.

  annotate_shots.py --grid screens/foo.png --out previews/foo-grid.png   # rulers in source pixels, for reading coordinates
  annotate_shots.py shots.json [id ...]                                  # write <out>/<id>.html and <out>/<id>-preview.png

shots.json: {"src_dir": "screens", "out_dir": "shotfrags", "shots": {"<id>": {
  "src": "foo.png", "alt": "...", "crop": [x, y, w, h], "maxw": 1400, "q": 78, "blur": [[x, y, w, h]],
  "marks": [{"box": [x, y, w, h], "n": 1, "at": "r|l|t|b|in", "c": "bad|warn|a|good"}, {"arrow": [x1, y1, x2, y2], "c": "bad"}]}}}
All coordinates are source-image pixels. Paths in the manifest are relative to the manifest.
"""
import argparse
import base64
import html
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

PREVIEW_COLOURS = {'bad': '#c8422f', 'warn': '#c08a10', 'a': '#2f6fd6', 'good': '#1f8a3c'}


def blurred(image, boxes):
    for x, y, w, h in boxes:
        box = (x, y, x + w, y + h)
        small = image.crop(box).resize((max(1, w // 8), max(1, h // 8)), Image.BILINEAR)
        image.paste(small.resize((w, h), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3)), box)
    return image


def prepared_image(shot, src_dir):
    image = Image.open(src_dir / shot['src']).convert('RGB')
    image = blurred(image, shot.get('blur', []))
    cx, cy, cw, ch = shot.get('crop', [0, 0, image.width, image.height])
    image = image.crop((cx, cy, cx + cw, cy + ch))
    maxw = shot.get('maxw', 1400)
    if image.width > maxw:
        image = image.resize((maxw, round(image.height * maxw / image.width)), Image.LANCZOS)
    return image, (cx, cy, image.width / cw)


def badge_centre(mark, x, y, w, h, r, size):
    at = mark.get('at', 'r')
    cx, cy = {'r': (x + w + r + 4, y + h / 2), 'l': (x - r - 4, y + h / 2), 't': (x + r, y - r - 3), 'b': (x + r, y + h + r + 3), 'in': (x + r + 3, y + r + 3)}[at]
    return min(max(cx, r + 1), size[0] - r - 1), min(max(cy, r + 1), size[1] - r - 1)


def scaled_marks(shot, frame, size):
    cx, cy, f = frame
    r = max(10.0, min(15.0, 12 * size[0] / 1000))
    marks = []
    for mark in shot.get('marks', []):
        colour = mark.get('c', 'bad')
        if 'arrow' in mark:
            x1, y1, x2, y2 = mark['arrow']
            marks.append(dict(kind='arrow', c=colour, pts=((x1 - cx) * f, (y1 - cy) * f, (x2 - cx) * f, (y2 - cy) * f)))
            continue
        x, y, w, h = mark['box']
        rect = ((x - cx) * f, (y - cy) * f, w * f, h * f)
        badge = badge_centre(mark, *rect, r, size) if 'n' in mark else None
        marks.append(dict(kind='box', c=colour, rect=rect, n=mark.get('n'), badge=badge))
    return marks, r


def arrow_markers(shot_id, marks):
    colours = sorted({m['c'] for m in marks if m['kind'] == 'arrow'})
    if not colours:
        return ''
    defs = ''.join(f'<marker id="ar-{shot_id}-{c}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
                   f'<path d="M0 0 L10 5 L0 10z" fill="var(--{c})"/></marker>' for c in colours)
    return f'<defs>{defs}</defs>'


def svg_mark(shot_id, mark, r, stroke):
    colour = f"var(--{mark['c']})"
    if mark['kind'] == 'arrow':
        x1, y1, x2, y2 = mark['pts']
        return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{colour}" stroke-width="{stroke * 1.3:.1f}" marker-end="url(#ar-{shot_id}-{mark["c"]})"/>'
    x, y, w, h = mark['rect']
    parts = f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="3" fill="none" stroke="{colour}" stroke-width="{stroke:.1f}"/>'
    if mark['badge']:
        bx, by = mark['badge']
        parts += f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{r:.1f}" fill="{colour}"/>'
        parts += f'<text x="{bx:.1f}" y="{by + r * 0.38:.1f}" text-anchor="middle" class="shotn" style="font-size:{r * 1.15:.1f}px">{mark["n"]}</text>'
    return parts


def fragment(shot_id, shot, image, marks, r):
    W, H = image.size
    buf = io.BytesIO()
    image.save(buf, 'WEBP', quality=shot.get('q', 78), method=6)
    data = base64.b64encode(buf.getvalue()).decode()
    stroke = max(2.0, 2.6 * W / 1000)
    alt = html.escape(shot['alt'], quote=True)
    layer = arrow_markers(shot_id, marks) + ''.join(svg_mark(shot_id, m, r, stroke) for m in marks)
    return (f'<div class="shotwrap"><div class="shotbox" style="width:min(100%,{W}px)" data-w="{W}"><img alt="{alt}" width="{W}" height="{H}" src="data:image/webp;base64,{data}">'
            f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Highlights on: {alt}">{layer}</svg></div></div>'), len(buf.getvalue())


def preview(image, marks, r):
    out = image.copy()
    draw = ImageDraw.Draw(out)
    for mark in marks:
        colour = PREVIEW_COLOURS[mark['c']]
        if mark['kind'] == 'arrow':
            draw.line(mark['pts'], fill=colour, width=3)
            draw.ellipse((mark['pts'][2] - 5, mark['pts'][3] - 5, mark['pts'][2] + 5, mark['pts'][3] + 5), fill=colour)
            continue
        x, y, w, h = mark['rect']
        draw.rectangle((x, y, x + w, y + h), outline=colour, width=3)
        if mark['badge']:
            bx, by = mark['badge']
            draw.ellipse((bx - r, by - r, bx + r, by + r), fill=colour)
            draw.text((bx, by), str(mark['n']), fill='white', anchor='mm')
    return out


def build_all(manifest_path, only):
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    root = manifest_path.parent
    src_dir, out_dir = root / manifest.get('src_dir', 'screens'), root / manifest.get('out_dir', 'shotfrags')
    out_dir.mkdir(parents=True, exist_ok=True)
    unknown = set(only) - set(manifest['shots'])
    if unknown:
        raise SystemExit(f'unknown shot ids: {sorted(unknown)}')
    total = 0
    for shot_id, shot in manifest['shots'].items():
        if only and shot_id not in only:
            continue
        image, frame = prepared_image(shot, src_dir)
        marks, r = scaled_marks(shot, frame, image.size)
        text, size = fragment(shot_id, shot, image, marks, r)
        (out_dir / f'{shot_id}.html').write_text(text, encoding='utf-8', newline='\n')
        preview(image, marks, r).save(out_dir / f'{shot_id}-preview.png')
        total += size
        print(f'{shot_id:16} {image.width:5}x{image.height:<5} {size // 1024:5} KB')
    print(f'total {total // 1024} KB before base64')


def grid(src, out, step=100):
    image = Image.open(src).convert('RGB')
    draw = ImageDraw.Draw(image)
    for x in range(0, image.width, step):
        draw.line((x, 0, x, image.height), fill='#ff00ff' if x % 500 == 0 else '#00d0d0', width=1)
        draw.text((x + 2, 2), str(x), fill='#ff00ff', stroke_width=2, stroke_fill='white')
    for y in range(0, image.height, step):
        draw.line((0, y, image.width, y), fill='#ff00ff' if y % 500 == 0 else '#00d0d0', width=1)
        draw.text((2, y + 2), str(y), fill='#ff00ff', stroke_width=2, stroke_fill='white')
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out)
    print(f'{out} {image.width}x{image.height}')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('manifest', nargs='?', type=Path)
    parser.add_argument('ids', nargs='*')
    parser.add_argument('--grid', type=Path, help='image to overlay rulers on')
    parser.add_argument('--out', type=Path, help='output for --grid')
    args = parser.parse_args()
    if args.grid:
        if not args.out:
            parser.error('--grid needs --out')
        grid(args.grid, args.out)
    elif args.manifest:
        build_all(args.manifest, set(args.ids))
    else:
        parser.error('give a manifest or --grid')


if __name__ == '__main__':
    main()
