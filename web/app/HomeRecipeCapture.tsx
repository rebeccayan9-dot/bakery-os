"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

type Mode = "url" | "photo";

export function HomeRecipeCapture() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("url");
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [pending, start] = useTransition();
  const [status, setStatus] = useState<{ kind: "ok" | "err"; msg: string } | null>(null);

  const submit = () => {
    setStatus(null);
    start(async () => {
      try {
        let res: Response;
        if (mode === "url") {
          if (!url.trim()) throw new Error("Paste a YouTube URL.");
          res = await fetch("/api/recipe-save", {
            method: "POST",
            headers: { "content-type": "application/json" },
            body: JSON.stringify({ mode: "url", url: url.trim(), name: name.trim() }),
          });
        } else {
          if (!file) throw new Error("Pick a photo to upload.");
          if (!name.trim()) throw new Error("Give the recipe a name.");
          const fd = new FormData();
          fd.append("mode", "photo");
          fd.append("name", name.trim());
          fd.append("photo", file);
          res = await fetch("/api/recipe-save", { method: "POST", body: fd });
        }
        const body = await res.json();
        if (!res.ok) throw new Error(body.error || "save failed");
        setStatus({ kind: "ok", msg: `Saved as featured: ${body.name}` });
        setUrl("");
        setFile(null);
        setName("");
        router.refresh();
      } catch (e) {
        setStatus({ kind: "err", msg: String(e instanceof Error ? e.message : e) });
      }
    });
  };

  return (
    <section className="card">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-lg font-medium">Capture a recipe</h3>
        <div className="flex gap-1 text-xs">
          <TabButton active={mode === "url"} onClick={() => setMode("url")}>YouTube URL</TabButton>
          <TabButton active={mode === "photo"} onClick={() => setMode("photo")}>Photo</TabButton>
        </div>
      </div>

      <div className="space-y-3">
        <input
          type="url"
          placeholder="https://www.youtube.com/watch?v=…"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className={mode === "url" ? "input" : "input hidden"}
        />
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className={mode === "photo" ? "input" : "input hidden"}
        />

        <input
          type="text"
          placeholder={mode === "url" ? "Optional: override the recipe name" : "Name this recipe"}
          value={name ?? ""}
          onChange={(e) => setName(e.target.value)}
          className="input"
        />

        <div className="flex items-center justify-between">
          <p className="text-xs text-stone-500">
            {mode === "url"
              ? "Pulls captions via yt-dlp, saves as a featured stub for the agent to flesh out."
              : "Photo is saved under web/public/uploads/. Flesh out the ingredient list later via chat."}
          </p>
          <button onClick={submit} disabled={pending} className="btn">
            {pending ? "Saving…" : "Save as featured"}
          </button>
        </div>

        {status && (
          <p className={`text-sm ${status.kind === "ok" ? "text-emerald-700" : "text-rose-600"}`}>
            {status.msg}
          </p>
        )}
      </div>
    </section>
  );
}

function TabButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={`rounded-full px-3 py-1 ${active ? "bg-stone-900 text-stone-50" : "border border-stone-300 text-stone-600 hover:bg-stone-100"}`}
    >
      {children}
    </button>
  );
}
