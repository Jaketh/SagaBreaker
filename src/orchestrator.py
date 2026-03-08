"""
Orchestrator — the main pipeline loop.

Flow:
  1. Build world model from premise          [Architect]
  2. Human checkpoint: approve world model
  3. Outline all chapters                    [Architect]
  4. Human checkpoint: approve outline / begin
  5. For each chapter:
       a. Write prose                         [Writer]
       b. Review continuity                   [Critic]
       c. Revise if needed (max 2 passes)     [Writer + Critic]
       d. Persist chapter to disk
       e. Summarize                           [Architect]
       f. Update world model                  [Architect]
       g. Human checkpoint at act breaks
  6. Done — report output location
"""
from __future__ import annotations
import sys
from pathlib import Path
import anthropic

from src.agents.architect import (
    build_world_model,
    outline_chapters,
    summarize_chapter,
    update_world_model,
)
from src.agents.writer import write_chapter, revise_chapter
from src.agents.critic import review_chapter
from src.models import Manifest, ManifestEntry
from src.utils.file_io import (
    ensure_output_dirs,
    save_world_model,
    load_world_model,
    save_manifest,
    load_manifest,
    save_chapter,
    save_summary,
    load_all_summaries,
)
from src.utils.console import (
    ask,
    confirm,
    human_checkpoint,
    print_world_summary,
    print_outline_summary,
)

MAX_REVISION_PASSES = 2


def _load_premise() -> str:
    """
    Get the novel premise from one of three sources (in priority order):
      1. A .md file path passed as a command-line argument: python app.py premise.md
      2. A file path typed interactively when prompted
      3. Plain text typed directly at the prompt
    """
    # Command-line file argument
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        if path.exists():
            print(f"Reading premise from: {path}\n")
            return path.read_text(encoding="utf-8")
        else:
            print(f"Warning: file '{path}' not found — falling back to interactive input.\n")

    # Interactive: file path or inline text
    print("Enter your premise one of two ways:")
    print("  • Type or paste a file path to a .md file  (e.g. premise.md)")
    print("  • Or just type your premise directly and press Enter\n")
    answer = ask("> ").strip()

    # If it looks like a file path, try to read it
    candidate = Path(answer)
    if candidate.suffix in {".md", ".txt"} and candidate.exists():
        print(f"Reading premise from: {candidate}\n")
        return candidate.read_text(encoding="utf-8")

    # Otherwise treat the answer as the premise itself
    return answer


def run() -> None:
    client = anthropic.Anthropic()
    ensure_output_dirs()

    # ── Resume or start fresh ─────────────────────────────────────────────────
    world = load_world_model()
    manifest = load_manifest()

    if world and manifest:
        completed = manifest.current_chapter - 1
        resume = confirm(
            f'\nFound existing novel "{world.title}" '
            f"({completed}/{manifest.total_chapters} chapters done). Resume?"
        )
        if not resume:
            world = None
            manifest = None

    # ── Phase 1: Build world model ────────────────────────────────────────────
    if world is None:
        print("\nWelcome to SagaBreaker — Agentic Novel Writer\n")
        premise = _load_premise()
        world = build_world_model(premise, client)
        save_world_model(world)

        print_world_summary(world)

        ok = human_checkpoint(
            "Review the world model above.",
            prompt="Does this capture your vision? (y to continue, n to exit and edit)",
        )
        if not ok:
            print("\nExiting. Edit output/world-model.json and rerun to resume.")
            return

    # ── Phase 2: Outline chapters ─────────────────────────────────────────────
    if manifest is None:
        count_str = ask("\nHow many chapters should the novel have? ")
        chapter_count = max(1, int(count_str) if count_str.isdigit() else 20)

        result = outline_chapters(world, chapter_count, client)
        outlines = result.chapters
        act_breaks = result.act_breaks

        print_outline_summary(outlines, act_breaks)

        entries = [
            ManifestEntry(
                chapter_number=o.chapter_number,
                title=o.title,
                status="planned",
                outline=o,
            )
            for o in outlines
        ]
        manifest = Manifest(
            title=world.title,
            total_chapters=chapter_count,
            current_chapter=1,
            act_breaks=act_breaks,
            entries=entries,
        )
        save_manifest(manifest)

        proceed = human_checkpoint(
            "Review the chapter outline above.",
            prompt="Shall we begin writing?",
        )
        if not proceed:
            print("\nOutline saved to output/manifest.json. Rerun to begin writing.")
            return

    # ── Phase 3: Write chapters ───────────────────────────────────────────────
    for chapter_num in range(manifest.current_chapter, manifest.total_chapters + 1):
        entry = next(
            (e for e in manifest.entries if e.chapter_number == chapter_num), None
        )
        if entry is None or entry.status == "final":
            manifest.current_chapter = chapter_num + 1
            continue

        outline = entry.outline
        previous_summaries = load_all_summaries(chapter_num - 1)

        # Write ───────────────────────────────────────────────────────────────
        prose = write_chapter(outline, world, previous_summaries, client)

        # Review + revise loop ────────────────────────────────────────────────
        review = review_chapter(prose, outline, world, client)
        revision_pass = 0

        while not review.approved and revision_pass < MAX_REVISION_PASSES:
            revision_pass += 1
            prose = revise_chapter(prose, review.issues, outline, world, client)
            review = review_chapter(prose, outline, world, client)

        # Persist chapter ─────────────────────────────────────────────────────
        chapter_path = save_chapter(chapter_num, outline.title, prose)
        print(f"\n[System] Saved → {chapter_path}")

        # Summarize ───────────────────────────────────────────────────────────
        summary = summarize_chapter(prose, chapter_num, world, client)
        summary_path = save_summary(chapter_num, summary.summary)

        # Update world model ──────────────────────────────────────────────────
        world = update_world_model(prose, summary, chapter_num, world, client)
        save_world_model(world)

        # Update manifest ─────────────────────────────────────────────────────
        entry.status = "final"
        entry.word_count = len(prose.split())
        entry.chapter_path = chapter_path
        entry.summary_path = summary_path
        if not review.approved:
            entry.continuity_warnings = review.issues

        manifest.current_chapter = chapter_num + 1
        save_manifest(manifest)

        # Human checkpoint at act breaks ──────────────────────────────────────
        if chapter_num in manifest.act_breaks and chapter_num < manifest.total_chapters:
            act_num = manifest.act_breaks.index(chapter_num) + 1
            cont = human_checkpoint(
                f"Act {act_num} complete! ({chapter_num} chapters written)",
                prompt=f"Continue to Act {act_num + 1}?",
            )
            if not cont:
                print(
                    f"\nPaused after Act {act_num}. "
                    "Rerun anytime — progress is saved."
                )
                return

    # ── Done ──────────────────────────────────────────────────────────────────
    total_words = sum(
        e.word_count or 0 for e in manifest.entries if e.word_count
    )
    print("\n" + "═" * 60)
    print(f'"{world.title}" is complete!')
    print("═" * 60)
    print(f"  Total words:   ~{total_words:,}")
    print(f"  Chapters:      {manifest.total_chapters}")
    print(f"  Novel files:   output/chapters/")
    print(f"  World model:   output/world-model.json")
    print(f"  Manifest:      output/manifest.json")
    print("\nThank you for writing with SagaBreaker.")
