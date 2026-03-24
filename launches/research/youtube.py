"""YouTube research agent."""

from __future__ import annotations

from launches.config import MODEL, MAX_TOKENS
from launches.core.agent import Agent, parse_json_from_response
from launches.core.models import KeywordResult, VideoData, YouTubeResearch
from launches.prompts.research import YOUTUBE_SYSTEM_PROMPT


class YouTubeResearchAgent:
    """Runs comprehensive YouTube research for a brand/product."""

    def __init__(self):
        self.agent = Agent(
            name="youtube_research",
            system_prompt=YOUTUBE_SYSTEM_PROMPT,
            model=MODEL,
            max_tokens=MAX_TOKENS,
        )

    async def run(self, brand: str, brief: str) -> YouTubeResearch:
        prompt = (
            f"BRAND: {brand}\n"
            f"PRODUCT BRIEF: {brief}\n\n"
            f"Run a full YouTube research sweep. Generate 15 keywords, analyze across "
            f"all 3 time filters, and find ceiling/floor patterns. Return valid JSON."
        )

        response = await self.agent.run(prompt)
        parsed = parse_json_from_response(response.text)

        if parsed and isinstance(parsed, dict):
            return self._build_research(parsed)

        return YouTubeResearch(summary=response.text)

    def _build_research(self, data: dict) -> YouTubeResearch:
        keywords = []
        for kw in data.get("keywords", []):
            ceiling = [
                VideoData(
                    title=v.get("title", ""),
                    views=v.get("views", ""),
                    channel=v.get("channel", ""),
                    age=v.get("age", ""),
                    pattern_notes=v.get("pattern_notes", ""),
                )
                for v in kw.get("ceiling", [])
            ]
            keywords.append(
                KeywordResult(
                    keyword=kw.get("keyword", ""),
                    time_filter=kw.get("time_filter", ""),
                    ceiling=ceiling,
                    floor_views=kw.get("floor_views", ""),
                    title_patterns=kw.get("title_patterns", []),
                )
            )

        return YouTubeResearch(
            keywords=keywords,
            top_title_patterns=data.get("top_title_patterns", []),
            summary=data.get("summary", ""),
        )
