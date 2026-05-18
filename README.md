# 🥐 Bakery OS

A personal home-baking assistant: a small set of agentic skills wrapped around
a Python toolkit and a Next.js dashboard. Built for one cook, not a storefront.

**🌐 Live demo:** https://bakery-os-six.vercel.app/

The Vercel deploy runs in read-only **demo mode** — pages render with real data
but interactive features (scale, plan, shopping, capture) require the Python
CLI and only work when you clone and run locally (see [Setup](#setup) below).

---

## 1. Purpose of this agentic OS

Bakery OS is a **personal operating system for a home baker.** It treats every
common chore that happens around a recipe — scaling, costing, scheduling,
shopping, substituting, journaling, even ingesting a recipe from a YouTube
video — as a discrete *skill* that an LLM agent can pick up and chain.

The point isn't to automate baking itself (the oven still does the work). The
point is to remove the **friction around** baking: the napkin math on
quantities, the "do I have enough butter?" pantry check, the "when do I start
the dough if I want fresh sourdough Sunday at 9am?" arithmetic, and the
"I just watched a great video, can I save this recipe?" capture problem.

---

## 2. How this agentic OS addresses my need

I bake for myself, irregularly, from a growing pile of recipes and YouTube
videos. The actual baking is fun. The friction is everything else:

- **Recipes don't match the batch I want.** I want 6 cookies, not 24. Or I want a triple-batch of focaccia for a dinner party.
  → `recipe-scale` resizes recipes by count or multiplier, and intelligently scales *active* step time (mixing, shaping) without scaling *passive* time (proof, bake).

- **I open the fridge mid-recipe and discover I'm out of butter.**
  → `pantry-check` runs the diff before I start. `substitution-finder` rescues me if I've already started.

- **I shop without a list and forget half the things.**
  → `shopping-list` diffs my planned bakes against the pantry, pads each missing quantity by 10% so I don't run out mid-recipe, and estimates the cost.

- **Timing is genuinely hard for fermented bakes.** Sourdough has 6 steps over 14 hours. "I want a fresh loaf at 9am Sunday" means starting at *3:15pm Saturday*.
  → `bake-plan` walks every step backward from a target ready time and tells me when to start. It flags oven collisions when two recipes want different temperatures at once.

- **I save recipes by emailing YouTube links to myself, then never look at them.**
  → `recipe-from-youtube` pulls the auto-captions via `yt-dlp`, structures them into the canonical recipe schema, and saves the result. The video itself becomes a recipe I can scale, price, and plan.

- **I never document what I baked or what I'd change next time.**
  → `bake-log` drafts a 5-line journal entry or social caption pulling specifics from the recipe.

- **Mornings feel chaotic.**
  → `daily-brief` composes the schedule, pantry check, and shopping list into one 30-second glance.

The agent makes these into a fluent conversation: I say *"I want sourdough
and brownies ready Saturday morning,"* and the agent chains `bake-plan` →
`pantry-check` → `shopping-list` without me thinking about which tool fires
when. The dashboard exists for moments when I'd rather click than chat.

---

## 3. Skills in this OS

Each skill is a single markdown file in `.claude/skills/` that Claude reads
on-demand. Skills shell out to `python -m bakery <command>`.

| Skill                  | What it does                                                                  |
| ---------------------- | ----------------------------------------------------------------------------- |
| `recipe-scale`         | Resize a recipe to N units or a multiplier. Handles unit conversion.          |
| `pantry-check`         | Compare a planned bake against pantry stock. Returns shortages.               |
| `shopping-list`        | Diff plan vs pantry → grocery list with quantities, units, estimated cost.    |
| `cost-calculator`      | Per-recipe ingredient cost; cost per cookie/loaf/square.                      |
| `bake-plan`            | Backward-schedule from a target ready time. Flags oven conflicts.             |
| `substitution-finder`  | Suggest swaps for missing or allergenic ingredients with ratios + notes.      |
| `recipe-from-youtube`  | Pull captions from a YouTube URL via `yt-dlp`; structure into recipe JSON.    |
| `bake-log`             | Draft a personal journal entry or social post about a finished bake.          |
| `daily-brief`          | Composed morning report: schedule + pantry + shopping in one glance.          |

### How skills collaborate (chains)

The interesting work happens when skills compose. A few realistic chains:

**Chain 1 — "Plan Saturday's bakes"**
```
bake-plan ── computes when to start each recipe
   ↓
pantry-check ── verifies I have everything
   ↓
shopping-list ── builds the grocery run for whatever's short
   ↓
daily-brief ── wraps it all into a 30-second morning glance
```

**Chain 2 — "Save this YouTube video as a recipe"**
```
recipe-from-youtube ── pulls captions, structures into the recipe schema
   ↓
cost-calculator ── now that the recipe exists, what does one batch cost?
   ↓
recipe-scale ── scale to the actual batch size I want to bake
   ↓
pantry-check ── do I have everything for this brand new recipe?
```

**Chain 3 — "I'm out of buttermilk, mid-prep"**
```
substitution-finder ── suggests milk + acid at 1:1 ratio
   ↓
recipe-scale ── re-scales the recipe with the substitute factored in
   ↓
shopping-list ── updated to reflect the swap (drop buttermilk, add lemon)
```

**Chain 4 — "What does this hobby cost me?"**
```
cost-calculator ── for each recipe in rotation
   ↓
[Claude aggregates] ── ranks by cost-per-bake, identifies cheapest staples
```

Each skill is small and JSON-in/JSON-out, which is what makes the chaining
clean. The agent doesn't need to parse natural language between steps — every
skill produces structured output the next skill can consume.

---

## Project layout

```
bakery-os/
├── bakery/           # Python package + CLI (the logic)
│   ├── __main__.py   # `python -m bakery <cmd>`
│   ├── scale.py      # recipe scaling
│   ├── inventory.py  # pantry check + deduct
│   ├── shopping.py   # diff plan vs pantry
│   ├── cost.py       # per-recipe cost
│   ├── schedule.py   # backward-pass bake scheduler
│   ├── youtube.py    # yt-dlp wrapper for captions
│   ├── units.py      # mass/volume/count conversion
│   └── data.py       # JSON loaders
├── data/             # JSON state — no database
│   ├── recipes.json
│   ├── inventory.json
│   ├── substitutions.json
│   └── config.json
├── web/              # Next.js 15 dashboard
│   ├── app/          # pages: /, /recipes, /pantry, /plan, /shopping
│   └── app/api/      # routes that shell out to the Python CLI
└── .claude/skills/   # the 9 agentic skills
```

## Setup

### Python

```bash
pip install -e .
pipx install yt-dlp     # needed for recipe-from-youtube
```

Quick sanity check:

```bash
python -m bakery recipes
python -m bakery scale sourdough-loaf --count 2
python -m bakery plan --bake "sourdough-loaf:1@2026-05-24T09:00"
python -m bakery cost chocolate-chip-cookies
```

### Web dashboard

```bash
cd web
npm install
npm run dev
# open http://localhost:3000
```

The dashboard reads `data/*.json` directly via server components, and posts
to `/api/*` routes which shell out to the Python CLI — so the Python install
above is required for the dashboard's interactive features.

## Design notes

- **Active vs passive time.** Scaling a recipe scales active step time linearly with batch size (more dough = more shaping). Passive time (proof, bake) does not — physics doesn't care about batch size.
- **Backward scheduling.** `bake-plan` walks each recipe's steps in reverse from the target ready time, so the user gets a single "start at X" answer.
- **Oven conflicts.** With `oven_capacity: 1`, the scheduler flags any window where two recipes want the oven at different temperatures.
- **No labor cost by default.** Personal use means time spent kneading is hobby, not overhead. Flip `labor_rate_per_hour` in `config.json` if you want to value your time.
