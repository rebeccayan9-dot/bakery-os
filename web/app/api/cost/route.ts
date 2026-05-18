import { NextResponse } from "next/server";
import { cli } from "@/lib/bakery";
import { DEMO_MODE, demoBlocked } from "@/lib/demo";

export async function POST(req: Request) {
  if (DEMO_MODE) return demoBlocked();
  const { slug, multiplier } = await req.json();
  const args = ["cost", slug];
  if (typeof multiplier === "number") args.push("--multiplier", String(multiplier));
  try {
    return NextResponse.json(await cli(args));
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}
