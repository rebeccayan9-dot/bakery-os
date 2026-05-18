import { NextResponse } from "next/server";
import { cli } from "@/lib/bakery";

export async function POST(req: Request) {
  const { bakes } = await req.json();
  if (!Array.isArray(bakes) || bakes.length === 0) {
    return NextResponse.json({ error: "bakes required" }, { status: 400 });
  }
  try {
    return NextResponse.json(await cli(["plan", "--from-stdin"], bakes));
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}
