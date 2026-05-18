import { NextResponse } from "next/server";

export const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === "1";

export function demoBlocked() {
  return NextResponse.json(
    {
      error: "Demo mode — interactive features are disabled on this deployment.",
      hint: "Clone the repo and run locally to use scale / plan / shopping / capture.",
    },
    { status: 503 },
  );
}
