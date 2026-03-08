"""
Pydantic models for SagaBreaker's world state and chapter management.
These are the source of truth shared across all agents.
"""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


# ── World Model ───────────────────────────────────────────────────────────────

class CharacterRelationship(BaseModel):
    character_name: str
    description: str


class Character(BaseModel):
    name: str
    traits: list[str]
    relationships: list[CharacterRelationship]
    current_arc: str
    established_facts: list[str]


class Location(BaseModel):
    name: str
    description: str
    established_facts: list[str]


ThreadStatus = Literal["open", "foreshadowed", "resolved"]


class PlotThread(BaseModel):
    id: str
    description: str
    status: ThreadStatus
    introduced_in_chapter: int | None
    resolved_in_chapter: int | None


class TimelineEntry(BaseModel):
    chapter: int
    key_events: list[str]


class WorldModel(BaseModel):
    title: str
    premise: str
    genre: str
    tone: str
    themes: list[str]
    narrative_voice: str  # e.g. "third-person limited, past tense, literary"
    characters: list[Character]
    locations: list[Location]
    timeline: list[TimelineEntry]
    plot_threads: list[PlotThread]
    last_updated_after_chapter: int  # 0 = not started yet


# ── Chapter Manifest ──────────────────────────────────────────────────────────

ChapterStatus = Literal["planned", "drafted", "revised", "final"]


class ChapterOutline(BaseModel):
    chapter_number: int
    title: str
    pov_character: str
    setting: str
    objectives: list[str]       # What this chapter must accomplish
    key_scenes: list[str]       # Scene beats in order
    threads_to_advance: list[str]   # Plot thread IDs to advance
    threads_to_introduce: list[str] # Plot thread IDs to introduce
    threads_to_resolve: list[str]   # Plot thread IDs to resolve
    target_word_count: int


class ManifestEntry(BaseModel):
    chapter_number: int
    title: str
    status: ChapterStatus
    outline: ChapterOutline
    word_count: int | None = None
    chapter_path: str | None = None
    summary_path: str | None = None
    continuity_warnings: list[str] = []


class Manifest(BaseModel):
    title: str
    total_chapters: int
    current_chapter: int
    act_breaks: list[int]   # Chapter numbers that END an act (e.g. [5, 12, 20])
    entries: list[ManifestEntry]


# ── Agent Response Models ─────────────────────────────────────────────────────

class ChapterOutlinesResponse(BaseModel):
    chapters: list[ChapterOutline]
    act_breaks: list[int]


class ThreadUpdate(BaseModel):
    thread_id: str
    new_status: ThreadStatus
    update: str


class ChapterSummary(BaseModel):
    summary: str
    key_events_for_memory: list[str]
    character_developments: list[str]
    thread_updates: list[ThreadUpdate]


class CriticResult(BaseModel):
    approved: bool
    issues: list[str]
    suggestions: list[str]
    continuity_score: int   # 1–10
