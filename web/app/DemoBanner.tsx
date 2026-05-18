import { DEMO_MODE } from "@/lib/demo";

export function DemoBanner() {
  if (!DEMO_MODE) return null;
  return (
    <div className="mb-6 rounded-2xl border border-amber-300 bg-amber-50 px-5 py-3 text-sm text-amber-900">
      <strong className="font-semibold">Demo mode.</strong> This is a read-only Vercel deployment.
      Interactive features (scale, plan, shopping, capture) need the Python CLI — clone the repo and run locally.
    </div>
  );
}
