"""Reddit research agent."""

from __future__ import annotations

from launches.config import MODEL, MAX_TOKENS
from launches.core.agent import Agent, parse_json_from_response
from launches.core.models import PainPoint, RedditResearch, ThreadData
from launches.prompts.research import REDDIT_SYSTEM_PROMPT


class RedditResearchAgent:
    """Mines Reddit for customer pain, desire, and controversy."""

    def __init__(self):
        self.agent = Agent(
            name="reddit_research",
            system_prompt=REDDIT_SYSTEM_PROMPT,
            model=MODEL,
            max_tokens=MAX_TOKENS,
        )

    async def run(self, brand: str, brief: str) -> RedditResearch:
        prompt = (
            f"BRAND: {brand}\n"
            f"PRODUCT BRIEF: {brief}\n\n"
            f"Mine Reddit for customer pain points, viral threads, and controversy. "
            f"Find exact quotes. Return valid JSON."
        )

        response = await self.agent.run(prompt)
        parsed = parse_json_from_response(response.text)

        if parsed and isinstance(parsed, dict):
            return self._build_research(parsed)

        return RedditResearch(summary=response.text)

    def _build_research(self, data: dict) -> RedditResearch:
        pain_points = [
            PainPoint(
                quote=p.get("quote", ""),
                source=p.get("source", ""),
                upvotes=p.get("upvotes", 0),
                context=p.get("context", ""),
            )
            for p in data.get("pain_points", [])
        ]

        viral_threads = [
            ThreadData(
                title=t.get("title", ""),
                subreddit=t.get("subreddit", ""),
                engagement=t.get("engagement", ""),
                key_quotes=t.get("key_quotes", []),
            )
            for t in data.get("viral_threads", [])
        ]

        controversial = [
            ThreadData(
                title=t.get("title", ""),
                subreddit=t.get("subreddit", ""),
                engagement=t.get("engagement", ""),
                key_quotes=t.get("key_quotes", []),
            )
            for t in data.get("controversial", [])
        ]

        return RedditResearch(
            pain_points=pain_points,
            viral_threads=viral_threads,
            controversial=controversial,
            summary=data.get("summary", ""),
        )
