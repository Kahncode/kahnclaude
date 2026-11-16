"""Tiny HTML tree on the standard library, enough for /illustrate pages.

Keeps each element's raw start tag so SVG attribute case (viewBox, refX…) survives re-serialisation.
"""
import html as H
import re
from html.parser import HTMLParser

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
RAW_TEXT = {'script', 'style'}


class Node:
    __slots__ = ('tag', 'attrs', 'children', 'parent', 'text', 'raw', 'closed')

    def __init__(self, tag=None, attrs=None, parent=None, text=None, raw=''):
        self.tag, self.attrs, self.parent, self.text, self.raw = tag, dict(attrs or {}), parent, text, raw
        self.children, self.closed = [], True

    def get(self, key, default=None): return self.attrs.get(key, default)
    @property
    def classes(self): return set((self.attrs.get('class') or '').split())
    def has_class(self, *names): return bool(self.classes & set(names))

    def iter(self):
        yield self
        for c in self.children:
            if c.tag:
                yield from c.iter()

    def text_content(self):
        if self.tag is None:
            return self.text or ''
        if self.tag in RAW_TEXT:
            return ''
        return ''.join(c.text_content() for c in self.children)

    def outer_html(self, skip=None):
        if self.tag is None:
            p = self.parent
            return self.text if p is not None and p.tag in RAW_TEXT else H.escape(self.text, quote=False)
        if skip and self in skip:
            return ''
        if not self.closed:
            return self.raw
        inner = ''.join(c.outer_html(skip) for c in self.children)
        name = re.match(r'<\s*([^\s/>]+)', self.raw).group(1) if self.raw else self.tag
        return f'{self.raw}{inner}</{name}>'


class _Builder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node('#root')
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, [(k, v if v is not None else '') for k, v in attrs], self.cur, raw=self.get_starttag_text())
        self.cur.children.append(node)
        if tag in VOID:
            node.closed = False
        else:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        node = Node(tag, [(k, v if v is not None else '') for k, v in attrs], self.cur, raw=self.get_starttag_text())
        node.closed = False
        self.cur.children.append(node)

    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is not self.root:
            self.cur = n.parent

    def handle_data(self, data):
        if data:
            self.cur.children.append(Node(None, parent=self.cur, text=data))


def parse(text):
    b = _Builder()
    b.feed(text)
    b.close()
    return b.root


def find(root, pred):
    return next((n for n in root.iter() if pred(n)), None)


def find_all(root, pred):
    return [n for n in root.iter() if pred(n)]
