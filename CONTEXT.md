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

_Earlier-resolved:_ Force Choke uses the basic ruling (not a CM exception); standard-blaster AD is 1.5 and
the "AD 1" line is to be dropped from the Project Instructions (see §6).

Flagged to James: the FORCE_DESC re-sync genericised ~30 panels from third-person (she/Chatni) to the
compendium's second-person "you" — correct for a shared multi-PC sheet, but if any of that personalisation
was deliberate, say the word and it can be selectively restored. Otherwise the toolset is current.
