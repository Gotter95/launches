"""Twitter/X content writing agent and manager."""

from __future__ import annotations

from launches.config import (
    MANAGER_MAX_TOKENS,
    MANAGER_MODEL,
    MAX_TOKENS,
    MODEL,
    TWITTER_DIMENSIONS,
)
from launches.core.agent import Agent
from launches.core.manager import ManagedAgent
from launches.core.models import ContentPiece, ManagedResult, VoiceProfile
from launches.prompts.managers import TWITTER_MANAGER_PROMPT
from launches.prompts.writing import TWITTER_SYSTEM_PROMPT
from launches.writing.linkedin import _format_voice


async def run_twitter_pipeline(
    topic: str, voice: VoiceProfile
) -> ContentPiece:
    """Write a tweet thread with manager gating."""
    worker = Agent(
        name="twitter_writer",
        system_prompt=TWITTER_SYSTEM_PROMPT,
        model=MODEL,
        max_tokens=MAX_TOKENS,
    )
    manager = Agent(
        name="twitter_manager",
        system_prompt=TWITTER_MANAGER_PROMPT,
        model=MANAGER_MODEL,
        max_tokens=MANAGER_MAX_TOKENS,
    )

    managed = ManagedAgent(worker, manager, TWITTER_DIMENSIONS)

    voice_text = _format_voice(voice)
    prompt = (
        f"TOPIC: {topic}\n\n"
        f"VOICE PROFILE:\n{voice_text}\n\n"
        f"Write a tweet thread about this topic in EXACTLY this person's voice. "
        f"Every tweet must feel like them — their rhythm, their energy, their quirks."
    )

    result: ManagedResult = await managed.run(prompt)

    return ContentPiece(
        platform="twitter",
        text=result.final_text,
        iterations=result.iterations,
        final_scores=result.final_scores,
    )
