import { NextResponse } from "next/server";
import { promises as fs } from "node:fs";
import path from "node:path";
import { cli } from "@/lib/bakery";
import { DEMO_MODE, demoBlocked } from "@/lib/demo";

const RECIPES_PATH = path.join(process.cwd(), "data", "recipes.json");
const UPLOADS_DIR = path.join(process.cwd(), "public", "uploads");

function slugify(input: string): string {
  return input
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 60) || `recipe-${Date.now()}`;
}

async function uniqueSlug(base: string, recipes: Record<string, unknown>): Promise<string> {
  if (!(base in recipes)) return base;
  let i = 2;
  while (`${base}-${i}` in recipes) i++;
  return `${base}-${i}`;
}

async function readRecipes(): Promise<Record<string, any>> {
  const raw = await fs.readFile(RECIPES_PATH, "utf8");
  return JSON.parse(raw);
}

async function writeRecipes(recipes: Record<string, any>): Promise<void> {
  await fs.writeFile(RECIPES_PATH, JSON.stringify(recipes, null, 2) + "\n");
}

export async function POST(req: Request) {
  if (DEMO_MODE) return demoBlocked();
  try {
    const contentType = req.headers.get("content-type") || "";
    const recipes = await readRecipes();
    const now = new Date().toISOString();

    if (contentType.includes("multipart/form-data")) {
      const form = await req.formData();
      const mode = form.get("mode");
      const name = String(form.get("name") || "").trim();
      const photo = form.get("photo");

      if (mode !== "photo" || !(photo instanceof File) || !name) {
        return NextResponse.json({ error: "name and photo required" }, { status: 400 });
      }

      const baseSlug = slugify(name);
      const slug = await uniqueSlug(baseSlug, recipes);
      const ext = (photo.name.split(".").pop() || "jpg").toLowerCase().replace(/[^a-z0-9]/g, "") || "jpg";
      await fs.mkdir(UPLOADS_DIR, { recursive: true });
      const filename = `${slug}.${ext}`;
      const buf = Buffer.from(await photo.arrayBuffer());
      await fs.writeFile(path.join(UPLOADS_DIR, filename), buf);

      recipes[slug] = {
        name,
        yield: { count: 1, unit: "batch" },
        ingredients: [],
        steps: [],
        tags: ["captured", "from-photo"],
        featured: true,
        source: {
          type: "photo",
          path: `/uploads/${filename}`,
          captured_at: now,
        },
      };
      await writeRecipes(recipes);
      return NextResponse.json({ slug, name, source: "photo" });
    }

    // JSON path → YouTube URL
    const body = await req.json();
    if (body.mode !== "url" || !body.url) {
      return NextResponse.json({ error: "url required" }, { status: 400 });
    }

    const meta = (await cli(["youtube", String(body.url)])) as {
      title: string;
      channel: string;
      transcript: string;
      has_transcript: boolean;
    };
    const name = String(body.name || "").trim() || meta.title || "Untitled recipe";
    const baseSlug = slugify(name);
    const slug = await uniqueSlug(baseSlug, recipes);

    recipes[slug] = {
      name,
      yield: { count: 1, unit: "batch" },
      ingredients: [],
      steps: [],
      tags: ["captured", "from-youtube"],
      featured: true,
      source: {
        type: "youtube",
        url: String(body.url),
        channel: meta.channel,
        captured_at: now,
        transcript: meta.transcript || undefined,
      },
    };
    await writeRecipes(recipes);
    return NextResponse.json({
      slug,
      name,
      source: "youtube",
      has_transcript: meta.has_transcript,
    });
  } catch (e) {
    return NextResponse.json({ error: String(e instanceof Error ? e.message : e) }, { status: 500 });
  }
}
