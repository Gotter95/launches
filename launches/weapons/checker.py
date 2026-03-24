"""Voice consistency check: scoring and rewriting for voice match."""

from __future__ import annotations

from launches.config import MAX_TOKENS, MODEL
from launches.core.agent import Agent, parse_json_from_response
from launches.core.models import ScoredSection, VoiceProfile
from launches.prompts.weapons import VOICE_REWRITER_PROMPT, VOICE_SCORER_PROMPT
from launches.writing.linkedin import _format_voice


class VoiceChecker:
    """Scores content on voice authenticity and platform fit, rewrites failures."""

    def __init__(self):
        self.scorer = Agent(
            name="voice_scorer",
            system_prompt=VOICE_SCORER_PROMPT,
            model=MODEL,
            max_tokens=MAX_TOKENS,
        )
        self.rewriter = Agent(
            name="voice_rewriter",
            system_prompt=VOICE_REWRITER_PROMPT,
            model=MODEL,
            max_tokens=MAX_TOKENS,
        )

    async def check(
        self, platform: str, text: str, voice: VoiceProfile
    ) -> ScoredSection:
        """Score a content piece and rewrite if it fails."""
        voice_text = _format_voice(voice)

        # Phase 1: Score
        score_prompt = (
            f"PLATFORM: {platform}\n\n"
            f"VOICE PROFILE:\n{voice_text}\n\n"
            f"CONTENT TO SCORE:\n{text}"
        )
        score_response = await self.scorer.run(score_prompt)
        parsed = parse_json_from_response(score_response.text)

        authenticity = 7
        platform_fit = 7
        diagnosis = ""

        if parsed and isinstance(parsed, dict):
            authenticity = parsed.get("voice_authenticity", 7)
            platform_fit = parsed.get("platform_fit", 7)
            diagnosis = parsed.get("diagnosis", "")

        passed = authenticity >= 10 and platform_fit >= 10

        if passed:
            return ScoredSection(
                platform=platform,
                text=text,
                voice_authenticity=authenticity,
                platform_fit=platform_fit,
            )

        # Phase 2: Rewrite if failed
        rewrite_prompt = (
            f"PLATFORM: {platform}\n\n"
            f"VOICE PROFILE:\n{voice_text}\n\n"
            f"ORIGINAL CONTENT:\n{text}\n\n"
            f"VOICE AUTHENTICITY SCORE: {authenticity}/10\n"
            f"PLATFORM FIT SCORE: {platform_fit}/10\n"
            f"DIAGNOSIS: {diagnosis}\n\n"
            f"Rewrite to hit 10/10 on both dimensions. Return valid JSON."
        )
        rewrite_response = await self.rewriter.run(rewrite_prompt)
        rewrite_parsed = parse_json_from_response(rewrite_response.text)

        if rewrite_parsed and isinstance(rewrite_parsed, dict):
            rewritten = rewrite_parsed.get("rewritten", "")
            if rewritten:
                return ScoredSection(
                    platform=platform,
                    text=rewritten,
                    voice_authenticity=10,
                    platform_fit=10,
                    rewritten=True,
                    original=text,
                )

        # Fallback: return original with scores
        return ScoredSection(
            platform=platform,
            text=text,
            voice_authenticity=authenticity,
            platform_fit=platform_fit,
        )
