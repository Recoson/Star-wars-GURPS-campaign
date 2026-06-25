# Force Power Ruling Schema — canonical spec for the full adjudication pass

**Purpose.** Make every Force power *fully adjudicated*: no table question about activation,
upkeep, movement, hands, scaling, or combat-legality should be left unanswered. This doc is
the rubric the 192-power pass runs against, so execution is consistent and resumable across
sessions. Compendium prose remains source of truth; this defines what each entry must state.

---

## 0. The one-second rule (combat vs meditative)
A GURPS combat turn = **1 second**. Therefore any mode that takes more than a few seconds
**cannot** be performed in combat (a 30-min meditation = 1,800 turns). Every power states its
meditative/ritual modes in real time, which makes the combat/out-of-combat split self-evident:
- **Combat-legal:** activates in 1–3 seconds (Concentrate/Attack/Move/Free/Reaction).
- **Out-of-combat only:** anything requiring minutes+ of meditation or ritual.

---

## 1. Per-power ruling schema (axes — fill those that apply)
1. **Activation** — maneuver (Concentrate / Attack / Move / Free / Reaction / Ritual / Instant) · time to switch on · FP to activate.
2. **Upkeep** — one-shot / sustained / passive / stored · FP/turn · FP/min · holds-Concentrate? · interruption · caps / max duration.
3. **Physical state while active** — hands tied up (0 / 1 / 2 / the blade) · movement · establish (channels only).
4. **Scaling** — FP→damage · FP→range · FP→targets/area/duration · advantages that apply · FP cap (if any).
5. **Combat legality & meditative modes** — combat-legal modes vs timed meditative modes (real-time hours + FP + what it grants + interruptible?).
6. **Targeting / defense** — range · LoS · resist stat · defenses allowed · damage type.

**Gap-audit:** while ruling each power, flag anything in 1–6 left unstated and fill it with a
default (marked). Note anything genuinely missing from the power's *design* for review.

---

## 2. Global rulings (LOCKED)

### 2.1 Maneuver → which advantages apply
- **Concentrate** powers: sped by **Compartmentalized Mind** (a free 2nd Concentrate) and **Altered Time Sense**. **Never** Extra Attack or Rapid Strike.
- **Attack** powers: sped by **Extra Attack** (a 2nd attack/turn) — applies to **most** attack-powers. **Rapid Strike** applies **only** to attack-powers delivered as a *melee* strike (Force-empowered blow, saber-carried power); ranged projections (Lightning, Push) do **not** get it. Default Rapid Strike = no; flag the melee ones.
- **Sustained** powers occupy a Concentrate every turn → no second power (or other Concentrate action) without CM; effect ends/weakens if concentration breaks.

### 2.1a What a "motion" is (the hybrid ruling)
A "motion" is the **delivery gesture of the effect resolving, folded into the Concentrate maneuver** — **not** a separate maneuver, **not** a Quick/free action, no extra cost.
- **Standard (1-second) powers:** spend one Concentrate; the motion **and** effect resolve at the **end of that same maneuver, same turn**. No next-turn delay, no separate upkeep.
- **Multi-second charge powers:** hold Concentrate across the charge turns (interruptible — damage/distraction → Will roll or it's lost); motion + effect fire at the **end of the final charge turn**.
- **Prepared/Stored** (§4): charged in advance, released later as their own action.
- The motion is delivery, **not an Attack** → Extra Attack never grants a second one.

### 2.2 Upkeep / interruption
Sustained powers always hold a **Concentrate each turn** (see 2.1). The FP/duration model varies — pick what fits, and **always state the duration cap and/or FP-refresh interval** (never open-ended):
- **(a) FP each turn** — a per-turn cost that may be the **full** activation FP **or a cheaper trickle**. Runs while you pay and concentrate.
- **(b) Concentrate-only, no FP, capped** — costs the maneuver but **no FP**, lasts up to a **stated** duration (e.g. 1 minute), then ends.
- **(c) FP per interval** — free turn-to-turn but **re-pay FP every stated interval** (e.g. each minute) to keep it up.
- **(d) Latched** — raised with one Concentrate, then **runs free**: no per-turn maneuver, no FP, and being struck **never** forces a Will roll. Does **not** hold your Concentrate (so other Concentrate powers run alongside it without CM, and you move freely). Ends only on a stated trigger — typically **falling unconscious**. The explicit override of the standard sustained rules. (e.g. Tempered Blade.)
- **Interruption roll = Will** (not affinity): take damage or a forced distraction → Will roll or the effect **ends** (or **drops a step**, for graduated powers like Force Speed). Affinity = how strong; Will = how hard to rattle.

### 2.3 Range
- **Every power states a default range.** For most, the default **is the maximum**.
- **Range bands where they matter:** a power may behave **differently at distance** (reduced effect, a to-hit/resist penalty, a damage step-down past a threshold) — state the bands.
- **FP→range where it makes sense** (ranged energy/TK projection). Rate: **+1 hex per 1 FP** off base. Most powers do **not** get this.
- **Effectively unlimited reach** for raw TK (**Force Push/Pull**): range climbs with FP toward "as far as you can perceive," but **bought, not free** — a cumulative penalty per increment and/or rising FP per band, so distance has a price.

### 2.4 Hands
- State hands tied up: **0** (TK, senses, mind powers) / **1** / **2** / **the blade**.
- Powers projected from the hand (Lightning) require empty hands; nothing held.
- **Saber-hand channel (mastery gate):** a hand-projected power may be used with a **lit lightsaber still in that same hand** if your best **Lightsaber/Form skill ≥ Force attribute + 6** — blade discipline automatic enough to free the hand's focus. Below that, the hand must be empty. Flag per-power which hand-powers allow it.

### 2.5 Movement while active (+ stance/movement-power interaction)
- **Maneuver used:** movement powers consume a **base maneuver, not a Concentrate** — usually **Move** (Phantom Stride's teleport replaces your Move) or **Instant/free** (Force Step doesn't even spend your step). **Exception:** sustained movement *buffs* (Force Speed = Concentrate). Some also carry a **separate defensive Reaction** (Stride's Blink) using your Reaction, not your maneuver. State the exact maneuver + any free/Reaction sub-component.
- **Free** — passive buffs/senses: move, Force Speed, Phantom Stride, Ataru momentum all fine while active (it only eats the Concentrate slot; CM to run a 2nd power).
- **Step-only** — active channels (Lightning, sustained TK crush, active mind-domination): a Step only. **Incompatible with** Force Speed's bonus, **Phantom Stride / Force Step** (a Move/teleport drops the channel by breaking LoS), and **Ataru's Momentum Strike** (needs a 2+ hex run-up the channel can't make). You are rooted to the effect — pick mobility *or* the channel.
- **Is-movement** — the power *is* the movement (Phantom Stride = Move-teleport; Force Step = Instant blink): cannot also sustain a rooted channel in the same turn.
- **Enhanced** — grants/extends movement (Force Speed): see its own caps.
- Each entry names the relevant stance/movement-power interactions explicitly.

### 2.6 Meditative / ritual modes
- Time-gated and **out-of-combat** (per §0); **no extra FP** for the meditation itself — you pay the effect's normal FP when you use the charged/empowered result (unless a power states otherwise).
- State exact real time (e.g. "Wrath Meditation, 30 min") and what it grants. Interruptible = lost.

### 2.7 FP scaling / caps
- Offensive **FP dumps** (Lightning: 1d/FP) are **uncapped** by rule — limited only by your FP pool; the natural brake is FP exhaustion (HT rolls / unconsciousness at 0 FP). This is intended: feed them and they're devastating.
- Per-power judgement on whether scaling and/or a cap applies; not every power scales.

---

## 3. Per-power OUTPUT FORMAT (what gets stamped)
Keep the statgrid scannable; put prose rulings in one body block.
- **New statgrid fields** (compact): `Upkeep`, `Hands`, `Move`.
- **New body block**, appended to each power:
  `<p class="warn"><b>At the table.</b> Combat-legal modes; FP scaling (incl. range if any);
  meditative mode (real time + what it grants); movement/stance interactions; any gap-fill rulings.</p>`

---

## 4. Classification (all 192 powers bucketed; 0 unsure)
Concentrate-one-shot **67** · Attack **32** · Ritual **28** · Concentrate-sustained **27** (+2 Instant→sustained) ·
Reactive **15** · Free **8** · Instant **6** · Passive **3** · Stored **2** · Attack-or-channel / Attack-then-sustained **2**.

Bucket → Upkeep default (FP cadence pulled per-power from each entry's FP field; costs preserved):
- **Concentrate one-shot** → `none — resolves at the end of the Concentrate.`
- **Concentrate / Instant sustained** → `sustained: 1 Concentrate + [FP] each turn; holds your Concentrate (CM to act/run a 2nd power); struck → Will roll or it ends/drops a step. Extra Attack N/A.`
- **Attack** → `none — resolves on the attack.` (+ Action gains "Extra Attack / Rapid Strike add uses")
- **Attack-or-channel** → `per attack (instant; Extra Attack adds uses), OR channel as sustained Concentrate ([FP]/turn) — holds your Concentrate, Will roll if struck or it breaks.`
- **Attack-then-sustained** → `the attack lands it; then sustained ([FP]/turn) — holds your Concentrate, Will roll if struck or it ends.`
- **Reactive / active defense** → `none — out-of-turn reaction.`
- **Free / quick** → `none — free action.`
- **Instant** → `none — instant one-shot.`
- **Passive** → `none — passive while held/active.`
- **Stored** → `charge held until released or your next rest; the release rides a normal action, not an extra attack.`
- **Ritual** → `resolves when the ritual completes [or: then sustained per its terms]. Not an in-combat maneuver.`

---

## 5. Worked examples

### 5.1 Force Lightning — active channel (the hard case)
- **Activation:** Attack maneuver. No flat FP — FP spent *is* the effect.
- **Upkeep:** Snap = one-shot. Channel = sustained, re-pay FP each turn (1d/FP), holds your Concentrate (CM to act/run a 2nd power), any hit → Will roll or the chain breaks.
- **Hands:** 1 or 2 empty (nothing held; 2 hands doubles output).
- **Move:** **Step-only** while channeling. Breaks if you Stride/Force-Step or take Ataru's run-up; no Momentum Strike while channeling.
- **Establish:** the opening bolt must land to start the channel; runs while LoS holds (cover/LoS break ends it).
- **Scaling:** FP→damage 1d/FP, **uncapped** (FP-pool limited). FP→range **+1 hex/FP** off the base 6. Extra Attack adds snap bolts; ATS lets you snap *and* channel; CM frees the Concentrate.
- **Combat vs meditative:** combat-legal: snap + channel. Meditative: **Wrath Meditation, 30 min** (out of combat) → double damage dice OR arcing targets, +1 Corruption; no extra FP, you pay the storm's FP on release.
- **Defense:** Range 6 (+FP), LoS, cover = immune. Two defense rolls (Dodge / Tutaminis bare-hand / saber-Parry). Wet +1d; metal armour −2 def; insulated +1.
- **Gaps filled:** channel-needs-hit, runs-while-LoS, step-only, FP→range rate, advantage interactions, Wrath Meditation FP, uncapped dump.

### 5.2 Force Speed — passive buff (the contrast)
- **Activation:** Concentrate (1 turn).
- **Upkeep:** sustained — 1 Concentrate + 1 FP each turn; holds your Concentrate (CM to act/run a 2nd power); struck → Will roll or speed drops 1 step. Extra Attack N/A.
- **Hands:** 0. **Move:** **Enhanced** — *grants* Move (now max **+4**, at +1 Move/FP) and/or +1 Dodge-Parry per 2 FP (max +2); fully compatible with Phantom Stride and Ataru.
- **Scaling:** FP→Move/defence up to caps. **Caps: +4 Move / +2 defence.**
- **Combat vs meditative:** combat-legal. Meditative: **Movement Meditation, 10 min** (out of combat) → doubles duration, +1 Move step beyond base.
- **Defense:** self.

---

## 6. Execution plan
1. This schema is canonical. Apply §1 to every power, output per §3, defaults per §2/§4.
2. Work in **batches by book/section**; verify (tag balance, statgrid integrity, node --check) and **push each batch**.
3. **Gap-audit** each power; default by type; surface to James only calls that can't be defaulted, plus any power that looks *mechanically* incomplete (missing a resist, a range, a defense).
4. Update this doc if a global ruling changes.

## 7. Open (set as we go, not blocking)
- Per-power FP→range eligibility (default: no; yes only for ranged energy/TK projection).
- Per-power FP cap eligibility (default: uncapped for dumps; judgement elsewhere).
- Whether sheet power entries mirror the new fields (planned after the compendium pass).
