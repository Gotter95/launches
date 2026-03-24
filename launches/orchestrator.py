"""Main pipeline orchestrator — coordinates all phases."""

from __future__ import annotations

import asyncio

from launches.core.logger import PaperTrailLogger
from launches.core.models import (
    ContentDraft,
    FinalContent,
    PipelineResult,
)
from launches.output.renderer import render_output
from launches.voice.analyzer import VoiceAnalyzer
from launches.weapons.checker import VoiceChecker
from launches.writing.email import run_email_pipeline
from launches.writing.linkedin import run_linkedin_pipeline
from launches.writing.twitter import run_twitter_pipeline


async def run_pipeline(
    topic: str,
    samples: str,
    output_dir: str = "./output",
) -> PipelineResult:
    """Run the full multi-agent content generation pipeline.

    Phase 1: Voice analysis (1 agent)
    Phase 2: Content generation (3 agents in parallel, each with manager gating)
    Phase 3: Voice consistency check (3 checks in parallel)
    Phase 4: Output rendering
    """
    logger = PaperTrailLogger()

    # ═══════════════════════════════════════════
    # PHASE 1: VOICE ANALYSIS
    # ═══════════════════════════════════════════
    print("\n" + "=" * 60)
    print("PHASE 1: VOICE ANALYSIS")
    print("Analyzing writing samples to build voice fingerprint...")
    print("=" * 60)

    analyzer = VoiceAnalyzer()
    voice = await analyzer.run(samples)

    logger.log("voice", "voice_analyzer", {"summary": voice.summary})

    print("  Voice analysis complete.")
    print(f"  Tone: {voice.tone[:80]}{'...' if len(voice.tone) > 80 else ''}")
    print(f"  Traits: {', '.join(voice.personality_traits[:5])}")
    print(f"  Quirks: {', '.join(voice.stylistic_quirks[:3])}")

    # ═══════════════════════════════════════════
    # PHASE 2: CONTENT GENERATION (3 platforms in parallel)
    # ═══════════════════════════════════════════
    print("\n" + "=" * 60)
    print("PHASE 2: CONTENT GENERATION")
    print("Writing LinkedIn, Twitter, and Email content in parallel...")
    print("=" * 60)

    linkedin_piece, twitter_piece, email_piece = await asyncio.gather(
        run_linkedin_pipeline(topic, voice),
        run_twitter_pipeline(topic, voice),
        run_email_pipeline(topic, voice),
    )

    print(f"\n  [linkedin] Complete after {len(linkedin_piece.iterations)} iterations")
    print(f"  [twitter] Complete after {len(twitter_piece.iterations)} iterations")
    print(f"  [email] Complete after {len(email_piece.iterations)} iterations")

    draft = ContentDraft(
        linkedin=linkedin_piece,
        twitter=twitter_piece,
        email=email_piece,
    )

    # ═══════════════════════════════════════════
    # PHASE 3: VOICE CONSISTENCY CHECK
    # ═══════════════════════════════════════════
    print("\n" + "=" * 60)
    print("PHASE 3: VOICE CHECK")
    print("Scoring every piece on Voice Authenticity and Platform Fit...")
    print("=" * 60)

    checker = VoiceChecker()

    linkedin_scored, twitter_scored, email_scored = await asyncio.gather(
        checker.check("linkedin", linkedin_piece.text, voice),
        checker.check("twitter", twitter_piece.text, voice),
        checker.check("email", email_piece.text, voice),
    )

    for scored in [linkedin_scored, twitter_scored, email_scored]:
        status = "PASS" if (scored.voice_authenticity >= 10 and scored.platform_fit >= 10) else "REWRITTEN" if scored.rewritten else "KEPT"
        print(f"  [{scored.platform}] {status} — voice: {scored.voice_authenticity}/10, fit: {scored.platform_fit}/10")

    final = FinalContent(
        linkedin=linkedin_scored,
        twitter=twitter_scored,
        email=email_scored,
    )

    # ═══════════════════════════════════════════
    # PHASE 4: OUTPUT
    # ═══════════════════════════════════════════
    print("\n" + "=" * 60)
    print("PHASE 4: OUTPUT")
    print("=" * 60)

    result = PipelineResult(
        voice=voice,
        draft=draft,
        final=final,
        paper_trail={"entries": logger.get_trail()},
    )

    output_path = render_output(result, output_dir)
    print(f"\n  Output written to: {output_path}/")
    print(f"    01_voice_profile.md  — Voice fingerprint analysis")
    print(f"    02_working_drafts.md — All iterations & paper trail")
    print(f"    03_final_content.md  — Production-ready content")

    return result
