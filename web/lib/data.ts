import recipesData from "../data/recipes.json";
import inventoryData from "../data/inventory.json";
import configData from "../data/config.json";
import substitutionsData from "../data/substitutions.json";

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

export const getRecipes = async (): Promise<Recipes> => recipesData as Recipes;
export const getInventory = async (): Promise<Inventory> => inventoryData as Inventory;
export const getConfig = async (): Promise<Config> => configData as Config;
export const getSubstitutions = async (): Promise<Substitutions> => substitutionsData as Substitutions;
