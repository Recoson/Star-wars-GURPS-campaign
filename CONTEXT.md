# CONTEXT.md — Dara Dara Campaign Toolset · live working context

**Read this top-to-bottom at the start of a fresh chat, then resume the grind with no further confirmation.**
This file is the churny/volatile companion to the durable Project Instructions and to
`/mnt/skills/user/kotor-toolset/SKILL.md` (engineering conventions, loads on code sessions).
Refresh it at the end of each session. Don't duplicate facts that already live in those two; this
file is *current task state + the exact mechanics of the job in flight*.

---

## 0. THE JOB IN ONE LINE

Per-power **"full adjudication" pass** over every Force power in the compendium: add a 3-field
statgrid extension (**Upkeep / Hands / Move**) plus an **"At the table."** ruling block to each of
the **192** powers, authored against the canonical schema. **COMPLETE — all 192 done and pushed**
(compendium commit `81d843a`). **Since then the 20 Minor Traditions sub-tradition abilities were also
converted into full power blocks** (compendium `c2334a0`) — corpus is now **212 powers**, every one
with the statgrid triple + At-the-table. **The sheet `window.FORCE_DESC` info panels are now fully
synced to the compendium** (latest sheet commit): all 204 in-compendium catalogue powers covered. The
pass is finished; §11 holds the only open items.

James's standing instruction is **"go nuts" / "keep going"** = grind continuously, batch after
batch, no pausing for review, honest pushback wanted on any ruling that breaks balance or the
action economy. Ship-then-correct.

---

## 1. REPO, ENVIRONMENT, GIT/PAT WORKFLOW (reuse verbatim every session)

- Repo: **`Recoson/Star-wars-GURPS-campaign`**, branch **`main`**, cloned at **`/home/claude/repo`**.
  The **repo is the source of truth**; **`git push origin main` is the default end step** of any
  edit session, alongside copying the touched file to `/mnt/user-data/outputs/`.
- **PAT** lives at `/home/claude/.ghtoken` (chmod 600); credential helper at `/home/claude/.gitcred`.
  Identity: `git config user.name "Recoson"`, `user.email "recoson@users.noreply.github.com"`.
  The **GitHub MCP connector is read-only (403)** — never use it for writes; all writes go through
  git-over-HTTPS with the token-authed remote.
- **NEVER echo the token.** Mask **all** git output through:
  ```
  sed -E 's/github_pat_[A-Za-z0-9_]+/***/g; s#x-access-token:[^@]*@#x-access-token:***@#g'
  ```
- **origin/main advances often (parallel sessions touch it concurrently).** Every push sequence:
  ```
  git fetch origin main
  git rebase origin/main          # resolve, then continue
  git push origin main            # masked
  ```
  If a rebase conflicts on the giant minified DATA line or a long HTML line:
  `git rebase --abort` → `git reset --hard origin/main` → **re-apply the Python patch fresh** → push.
  (Conflicts are not merge-able by hand on those lines; always re-derive from current origin.)
- Sandbox resets between sessions: `/home/claude/batch*.py` scripts and `/tmp` scratch do **not**
  persist. The repo clone, the schema doc, and this file **do** (they're committed). Re-clone if
  `/home/claude/repo` is missing.
- Optional fast-grep helper: stripped compendium text at `/tmp/comp.txt` — rebuild before grepping:
  ```
  python3 -c "import re; s=open('Star Wars the Old Republic GURPS 4E conversion.html',encoding='utf-8',errors='ignore').read(); s=re.sub(r'<[^>]+>',' ',s); s=re.sub(r'\s+',' ',s); open('/tmp/comp.txt','w').write(s)"
  ```

---

## 2. CONTEXT BUDGET — non-negotiable

Chat window ≈ 200K tokens. **The compendium is ≈700K tokens read whole and `sheet.html` ≈280K —
reading either in full OVERFLOWS THE WINDOW AND ENDS THE CHAT.**

- **NEVER `view`/`cat` a large file whole.** `grep`/`sed -n`/Python-slice to locate, then `view`
  a tight line range. Targeted reads only.
- Per-power recon (the read step of each batch) pulls *only* the statgrid + a few body `<p>`
  excerpts for the powers in that batch, ASCII-cleaned, via a small Python script — never the
  surrounding document.
- Use **Python** (not `cut`/`fmt`/`head -c`) to slice UTF-8 so multibyte chars don't get severed.

---

## 3. THE COMPENDIUM FILE & POWER MARKUP

- File: **`Star Wars the Old Republic GURPS 4E conversion.html`** (single-file HTML, vanilla JS,
  offline-first, the SOURCE OF TRUTH for all mechanics).
- Each power is:
  ```
  <h4 class="power-name">NAME</h4>
  <div class="statgrid"> … <span class="stat-k">KEY</span><span class="stat-v">VAL</span> … </div>
  <div class="power-body"> … <p>…</p> … </div>
  ```
- **Sections** are `<h1>`/`<h2>` headers. The witch tradition ("The Inscribed Voice") groups its
  powers under a run of **H1 sub-banners** (The First Faces, The Hexing Hand, The Reach Beyond,
  The Greater Workings, The Final Inscriptions) with intro prose between each banner and its first
  power — *not* a single H2. The Dark Side lives under H1 "THE UNCHAINED" → H2 "The Dark Side".
- **Minor Traditions are now CONVERTED** (commit `c2334a0`): all 20 sub-tradition abilities
  (Iktotchi 6 / Baran Do 7 / Zeltron 7) were rewritten from compact `<p class="rule">` form into full
  `power-name` h4 + statgrid (with an added **Tier** field) + Upkeep/Hands/Move + At-the-table blocks,
  taking the corpus to **212**. **The Nine Forms and Battle Master Signatures still use different
  markup and remain OUT OF SCOPE.** The 8 **Form-Neutral Techniques** are power-name h4s (#185–192).

### 3a. What we add to each power (output format, per schema §3)
1. Into the statgrid, **before the statgrid's own closing `</div>`** (found by div-balance from
   `<div class="statgrid">`), three new key/value pairs in this exact shape and order:
   ```
   <span class="stat-k">Upkeep</span><span class="stat-v">…</span>
   <span class="stat-k">Hands</span><span class="stat-v">…</span>
   <span class="stat-k">Move</span><span class="stat-v">…</span>
   ```
2. An **At-the-table** block appended as the **last `</p>` before the power's body boundary**:
   ```
   <p class="warn"><b>At the table.</b> …</p>
   ```
   Boundary = min position of {next `<h4 class="power-name">`, next `<h2`, next `<h1`} after the
   statgrid. The block is inserted right after the final `</p>` inside that range.
- **ASCII-safe text only** in injected strings: hyphen `-` for minus, `x` for ×, spell out "half",
  avoid `÷` (write "divided by" or restructure). Curly apostrophes in power *names* must be matched
  exactly when anchoring (e.g. `Mother's Calling`, `Crown's Compulsion` use the right glyph — copy
  from the live file, don't retype).

### 3b. KNOWN HAZARD — block placement around H1 sub-banners
Commit **`ad900d0`** fixed 16 At-the-table blocks that landed in *trailing band-intro prose*: when a
power is the **last in its sub-section** and is followed by an H1 sub-banner + intro `<p>`s, the
naive "last `</p>` before boundary" can mis-place. After any batch that includes a section's final
power, **verify each new block sits inside its own power-body**, not in the next banner's intro.
(`git show ad900d0` for the fix pattern.)

---

## 4. THE SCHEMA — canonical rulings (authoritative doc in repo)

Full spec: **`FORCE_POWER_RULING_SCHEMA.md`** in the repo root (≈12.9 KB). It is the gate the whole
pass runs against. The load-bearing locked rulings, summarized so a fresh session needn't re-read
the compendium to apply them:

**Maneuver → advantages**
- **Concentrate** → Compartmentalized Mind (CM grants a free 2nd Concentrate) **+** Altered Time
  Sense. **NEVER** Extra Attack.
- **Attack** → Extra Attack.
- **Rapid Strike = MELEE only** (Force-empowered or saber-delivered strikes). Ranged/projected
  powers do **not** get Rapid Strike.

**Sustain models** — every sustained power MUST state a duration cap and/or an FP-refresh rule. Four
canonical models:
- (a) **FP/turn** — pay FP each turn to keep it up.
- (b) **Concentrate-only, no-FP, time-capped** — holds a Concentrate each turn, ends at a stated cap.
- (c) **free turn-to-turn but re-pay FP per interval** (e.g. re-drain every minute). Used for the
  sensory powers (Force Sense, Force Sense (Grey), etc.): activate with a 1-second Concentrate, then
  hold a Concentrate each turn **and** re-pay FP every minute. Holds your Concentrate (so CM is what
  frees a 2nd power).
- (d) **latched** — raise once with a Concentrate, then runs **free** (no maneuver, no FP, no
  Will-roll-on-hit), **does NOT hold your Concentrate**, ends only on a stated trigger. Established
  by Tempered Blade in The Bonded Blade.

**Interruption roll = Will.** Damage/distraction forces a **Will** roll or the effect ends / steps
down.

**Range.** Every power states a default range. FP→range scales at **+1 hex/FP** where sensible.
- **Force Push / Force Pull TK-reach extension** shipped as a **PROPOSED** falloff: **+2 FP and
  −2 to hit per extra 8 hexes beyond the base 8.** **AWAITING JAMES CONFIRM** (see §6).

**Hands.** Values are `0` / `1` / `2` / `the blade`.
- **Saber-hand gate:** a hand-projected power may be used with a **lit saber in the same hand** if
  Lightsaber/relevant-Form skill ≥ (Force attribute + 6), applied per-power. Where the source states
  a flat threshold, use it verbatim: **Electric Judgment** = "skill 22+"; **Hollow the Wound** =
  "skill 20+".

**Movement axis (the "Move" field):** `Free` / `Step-only` / `Is-movement` / `Enhanced`.
- Movement powers consume the **base maneuver** (Move/Instant), **not** a Concentrate — *except*
  sustained movement buffs (e.g. **Force Speed** activates/sustains on a Concentrate).
- **Force Speed:** Move cap is **+4 per FP/turn** (CONFIRMED, raised from +2); defense bonus stays
  **+2**. Both the stat-sum and the effect text were edited to match.

**1-second rule.** 1 combat turn = 1 second. Anything costing minutes+ is out-of-combat. Meditative
/ ritual modes are time-gated, out-of-combat, and grant **no extra FP**.

**The At-the-table block always closes** by stating: Extra-Attack / CM / Rapid-Strike applicability,
the FP-to-range behaviour, and whether a meditative mode exists.

**Bucket → Upkeep templates (schema §4).** Each power is classified to one bucket whose Upkeep
template it follows: Concentrate-one-shot · Attack · Ritual · Concentrate-sustained · Reactive ·
Free · Instant · Passive · Stored · Attack-or-channel.

**Unique exceptions already locked (do not "regularize"):**
- **Force Grip** and **Force Whirlwind**: hard-forbid running **any** other concentration power
  simultaneously — **even with Compartmentalized Mind**. (The one place CM does *not* free a 2nd
  concentration power.)
- **Tutaminis** is its **own Energy Absorption skill** (reactive, bare-hand energy defence); the old
  Brawling-bonus stand-in was dropped — never flag a Brawling entry as suspicious on that basis.
- **Consume the Spark** = FP 0 (already corrected in source).
- Death-rite powers (**Joining the Force**, **Becoming**) sit *outside* the action economy.

---

## 5. THE BATCH MACHINE

Each batch = one cohesive group of powers (a sub-section or ~9–10 powers). Steps:

**(1) Recon read** — small Python that, for the batch's power names only, prints the current
statgrid (stat-k/stat-v) and a few body `<p>` excerpts, ASCII-cleaned. No surrounding document.

**(2) Author** — write Upkeep/Hands/Move + At-the-table for each power per the schema. Classify to a
bucket; apply the locked global rulings; surface any un-defaultable call to James inline.

**(3) Inject** — the reused injection script (saved each time as `/home/claude/batchNN.py`). The
mechanics are stable; only the `P={…}` dict changes. Exact mechanics:

```python
import io,re,sys
FN="Star Wars the Old Republic GURPS 4E conversion.html"
s=io.open(FN,encoding="utf-8").read()
P={
 # "Power Name": {"up":"…","hands":"…","move":"…","table":"…"}, …
}
inserts=[]
for name,d in P.items():
    h=s.find('<h4 class="power-name">%s</h4>'%name)
    if h<0 or s.count('<h4 class="power-name">%s</h4>'%name)!=1: sys.exit("anchor: "+name)
    sg=s.find('<div class="statgrid">',h); depth=0;i=sg;sgc=-1
    while i<len(s):
        if s.startswith('<div',i):depth+=1;i+=4;continue
        if s.startswith('</div>',i):
            depth-=1
            if depth==0:sgc=i;break
            i+=6;continue
        i+=1
    if sgc<0: sys.exit("sg: "+name)
    inserts.append((sgc,f'<span class="stat-k">Upkeep</span><span class="stat-v">{d["up"]}</span><span class="stat-k">Hands</span><span class="stat-v">{d["hands"]}</span><span class="stat-k">Move</span><span class="stat-v">{d["move"]}</span>'))
    cands=[s.find('<h4 class="power-name">',sgc+6)]
    for tag in ['<h2','<h1']:
        p=s.find(tag,sgc+6)
        if p>=0: cands.append(p)
    bound=min(c for c in cands if c>=0)
    lastp=s[sgc:bound].rfind('</p>')
    inserts.append((sgc+lastp+4,f'<p class="warn"><b>At the table.</b> {d["table"]}</p>'))
for pos,text in sorted(inserts,key=lambda x:-x[0]): s=s[:pos]+text+s[pos:]
io.open(FN,"w",encoding="utf-8").write(s)
print(f"injected {len(P)} ({len(inserts)} insertions)")
```

The script is **assertion-guarded** (anchor must exist exactly once; statgrid must div-balance) and
**insertion-only** — it never rewrites existing prose. Run it from inside `/home/claude/repo`.

**(4) Verify (scope to the change — this is an HTML edit, so):**
- Every batch power gained the **3 new stat-k fields + 1 At-the-table block** (grep counts).
- **Tag balance:** net change per batch is **0 unclosed divs**; the long-standing **Δ1 unclosed
  `<p>` and `<span>` in the document HEAD is a PRE-EXISTING source quirk** (present before this work,
  not from these edits, doesn't affect rendering). Confirm the delta is *unchanged*, not zero.
- `node --check` on the **2 extracted inline `<script>` blocks** → 0 failures. Extract with
  `re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', html, re.S)`.
- For section-final powers, eyeball that the new block is **inside its power-body**, not a trailing
  band-intro (the `ad900d0` hazard, §3b).

**(5) Push** — `git fetch origin main` → `git rebase origin/main` → `git push origin main` (masked)
→ `cp "<file>" /mnt/user-data/outputs/` (+ `present_files` when surfacing to chat).

Commit message convention: `Power adjudication batch NN (<section> X/Y): N powers`.

---

## 6. OPEN FLAGS / PENDING JAMES DECISIONS (carry forward, surface when relevant)

- **[RESOLVED — slim keeps Upkeep] Block-slimming pass.** `631a97f`'s exemplar *dropped* Force Empathy's Upkeep field, broke the corpus-wide Upkeep/Hands/Move invariant, and reddened CI. `04e3b06` corrected it: re-slims the block (no top stat-sum; effect leads with the summary) while **keeping Upkeep** (moved to its own coloured line). Contract intact, `check.py` unaffected — the "drop Upkeep / relax the invariant" fork is dead. Still open but now **contract-safe**: whether to roll the cosmetic slim across the rest of the corpus. Force Empathy is the lone exemplar so far — bless a wider pass before doing it en masse, and any slim MUST retain Upkeep/Hands/Move or CI re-reds.

- **Force Push / Force Pull range-falloff rate** — shipped PROPOSED as **+2 FP and −2 to hit per
  +8 hexes beyond base 8**. James has not confirmed. Flag for ratification, don't silently re-tune.
- **Saber-hand-gate per-power eligibility** — default rule applied (ranged hand-projected powers
  gate at skill ≥ Force attr + 6; flat thresholds where the source states one). James to confirm the
  per-power eligibility list.
- **Force Grip & Force Whirlwind** are the only CM exceptions (no 2nd concentration power at all).
  Flagged and locked. **Force Choke is NOT an exception (James ruled, this session):** it uses the
  basic sustained-Concentrate ruling — holds your Concentrate, CM frees a 2nd power. Its source line
  "cannot use other concentration powers simultaneously" is read as the ordinary no-CM default; the
  Choke Upkeep + At-the-table in compendium and sheet were corrected to match.
- **Standard-blaster AD (RESOLVED, James ruled this session):** canon is **AD 1.5** (already folded
  through the compendium prose + both weapon stat tables). The stale "standard blasters AD 1" line is
  to be **dropped from the Project Instructions** (James's panel — can't edit from here). Heavy-
  blaster-vs-energy-weave stays at 3/2 → AD 1 as a deliberate exception.
- **Pre-existing HEAD quirk:** Δ1 unclosed `<p>` and `<span>` in the document head — not ours.

---

## 7. PROGRESS LEDGER — 212 POWERS · COMPENDIUM COMPLETE · SHEET FORCE_DESC FULLY SYNCED (204 panels)

**ALL SECTIONS COMPLETE (every batch pushed).** Final tally below; recompute command retained.

- The Bonded Blade (4) · The Light Side (28) · The Common Force (28) · The Concordance of Feathers (26)
  · The Hollowing (34) · The Inscribed Voice / witch tradition — all four sub-books (The First Faces 7,
  The Hexing Hand 7, The Reach Beyond 5, The Greater Workings 6, The Final Inscriptions 6) · **The Dark
  Side (33)** · **Form-Neutral Techniques (8)**. Total = **192**, + **Minor Traditions 20** (Iktotchi 6 / Baran Do 7 / Zeltron 7, converted in `c2334a0`) = **212**.

- Final batches this run: 18 (Greater Workings finish), 19 (Final Inscriptions → witch tradition complete),
  20–23 (The Dark Side 33/33), 24 (Form-Neutral 8/8 → 192/192, commit `81d843a`).

- **Whole-corpus integrity check passed:** **212** `power-name` h4s, each with exactly one Upkeep field and one
  At-the-table block; zero misses, zero duplicates.

**§7 SHEET FORCE_DESC — FULLY SYNCED TO THE COMPENDIUM.** Originally 179 of 192 mirrored (`d0c54f3`).
Now **rebuilt to 204 entries** = every in-compendium catalogue power: the 20 Minor Traditions abilities
mirrored, the 5 previously-absent powers (Force Torrent / Force Vessel / Blade Velocity / Tempered Blade /
Mist-Fold) added, and all 40 stale panels re-synced to the compendium — including mechanical drift such as
Force Speed's +2→+4 cap, and a voice genericisation she/Chatni → "you" (the shared multi-PC sheet should
read second-person). Transform = extract statgrid→At-the-table, strip the `power-body` wrapper, normalise
inter-tag whitespace, escape via JSON. Verified: object evals to **204** keys, `node --check` 0 fails,
0 U+FFFD, and **Playwright** confirms the page loads error-free and new/updated panels open. The 8 Form-
Neutral saber techniques and other compendium-only powers are not in the sheet catalogue, so need no panel.

**Recompute progress any time** with:
```
grep -o '<span class="stat-k">Upkeep</span>' "Star Wars the Old Republic GURPS 4E conversion.html" | wc -l
```
(equals the number of completed powers; total power headers = `grep -o '<h4 class="power-name">' … | wc -l`).

---

## 8. HARD CAMPAIGN CONSTRAINTS (always in force)

- **Compendium wins ALL data disputes.** Verify any trait/skill/stat against compendium prose before
  editing the sheet or console; flag and explain any deliberate deviation.
- Self-contained **offline-first HTML, vanilla JS only, no external deps**, localStorage
  persistence, must run on **GitHub Pages + iPad**. Dark aesthetic: void bg, gold + holo-blue,
  Cinzel + EB Garamond.
- **1 metre = 1 hex.** Lightsaber / disruptor / ion are **distinct** damage types.
- **Morality/alignment removed from the tool/UI layer**, but `C.morality` readers still exist in
  code — **leave them**.
- **Do NOT "fix" the deliberate misspelling `Damage Resistance_Absorbtion`** in the catalog.
- **Ghost-fire / Ghostfire crystal** is exclusive to Chatni — must not enter the forge/loot pool.
- Edits are **surgical / insertion-only**; prefer removal over layered workarounds; never rewrite
  working code wholesale.

---

## 9. KEY FILES

- `Star Wars the Old Republic GURPS 4E conversion.html` — compendium, SOURCE OF TRUTH (~3 MB; never
  read whole). **Active edit target of this pass.**
- `sheet.html` — character sheet (~1.49 MB; minified `DATA` object). **§7 target after the pass.**
- `KOTOR_GM_Console_v4.html` — GM console; **script wrapped in an outer IIFE** (top-level
  const/function are closure-private → verify by injecting a probe inside the IIFE or driving the
  DOM, never `page.evaluate` free-var refs).
- `Combat_Cheatsheet_A3.html` — A3 combat reference (per-section clip + per-`.col .sec` bottom-vs-`wpn`
  collision checks required after any edit; page 2 can't exceed 6.6pt without a 4→5 page split).
- supporting: `galaxy-map.html`, `galactic-record.html`, `Combat_Player_Briefs*`, `ambience-player.html`,
  `group-storage.html`.
- `characters/truman.json` (Tylo Dara) · `characters/chatni.json` (Chatni) · `characters/sekan.json`
  (Sekan Nightfall). JSON edits = `json.loads` parse-check only, no Playwright.
- `FORCE_POWER_RULING_SCHEMA.md` — the schema this pass runs against.
- `/mnt/skills/user/kotor-toolset/SKILL.md` — engineering conventions (golden rules).

---

## 10. ALREADY-SHIPPED PRIOR PHASES (context only — in git history, do not redo)

- **Armour variety expansion:** 7 new armours into sheet + compendium, Monte-Carlo balance-validated
  (kinetic-strong/energy-weak vs energy-tough split).
- **Blaster AD 1 → 1.5 fold-through** across compendium prose + both weapon stat tables (left
  heavy-blaster-vs-energy-weave at 3/2 → AD 1). Instructions-line drift resolved (see §6): AD 1.5 is
  canonical; the "AD 1" line is dropped from the Project Instructions.
- **Per-cell recharge differentiation** (+2 blaster ladder replacing the flat +4/turn trickle) and
  **ion magnetic-explosion redefinition** across compendium, sheet, console, cheatsheet
  (commit `3e29e5c` / handoff `08cc93f`).
- **Vehicles hardpoint-budget enforcement** + budget recalibration (commit `a2df03a`, a parallel
  session).

---

## 11. IMMEDIATE NEXT STEP

**SHIP-BUILDER WORKSTREAM (separate from the Force/RAW work below).** A full vehicle/ship-builder overhaul
shipped this session — size-first mounts, swivel+location firing arcs, compendium range bands + warhead
flight, hardpoints-from-hull, free-form per-part mods, a frame-scale part filter, 3 capital frames, and
frame-driven base HP/DR/mass/econ. Full detail in the latest dated entry below. (Capital-frame numbers ratified by James; sensors/cargo/crew
now in the part-mod stat dropdown.) Remaining ship-builder items are minor — see the dated entry.

**The adjudication pass, the Minor Traditions conversion, and the full sheet FORCE_DESC sync are all
COMPLETE and pushed.** No batch work remains. Open items, in priority order:

1. **PAT exposure (security) — still open.** A live `github_pat_…` was pasted in plaintext and
   proposed for the durable Project Instructions. **Rotate it**, and keep the literal token out of any
   saved instructions (paste per-session instead).

_Done this session:_ Force Guidance cap ½→¼ of the assisted skill's governing attribute (`faaaa16`); all
20 Minor Traditions abilities converted to full power blocks (`c2334a0`); sheet sub-tradition **dropdown
selector** (Iktotchi/Baran Do/Zeltron, race-titled, smooth learn/unlearn, Playwright-verified) (`0aa69cd`);
FORCE_DESC mirror for the 20 (`7142457`); and the full FORCE_DESC re-sync to 204 panels. **Blade techniques recategorised as Common Force** in both files: the compendium “Form-Neutral Techniques” section retitled “Common Force — Blade Techniques” (intro reframed, Trakata carved out under a new “The Unorthodox Technique” h3); the sheet’s standalone technique table relabelled “Common Force — Blade Techniques” with Trakata split into its own “Unorthodox Technique” section (scope-safe inline-map split, no global helper — slotBadge is nested in the render fn). The 11 sheet FORCE_TECHNIQUES (Bolt Deflection, Saber Throw, Saber Bind, Saber Bash, Sokan, Blade Barrier, Guided Strike, Sundering Strike, Saber Split, Force Cadence) are now Common Force; Trakata alone is Unorthodox. NB: these techniques live in their own non-tiered system (FORCE_TECHNIQUES / the compendium Form-Neutral section), NOT in FORCE_POWERS. **Now PHYSICALLY MERGED** (per James): the 7 existing + 3 newly-authored techniques (Bolt Deflection, Saber Bash, Sokan) were moved INTO the compendium’s “The Common Force” section (power-name h4 212→215) and now render under the **Common Force book** in the sheet (via `forceBookChecklist`, with `const SLOT_BADGE` + `slotBadge` hoisted to global so the technique table can render outside renderStances; `techRow` is now a global helper). Trakata alone stays in its own “The Unorthodox Technique” section (compendium) / the Stances tab (sheet). The 3 new blocks’ mechanics are AUTHORED best-effort: Saber Bash 4 FP + ST Quick Contest is from its sheet desc; Bolt Deflection and Sokan (2 FP) were Claude’s derivation. **Cross-referenced against the Nine Forms, then balance-tuned to James’ spec:** Bolt Deflection parries bolts at full Lightsaber (NO fake ranged-Parry penalty) and reflects on margin 3+, but BASELINE reflect is capped at ONCE PER TURN — under sustained fire the cumulative -4 means you parry to survive rather than bounce everything back. Forms lift this: Soresu raises the deflect-count (survive the storm); **Shien removes the once-per-turn reflect cap** (Initiate core buff) and stays the best at throwing bolts back (+reflected-attack, Riposte, Returned Volley). Saber Bash knockback uses hexes (cf. Force Push). **Sokan fully repurposed** — was an OP half-Move-and-attack-at-full-skill; now a cheap 1-FP Acrobatics stance: fight from crouch/kneel/prone with no posture penalty + free posture changes, NO movement (that is Ataru). NB naming collision: Ataru already has a built-in “Sokan” terrain-as-weapon perk in SABER_FORMS — flagged to James (rename standalone / remove / leave). James to sanity-check balance.

**Design principle (James, firm): NEVER fully negate a core mechanic.** Flat bonuses and partial reductions are fine; total negation makes one option strictly dominant. Applied: Soresu’s core-buff “parry 3/4/5/7/unlimited bolts before cumulative penalties” was REMOVED (kept the flat +2/+2/+3/+4/+5 Parry — which by itself still rides out the cumulative −2 Weapon-Master penalty longer, so Soresu still ‘parries more for longer’). All lightsaber users already have Weapon Master, so the multi-parry penalty is already halved to −2/parry — Soresu also zeroing it was double-dipping into invulnerability. Iron Ward softened: “no multi-defense penalty, regardless of facing” → realistic guarding (multi-parry penalty accumulates; front/side arc only, side −2; no rear; its reflect now subject to the 1/turn cap, which also makes ‘Shien always reflects more’ airtight). Both files synced (compendium + sheet SABER_FORMS). STILL-OPEN negations flagged for James: Makashi “negates the standard −1 Lightsaber parry penalty” (swap to “+1 Parry vs lightsabers”?), Shien Returned Volley “no multiple-attack penalty” (offensive signature — keep, or cap to Weapon-Master −2 Rapid Strike?).

**FORMS REWORK DONE (“flat damage is dead, skill is 30+” pass).** Lightsaber = 8d+8 AD 5 (avg ~36) — flat +1/+2 damage is noise, −2-damage flaws are toothless; at skill 30+ small to-hit is marginal. Levers that bite: target-defence penalties, armour divisors, knockback (hexes), stagger, prone, action economy. Done across compendium + sheet SABER_FORMS: **Djem So** rebuilt from “+N damage on hits/counters” → KNOCKBACK (1 hex +1 per 3 pts the attack beats the defence; a clean hit clears a Step and forces a DX/Acrobatics roll or prone) + STAGGER (−1/−2/−3 to next defence); counter keeps action economy + to-hit progression. **Shien Riposte** “+N damage” → Riposted foe defends at −1/−2/−3. **Soresu flaw** dead “−2 damage” → “No All-Out Attack of any type; −2 to hit”. **Makashi** phantom “−1 lightsaber parry penalty” removed (undefined; lightsaber Parry is 0F). Negations floored, not erased: **Shii-Cho T5** “negated entirely” → “−6/extra target, min −1”; **Jar'Kai T5** “cannot be flanked” → “defend vs flank/rear at −2”; **double-blade** “two full-skill strikes” → “second strike at −2, may sweep a different adjacent target” + flank/rear at −2. **STEP RULING** (drives Djem So knockback): extra steps come from All-Out Attack (Determined = “step, or two steps, 2nd at −2 hit”), NOT high Move; one step per maneuver (two via AoA); there is no “attack-step-attack-step”. Forms already sound (Ataru −defence, Juyo/Vaapad armour-divisor + Overwhelming Tempo, Niman Force-follow-up) left untouched. Sheet has no double-blade FORM (saberstaff is a weapon only) — fixed compendium-side only.

_Earlier-resolved:_ Force Choke uses the basic ruling (not a CM exception); standard-blaster AD is 1.5 and
the "AD 1" line is to be dropped from the Project Instructions (see §6).

Flagged to James: the FORCE_DESC re-sync genericised ~30 panels from third-person (she/Chatni) to the
compendium's second-person "you" — correct for a shared multi-PC sheet, but if any of that personalisation
was deliberate, say the word and it can be selectively restored. Otherwise the toolset is current.

---

## 2026-06-26 — Djem So redesign + start of GURPS-4e-RAW basics audit (commit 38669c4)

**Djem So reworked (compendium + sheet):** the push-away knockback contradicted the form's constant-aggression identity. Replaced with **Relentless Advance** — the blow still drives the foe back 1 hex (+1 per 3 pts of success; 2+ hexes = DX/Acrobatics roll or prone) and staggers (−1→−3 by tier), but immediately after the blow you may **step toward the foe to stay in reach, one step (1/10 Move, min 1 hex) per attack you have made this turn**. You drive them across the field and advance into the space they leave — never away from you. Knockback now functions as positional control + footing disruption, not distance-opening. Counterattack economy (no-limit, 1 FP each, −2→+0 by tier) unchanged.

**Step rule → RAW (compendium):** was flat "one hex"; now **1/10 your Move rounded down, min 1 hex** (Move 20 = 2 hexes, 30 = 3; below 20 = 1 hex). Still one step per maneuver.

**CORRECTION to the prior "STEP RULING" above:** the "step, or two steps (2nd at −2)" option is **Committed Attack (Determined)** — a *Martial Arts* maneuver — NOT All-Out Attack. RAW **All-Out Attack** movement = move FIRST then attack, up to **half your Move (round up), min 2 hexes**. The compendium's AoA "Step or full Move" is a divergence (full > RAW half); it is tagged HOUSE on the A3 cheatsheet (deliberate) but **untagged in the compendium**.

**OPEN DECISIONS for James (RAW cited, not yet changed — both are balance-affecting / possibly-intentional home-brew):**
1. **All-Out Attack movement** — compendium "full Move" vs RAW "half Move (round up), min 2 hexes, move-then-attack." Cheatsheet tags it HOUSE (but the tag is ambiguous — may apply to the QA/Fast-Draw permission, not the movement). → revert to RAW half-Move, or formally tag the full-Move as HOUSE in the compendium?
2. **Move-and-Attack melee cap** — compendium "max(9, DX+2)" (in BOTH compendium and cheatsheet, untagged) vs RAW "**−4 to hit, adjusted skill capped at 9**" (the asterisk rule; no DX+2 floor). The DX+2 floor specifically rescues high-DX duelists from RAW's max-9 — looks deliberate. → revert to RAW, or formally tag the DX+2 floor as HOUSE?

**A3 cheatsheet checked:** AoA full-Move tagged HOUSE ✓; M&A DX+2 present, untagged (same as #2); no incorrect step-distance statement (only the "1 m = 1 hex" scale note, which is fine); does not yet reflect the Move/10 step.

**Remaining GURPS-RAW basics audit (each its own focused pass; not yet done):** active-defence formulas (Parry/Block = skill/2+3, Dodge = Speed+3); retreat bonus (RAW +3 Dodge / +1 Parry-Block / **+3 Parry for fencing skills** — lightsaber weapon Parry is `0F`=Fencing, so it gets +3 retreat; verify compendium matches & whether the Fencing class is intended); multiple-defense penalty (RAW −4 per extra same-hand parry, **WM/TbaM halves to −2** — already confirmed applied); knockback formula (RAW per ST−2 of crushing/cutting after DR); posture penalties; ranged (Acc/Aim/RoF/range bands). **Caveat: GURPS Martial Arts is NOT in the project files** — MA-sourced rules (Committed Attack, Deceptive Attack variants, Beat, etc.) are adjudicated from knowledge and flagged as not book-verifiable.

### 2026-06-26 (cont.) — GM rulings applied + MA book now in project (commit f824557)

Both open decisions above are now **RESOLVED**:
1. **All-Out Attack movement — KEEP full Move, tagged HOUSE.** GM ruling: AoA already surrenders every active defence, so half-Move would make it a trap against a mobile foe. Compendium AoA definition now carries an inline HOUSE tag documenting the deviation from RAW (half Move, round up, min 2). Cheatsheet was already HOUSE-tagged.
2. **Move-and-Attack — REVERTED to RAW.** Now "**−4 to hit, adjusted skill capped at 9**" (no DX+2 floor) in all 6 compendium M&A spots + both cheatsheet spots. Fixed the rule that falsely claimed the DX+2 floor was "Per RAW". **Slams** corrected too: RAW exempts slams from the −4/cap-9 (roll vs DX). The 2 surviving "DX+2" in the compendium are the **Weapon Master / Mighty Blows damage bonus** (+2/die at skill DX+2) — correct, left intact.

**GURPS Martial Arts is now in the project** (`/mnt/project/GURPS_-_Martial_Arts.pdf`, a text dump like the Basic Set, 1.37 M chars, fully readable/cite-able). The "MA rules not book-verifiable" caveat is closed. Verified core **Committed Attack** (MA p99): Determined +2 hit / Strong +1 dmg, and the Strong bonus **explicitly excludes force swords** — corroborates the compendium's AoA-Strong carve-out and the "flat +damage is noise for lightsabers" principle.

**STALE ARTIFACT:** `Combat_Cheatsheet_A3.pdf` is now out of sync with the edited `.html` (M&A/slam lines). Needs regeneration from the HTML.

**Remaining RAW basics audit (now fully book-backed, both Basic Set + MA):** active-defence formulas; retreat bonus (+3 Dodge / +1 Parry-Block / +3 Parry for fencing — lightsaber `0F` Parry gets the +3); multiple-defence penalty (−4, WM/TbaM −2); knockback formula; posture; full ranged section. Awaiting GM's preferred order (defences/retreat flagged as highest-value next).

### 2026-06-26 (cont.) — Audit pass 1: Active Defences + Retreat (vs Basic Set + MA)

**Verified RAW-faithful (no change):** Dodge = Basic Speed+3 (drop fractions, −enc); Parry = skill/2+3; Block = skill/2+3; one active defence per attack; side arc −2; rear-arc-unaware = no defence; off-hand parry −4 (unless Ambidexterity); unbalanced ("U") weapon can't parry the turn after attacking; +1 Combat Reflexes; retreat = +3 Dodge / +1 Parry-Block / +3 Parry for fencing or Boxing/Judo/Karate; retreat once per turn, applies vs that attacker, costs your step.

**FIXED → RAW (commit pending):** **Retreat distance.** Was "retreat is one hex" (2 spots); RAW B377 = a retreat is a step, "at least one yard, not more than 1/10 your Move." Now "a step (1/10 Move, min 1 hex)" — direct corollary of the Step fix.

**OPEN DECISIONS for James (consequential / mislabelled — flagged, NOT changed):**
- **(A) Multiple-defence penalty is mislabelled "Standard (RAW)."** Basic Set B376 penalises ONLY repeated parries with the *same weapon/hand*: −4 cumulative per parry after the first; reduced to −2 with a **fencing weapon OR WM/TbaM**, −1 with **both**. **Dodge has NO penalty (unlimited); Block is once/turn.** MA adds no general multi-defence penalty. The compendium's universal −4/−8/−12 to *all* defences (dodge included) is a **HOUSE rule**, not RAW. → (a) keep the universal penalty but re-tag HOUSE, or (b) revert to true RAW (parries-only; dodge spammable). Balance-defining.
- **(B) WM/TbaM halving citation is wrong.** Compendium says "MA p.122 RAW halves all defenses." Actually the −4→−2 reduction is Basic Set B376, applies to **parries**, and triggers on fencing-weapon OR WM OR TbaM (−1 with both). MA p.122 only halves Rapid Strike + multiple-parry penalties. Tied to (A).
- **(C) Is the lightsaber a fencing weapon (`0F`)?** If yes: its Parry gets the **+3 retreat**, and its multiple-parry penalty is **−2 even without WM (−1 with WM)**. RAW's fencing list (Main-Gauche/Rapier/Saber/Smallsword) excludes setting weapons, so this is a classification call. Confirm intended.
- **(D) Rear attack when AWARE: compendium −4 vs RAW −2.** RAW (B392/Close Combat) treats a rear attack the victim *is* aware of (attacker circled into the back arc) as a **side attack: −2**. Compendium gives −4, reserving −2 for 360°/Peripheral Vision. → keep −4 (house) or align to RAW −2?

**Next audit slices (unstarted):** knockback formula; posture penalties; full ranged section (Acc/Aim/RoF/range bands/Bolt Deflection already done).

### 2026-06-26 (cont.) — Decisions A & B resolved (multiple-defence penalty)
GM confirmed (PCs reach Dodge 15+: Truman 15, Sekan 12, Chatni 11 at base; higher in defensive forms) that true-RAW uncapped dodge would make high-Speed PCs untouchable. **(A) KEEP the universal multi-defence penalty; re-tagged from "Standard (RAW)" to "House Rule"** with a note that Basic Set RAW penalises only repeated same-hand parries (dodge/block uncapped). **(B) Fixed the false "MA p.122 halves all defenses" citation** to the real B376 rule (−2 with fencing weapon / WM / TbaM, −1 with both, parries only; ruleset extends the halving to the matching weapon/skill). Mechanic unchanged — label/citation only. **Still open: (C) lightsaber-as-fencing (0F) -> +3 retreat & −2/−1 multi-parry; (D) rear-aware −4 vs RAW −2.**

### 2026-06-26 (cont.) — Dev tooling: CI gate + compendium locator

Two additive dev aids landed (no rules/data touched):

- **`.github/workflows/check.yml`** — first CI on the repo. Job `invariants` runs `check.py` on
  every push to `main` (auto-catches a broken parallel-session push; currently green, 3 pre-existing
  non-breaking schema-key warnings). Job `smoke` boots `sheet.html` in real headless Chromium via
  `tools/ci_smoke.mjs` — the runtime check the dev sandbox can't run — failing only on an uncaught
  JS exception at load. NOTE: the `smoke` job's first real exercise *is* CI itself (Chromium won't
  launch in the sandbox), so it may want a tweak on first run; `invariants` is the proven gate.
- **`tools/query_compendium.py`** — `name → section + tight line range` locator, plus `--grep`,
  `--headers`, `--all`, `--strip`, `--full`. Output capped by default. Use it instead of ad-hoc grep
  / whole-file reads against the compendium. Documented in SKILL.md → "Dev aids".

Both verified locally: YAML parses, `node --check` clean on the smoke script, query tool exercised
against the live compendium (exact lookup / multi-match / TOC / grep / no-match exit), `check.py` green.

### 2026-06-26 (cont.) — Decision C resolved (lightsaber NOT fencing)
GM ruled the lightsaber is **not** a fencing weapon (would be overpowered with Dodge-15+ duelists). Stripped the `F` from all lightsaber Parry cells (compendium: standard/shoto/saberstaff/great saber `0F`->`0`; sheet: standard + Sith synth-crystal `0F`->`0`) and added an explicit note on the Lightsaber Parry rule: balanced weapon, retreat gives the standard **+1** Parry (never +3), and it does **not** get the fencing −2 multi-parry reduction (only Weapon Master halves it, per the house rule). No code keyed off the `F`, so this is the table-tag + prose only. **Still open: (D) rear-aware −4 vs RAW −2.**

### 2026-06-26 (cont.) — D closed + audit pass 2: Knockback + Posture

**(D) closed:** rear-aware −4 tagged as a deliberate house deviation (RAW = side attack, −2). GM confirmed keeping −4.

**Knockback (vs B378) — mostly RAW-faithful:** ST−2 per metre formula ✓; crushing knocks back regardless of DR ✓; impaling/piercing no knockback ✓; fall rule (1m safe, 2+ roll vs best of DX/Acrobatics/Judo at −1/m) ✓; knockback off basic damage before DR/multiplier ✓. **DIVERGENCE (flagged, not changed): cutting.** RAW = cutting causes knockback ONLY if it fails to penetrate DR (then full). Compendium = cutting knocks back at HALF, always, regardless of DR. Likely a deliberate simplification (and near-moot for a saber game — lightsabers are burn, no knockback either way). → keep house "cutting half" (tag HOUSE) or align to RAW?

**Posture (vs B364/B551) — core penalties RAW-correct:** own-attack penalties (crouch/kneel/sit −2, crawl/prone −4) ✓; own-defence penalties (kneel/sit −2, crawl/prone −3) ✓. **FLAG: the "Hit Against" column** (+3 close / −2 ranged for prone; +2 close for crawling). RAW's lever for "prone = easy melee target" is the defender's −3 defence (already in the table); couldn't confirm a *separate* melee to-hit bonus in the Basic Set dump, so the "+3/+2 close" may double-count (harsher than RAW). Ranged −2 vs prone is plausibly RAW. → confirm whether "+N close" is an extra modifier or a restatement of the −3 defence.

**Next slice: ranged** (Acc/Aim/RoF/range bands; Bolt Deflection already done).

### 2026-06-26 (cont.) — Knockback/Posture RAW applied + Ranged slice (audit complete)

**Knockback → RAW (done):** cutting now knocks back ONLY if it fails to penetrate DR (was "half, always"); crushing regardless of DR; impaling/piercing none. Compendium + sheet knockback hint both updated.

**Posture → RAW (done):** the counterintuitive one — a *crawling or lying* foe is **−3 to hit in melee** (kneeling/sitting −2), offset by their −3 defence; ranged −2 vs low postures. Flipped the compendium's wrong **+3/+2 close** to **−3** across ALL 7 references (main posture table, two ranged-section copies, the prose "easy to hit at close range", the "attacker bonus" line, the ranged targeting summary, and two End-Prone maneuver notes reframed to the −3 defence downside). Sheet had no posture table.

**Ranged slice — mostly RAW-clean:** Aim (Acc, +1@2s, +2@3+s) ✓; Recoil (hits = margin÷Rcl +1, bracing −1) ✓; ranged maneuvers table (M&A −2/Bulk, AoA, Committed +2, Defensive, Telegraphic, Targeted hit-locations, Off-Hand −4, Bulk) ✓; the **entire range/Speed table** (7-10→−3/−4 … 700-1000→−15/−16) ✓. **FIXED:** the 3–5 hex band was −2/−3, off by one; now RAW **−1 to −2**. **FLAGGED (not changed): RoF bonus table.** Compendium "9–16 → +2, 17–49 → +3" vs RAW finer "9–12→+2, 13–16→+3, 17–24→+4, 25–49→+5, 50–99→+6". Simplified, looks deliberate. → adopt RAW progression or keep simplified?

**AUDIT STATUS: all five slices complete** — (1) movement/maneuvers [Step, AoA-HOUSE, M&A→RAW], (2) defences/retreat [multi-defence HOUSE re-tag, retreat distance→RAW, lightsaber-not-fencing, rear-aware-HOUSE], (3) knockback→RAW, (4) posture→RAW, (5) ranged [3-5 band→RAW; RoF flagged]. Only open item: the RoF-table decision.

### 2026-06-26 (cont.) — RoF table → RAW (audit fully closed)

GM ruled adopt RAW RoF. **The sheet was already RAW** (`rofBonus()` labelled B373: 9–12 +2, 13–16 +3, 17–24 +4, 25–49 +5, 50–99 +6, 100+ +7) — the compendium and cheatsheet were the drifted ones (simplified 9–16 +2 / 17–49 +3 / 50–99 +4 / 100+ +5). Fixed both to the RAW progression; all three artifacts now agree. Cheatsheet PDF regenerated (4pp A3, fonts subset). **No open items remain — the GURPS-RAW basics audit is fully closed.**

### 2026-06-26 (cont.) — Ship-builder overhaul: mounts → parts → frames → frame-driven base stats

A self-contained **vehicle / ship-builder** workstream (sheet.html), separate from the Force/RAW work above.
Each commit node --check + Playwright verified.

**Size-first mounts** (`c9c9ede`): first mount column is an S/M/L/C **size** selector that filters the weapon
dropdown (larger holds smaller). Dropped the free-text label + drag-and-drop (weapon palette is tap-only).

**Firing arcs = swivel + location** (`7cff69e`): per mount a **Swivel** (Fixed-forward / 120° arc / 360°
turret) + **Location** = Deck (top/mid/bot) × Position (3×3 bow-to-stern grid). Deck drives above/below
coverage; swivel drives pilot-vs-gunner (pilot fires fixed-forward + 120°-front; else needs a gunner).
Legacy arc/face fields migrate on read.

**Range bands + warhead flight** (`64cd76f`,`6bdcd24`) per compendium: range is abstract bands on 100-m
hexes (Knife ±0 / Close −4 / Medium −6 / Long −8 / Extreme −12; penalty on Gunnery, not Perception), derived
hex spans shown (Knife ≤2 … Extreme ≤200). Warhead flight = impact delay in TURNS (missiles Fast, torpedoes
Slow, mines Placed, beams instant).

**STAGE 1 — hardpoints from the hull** (`56a20d6`): each hull frame carries `mounts:{S,M,L,C}` (compendium
per-class table); `hardpointBudget(v)` reads the assigned `v.core.Hull` part first, class/cap fallback only
for catalogue ships.

**STAGE 2 — free-form part mods** (`29df7b7`, "Full" per James): every assigned core part takes free-form
mods stored on **`v.coreMods[cat]=[{label,mass,pwr,stat,val}]`** (mirrors equipment `mods[]`). Each adds mass
+ power draw (negative frees power, clamped ≥0) and may bump ONE stat: +S/M/L/C hardpoint, Hull DR, Hull HP,
Shield SP, Move, Power output. `coreModSum(v,key)` is the single summer, hooked into shipPowerMass
(mass/draw/gen), hardpointBudget, vehHullDR, vehShieldSP, vehMoveBase, vehicleEffectiveStat hpMax. Added the
**Hull picker row** (was UI-unreachable before).

**Frame-scale filter + 3 capital frames** (`7127c25`→retuned `dbdc921`): frame ladder is now 6 tiers —
**Small · Fighter · Light · Medium · Heavy · Capital**. Core-system pickers only offer parts that suit the
assigned hull. **CORRECTION to an earlier in-chat claim:** the compendium hardpoint table STOPS at Frigate
(6S/6M/4L/1C) + generic "capital 4C" — it does NOT spell out Cruiser/Dreadnought/Carrier rows. So the 3 new
capital frames (Cruiser 6S/8M/6L/2C · Dreadnought 8S/10M/8L/4C · Carrier 6S/4M/2L/1C) have **DR grounded in
the warships catalogue** (~150/300/270) but **S/M/L hardpoints + HP/mass EXTRAPOLATED**. Fit logic
(`partFrameBand`) is **stat-tiered**, not keyword: Reactor by power, Sublight by mass, Shields by SP →
light/heavy/capital bands with a 1-tier overlap; every other system fits any hull. Off-scale current
selection stays visible with a hint.

**STAGE 3 — frames drive base HP/DR/mass/econ** (`dbdc921`): a frame sets base HP (its own pool — Gunship 900
/ Cruiser 45000, supersedes hullHPForClass when a frame is assigned), base Hull DR (frame dr, before armour +
mods), structural mass (frame mass), and class economy (cap/power via the frame's class keyword — every frame
name resolves). Stage-2 mods still layer on top. Catalogue ships (no frame) fully unchanged.

**Econ rescale** (`d230db6`): Stage 3 exposed Medium Freighter(45)/Heavy Freighter(85)/Carrier(1800) frames
out-massing their caps(48/48/2000). Added Medium Freighter econ (cap 130), rescaled Heavy Freighter (240) +
carrier (5000), routed both freighter frame names ahead of the generic /freighter/. All 15 frames now 18–60%
structural mass, 40–82% headroom, none overweight stock.

**Data model:** `v.core={cat:partName}` (frame + core parts; `vehCorePart`/`setVehicleCore`),
`v.coreMods={cat:[mods]}` (part mods), hull parts carry `mounts:{S,M,L,C}` + `size` (1 of 6 tiers).
`FRAME_RANK` size→0..5; `partFrameBand`/`partFitsFrame`/`vehFrameSize` drive the filter.

**RATIFIED/DONE (follow-up):** capital-frame HP/mass/hardpoints stay extrapolations (no compendium source
for capital hull HP/mounts) — **James ratified them as best-available**; revisit only if a source surfaces.
**Sensors/Cargo/Crew are now in the part-mod stat dropdown** (`sens`/`cargo`/`pax`), shown as the part+mod
total in the picker tag (their only display surface — none are read in combat). **Still open (minor):** the
part-tier heuristic is stat-threshold based — retune `partFrameBand` if a generic mis-tiers; Hull picker tag
shows `slots` (could show HP/DR; cosmetic).

### 2026-06-26 (cont.) — Compendium polish + cross-file rule consistency

**Structural breakage fixed:** one unclosed `<p>` (the "Power Affinity" rule ran straight into the "What an hour buys" `<div>` with no `</p>` — closing it dropped rendered height ~17k px, so it had been wrapping following content in a stray paragraph) + removed 9 empty `<p></p>`. Paragraphs now balanced 3727/3727. (The 16 "xxx- xxx" hyphen hits are intentional suspended compounds — "one- and two-handed", "vehicle- and ship-mounted" — left alone.)

**Cross-file rule consistency (compendium ↔ cheatsheet ↔ sheet):** cheatsheet had two values still on the pre-RAW numbers I'd fixed in the compendium — the **3–5 hex range band ("−2/3" → RAW "−1/2")** and **retreat distance ("Step 1 m back" → "1/10 Move, min 1 m")**. Both fixed + PDF regenerated. Verified consistent across files: RoF (all RAW), M&A (−4/max-9), AoA (full-Move HOUSE), multi-defence penalty, lightsaber Parry 0. Cheatsheet knockback is generic (no cr/cut claim to contradict) and has no posture-modifier table, so nothing to reconcile there.

**Visual:** compendium is already well-designed (clean tables, power blocks, drop caps, consistent headers) — did not impose a redesign. Minor open item: ~8px horizontal overflow at iPad width (768px) from `.cover`/`.path-doc`; `box-sizing` + body margin are already correct so it's a specific child element, and the fix risks the shared print/PDF CSS — left it.

### 2026-06-26 (cont.) — Quick-find shipped + ship-builder & point-cost status

**Compendium quick-find (DONE, pushed):** full-text search overlay — `/` or Cmd/Ctrl-K (bottom-left magnifier FAB for touch). Lazy TreeWalker index over ALL sections (rooted at `document.body`, not `.path-doc` — `.path-doc` is only the first document's wrapper, so rooting there missed ~everything after it; that was the bug). Ranked results (title-start > title-contains > body-frequency) with snippets + gold `<mark>`, ↑↓/Enter/Esc, jump-and-flash, hash update. ~345ms one-time index. Complements the existing title-only `#sidenavFilter`.

**Ship-builder gap (a) — sensors/cargo/crew part-mod dropdown: ALREADY DONE** (parallel session). `COREMOD_STATS` has `+Sensor km`/`+Cargo t`/`+Crew berths`; wired via `_mk={sensorRng:'sens',cargo:'cargo',pax:'pax'}` + summed (`cargo:sum('cargo')`, `pax:sum('pax')`, `sensorRng:sum('sensorRng')`) + displayed. Verified by code inspection.

**Ship-builder gap (b) — capital-frame ratification: DONE (option A).** James ratified as-is; numbers unchanged, Cruiser note hedge stripped ("...extrapolated above frigate / per catalogue..." -> "Heavy main batteries on a balanced capital hull"). Capital frames now final.

_Superseded note:_ Full 15-frame table reviewed. Capital tier (Cruiser hp62000/dr150/mass850/70slots/6-8-6-2 · Carrier hp100000/dr270/mass1800/100/6-4-2-1 · Dreadnought hp150000/dr300/mass2400/130/8-10-8-4). Key finding: the big Frigate→Cruiser HP jump (14000→62000, 4.4×) is the Heavy→Capital tier boundary, and HP-per-DR is internally consistent ACROSS the capital tier (Cruiser 413, Carrier 370, Dreadnought 500) — it's the Heavy tier (Frigate 113) that's DR-heavy. Cruiser note flags hardpoints as "extrapolated above frigate", DR "per catalogue". Recommend ratify-as-is + strip the hedge wording; offered smoothing/DR-bump alternatives.

**Skills/traits/point-cost audit — STARTED (foundational tier clean).** Primer-A chargen sections are thin orientation prose (no big cost tables). Verified vs GURPS RAW: A.3 attribute costs (ST10/DX20/IQ20/HT10) and A.4 secondary costs (HP2/Will5/Per5/FP3/BasicSpeed5-per-0.25/Move=Speed-floored) — ALL correct, no changes. Remaining (multi-pass): skill costs-by-difficulty + defaults, advantage/disadvantage *costs* (traits section names them only — costs live in sheet trait data), Force-power point costs in the Force sections.

### 2026-06-27 — Sheet audit + panel↔compendium FP-fidelity CI guard

**Project Instructions' "What is not tracked" block is STALE.** sheet.html already implements thrust/swing, Dodge/Parry/Block (effDodge / weaponParry / block + rollDef), Basic Lift/Speed/Move, the full encumbrance chain (gearWeight→encLevel→encName→effDodge/effMove), reeling/tired + negative-HP death ladder + shock strip, totalPts vs ptTarget, and per-location DR ("DR by Hit Location": shield→armour, energy/kinetic). No Critical/Important data gap remains.

**Genuinely not tracked (all Minor):** self-control CR+roll on disads; Cultural Familiarity tracker. Possible-minor: major-wound auto-flag; natural/racial DR folded into the DR-by-location readout.

**Automation is deep** — v29 integrated hit resolver (skill +RoF −loc −range ±sit → 3d6 → dmg → AD÷DR → wound-mult → injury) + all rollers. **The one real gap: Force-power activation** (no usePower/spendFP; clicking a power doesn't deduct FP or start Upkeep/concentration, though powers carry FP+Upkeep and the tracker has concentration/charge fields). Minor: shock not subtracted from rolls; no recovery roll. ← next feature candidate.

**"Panel FP drift" was a FALSE ALARM:** panel FP *fields* are byte-identical to the compendium for all 204 powers. "no FP" in compendium Upkeep prose = "no *per-turn* FP" (metered per minute), consistent with the FP field. Now CI-guarded: check.py `check_panel_fidelity()` asserts every panel FP == compendium FP (204/204 pass); future drift WARNs.

**Open compendium-internal question (James's ruling, NOT a sync fix):** a couple of *latched* powers read in tension within the compendium itself — Force Balance Walk FP "1 per turn" vs Upkeep "runs free … no FP"; Tempered Blade "…then 1 per turn" vs "runs free … no FP". Likely the FP field is the pre-latch cost and "runs free" is post-latch; confirm intended reading. Panels mirror the compendium faithfully either way.
### 2026-06-26 (cont.) — Point-cost audit: trait/advantage/disadvantage costs (DONE)

Audited the sheet's `DATA.ads` (457) + `DATA.disads` (367) cost catalogs vs GURPS Basic Set. Method: programmatic diff against a curated reference of ~175 well-known Basic Set entries, then **every mismatch verified against the Basic Set PDF before acting** (book is arbiter, not memory — this caught 3 false alarms where my reference was wrong: Appearance Transcendent IS 20 not 25 (B21), Weapon Master small class IS 30 not 25 (B99: small class = fencing/knightly weapons 30; "two weapons together" is the separate 25 tier), Dyslexia IS −10 not −15 (B). All confirmed catalog-correct.).

**One real error found + fixed:** `Gadgeteer (Quick)` was 40 → corrected to **50** (Basic Set: Gadgeteer "25 or 50 points"). All other checked core traits (Combat Reflexes 15, HPT 10, Trained By A Master 30, full Innate-Attack/Regeneration/Wealth/Weapon-Master ladders, etc.) are RAW-accurate. Coverage = the common Basic-Set core; the ~640 supplement/Powers/home-brew entries (Magery variants, Damage Reduction tiers, Force-linked) not individually checked.

**Still open (next point-cost passes):** skill defaults + costs-by-difficulty, and Force-power point costs (compendium Force sections — internal-consistency check, since those are home-brew).

### 2026-06-27 (cont.) — Force-power activation v1 (shipped)

Closed the real automation gap. **⚡ on every KNOWN power row** (Force tab, beside ⓘ) → `activatePower(name)`: deducts activation FP (`parseInt(FORCE_POWERS[name].fp)` — FORCE_POWERS is a lexical `const`, reference it BARE, not `window.FORCE_POWERS`, or it reads undefined → deducts 0) and, if sustained/latched (detected from `window.FORCE_DESC[name]` FP field matching `/then|per (turn|min)/`), pushes `{n,up}` to a NEW `C.combat.active[]` with a short upkeep reminder ("1/min","2/turn"). **Active powers render as violet badges in `renderStatusStrip`** (beside stance/form) with × → `dropPower`. Toast feedback = `_fxToast`. Helpers sit right after `adjFP`.

Deliberate scope: **no auto-metering** of ongoing FP (upkeep is a displayed reminder; the player meters it with the existing FP ± buttons). Sustained powers dedupe (no double-charge on re-click); one-shot powers just deduct. Playwright-tested (11 assertions: FP deduction, upkeep parse, dedupe, one-shot, drop, no console errors); check.py green.

**v2 candidates (not built):** quick-cast list in the HUD (activate lives on the Force tab, see/drop on the combat HUD — split surfaces); subtract shock from to-hit rolls; FP recovery roll.

### 2026-06-27 (cont.) — Firebase sync: multi-device rollback war FIXED (v4.1)

Symptom (Chatni): point total flip-flopping 1150↔1485↔1501 across the iPad + other open tabs/devices; live sync rolling back yesterday's work. **Root cause in firebase-sync.js: echo-suppression keyed on the ACCOUNT (`updatedBy === auth.currentUser.uid`), not the device/session.** Two+ tabs/devices on the SAME login each saw the others' writes as their own echo → skipped applyRemote → kept stale local C and kept pushing it → infinite flip-flop between every open device's state. No newest-wins guard either.

**Fix (v4.1):** suppress only THIS tab's echo via a per-page-load random `clientId`; writes from any other session (even same account) now applyRemote. A fresh/returning device's clientId never matches prior writes, so it always applies the current doc on connect and can't sit on stale local and push it. Model = Firestore doc is source of truth; last-write-wins on truly-simultaneous same-character edits (acceptable; not the bug). Added `writer: clientId` to the doc + a `[sync] v4.1 · client <id>` console marker to confirm a device reloaded the fix and see distinct ids.

**Recovery given to James:** on the device showing the good 1501, hit Export (backup JSON); close/sign-out the stale tabs/devices so the doc settles on 1501; then hard-reload all devices on the v4.1 code. Export/Import = top of sheet (exportChar/importChar).

### 2026-06-27 (cont.) — Game-XP into point budget + Attribute Training tool

**Budget fix:** the Total Pts bar compared `totalPts()` against `ptTarget` ALONE — earned Game XP (`C.xpEarned`) was never added, so any in-play growth showed "over". Now budget = `ptTarget + xpEarned` (renders "X / 200 (150+50 XP)"). `xpEarned` was already tracked (🎓 Game XP, sheet tab); the bug was purely the budget comparison at the Total Pts item. No data change for chars with 0 XP.

**Attribute Training (new — skills tab, below Study & Training):** `C.attrStudy[]`, mirrors the skill tool. Pick ST/DX/IQ/HT/HP/Will/Per/FP → auto-computes Req hours = per-level cost × 200 (`ATTR_TRAIN_PER` = {ST10 DX20 IQ20 HT10 HP2 Will5 Per5 FP3}) with the same level/teacher(×0.75)/self(×1.5) modifiers. ⚄ Roll = `rollAttrStudy`: 3d6 vs Tgt (current level), margin × /Marg hrs off, crit learns outright, crit-fail loses hrs. At Req hours → `grantAttrPoint` raises the attribute one level (primary → `C.attr[x]+cost`, secondary → `C.sec[x]+cost`), resets progress, recomputes next level + calls renderSheet so the main tab updates. **Shares the same hours pool** (`trainHoursAvail`/`trainHoursTotal`) as skill training. Point cost lands in `totalPts()` → covered by the Game-XP budget (ties to the fix above). Functions inserted before `addSkill`; `${attrTrainingSection()}` wired into renderSkills before customSkillsSection. Playwright-tested (13 assertions: per-attr hours, primary+secondary raise, full roll→crit→raise, budget annotation).

Not added (easy if wanted): a manual "Tr. Attr" XP sub-counter next to Tr. Skills/Tr. Force — the budget already accounts via xpEarned+totalPts, so it's optional.

### 2026-06-27 (cont.) — Firebase sync v5 (per-key field-level merge) + Merge-patch import

**Desync root cause:** v4.1 serialized the ENTIRE character into one `data` string and wrote it whole (`setDoc({data:lastJSON},{merge:true})` — merge:true is meaningless with one field). Concurrent edits raced on that blob → whole-doc last-write-wins clobbered everyone → rollback/desync. The clientId trick only stopped the self-echo loop.

**Fix — v5 per-top-level-key sync (firebase-sync.js):** each top-level key of C (attr, sec, skills, traits, cyber, force, combat, notes, study, forceStudy, attrStudy, ptTarget, xpEarned, languages, _meta, …) is stored as its own JSON string under a Firestore map field `f`. Only CHANGED keys push as deltas via `setDoc({f:patch},{merge:true})` → Firestore merges concurrent edits to DIFFERENT keys; SAME-key resolves last-write/cloud-priority. `applyRemoteKeys` applies cloud key-by-key: skip if == ancestor, advance ancestor if == local (echo), else overwrite local (CLOUD PRIORITY) — no wholesale wipe. Value-based ancestor tracking (`base` = last-synced JSON per key) replaces clientId as the correctness mechanism → structurally fixes same-account multi-device. Legacy `{data:blob}` docs auto-migrate on first load (`applyLegacyBlob` → reseed as `f`; old `data` ignored once `f` exists). UI/login/pill/gate/daraCloud kept verbatim. Tested: node --check + 13-assert concurrency sim (diff-key concurrency both survive, same-key cloud-wins, echo no-loop, legacy migration, unpushed-edit preserved).

**Granularity:** top-level key. Co-edit hotspot is `combat` (player tracks HP/FP, GM applies damage) — same-key there = cloud/last-write wins. Can deepen combat to sub-keys later if hit.

**Req (c) — GM/Claude edits merge concurrently (sheet.html):** added `applyCharPatch(patch)` + `importCharMerge` + a "Merge patch" button (next to Import). Applies ONLY the top-level keys present in the file (does NOT wipe the rest — UNLIKE importChar/mergeChar which reset everything to blank). With v5 live, changed keys propagate as deltas → merge with players' concurrent edits. Workflow: Claude hands James a PARTIAL patch (changed keys only) → Merge patch → live-syncs. (Full files merged would overwrite every key — deliver partials only.) Playwright 5/5. ZERO-TOUCH alt offered: a GM Firebase login (email+pw) would let Claude write the `f`-map patch straight to the live doc from the sandbox via Identity Toolkit REST → Firestore REST — pending James's decision + credential.

**Rollout:** all devices must reload onto v5; legacy (`data`) and v5 (`f`) coexist during rollout (first v5 client to load writes `f`).

### 2026-06-29 — Training-session mechanic overhaul (commits d04ad6d, 30b80c6, dd7cb9d)

Audited skill/attribute/Force training math against the compendium (§3.1–3.2) and reworked the per-session model across all three roll functions (`rollStudy`, `rollAttrStudy`, `rollForceStudy`). The compendium study model is pure deterministic hour-accumulation (no roll); the per-session 3d6/margin layer is the tool's own house mechanic, so James's worked example is the ruling.

- **Base session = 4 h** (`STUDY_SESSION_HOURS=4`, compendium §3.2b "a single sitting tops out at 4 hours"). A successful session now advances `done` by `4 + margin × Hrs/Marg` (was margin-only). IQ-15/by-4 → 44, matching James's example.
- **Bank drains by the session, not the progress.** Every roll draws the flat 4 h from `trainHoursAvail` regardless of margin/outcome; the margin is a genuine *cut* off the requirement (done advances 44 while only 4 leave the bank), so good rolls stretch real study time. `trainHoursTotal` still accumulates effective progress (gd) so the "÷200 = pts" readout stays correct — avail (real hrs) and total (effective progress) intentionally diverge.
- **Failed session banks its 4 study-hours** (no margin cut) instead of zero — studying always progresses.
- **Bounded crit** (all three): `max(500, round(req×0.25))` capped at req, replacing learn-outright. A cheap skill/Tier-I–II power a crit can still finish (≤500-req completes); a Tier IV power or attribute raise keeps its months. Force crit no longer dumps the whole requirement. **Side effect: the "Monumental" checkbox is now redundant for crit (all crits bounded) — repurpose or remove if desired.**
- **`STUDY_MARGIN_CAP=6`** — a sitting absorbs at most 6 margin-points of cut. Force rolls against the Force attribute (runs 30+), so the raw margin (~19) was cutting ~190 h/session; capped, Force tracks the compendium tier-pace (Tier I ~1 wk … Tier IV ~10–12 wks) even at a high attribute. Applies globally but only binds for high targets (Force, 30+ attrs); normal skills/attrs sit below the cap, unaffected. High attr now gives ~1.3× edge, not the old ~4× runaway.
- **`/Marg` stays flat at 10** — the margin-cut has no compendium basis to scale by difficulty; difficulty already lives in required hours (cost × 200, §3.2a discounts / Force affinity ¼·½ + mentor 150-rate, all verified correct).

Tunable knobs for James: `STUDY_MARGIN_CAP` (6), crit fraction (25%) / floor (500). All three commits verified by jsdom smoke tests (margin add, bank-drain-by-4, crit bounded + bank-safe, cap binds at 30-attr, cheap-crit completes) + `check.py` green. Force-training picker "only shows known" report (earlier this session) was NOT a bug — `forceLearnable()` returns 60 unknown powers for Chatni; it was a stale GitHub Pages/browser cache (hard-refresh).

### 2026-06-27 (cont.) — Zero-touch GM live-write path (tools/gm_push.py) VERIFIED

James chose option 2 (zero-touch). Built `tools/gm_push.py` — signs in via Identity Toolkit REST (signInWithPassword + public apiKey) → idToken → reads/writes the live Firestore doc via REST on the NAMED `kotor` DB (`projects/kotor-gurps/databases/kotor/documents/characters/<id>`). Writes per-key patches with `updateMask.fieldPaths=f.<key>` → field-level merge matching v5's `f`-map shape → GM/Claude edits coexist with players' concurrent edits (cloud-priority on same key). Auto-migrates a still-legacy (`data` blob) doc to the f-map before patching. NO secrets in the script (reads ~/.gmcreds line1=email/line2=pw, or env GM_EMAIL/GM_PW; James supplies the dedicated throwaway GM account).

VERIFIED end-to-end vs live Firestore: auth OK; write 2 keys + read back; FIELD-LEVEL MERGE (patch one key, the other survives untouched); legacy data-blob → f-map migration + patch; delete. All on throwaway docs (synctest/synctest2), no real char touched.

**GM-edit workflow now:** `python3 tools/gm_push.py get <charId>` to inspect the live f-map, edit the relevant section, then `python3 tools/gm_push.py patch <charId> patch.json` (patch.json = {topKey: value, ...} for changed keys only) → live-syncs to every signed-in device, merging with players' in-flight edits.

**Creds across sessions:** ~/.gmcreds is sandbox-only (resets each session) — James must re-provide the GM login each session (add to project instructions like the PAT — throwaway account, Firestore-only write, low blast radius — or paste per session) for gm_push to run.
cmds: `gm_push.py get|patch|delete|seed-legacy <charId> [file]`

### 2026-06-29 (cont.) — Training completion auto-credits the trained-XP pools

`sheet.html` (commit 58f124c). Wired every training completion to the XP tracking so build XP is no longer silently eaten. On grant (auto-fires at the hour threshold AND via the manual grant button, since the credit lives inside the grant functions): skill → `C.xpSkillTrained += needed` (grantStudyPoint); attribute → `C.xpAttrTrained += cost` (grantAttrPoint); Force power → `C.xpForceTrained += d.pts` (learnForcePower, both the auto-learn and the buy-with-points paths). Each grant message/toast now shows the credit (e.g. "· +4 Tr. Skills XP") and calls renderSheet() so the Identity XP tally refreshes live.

NEW field `C.xpAttrTrained` (Tr. Attr) — defaults via `||0` guards like the other xp* fields (not in blankChar; mergeChar-safe, char JSONs untouched). `xpFree()` now nets all three trained pools: `xpEarned − (skill+force+attr trained)`. UI: the standalone "XP Free" cell in the Identity XP row was replaced by a Tr. Attr ± counter (modeled on Tr. Force); the free total now shows inline at the end of that cell (red when negative). Row stays 8-col (table width unchanged).

Model is consistent: Game XP (`xpEarned`) is the only manual input (income earned in play); training spends it, tracked per-category by the Tr. pools; budget stays Build + Game XP (Tr. pools are spends already counted in totalPts — NOT added to the budget). Trace: earn 20 GameXP → train 4-pt skill → totalPts +4, Tr. Skills +4, xpFree 16 = budget-unspent 16. Verified: jsdom smoke (skill +1, attr +20 IQ, Force +5 Force Torrent, xpFree 100−26=74) + Tr. Attr counter renders + check.py green.

Open design forks flagged to James: (a) attributes credit a NEW Tr. Attr pool (he named "game/trained/force xp" — confirm Tr. Attr is the right home vs folding into Tr. Skills); (b) buy-with-points also credits Tr. Force — if used for build-time powers it over-credits, can gate to training-only; (c) budget is Build+GameXP (training is NOT self-funding) — flag if training should instead generate its own budget room.

### 2026-06-29 (cont.) — Sheet layout: Attacks + Active Styles moved into the left column

`sheet.html` (renderSheet). The main sheet tab was three stacked `.char-grid` containers: Grid 1 = `.char-left` (span 7: Attributes / Reference Values / Active Defenses) + Skills quick-ref (span 5, right); Grid 2 = Attacks (full-width `1/-1`); Grid 3 = Active Styles (full-width). Because Attacks/Styles were full-width rows *after* Grid 1, they could only begin below the taller of {char-left, Skills}, so a long skills list stranded them at the bottom with dead space under Active Defenses.

Fix: moved the Attacks and Active Styles sections *inside* `.char-left`, after Active Defenses, and deleted the two now-empty grid wrappers (9564→9558 lines). They're now flex children of the left column and sit directly under Active Defenses regardless of skill count. Verified (Playwright, 16-skill repro): Attacks x=18 w=721 y=1080, Active Styles x=18 w=721 y=1196 — both in the left column (w=721, matching Attributes/Ref/Defenses) right under Active Defenses (y=914); Skills stays right (x=751 w=511). tab-sheet height 1569→1467. check.py green (2 inline scripts parse, FP-fidelity 204/204). Moved sections' inline `grid-column:1/-1`/`data-size=full` are inert inside the flex column. Responsive unchanged (<980px → char-left full-width stack).

Open: if the 6-col Attacks table feels cramped at span-7 width, widen char-left→span 8 / Skills→span 4 (one-line change).

### 2026-07-01 — check.py consistency additions + safe-push ship script; live Kryze catch

Extended the invariant harness with two cross-surface consistency checks — both follow the existing
doctrine (assert relationships, never magic numbers), so they survive the growing corpus:
- **Force-catalogue coverage** — the sheet's catalogued Force powers (`{"name":X,"skill":"Force"}`, the
  exact set `tools/regen_force_desc.py` reads) must all resolve to a compendium power block. The
  coverage complement to the existing FORCE_DESC-orphan check; together they pincer sheet↔compendium
  Force naming from both directions. Currently clean (200 catalogued, 0 missing). WARN severity.
- **Kryze-ban** — the pre-rename string `Kryze` must not appear in any shipped surface (`*.html` +
  `characters/*.json`; meta-docs README/SKILL/CONTEXT excluded, since they name it to document the
  rule). FAIL severity. **Caught a live violation on first run:** `KOTOR_GM_Console_v4.html`'s NPC
  surname generator (`NAME_SUR`) still listed `"Kryze"` → fixed to `"Krysla"`. Negative-tested
  (planted string → exit 1; removed → exit 0).

New tool: **`tools/safe-push.sh`** — the ship step wrapped: [stage+commit] → check.py gate → fetch →
rebase origin/main → re-gate → masked push, with conservative abort+hard-reset+handoff on ANY rebase
conflict (re-apply patch fresh, re-run). dash-safe, exit codes captured without pipefail. Use:
`sh tools/safe-push.sh "commit message"`.

Deliberately NOT built (flagged): a compendium **index cache** — `tools/query_compendium.py` already
reads the file in its own process and emits only the slice, so it already solves the context-budget
problem; an index would save sub-second parse CPU, not context, and isn't worth a staleness surface.
And a **bootstrap** script — marginal over `git log && check.py`; its one real value (auto-extracting
this file's in-flight section) is fragile to parse.

Open observation (not acted on): the sheet has **204 FORCE_DESC panels but 200 `skill:"Force"`
catalogue entries** — 4 panels `regen_force_desc.py` would not reproduce. Worth pinning down which 4
(stale, or legitimately hand-kept non-`Force`-skill panels) in a later pass.


### 2026-07-01 (cont.) — Compendium ship-combat subsection reformat (Vehicles book)

Fixed the formatting/UX defects James flagged (screenshot: dead column space, ragged text-wrap,
inconsistent heads, unstyled tables) in the **Starship Combat** subsection — the worst offender in
the Vehicles book. Scope was deliberately held to this subsection; the Force section was left
untouched per instruction (its layout is dictated by the ability statgrid structure).

Root causes, all localized to Scale & Scope / Starship Combat:
- **3-column stranding.** The Scale & Scope PART sat in a `.body-3col` with `column-fill:balance`;
  the many full-width spanners (h2 section-heads + tables) chopped the flow into short balanced
  islands, stranding near-empty third columns and forcing brutal narrow-column wrapping.
- **Ad-hoc inline-styled heads.** 8 `<h3 style="…color:#6a5a2a…">` (olive) + 1 `<h4 style="…#3a5a3a…">`
  (green) instead of doc classes — off-palette AND invisible to the TOC/anchor system.
- **4 bare `<table>`** (no `.tbl`, no `.tbl-scroll` wrapper) → browser-default unstyled tables:
  the Ship-Block translation ("what is renamed"), the Modifiers table, the Systems Strain 3d table,
  and the Weapon Ladder (ship-scale flat dmg / vs shields / vs person / trade-off).

Fix (guarded Python patch, exact-count assertions on every substitution; net −840 code points):
- Scale & Scope block `body-3col` → **`body-2col`** (GURPS-authentic 2-col; halves the stranding).
- 8 inline `<h3>` + 1 inline `<h4>` → **`.subsection-head`** (Cormorant Title-Case; now on-palette and
  TOC-visible; and since subsection-heads do NOT `column-span:all`, they no longer re-fragment the
  column flow the way the old spanning heads did).
- 4 bare tables → **`<div class="tbl-scroll"><table class="tbl tbl--compact">`** (transformed by
  byte-offset inside the ship-combat region, not by retyping the glyph-heavy cell content).

House style basis: GURPS **Space** + **Ultra-Tech** (2-col body, tiered heads CHAPTER → ALL-CAPS major
head → Title-Case subsection → run-in bold lead-in, tables span the columns) — which maps cleanly onto
the compendium's own `section-head` / `subsection-head` / `rule__name` system, so the fix is
"use the doc's own ladder correctly", not a new style.

Left intentional (per the don't-touch-deliberate-looking-things rule): olive caption color `#876b58`
(55 captions doc-wide = the standard), the olive `<strong>` damage-number accents, and the tan
`<tr style="background:#faf3e4">` warhead rows (they semantically flag ordnance).

Verified: **check.py exit 0** (215 powers, headers unique, divs balanced, Kryze absent; only the 3
known non-blocking character-JSON backfill warnings). WeasyPrint before/after render of the same
fragment confirms the four tables now carry dark header rows + ruled/striped cells, the heads are
consistent serif Title-Case, and the body flows clean 2-col. NB WeasyPrint is paged media, so the
screen-continuous column-stranding improvement is reasoned (2-col strictly reduces it vs 3-col), not
visually reproducible in-sandbox — eyeball on GitHub Pages / iPad (ship-then-correct).

Flagged, NOT done (offered to extend): the same two defects live elsewhere — **17 more bare `<table>`
across the rest of the compendium** (17 outside this section, of 21 total), plus likely other 3-col
stranding and inline-styled heads in the wider Vehicles chapter. Same normalization can roll across
the rest of Vehicles / the whole doc on a green light.


### 2026-07-01 (cont.) — Broader-scope formatting pass: table normalization doc-wide

Follow-on to the ship-combat reformat. James greenlit rolling the same normalization across the
whole compendium and asked about column balance too. Ran a full diagnostic sweep first (table
classification, a div-depth matcher measuring every `.body-Ncol` block's spanner density, and an
inline-header scan) before touching anything.

**Done — 18 unstyled tables → styled** (guarded patch, +977 bytes; every substitution assertion-checked;
div-balance verified via check.py):
- **17 bare `<table>`** (no class) across the Learning / Capstones / Quick-Reference / Saber-Forms /
  Named-Shields sections → `<div class="tbl-scroll"><table class="tbl tbl--compact">`. All confirmed
  real data tables (each has `<thead>`/`<th>` + rows), same defect class as the 4 ship tables. The big
  one was the **31-row × 7-col Named Energy Shields table** — was rendering browser-default, now has
  dark header + striping + category band-rows. Rendered-verified.
- **1 skills-quickref table** (`<table style="font-size:10pt">`, no class) → `.tbl` (NOT `--compact`,
  to keep the author's 10pt + the 30%/auto/18% `<th>` widths), wrapped in `.tbl-scroll`. This is the
  **~270-row** full skill list; striping matters enormously for scannability there. Rendered-verified.
- Tables carrying a `.tbl*` class: 365 → 383. The specialized `.skilltbl` / `.bm-table` / `.tk-table`
  tables (41 of them, all with real CSS definitions) were left untouched — they're purpose-built, not
  defects.

**Deliberately NOT done — column mass-conversion (honest pushback).** The diagnostic showed **`.body-3col`
is the document's default body layout — 119 blocks vs 25 two-col.** The 54 blocks the spanner heuristic
flagged are almost all multi-h2 *prose* runs with **zero tables**; only 12 tables sit inside 3-col
blocks total, and none pile up the way ship-combat's four did. A styled `.tbl` inside a 3-col block just
becomes a clean full-width band (the GURPS-standard look), so once the bare tables are styled the 3-col
context reads fine. Ship-combat warranted 2-col specifically because of its unique 4-table pile-up.
A blanket 3→2 would be a 119-block change against the author's clear default, and — because WeasyPrint
is paged media — the screen-continuous stranding it'd target **can't even be verified in-sandbox**.
Recommendation stands: leave the 3-col default; convert individual blocks only if a specific one is
seen to strand on Pages/iPad. (The handful of table-bearing 3-col blocks are the only plausible
candidates if we ever do: penetration-armour-2, starfighterscale-2, boardingactions-2, repair-
maintenance-2 — each has just 1 table, so low priority.)

**Header defect class — fully resolved, 0 further changes.** Only ONE inline-styled `<h*>` remained
doc-wide after the ship fix: an `<h3 style="color:#2a3d2a">` inside a `.callout philosophy` box. That's
**intentional** — the colour is a recurring palette value (5×) themed to the callout, not an off-palette
fake of the doc's header hierarchy (which is what the ship-section olive heads were). Left alone.

Verified: check.py exit 0 (215 powers, headers unique, div-balanced, Kryze absent; 3 known JSON warns).
WeasyPrint render confirmed the Named-Shields and quickref tables specifically.


### 2026-07-01 (cont.) — Whole-compendium formatting audit + table-overflow / dead-anchor fixes

James asked for a full audit of the compendium for defects of the kind we'd been fixing. Ran a broad
multi-category scan (heading classes, `.tbl` scroll-wrap coverage + column width, inline-style clusters,
empty/malformed elements, duplicate ids, broken internal anchors) and triaged before touching anything.

**Fixed:**
- **Table overflow (iPad).** 86 of 383 `.tbl` tables were NOT wrapped in `.tbl-scroll`; 45 of those were
  wide (5–11 columns) — a real overflow/clip risk on iPad portrait. The CSS author's own comment says
  *"tables never overflow the page: wrap each in a horizontal scroll shell"*, and the master rule
  (`.body-Ncol .tbl-scroll, .body-Ncol table { column-span: all }`) makes BOTH bare tables and scroll
  shells span all columns — so wrapping does **not** change spanning (no regression), it only adds the
  `overflow-x:auto` shell. Wrapped **all 86** (45 wide + 41 narrow) so the whole doc satisfies the
  documented wrap-each invariant. `.tbl` scroll-wrap coverage is now 383/383.
- **Dead internal anchor.** `<a href="#sec-ship-countermeasures">Countermeasures</a>` (in the fighter
  section) pointed at a non-existent id — the countermeasures table lives under an id-less
  `<h3 class="subsection">Ship Countermeasures, Systems & Utility</h3>`. Gave that heading the
  `id="sec-ship-countermeasures"`; the link now resolves. (Was the only genuinely broken anchor; the
  other flagged "broken href" was `'#'+r.e.id+'` inside the quick-find JS — a false positive.)

**Audited and deliberately left alone (with rationale):**
- **Heading system — NOT a defect, do not refactor.** 199 "no-class" headings + competing classes
  (`.section-head` 447 / `.section-h2` 38 / `.section` 9; `.subsection-head` 83 / `.subsection` 68) look
  inconsistent but aren't: the doc is split into *books* (`.book--force`, `.book--makers`, `.path-doc`,
  `.dark-section`, `.stance-header`…) each with its own heading styling via descendant selectors, plus a
  global `h2,h3,h4{}` base. No-class headings are context-styled; the competing classes are genuinely
  different tiers (13pt vs 22pt vs 11.5pt). Mass-normalising would break the per-book identity — same
  call as the column default.
- **Inline styles (2167 `<td>`, 507 `<span>`, 135 `<p>`, 81 `<div>`, …)** are the doc's authoring style
  — cell widths/alignment, palette colours, `page-break` controls. Not defects. (The only inline-style
  defect class — headers faking the doc hierarchy off-palette — was already cleared; the one remaining
  inline-styled `<h3>` is an intentional themed `.callout` header.)
- **Duplicate id `qf-empty`** — both occurrences are inside the quick-find JS as mutually-exclusive
  `innerHTML` states ("Keep typing…" vs "No matches"); never two in the DOM at once. Not real.
- **48 nested `<p>`, 4 empty `<div>`, 9 empty `<td>`** — non-strict markup, no visual effect (browsers
  auto-close; empty cells are legitimate blanks). Left.

Verified: check.py exit 0 (div-balanced, table count unchanged, 3 known JSON warns). The wrap benefit
(horizontal scroll on touch) is interactive/iPad and isn't reproducible in the paged WeasyPrint sandbox;
verified structurally instead (spanning rule confirmed, 383/383 wrapped).

**Follow-up (DONE):** added a check.py guard — `check_table_wrap()` — asserting every `.tbl` in the
compendium has a `.tbl-scroll` parent. FAIL severity (bright-line, like the Kryze ban): a future bare
table blocks the push. Asserts the relationship, not a count (per check.py's design rule); detection is
attribute-order/extra-class tolerant (`<div ... tbl-scroll ...>`), and it names offenders by line +
first header cell. Negative-tested (planted bare table → FAIL naming it; removed → exit 0). Note reads
"tables: all N .tbl tables wrapped in .tbl-scroll (overflow-safe)".


### 2026-07-01 (cont.) — GUIDE REORGANISATION workstream (ACTIVE, multi-session) — plan + numbering pilot

Big IA job: reshape the compendium into a proper first-read rules/player guide (modern-TTRPG-guide
pacing: intro → rulings → first-read relevance). **Living Force stays a SEALED UNIT — content never
touched, but it MAY be moved as a whole block.** Not removing info unless doubled/unnecessary; rules
first; concise-but-clear. James's confirmed decisions:
- **Engine-first:** The Core Game (Primer B) moves ahead of Creating a Character (Primer A).
- **Skills placement:** follow GURPS → Skills sits with the character-building material (GURPS order is
  Create → Advantages(2) → Disadvantages(3) → **Skills(4)** → … → Combat much later), i.e. up from its
  current book-12 slot to right after char-gen, before combat.
- **Cross-references:** use **stable section numbers (§X.Y), NOT literal page numbers.** Page numbers
  only exist in the A4 print/PDF view (CSS `counter(page)`), not the iPad/browser scroll build players
  use, and they reflow on every edit (parallel pushes = perpetual staleness). §-numbers are stable,
  work in both media, and keep the tap-to-jump nav. Add the current section number to the running
  header (currently only shows the doc title) so a *printed* reader can find §X.Y.
- **Target macro order:** front matter (Cover · How to Use · setting primer) → Core Game · Char · Skills
  · Core Combat · Ranged · Damage → Living Force (sealed) · Force Training → Equipment · Vehicles ·
  Droids · Trade → Galaxy · Factions.

**Structure facts (recon):** 14 books = **2 Primers (A,B) + 12 Documents (I–XII)** (front matter's "Ten
Documents" was stale → fixed to Twelve). 447 h2 `.section-head`; ~395 TOC number labels but only ~71
align to section-heads — **the §-numbering is only PARTIAL and must be completed** (assign N.k = k-th
section of Document N, primers keep A.x/B.x). 847 `<a href="#…">` links; **295 "Doc «Roman»" refs, 262
linked — ALL point at stable `#book-<slug>` anchors (chargen/coregame/combat/ranged/damage/force/
training/vehicles/equipment/makers/economy/droids/galaxy/factions).** KEY CONSEQUENCE: **reordering
books breaks NO links** (slugs are position-independent) — only the positional "Document N" labels +
"Doc N" visible ref text need renumbering. So the reorder is far safer than first feared; the ref
LINKS are already reorder-proof.

**Safe sequence:** (1) complete + surface §-numbering, convert the 295 book-level "Doc N" refs to
section-level "§X.Y" (per-ref: resolve the named target, e.g. "Rate of Fire (Doc II)" → §2.k) + add
running-header section indicator; (2) reorder books (mechanical: move blocks + reorder TOC/sidenav +
renumber the 12 Document labels/refs to new order), Living Force moved as a sealed block; (3) per-book
first-read pacing + dedup.

**SHIPPED so far (this commit):** numbering PILOT — added `.secnum` style (accent-colour, exact-case
so "A.5a" stays lc), surfaced the A.x/B.x numbers onto the 15 Primer headings, fixed the "Ten
Documents" drift. Render-verified (headings read e.g. "A.1 HOW POINTS WORK", number in accent blue).
**Awaiting James's sign-off on the heading-number + ref FORMAT before scaling to all 12 Documents +
the 295-ref conversion.** check.py green.
