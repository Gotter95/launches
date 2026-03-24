"""Voice analysis agent."""

from __future__ import annotations

from launches.config import MAX_TOKENS, MODEL
from launches.core.agent import Agent, parse_json_from_response
from launches.core.models import VoiceProfile
from launches.prompts.voice import VOICE_ANALYZER_PROMPT


class VoiceAnalyzer:
    """Analyzes writing samples to build a voice fingerprint."""

    def __init__(self):
        self.agent = Agent(
            name="voice_analyzer",
            system_prompt=VOICE_ANALYZER_PROMPT,
            model=MODEL,
            max_tokens=MAX_TOKENS,
        )

    async def run(self, samples: str) -> VoiceProfile:
        prompt = (
            f"WRITING SAMPLES:\n\n{samples}\n\n"
            f"Analyze these samples and produce a detailed voice fingerprint. "
            f"Be extremely specific — generic descriptions are useless. "
            f"Return valid JSON."
        )

        response = await self.agent.run(prompt)
        parsed = parse_json_from_response(response.text)

        if parsed and isinstance(parsed, dict):
            return self._build_profile(parsed)

        return VoiceProfile(summary=response.text)

    def _build_profile(self, data: dict) -> VoiceProfile:
        return VoiceProfile(
            tone=data.get("tone", ""),
            vocabulary_patterns=data.get("vocabulary_patterns", []),
            sentence_structure=data.get("sentence_structure", ""),
            personality_traits=data.get("personality_traits", []),
            recurring_themes=data.get("recurring_themes", []),
            stylistic_quirks=data.get("stylistic_quirks", []),
            emotional_range=data.get("emotional_range", ""),
            summary=data.get("summary", ""),
        )
