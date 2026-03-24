"""Twitter/X research agent."""

from __future__ import annotations

from launches.config import MODEL, MAX_TOKENS
from launches.core.agent import Agent, parse_json_from_response
from launches.core.models import PostData, TwitterResearch
from launches.prompts.research import TWITTER_SYSTEM_PROMPT


class TwitterResearchAgent:
    """Analyzes X/Twitter engagement patterns and controversy."""

    def __init__(self):
        self.agent = Agent(
            name="twitter_research",
            system_prompt=TWITTER_SYSTEM_PROMPT,
            model=MODEL,
            max_tokens=MAX_TOKENS,
        )

    async def run(self, brand: str, brief: str) -> TwitterResearch:
        prompt = (
            f"BRAND: {brand}\n"
            f"PRODUCT BRIEF: {brief}\n\n"
            f"Analyze X/Twitter for engagement patterns, ceiling/floor analysis, "
            f"and high quote-tweet ratio controversy posts. Return valid JSON."
        )

        response = await self.agent.run(prompt)
        parsed = parse_json_from_response(response.text)

        if parsed and isinstance(parsed, dict):
            return self._build_research(parsed)

        return TwitterResearch(summary=response.text)

    def _build_research(self, data: dict) -> TwitterResearch:
        def parse_posts(posts: list) -> list[PostData]:
            return [
                PostData(
                    text=p.get("text", ""),
                    engagement=p.get("engagement", ""),
                    quote_tweet_ratio=p.get("quote_tweet_ratio", ""),
                    author=p.get("author", ""),
                    notes=p.get("notes", ""),
                )
                for p in posts
            ]

        return TwitterResearch(
            top_posts=parse_posts(data.get("top_posts", [])),
            ceiling=parse_posts(data.get("ceiling", [])),
            floor=parse_posts(data.get("floor", [])),
            high_qt_ratio=parse_posts(data.get("high_qt_ratio", [])),
            summary=data.get("summary", ""),
        )
