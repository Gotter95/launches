"""CLI entry point for the content generator."""

from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from launches.orchestrator import run_pipeline


def main() -> None:
    # Load .env file (ANTHROPIC_API_KEY, etc.)
    load_dotenv()
    parser = argparse.ArgumentParser(
        prog="launches",
        description=(
            "Multi-agent content generator. "
            "AI agents write LinkedIn, Twitter, and email content in your voice."
        ),
    )
    parser.add_argument(
        "topic",
        help="Topic to write about",
    )
    parser.add_argument(
        "--samples",
        required=True,
        help="Writing samples for voice training (text or path to .txt file)",
    )
    parser.add_argument(
        "--output",
        default="./output",
        help="Output directory (default: ./output)",
    )

    args = parser.parse_args()

    # Load samples from file if it's a path
    samples = args.samples
    samples_path = Path(samples)
    if samples_path.exists() and samples_path.is_file():
        samples = samples_path.read_text().strip()
        print(f"Loaded samples from: {samples_path}")

    print("\n" + "=" * 60)
    print("CONTENT GENERATOR")
    print("=" * 60)
    print(f"Topic:          {args.topic}")
    print(f"Samples:        {samples[:80]}{'...' if len(samples) > 80 else ''}")
    print(f"Output Dir:     {args.output}")
    print("=" * 60)

    start = time.monotonic()

    result = asyncio.run(
        run_pipeline(
            topic=args.topic,
            samples=samples,
            output_dir=args.output,
        )
    )

    elapsed = time.monotonic() - start
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    print("\n" + "=" * 60)
    print("COMPLETE")
    print(f"Time: {minutes}m {seconds}s")
    for section in [result.final.linkedin, result.final.twitter, result.final.email]:
        if section:
            status = "rewritten" if section.rewritten else "original"
            print(f"  {section.platform}: {len(section.text)} chars ({status})")
    print("=" * 60)


if __name__ == "__main__":
    main()
