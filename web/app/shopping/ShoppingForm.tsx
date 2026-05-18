"use client";

import { useState, useTransition } from "react";

type Opt = { slug: string; name: string };
type Item = { item: string; name?: string; qty: number; unit: string; est_cost: number | null; note?: string };

export function ShoppingForm({ recipes }: { recipes: Opt[] }) {
  const [picks, setPicks] = useState<Record<string, number>>({});
  const [result, setResult] = useState<{ items: Item[]; estimated_total: number; currency: string } | null>(null);
  const [pending, start] = useTransition();
  const [error, setError] = useState<string | null>(null);

  const toggle = (slug: string, qty: number) =>
    setPicks((p) => (qty <= 0 ? Object.fromEntries(Object.entries(p).filter(([k]) => k !== slug)) : { ...p, [slug]: qty }));

  const run = () => {
    setError(null);
    const plan = Object.entries(picks).map(([recipe, qty]) => ({ recipe, qty }));
    if (plan.length === 0) {
      setError("Pick at least one recipe.");
      return;
    }
    start(async () => {
      try {
        const res = await fetch("/api/shopping", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ plan }),
        });
        if (!res.ok) throw new Error(await res.text());
        setResult(await res.json());
      } catch (e) {
        setError(String(e));
      }
    });
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="grid gap-2 sm:grid-cols-2">
          {recipes.map((r) => (
            <label key={r.slug} className="flex items-center justify-between gap-3 text-sm">
              <span>{r.name}</span>
              <input
                type="number"
                min={0}
                className="input w-20"
                value={picks[r.slug] ?? 0}
                onChange={(e) => toggle(r.slug, Number(e.target.value))}
              />
            </label>
          ))}
        </div>
        <div className="mt-4 flex justify-end">
          <button className="btn" onClick={run} disabled={pending}>
            {pending ? "Building…" : "Build list"}
          </button>
        </div>
        {error && <p className="mt-2 text-sm text-rose-600">{error}</p>}
      </div>

      {result && (
        <section>
          <h3 className="mb-3 text-lg font-medium">Shopping list</h3>
          {result.items.length === 0 ? (
            <div className="card text-sm text-stone-500">You have everything you need 🎉</div>
          ) : (
            <ul className="card divide-y divide-stone-100 p-0">
              {result.items.map((it, i) => (
                <li key={i} className="flex items-center justify-between px-5 py-3 text-sm">
                  <span>
                    {it.name ?? it.item}
                    {it.note && <span className="ml-2 text-xs text-amber-700">({it.note})</span>}
                  </span>
                  <span className="flex items-center gap-3">
                    <span className="font-mono text-stone-600">
                      {it.qty} {it.unit}
                    </span>
                    {it.est_cost !== null && (
                      <span className="font-mono text-stone-400">${it.est_cost.toFixed(2)}</span>
                    )}
                  </span>
                </li>
              ))}
            </ul>
          )}
          {result.items.length > 0 && (
            <div className="mt-2 text-right text-sm text-stone-500">
              Estimated total: <span className="font-mono">${result.estimated_total.toFixed(2)}</span>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
