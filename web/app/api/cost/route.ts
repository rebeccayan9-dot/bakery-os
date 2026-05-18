import { NextResponse } from "next/server";
import { cli } from "@/lib/bakery";

export async function POST(req: Request) {
  const { slug, multiplier } = await req.json();
  const args = ["cost", slug];
  if (typeof multiplier === "number") args.push("--multiplier", String(multiplier));
  try {
    return NextResponse.json(await cli(args));
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}
