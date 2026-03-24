"""Hook writing agent and manager."""

from __future__ import annotations

import json
from dataclasses import asdict

from launches.config import HOOK_DIMENSIONS, MANAGER_MODEL, MANAGER_MAX_TOKENS, MODEL, MAX_TOKENS
from launches.core.agent import Agent
from launches.core.manager import ManagedAgent
from launches.core.models import HookOption, ManagedResult, ResearchBundle
from launches.prompts.managers import HOOK_MANAGER_PROMPT
from launches.prompts.writing import HOOK_SYSTEM_PROMPT


def create_hook_agent(style: str) -> tuple[ManagedAgent, str]:
    """Create a managed hook agent for a specific style."""
    worker = Agent(
        name=f"hook_writer_{style}",
        system_prompt=HOOK_SYSTEM_PROMPT.format(hook_style=style),
        model=MODEL,
        max_tokens=MAX_TOKENS,
    )
    manager = Agent(
        name=f"hook_manager_{style}",
        system_prompt=HOOK_MANAGER_PROMPT,
        model=MANAGER_MODEL,
        max_tokens=MANAGER_MAX_TOKENS,
    )
    return ManagedAgent(worker, manager, HOOK_DIMENSIONS), style


def build_hook_prompt(brand: str, brief: str, research: ResearchBundle) -> str:
    """Build the user prompt for hook writing with research context."""
    research_summary = _summarize_research(research)
    return (
        f"BRAND: {brand}\n"
        f"PRODUCT BRIEF: {brief}\n\n"
        f"RESEARCH DATA:\n{research_summary}\n\n"
        f"Write your hook. Make it lethal. Every word must earn its place."
    )


async def run_hook_pipeline(
    brand: str, brief: str, research: ResearchBundle
) -> list[HookOption]:
    """Run all 4 hook agents in parallel, each with manager gating."""
    import asyncio

    prompt = build_hook_prompt(brand, brief, research)

    agents_and_styles = [
        create_hook_agent(style)
        for style in ["contrarian", "story", "statistic", "question"]
    ]

    tasks = [agent.run(prompt) for agent, _ in agents_and_styles]
    results: list[ManagedResult] = await asyncio.gather(*tasks)

    hooks = []
    for (_, style), result in zip(agents_and_styles, results):
        hooks.append(
            HookOption(
                style=style,
                text=result.final_text,
                iterations=result.iterations,
                final_scores=result.final_scores,
            )
        )

    return hooks


def _summarize_research(research: ResearchBundle) -> str:
    """Create a condensed research summary for the writing agents."""
    parts = []

    if research.youtube.summary:
        parts.append(f"YOUTUBE INSIGHTS:\n{research.youtube.summary}")
    if research.youtube.top_title_patterns:
        parts.append(
            f"TOP TITLE PATTERNS: {', '.join(research.youtube.top_title_patterns[:10])}"
        )

    if research.reddit.summary:
        parts.append(f"\nREDDIT INSIGHTS:\n{research.reddit.summary}")
    if research.reddit.pain_points:
        quotes = [p.quote for p in research.reddit.pain_points[:5]]
        parts.append(f"CUSTOMER PAIN QUOTES:\n" + "\n".join(f'- "{q}"' for q in quotes))

    if research.twitter.summary:
        parts.append(f"\nTWITTER/X INSIGHTS:\n{research.twitter.summary}")
    if research.twitter.high_qt_ratio:
        hot_takes = [p.text for p in research.twitter.high_qt_ratio[:5]]
        parts.append(
            f"HIGH-CONTROVERSY POSTS:\n" + "\n".join(f"- {t}" for t in hot_takes)
        )

    return "\n".join(parts) if parts else "No research data available."
