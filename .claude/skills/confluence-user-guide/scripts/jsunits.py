"""Split page JavaScript into top-level statements, and find which element ids each one uses.

Good enough for hand-written /illustrate scripts: strings, template literals, comments and the
usual regex literals are skipped; statements end at a top-level `;` or at a newline that ASI would end.
"""
import re

REGEX_PREV = set('(,=:[!&|?{};+-*%<>~^') | {''}
CONTINUES = set('.,?:+-*/%=&|<>)]}([`')


def _skip_string(js, i):
    q, i = js[i], i + 1
    while i < len(js) and js[i] != q:
        i += 2 if js[i] == '\\' else 1
    return i + 1


def _skip_comment(js, i):
    if js.startswith('//', i):
        j = js.find('\n', i)
        return len(js) if j < 0 else j
    j = js.find('*/', i + 2)
    return len(js) if j < 0 else j + 2


def _skip_regex(js, i):
    i, in_class = i + 1, False
    while i < len(js) and js[i] != '\n':
        c = js[i]
        if c == '\\':
            i += 2
            continue
        if c == '[':
            in_class = True
        elif c == ']':
            in_class = False
        elif c == '/' and not in_class:
            i += 1
            while i < len(js) and js[i].isalpha():
                i += 1
            return i
        i += 1
    return i


def _skip_template(js, i):
    i += 1
    while i < len(js):
        c = js[i]
        if c == '\\':
            i += 2
        elif c == '`':
            return i + 1
        elif js.startswith('${', i):
            i = _skip_block(js, i + 1)
        else:
            i += 1
    return i


def _skip_block(js, i):
    """From an opening brace to just past its match."""
    depth, prev = 0, ''
    while i < len(js):
        start = i
        i, c = _skip_token(js, i, prev)
        prev = _prev_after(js, start, c, prev)
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return i
    return i


def _skip_token(js, i, prev=''):
    """Returns (next index, structural char or '' for skipped literals/comments)."""
    c = js[i]
    if c in '"\'':
        return _skip_string(js, i), ''
    if c == '`':
        return _skip_template(js, i), ''
    if js.startswith('//', i) or js.startswith('/*', i):
        return _skip_comment(js, i), ''
    if c == '/' and prev in REGEX_PREV:
        return _skip_regex(js, i), ''
    return i + 1, c


def _next_significant(js, i):
    while i < len(js):
        if js[i].isspace():
            i += 1
        elif js.startswith('//', i) or js.startswith('/*', i):
            i = _skip_comment(js, i)
        else:
            return i
    return i


def _ends_here(js, i, prev):
    if not (prev in ';})]\'"`' or prev.isalnum() or prev == '_'):
        return False
    j = _next_significant(js, i)
    if j >= len(js):
        return True
    if js[j] in CONTINUES:
        return False
    return not re.match(r'(else|catch|finally|while)\b', js[j:])


def _prev_after(js, i, c, prev):
    if c:
        return prev if c.isspace() else c
    if js[i] in '"\'`':
        return js[i]
    if js.startswith('//', i) or js.startswith('/*', i):
        return prev
    return 'a'  # a regex literal is a value, so a following '/' divides


def split_units(js):
    units, start, depth, i, prev = [], 0, 0, 0, ''
    while i < len(js):
        nxt, c = _skip_token(js, i, prev)
        if c and c in '([{':
            depth += 1
        elif c and c in ')]}':
            depth -= 1
        if depth == 0 and (c == ';' or (c == '\n' and _ends_here(js, i, prev))):
            if js[start:nxt].strip():
                units.append(js[start:nxt])
            start = nxt
        prev = _prev_after(js, i, c, prev)
        i = nxt
    if js[start:].strip():
        units.append(js[start:])
    return units


LITERAL = re.compile(r'"((?:\\.|[^"\\\n])*)"|\'((?:\\.|[^\'\\\n])*)\'|`((?:\\.|[^`\\])*)`', re.S)


def referenced_ids(code, all_ids):
    """Element ids named in string literals: 'btnPrev', '#cards > g', `#${x}` is not resolved."""
    found = set()
    for m in LITERAL.finditer(code):
        lit = next(g for g in m.groups() if g is not None)
        if lit in all_ids:
            found.add(lit)
        for tok in re.findall(r'#([A-Za-z][\w-]*)', lit):
            if tok in all_ids:
                found.add(tok)
    return found


DECL = re.compile(r'^\s*(?:(?:async\s+)?function\s*\*?\s*([A-Za-z_$][\w$]*)|(?:const|let|var|class)\s+([A-Za-z_$][\w$]*))')
DECL_LIST = re.compile(r'(?:^|,)\s*([A-Za-z_$][\w$]*)\s*=')


def declared_names(code):
    """Top-level names a statement declares: function f, class C, const a = …, b = … (destructuring skipped)."""
    m = DECL.match(_strip_leading_comments(code))
    if not m:
        return set()
    names = {m.group(1) or m.group(2)}
    if m.group(2) and re.match(r'\s*(const|let|var)\b', _strip_leading_comments(code)):
        body = _strip_leading_comments(code)
        names |= set(DECL_LIST.findall(_top_level_text(body)))
    return names


def _strip_leading_comments(code):
    i = _next_significant(code, 0)
    return code[i:]


def _top_level_text(code):
    """The statement with bracketed parts and literals blanked, so `a = f(b = 1)` only yields a."""
    out, depth, i, prev = [], 0, 0, ''
    while i < len(code):
        nxt, c = _skip_token(code, i, prev)
        if c and c in '([{':
            depth += 1
        elif c and c in ')]}':
            depth -= 1
        elif depth == 0 and c:
            out.append(c)
        prev = _prev_after(code, i, c, prev)
        i = nxt
    return ''.join(out)


def with_dependencies(chosen, units):
    """Add the statements that declare names the chosen ones use, transitively, keeping page order."""
    decl = {}
    for k, u in enumerate(units):
        for name in declared_names(u['code']):
            decl.setdefault(name, k)
    keep, todo = set(chosen), list(chosen)
    while todo:
        k = todo.pop()
        words = set(re.findall(r'[A-Za-z_$][\w$]*', units[k]['code']))
        for w in words:
            d = decl.get(w)
            if d is not None and d not in keep:
                keep.add(d)
                todo.append(d)
    return sorted(keep)
