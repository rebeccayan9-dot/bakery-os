import { getInventory } from "@/lib/data";

export default async function PantryPage() {
  const inventory = await getInventory();
  const byCategory = Object.entries(inventory).reduce<Record<string, [string, typeof inventory[string]][]>>(
    (acc, entry) => {
      const cat = entry[1].category || "other";
      (acc[cat] ||= []).push(entry);
      return acc;
    },
    {},
  );

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-medium">Pantry</h2>
      {Object.entries(byCategory).map(([cat, items]) => (
        <section key={cat}>
          <h3 className="mb-2 text-xs uppercase tracking-wide text-stone-400">{cat}</h3>
          <ul className="card divide-y divide-stone-100 p-0">
            {items.map(([slug, item]) => (
              <li key={slug} className="flex items-center justify-between px-5 py-3 text-sm">
                <span>{item.name}</span>
                <span className="flex items-center gap-3">
                  <span className="font-mono text-stone-600">
                    {item.qty} {item.unit}
                  </span>
                  <span className="text-xs text-stone-400">
                    ${item.price_per_unit.toFixed(4)}/{item.unit}
                  </span>
                </span>
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}
