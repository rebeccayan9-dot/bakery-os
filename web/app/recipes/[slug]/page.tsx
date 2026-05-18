import { notFound } from "next/navigation";
import { getRecipes } from "@/lib/data";
import { ScaleControls } from "./ScaleControls";

export default async function RecipeDetail({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const recipes = await getRecipes();
  const recipe = recipes[slug];
  if (!recipe) notFound();

  const activeMin = recipe.steps.filter((s) => s.active).reduce((a, b) => a + b.duration_min, 0);
  const totalMin = recipe.steps.reduce((a, b) => a + b.duration_min, 0);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-medium">{recipe.name}</h2>
        <p className="mt-1 text-sm text-stone-500">
          Makes {recipe.yield.count} {recipe.yield.unit}
          {recipe.yield.weight_g ? ` (${recipe.yield.weight_g}g each)` : ""} · {fmtTime(activeMin)} active · {fmtTime(totalMin)} total
        </p>
      </div>

      <ScaleControls slug={slug} baseCount={recipe.yield.count} unit={recipe.yield.unit} />

      <section>
        <h3 className="mb-3 text-lg font-medium">Ingredients</h3>
        <ul className="card divide-y divide-stone-100 p-0">
          {recipe.ingredients.map((ing, i) => (
            <li key={i} className="flex justify-between px-5 py-3 text-sm">
              <span>{ing.item.replace(/-/g, " ")}</span>
              <span className="font-mono text-stone-600">{ing.qty} {ing.unit}</span>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h3 className="mb-3 text-lg font-medium">Steps</h3>
        <ol className="space-y-2">
          {recipe.steps.map((s, i) => (
            <li key={i} className="card flex items-center justify-between text-sm">
              <span>
                <span className="mr-2 text-stone-400">{i + 1}.</span>
                {s.name}
              </span>
              <span className="flex items-center gap-2 text-xs">
                {s.oven && <span className="pill">{s.oven_temp_f}°F oven</span>}
                <span className={s.active ? "text-stone-700" : "text-stone-400"}>
                  {fmtTime(s.duration_min)} {s.active ? "active" : "passive"}
                </span>
              </span>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}

function fmtTime(min: number): string {
  if (min < 60) return `${min}m`;
  const h = Math.floor(min / 60);
  const m = min % 60;
  return m ? `${h}h ${m}m` : `${h}h`;
}
