"""Email content writing agent and manager."""

from __future__ import annotations

from launches.config import (
    EMAIL_DIMENSIONS,
    MANAGER_MAX_TOKENS,
    MANAGER_MODEL,
    MAX_TOKENS,
    MODEL,
)
from launches.core.agent import Agent
from launches.core.manager import ManagedAgent
from launches.core.models import ContentPiece, ManagedResult, VoiceProfile
from launches.prompts.managers import EMAIL_MANAGER_PROMPT
from launches.prompts.writing import EMAIL_SYSTEM_PROMPT
from launches.writing.linkedin import _format_voice


async def run_email_pipeline(
    topic: str, voice: VoiceProfile
) -> ContentPiece:
    """Write a newsletter email with manager gating."""
    worker = Agent(
        name="email_writer",
        system_prompt=EMAIL_SYSTEM_PROMPT,
        model=MODEL,
        max_tokens=MAX_TOKENS,
    )
    manager = Agent(
        name="email_manager",
        system_prompt=EMAIL_MANAGER_PROMPT,
        model=MANAGER_MODEL,
        max_tokens=MANAGER_MAX_TOKENS,
    )

    managed = ManagedAgent(worker, manager, EMAIL_DIMENSIONS)

    voice_text = _format_voice(voice)
    prompt = (
        f"TOPIC: {topic}\n\n"
        f"VOICE PROFILE:\n{voice_text}\n\n"
        f"Write a newsletter-style email about this topic in EXACTLY this person's voice. "
        f"Subject line first, then body, then sign-off. Must read like they wrote it."
    )

    result: ManagedResult = await managed.run(prompt)

    return ContentPiece(
        platform="email",
        text=result.final_text,
        iterations=result.iterations,
        final_scores=result.final_scores,
    )
