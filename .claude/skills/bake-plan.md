---
name: bake-plan
description: Build a backward-scheduled timeline from a target ready time. Tells you when to start each step so the bake is ready when you want it. Flags oven conflicts when two recipes need different temperatures at the same time.
---

# bake-plan

Use when the user says *"I want fresh sourdough Sunday at 9am,"* *"plan my Saturday baking,"* or *"when should I start the cinnamon rolls if I want them ready at 8am?"*

## How to run

Inline (one or more bakes):

```bash
python3 -m bakery plan \
  --bake "sourdough-loaf:1@2026-05-24T09:00" \
  --bake "brownies:1@2026-05-24T10:00"
```

Format: `<slug>[:qty]@<ISO-8601 datetime>` (no timezone needed; uses local).

From JSON on stdin:

```bash
echo '[{"recipe":"sourdough-loaf","qty":1,"ready_at":"2026-05-24T09:00"}]' \
  | python3 -m bakery plan --from-stdin
```

Output:
```json
{
  "overall_start": "2026-05-23T15:15",
  "timeline": [{"start": "...", "end": "...", "step": "mix", "active": true, ...}],
  "oven_conflicts": [...],
  "oven_capacity": 1
}
```

## Notes for Claude

- Lead the reply with `overall_start` — that's the single most important number to the user.
- If `oven_conflicts` is non-empty, surface them clearly: same time slot, different temps, single oven. Suggest staggering the ready times by ~30min or asking which to bake first.
- Group the timeline by recipe in your reply if the user has multiple bakes — interleaved steps are confusing to read flat.
- Active steps require attention (mix, shape, glaze); passive steps are wait time (proof, bake). Highlight active blocks so the user knows when they need to be in the kitchen.
