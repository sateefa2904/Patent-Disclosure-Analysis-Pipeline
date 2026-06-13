#!/usr/bin/env python3
"""
LegalReport — CLI
Usage:
  python cli.py --input sample_inputs/example.json --format markdown
  python cli.py --input sample_inputs/example.json --format html --output outputs/report.html
  python cli.py --input sample_inputs/example.json --format json
"""

import argparse
import json
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.pipeline import LegalReportPipeline, DisclosureInput, PriorArtReference
from core.formatter import to_markdown, to_json, to_html


def load_input(path: str) -> DisclosureInput:
    """Load and parse a disclosure JSON file."""
    with open(path) as f:
        data = json.load(f)

    prior_art = [
        PriorArtReference(
            title=r["title"],
            source=r["source"],
            relevance_notes=r["relevance_notes"]
        )
        for r in data.get("prior_art_references", [])
    ]

    return DisclosureInput(
        invention_title=data["invention_title"],
        technical_summary=data["technical_summary"],
        claimed_novelty=data["claimed_novelty"],
        prior_art_references=prior_art,
        inventor_notes=data.get("inventor_notes")
    )


def main():
    parser = argparse.ArgumentParser(
        description="LegalReport — Patent Disclosure Analysis Pipeline"
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to disclosure JSON file"
    )
    parser.add_argument(
        "--format", choices=["markdown", "json", "html"], default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "--output", default=None,
        help="Output file path (default: prints to stdout)"
    )
    parser.add_argument(
        "--api-key", default=None,
        help="Anthropic API key (or set ANTHROPIC_API_KEY env var)"
    )

    args = parser.parse_args()

    # Load input
    try:
        disclosure = load_input(args.input)
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    except KeyError as e:
        print(f"Error: Missing required field in input JSON: {e}")
        sys.exit(1)

    # Run pipeline
    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")
    pipeline = LegalReportPipeline(api_key=api_key)
    report, validation = pipeline.run(disclosure)

    # Format output
    if args.format == "markdown":
        output = to_markdown(report)
    elif args.format == "json":
        output = to_json(report)
    else:
        output = to_html(report)

    # Write or print
    if args.output:
        os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
        with open(args.output, "w") as f:
            f.write(output)
        print(f"\n✓ Report saved to: {args.output}")
    else:
        print("\n" + output)


if __name__ == "__main__":
    main()
