#!/usr/bin/env python3
"""
check.py — KOTOR/GURPS toolset invariant + golden-math harness.

Run before every push:  python3 check.py
Exit code 0 = all invariants hold; non-zero = at least one FAIL.

Design rule: assert STRUCTURE and RELATIONSHIPS, never magic numbers — the power
corpus and schemas grow constantly, so a hardcoded count would rot. SKILL.md says
silent corruption is worse than a crash; this is the guard that makes that true.

Checks
  A. Compendium  — every <h4 class="power-name"> has exactly one Upkeep/Hands/Move
                   stat field + one "At the table." block; headers unique; div-balanced.
  B. Sheet       — all inline <script> blocks parse (node --check); every
                   window.FORCE_DESC info-panel key maps to a real compendium power.
  C. Characters  — each characters/*.json parses and carries every top-level key
                   that the sheet's own blankChar() schema defines.
  D. Golden math — the REAL extracted attrRaw()/ATTR_COST derivation returns the
                   expected attribute level for known point-cost inputs (incl. the
                   HT-at-10/level gotcha). Extend CASES freely.
"""
import re, sys, glob, json, subprocess, tempfile, os

REPO = os.path.dirname(os.path.abspath(__file__))
def find(pat):
    m = glob.glob(os.path.join(REPO, pat))
    return m[0] if m else None

COMP  = find("Star Wars the Old Republic GURPS 4E conversion.html")
SHEET = find("sheet.html")
CHARS = sorted(glob.glob(os.path.join(REPO, "characters", "*.json")))

FAILS, WARNS, NOTES = [], [], []
def fail(m): FAILS.append(m)
def warn(m): WARNS.append(m)
def note(m): NOTES.append(m)

# ---- helpers -------------------------------------------------------------
def brace_extract(s, brace_idx):
    """Return the balanced {...} starting at s[brace_idx]=='{', string-aware
    (handles ' " ` quoting and \\ escapes so braces inside HTML values don't fool it)."""
    i, depth, n, q = brace_idx, 0, len(s), None
    while i < n:
        c = s[i]
        if q:
            if c == '\\': i += 2; continue
            if c == q: q = None
            i += 1; continue
        if c in '"\'`': q = c
        elif c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return s[brace_idx:i+1]
        i += 1
    return None

def node_run(js, check_only=False):
    f = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8')
    f.write(js); f.close()
    try:
        cmd = ['node', '--check', f.name] if check_only else ['node', f.name]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return r.returncode, r.stdout, r.stderr
    finally:
        os.unlink(f.name)

def obj_after(label, text):
    """Extract the object literal assigned to `label` (first `{` after `label=`)."""
    m = re.search(re.escape(label) + r'\s*=', text)
    if not m: return None
    b = text.find('{', m.end())
    return brace_extract(text, b) if b >= 0 else None

# ---- A. Compendium -------------------------------------------------------
def check_compendium():
    if not COMP:
        fail("compendium file not found"); return set()
    s = open(COMP, encoding="utf-8").read()
    heads = sorted([m.start() for m in re.finditer(r'<h4 class="power-name">', s)] +
                   [m.start() for m in re.finditer(r'<h[12]', s)])
    ph = [m.start() for m in re.finditer(r'<h4 class="power-name">', s)]
    names = [re.sub(r'<[^>]+>', '', s[h+len('<h4 class="power-name">'):s.find('</h4>', h)]).strip()
             for h in ph]
    dup = sorted({n for n in names if names.count(n) > 1})
    if dup: fail(f"compendium: duplicate power-name headers: {dup}")
    viol = []
    for h, nm in zip(ph, names):
        nxt = min([x for x in heads if x > h], default=len(s)); seg = s[h:nxt]
        cnt = [seg.count(f'<span class="stat-k">{k}</span>') for k in ('Hands', 'Move')]
        up = seg.count('<p class="upkeep">')
        w = seg.count('<p class="warn"><b>At the table.</b>')
        if cnt != [1, 1] or up != 1 or w != 1: viol.append((nm, cnt, up, w))
    if viol:
        fail(f"compendium: {len(viol)} power(s) with bad statgrid fields / At-the-table block: {viol[:8]}")
    d = s.count('<div') - s.count('</div>')
    if d != 0: fail(f"compendium: <div> balance delta {d} (expected 0)")
    if not dup and not viol and d == 0:
        note(f"compendium: {len(ph)} powers, each with Hands/Move (grid) + Upkeep line + At-the-table; headers unique; div-balanced")
    return set(names)

# ---- B. Sheet ------------------------------------------------------------
def check_sheet(power_names):
    if not SHEET:
        fail("sheet.html not found"); return
    s = open(SHEET, encoding="utf-8").read()
    scripts = re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', s, re.S)
    nbad = 0
    for i, sc in enumerate(scripts):
        rc, _, err = node_run(sc, check_only=True)
        if rc != 0:
            nbad += 1; fail(f"sheet: inline script #{i} fails node --check: {err.strip().splitlines()[-1] if err.strip() else 'parse error'}")
    if nbad == 0:
        note(f"sheet: {len(scripts)} inline script block(s) parse clean")
    # FORCE_DESC keys -> must be real compendium powers
    lit = obj_after("FORCE_DESC", s)
    if not lit:
        warn("sheet: could not locate FORCE_DESC object literal — skipping panel-subset check")
    else:
        rc, out, err = node_run(f"const O={lit};process.stdout.write(Object.keys(O).join('\\n'))")
        if rc != 0:
            warn(f"sheet: FORCE_DESC literal did not eval — skipping panel-subset check ({err.strip()[:120]})")
        else:
            keys = [k for k in out.split('\n') if k]
            orphans = [k for k in keys if k not in power_names]
            if orphans:
                warn(f"sheet: {len(orphans)} FORCE_DESC panel(s) have no matching compendium power "
                     f"(naming drift or stale panel) — review: {orphans[:12]}")
            else:
                note(f"sheet: all {len(keys)} FORCE_DESC panels map to a real compendium power")

# ---- B2. Panel <-> compendium FP fidelity --------------------------------
def _norm_fp(x): return re.sub(r'\s+', '', (x or '')).lower()

def check_panel_fidelity():
    """Every FORCE_DESC panel that exposes an FP stat field must carry the SAME
    FP cost as its compendium block. Catches the mechanical-cost drift the
    name-mapping check (B) can't see. Compares only where BOTH sides have an FP
    field; the Upkeep *prose* legitimately differs in wording between the panel
    (grid) and compendium (prose) formats, so only the discrete FP value is
    asserted. WARN (reconcile), not FAIL — matches the panel-subset severity."""
    if not (COMP and SHEET): return
    comp = open(COMP, encoding="utf-8").read()
    sheet = open(SHEET, encoding="utf-8").read()
    fp_re = r'>FP</span><span class="stat-v[^"]*">([^<]*)</span>'
    # compendium: power-name -> FP grid value
    heads = sorted([m.start() for m in re.finditer(r'<h4 class="power-name">', comp)] +
                   [m.start() for m in re.finditer(r'<h[12]', comp)])
    comp_fp = {}
    for h in [m.start() for m in re.finditer(r'<h4 class="power-name">', comp)]:
        nm = re.sub(r'<[^>]+>', '', comp[h+len('<h4 class="power-name">'):comp.find('</h4>', h)]).strip()
        nxt = min([x for x in heads if x > h], default=len(comp))
        m = re.search(fp_re, comp[h:nxt])
        if m: comp_fp[nm] = m.group(1).strip()
    # panel: eval FORCE_DESC, pull each panel's FP with the same regex inside node
    lit = obj_after("FORCE_DESC", sheet)
    if not lit: return   # check_sheet already warned
    js = ("const O=%s;const out={};const re=new RegExp('>FP</span><span class=\"stat-v[^\"]*\">([^<]*)</span>');"
          "for(const k in O){const m=O[k].match(re); if(m) out[k]=m[1].trim();}"
          "process.stdout.write(JSON.stringify(out));") % lit
    rc, o, err = node_run(js)
    if rc != 0: return   # eval failure already surfaced by check_sheet
    panel_fp = json.loads(o)
    both = [n for n in panel_fp if n in comp_fp]
    mism = [(n, panel_fp[n], comp_fp[n]) for n in both if _norm_fp(panel_fp[n]) != _norm_fp(comp_fp[n])]
    if mism:
        warn("sheet: %d panel FP cost(s) differ from the compendium — reconcile: %s"
             % (len(mism), "; ".join("%s [panel %r vs comp %r]" % (n, p, c) for n, p, c in mism[:6])))
    else:
        note("sheet: all %d panel FP costs (of %d panels) match the compendium (FP-fidelity)"
             % (len(both), len(panel_fp)))

# ---- C. Characters -------------------------------------------------------
def required_keys_from_blankchar():
    if not SHEET: return None
    s = open(SHEET, encoding="utf-8").read()
    m = re.search(r'blankChar\(\)\s*\{', s)
    if not m: return None
    rb = s.find('return', m.end())
    if rb < 0: return None
    b = s.find('{', rb)
    if b < 0: return None
    lit = brace_extract(s, b)
    if not lit: return None
    rc, out, err = node_run(f"function bc(){{return {lit}}};process.stdout.write(Object.keys(bc()).join('\\n'))")
    if rc != 0: return None
    return [k for k in out.split('\n') if k]

def check_characters():
    if not CHARS:
        warn("no characters/*.json found"); return
    req = required_keys_from_blankchar()
    if req:
        note(f"schema: blankChar() defines {len(req)} top-level keys (used as the JSON contract)")
    else:
        # fall back to the intersection of the shipped, known-good characters
        sets = []
        for c in CHARS:
            try: sets.append(set(json.load(open(c)).keys()))
            except Exception: pass
        req = sorted(set.intersection(*sets)) if sets else []
        warn("could not extract blankChar() schema — falling back to shared keys of existing characters")
    for c in CHARS:
        name = os.path.basename(c)
        try:
            d = json.load(open(c))
        except Exception as e:
            fail(f"character {name}: invalid JSON ({e})"); continue
        missing = [k for k in req if k not in d]
        if missing:
            warn(f"character {name}: {len(missing)} schema key(s) absent {missing} — non-breaking "
                 f"(import backfills via mergeChar from blankChar() defaults); backfill on disk to silence")
        else:
            note(f"character {name}: valid JSON, all schema keys present")

# ---- D. Golden rules-math (runs the REAL extracted code) -----------------
# (attribute, points_spent, expected_level). ST/HT cost 10/lvl, DX/IQ cost 20/lvl.
CASES = [
    ("ST", 20, 12), ("ST", 0, 10),
    ("DX", 40, 12), ("DX", 20, 11),
    ("IQ", 0, 10),
    ("HT", 20, 12),   # the gotcha: HT is 10/lvl, not DX/IQ's 20/lvl
    ("HT", 40, 14),
]
def check_golden_math():
    if not SHEET:
        fail("sheet.html not found — cannot run golden math"); return
    s = open(SHEET, encoding="utf-8").read()
    cost = obj_after("ATTR_COST", s)
    m = re.search(r'function attrRaw\([^)]*\)\s*\{', s)
    if not (cost and m):
        warn("golden: ATTR_COST / attrRaw not found — skipping attribute-derivation golden test"); return
    body = brace_extract(s, m.start() + s[m.start():].find('{'))
    fn = s[m.start():m.start()+s[m.start():].find('{')] + body  # 'function attrRaw(a){...}'
    cases_js = json.dumps(CASES)
    js = f"""
const ATTR_COST={cost};
let C;
{fn}
const cases={cases_js};
let bad=0;
for(const [a,pts,exp] of cases){{
  C={{attr:{{[a]:pts}}}};
  const got=attrRaw(a);
  if(got!==exp){{bad++;console.log(`attrRaw ${{a}} pts=${{pts}} got=${{got}} expected=${{exp}}`);}}
}}
process.exit(bad?1:0);
"""
    rc, out, err = node_run(js)
    if rc != 0:
        fail("golden: attrRaw derivation mismatch — " + (out.strip() or err.strip()))
    else:
        note(f"golden: attrRaw passes {len(CASES)} attribute-derivation cases (incl. HT 10/level)")

# ---- run -----------------------------------------------------------------
def main():
    names = check_compendium()
    check_sheet(names)
    check_panel_fidelity()
    check_characters()
    check_golden_math()

    print("\n".join("  · " + n for n in NOTES))
    if WARNS:
        print("\nWARN:")
        print("\n".join("  ! " + w for w in WARNS))
    if FAILS:
        print("\nFAIL:")
        print("\n".join("  ✗ " + f for f in FAILS))
        print(f"\n{len(FAILS)} failure(s).")
        sys.exit(1)
    print(f"\nOK — all invariants hold ({len(WARNS)} warning(s)).")
    sys.exit(0)

if __name__ == "__main__":
    main()
