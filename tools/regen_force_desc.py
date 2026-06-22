#!/usr/bin/env python3
"""Regenerate the Force-power description data embedded in sheet.html.

Source of truth is the compendium. This script extracts each power's
<div class="power-body"> prose and rewrites the block between the
/*FORCE_DESC_DATA_START*/ ... /*FORCE_DESC_DATA_END*/ markers in sheet.html.

Run from the repo root after editing the compendium:
    python3 tools/regen_force_desc.py
Then commit sheet.html.
"""
import re, json, io, sys, os

COMP = "Star Wars the Old Republic GURPS 4E conversion.html"
SH = "sheet.html"
START = "/*FORCE_DESC_DATA_START*/"
END = "/*FORCE_DESC_DATA_END*/"

def read(p): return io.open(p, encoding='utf-8', newline='').read()

def bounded(s, start):
    depth = 0
    for m in re.finditer(r'<(/?)div\b[^>]*>', s[start:]):
        depth += -1 if m.group(1) == '/' else 1
        if depth == 0:
            return s[start:start + m.end()]
    return s[start:start + 6000]

def main():
    if not os.path.exists(COMP) or not os.path.exists(SH):
        sys.exit("Run from the repo root (compendium + sheet.html must be present).")
    s = read(COMP)
    sh = read(SH)
    sheet_names = set(re.findall(r'\{"name": "([^"]+)", "skill": "Force"', sh))
    drop_attr = re.compile(r'\s+(?:style|id)="[^"]*"')

    out = {}
    for m in re.finditer(r'<div class="power">', s):
        blk = bounded(s, m.start())
        nm = re.search(r'<h4 class="power-name">([^<]+)</h4>', blk)
        if not nm:
            continue
        key = nm.group(1).strip().replace('&amp;', '&').replace('&rsquo;', '\u2019').replace('&lsquo;', '\u2018')
        body = re.search(r'<div class="power-body">(.*?)</div>\s*</div>\s*$', blk, re.S)
        if body:
            h = body.group(1)
        else:
            parts = re.split(r'</div>\s*</div>', blk, maxsplit=1)
            h = re.sub(r'</div>\s*$', '', parts[1]).strip() if len(parts) > 1 else ''
        h = drop_attr.sub('', h)
        h = re.sub(r'>\s+<', '><', h)
        h = re.sub(r'[ \t]{2,}', ' ', h).strip()
        if h and key in sheet_names:
            out[key] = h

    js = json.dumps(out, ensure_ascii=False).replace('</script', '<\\/script')
    new_block = START + "window.FORCE_DESC=" + js + ";" + END

    if sh.count(START) != 1 or sh.count(END) != 1:
        sys.exit("ABORT: data markers not found exactly once in sheet.html")
    pre = sh[:sh.index(START)]
    post = sh[sh.index(END) + len(END):]
    io.open(SH, 'w', encoding='utf-8', newline='').write(pre + new_block + post)

    missing = sorted(n for n in sheet_names if n not in out)
    print(f"FORCE_DESC refreshed: {len(out)} powers, {len(js.encode('utf-8'))//1024} KB")
    print(f"{len(missing)} Force powers have no compendium entry:")
    print("  " + ", ".join(missing))

if __name__ == "__main__":
    main()
