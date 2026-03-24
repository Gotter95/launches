"""CLI entry point for the launch script orchestrator."""

from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

from launches.config import DEFAULT_CHAR_BUDGET
from launches.orchestrator import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="launches",
        description=(
            "Multi-agent launch script orchestrator. "
            "20 specialized AI agents write production-ready video scripts."
        ),
    )
    parser.add_argument(
        "brand",
        help="Brand name",
    )
    parser.add_argument(
        "--brief",
        required=True,
        help="Product brief (text or path to .txt file)",
    )
    parser.add_argument(
        "--budget",
        type=int,
        default=DEFAULT_CHAR_BUDGET,
        help=f"Character budget for the script body (default: {DEFAULT_CHAR_BUDGET})",
    )
    parser.add_argument(
        "--output",
        default="./output",
        help="Output directory (default: ./output)",
    )

    args = parser.parse_args()

    # Load brief from file if it's a path
    brief = args.brief
    brief_path = Path(brief)
    if brief_path.exists() and brief_path.is_file():
        brief = brief_path.read_text().strip()
        print(f"Loaded brief from: {brief_path}")

    print("\n" + "=" * 60)
    print("LAUNCH SCRIPT ORCHESTRATOR")
    print("=" * 60)
    print(f"Brand:          {args.brand}")
    print(f"Brief:          {brief[:100]}{'...' if len(brief) > 100 else ''}")
    print(f"Char Budget:    {args.budget}")
    print(f"Output Dir:     {args.output}")
    print("=" * 60)

    start = time.monotonic()

    result = asyncio.run(
        run_pipeline(
            brand=args.brand,
            brief=brief,
            char_budget=args.budget,
            output_dir=args.output,
        )
    )

    elapsed = time.monotonic() - start
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    print("\n" + "=" * 60)
    print("COMPLETE")
    print(f"Time: {minutes}m {seconds}s")
    print(f"Hooks: {len(result.final.hooks)} options")
    print(f"Body: {len(result.final.body_lines)} lines")
    print(f"CTAs: {len(result.final.ctas)} options")
    print(f"Characters: {result.final.char_count}/{result.final.char_budget}")
    print("=" * 60)


if __name__ == "__main__":
    main()
