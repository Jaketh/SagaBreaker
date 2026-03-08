"""
Architect Agent — owns the story's world model.

Responsibilities:
  • Build the initial world model from a user premise
  • Outline all chapters (structure, objectives, act breaks)
  • Summarize a completed chapter into a compact memory entry
  • Update the world model after each chapter is written
"""
import json
import anthropic

from src.models import (
    WorldModel,
    ChapterOutline,
    ChapterOutlinesResponse,
    ChapterSummary,
)

MODEL = "claude-opus-4-6"


def _parse(client: anthropic.Anthropic, system: str, user: str, schema: type) -> object:
    """Call Claude with structured output and return the parsed Pydantic model."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=16_000,
        thinking={"type": "adaptive"},
        system=system,
        messages=[{"role": "user", "content": user}],
        output_config={
            "format": {
                "type": "json_schema",
                "json_schema": {
                    "name": schema.__name__,
                    "schema": schema.model_json_schema(),
                },
            }
        },
    )
    text_block = next(b for b in response.content if b.type == "text")
    return schema.model_validate_json(text_block.text)


def build_world_model(premise: str, client: anthropic.Anthropic) -> WorldModel:
    """Build the story's world model from a raw premise."""
    print("\n[Architect] Building world model…")

    system = """\
You are a master narrative architect. Given a premise, you construct a rich, \
internally consistent story world.

Your world models feature:
- Characters with clear motivations, specific relationships, and believable arcs
- Locations with distinct atmosphere and established physical rules
- Plot threads that create sustained tension and satisfying payoff
- A narrative voice that suits the genre and tone

Be specific and concrete — vague traits like "brave" should be grounded in \
actual backstory or behavior. Every character relationship must state HOW the \
characters know each other and what the dynamic is.\
"""

    user = f"""\
Build a complete world model for this novel premise:

{premise}

Create richly developed characters, vivid locations, compelling plot threads, \
and a clear narrative vision. Set last_updated_after_chapter to 0.\
"""

    return _parse(client, system, user, WorldModel)


def outline_chapters(
    world: WorldModel,
    chapter_count: int,
    client: anthropic.Anthropic,
) -> ChapterOutlinesResponse:
    """Generate a chapter-by-chapter outline and identify act breaks."""
    print(f"\n[Architect] Outlining {chapter_count} chapters…")

    system = """\
You are a master narrative architect specializing in story structure.

You create chapter-by-chapter outlines that balance pacing, tension, and \
character development. Each chapter must:
- Have a clear dramatic purpose
- Advance at least one plot thread
- End with a hook, revelation, or emotional shift

You understand three-act structure deeply. Act breaks should land at moments \
of maximum dramatic reversal — not just the midpoint, but where the \
protagonist's goal fundamentally changes or is threatened.\
"""

    world_json = world.model_dump_json(indent=2)
    user = f"""\
Given this world model, create a {chapter_count}-chapter outline.

World Model:
{world_json}

Requirements:
- Each chapter should target 2,500–4,000 words
- Identify natural act breaks (chapter numbers that END an act)
- Balance action, dialogue, and character interiority
- Make sure every plot thread is introduced, developed, and resolved across \
the arc
- The final chapter should close all major threads and provide emotional \
resolution\
"""

    return _parse(client, system, user, ChapterOutlinesResponse)


def summarize_chapter(
    prose: str,
    chapter_number: int,
    world: WorldModel,
    client: anthropic.Anthropic,
) -> ChapterSummary:
    """Distill a completed chapter into a compact memory object."""
    print(f"\n[Architect] Summarizing Chapter {chapter_number}…")

    active_threads = [
        t for t in world.plot_threads if t.status != "resolved"
    ]
    thread_list = "\n".join(f"- {t.id}: {t.description}" for t in active_threads)

    system = """\
You are a precise literary summarizer. You distill chapters into structured \
summaries that serve as long-term memory for the writing agents.

Your summaries must capture:
- The essential plot events (what happened, in sequence)
- Character development moments (how someone changed or revealed themselves)
- Any new world facts established (rules, places, relationships)
- Which plot threads moved and how\
"""

    user = f"""\
Summarize Chapter {chapter_number} of "{world.title}".

Active plot threads going in:
{thread_list}

Chapter prose:
{prose}\
"""

    return _parse(client, system, user, ChapterSummary)


def update_world_model(
    prose: str,
    summary: ChapterSummary,
    chapter_number: int,
    world: WorldModel,
    client: anthropic.Anthropic,
) -> WorldModel:
    """Update the world model to reflect what happened in the completed chapter."""
    print(f"\n[Architect] Updating world model after Chapter {chapter_number}…")

    system = """\
You are a narrative continuity keeper. After each chapter is written you \
update the living world model to reflect all changes.

Rules:
- Preserve every established fact from the previous world model
- Update character arcs, relationships, and established_facts as events unfold
- Add the chapter's key events to the timeline
- Update plot thread statuses based on what actually happened in the chapter
- Set last_updated_after_chapter to the chapter number just completed
- Do NOT invent new facts that weren't in the chapter\
"""

    world_json = world.model_dump_json(indent=2)
    summary_json = summary.model_dump_json(indent=2)
    prose_excerpt = prose[:2000] + ("…[truncated]" if len(prose) > 2000 else "")

    user = f"""\
Update the world model after Chapter {chapter_number}.

Current world model:
{world_json}

Chapter summary:
{summary_json}

Chapter prose excerpt (for reference):
{prose_excerpt}

Return the complete updated world model with \
last_updated_after_chapter = {chapter_number}.\
"""

    return _parse(client, system, user, WorldModel)
