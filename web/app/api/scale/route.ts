import { NextResponse } from "next/server";
import { cli } from "@/lib/bakery";
import { DEMO_MODE, demoBlocked } from "@/lib/demo";

export async function POST(req: Request) {
  if (DEMO_MODE) return demoBlocked();
  const { slug, target_count, multiplier } = await req.json();
  const args = ["scale", slug];
  if (typeof target_count === "number") args.push("--count", String(target_count));
  else if (typeof multiplier === "number") args.push("--multiplier", String(multiplier));
  else return NextResponse.json({ error: "target_count or multiplier required" }, { status: 400 });
  try {
    return NextResponse.json(await cli(args));
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}
