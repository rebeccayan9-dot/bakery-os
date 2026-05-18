import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";
import { DemoBanner } from "./DemoBanner";

export const metadata: Metadata = {
  title: "Bakery OS",
  description: "Personal home-baking assistant",
};

const NAV = [
  { href: "/", label: "Today" },
  { href: "/recipes", label: "Recipes" },
  { href: "/pantry", label: "Pantry" },
  { href: "/plan", label: "Bake Plan" },
  { href: "/shopping", label: "Shopping" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="mx-auto max-w-5xl px-6 py-8">
          <header className="mb-10 flex items-end justify-between border-b border-stone-200 pb-6">
            <div>
              <Link href="/" className="block">
                <h1 className="text-3xl font-semibold tracking-tight">🥐 Bakery OS</h1>
                <p className="text-sm text-stone-500">Personal home-baking assistant</p>
              </Link>
            </div>
            <nav className="flex gap-1 text-sm">
              {NAV.map((n) => (
                <Link
                  key={n.href}
                  href={n.href}
                  className="rounded-full px-3 py-1.5 text-stone-600 hover:bg-stone-100"
                >
                  {n.label}
                </Link>
              ))}
            </nav>
          </header>
          <main>
            <DemoBanner />
            {children}
          </main>
          <footer className="mt-16 border-t border-stone-200 pt-6 text-xs text-stone-400">
            <p>Bakery OS · agentic skills + Next.js · personal use only</p>
          </footer>
        </div>
      </body>
    </html>
  );
}
