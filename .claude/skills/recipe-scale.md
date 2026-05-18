---
name: recipe-scale
description: Resize a saved recipe to a target number of units or a multiplier. Handles unit conversions, scales active step times linearly with batch size, leaves passive steps (proof, bake) untouched.
---

# recipe-scale

Use when the user says things like *"scale the sourdough recipe to 3 loaves,"* *"halve the cookie recipe,"* or *"how much butter do I need for a double batch of brownies?"*

## How to run

Shell out to the bakery CLI:

```bash
# By target unit count
python3 -m bakery scale <slug> --count <N>

# By multiplier
python3 -m bakery scale <slug> --multiplier 0.5
```

Output is JSON: `{slug, name, multiplier, yield, ingredients, steps, tags}`.

## Notes for Claude

- If the user names a recipe in prose, look it up first with `python3 -m bakery recipes` to find the matching slug.
- Active step time scales with batch size (more dough = more shaping time). Passive time (fermentation, baking) does not — physics doesn't care about batch size.
- After scaling, present ingredient quantities rounded to baker-friendly numbers (e.g. 337g → "335g" or "1⅓ cups"). The raw output is exact; you can round in your reply.
- If the user wants the recipe priced after scaling, chain with `cost-calculator`.
