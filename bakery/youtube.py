"""Pull metadata + transcript from a YouTube video for recipe extraction.

We shell out to `yt-dlp` (https://github.com/yt-dlp/yt-dlp) — it's the most
reliable way to fetch auto-generated captions without hitting the YouTube
internal API. Captions are returned as plain text; Claude does the work of
turning that into a structured recipe.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


class YouTubeError(RuntimeError):
    pass


def _require_ytdlp() -> str:
    binary = shutil.which("yt-dlp")
    if not binary:
        raise YouTubeError(
            "yt-dlp not found. Install with: pipx install yt-dlp  (or)  pip install yt-dlp"
        )
    return binary


def _strip_vtt(vtt: str) -> str:
    """Strip WEBVTT timing lines down to clean prose."""
    out: list[str] = []
    seen: set[str] = set()
    for line in vtt.splitlines():
        line = line.strip()
        if not line or line == "WEBVTT":
            continue
        if "-->" in line or line.startswith(("Kind:", "Language:", "NOTE")):
            continue
        # Inline timing tags like <00:00:01.000>
        clean = re.sub(r"<[^>]+>", "", line)
        clean = re.sub(r"\s+", " ", clean).strip()
        if clean and clean not in seen:
            seen.add(clean)
            out.append(clean)
    return "\n".join(out)


def fetch(url: str, *, lang: str = "en") -> dict:
    """Download metadata + auto-captions for a YouTube URL.

    Returns {title, channel, description, duration_sec, transcript}.
    Transcript may be empty if the video has no captions.
    """
    binary = _require_ytdlp()
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        # 1. Metadata (JSON dump, no download)
        meta_proc = subprocess.run(
            [binary, "--skip-download", "--dump-single-json", "--no-warnings", url],
            capture_output=True, text=True, check=False,
        )
        if meta_proc.returncode != 0:
            raise YouTubeError(f"yt-dlp metadata fetch failed: {meta_proc.stderr.strip()}")
        meta = json.loads(meta_proc.stdout)

        # 2. Captions (auto-generated if no manual subs)
        sub_proc = subprocess.run(
            [
                binary, "--skip-download",
                "--write-auto-sub", "--write-sub",
                "--sub-lang", lang,
                "--sub-format", "vtt",
                "--no-warnings",
                "-o", str(tmpdir / "%(id)s.%(ext)s"),
                url,
            ],
            capture_output=True, text=True, check=False,
        )
        # don't fail hard — some videos have no captions
        transcript = ""
        for vtt_file in tmpdir.glob("*.vtt"):
            transcript = _strip_vtt(vtt_file.read_text())
            break

    return {
        "url": url,
        "title": meta.get("title", ""),
        "channel": meta.get("uploader") or meta.get("channel", ""),
        "description": (meta.get("description") or "")[:4000],
        "duration_sec": meta.get("duration"),
        "transcript": transcript,
        "has_transcript": bool(transcript),
    }
