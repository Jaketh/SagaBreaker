"""
Writer Agent — produces the actual prose.

Uses streaming so the user can watch the chapter appear in real time.
Supports both initial drafts and revision passes.
"""
import sys
import anthropic

from src.models import WorldModel, ChapterOutline

MODEL = "claude-opus-4-6"

SYSTEM = """\
You are a skilled literary novelist. You write vivid, emotionally resonant \
prose that brings characters to life through action, dialogue, and interiority.

Your writing:
- Shows rather than tells — use scene and behavior, not summary
- Anchors scenes in specific sensory detail
- Gives each character a distinct voice in dialogue
- Maintains consistent POV within a scene (no head-hopping)
- Varies sentence rhythm to control pacing
- Never recaps what the reader already knows

You stay strictly within the established world facts. You do not introduce new \
major characters, locations, or abilities without cause. You do not resolve \
plot threads that aren't marked for resolution in this chapter.\
"""


def _build_context(world: WorldModel, previous_summaries: list[str]) -> str:
    """Build the standing story context injected into every write/revise call."""
    recent = previous_summaries[-3:]
    earlier = previous_summaries[:-3]

    active_threads = [t for t in world.plot_threads if t.status != "resolved"]
    thread_lines = "\n".join(
        f"  [{t.status.upper()}] {t.id}: {t.description}"
        for t in active_threads
    )

    character_lines = "\n".join(
        f"  • {c.name}: {', '.join(c.traits[:3])} — {c.current_arc}"
        for c in world.characters
    )

    earlier_block = ""
    if earlier:
        earlier_block = "## Earlier Story (brief)\n" + "\n".join(
            f"  Ch {i + 1}: {s}" for i, s in enumerate(earlier)
        ) + "\n\n"

    recent_block = "## Most Recent Chapters\n"
    if recent:
        start = len(earlier)
        recent_block += "\n".join(
            f"  Ch {start + i + 1}: {s}" for i, s in enumerate(recent)
        )
    else:
        recent_block += "  (This is the opening chapter.)"

    return f"""\
# "{world.title}"

## Narrative Voice
{world.narrative_voice}

## Themes
{", ".join(world.themes)}

## Characters
{character_lines}

## Active Plot Threads
{thread_lines}

{earlier_block}{recent_block}\
"""


def _stream_text(stream: anthropic.MessageStream) -> str:
    """Stream text blocks to stdout and return the full accumulated text."""
    in_text_block = False
    prose_parts: list[str] = []

    for event in stream:
        if event.type == "content_block_start":
            in_text_block = event.content_block.type == "text"
        elif event.type == "content_block_delta" and in_text_block:
            delta = event.delta
            if delta.type == "text_delta":
                sys.stdout.write(delta.text)
                sys.stdout.flush()
                prose_parts.append(delta.text)
        elif event.type == "content_block_stop":
            in_text_block = False

    return "".join(prose_parts)


def write_chapter(
    outline: ChapterOutline,
    world: WorldModel,
    previous_summaries: list[str],
    client: anthropic.Anthropic,
) -> str:
    """Write a full chapter and stream it to the console."""
    print(
        f"\n[Writer] Writing Chapter {outline.chapter_number}: "
        f'"{outline.title}"…\n'
    )
    print("─" * 60)

    context = _build_context(world, previous_summaries)

    objectives = "\n".join(f"  - {o}" for o in outline.objectives)
    key_scenes = "\n".join(f"  - {s}" for s in outline.key_scenes)

    user = f"""\
Write Chapter {outline.chapter_number}: "{outline.title}"

{context}

## This Chapter's Brief
- **POV character**: {outline.pov_character}
- **Setting**: {outline.setting}
- **Objectives** (must accomplish):
{objectives}
- **Key scenes** (in order):
{key_scenes}
- **Threads to advance**: \
{", ".join(outline.threads_to_advance) or "none"}
- **Threads to introduce**: \
{", ".join(outline.threads_to_introduce) or "none"}
- **Threads to resolve**: \
{", ".join(outline.threads_to_resolve) or "none"}
- **Target word count**: ~{outline.target_word_count:,} words

Write the full chapter now. Start directly with the prose — no preamble, no \
chapter heading (the system will add that).\
"""

    with client.messages.stream(
        model=MODEL,
        max_tokens=32_768,
        thinking={"type": "adaptive"},
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
    ) as stream:
        prose = _stream_text(stream)

    word_count = len(prose.split())
    print(f"\n{'─' * 60}")
    print(f"[Writer] Chapter {outline.chapter_number} done. (~{word_count:,} words)")
    return prose


def revise_chapter(
    draft: str,
    issues: list[str],
    outline: ChapterOutline,
    world: WorldModel,
    client: anthropic.Anthropic,
) -> str:
    """Revise a draft based on continuity issues flagged by the Critic."""
    print(
        f"\n[Writer] Revising Chapter {outline.chapter_number} "
        f"({len(issues)} issue(s) to fix)…\n"
    )
    print("─" * 60)

    issue_list = "\n".join(f"{i + 1}. {issue}" for i, issue in enumerate(issues))

    user = f"""\
Revise Chapter {outline.chapter_number}: "{outline.title}"

Issues flagged by the continuity editor (fix these exactly):
{issue_list}

Established world facts (source of truth):
- Narrative voice: {world.narrative_voice}
- Characters: {", ".join(c.name for c in world.characters)}

Original draft:
{draft}

Return the complete revised chapter. Fix the flagged issues; preserve \
everything else. Do not summarise or truncate — return the full chapter.\
"""

    with client.messages.stream(
        model=MODEL,
        max_tokens=32_768,
        thinking={"type": "adaptive"},
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
    ) as stream:
        revised = _stream_text(stream)

    print(f"\n{'─' * 60}")
    return revised
