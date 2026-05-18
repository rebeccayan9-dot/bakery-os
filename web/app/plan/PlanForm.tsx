"use client";

import { useState, useTransition } from "react";

type RecipeOpt = { slug: string; name: string };
type Bake = { recipe: string; qty: number; ready_at: string };
type Step = {
  recipe: string;
  recipe_name: string;
  qty: number;
  step: string;
  active: boolean;
  start: string;
  end: string;
  duration_min: number;
};
type PlanResult = {
  overall_start: string | null;
  timeline: Step[];
  oven_conflicts: { window_start: string; window_end: string; temp_spread: number[] }[];
  oven_capacity: number;
};

export function PlanForm({ recipes }: { recipes: RecipeOpt[] }) {
  const defaultReady = nextSundayAt9();
  const [bakes, setBakes] = useState<Bake[]>([
    { recipe: recipes[0]?.slug ?? "", qty: 1, ready_at: defaultReady },
  ]);
  const [result, setResult] = useState<PlanResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, start] = useTransition();

  const update = (i: number, patch: Partial<Bake>) =>
    setBakes((b) => b.map((row, idx) => (idx === i ? { ...row, ...patch } : row)));

  const submit = () => {
    setError(null);
    start(async () => {
      try {
        const res = await fetch("/api/plan", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ bakes }),
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
      <div className="card space-y-3">
        {bakes.map((b, i) => (
          <div key={i} className="grid gap-2 sm:grid-cols-[2fr_80px_1.5fr_40px]">
            <select className="input" value={b.recipe} onChange={(e) => update(i, { recipe: e.target.value })}>
              {recipes.map((r) => (
                <option key={r.slug} value={r.slug}>
                  {r.name}
                </option>
              ))}
            </select>
            <input
              type="number"
              min={1}
              className="input"
              value={b.qty}
              onChange={(e) => update(i, { qty: Number(e.target.value) })}
            />
            <input
              type="datetime-local"
              className="input"
              value={b.ready_at.slice(0, 16)}
              onChange={(e) => update(i, { ready_at: e.target.value })}
            />
            <button
              className="text-stone-400 hover:text-rose-600"
              onClick={() => setBakes((bs) => bs.filter((_, idx) => idx !== i))}
              aria-label="remove"
            >
              ✕
            </button>
          </div>
        ))}
        <div className="flex items-center justify-between">
          <button
            className="btn-ghost"
            onClick={() => setBakes((bs) => [...bs, { recipe: recipes[0]?.slug ?? "", qty: 1, ready_at: defaultReady }])}
          >
            + add bake
          </button>
          <button className="btn" onClick={submit} disabled={pending || bakes.length === 0}>
            {pending ? "Planning…" : "Build schedule"}
          </button>
        </div>
        {error && <p className="text-sm text-rose-600">{error}</p>}
      </div>

      {result && (
        <>
          {result.overall_start && (
            <div className="card">
              <div className="text-xs uppercase tracking-wide text-stone-400">Start at</div>
              <div className="text-2xl font-medium">{fmtDate(result.overall_start)}</div>
            </div>
          )}
          {result.oven_conflicts.length > 0 && (
            <div className="card border-amber-300 bg-amber-50">
              <div className="text-sm font-medium text-amber-800">⚠ Oven conflicts</div>
              <ul className="mt-2 space-y-1 text-sm text-amber-700">
                {result.oven_conflicts.map((c, i) => (
                  <li key={i}>
                    {fmtTime(c.window_start)} – {fmtTime(c.window_end)} ·{" "}
                    temps: {c.temp_spread.join(", ")}°F
                  </li>
                ))}
              </ul>
            </div>
          )}
          <section>
            <h3 className="mb-3 text-lg font-medium">Timeline</h3>
            <ol className="space-y-2">
              {result.timeline.map((s, i) => (
                <li key={i} className="card flex flex-wrap items-center gap-3 text-sm">
                  <span className="font-mono text-stone-500">{fmtTime(s.start)}</span>
                  <span className="text-stone-300">→</span>
                  <span className="flex-1">
                    <span className="font-medium">{s.recipe_name}</span> · {s.step}
                  </span>
                  <span className={`pill ${s.active ? "" : "bg-stone-50"}`}>
                    {s.active ? "active" : "passive"} {s.duration_min}m
                  </span>
                </li>
              ))}
            </ol>
          </section>
        </>
      )}
    </div>
  );
}

function nextSundayAt9(): string {
  const d = new Date();
  const dow = d.getDay();
  const add = (7 - dow) % 7 || 7;
  d.setDate(d.getDate() + add);
  d.setHours(9, 0, 0, 0);
  return d.toISOString().slice(0, 16);
}

function fmtDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function fmtTime(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    weekday: "short",
    hour: "numeric",
    minute: "2-digit",
  });
}
