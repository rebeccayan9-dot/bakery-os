import { getRecipes } from "@/lib/data";
import { ShoppingForm } from "./ShoppingForm";

export default async function ShoppingPage() {
  const recipes = await getRecipes();
  const options = Object.entries(recipes).map(([slug, r]) => ({ slug, name: r.name }));
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-medium">Shopping</h2>
        <p className="mt-1 text-sm text-stone-500">
          Pick what you plan to bake. I'll diff it against your pantry and tell you what to buy.
        </p>
      </div>
      <ShoppingForm recipes={options} />
    </div>
  );
}
