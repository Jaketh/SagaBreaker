"""
Critic Agent — continuity and consistency reviewer.

Checks a drafted chapter against the world model and chapter brief.
Returns a structured verdict: approved or list of specific issues to fix.
"""
import anthropic

from src.models import WorldModel, ChapterOutline, CriticResult

MODEL = "claude-opus-4-6"

SYSTEM = """\
You are a meticulous literary continuity editor. You check drafted chapters \
against the story's established world model for hard errors only.

You flag:
- Character inconsistencies (acting out of established character, violating \
established facts about them)
- Timeline errors (events happening in the wrong order relative to established \
facts)
- World-fact violations (locations, rules, relationships contradicted)
- Narrative voice breaks (wrong POV, wrong tense, tone shift)
- Objective failures (chapter didn't accomplish what it was supposed to)
- Thread violations (wrong threads resolved/introduced/advanced)

You do NOT flag:
- Stylistic preferences
- Prose quality
- Word choice
- Pacing opinions

Approve chapters that are internally consistent even if imperfect prose. \
Only reject for genuine continuity errors that would confuse or contradict \
established story facts.\
"""


def review_chapter(
    prose: str,
    outline: ChapterOutline,
    world: WorldModel,
    client: anthropic.Anthropic,
) -> CriticResult:
    """Review a drafted chapter for continuity errors."""
    print(f"\n[Critic] Reviewing Chapter {outline.chapter_number}…")

    # Pass only the facts the critic needs — not the full timeline history
    world_facts = {
        "narrative_voice": world.narrative_voice,
        "characters": [
            {
                "name": c.name,
                "traits": c.traits,
                "relationships": [r.model_dump() for r in c.relationships],
                "established_facts": c.established_facts,
                "current_arc": c.current_arc,
            }
            for c in world.characters
        ],
        "locations": [l.model_dump() for l in world.locations],
        "plot_threads": [t.model_dump() for t in world.plot_threads],
    }

    import json
    world_json = json.dumps(world_facts, indent=2)

    objectives = "\n".join(f"  - {o}" for o in outline.objectives)
    advance = ", ".join(outline.threads_to_advance) or "none"
    resolve = ", ".join(outline.threads_to_resolve) or "none"
    introduce = ", ".join(outline.threads_to_introduce) or "none"

    user = f"""\
Review Chapter {outline.chapter_number}: "{outline.title}"

Chapter brief (what it was supposed to do):
- POV character: {outline.pov_character}
- Setting: {outline.setting}
- Objectives:
{objectives}
- Threads to advance: {advance}
- Threads to resolve: {resolve}
- Threads to introduce: {introduce}

Established world model (source of truth):
{world_json}

Chapter prose:
{prose}

Identify any genuine continuity errors. Approve if there are no blocking \
issues. Rate continuity_score 1–10 (10 = perfect consistency).\
"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=4_096,
        thinking={"type": "adaptive"},
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
        output_config={
            "format": {
                "type": "json_schema",
                "name": "CriticResult",
                "schema": CriticResult.model_json_schema(),
            }
        },
    )

    text_block = next(b for b in response.content if b.type == "text")
    result = CriticResult.model_validate_json(text_block.text)

    if result.approved:
        print(f"  ✓ Approved  (continuity score: {result.continuity_score}/10)")
    else:
        print(f"  ✗ {len(result.issues)} issue(s) found:")
        for issue in result.issues:
            print(f"    - {issue}")

    return result
