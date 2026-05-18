import { getRecipes } from "@/lib/data";
import { PlanForm } from "./PlanForm";

export default async function PlanPage() {
  const recipes = await getRecipes();
  const options = Object.entries(recipes).map(([slug, r]) => ({ slug, name: r.name }));
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-medium">Bake plan</h2>
        <p className="mt-1 text-sm text-stone-500">
          Tell me what you want ready and when — I'll work backward through each recipe to tell you when to start.
        </p>
      </div>
      <PlanForm recipes={options} />
    </div>
  );
}
