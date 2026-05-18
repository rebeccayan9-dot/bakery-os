"use client";

import { useState, useTransition } from "react";

type Scaled = {
  multiplier: number;
  yield: { count: number; unit: string };
  ingredients: { item: string; qty: number; unit: string }[];
};

type CostResult = {
  ingredient_cost: number;
  total_cost: number;
  cost_per_unit: number;
  yield_unit: string;
  currency: string;
};

export function ScaleControls({
  slug,
  baseCount,
  unit,
}: {
  slug: string;
  baseCount: number;
  unit: string;
}) {
  const [target, setTarget] = useState<number>(baseCount);
  const [scaled, setScaled] = useState<Scaled | null>(null);
  const [cost, setCost] = useState<CostResult | null>(null);
  const [pending, start] = useTransition();
  const [error, setError] = useState<string | null>(null);

  const run = () => {
    setError(null);
    start(async () => {
      try {
        const [scaleRes, costRes] = await Promise.all([
          fetch("/api/scale", {
            method: "POST",
            headers: { "content-type": "application/json" },
            body: JSON.stringify({ slug, target_count: target }),
          }).then((r) => r.json()),
          fetch("/api/cost", {
            method: "POST",
            headers: { "content-type": "application/json" },
            body: JSON.stringify({ slug, multiplier: target / baseCount }),
          }).then((r) => r.json()),
        ]);
        setScaled(scaleRes);
        setCost(costRes);
      } catch (e) {
        setError(String(e));
      }
    });
  };

  return (
    <section className="card">
      <div className="flex flex-wrap items-end gap-4">
        <label className="flex flex-col text-sm">
          <span className="mb-1 text-stone-500">Scale to</span>
          <div className="flex items-center gap-2">
            <input
              type="number"
              min={1}
              value={target}
              onChange={(e) => setTarget(Number(e.target.value))}
              className="input w-24"
            />
            <span className="text-sm text-stone-600">{unit}</span>
          </div>
        </label>
        <button onClick={run} disabled={pending} className="btn">
          {pending ? "Scaling…" : "Scale + price"}
        </button>
        {error && <span className="text-sm text-rose-600">{error}</span>}
      </div>

      {scaled && (
        <div className="mt-5 grid gap-5 sm:grid-cols-2">
          <div>
            <div className="mb-2 text-xs uppercase tracking-wide text-stone-400">Scaled ingredients</div>
            <ul className="divide-y divide-stone-100 text-sm">
              {scaled.ingredients.map((ing, i) => (
                <li key={i} className="flex justify-between py-1.5">
                  <span>{ing.item.replace(/-/g, " ")}</span>
                  <span className="font-mono text-stone-600">{ing.qty} {ing.unit}</span>
                </li>
              ))}
            </ul>
          </div>
          {cost && (
            <div>
              <div className="mb-2 text-xs uppercase tracking-wide text-stone-400">Ingredient cost</div>
              <div className="space-y-1 text-sm">
                <Row label="Ingredients" value={`$${cost.ingredient_cost.toFixed(2)}`} />
                <Row label="Total batch" value={`$${cost.total_cost.toFixed(2)}`} />
                <Row label={`Per ${cost.yield_unit}`} value={`$${cost.cost_per_unit.toFixed(2)}`} strong />
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}

function Row({ label, value, strong }: { label: string; value: string; strong?: boolean }) {
  return (
    <div className={`flex justify-between ${strong ? "border-t border-stone-200 pt-2 font-medium" : ""}`}>
      <span className="text-stone-500">{label}</span>
      <span className="font-mono">{value}</span>
    </div>
  );
}
