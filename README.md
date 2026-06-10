# Star Wars KOTOR · GURPS 4e — Campaign Database

Live site: **https://recoson.github.io/Star-wars-GURPS-campaign/**

| What | Where |
|---|---|
| Campaign hub | [index.html](https://recoson.github.io/Star-wars-GURPS-campaign/) |
| Star Wars the Old Republic — GURPS 4E Conversion (the rulebook, 12 documents) | [Star Wars the Old Republic GURPS 4E conversion.html](https://recoson.github.io/Star-wars-GURPS-campaign/Star%20Wars%20the%20Old%20Republic%20GURPS%204E%20conversion.html) |
| Character sheet | [sheet.html](https://recoson.github.io/Star-wars-GURPS-campaign/sheet.html) |
| Galaxy Map (hyperspace travel) | [galaxy-map.html](https://recoson.github.io/Star-wars-GURPS-campaign/galaxy-map.html) |
| Galactic Record (lore) | [galactic-record.html](https://recoson.github.io/Star-wars-GURPS-campaign/galactic-record.html) |
| GM Console | [KOTOR_GM_Console_v4.html](https://recoson.github.io/Star-wars-GURPS-campaign/KOTOR_GM_Console_v4.html) — GM eyes only |
| Combat Cheatsheet (A3, double-sided) | [HTML](https://recoson.github.io/Star-wars-GURPS-campaign/Combat_Cheatsheet_A3.html) · [print PDF](https://recoson.github.io/Star-wars-GURPS-campaign/Combat_Cheatsheet_A3.pdf) |
| Characters (one JSON each) | [/characters](characters/) — open via `sheet.html?char=<name>` |

## How characters work
- Open a character from the hub (or `sheet.html?char=chatni`). The sheet autosaves locally in your browser as you play.
- **☁ Save** writes your character back here; with a token stored, the sheet also **auto-saves to the cloud** ~60s after each burst of edits and when you close the tab.
- Tokens: fine-grained personal access token with *Contents: read/write* on this repo, entered once per browser.
- Every save is a git commit: full history, nothing is ever lost.

## Combat systems (sheet ⇄ compendium, simulation-verified)
- **Personal scale:** GURPS 4e with campaign rules — AD(1) standard blasters (hard armour tiers), ion/disruptor as distinct types, metric (1 m = 1 hex).
- **Ships & droids: components ARE the health.** No HP pools — shields soak → DR (weapons carry flat **AP** that ignores that much DR; damage is 1:1, no dividing — AD applies only cross-scale) → Damage Threshold degrades the struck system (● → ◐ → ✕). Vaporisation at ≥6×DT. Ion: ×2 vs shields, never structural.
- Sheet tools: 🔫 Fire (Gunner roller), ⚔ Incoming hit (full pipeline), 🛡 live Dodge readout (3 + Pilot÷3 + Hnd), ⟳ shield regen, 🔧 damage control.
- Canon for all of it: compendium Part VIII (*Components Are the Health*, *Ship-to-Ship Defence & Scale*, repair ladder).
