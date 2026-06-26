#!/usr/bin/env python3
"""
query_compendium.py — deterministic "name -> section + tight line range" locator
for the compendium, so a session can pull the exact rule slice instead of grepping
a 21k-line / 3.2MB file by hand (and instead of reading it whole, which blows the
chat context budget — that has ended chats).

The tool reads the big file in *its own* process and emits only the tight slice to
stdout, so what lands in context stays small. Output is capped (per-line width and
total lines) for the same reason; use --full to override.

Power sections are delimited exactly the way check.py delimits them: a power runs
from its <h4 class="power-name"> header to the next header (another power-name h4,
or an <h1>/<h2>).

USAGE
  query_compendium.py "Blade Velocity"      # show that power's section
  query_compendium.py force torrent         # words are joined; case-insensitive substring
  query_compendium.py saber --all           # dump every section whose name matches 'saber'
  query_compendium.py --headers             # table of contents (h1/h2/h4 + line numbers)
  query_compendium.py --grep 'Upkeep .* FP' # arbitrary regex, grep -n style
  query_compendium.py "Force Vessel" --strip --full   # tags stripped, no truncation

Exit 0 if something was found/printed, 1 if nothing matched.
"""
import re, sys, os, glob, argparse, bisect

REPO = os.path.dirname(os.path.abspath(__file__))
# tool lives in tools/, compendium lives one level up (repo root)
SEARCH_DIRS = [os.path.dirname(REPO), REPO]

H4_OPEN = '<h4 class="power-name">'
MAX_LINE = 400     # truncate displayed lines wider than this (compendium has 37k-char lines)
MAX_BODY = 400     # cap a single section's printed lines


def find_compendium():
    for d in SEARCH_DIRS:
        m = glob.glob(os.path.join(d, "*GURPS 4E conversion.html"))
        if m:
            return m[0]
    return None


def line_starts(s):
    """Offsets where each line begins, for offset -> 1-based line-number mapping."""
    starts = [0]
    i = s.find('\n')
    while i != -1:
        starts.append(i + 1)
        i = s.find('\n', i + 1)
    return starts


def line_of(starts, off):
    return bisect.bisect_right(starts, off)  # 1-based


def strip_tags(t):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', t)).strip()


def headers(s):
    """All structural headers as (offset, level, visible_text). level: 1/2 for h1/h2, 4 for power."""
    hs = []
    for m in re.finditer(r'<h([12])\b[^>]*>(.*?)</h\1>', s, re.S):
        hs.append((m.start(), int(m.group(1)), strip_tags(m.group(2))))
    for m in re.finditer(re.escape(H4_OPEN) + r'(.*?)</h4>', s, re.S):
        hs.append((m.start(), 4, strip_tags(m.group(1))))
    hs.sort(key=lambda x: x[0])
    return hs


def power_sections(s, hs):
    """For each power-name header, (name, start_off, end_off) bounded by the next header."""
    offs = [h[0] for h in hs]
    out = []
    for i, (off, lvl, txt) in enumerate(hs):
        if lvl != 4:
            continue
        nxt = offs[i + 1] if i + 1 < len(offs) else len(s)
        out.append((txt, off, nxt))
    return out


def emit_block(s, starts, start_off, end_off, strip, full):
    """Print a [start_off, end_off) span as numbered lines, capped unless --full."""
    first = line_of(starts, start_off)
    seg = s[start_off:end_off].rstrip('\n')
    lines = seg.split('\n')
    shown = lines if full else lines[:MAX_BODY]
    for n, ln in enumerate(shown, start=first):
        if strip:
            ln = strip_tags(ln)
            if not ln:
                continue
        if not full and len(ln) > MAX_LINE:
            ln = ln[:MAX_LINE] + f' …[+{len(ln) - MAX_LINE} chars, --full]'
        print(f'{n:>6}  {ln}')
    if not full and len(lines) > MAX_BODY:
        print(f'       …[+{len(lines) - MAX_BODY} more lines; --full or open the range directly]')


def main():
    ap = argparse.ArgumentParser(add_help=True, description="Locate a compendium section by name.")
    ap.add_argument('query', nargs='*', help='power-name substring (words joined, case-insensitive)')
    ap.add_argument('--headers', '-H', action='store_true', help='print a table of contents and exit')
    ap.add_argument('--grep', '-g', metavar='REGEX', help='arbitrary regex search, grep -n style')
    ap.add_argument('--all', '-a', action='store_true', help='dump bodies of all matching sections')
    ap.add_argument('--strip', '-s', action='store_true', help='strip HTML tags from body output')
    ap.add_argument('--full', '-f', action='store_true', help='do not truncate long lines / big sections')
    args = ap.parse_args()

    comp = find_compendium()
    if not comp:
        print('compendium (*GURPS 4E conversion.html) not found', file=sys.stderr)
        sys.exit(2)
    s = open(comp, encoding='utf-8').read()
    starts = line_starts(s)
    print(os.path.basename(comp))

    # --- table of contents ---
    if args.headers:
        for off, lvl, txt in headers(s):
            indent = {1: '', 2: '  ', 4: '      '}[lvl]
            print(f'{line_of(starts, off):>6}  {indent}{txt}')
        sys.exit(0)

    # --- arbitrary regex ---
    if args.grep:
        try:
            rx = re.compile(args.grep, re.I)
        except re.error as e:
            print(f'bad regex: {e}', file=sys.stderr)
            sys.exit(2)
        hits, cap = 0, 200
        for m in rx.finditer(s):
            n = line_of(starts, m.start())
            ln = s[starts[n - 1]:(starts[n] - 1 if n < len(starts) else len(s))]
            if not args.full and len(ln) > MAX_LINE:
                ln = ln[:MAX_LINE] + ' …'
            print(f'{n:>6}: {ln.rstrip()}')
            hits += 1
            if hits >= cap and not args.full:
                print(f'       …[{cap}+ hits; refine the regex or use --full]')
                break
        if hits == 0:
            print(f"no match for /{args.grep}/", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    # --- power-name lookup (default) ---
    q = ' '.join(args.query).strip().lower()
    if not q:
        ap.print_help()
        sys.exit(2)
    secs = power_sections(s, headers(s))
    matches = [(nm, a, b) for (nm, a, b) in secs if q in nm.lower()]

    if not matches:
        print(f"no power-name matches '{q}'. Try --grep for prose, or --headers for the index.",
              file=sys.stderr)
        sys.exit(1)

    if len(matches) == 1 or args.all:
        for nm, a, b in matches:
            ln0, ln1 = line_of(starts, a), line_of(starts, b - 1)
            print(f"\n=== {nm}  (lines {ln0}\u2013{ln1}) ===")
            emit_block(s, starts, a, b, args.strip, args.full)
        sys.exit(0)

    # several matches, no --all: list them with a short preview
    print(f"{len(matches)} matches for '{q}':")
    for nm, a, b in matches:
        ln0, ln1 = line_of(starts, a), line_of(starts, b - 1)
        preview = strip_tags(s[a:b])[:90]
        print(f'  lines {ln0:>6}\u2013{ln1:<6}  {nm:<28}  {preview}…')
    print("Re-run with the exact name, or --all to dump every match.")
    sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except BrokenPipeError:
        # piped into head/grep/less and the reader closed early — not an error
        try:
            sys.stdout.close()
        except Exception:
            pass
        os._exit(0)
