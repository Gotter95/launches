"""Data models for the content generator pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field


# ── Voice Analysis ──────────────────────────────────────────


@dataclass
class VoiceProfile:
    tone: str = ""
    vocabulary_patterns: list[str] = field(default_factory=list)
    sentence_structure: str = ""
    personality_traits: list[str] = field(default_factory=list)
    recurring_themes: list[str] = field(default_factory=list)
    stylistic_quirks: list[str] = field(default_factory=list)
    emotional_range: str = ""
    summary: str = ""


# ── Writing Pipeline ────────────────────────────────────────


@dataclass
class Iteration:
    attempt: int
    draft: str
    scores: dict[str, int] = field(default_factory=dict)
    diagnosis: str = ""
    passed: bool = False


@dataclass
class ManagedResult:
    final_text: str
    iterations: list[Iteration] = field(default_factory=list)
    final_scores: dict[str, int] = field(default_factory=dict)
    passed: bool = False


@dataclass
class ContentPiece:
    platform: str
    text: str
    iterations: list[Iteration] = field(default_factory=list)
    final_scores: dict[str, int] = field(default_factory=dict)


@dataclass
class ContentDraft:
    linkedin: ContentPiece | None = None
    twitter: ContentPiece | None = None
    email: ContentPiece | None = None


# ── Voice Check ─────────────────────────────────────────────


@dataclass
class ScoredSection:
    platform: str
    text: str
    voice_authenticity: int = 0
    platform_fit: int = 0
    rewritten: bool = False
    original: str | None = None
    cut: bool = False


# ── Final Output ────────────────────────────────────────────


@dataclass
class FinalContent:
    linkedin: ScoredSection | None = None
    twitter: ScoredSection | None = None
    email: ScoredSection | None = None


@dataclass
class PipelineResult:
    voice: VoiceProfile
    draft: ContentDraft
    final: FinalContent
    paper_trail: dict = field(default_factory=dict)
