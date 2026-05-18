---
name: shopping-list
description: Diff a planned bake against the pantry to produce a grocery list with quantities and estimated costs. Pads each missing quantity by a configurable buffer so you don't run out mid-recipe.
---

# shopping-list

Use when the user says *"what do I need to buy for Saturday's baking,"* *"build a shopping list,"* or after `pantry-check` reports shortages.

## How to run

```bash
python3 -m bakery shop "sourdough-loaf:2,brownies:1" [--buffer 1.10]
```

`--buffer 1.10` (default) adds a 10% safety pad on each short item. Set to `1.0` for exact.

Output:
```json
{ "items": [{"item": "butter", "name": "Unsalted Butter", "qty": 250, "unit": "g", "est_cost": 3.00}], "estimated_total": 5.42, "currency": "USD" }
```

## Notes for Claude

- If `items` is empty, the user is fully stocked — say so cheerfully.
- Items flagged `"note": "new ingredient — not in inventory"` are ingredients the pantry has never tracked; the cost is null and the user may want to add them to `data/inventory.json` after purchase.
- Group the list by category in your reply (e.g., dairy, flour, mix-ins) — categories live in `data/inventory.json`.
