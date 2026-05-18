"""Inventory checks and deductions."""
from __future__ import annotations

from collections import defaultdict

from . import data, units


def aggregate_needs(plan: list[dict]) -> dict[str, dict]:
    """Sum ingredient needs across a list of {recipe, qty} entries.

    plan: [{"recipe": "sourdough-loaf", "qty": 2}, ...]
    Returns {item_slug: {"qty": float, "unit": "g"}} in canonical units.
    """
    recipes = data.recipes()
    needs: dict[str, dict] = defaultdict(lambda: {"qty": 0.0, "unit": ""})

    for entry in plan:
        slug = entry["recipe"]
        qty = entry["qty"]
        if slug not in recipes:
            raise KeyError(f"Unknown recipe: {slug}")
        for ing in recipes[slug]["ingredients"]:
            base_qty, base_unit = units.to_base(ing["qty"] * qty, ing["unit"])
            current = needs[ing["item"]]
            current["qty"] += base_qty
            current["unit"] = base_unit
    return dict(needs)


def check(plan: list[dict]) -> dict:
    """Compare planned needs vs current stock. Returns a status report."""
    inv = data.inventory()
    needs = aggregate_needs(plan)
    have: list[dict] = []
    short: list[dict] = []

    for item, need in needs.items():
        stock = inv.get(item)
        if stock is None:
            short.append({"item": item, "needed": need["qty"], "unit": need["unit"], "have": 0, "missing": need["qty"]})
            continue
        # Convert stock to the canonical unit
        stock_qty, stock_unit = units.to_base(stock["qty"], stock["unit"])
        if stock_unit != need["unit"]:
            short.append({"item": item, "needed": need["qty"], "unit": need["unit"], "have": 0,
                          "missing": need["qty"], "note": f"unit mismatch ({stock_unit} vs {need['unit']})"})
            continue
        if stock_qty >= need["qty"]:
            have.append({"item": item, "needed": round(need["qty"], 2), "unit": need["unit"],
                         "have": round(stock_qty, 2)})
        else:
            short.append({"item": item, "needed": round(need["qty"], 2), "unit": need["unit"],
                          "have": round(stock_qty, 2), "missing": round(need["qty"] - stock_qty, 2)})

    return {"have": have, "short": short, "ok": len(short) == 0}


def deduct(plan: list[dict]) -> dict:
    """Subtract planned ingredient needs from inventory. Persists to disk."""
    inv = data.inventory()
    needs = aggregate_needs(plan)
    changes: list[dict] = []
    for item, need in needs.items():
        if item not in inv:
            changes.append({"item": item, "skipped": True, "reason": "not tracked"})
            continue
        stock_qty_base, base_unit = units.to_base(inv[item]["qty"], inv[item]["unit"])
        if base_unit != need["unit"]:
            changes.append({"item": item, "skipped": True, "reason": "unit mismatch"})
            continue
        new_base = max(0.0, stock_qty_base - need["qty"])
        # Write back in the inventory's display unit
        new_display = units.convert(new_base, base_unit, inv[item]["unit"])
        before = inv[item]["qty"]
        inv[item]["qty"] = round(new_display, 2)
        changes.append({"item": item, "before": before, "after": inv[item]["qty"], "unit": inv[item]["unit"]})
    data.save("inventory", inv)
    return {"changes": changes}
