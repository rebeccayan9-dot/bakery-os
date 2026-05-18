"""Build a shopping list from a production plan."""
from __future__ import annotations

from . import data, inventory, units


def shopping_list(plan: list[dict], *, buffer: float = 1.10) -> dict:
    """Diff planned needs against stock; suggest a shopping list.

    buffer: pad each missing quantity by this multiplier (default 10%) so we
    don't run out mid-recipe.
    """
    inv = data.inventory()
    check = inventory.check(plan)
    list_items: list[dict] = []
    total_cost = 0.0

    for short in check["short"]:
        item = short["item"]
        missing = short["missing"] * buffer
        stock = inv.get(item)
        if stock is None:
            list_items.append({"item": item, "qty": round(missing, 2), "unit": short["unit"],
                               "est_cost": None, "note": "new ingredient — not in inventory"})
            continue
        # Convert missing back to inventory's display unit for the shopping list
        display_qty = units.convert(missing, short["unit"], stock["unit"])
        cost = display_qty * stock["price_per_unit"]
        total_cost += cost
        list_items.append({
            "item": item,
            "name": stock["name"],
            "qty": round(display_qty, 2),
            "unit": stock["unit"],
            "est_cost": round(cost, 2),
        })

    cfg = data.config()
    return {
        "items": list_items,
        "estimated_total": round(total_cost, 2),
        "currency": cfg.get("currency", "USD"),
        "buffer_pct": round((buffer - 1) * 100, 1),
    }
