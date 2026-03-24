"""Base agent class wrapping the Anthropic async API."""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass

import anthropic

from launches.config import MAX_CONCURRENT_AGENTS, MAX_TOKENS, MODEL

# Global semaphore to cap concurrent API calls
_semaphore = asyncio.Semaphore(MAX_CONCURRENT_AGENTS)


@dataclass
class AgentResponse:
    text: str
    usage: dict
    latency_ms: float
    model: str


class Agent:
    """Base agent that makes a single async Anthropic API call."""

    def __init__(
        self,
        name: str,
        system_prompt: str,
        model: str = MODEL,
        max_tokens: int = MAX_TOKENS,
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.max_tokens = max_tokens
        self._client = anthropic.AsyncAnthropic()

    async def run(self, user_message: str) -> AgentResponse:
        """Execute the agent with a user message and return the response."""
        async with _semaphore:
            start = time.monotonic()
            response = await self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            elapsed = (time.monotonic() - start) * 1000

            text = ""
            for block in response.content:
                if block.type == "text":
                    text += block.text

            return AgentResponse(
                text=text,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                latency_ms=elapsed,
                model=self.model,
            )

    def __repr__(self) -> str:
        return f"Agent(name={self.name!r}, model={self.model!r})"


def parse_json_from_response(text: str) -> dict | list | None:
    """Extract JSON from an agent response that may contain markdown fences."""
    # Try to find JSON in code blocks first
    if "```json" in text:
        start = text.index("```json") + 7
        end = text.index("```", start)
        return json.loads(text[start:end].strip())
    if "```" in text:
        start = text.index("```") + 3
        end = text.index("```", start)
        candidate = text[start:end].strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
    # Try parsing the whole text
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return None
