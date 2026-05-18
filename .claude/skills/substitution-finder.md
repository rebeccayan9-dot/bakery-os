---
name: substitution-finder
description: Suggest ingredient swaps when something is missing or unwanted (allergies, dietary, ran out). Returns ratios and technique notes.
---

# substitution-finder

Use when the user says *"I'm out of buttermilk,"* *"can I swap butter for oil?"*, or *"make the brownies dairy-free."*

## How to run

```bash
# Full table
python3 -m bakery subs

# One ingredient
python3 -m bakery subs buttermilk
```

Output (per item):
```json
[
  { "replacement": "milk + acid", "ratio": 1.0, "notes": "1 cup milk + 1 tbsp lemon juice or vinegar, rest 5 min" }
]
```

## Notes for Claude

- The `ratio` is "how much replacement per unit of original" — `0.75` means use 75% by weight.
- If the substitution requires adjusting other ingredients (e.g., reducing liquid when swapping honey for sugar), call that out explicitly.
- After a substitution, the recipe's ingredient list is no longer accurate — offer to re-scale or re-cost the modified version.
- If the requested ingredient isn't in the substitutions table, fall back on your baking knowledge but say "this isn't from the saved table" so the user knows it's general advice.
