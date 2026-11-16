"""Native ADF for the static parts of an /illustrate page.

Widgets and images are not built here: the converter passes `widget_for(node)` and `image_for(node)`
callbacks, so this module only knows how each page component maps to Confluence's own blocks.
"""
import re
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path.home() / '.claude' / 'scripts' / 'lib'))
from project_vars import get  # noqa: E402

PANEL_CLASSES = {'goals': 'info', 'start': 'info', 'verify': 'info', 'analogy': 'note', 'predict': 'note',
                 'myth': 'error', 'note': 'warning', 'recap': 'success', 'warn': 'warning'}
TAG_COLOURS = {'bad': 'red', 'real': 'red', 'good': 'green', 'dir': 'blue', 'inj': 'purple', 'open': 'neutral', 'warn': 'yellow'}
INLINE = {'a', 'b', 'strong', 'i', 'em', 'code', 'span', 'br', 'small', 'sub', 'sup', 'kbd', 'mark', 'u', 's', 'del',
          'abbr', 'label', 'q', 'cite', 'var', 'samp', 'time', 'button'}
SKIP = {'script', 'style', 'nav', 'noscript', 'template', 'meta', 'link', 'title', 'head'}
ALLOWED = {
    'panel': {'paragraph', 'heading', 'bulletList', 'orderedList', 'codeBlock', 'mediaSingle', 'rule'},
    'expand': {'paragraph', 'heading', 'bulletList', 'orderedList', 'codeBlock', 'mediaSingle', 'rule', 'panel',
               'blockquote', 'table'},
    'blockquote': {'paragraph', 'bulletList', 'orderedList', 'codeBlock', 'mediaSingle'},
    'listItem': {'paragraph', 'bulletList', 'orderedList', 'codeBlock', 'mediaSingle'},
    'tableCell': {'paragraph', 'heading', 'bulletList', 'orderedList', 'codeBlock', 'panel', 'mediaSingle', 'blockquote', 'rule'},
}
CODE_MARK_OK = {'code', 'link'}


def anchor_of(text):
    """Confluence Cloud heading anchor: the heading text with whitespace runs turned into '-'."""
    return re.sub(r'\s+', '-', text.strip())


class Converter:
    def __init__(self, widget_for, image_for, anchors, native=None):
        self.widget_for, self.image_for, self.anchors = widget_for, image_for, anchors
        self.native = native or {}
        self.title, self.warnings, self.last_heading = None, [], ''

    # ---------- inline ----------
    def inlines(self, node, marks=()):
        if node.tag is None:
            return [{'type': 'text', 'text': node.text, 'marks': list(marks)}] if node.text else []
        if node.tag in SKIP or node.tag in ('svg', 'img') or node.has_class('up'):
            return []
        if node.tag == 'br':
            return [{'type': 'hardBreak'}]
        if node.has_class('tag'):
            return [self.status(node)]
        return [x for c in node.children for x in self.inlines(c, self.marks_for(node, marks))]

    def marks_for(self, node, marks):
        add = {'b': 'strong', 'strong': 'strong', 'i': 'em', 'em': 'em', 'cite': 'em', 'u': 'underline', 's': 'strike',
               'del': 'strike', 'code': 'code', 'kbd': 'code', 'samp': 'code', 'var': 'code'}.get(node.tag)
        if node.has_class('ref', 'mono', 'when'):
            add = 'code'
        out = list(marks)
        if add and not any(m['type'] == add for m in out):
            out.append({'type': add})
        if node.tag in ('sub', 'sup'):
            out.append({'type': 'subsup', 'attrs': {'type': node.tag}})
        if node.tag == 'a' and node.get('href'):
            href = self.href(node.get('href'))
            if href:
                out = [m for m in out if m['type'] != 'link'] + [{'type': 'link', 'attrs': {'href': href}}]
        return tuple(out)

    def href(self, href):
        if not href.startswith('#'):
            return href
        anchor = self.anchors.get(href[1:])
        return f'#{anchor}' if anchor else None

    def status(self, node):
        colours = {**TAG_COLOURS, **self.native.get('tag_colors', {})}
        colour = next((colours[c] for c in node.classes if c in colours), 'neutral')
        return {'type': 'status', 'attrs': {'text': node.text_content().strip().upper(), 'color': colour,
                                            'localId': str(uuid.uuid4()), 'style': ''}}

    def paragraph(self, nodes, marks=()):
        content = clean_inline([x for n in nodes for x in self.inlines(n, marks)])
        return {'type': 'paragraph', 'content': content}

    # ---------- blocks ----------
    def children(self, node):
        """Block list for a container: widget runs, inline runs as paragraphs, block children converted."""
        out, run = [], []
        kids = [c for c in node.children if not (c.tag in SKIP)]
        i = 0
        while i < len(kids):
            widget, used = self.widget_for(kids, i)
            if widget:
                out += self.flush(run) + widget
                run, i = [], i + used
                continue
            c = kids[i]
            if is_inline(c):
                run.append(c)
            else:
                out += self.flush(run) + self.block(c)
                run = []
            i += 1
        return out + self.flush(run)

    def flush(self, run):
        if not run:
            return []
        p = self.paragraph(run)
        return [p] if p['content'] else []

    def block(self, n):
        t, cls = n.tag, n.classes
        if t in SKIP or 'up' in cls or 'topnav' in cls or is_concept_index(n):
            return []
        img = self.image_for(n)
        if img is not None:
            return img
        if t == 'h1':
            if self.title is None:
                self.title = n.text_content().strip()
                return []
            return [self.heading(n, 1)]
        if t in ('h2', 'h3', 'h4', 'h5', 'h6'):
            return [self.heading(n, int(t[1]))]
        return self.dispatch(n, t, cls)

    def dispatch(self, n, t, cls):
        if t == 'p' and 'eyebrow' not in cls:
            return self.flush([n]) if all(is_inline(c) for c in n.children) else self.children(n)
        if 'eyebrow' in cls:
            return self.eyebrow(n)
        if t in ('ul', 'ol'):
            return self.listing(n, ordered=(t == 'ol'))
        if t == 'pre':
            return [code_block(n)]
        if 'diff' in cls:
            return self.diff(n)
        if t == 'table':
            return self.table(n)
        if t == 'details':
            return self.expand(n)
        if 'inshort' in cls and 'inshort' in self.native.get('panels', {}):
            return self.wrap('panel', dict(self.native['panels']['inshort']), self.children(n))
        if t == 'blockquote' or 'inshort' in cls:
            return self.wrap('blockquote', {}, self.children(n))
        if t == 'hr':
            return [{'type': 'rule'}]
        if t == 'figure':
            return self.figure(n)
        kind = next((PANEL_CLASSES[c] for c in cls if c in PANEL_CLASSES), None)
        if kind:
            return self.panel(n, kind)
        return self.special(n, cls)

    def special(self, n, cls):
        if 'facts' in cls:
            return self.facts(n)
        if 'flow' in cls:
            return self.flow(n)
        if 'pagecards' in cls:
            return self.pagecards(n)
        if n.tag in ('summary', 'figcaption'):
            return self.flush([n])
        return self.children(n)

    def heading(self, n, level):
        self.last_heading = re.sub(r'\s+', ' ', n.text_content()).strip()
        content = self.paragraph([n])['content']
        colour = self.native.get('heading_colors', {}).get(str(level))
        if colour:  # Confluence won't colour code or link text, so only plain runs get the scheme colour
            for x in content:
                if x['type'] == 'text' and not any(m['type'] in ('code', 'link') for m in x.get('marks', [])):
                    x['marks'] = x.get('marks', []) + [{'type': 'textColor', 'attrs': {'color': colour}}]
        return {'type': 'heading', 'attrs': {'level': min(level, 6)}, 'content': content}

    def eyebrow(self, n):
        p = self.paragraph([n], ({'type': 'em'},))
        return [p] if p['content'] else []

    def panel(self, n, kind):
        content = self.children(n)
        if 'predict' in n.classes and content and content[0]['type'] == 'paragraph':
            content[0]['content'] = [{'type': 'text', 'text': 'Predict: ', 'marks': [{'type': 'strong'}]}] + content[0]['content']
        custom = next((self.native['panels'][c] for c in n.classes if c in self.native.get('panels', {})), None)
        return self.wrap('panel', dict(custom) if custom else {'panelType': kind}, content)

    def wrap(self, kind, attrs, content):
        inside, after = pack(kind, content)
        if not inside:
            return after
        node = {'type': kind, 'content': inside}
        if attrs:
            node['attrs'] = attrs
        return [node] + after

    def expand(self, n):
        summary = next((c for c in n.children if c.tag == 'summary'), None)
        title = summary.text_content().strip() if summary else 'Details'
        body = [c for c in n.children if c is not summary]
        holder = type(n)('div', parent=n.parent)
        holder.children = body
        content = [flatten_expand(x) for x in self.children(holder)]
        inside, after = pack('expand', [x for x in content if x])
        return [{'type': 'expand', 'attrs': {'title': re.sub(r'\s+', ' ', title)}, 'content': inside or [empty_p()]}] + after

    def figure(self, n):
        cap = next((c for c in n.children if c.tag == 'figcaption'), None)
        holder = type(n)('div', parent=n.parent)
        holder.children = [c for c in n.children if c is not cap]
        blocks = self.children(holder)
        if cap is None:
            return blocks
        caption = clean_inline(self.paragraph([cap])['content'])
        media = [b for b in blocks if b['type'] == 'mediaSingle']
        if len(media) == 1 and len(caption) and not any(b['type'] == 'extension' for b in blocks):
            media[0]['content'].append({'type': 'caption', 'content': caption})
            return blocks
        return blocks + [{'type': 'paragraph', 'content': [dict(x, marks=add_mark(x, 'em')) for x in caption]}]

    def listing(self, n, ordered):
        items, hoisted = [], []
        for li in [c for c in n.children if c.tag == 'li']:
            content, after = pack('listItem', self.children(li))
            hoisted += after
            if not content or content[0]['type'] != 'paragraph':
                content = [empty_p()] + content
            items.append({'type': 'listItem', 'content': content})
        if not items:
            return hoisted
        node = {'type': 'orderedList' if ordered else 'bulletList', 'content': items}
        if ordered:
            start = n.get('start') or '1'
            node['attrs'] = {'order': int(start) if start.isdigit() else 1}
        return [node] + hoisted

    def table(self, n):
        rows, hoisted = [], []
        for tr in [x for x in n.iter() if x.tag == 'tr']:
            cells = []
            for td in [c for c in tr.children if c.tag in ('td', 'th')]:
                content, after = pack('tableCell', self.children(td))
                hoisted += after
                attrs = {k: int(td.get(k)) for k in ('colspan', 'rowspan') if (td.get(k) or '').isdigit()}
                if td.tag == 'th' and self.native.get('table_header_bg'):
                    attrs['background'] = self.native['table_header_bg']
                cells.append({'type': 'tableHeader' if td.tag == 'th' else 'tableCell', 'attrs': attrs, 'content': content or [empty_p()]})
            if cells:
                rows.append({'type': 'tableRow', 'content': cells})
        if not rows:
            return hoisted
        return [{'type': 'table', 'attrs': {'isNumberColumnEnabled': False, 'layout': 'default'}, 'content': rows}] + hoisted

    def facts(self, n):
        facts = [c for c in n.children if c.tag and c.has_class('fact')]
        head = [self.cell('tableHeader', [x for x in f.children if x.tag in ('b', 'strong')]) for f in facts]
        body = [self.cell('tableCell', [x for x in f.children if x.tag not in ('b', 'strong')]) for f in facts]
        if not facts:
            return self.children(n)
        return [{'type': 'table', 'attrs': {'isNumberColumnEnabled': False, 'layout': 'default'},
                 'content': [{'type': 'tableRow', 'content': head}, {'type': 'tableRow', 'content': body}]}]

    def cell(self, kind, nodes):
        attrs = {'background': self.native['table_header_bg']} if kind == 'tableHeader' and self.native.get('table_header_bg') else {}
        return {'type': kind, 'attrs': attrs, 'content': [self.paragraph(nodes)]}

    def flow(self, n):
        items = []
        for step in [c for c in n.children if c.tag and c.has_class('step')]:
            parts = {k: next((c for c in step.children if c.tag and c.has_class(k)), None) for k in ('q', 'ref', 'd')}
            mark = '❌ ' if step.has_class('bad') else '✅ ' if step.has_class('good') else ''
            head = [{'type': 'text', 'text': mark}] if mark else []
            head += self.paragraph([parts['q']] if parts['q'] else [], ({'type': 'strong'},))['content']
            if parts['ref']:
                head += [{'type': 'text', 'text': '  '}] + self.paragraph([parts['ref']])['content']
            content = [{'type': 'paragraph', 'content': clean_inline(head)}]
            if parts['d']:
                content.append(self.paragraph([parts['d']]))
            items.append({'type': 'listItem', 'content': content})
        return [{'type': 'orderedList', 'attrs': {'order': 1}, 'content': items}] if items else self.children(n)

    def diff(self, n):
        head = next((c for c in n.children if c.tag and c.has_class('dh')), None)
        pre = next((c for c in n.iter() if c.tag == 'pre'), None)
        out = [self.paragraph([head], ({'type': 'strong'},))] if head else []
        return out + ([code_block(pre, 'diff', skip_class='ln')] if pre else [])

    def pagecards(self, n):
        items = []
        for a in [c for c in n.children if c.tag == 'a']:
            p = self.paragraph([a])
            items.append({'type': 'listItem', 'content': [p if p['content'] else empty_p()]})
        return [{'type': 'bulletList', 'content': items}] if items else []


# ---------- helpers ----------
CONCEPT_INDEX_TITLE = re.compile(r'^\s*(concepts?( on this page| index)?|on this page|contents)\s*$', re.I)


def is_concept_index(n):
    """The illustrate concept index (ul.concepts and its heading): Confluence's own table of contents replaces it."""
    if n.tag in ('ul', 'ol') and n.has_class('concepts'):
        return True
    return n.tag in ('h2', 'h3') and (n.get('id') == 'concepts' or bool(CONCEPT_INDEX_TITLE.match(n.text_content())))


def toc(max_level=2):
    """Confluence's Table of Contents macro, as the editor stores it."""
    import uuid as _uuid
    return {'type': 'extension', 'attrs': {
        'layout': 'default', 'extensionType': 'com.atlassian.confluence.macro.core', 'extensionKey': 'toc',
        'parameters': {'macroParams': {'style': {'value': 'none'}, 'maxLevel': {'value': str(max_level)}},
                       'macroMetadata': {'macroId': {'value': str(_uuid.uuid4())}, 'schemaVersion': {'value': '1'},
                                         'title': 'Table of Contents'}},
        'localId': str(_uuid.uuid4())}}


def is_inline(n):
    if n.tag is None:
        return True
    return n.tag in INLINE and not any(c.tag and not is_inline(c) for c in n.children)


def empty_p():
    return {'type': 'paragraph', 'content': []}


def add_mark(x, mark):
    marks = x.get('marks', [])
    if x.get('type') != 'text' or any(m['type'] in (mark, 'code') for m in marks):
        return marks
    return marks + [{'type': mark}]


def clean_inline(nodes):
    """Collapse whitespace, merge equal-mark text, trim the ends, drop empties and illegal mark mixes."""
    out = []
    for x in nodes:
        if x['type'] != 'text':
            out.append(x)
            continue
        text = re.sub(r'\s+', ' ', x['text'])
        marks = x.get('marks') or []
        if any(m['type'] == 'code' for m in marks):
            marks = [m for m in marks if m['type'] in CODE_MARK_OK]
        if out and out[-1]['type'] == 'text' and out[-1].get('marks', []) == marks:
            out[-1]['text'] += text
            continue
        out.append({'type': 'text', 'text': text, **({'marks': marks} if marks else {})})
    if out and out[0]['type'] == 'text':
        out[0]['text'] = out[0]['text'].lstrip()
    if out and out[-1]['type'] == 'text':
        out[-1]['text'] = out[-1]['text'].rstrip()
    return [x for x in out if x['type'] != 'text' or x['text']]


def code_block(pre, lang=None, skip_class=None):
    def text(node):
        if node.tag is None:
            return node.text
        if skip_class and node.has_class(skip_class):
            return ''
        return ''.join(text(c) for c in node.children) + ('\n' if node.has_class('ln') and not skip_class else '')
    body = text(pre).strip('\n')
    lang = lang or pre.get('data-lang') or guess_language(body)
    node = {'type': 'codeBlock', 'attrs': {'language': lang} if lang else {}}
    if body:
        node['content'] = [{'type': 'text', 'text': body}]
    return node


def project_macro_pattern():
    name = get('UE_PROJECT_NAME', '')
    return rf'|{re.escape(name.upper())}_\w+' if name else ''


def guess_language(code):
    if re.search(r'\b(UCLASS|UPROPERTY|TEXT\(|::|#include|TArray|FString|nullptr' + project_macro_pattern() + r')\b|\w+\.(cpp|h)\b', code):
        return 'cpp'
    if re.search(r'^\s*(def |import |from \w+ import )', code, re.M):
        return 'python'
    if re.search(r'^\s*\[[/\w.]+\]\s*$', code, re.M):
        return 'ini'
    if re.search(r'^\s*(const|let|function|document\.)', code, re.M):
        return 'javascript'
    return None


def pack(kind, content):
    """Split blocks into what the container may hold and what must follow it at the top level.

    Lists and table cells can't move content out without breaking reading order, so headings and
    panels there become plain paragraphs; widgets still move out because nothing else can hold them.
    """
    allowed = ALLOWED[kind]
    inside, after = [], []
    for b in content:
        if b['type'] in allowed:
            inside.append(b)
        elif b['type'] == 'extension' or kind not in ('listItem', 'tableCell'):
            after.append(b)
        else:
            inside.append({'type': 'paragraph', 'content': plain_text(b)})
    return inside, after


def plain_text(block):
    texts = []

    def walk(x):
        if x.get('type') == 'text':
            texts.append({'type': 'text', 'text': x['text'], **({'marks': x['marks']} if x.get('marks') else {})})
        for c in x.get('content', []):
            walk(c)
    walk(block)
    return clean_inline(texts)


def flatten_expand(b):
    """An expand can't hold another expand: show the inner one as a bold line plus its content."""
    if b['type'] != 'expand':
        return b
    return {'type': 'panel', 'attrs': {'panelType': 'info'},
            'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': b['attrs']['title'], 'marks': [{'type': 'strong'}]}]}]
            + [x for x in b['content'] if x['type'] in ALLOWED['panel']]}
