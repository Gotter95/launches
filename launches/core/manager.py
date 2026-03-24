"""Manager-gated agent loop for enforcing quality bars."""

from __future__ import annotations

import json

from launches.config import MAX_MANAGER_ITERATIONS, REQUIRED_SCORE
from launches.core.agent import Agent, parse_json_from_response
from launches.core.models import Iteration, ManagedResult


class ManagedAgent:
    """Wraps a worker agent with a manager agent that scores and gates output.

    The loop:
    1. Worker produces output
    2. Manager scores on N dimensions (each 1-10)
    3. If all dimensions == REQUIRED_SCORE: accept
    4. Else: Manager writes diagnosis, worker rewrites
    5. Repeat up to max_iterations
    """

    def __init__(
        self,
        worker: Agent,
        manager: Agent,
        dimensions: list[str],
        max_iterations: int = MAX_MANAGER_ITERATIONS,
    ):
        self.worker = worker
        self.manager = manager
        self.dimensions = dimensions
        self.max_iterations = max_iterations

    async def run(self, user_message: str) -> ManagedResult:
        iterations: list[Iteration] = []
        best_text = ""
        best_scores: dict[str, int] = {}
        best_min_score = 0

        for attempt in range(1, self.max_iterations + 1):
            # Step 1: Worker produces output
            if attempt == 1:
                worker_prompt = user_message
            else:
                last = iterations[-1]
                worker_prompt = (
                    f"{user_message}\n\n"
                    f"--- PREVIOUS ATTEMPT (scored below 10/10) ---\n"
                    f"{last.draft}\n\n"
                    f"--- MANAGER DIAGNOSIS ---\n"
                    f"{last.diagnosis}\n\n"
                    f"--- SCORES ---\n"
                    f"{json.dumps(last.scores, indent=2)}\n\n"
                    f"Rewrite to address every issue. Every dimension must hit 10/10."
                )

            worker_response = await self.worker.run(worker_prompt)
            draft = worker_response.text

            # Step 2: Manager scores
            manager_prompt = self._build_manager_prompt(draft)
            manager_response = await self.manager.run(manager_prompt)
            scores, diagnosis = self._parse_manager_response(manager_response.text)

            # Check if all dimensions pass
            passed = all(scores.get(d, 0) >= REQUIRED_SCORE for d in self.dimensions)

            iteration = Iteration(
                attempt=attempt,
                draft=draft,
                scores=scores,
                diagnosis=diagnosis,
                passed=passed,
            )
            iterations.append(iteration)

            # Track best result
            min_score = min(scores.get(d, 0) for d in self.dimensions) if scores else 0
            if min_score > best_min_score:
                best_min_score = min_score
                best_text = draft
                best_scores = scores

            if passed:
                return ManagedResult(
                    final_text=draft,
                    iterations=iterations,
                    final_scores=scores,
                    passed=True,
                )

            print(
                f"  [{self.worker.name}] Attempt {attempt}/{self.max_iterations} "
                f"- min score: {min_score}/10"
            )

        # Return best result even if not perfect
        print(
            f"  [{self.worker.name}] Hit iteration cap. "
            f"Best min score: {best_min_score}/10"
        )
        return ManagedResult(
            final_text=best_text,
            iterations=iterations,
            final_scores=best_scores,
            passed=False,
        )

    def _build_manager_prompt(self, draft: str) -> str:
        dims_list = "\n".join(f"- {d}" for d in self.dimensions)
        json_example = (
            '{"scores": {"dimension_name": score, ...}, '
            '"diagnosis": "What failed and why. Be specific about which lines '
            'are weak and exactly how to fix them.", '
            '"passed": true/false}'
        )
        return (
            f"Score the following draft on each dimension (1-10). "
            f"Every dimension must be 10/10 to pass. A 9 is NOT a 10.\n\n"
            f"DIMENSIONS:\n{dims_list}\n\n"
            f"DRAFT:\n{draft}\n\n"
            f"Respond with valid JSON:\n{json_example}"
        )

    def _parse_manager_response(self, text: str) -> tuple[dict[str, int], str]:
        parsed = parse_json_from_response(text)
        if parsed and isinstance(parsed, dict):
            scores = parsed.get("scores", {})
            diagnosis = parsed.get("diagnosis", "")
            return scores, diagnosis

        # Fallback: try to extract scores manually
        scores = {}
        for dim in self.dimensions:
            for line in text.split("\n"):
                if dim in line:
                    for word in line.split():
                        try:
                            val = int(word.strip("/10,."))
                            if 1 <= val <= 10:
                                scores[dim] = val
                                break
                        except ValueError:
                            continue
        return scores, text
