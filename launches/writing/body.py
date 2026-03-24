"""Body writing agent and manager."""

from __future__ import annotations

from launches.config import (
    BODY_DIMENSIONS,
    DEFAULT_CHAR_BUDGET,
    MANAGER_MAX_TOKENS,
    MANAGER_MODEL,
    MAX_TOKENS,
    MODEL,
)
from launches.core.agent import Agent
from launches.core.manager import ManagedAgent
from launches.core.models import HookOption, ManagedResult, ResearchBundle
from launches.prompts.managers import BODY_MANAGER_PROMPT
from launches.prompts.writing import BODY_SYSTEM_PROMPT
from launches.writing.hook import _summarize_research


async def run_body_pipeline(
    brand: str,
    brief: str,
    research: ResearchBundle,
    hooks: list[HookOption],
    char_budget: int = DEFAULT_CHAR_BUDGET,
) -> ManagedResult:
    """Write the body script with manager gating."""
    worker = Agent(
        name="body_writer",
        system_prompt=BODY_SYSTEM_PROMPT.format(char_budget=char_budget),
        model=MODEL,
        max_tokens=MAX_TOKENS,
    )
    manager = Agent(
        name="body_manager",
        system_prompt=BODY_MANAGER_PROMPT,
        model=MANAGER_MODEL,
        max_tokens=MANAGER_MAX_TOKENS,
    )

    managed = ManagedAgent(worker, manager, BODY_DIMENSIONS)

    research_summary = _summarize_research(research)
    hooks_text = "\n".join(
        f"[{h.style}] {h.text}" for h in hooks
    )

    prompt = (
        f"BRAND: {brand}\n"
        f"PRODUCT BRIEF: {brief}\n"
        f"CHARACTER BUDGET: {char_budget}\n\n"
        f"APPROVED HOOKS (for tone reference):\n{hooks_text}\n\n"
        f"RESEARCH DATA:\n{research_summary}\n\n"
        f"Write the body script. Every line must be a weapon. "
        f"Stay within {char_budget} characters."
    )

    return await managed.run(prompt)
