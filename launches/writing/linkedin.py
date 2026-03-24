"""LinkedIn content writing agent and manager."""

from __future__ import annotations

from launches.config import (
    LINKEDIN_DIMENSIONS,
    MANAGER_MAX_TOKENS,
    MANAGER_MODEL,
    MAX_TOKENS,
    MODEL,
)
from launches.core.agent import Agent
from launches.core.manager import ManagedAgent
from launches.core.models import ContentPiece, ManagedResult, VoiceProfile
from launches.prompts.managers import LINKEDIN_MANAGER_PROMPT
from launches.prompts.writing import LINKEDIN_SYSTEM_PROMPT


def _format_voice(voice: VoiceProfile) -> str:
    """Format voice profile for inclusion in prompts."""
    parts = [f"VOICE SUMMARY: {voice.summary}"]
    if voice.tone:
        parts.append(f"TONE: {voice.tone}")
    if voice.vocabulary_patterns:
        parts.append(f"VOCABULARY: {', '.join(voice.vocabulary_patterns)}")
    if voice.sentence_structure:
        parts.append(f"SENTENCE STRUCTURE: {voice.sentence_structure}")
    if voice.personality_traits:
        parts.append(f"PERSONALITY: {', '.join(voice.personality_traits)}")
    if voice.stylistic_quirks:
        parts.append(f"QUIRKS: {', '.join(voice.stylistic_quirks)}")
    if voice.emotional_range:
        parts.append(f"EMOTIONAL RANGE: {voice.emotional_range}")
    return "\n".join(parts)


async def run_linkedin_pipeline(
    topic: str, voice: VoiceProfile
) -> ContentPiece:
    """Write a LinkedIn post with manager gating."""
    worker = Agent(
        name="linkedin_writer",
        system_prompt=LINKEDIN_SYSTEM_PROMPT,
        model=MODEL,
        max_tokens=MAX_TOKENS,
    )
    manager = Agent(
        name="linkedin_manager",
        system_prompt=LINKEDIN_MANAGER_PROMPT,
        model=MANAGER_MODEL,
        max_tokens=MANAGER_MAX_TOKENS,
    )

    managed = ManagedAgent(worker, manager, LINKEDIN_DIMENSIONS)

    voice_text = _format_voice(voice)
    prompt = (
        f"TOPIC: {topic}\n\n"
        f"VOICE PROFILE:\n{voice_text}\n\n"
        f"Write a LinkedIn post about this topic in EXACTLY this person's voice. "
        f"It must be indistinguishable from something they'd actually post."
    )

    result: ManagedResult = await managed.run(prompt)

    return ContentPiece(
        platform="linkedin",
        text=result.final_text,
        iterations=result.iterations,
        final_scores=result.final_scores,
    )
