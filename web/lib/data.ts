import { promises as fs } from "node:fs";
import path from "node:path";

const DATA_DIR = path.resolve(process.cwd(), "data");

async function read<T>(name: string): Promise<T> {
  const raw = await fs.readFile(path.join(DATA_DIR, `${name}.json`), "utf8");
  return JSON.parse(raw) as T;
}

export type Ingredient = { item: string; qty: number; unit: string };
export type Step = {
  name: string;
  duration_min: number;
  active?: boolean;
  oven?: boolean;
  oven_temp_f?: number;
};
export type RecipeSource = {
  type: "youtube" | "photo";
  url?: string;
  path?: string;
  channel?: string;
  captured_at: string;
  transcript?: string;
};

export type Recipe = {
  name: string;
  yield: { count: number; unit: string; weight_g?: number };
  ingredients: Ingredient[];
  steps: Step[];
  tags?: string[];
  featured?: boolean;
  source?: RecipeSource;
};
export type Recipes = Record<string, Recipe>;

export type InventoryItem = {
  name: string;
  qty: number;
  unit: string;
  price_per_unit: number;
  category: string;
};
export type Inventory = Record<string, InventoryItem>;

export type Config = {
  kitchen_name: string;
  oven_capacity: number;
  currency: string;
  labor_rate_per_hour?: number;
  overhead_pct?: number;
};

export type Substitution = {
  replacement: string;
  ratio: number;
  notes: string;
};
export type Substitutions = Record<string, Substitution[]>;

export const getRecipes = () => read<Recipes>("recipes");
export const getInventory = () => read<Inventory>("inventory");
export const getConfig = () => read<Config>("config");
export const getSubstitutions = () => read<Substitutions>("substitutions");
