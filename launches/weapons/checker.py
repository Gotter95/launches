"""Weapons check: line-by-line scoring and rewriting."""

from __future__ import annotations

import asyncio

from launches.config import (
    FILLER_THRESHOLD,
    MAX_TOKENS,
    MODEL,
    REQUIRED_SCORE,
    WEAPONS_BATCH_SIZE,
)
from launches.core.agent import Agent, parse_json_from_response
from launches.core.models import ScoredLine
from launches.prompts.weapons import LINE_REWRITER_PROMPT, LINE_SCORER_PROMPT


class WeaponsChecker:
    """Scores every line on invention novelty and copy intensity, rewrites failures."""

    def __init__(self):
        self.scorer = Agent(
            name="weapons_scorer",
            system_prompt=LINE_SCORER_PROMPT,
            model=MODEL,
            max_tokens=MAX_TOKENS,
        )
        self.rewriter = Agent(
            name="weapons_rewriter",
            system_prompt=LINE_REWRITER_PROMPT,
            model=MODEL,
            max_tokens=MAX_TOKENS,
        )

    async def run(self, body_text: str, char_budget: int) -> list[ScoredLine]:
        """Score all lines, rewrite failures, cut filler, enforce budget."""
        lines = [l.strip() for l in body_text.strip().split("\n") if l.strip()]

        # Phase 1: Score all lines in batches
        scored = await self._score_lines(lines)

        # Phase 2: Identify failures and rewrite
        failures = [
            s for s in scored
            if not s.cut and (
                s.invention_novelty < REQUIRED_SCORE
                or s.copy_intensity < REQUIRED_SCORE
            )
        ]

        if failures:
            rewritten = await self._rewrite_lines(failures)
            # Replace in scored list
            rewrite_map = {r.original or r.text: r for r in rewritten}
            for i, s in enumerate(scored):
                if s.text in rewrite_map:
                    scored[i] = rewrite_map[s.text]

        # Phase 3: Cut filler
        scored = [s for s in scored if not s.cut]

        # Phase 4: Enforce character budget
        total = sum(len(s.text) for s in scored)
        if total > char_budget:
            scored = self._trim_to_budget(scored, char_budget)

        return scored

    async def _score_lines(self, lines: list[str]) -> list[ScoredLine]:
        """Score lines in parallel batches."""
        all_scored: list[ScoredLine] = []

        for i in range(0, len(lines), WEAPONS_BATCH_SIZE):
            batch = lines[i : i + WEAPONS_BATCH_SIZE]
            tasks = [self._score_single_line(line) for line in batch]
            batch_results = await asyncio.gather(*tasks)
            all_scored.extend(batch_results)

        return all_scored

    async def _score_single_line(self, line: str) -> ScoredLine:
        """Score a single line."""
        prompt = f"Score this line:\n\n\"{line}\""
        response = await self.scorer.run(prompt)
        parsed = parse_json_from_response(response.text)

        if parsed and isinstance(parsed, dict):
            scored_lines = parsed.get("scored_lines", [parsed])
            if scored_lines:
                s = scored_lines[0] if isinstance(scored_lines, list) else scored_lines
                novelty = s.get("invention_novelty", 5)
                intensity = s.get("copy_intensity", 5)
                return ScoredLine(
                    text=line,
                    invention_novelty=novelty,
                    copy_intensity=intensity,
                    cut=(novelty <= FILLER_THRESHOLD and intensity <= FILLER_THRESHOLD),
                )

        return ScoredLine(text=line, invention_novelty=7, copy_intensity=7)

    async def _rewrite_lines(self, failures: list[ScoredLine]) -> list[ScoredLine]:
        """Rewrite failed lines in parallel."""
        tasks = [self._rewrite_single(line) for line in failures]
        return await asyncio.gather(*tasks)

    async def _rewrite_single(self, scored: ScoredLine) -> ScoredLine:
        """Rewrite a single failed line."""
        prompt = (
            f"Rewrite this line to hit 10/10 on both dimensions:\n\n"
            f"Original: \"{scored.text}\"\n"
            f"Invention Novelty: {scored.invention_novelty}/10\n"
            f"Copy Intensity: {scored.copy_intensity}/10\n\n"
            f"Return valid JSON."
        )
        response = await self.rewriter.run(prompt)
        parsed = parse_json_from_response(response.text)

        if parsed and isinstance(parsed, dict):
            rewritten_lines = parsed.get("rewritten_lines", [parsed])
            if rewritten_lines:
                r = rewritten_lines[0] if isinstance(rewritten_lines, list) else rewritten_lines
                new_text = r.get("rewritten", "")
                if new_text == "CUT" or not new_text:
                    return ScoredLine(
                        text=scored.text,
                        invention_novelty=0,
                        copy_intensity=0,
                        cut=True,
                        original=scored.text,
                    )
                return ScoredLine(
                    text=new_text,
                    invention_novelty=r.get("new_novelty", 10),
                    copy_intensity=r.get("new_intensity", 10),
                    rewritten=True,
                    original=scored.text,
                )

        return scored

    def _trim_to_budget(
        self, scored: list[ScoredLine], budget: int
    ) -> list[ScoredLine]:
        """Remove lowest-scoring lines until within budget."""
        # Sort by combined score (keep highest)
        scored_with_idx = [
            (i, s, s.invention_novelty + s.copy_intensity) for i, s in enumerate(scored)
        ]
        scored_with_idx.sort(key=lambda x: x[2], reverse=True)

        kept: list[tuple[int, ScoredLine]] = []
        total = 0
        for idx, line, score in scored_with_idx:
            if total + len(line.text) <= budget:
                kept.append((idx, line))
                total += len(line.text)

        # Restore original order
        kept.sort(key=lambda x: x[0])
        return [line for _, line in kept]
