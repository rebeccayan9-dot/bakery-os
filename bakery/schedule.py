"""Backward-pass bake scheduler for personal use.

Given a list of bakes with target ready times (e.g. "I want sourdough ready
Sunday at 9am"), work backward through each recipe's steps to compute when
to start. Detect oven collisions against the configured oven capacity.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from . import data


def _parse(iso: str) -> datetime:
    return datetime.fromisoformat(iso)


def plan_bakes(bakes: list[dict]) -> dict:
    """bakes: [{"recipe": slug, "qty": int, "ready_at": iso}].

    Returns a timeline of steps sorted by start time, plus any oven conflicts.
    """
    cfg = data.config()
    recipes = data.recipes()

    timeline: list[dict] = []
    oven_blocks: list[dict] = []

    for bake in bakes:
        slug = bake["recipe"]
        qty = bake.get("qty", 1)
        ready_at = _parse(bake["ready_at"])
        if slug not in recipes:
            continue
        recipe = recipes[slug]

        cursor = ready_at
        steps_for_item: list[dict] = []
        for step in reversed(recipe["steps"]):
            duration = step["duration_min"]
            if step.get("active"):
                duration = duration * qty
            end = cursor
            start = end - timedelta(minutes=duration)
            steps_for_item.append({
                "recipe": slug,
                "recipe_name": recipe["name"],
                "qty": qty,
                "step": step["name"],
                "active": bool(step.get("active")),
                "start": start.isoformat(timespec="minutes"),
                "end": end.isoformat(timespec="minutes"),
                "duration_min": round(duration, 1),
            })
            if step.get("oven"):
                oven_blocks.append({
                    "recipe": slug,
                    "qty": qty,
                    "start": start,
                    "end": end,
                    "temp_f": step.get("oven_temp_f"),
                })
            cursor = start
        steps_for_item.reverse()
        timeline.extend(steps_for_item)

    timeline.sort(key=lambda s: s["start"])
    overall_start = timeline[0]["start"] if timeline else None

    capacity = cfg.get("oven_capacity", 1)
    conflicts: list[dict] = []
    sorted_blocks = sorted(oven_blocks, key=lambda b: b["start"])
    for i, a in enumerate(sorted_blocks):
        overlapping = [a]
        for b in sorted_blocks[i + 1:]:
            if b["start"] < a["end"]:
                overlapping.append(b)
        if len(overlapping) > capacity:
            temps = {ov["temp_f"] for ov in overlapping if ov.get("temp_f")}
            conflicts.append({
                "window_start": a["start"].isoformat(timespec="minutes"),
                "window_end": min(ov["end"] for ov in overlapping).isoformat(timespec="minutes"),
                "blocks": [{"recipe": ov["recipe"], "temp_f": ov.get("temp_f")} for ov in overlapping],
                "capacity": capacity,
                "temp_spread": sorted(temps),
            })

    return {
        "overall_start": overall_start,
        "timeline": timeline,
        "oven_conflicts": conflicts,
        "oven_capacity": capacity,
    }
