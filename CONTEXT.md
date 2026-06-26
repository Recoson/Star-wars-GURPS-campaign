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

- **[OPEN — needs James] Slim-block format vs the Upkeep/Hands/Move contract.** Commit `631a97f` piloted a slimmer power block on **Force Empathy** (dropped the verbose Upkeep stat field as "covered in At-the-table"), flagged as an *exemplar for a wider block-slimming pass*. That breaks the corpus-wide invariant (every power carries exactly one Upkeep/Hands/Move field) that the batch machine emits, §3a mandates, and `check.py` enforces — so it turned **CI red on every push**. **Restored Upkeep on Force Empathy to unblock CI.** DECISION: (A) hold the contract — keep Upkeep in the grid, no slimming; or (B) adopt the slim format corpus-wide, which means *deliberately* relaxing the `check.py` Upkeep invariant (weakening detection of accidental Upkeep loss across all 215 powers), updating the §3a format spec + batch machine, and a re-slimming pass. **Do not re-slim any power until James rules** — re-dropping Upkeep just re-reds CI.

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
