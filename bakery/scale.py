"""Scale a recipe by multiplier or to a target yield."""
from __future__ import annotations

from typing import Any

from . import data


def scale_recipe(slug: str, *, multiplier: float | None = None, target_count: int | None = None) -> dict:
    recipes = data.recipes()
    if slug not in recipes:
        raise KeyError(f"Unknown recipe: {slug}")
    recipe = recipes[slug]

    if multiplier is None and target_count is None:
        raise ValueError("Provide multiplier or target_count")
    if multiplier is None:
        base = recipe["yield"]["count"]
        multiplier = target_count / base

    scaled_ingredients = []
    for ing in recipe["ingredients"]:
        scaled_ingredients.append({
            **ing,
            "qty": round(ing["qty"] * multiplier, 2),
        })

    # Active step time scales linearly with batch size; passive time (proof,
    # bake) does not — physics doesn't care about batch size for fermentation.
    scaled_steps: list[dict[str, Any]] = []
    for step in recipe["steps"]:
        scaled = dict(step)
        if step.get("active"):
            scaled["duration_min"] = round(step["duration_min"] * multiplier, 1)
        scaled_steps.append(scaled)

    return {
        "slug": slug,
        "name": recipe["name"],
        "multiplier": round(multiplier, 3),
        "yield": {
            **recipe["yield"],
            "count": round(recipe["yield"]["count"] * multiplier, 2),
        },
        "ingredients": scaled_ingredients,
        "steps": scaled_steps,
        "tags": recipe.get("tags", []),
    }
