"""Data models for the orchestrator pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class VideoData:
    title: str
    views: str
    channel: str
    age: str
    pattern_notes: str = ""


@dataclass
class KeywordResult:
    keyword: str
    time_filter: str
    ceiling: list[VideoData] = field(default_factory=list)
    floor_views: str = ""
    title_patterns: list[str] = field(default_factory=list)


@dataclass
class YouTubeResearch:
    keywords: list[KeywordResult] = field(default_factory=list)
    top_title_patterns: list[str] = field(default_factory=list)
    summary: str = ""


@dataclass
class PainPoint:
    quote: str
    source: str
    upvotes: int = 0
    context: str = ""


@dataclass
class ThreadData:
    title: str
    subreddit: str
    url: str = ""
    engagement: str = ""
    key_quotes: list[str] = field(default_factory=list)


@dataclass
class RedditResearch:
    pain_points: list[PainPoint] = field(default_factory=list)
    viral_threads: list[ThreadData] = field(default_factory=list)
    controversial: list[ThreadData] = field(default_factory=list)
    summary: str = ""


@dataclass
class PostData:
    text: str
    engagement: str
    quote_tweet_ratio: str = ""
    author: str = ""
    notes: str = ""


@dataclass
class TwitterResearch:
    top_posts: list[PostData] = field(default_factory=list)
    ceiling: list[PostData] = field(default_factory=list)
    floor: list[PostData] = field(default_factory=list)
    high_qt_ratio: list[PostData] = field(default_factory=list)
    summary: str = ""


@dataclass
class ResearchBundle:
    youtube: YouTubeResearch
    reddit: RedditResearch
    twitter: TwitterResearch
    brand: str
    brief: str


@dataclass
class Iteration:
    attempt: int
    draft: str
    scores: dict[str, int] = field(default_factory=dict)
    diagnosis: str = ""
    passed: bool = False


@dataclass
class HookOption:
    style: str
    text: str
    iterations: list[Iteration] = field(default_factory=list)
    final_scores: dict[str, int] = field(default_factory=dict)


@dataclass
class ManagedResult:
    final_text: str
    iterations: list[Iteration] = field(default_factory=list)
    final_scores: dict[str, int] = field(default_factory=dict)
    passed: bool = False


@dataclass
class ScriptDraft:
    hooks: list[HookOption] = field(default_factory=list)
    body: str = ""
    body_iterations: list[Iteration] = field(default_factory=list)
    ctas: list[str] = field(default_factory=list)
    cta_iterations: list[list[Iteration]] = field(default_factory=list)


@dataclass
class ScoredLine:
    text: str
    invention_novelty: int = 0
    copy_intensity: int = 0
    rewritten: bool = False
    original: str | None = None
    cut: bool = False


@dataclass
class FinalScript:
    hooks: list[HookOption] = field(default_factory=list)
    body_lines: list[ScoredLine] = field(default_factory=list)
    ctas: list[str] = field(default_factory=list)
    char_count: int = 0
    char_budget: int = 0


@dataclass
class PipelineResult:
    research: ResearchBundle
    draft: ScriptDraft
    final: FinalScript
    paper_trail: dict = field(default_factory=dict)
