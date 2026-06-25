# Dara Dara Campaign — Context & Pending Work

*This file is the churny handoff layer. Update it at the end of each session.
Durable conventions live in SKILL.md; durable project facts live in the Project
custom instructions. Don't duplicate those here.*

---

## Repo state

Branch `main`, latest commit: **3e29e5c**
"Ship per-cell recharge differentiation (+2 blaster ladder) + ion
magnetic-explosion redefinition across compendium, sheet, console, cheatsheet"

PAT at `~/.ghtoken` (chmod 600). Credential helper and git identity already
configured if the sandbox still has the clone at `/home/claude/repo`. If not,
re-clone with the PAT and `git remote set-url` to a clean URL, then mask all
push output via `sed`.

Stripped compendium text at `/tmp/comp.txt` — rebuild before grepping:
```
python3 -c "import re; s=open('Star Wars the Old Republic GURPS 4E conversion.html',encoding='utf-8',errors='ignore').read(); s=re.sub(r'<[^>]+>',' ',s); s=re.sub(r'\s+',' ',s); open('/tmp/comp.txt','w').write(s)"
```

---

## What shipped last session (do not re-do)

### Per-cell recharge differentiation
- Replaced the old flat +4/turn trickle with a per-cell ladder across all four
  files (compendium, sheet, console, cheatsheet):
  - Standard & heavy blaster cores: **+2/turn**
  - Sonic & crew/emplaced cores: **+1/turn**
  - Ion cells: **+1 per 2 turns**
  - Disruptor cells: **+1 per 4 turns**
  - Slug/kinetic: no recharge (magazines; unchanged)
- Added "Trickle by Cell" rule paragraph in the compendium and surfaced
  Sonic, Ion, Disruptor cells as named items in the deep-charge roster table.
- Sheet and console have **no live-ammo engine** — `shots` is display-only.
  Recharge is rule-level only; no code was wired.

### Ion magnetic-explosion redefinition
Ion is now a **magnetic concussion** (not anti-machine/near-0 vs flesh):
- **vs flesh/organics:** full listed dice as crushing, **AD 1** — it ruptures.
- **vs droids/vehicles/cyborgs:** **AD 5 + HT/shutdown** (capture-intact
  survives: droid takes system shock, not HP; disable still distinct from destroy).
- **vs personal energy shields:** bypasses them entirely (recategorised
  energy→kinetic; stops only kinetic deflectors).
- **Ship-scale ion:** unchanged — ×2 vs shields, 0 hull.

Changed across: jargon damage code, Master Damage matrix, "Anti-Machine Key"
section, Part V weapon entries + header, droid book (glossary, shutdown, capture
note, grenades), ion grenade / plasma mine, energy-shield family line, sheet
`vsOrganic` flags (false→true ×4), sheet/console weapon notes, cheatsheet ion
damage-type matrix row, cheatsheet ion-class skills line.

All four files contradiction-swept (0 hits); medpack healing rates intact
(2d+4/turn ×4, 3d+6/turn ×2, 1d+2/turn ×2); all inline JS node-checked clean.

---

## Pending — immediate / agreed

### Etched Counter redesign *(agreed, not yet executed)*
Approved model: banked counter inscribed in advance, FP paid upfront, fires
free at trigger against any incoming Force power of Tier III or lower (not one
named power). Needs a handoff doc authored before execution (per design-work
discipline).

### Sekan JSON skill rename
`sekan.json`: two skill entries need renaming to canonical shape:
- `Blasters (Rifle)` → `Blasters` / specialisation `Rifle`
- `Blasters (Pistol)` → `Blasters` / specialisation `Pistol`
Verify exact key names against compendium skills list before touching.

### Sheet — SABER_FORMS Ataru entry
`sheet.html` `SABER_FORMS` constant: Ataru entry needs updating to match
current compendium Ataru prose (changed in a prior pass).

### Compendium — Doc II §2.9 cross-ref fix
"Combinations Reference" link in Doc II §2.9 points to Doc I's section —
safe one-line anchor fix, awaiting go-ahead.

### Cheatsheet page 2 readability
Page 2 of `Combat_Cheatsheet_A3.html` cannot exceed 6.6pt font without
restructuring layout. The only path to page-4-level readability is splitting
page 2 into two pages (4→5 total). James has not yet said to proceed.

---

## Pending — backlog / longer-horizon

- **Galactic-record chronicle update** — off-chronicle events need adding,
  broken galaxy-map link fix pending.
- **Heading-level drift** in the Vehicles doc (Doc VI) from the SP-shield
  rework — cosmetic but noticeable.
- **Continued compendium review passes** — weapons/armour stat tables,
  reworked ship stat blocks, droids, skills point-ledger, economy pricing.
- **Battlemap generator** — procedural, in-repo, compendium-driven, top-down
  Canvas-based, hex-native (flat-top, 1 m/hex). Prototype-one-room-first
  approach agreed; not started.

---

## Critical learnings from this session

**Ion is load-bearing (~340 occurrences).** Before changing any damage-type
rule: grep the stripped text for the type, map every occurrence by subsystem,
then reconcile old-model phrases against the new model before touching anything.
The sweep pattern that caught everything:

```python
import re
s = open("/tmp/comp.txt", encoding="utf-8", errors="ignore").read()
hits = [m.start() for m in re.finditer(r"\bion\b", s, re.I)]
```

**Recharge system already existed.** Always grep for the mechanic before
building it from scratch. The flat +4 trickle was in Part I "Blaster-Core
Recharge" — the session work was differentiating it, not creating it.

**Medpack healing rates contain "+N/turn" patterns.** Any automated
recharge-number sweep must exclude `2d+4/turn`, `3d+6/turn`, `1d+2/turn`.
These are kolto medpack HP-over-time values, not recharge rates.

**The +4 trickle survived in "Overcharge & Drain" paragraph** — a straggler
the initial sweep missed. Always run the contradiction sweep before committing,
and design the sweep patterns carefully enough to catch every site.

---

## Constraint reminders (non-exhaustive)

- Standard blaster AD 1 is **deliberate** — do not change.
- `Damage Resistance_Absorbtion` misspelling is **deliberate** — do not fix.
- `Damage Resistance_Absorbtion` misspelling is **deliberate** — do not fix.
- Ship-scale ion (×2 vs shields, 0 hull) is **unchanged** by the ion redesign.
- Ghost-fire crystal is **exclusive to Chatni** — not in forge/loot pool.
- `C.morality` readers still exist in sheet code — leave `.morality` field.
- `mergeChar` does shallow merge only.
- Chatni's Tutaminis is its own Energy Absorption skill — Brawling entries
  are not suspicious.
- "Krysla" never "Kryze" in tool text.
