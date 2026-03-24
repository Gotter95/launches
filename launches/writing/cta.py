"""CTA writing agent and manager."""

from __future__ import annotations

import asyncio

from launches.config import (
    CTA_DIMENSIONS,
    CTA_STYLES,
    MANAGER_MAX_TOKENS,
    MANAGER_MODEL,
    MAX_TOKENS,
    MODEL,
)
from launches.core.agent import Agent
from launches.core.manager import ManagedAgent
from launches.core.models import ManagedResult
from launches.prompts.managers import CTA_MANAGER_PROMPT
from launches.prompts.writing import CTA_SYSTEM_PROMPT


async def run_cta_pipeline(
    brand: str, brief: str, body_text: str
) -> list[ManagedResult]:
    """Run CTA agents for both styles in parallel with manager gating."""
    tasks = []
    for style in CTA_STYLES:
        worker = Agent(
            name=f"cta_writer_{style}",
            system_prompt=CTA_SYSTEM_PROMPT.format(cta_style=style),
            model=MODEL,
            max_tokens=MAX_TOKENS,
        )
        manager = Agent(
            name=f"cta_manager_{style}",
            system_prompt=CTA_MANAGER_PROMPT,
            model=MANAGER_MODEL,
            max_tokens=MANAGER_MAX_TOKENS,
        )
        managed = ManagedAgent(worker, manager, CTA_DIMENSIONS)

        prompt = (
            f"BRAND: {brand}\n"
            f"PRODUCT BRIEF: {brief}\n\n"
            f"BODY SCRIPT (for context and flow):\n{body_text}\n\n"
            f"Write a {style} CTA that flows naturally from the body. "
            f"Make it impossible to not click."
        )
        tasks.append(managed.run(prompt))

    return await asyncio.gather(*tasks)
