import { NextResponse } from "next/server";
import { cli } from "@/lib/bakery";

export async function POST(req: Request) {
  const { url, lang } = await req.json();
  if (!url) return NextResponse.json({ error: "url required" }, { status: 400 });
  const args = ["youtube", url];
  if (lang) args.push("--lang", lang);
  try {
    return NextResponse.json(await cli(args));
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}
