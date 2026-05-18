"""CLI: `python -m bakery <command> [args]`.

All commands print JSON to stdout so skills and the Next.js dashboard can
parse output directly.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

from . import cost, data, inventory, scale, schedule, shopping, youtube


def _emit(value) -> None:
    json.dump(value, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


def _parse_plan(arg: str) -> list[dict]:
    """'sourdough-loaf:2,brownies:1' → [{recipe, qty}, ...]."""
    out = []
    for chunk in arg.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        slug, _, qty = chunk.partition(":")
        out.append({"recipe": slug.strip(), "qty": int(qty) if qty else 1})
    return out


_BAKE_RE = re.compile(r"^(?P<slug>[^:@]+)(?::(?P<qty>\d+))?@(?P<ready>.+)$")


def _parse_bake(arg: str) -> dict:
    """'sourdough-loaf:1@2026-05-24T09:00' → {recipe, qty, ready_at}."""
    m = _BAKE_RE.match(arg.strip())
    if not m:
        raise ValueError(f"Bad bake spec {arg!r}; expected slug[:qty]@iso8601")
    return {
        "recipe": m["slug"],
        "qty": int(m["qty"]) if m["qty"] else 1,
        "ready_at": m["ready"],
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="bakery", description="Personal home-bakery CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    s_recipes = sub.add_parser("recipes", help="List recipes")
    s_recipes.add_argument("--slug")

    sub.add_parser("inventory", help="Show pantry inventory")

    s_scale = sub.add_parser("scale", help="Scale a recipe")
    s_scale.add_argument("slug")
    g = s_scale.add_mutually_exclusive_group(required=True)
    g.add_argument("--multiplier", type=float)
    g.add_argument("--count", type=int, dest="target_count")

    s_check = sub.add_parser("check", help="Check pantry against a plan")
    s_check.add_argument("plan", help="'slug:qty,slug:qty'")

    s_shop = sub.add_parser("shop", help="Build a shopping list")
    s_shop.add_argument("plan")
    s_shop.add_argument("--buffer", type=float, default=1.10)

    s_cost = sub.add_parser("cost", help="Compute recipe cost")
    s_cost.add_argument("slug")
    s_cost.add_argument("--multiplier", type=float, default=1.0)

    s_plan = sub.add_parser("plan", help="Bake schedule from target ready times")
    s_plan.add_argument("--bake", action="append", default=[],
                        help="Repeatable: slug[:qty]@iso8601 (e.g. sourdough-loaf:1@2026-05-24T09:00)")
    s_plan.add_argument("--from-stdin", action="store_true",
                        help="Read JSON list of {recipe,qty,ready_at} from stdin instead")

    s_subs = sub.add_parser("subs", help="Look up substitutions")
    s_subs.add_argument("item", nargs="?")

    s_yt = sub.add_parser("youtube", help="Fetch YouTube transcript + metadata")
    s_yt.add_argument("url")
    s_yt.add_argument("--lang", default="en")

    s_deduct = sub.add_parser("deduct", help="Deduct a plan from pantry (persists)")
    s_deduct.add_argument("plan")

    s_save = sub.add_parser("save-recipe", help="Add a recipe (reads JSON from stdin)")
    s_save.add_argument("slug")

    args = p.parse_args(argv)

    if args.cmd == "recipes":
        recipes = data.recipes()
        _emit(recipes[args.slug] if args.slug else recipes)
    elif args.cmd == "inventory":
        _emit(data.inventory())
    elif args.cmd == "scale":
        _emit(scale.scale_recipe(args.slug, multiplier=args.multiplier, target_count=args.target_count))
    elif args.cmd == "check":
        _emit(inventory.check(_parse_plan(args.plan)))
    elif args.cmd == "shop":
        _emit(shopping.shopping_list(_parse_plan(args.plan), buffer=args.buffer))
    elif args.cmd == "cost":
        _emit(cost.recipe_cost(args.slug, multiplier=args.multiplier))
    elif args.cmd == "plan":
        if args.from_stdin:
            bakes = json.load(sys.stdin)
        else:
            bakes = [_parse_bake(b) for b in args.bake]
        if not bakes:
            print("plan requires at least one --bake or --from-stdin", file=sys.stderr)
            return 2
        _emit(schedule.plan_bakes(bakes))
    elif args.cmd == "subs":
        subs = data.substitutions()
        _emit(subs[args.item] if args.item else subs)
    elif args.cmd == "youtube":
        _emit(youtube.fetch(args.url, lang=args.lang))
    elif args.cmd == "deduct":
        _emit(inventory.deduct(_parse_plan(args.plan)))
    elif args.cmd == "save-recipe":
        body = json.load(sys.stdin)
        recipes = data.recipes()
        recipes[args.slug] = body
        data.save("recipes", recipes)
        _emit({"saved": args.slug, "name": body.get("name")})
    else:
        p.print_help()
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
