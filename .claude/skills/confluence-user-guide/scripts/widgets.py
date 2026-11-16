"""Find the interactive parts of an /illustrate page and package each as a self-contained HTML macro.

A widget is either an element marked data-widget="Name" (the contract the illustrate agent follows)
or, for unmarked pages, the smallest run of siblings holding buttons/inputs/canvas or elements the
page script reaches by id. Siblings driven by the same script statements become one widget.
Each widget gets the page CSS, the shared helper statements, only the statements that touch it,
and hidden copies of any other element those statements still look up, so nothing throws.
"""
import base64
import re
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

import dom
from jsunits import split_units, referenced_ids, with_dependencies

sys.path.insert(0, str(Path.home() / '.claude' / 'scripts' / 'lib'))
from project_vars import get  # noqa: E402

INTERACTIVE_TAGS = {'button', 'input', 'select', 'textarea', 'canvas'}
NATIVE_CONTAINERS = {'details', 'ul', 'ol', 'table', 'pre', 'blockquote'}
PANEL_CLASSES = {'goals', 'start', 'verify', 'analogy', 'predict', 'myth', 'note', 'recap', 'card'}
HEADINGS = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
WIDGET_CSS = ('html,body{margin:0;background:var(--panel)}'
              '.wrap{max-width:none;margin:0;padding:4px 2px 10px;display:grid;gap:12px}'
              'svg{max-width:1100px;margin-inline:auto}')


class Page:
    def __init__(self, root, page_dir=None):
        self.root, self.page_dir = root, page_dir
        self.body = dom.find(root, lambda n: n.has_class('wrap')) or dom.find(root, lambda n: n.tag == 'body') or root
        self.head_css = '\n'.join(s.text_content() or ''.join(c.text or '' for c in s.children)
                                  for s in dom.find_all(root, lambda n: n.tag == 'style'))
        self.head_links = [n.raw for n in dom.find_all(root, lambda n: n.tag == 'link' and n.get('rel') == 'stylesheet')]
        self.script_srcs = [n.raw + '</script>' for n in dom.find_all(root, lambda n: n.tag == 'script' and n.get('src'))]
        self.ids = {n.get('id'): n for n in root.iter() if n.get('id')}
        self.warnings, self.built, self.converter = [], [], None
        self.units = self._units()
        self.comp = self._components()
        self.interactive = self._mark_interactive()
        self.explicit = any(n.get('data-widget') is not None and n.tag != 'script' for n in root.iter())

    # ---------- script analysis ----------
    def _units(self):
        units = []
        for s in dom.find_all(self.root, lambda n: n.tag == 'script' and not n.get('src')):
            code = ''.join(c.text or '' for c in s.children)
            owner = s.get('data-widget')
            parts = [code] if owner else split_units(code)
            units += [{'code': p, 'owner': owner, 'refs': referenced_ids(p, self.ids)} for p in parts]
        return units

    def _components(self):
        parent = {i: i for i in self.ids}

        def top(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i
        for u in self.units:
            refs = sorted(u['refs'])
            for r in refs[1:]:
                parent[top(r)] = top(refs[0])
        return {i: top(i) for i in self.ids}

    def _mark_interactive(self):
        referenced = set().union(*[u['refs'] for u in self.units]) if self.units else set()
        hot = set()

        def visit(n):
            own = n.tag in INTERACTIVE_TAGS or n.get('id') in referenced or (n.get('data-widget') is not None and n.tag != 'script')
            child = False
            for c in n.children:
                if c.tag and visit(c):
                    child = True
            if own or child:
                hot.add(n)
            return own or child
        visit(self.root)
        return hot

    # ---------- grouping ----------
    def directly_interactive(self, n):
        return n.tag in INTERACTIVE_TAGS or (n.get('id') and any(n.get('id') in u['refs'] for u in self.units))

    def candidate(self, n):
        if n.tag is None or n not in self.interactive or n.tag == 'script':
            return False
        if self.explicit and dom.find(n, lambda x: x.get('data-widget') is not None and x.tag != 'script') not in (None, n):
            return False
        if n.get('data-widget') is not None:
            return True
        if dom.find(n, lambda x: x.tag in HEADINGS) is not None:
            return False
        if (n.tag in NATIVE_CONTAINERS or n.has_class(*PANEL_CLASSES)) and not self.directly_interactive(n):
            return False
        return True

    def comps_of(self, n):
        return {self.comp[x.get('id')] for x in n.iter() if x.get('id') in self.comp and self.comp[x.get('id')] in self._used}

    @property
    def _used(self):
        if not hasattr(self, '_used_cache'):
            self._used_cache = {self.comp[r] for u in self.units for r in u['refs']}
        return self._used_cache

    def widget_for(self, kids, i):
        n = kids[i]
        if not self.candidate(n):
            return None, 0
        last, comps = i, self.comps_of(n)
        if n.get('data-widget') is None and comps:
            for j in range(i + 1, len(kids)):
                k = kids[j]
                if k.tag in HEADINGS or (k.tag and dom.find(k, lambda x: x.tag in HEADINGS) is not None):
                    break
                if k.tag and k.get('data-widget') is None and self.comps_of(k) & comps:
                    last, comps = j, comps | self.comps_of(k)
        group = [k for k in kids[i:last + 1] if k.tag != 'script']
        return self.build(group), last - i + 1

    # ---------- building ----------
    def build(self, group):
        name = self.name_of(group)
        caption = None
        if len(group) == 1 and group[0].tag == 'figure':
            caption = next((c for c in group[0].children if c.tag == 'figcaption'), None)
        body = ''.join(g.outer_html(skip={caption} if caption else None) for g in group)
        inside = {x.get('id') for g in group for x in g.iter() if x.get('id')}
        script, stubs = self.script_for(name, inside)
        doc = self.document(name, body, stubs, script)
        self.built.append({'name': name, 'doc': doc})
        out = [extension(name, doc)]
        if caption is not None and self.converter:
            p = self.converter.paragraph([caption], ({'type': 'em'},))
            if p['content']:
                out.append(p)
        return out

    def name_of(self, group):
        g = group[0]
        explicit = g.get('data-widget')
        if explicit:
            return explicit.strip()[:60]
        section = self.converter.last_heading if self.converter else ''
        label = next((x.get('aria-label') for x in g.iter() if x.get('aria-label')), None)
        text = re.sub(r'\s+', ' ', section or label or 'interactive').strip()
        return f'{text[:50]} · widget {len(self.built) + 1}'

    def script_for(self, name, inside):
        comps = {self.comp[i] for i in inside if i in self.comp}
        chosen = [k for k, u in enumerate(self.units) if u['owner'] == name
                  or (u['owner'] is None and (not u['refs'] or {self.comp[r] for r in u['refs']} & comps))]
        mine = [self.units[k] for k in with_dependencies(chosen, self.units)]
        code = '\n'.join(u['code'].strip('\n') for u in mine)
        if not syntax_ok(code):
            self.warnings.append(f'{name}: split script failed a syntax check, using the whole page script')
            mine = self.units
            code = '\n'.join(u['code'].strip('\n') for u in mine)
        wanted = set().union(*[u['refs'] for u in mine]) if mine else set()
        stubs = ''.join(hidden_copy(self.ids[i]) for i in sorted(wanted - inside) if not self.inside_any(i, inside))
        return code, stubs

    def inside_any(self, i, inside):
        return i in inside

    def document(self, name, body, stubs, script):
        links = ''.join(self.head_links)
        srcs = ''.join(self.script_srcs)
        stub_html = f'<div hidden aria-hidden="true">{stubs}</div>' if stubs else ''
        body = inline_local_images(body, self.page_dir)
        body = re.sub(r'<a\b(?![^>]*\btarget=)([^>]*\bhref="(?!#)[^"]+"[^>]*)>', r'<a\1 target="_blank" rel="noopener">', body)
        return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                f'<title>{name}</title>{links}<style>\n{self.head_css}\n{WIDGET_CSS}\n</style>{srcs}</head>'
                f'<body><div class="wrap">\n{body}\n{stub_html}</div>\n<script>\n{script}\n</script></body></html>')


def inline_local_images(html, page_dir):
    """Confluence can't see local files, so a widget's relative <img src> becomes a data: URI."""
    if page_dir is None:
        return html

    def swap(m):
        src = m.group(2)
        p = Path(page_dir, src)
        if re.match(r'\w+:', src) or not p.is_file():
            return m.group(0)
        ext = p.suffix.lower().lstrip('.')
        mime = {'jpg': 'image/jpeg', 'svg': 'image/svg+xml'}.get(ext, f'image/{ext}')
        return f'{m.group(1)}data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"'
    return re.sub(r'(<img\b[^>]*?\ssrc=")([^"]+)"', swap, html)


def hidden_copy(node):
    html = node.outer_html()
    return re.sub(r'(<img\b[^>]*?)\ssrc="[^"]*"', r'\1', html)


def syntax_ok(code):
    if not code.strip():
        return True
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(code)
        path = f.name
    try:
        return subprocess.run(['node', '--check', path], capture_output=True, text=True, timeout=30).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return True  # no node: the headless widget check still catches it
    finally:
        Path(path).unlink(missing_ok=True)


def search_text(doc):
    t = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', doc, flags=re.S)
    t = re.sub(r'<svg.*?</svg>', ' ', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = t.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&quot;', '"')
    return re.sub(r'\s+', ' ', t).strip()[:9990]


def extension(name, doc):
    text = search_text(doc)
    file_name = re.sub(r'[^\w .·-]+', '', name).strip() or 'widget'
    ext_key = get('CONFLUENCE_HTML_MACRO_EXT_KEY')
    return {'type': 'extension', 'attrs': {
        'layout': 'default', 'extensionType': 'com.atlassian.ecosystem', 'extensionKey': ext_key, 'text': 'HTML File (Attachment)',
        'macroMetadata': {'indexedMacroParams': {'text': text, 'type': 'text'}},
        'parameters': {'layout': 'extension',
                       'guestParams': {'searchText': text, 'htmlAttachment': f'{file_name}.html', 'htmlContent': doc},
                       'extensionId': 'ari:cloud:ecosystem::extension/' + ext_key, 'extensionTitle': 'HTML File (Attachment)',
                       'forgeEnvironment': 'PRODUCTION'},
        'localId': str(uuid.uuid4())}}
