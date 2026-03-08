"""
Filesystem helpers — all disk I/O goes through here.

Output layout:
  output/
    world-model.json          — living world state
    manifest.json             — chapter tracking
    chapters/
      chapter-01.md           — final prose per chapter
      summaries/
        chapter-01-summary.txt
"""
from __future__ import annotations
import json
from pathlib import Path

from src.models import WorldModel, Manifest

OUTPUT_DIR = Path("output")
CHAPTERS_DIR = OUTPUT_DIR / "chapters"
SUMMARIES_DIR = CHAPTERS_DIR / "summaries"
WORLD_MODEL_PATH = OUTPUT_DIR / "world-model.json"
MANIFEST_PATH = OUTPUT_DIR / "manifest.json"


def ensure_output_dirs() -> None:
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)


# ── World Model ───────────────────────────────────────────────────────────────

def save_world_model(world: WorldModel) -> None:
    WORLD_MODEL_PATH.write_text(world.model_dump_json(indent=2), encoding="utf-8")


def load_world_model() -> WorldModel | None:
    if not WORLD_MODEL_PATH.exists():
        return None
    return WorldModel.model_validate_json(WORLD_MODEL_PATH.read_text(encoding="utf-8"))


# ── Manifest ──────────────────────────────────────────────────────────────────

def save_manifest(manifest: Manifest) -> None:
    MANIFEST_PATH.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")


def load_manifest() -> Manifest | None:
    if not MANIFEST_PATH.exists():
        return None
    return Manifest.model_validate_json(MANIFEST_PATH.read_text(encoding="utf-8"))


# ── Chapters ──────────────────────────────────────────────────────────────────

def save_chapter(chapter_number: int, title: str, prose: str) -> str:
    filename = f"chapter-{chapter_number:02d}.md"
    path = CHAPTERS_DIR / filename
    content = f"# Chapter {chapter_number}: {title}\n\n{prose}\n"
    path.write_text(content, encoding="utf-8")
    return str(path)


def save_summary(chapter_number: int, summary: str) -> str:
    filename = f"chapter-{chapter_number:02d}-summary.txt"
    path = SUMMARIES_DIR / filename
    path.write_text(summary, encoding="utf-8")
    return str(path)


def load_all_summaries(up_to_chapter: int) -> list[str]:
    """Return summary strings for chapters 1..up_to_chapter, in order."""
    summaries: list[str] = []
    for i in range(1, up_to_chapter + 1):
        path = SUMMARIES_DIR / f"chapter-{i:02d}-summary.txt"
        if path.exists():
            summaries.append(path.read_text(encoding="utf-8"))
    return summaries
