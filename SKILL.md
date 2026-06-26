---
name: kotor-toolset
description: >-
  Engineering conventions, data model, and workflow for a Star Wars KOTOR-era
  tabletop RPG toolset built on a custom GURPS 4th Edition ruleset. Use this
  whenever working on any of the campaign HTML tools — the character sheet
  (sheet.html), the galaxy map (galaxy-map.html), the galactic-record
  companion, the GM console (KOTOR_GM_Console_v4.html), or the combat
  cheatsheet — or when editing campaign data such as the global C character
  object, Force powers, weapons / armour / shields, skills / traits, the credits
  system, or anything grounded in the compendium ("Star Wars the Old Republic
  GURPS 4E conversion.html"). Apply it for ANY edit, bugfix, feature, data conversion, JSON
  import, or test on these files, even when the request doesn't name the
  conventions explicitly, so the compendium-first rule, the point-cost data
  model, the exact trait-naming catalog, and the Python → node --check →
  Playwright → outputs workflow are followed consistently and silent failures
  are avoided.
---

# KOTOR / GURPS Campaign Toolset

A bespoke, offline-first toolset for running a Star Wars Knights of the Old
Republic / SWTOR-era tabletop campaign on a custom GURPS 4e ruleset. Every
deliverable is a single self-contained HTML file (no external dependencies,
no build step, localStorage persistence). Treat that constraint as load-bearing:
do not introduce CDNs, frameworks, bundlers, or network calls unless the user
explicitly asks to break offline self-containment.

## The files

| File | Role |
|---|---|
| `sheet.html` (~1.7 MB) | The character sheet. Single-file HTML/CSS/vanilla-JS, localStorage; dense aesthetic for laptop + iPad. The largest and most complex tool. Holds the minified `DATA` object and the `window.FORCE_DESC` info panels. |
| `galaxy-map.html` | Interactive hyperspace travel calculator. |
| `galactic-record.html` | In-tool lore / reference companion. |
| `KOTOR_GM_Console_v4.html` | GM-side console / utilities. Script is wrapped in an outer IIFE — top-level consts/functions are closure-private (test via the DOM or a probe injected inside the IIFE, not `page.evaluate` free-var refs). |
| `Combat_Cheatsheet_A3.html` | A3 landscape HTML quick reference. (Also `Combat_Player_Briefs.html`, `ambience-player.html`, `group-storage.html`.) |
| `Star Wars the Old Republic GURPS 4E conversion.html` (~3 MB) | **The authoritative rules document.** Source of truth for all mechanics. Too large to read whole — grep/slice only. |
| `characters/` | `truman.json` (Tylo Dara), `chatni.json` (Chatni), `sekan.json` (Sekan Nightfall). |

## Golden rules

These exist because the toolset is a rules engine, not just a form. Getting the
mechanics subtly wrong is worse than a visible crash — it silently corrupts play.

1. **Compendium-first.** Ground every mechanical or data change in "The Force &
   the Fight" compendium *before* touching sheet data. Where sheet data and the
   compendium disagree, **the compendium wins.** When a value looks wrong, check
   the compendium rather than assuming the sheet is canonical.
2. **Explain mechanical design decisions; don't silently override them.** Several
   deviations from baseline GURPS are deliberate (see Campaign constants). If a
   change would alter one, surface it and explain the consequence — don't quietly
   "fix" it to match vanilla GURPS.
3. **Prefer removal over complexity.** When a tool feels overwhelming, remove the
   feature rather than adding progressive-disclosure layers to hide it. Clean
   deletions over clever scaffolding.
4. **Surgical fixes over rewrites.** Edit the specific lines that are wrong.
   Don't regenerate large blocks or "tidy while you're in there" unless asked.
5. **Diagnose, then propose.** The user wants the actual problem identified and a
   solution proposed, not just literal instruction-following. Honest pushback is
   preferred over agreement.

## Data model — the `C` object

The entire active character is one global mutable object, `C`. It is the single
source of persisted state.

- **Persistence:** `save()` writes `JSON.stringify(C)` to `localStorage` under
  `STORE_KEY = 'kotor_gurps_v2'`. `load()` reads it back. Theme is stored
  separately under `'kotorTheme'`.
- **Schema:** the canonical shape is whatever `blankChar()` returns. That
  function IS the schema — read it before assuming any key exists. Full key list
  and nested shapes are in `references/data-model.md`.
- **Import reconciles against the schema (shallow).** `importChar()` does
  `C = mergeChar(JSON.parse(file))`, and `mergeChar` starts from a full
  `blankChar()` and overlays the file's **top-level** keys
  (`for (k in data) if (data[k]!==undefined) base[k]=data[k]`). Implications:
  > A **missing top-level key is backfilled with its `blankChar()` default** —
  > non-breaking, but you get the default *silently* (a silent-wrong, not a
  > crash): a forgotten key like `force` or `weapons` yields an empty default
  > rather than an error. The live footgun is that the merge is **shallow** — a
  > present-but-*partial* nested object replaces the whole default for that key,
  > so nested sub-keys are **not** backfilled. Build nested objects complete.
  > Some access is guarded (`(C.stances||[])`), but plenty is not (`C.attr[a]`,
  > `C.force.powers`).
  >
  > `load()` (localStorage restore) is a raw `JSON.parse` with no merge, but
  > localStorage is written by the running sheet, so it's already schema-complete.

### Attributes are stored as raw point-costs, not levels

`C.attr` holds **points spent**, not the attribute score. The displayed level is
derived at render time:

```js
ATTR_COST = {ST:10, DX:20, IQ:20, HT:10}
// level = (cost===10) ? round(points/10)+10 : round(points/20)+10
```

So ST/HT cost 10 points per level and DX/IQ cost 20. **HT at 10/level is the
easy one to get wrong** when reverse-engineering a character from another source —
don't assume HT shares DX/IQ's 20/level cost. To store "HT 12", write
`C.attr.HT = 20` (two levels above 10 × 10 pts). Secondary characteristics live
under `C.sec` and follow GURPS costing relative to their base attribute.

### Trait names must match the internal catalog *exactly*

Traits are matched by literal string against the catalog baked into `DATA`. A
near-miss silently does nothing. Two specifics that bite:

- Underscored variant names, e.g. `Damage Resistance_Normal`,
  `Damage Resistance_Force`, `Damage Resistance_Reflection`.
- **The catalog contains a misspelling: `Damage Resistance_Absorbtion`**
  (not "Absorption"). Match the misspelling — do not correct it in code that
  looks up the trait, or the lookup fails. (If the user wants the catalog string
  itself fixed, that's a separate, deliberate change touching every reference.)

When in doubt about a trait, skill, weapon, or species name, grep the actual file
for the exact string rather than typing it from memory.

## Data formats: `DATA` vs `FORCE_POWERS`

The two big embedded datasets use **different JSON styles**, so extraction /
edit regexes differ:

- `const DATA={...}` — **minified** JSON, single line, no spaces after colons:
  `{"weapons":[{"cat":"Knife",...`
- `const FORCE_POWERS=[...]` — **spaced** JSON: `[{"name": "Force Torrent",
  "skill": "ST (blade)", ...`

A regex tuned for one will miss the other. Confirm which dataset you're editing
and match its spacing.

## Working session workflow

The established, reliable loop — follow it for every change:

1. **Copy to the working dir first.** `/mnt/project/` (and any uploaded copy) is
   **read-only** and goes **stale after each export**. Work in `/home/claude/`.
2. **Edit surgically** with Python `str_replace`-style scripts for precise edits,
   or extraction scripts for data work. For multi-line test bodies, use a heredoc:
   ```bash
   cat > t.js << 'EOF'
   ...test code...
   EOF
   ```
3. **Syntax-check:** `node --check file.html` is not valid (it's HTML), so extract
   the script or run `node --check` on a `.js` copy of the relevant block.
   Always verify JS parses before functional testing.
4. **Functionally test** with Playwright (headless Chromium): load the file,
   exercise the changed path, assert on rendered output / `C` state.
5. **Ship** by committing and pushing to `main` (the repo is the source of
   truth), then copy the finished file to `/mnt/user-data/outputs/` and present
   it. The `/mnt/project/` mount goes stale after edits — rely on the repo.

The compendium is edited like any other file — clone, surgical patch, verify,
commit, push (see the GitHub workflow below). It is too large to read whole, so
grep/slice to locate and view a tight range; never read it end-to-end.

## GitHub read/write workflow

The repo `Recoson/Star-wars-GURPS-campaign` (branch `main`) is the source of
truth. A fine-grained PAT scoped to this repo lives in the **project
instructions** — it grants full clone/push via git over HTTPS, which bypasses
the GitHub MCP connector's ~50 KB write ceiling entirely.

- **Reads:** prefer a fresh `git clone --depth 1` at session start over curling
  individual raw files or trusting `/mnt/project/` mounts (both go stale).
  The MCP connector remains fine for quick single-file reads.
- **Writes:** edit in `/home/claude/<clone>/`, run the verify loop above, then
  commit and push. **Pushing to `main` is the default final ship step for every
  session that edits any project file** — not just large ones. The repo is the
  source of truth; an update that only lands in `/mnt/user-data/outputs/` is
  not shipped. Still copy final deliverables to `/mnt/user-data/outputs/` so
  they're visible in-chat.
- **`main` moves under you — parallel sessions push constantly.** `git fetch` +
  `git rebase origin/main` before every push. Conflicts on the giant minified
  lines aren't hand-mergeable: `git rebase --abort` → `git reset --hard
  origin/main` → re-apply the patch fresh → push. Re-check current state before
  re-applying — another session may have already done the task.
- **Claim your workstream in `CONTEXT.md`.** When starting a multi-batch job,
  add a named, status-tagged line to the in-flight section (e.g. "*power
  adjudication — IN PROGRESS, batch N*") so a parallel session sees the claim
  before duplicating it. Read that section first; refresh it when you finish.
- **Run `python3 check.py` before every push.** It asserts the structural
  invariants (per-power statgrid fields + At-the-table block, unique headers,
  div balance, FORCE_DESC panels ⊆ real powers, JSON schema-key coverage) and
  the golden attribute-derivation math. Green-with-warnings is fine; a FAIL means
  don't push. It pins no magic numbers, so it survives the growing corpus.

### Token hygiene — never echo the PAT

The raw token string must appear **zero times** in visible output (responses,
command text, logs). Streaming a credential trips secret-scanning and causes
the chat to pause/stall, and every repetition widens transcript exposure.

1. At session start, write it to a scratch env file **once** via heredoc, with
   the value taken from project instructions — never retype it into later
   commands:
   ```bash
   cat > /home/claude/.ghtoken << 'EOF'
   <token from project instructions>
   EOF
   ```
2. Clone with output suppressed, then immediately strip the token from the
   remote so it never reappears in `git remote -v`, push output, or errors:
   ```bash
   TOKEN=$(cat /home/claude/.ghtoken)
   git clone --depth 1 "https://x-access-token:${TOKEN}@github.com/Recoson/Star-wars-GURPS-campaign.git" repo > /dev/null 2>&1
   cd repo
   git remote set-url origin https://github.com/Recoson/Star-wars-GURPS-campaign.git
   git config credential.helper "store --file=/home/claude/.gitcred"
   echo "https://x-access-token:${TOKEN}@github.com" > /home/claude/.gitcred
   ```
3. From then on, plain `git pull` / `git push` work with no token in any
   command. Reference `$TOKEN` only inside command substitution if an API call
   needs it directly; never `echo` it or include it in a curl line shown in
   output.

## Campaign constants (deliberate design — do not "correct")

The compendium is the source of truth for every rule value; this table only flags
*deliberate deviations* from baseline GURPS so they aren't "corrected" back. Treat
the values below as reminders of intent — when one matters to a task, confirm the
live number in the compendium rather than trusting this table.

| Constant | Value | Why it matters |
|---|---|---|
| Scale | **1 metre = 1 hex** | House convention; all ranges/areas assume it. |
| Standard blaster armour divisor | **AD (1.5)** | *Intentional* deviation from baseline GURPS, creating hard armour-penetration tiers (a rock-paper-scissors dynamic, not an attrition curve). The compendium is authoritative for the live value; heavy-blaster-vs-energy-weave is kept at AD 1 as a deliberate sub-exception. |
| Morality / alignment mechanics | **Removed** from tool mechanics; Force power system fully preserved | The removal was at the mechanics/UI layer. Note: the data schema still *seeds* `force.morality / conflict / darkSurgeLog` — see Known quirks. |
| Damage types | lightsaber, disruptor, ion treated as **distinct** types | Combat resolver branches on these. |
| Hyperdrive (galaxy-crossing baseline) | ~24 h @ Class 0.5 · ~48 h @ Class 1.0 · ~96 h @ Class 2.0 | Class labels in-tool: 0.5 = elite courier/Jedi scout, 1.0 = military/fine freighter, 2.0 = standard freighter. The Galaxy Map's own formula is authoritative — reconfirm there before changing. |
| Hyperfuel | ~50 credits / unit | Used by the refuelling integration. |

## Known quirks worth flagging (observed in the current sheet)

Mention these when relevant; don't auto-fix without asking:

- **Duplicate key in `blankChar()`:** `credits:0, creditLog:[]` appears twice in
  the returned object. Harmless (the later literal wins, same values) but it's
  dead duplication from the credits-system addition — a one-line tidy if wanted.
- **Vestigial morality fields:** `blankChar()` still seeds
  `force:{ morality:50, conflict:0, darkSurgeLog:[] }` even though
  morality/alignment mechanics were removed. Decide deliberately: strip for
  cleanliness, or keep for backward-compatible imports of older characters.

## Deeper reference

For the full `blankChar()` schema (every top-level key and nested shape), the
exact persistence/import/attribute-math code, and conversion notes for building
a JSON import from another source (e.g. an Excel character), read
`references/data-model.md`.
