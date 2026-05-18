---
name: cost-calculator
description: Compute the ingredient cost of a recipe (and optionally a scaled batch). Useful for "how much does this hobby cost me?" or comparing two recipes by ingredient spend.
---

# cost-calculator

Use when the user asks *"how much does it cost to make X?"*, *"what's the cost per cookie?"*, or *"compare cost of brownies vs cookies."*

## How to run

```bash
python3 -m bakery cost <slug> [--multiplier 2.0]
```

Output:
```json
{
  "ingredient_cost": 6.42,
  "labor_cost": 0,
  "overhead": 0,
  "total_cost": 6.42,
  "yield_count": 24,
  "yield_unit": "cookies",
  "cost_per_unit": 0.27,
  "currency": "USD"
}
```

## Notes for Claude

- For personal use, `labor_cost` and `overhead` default to 0 — only ingredients count. The user can flip those on in `data/config.json` if they want to value their time.
- The `lines` array shows per-ingredient cost; surface the top 3 cost drivers if the user is curious "what's making this expensive."
- A line with `"note": "not in inventory"` means the recipe references an ingredient the pantry doesn't track — that line's cost is null. Mention this so they can add a price.
