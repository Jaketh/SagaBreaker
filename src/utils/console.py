"""
Console helpers — user interaction and display formatting.
"""
from __future__ import annotations
from src.models import WorldModel


def ask(prompt: str) -> str:
    return input(prompt).strip()


def confirm(prompt: str) -> bool:
    answer = ask(f"{prompt} (y/n): ")
    return answer.lower().startswith("y")


def human_checkpoint(message: str, prompt: str = "Continue?") -> bool:
    print("\n" + "═" * 60)
    print(f"CHECKPOINT: {message}")
    print("═" * 60)
    return confirm(prompt)


def print_world_summary(world: WorldModel) -> None:
    print("\n" + "═" * 60)
    print(f'WORLD MODEL: "{world.title}"')
    print("═" * 60)
    print(f"Genre: {world.genre}  |  Tone: {world.tone}")
    print(f"Themes: {', '.join(world.themes)}")
    print(f"Narrative voice: {world.narrative_voice}")

    print("\nCharacters:")
    for c in world.characters:
        traits = ", ".join(c.traits[:2])
        print(f"  • {c.name}: {traits} — {c.current_arc}")

    print("\nPlot threads:")
    for t in world.plot_threads:
        print(f"  [{t.status.upper():12s}] {t.description}")

    print("═" * 60)


def print_outline_summary(outlines, act_breaks: list[int]) -> None:
    print("\nChapter outline:")
    for o in outlines:
        marker = "  [ACT BREAK]" if o.chapter_number in act_breaks else ""
        print(f"  {o.chapter_number:2d}. {o.title}{marker}")
    print(f"\nAct breaks after chapters: {act_breaks}")
