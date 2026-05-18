"""Per-recipe cost calculation."""
from __future__ import annotations

from . import data, units


def recipe_cost(slug: str, *, multiplier: float = 1.0) -> dict:
    recipes = data.recipes()
    inv = data.inventory()
    cfg = data.config()

    if slug not in recipes:
        raise KeyError(f"Unknown recipe: {slug}")
    recipe = recipes[slug]

    lines: list[dict] = []
    ingredient_cost = 0.0
    for ing in recipe["ingredients"]:
        item = inv.get(ing["item"])
        if item is None:
            lines.append({"item": ing["item"], "qty": ing["qty"], "unit": ing["unit"],
                          "cost": None, "note": "not in inventory"})
            continue
        qty = ing["qty"] * multiplier
        # Convert ingredient qty to inventory unit, then multiply by price_per_unit
        if not units.compatible(ing["unit"], item["unit"]):
            lines.append({"item": ing["item"], "qty": qty, "unit": ing["unit"],
                          "cost": None, "note": "unit mismatch"})
            continue
        qty_in_inv_unit = units.convert(qty, ing["unit"], item["unit"])
        cost = qty_in_inv_unit * item["price_per_unit"]
        ingredient_cost += cost
        lines.append({"item": ing["item"], "name": item["name"], "qty": round(qty, 2),
                      "unit": ing["unit"], "cost": round(cost, 3)})

    active_minutes = sum(s["duration_min"] for s in recipe["steps"] if s.get("active")) * multiplier
    labor_cost = (active_minutes / 60.0) * cfg.get("labor_rate_per_hour", 0)
    overhead = ingredient_cost * cfg.get("overhead_pct", 0)
    total = ingredient_cost + labor_cost + overhead

    yield_count = recipe["yield"]["count"] * multiplier
    per_unit = total / yield_count if yield_count else total

    return {
        "slug": slug,
        "name": recipe["name"],
        "multiplier": multiplier,
        "lines": lines,
        "ingredient_cost": round(ingredient_cost, 2),
        "labor_minutes": round(active_minutes, 1),
        "labor_cost": round(labor_cost, 2),
        "overhead": round(overhead, 2),
        "total_cost": round(total, 2),
        "yield_count": round(yield_count, 2),
        "yield_unit": recipe["yield"]["unit"],
        "cost_per_unit": round(per_unit, 2),
        "currency": cfg.get("currency", "USD"),
    }
