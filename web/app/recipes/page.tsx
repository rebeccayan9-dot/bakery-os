import Link from "next/link";
import { getRecipes } from "@/lib/data";

export default async function RecipesPage() {
  const recipes = await getRecipes();
  return (
    <div>
      <h2 className="mb-6 text-2xl font-medium">Recipes</h2>
      <div className="grid gap-3 sm:grid-cols-2">
        {Object.entries(recipes).map(([slug, r]) => (
          <Link key={slug} href={`/recipes/${slug}`} className="card block transition hover:border-stone-400">
            <div className="flex items-center justify-between">
              <span className="font-medium">{r.name}</span>
              <span className="text-stone-400">→</span>
            </div>
            <div className="mt-1 text-xs text-stone-500">
              Makes {r.yield.count} {r.yield.unit} · {r.ingredients.length} ingredients · {r.steps.length} steps
            </div>
            {r.tags && r.tags.length > 0 && (
              <div className="mt-2 flex gap-1">
                {r.tags.map((t) => (
                  <span key={t} className="pill">{t}</span>
                ))}
              </div>
            )}
          </Link>
        ))}
      </div>
    </div>
  );
}
