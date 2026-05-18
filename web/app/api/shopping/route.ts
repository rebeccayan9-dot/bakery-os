import { NextResponse } from "next/server";
import { cli } from "@/lib/bakery";
import { DEMO_MODE, demoBlocked } from "@/lib/demo";

type PlanEntry = { recipe: string; qty: number };

export async function POST(req: Request) {
  if (DEMO_MODE) return demoBlocked();
  const { plan } = await req.json();
  if (!Array.isArray(plan)) return NextResponse.json({ error: "plan required" }, { status: 400 });
  const arg = (plan as PlanEntry[]).map((p) => `${p.recipe}:${p.qty}`).join(",");
  try {
    return NextResponse.json(await cli(["shop", arg]));
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}
