---
name: pantry-check
description: Inspect home pantry stock and check whether a planned bake (or set of bakes) has enough of every ingredient. Identifies shortages and what specifically is missing.
---

# pantry-check

Use when the user asks *"do I have everything to make X?"*, *"what am I out of?"*, or *"check my pantry."*

## How to run

```bash
# Show full pantry
python3 -m bakery inventory

# Check a planned bake against pantry
python3 -m bakery check "sourdough-loaf:2,brownies:1"
```

The plan argument is a comma-separated list of `slug:qty` pairs.

Output for `check`:
```json
{ "have": [...], "short": [{"item": "butter", "needed": 450, "have": 200, "missing": 250, "unit": "g"}], "ok": false }
```

## Notes for Claude

- If `ok` is true, just confirm — no further action needed.
- If `ok` is false, surface the short list in plain English and offer to either run `shopping-list` (to build a grocery run) or `substitution-finder` (to swap missing items).
- Units in the output are canonical (g, ml, each). Display in user-friendly form if asked.
- After a bake is actually completed, the user can run `python3 -m bakery deduct <plan>` to subtract used ingredients — this persists to `data/inventory.json`.
