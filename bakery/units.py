"""Unit conversion for bakery ingredients.

We track three categories:
  - mass:   g, kg, oz, lb
  - volume: ml, l, tsp, tbsp, cup, floz
  - count:  each

Cross-category conversion (volume→mass) is intentionally not supported here;
recipes should normalize to grams or milliliters at ingestion.
"""
from __future__ import annotations

MASS_TO_G = {"g": 1.0, "kg": 1000.0, "oz": 28.3495, "lb": 453.592}
VOL_TO_ML = {"ml": 1.0, "l": 1000.0, "tsp": 4.92892, "tbsp": 14.7868, "cup": 236.588, "floz": 29.5735}
COUNT_UNITS = {"each", "ea", "count"}


def category(unit: str) -> str:
    u = unit.lower()
    if u in MASS_TO_G:
        return "mass"
    if u in VOL_TO_ML:
        return "volume"
    if u in COUNT_UNITS:
        return "count"
    raise ValueError(f"Unknown unit: {unit!r}")


def to_base(qty: float, unit: str) -> tuple[float, str]:
    """Convert to the canonical base unit for its category (g, ml, or each)."""
    cat = category(unit)
    if cat == "mass":
        return qty * MASS_TO_G[unit.lower()], "g"
    if cat == "volume":
        return qty * VOL_TO_ML[unit.lower()], "ml"
    return qty, "each"


def convert(qty: float, from_unit: str, to_unit: str) -> float:
    if category(from_unit) != category(to_unit):
        raise ValueError(f"Cannot convert {from_unit} → {to_unit} (different categories)")
    base, _ = to_base(qty, from_unit)
    if category(to_unit) == "mass":
        return base / MASS_TO_G[to_unit.lower()]
    if category(to_unit) == "volume":
        return base / VOL_TO_ML[to_unit.lower()]
    return base


def compatible(a: str, b: str) -> bool:
    try:
        return category(a) == category(b)
    except ValueError:
        return False
