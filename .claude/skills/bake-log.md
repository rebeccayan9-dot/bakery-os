---
name: bake-log
description: Draft a personal bake-log entry or social post about a finished bake — what worked, what to change next time, optional photo caption. Pulls from the recipe and any notes the user shares.
---

# bake-log

Use when the user says *"write up my bake,"* *"draft an Instagram caption for the focaccia,"* or *"log this bake in my journal."*

## How to run

There's no dedicated CLI for this — bake-log is mostly Claude reasoning. Grab context with:

```bash
python3 -m bakery recipes --slug <slug>
```

Then ask the user (briefly) for:
- How did it turn out? Any wins or misses?
- Is this for personal notes or a social post? (different voice)
- Any photo or hashtags they want included?

## Voice presets

- **Personal journal**: warm, specific, terse. 3–5 lines. Note one thing to change next time. No hashtags.
- **Social post (IG/Bluesky)**: 2–3 short paragraphs. Sensory verbs. One small "lesson learned" beat. 3–6 hashtags. No emoji spam.
- **Recipe note** (for the project README or a friend): conversational, mentions hydration/oven temp/timing tweaks the user made.

## Notes for Claude

- Pull the recipe name and a notable ingredient from the recipe JSON to ground the post in specifics.
- If the user mentions a substitution they made, reference it ("subbed olive oil for half the butter — crumb stayed tender").
- Resist generic bakery clichés ("fresh from the oven 🥖✨"). Personal voice = specific details, not adjectives.
- Save the final text to `bake-log/<date>-<slug>.md` if the user wants a persistent record (create the directory on demand).
