---
name: daily-brief
description: Composed morning report. Pulls today's planned bakes, the schedule, low pantry items, and any shopping needs into one tight summary. Chains pantry-check, bake-plan, and shopping-list under the hood.
---

# daily-brief

Use when the user says *"what's on for today,"* *"morning brief,"* or *"what do I need to do this morning?"*

## How to run

Ask the user (briefly) for **today's bake list** if it's not obvious from context. Format each as `slug:qty@ready-time`.

Then chain:

```bash
# 1. Schedule
python3 -m bakery plan --bake "<slug>:<qty>@<iso>" ...

# 2. Inventory check
python3 -m bakery check "<slug>:<qty>,..."

# 3. Shopping (only if the check shows shortages)
python3 -m bakery shop "<slug>:<qty>,..."

# 4. Show pantry low items
python3 -m bakery inventory   # filter to items with qty < threshold
```

## Output format

Compose the reply as four short blocks:

```
☀️ Today (<date>)

⏱  Start at <overall_start> — <total active time> active, <total passive>m passive
   • <step 1 — recipe — time>
   • <step 2 — recipe — time>
   • ...

🥣 Pantry: ✅ all set   OR   ⚠ short on: <items>
🛒 Shopping run: <total estimate>   (or "none needed")
```

## Notes for Claude

- Keep it scannable — this runs as a 30-second morning glance.
- If there are oven conflicts in the plan, lead with that warning before the timeline.
- If the pantry's fully stocked AND no shopping needed, omit those lines entirely — silence is fine.
- Default to "now" when the user doesn't specify a ready time — schedule for end-of-day at 6pm and ask if they want to adjust.
