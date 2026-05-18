---
name: recipe-from-youtube
description: Extract a structured recipe from a YouTube video. Pulls metadata + auto-generated captions, then structures them into the bakery's recipe schema (ingredients, steps, yield). Optionally saves to recipes.json.
---

# recipe-from-youtube

Use when the user shares a YouTube URL and says *"turn this into a recipe,"* *"save this video as a recipe,"* or *"add this to my recipes."*

## How to run

### 1. Fetch transcript + metadata

```bash
python3 -m bakery youtube "https://www.youtube.com/watch?v=XXXX"
```

Output:
```json
{
  "url": "...",
  "title": "Perfect Sourdough Loaf | Recipe & Technique",
  "channel": "...",
  "description": "...",
  "duration_sec": 720,
  "transcript": "Hello bakers today we're making...",
  "has_transcript": true
}
```

Requires `yt-dlp` (install with `pipx install yt-dlp` or `pip install yt-dlp`).

### 2. Structure the transcript

Read the transcript and produce a JSON object matching this schema:

```json
{
  "name": "Recipe Name",
  "yield": { "count": 1, "unit": "loaf", "weight_g": 900 },
  "ingredients": [
    { "item": "bread-flour", "qty": 500, "unit": "g" }
  ],
  "steps": [
    { "name": "mix", "duration_min": 15, "active": true },
    { "name": "bake", "duration_min": 45, "active": false, "oven": true, "oven_temp_f": 475 }
  ],
  "tags": ["bread", "from-youtube"]
}
```

Rules for structuring:
- **Ingredient slugs** should match the pantry where possible (`data/inventory.json`). For new ingredients, kebab-case the common name.
- **Units**: prefer `g` and `ml`. Convert cups/tbsp/oz to grams when the video implies a clear weight. If only volume is given, keep `cup`/`tbsp`/`tsp`.
- **Steps**: split into `active` (mixing, shaping, decorating) vs passive (rising, baking, resting). Mark `oven: true` and `oven_temp_f` for any oven step.
- **Yield**: capture both count and unit (e.g., 12 muffins, 1 loaf, 9x9 pan = 1 tray).
- Tag with the source: add `"from-youtube"` plus genre tags (bread, cookie, etc.).

### 3. Save it

Pipe your JSON into the save command:

```bash
echo '<json>' | python3 -m bakery save-recipe <slug>
```

Or, from inside Claude: write to `data/recipes.json` directly under the chosen slug.

## Notes for Claude

- **No transcript?** If `has_transcript: false`, tell the user — auto-captions may be disabled. They can paste the recipe text manually and you can structure it the same way.
- **Verify ingredient slugs** against `python3 -m bakery inventory` before saving. New ingredients are fine, just flag them so the user can add prices.
- **Show the structured recipe to the user before saving** when the video is ambiguous about quantities. Better to confirm than to save a wrong recipe.
- Channel attribution is polite — include the channel name in a comment or description field if the user wants to credit later.
- After saving, suggest scaling or pricing it as a sanity check.
