"""Main pipeline orchestrator — coordinates all phases."""

from __future__ import annotations

import asyncio

from launches.config import DEFAULT_CHAR_BUDGET
from launches.core.logger import PaperTrailLogger
from launches.core.models import (
    FinalScript,
    PipelineResult,
    ResearchBundle,
    ScriptDraft,
)
from launches.output.renderer import render_output
from launches.research.reddit import RedditResearchAgent
from launches.research.twitter import TwitterResearchAgent
from launches.research.youtube import YouTubeResearchAgent
from launches.weapons.checker import WeaponsChecker
from launches.writing.body import run_body_pipeline
from launches.writing.cta import run_cta_pipeline
from launches.writing.hook import run_hook_pipeline


async def run_pipeline(
    brand: str,
    brief: str,
    char_budget: int = DEFAULT_CHAR_BUDGET,
    output_dir: str = "./output",
) -> PipelineResult:
    """Run the full multi-agent launch script pipeline.

    Phase 1: Research (3 agents in parallel)
    Phase 2: Writing (hooks parallel, body sequential, CTAs parallel)
    Phase 3: Weapons check (line-by-line scoring)
    Phase 4: Output rendering
    """
    logger = PaperTrailLogger()

    # ═══════════════════════════════════════════
    # PHASE 1: RESEARCH (3 agents in parallel)
    # ═══════════════════════════════════════════
    print("\n" + "=" * 60)
    print("PHASE 1: RESEARCH")
    print("Running YouTube, Reddit, and Twitter agents in parallel...")
    print("=" * 60)

    yt_agent = YouTubeResearchAgent()
    reddit_agent = RedditResearchAgent()
    twitter_agent = TwitterResearchAgent()

    yt_result, reddit_result, twitter_result = await asyncio.gather(
        yt_agent.run(brand, brief),
        reddit_agent.run(brand, brief),
        twitter_agent.run(brand, brief),
    )

    research = ResearchBundle(
        youtube=yt_result,
        reddit=reddit_result,
        twitter=twitter_result,
        brand=brand,
        brief=brief,
    )

    logger.log("research", "youtube", {"summary": yt_result.summary})
    logger.log("research", "reddit", {"summary": reddit_result.summary})
    logger.log("research", "twitter", {"summary": twitter_result.summary})

    print("  Research complete.")
    print(f"  YouTube: {len(yt_result.keywords)} keyword results")
    print(f"  Reddit: {len(reddit_result.pain_points)} pain points")
    print(f"  Twitter: {len(twitter_result.top_posts)} posts analyzed")

    # ═══════════════════════════════════════════
    # PHASE 2: WRITING PIPELINE
    # ═══════════════════════════════════════════
    print("\n" + "=" * 60)
    print("PHASE 2: WRITING PIPELINE")
    print("=" * 60)

    # Step 2a: 4 Hook Agents in parallel (each with manager gating)
    print("\n--- Hooks (4 agents in parallel, each with manager loop) ---")
    hooks = await run_hook_pipeline(brand, brief, research)

    for h in hooks:
        status = "PASSED" if h.final_scores else "BEST EFFORT"
        print(f"  [{h.style}] {status} after {len(h.iterations)} iterations")

    # Step 2b: Body Agent (sequential — needs hooks for tone)
    print("\n--- Body (1 agent with manager loop) ---")
    body_result = await run_body_pipeline(brand, brief, research, hooks, char_budget)
    print(f"  Body complete after {len(body_result.iterations)} iterations")

    # Step 2c: 2 CTA Agents in parallel (need body for context)
    print("\n--- CTAs (2 agents in parallel, each with manager loop) ---")
    cta_results = await run_cta_pipeline(brand, brief, body_result.final_text)

    for i, cta in enumerate(cta_results):
        style = ["direct", "soft"][i]
        print(f"  [{style}] Complete after {len(cta.iterations)} iterations")

    # Build script draft
    draft = ScriptDraft(
        hooks=hooks,
        body=body_result.final_text,
        body_iterations=body_result.iterations,
        ctas=[r.final_text for r in cta_results],
        cta_iterations=[r.iterations for r in cta_results],
    )

    # ═══════════════════════════════════════════
    # PHASE 3: WEAPONS CHECK
    # ═══════════════════════════════════════════
    print("\n" + "=" * 60)
    print("PHASE 3: WEAPONS CHECK")
    print("Scoring every line on Invention Novelty and Copy Intensity...")
    print("=" * 60)

    checker = WeaponsChecker()
    scored_lines = await checker.run(body_result.final_text, char_budget)

    passed = sum(1 for s in scored_lines if s.invention_novelty >= 10 and s.copy_intensity >= 10)
    rewritten = sum(1 for s in scored_lines if s.rewritten)
    total_chars = sum(len(s.text) for s in scored_lines)

    print(f"  Lines passed: {passed}/{len(scored_lines)}")
    print(f"  Lines rewritten: {rewritten}")
    print(f"  Character count: {total_chars}/{char_budget}")

    # Build final script
    final = FinalScript(
        hooks=hooks,
        body_lines=scored_lines,
        ctas=[r.final_text for r in cta_results],
        char_count=total_chars,
        char_budget=char_budget,
    )

    # ═══════════════════════════════════════════
    # PHASE 4: OUTPUT
    # ═══════════════════════════════════════════
    print("\n" + "=" * 60)
    print("PHASE 4: OUTPUT")
    print("=" * 60)

    result = PipelineResult(
        research=research,
        draft=draft,
        final=final,
        paper_trail={"entries": logger.get_trail()},
    )

    output_path = render_output(result, output_dir)
    print(f"\n  Output written to: {output_path}/")
    print(f"    01_research.md      — Full research data")
    print(f"    02_working_script.md — All iterations & paper trail")
    print(f"    03_final_script.md  — Clean, production-ready script")

    return result
