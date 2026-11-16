"""Dry-run Horde templates: RunUAT BuildGraph -ListOnly with each template's default args.

Usage: python -I -X utf8 listonly_templates.py <stream.json> <id,id,...> [--out <dir>] [extra BuildGraph args]
Get the stream json with PowerShell: p4 print -q -o <file> <HORDE_STREAM_CONFIG from project-vars>
Logs: <out>\\<templateId>.log (default out: <TEMP_BASE>\\horde-scratch\\listonly)
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / '.claude' / 'scripts' / 'lib'))
from project_vars import get  # noqa: E402

NODE_LINE = re.compile(r'Compile .*(Editor|Tools)|Update Version Files|Test$')


def load_stream_json(path):
    src = open(path, encoding='utf-8').read()
    src = re.sub(r'(?m)^\s*//.*$', '', src)       # Horde accepts // comments
    src = re.sub(r',(\s*[}\]])', r'\1', src)      # and trailing commas
    return json.loads(src)


def template_args(template):
    args = [a for a in template['arguments'] if a not in ('-p4', '-submit')]
    for param in template.get('parameters', []):
        for item in param.get('items', []):
            key = 'argumentIfEnabled' if item.get('default') else 'argumentIfDisabled'
            if item.get(key):
                args.append(item[key])
    return args


def run_listonly(template, extra, root, engine, out_dir):
    cmd = [os.path.join(engine, 'Build', 'BatchFiles', 'RunUAT.bat'), 'BuildGraph']
    cmd += template_args(template) + ['-set:Horde=true', '-ListOnly'] + extra
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=root)
    log = result.stdout + result.stderr
    with open(os.path.join(out_dir, template['id'] + '.log'), 'w', encoding='utf-8') as f:
        f.write(log)
    print(f"=== {template['id']} ({template['name']}) exit={result.returncode}")
    for line in log.splitlines():
        if NODE_LINE.search(line.strip()):
            print('   ', line.strip())
    return result.returncode


def parse_args():
    if len(sys.argv) < 3:
        sys.exit(__doc__ + f"\nHORDE_STREAM_CONFIG = {get('HORDE_STREAM_CONFIG', '<not set>')}")
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('stream_json')
    parser.add_argument('ids')
    parser.add_argument('--out')
    args, extra = parser.parse_known_args()
    args.out = args.out or os.path.join(get('TEMP_BASE'), 'horde-scratch', 'listonly')
    return args, extra


def main():
    args, extra = parse_args()
    root = os.environ.get('PROJECT_ROOT') or get('PROJECT_ROOT')
    engine = os.environ.get('UE_ENGINE') or get('UE_ENGINE')
    stream = load_stream_json(args.stream_json)
    ids = args.ids.split(',')
    os.makedirs(args.out, exist_ok=True)
    found = [t for t in stream['templates'] if t['id'] in ids]
    missing = set(ids) - {t['id'] for t in found}
    if missing:
        print(f"Unknown template ids: {', '.join(sorted(missing))}", file=sys.stderr)
    codes = [run_listonly(t, extra, root, engine, args.out) for t in found]
    sys.exit(1 if missing or any(codes) else 0)


if __name__ == '__main__':
    main()
