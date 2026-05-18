import Link from "next/link";
import Image from "next/image";
import { getRecipes, getInventory } from "@/lib/data";
import { HomeRecipeCapture } from "./HomeRecipeCapture";

export default async function HomePage() {
  const [recipes, inventory] = await Promise.all([getRecipes(), getInventory()]);
  const recipeCount = Object.keys(recipes).length;
  const pantryLow = Object.entries(inventory)
    .filter(([, item]) => item.qty > 0 && item.qty < lowThreshold(item.unit))
    .slice(0, 5);
  const featured = Object.entries(recipes).filter(([, r]) => r.featured);
  const otherFeatured = Object.entries(recipes)
    .filter(([, r]) => !r.featured)
    .slice(0, 4);

  return (
    <div className="space-y-10">
      <section>
        <h2 className="mb-2 text-2xl font-medium">Today</h2>
        <p className="text-stone-600">
          A small home kitchen with {recipeCount} recipes in rotation. Capture a new one, plan a bake, or peek at the pantry.
        </p>
      </section>

      <HomeRecipeCapture />

      <section className="grid gap-4 sm:grid-cols-2 md:grid-cols-4">
        <QuickCard href="/plan" title="Plan a bake" hint="Schedule backward from a target time" />
        <QuickCard href="/recipes" title="Browse recipes" hint="Scale and price any recipe" />
        <QuickCard href="/pantry" title="Pantry" hint="What's on the shelf" />
        <QuickCard href="/shopping" title="Shopping" hint="What's missing for the plan" />
      </section>

      {featured.length > 0 && (
        <section>
          <div className="mb-3 flex items-baseline justify-between">
            <h3 className="text-lg font-medium">⭐ Featured recipes</h3>
            <span className="text-xs text-stone-500">Captured & awaiting flesh-out</span>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {featured.map(([slug, r]) => (
              <Link
                key={slug}
                href={`/recipes/${slug}`}
                className="card flex gap-4 transition hover:border-stone-400"
              >
                {r.source?.type === "photo" && r.source.path && (
                  <div className="relative h-20 w-20 shrink-0 overflow-hidden rounded-xl bg-stone-100">
                    <Image
                      src={r.source.path}
                      alt={r.name}
                      fill
                      sizes="80px"
                      className="object-cover"
                    />
                  </div>
                )}
                {r.source?.type === "youtube" && (
                  <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-xl bg-stone-100 text-2xl">
                    🎥
                  </div>
                )}
                <div className="min-w-0 flex-1">
                  <div className="truncate font-medium">{r.name}</div>
                  <div className="mt-0.5 text-xs text-stone-500">
                    {r.source?.type === "youtube"
                      ? `via YouTube${r.source.channel ? ` · ${r.source.channel}` : ""}`
                      : "via photo"}
                  </div>
                  {r.ingredients.length === 0 && (
                    <div className="mt-2">
                      <span className="pill bg-amber-50 text-amber-700">stub — needs ingredients</span>
                    </div>
                  )}
                </div>
                <span className="self-center text-stone-400">→</span>
              </Link>
            ))}
          </div>
        </section>
      )}

      {otherFeatured.length > 0 && (
        <section>
          <h3 className="mb-3 text-lg font-medium">In rotation</h3>
          <div className="grid gap-3 sm:grid-cols-2">
            {otherFeatured.map(([slug, r]) => (
              <Link
                key={slug}
                href={`/recipes/${slug}`}
                className="card flex items-center justify-between transition hover:border-stone-400"
              >
                <div>
                  <div className="font-medium">{r.name}</div>
                  <div className="text-xs text-stone-500">
                    Makes {r.yield.count} {r.yield.unit} · {r.ingredients.length} ingredients
                  </div>
                </div>
                <span className="text-stone-400">→</span>
              </Link>
            ))}
          </div>
        </section>
      )}

      {pantryLow.length > 0 && (
        <section>
          <h3 className="mb-3 text-lg font-medium">Running low</h3>
          <ul className="grid gap-2 sm:grid-cols-2">
            {pantryLow.map(([slug, item]) => (
              <li key={slug} className="card flex justify-between text-sm">
                <span>{item.name}</span>
                <span className="text-stone-500">
                  {item.qty} {item.unit}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

function QuickCard({ href, title, hint }: { href: string; title: string; hint: string }) {
  return (
    <Link href={href} className="card block transition hover:border-stone-400">
      <div className="text-sm font-medium">{title}</div>
      <div className="mt-1 text-xs text-stone-500">{hint}</div>
    </Link>
  );
}

function lowThreshold(unit: string): number {
  if (unit === "g" || unit === "ml") return 200;
  if (unit === "each") return 3;
  return 50;
}
