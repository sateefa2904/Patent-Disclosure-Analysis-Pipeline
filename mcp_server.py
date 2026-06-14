"""
LegalReport — MCP Server
Exposes the patent disclosure analysis pipeline as tools
that Claude can call directly in a conversation.

Run: python3 mcp_server.py
Then connect via Claude Desktop or any MCP client.

Tools exposed:
  - analyze_disclosure: full 5-stage pipeline analysis
  - assess_novelty: standalone novelty scoring
  - map_prior_art: compare invention against a single reference
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from core.pipeline import (
    LegalReportPipeline,
    DisclosureInput,
    PriorArtReference,
)
from core.formatter import to_markdown

# ── Server instance ───────────────────────────────────────────────────────────

server = Server("legalreport")
pipeline = LegalReportPipeline()


# ── Tool definitions ──────────────────────────────────────────────────────────

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """Register all tools Claude can call."""
    return [
        types.Tool(
            name="analyze_disclosure",
            description=(
                "Run a full 5-stage patent disclosure analysis pipeline. "
                "Takes an invention title, technical summary, claimed novelty, "
                "and optional prior art references. Returns a structured report "
                "including novelty assessment, prior art claim mapping, "
                "patentability outlook, and prosecution strategy recommendations. "
                "Use this when an attorney or user provides a patent disclosure "
                "and wants a complete analysis."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "invention_title": {
                        "type": "string",
                        "description": "The title of the invention being analyzed"
                    },
                    "technical_summary": {
                        "type": "string",
                        "description": "Detailed technical description of how the invention works"
                    },
                    "claimed_novelty": {
                        "type": "string",
                        "description": "What is new and non-obvious about this invention"
                    },
                    "inventor_notes": {
                        "type": "string",
                        "description": "Optional additional context from the inventor"
                    },
                    "prior_art_references": {
                        "type": "array",
                        "description": "List of prior art references to compare against",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "source": {"type": "string"},
                                "relevance_notes": {"type": "string"}
                            },
                            "required": ["title"]
                        }
                    }
                },
                "required": ["invention_title", "technical_summary"]
            }
        ),

        types.Tool(
            name="assess_novelty",
            description=(
                "Quickly assess the novelty of an invention against provided "
                "prior art references. Returns a score from 1-10, a label "
                "(Strong/Moderate/Weak/Unclear), and a rationale. "
                "Use this for a fast novelty check without a full analysis."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "invention_title": {
                        "type": "string",
                        "description": "The title of the invention"
                    },
                    "claimed_novelty": {
                        "type": "string",
                        "description": "The claimed novel aspects of the invention"
                    },
                    "prior_art_references": {
                        "type": "array",
                        "description": "Prior art to assess novelty against",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "source": {"type": "string"},
                                "relevance_notes": {"type": "string"}
                            },
                            "required": ["title"]
                        }
                    }
                },
                "required": ["invention_title", "claimed_novelty"]
            }
        ),

        types.Tool(
            name="map_prior_art",
            description=(
                "Compare a specific invention against a single prior art reference. "
                "Returns overlapping elements, distinguishing elements, and a risk "
                "level (High/Medium/Low). Use this when you want to analyze one "
                "prior art reference in depth."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "invention_title": {
                        "type": "string",
                        "description": "The title of the invention"
                    },
                    "technical_summary": {
                        "type": "string",
                        "description": "Technical description of the invention"
                    },
                    "claimed_novelty": {
                        "type": "string",
                        "description": "The claimed novel aspects"
                    },
                    "prior_art_title": {
                        "type": "string",
                        "description": "Title of the prior art reference"
                    },
                    "prior_art_source": {
                        "type": "string",
                        "description": "Source of the prior art (patent number, paper, etc.)"
                    },
                    "prior_art_relevance": {
                        "type": "string",
                        "description": "Notes on how this prior art relates to the invention"
                    }
                },
                "required": [
                    "invention_title", "technical_summary",
                    "claimed_novelty", "prior_art_title"
                ]
            }
        )
    ]


# ── Tool handlers ─────────────────────────────────────────────────────────────

@server.call_tool()
async def call_tool(
    name: str,
    arguments: dict
) -> list[types.TextContent]:
    """Handle tool calls from Claude."""

    try:
        if name == "analyze_disclosure":
            return await _handle_analyze_disclosure(arguments)
        elif name == "assess_novelty":
            return await _handle_assess_novelty(arguments)
        elif name == "map_prior_art":
            return await _handle_map_prior_art(arguments)
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Tool error: {str(e)}"
        )]


async def _handle_analyze_disclosure(args: dict) -> list[types.TextContent]:
    """Full 5-stage pipeline analysis."""
    prior_art = [
        PriorArtReference(
            title=r.get("title", ""),
            source=r.get("source", ""),
            relevance_notes=r.get("relevance_notes", "")
        )
        for r in args.get("prior_art_references", [])
    ]

    disclosure = DisclosureInput(
        invention_title=args["invention_title"],
        technical_summary=args["technical_summary"],
        claimed_novelty=args.get("claimed_novelty", ""),
        prior_art_references=prior_art,
        inventor_notes=args.get("inventor_notes")
    )

    # Run pipeline in thread pool to avoid blocking async event loop
    loop = asyncio.get_event_loop()
    report, validation = await loop.run_in_executor(
        None, lambda: pipeline.run(disclosure)
    )

    # Return as structured markdown the LLM can reason over
    result = {
        "disclosure_title": report.disclosure_title,
        "generated_at": report.generated_at,
        "novelty_assessment": {
            "score": report.novelty_assessment.score,
            "label": report.novelty_assessment.label,
            "rationale": report.novelty_assessment.rationale
        },
        "invention_summary": report.invention_summary,
        "claim_mappings": [
            {
                "prior_art_source": m.prior_art_source,
                "overlapping_elements": m.overlapping_elements,
                "distinguishing_elements": m.distinguishing_elements,
                "risk_level": m.risk_level
            }
            for m in report.claim_mappings
        ],
        "patentability_outlook": report.patentability_outlook,
        "recommended_claim_focus": report.recommended_claim_focus,
        "attorney_notes": report.attorney_notes,
        "pipeline_warnings": validation.get("warnings", [])
    }

    return [types.TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]


async def _handle_assess_novelty(args: dict) -> list[types.TextContent]:
    """Standalone novelty assessment."""
    prior_art = [
        PriorArtReference(
            title=r.get("title", ""),
            source=r.get("source", ""),
            relevance_notes=r.get("relevance_notes", "")
        )
        for r in args.get("prior_art_references", [])
    ]

    disclosure = DisclosureInput(
        invention_title=args["invention_title"],
        technical_summary=args.get("claimed_novelty", ""),
        claimed_novelty=args["claimed_novelty"],
        prior_art_references=prior_art
    )

    loop = asyncio.get_event_loop()
    novelty = await loop.run_in_executor(
        None, lambda: pipeline.stage_3_novelty(disclosure)
    )

    result = {
        "invention_title": args["invention_title"],
        "novelty_score": novelty.score,
        "novelty_label": novelty.label,
        "rationale": novelty.rationale
    }

    return [types.TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]


async def _handle_map_prior_art(args: dict) -> list[types.TextContent]:
    """Single prior art comparison."""
    ref = PriorArtReference(
        title=args["prior_art_title"],
        source=args.get("prior_art_source", ""),
        relevance_notes=args.get("prior_art_relevance", "")
    )

    disclosure = DisclosureInput(
        invention_title=args["invention_title"],
        technical_summary=args["technical_summary"],
        claimed_novelty=args["claimed_novelty"],
        prior_art_references=[ref]
    )

    loop = asyncio.get_event_loop()
    mappings = await loop.run_in_executor(
        None, lambda: pipeline.stage_4_claim_mapping(disclosure)
    )

    if mappings:
        m = mappings[0]
        result = {
            "prior_art_source": m.prior_art_source,
            "overlapping_elements": m.overlapping_elements,
            "distinguishing_elements": m.distinguishing_elements,
            "risk_level": m.risk_level
        }
    else:
        result = {"error": "No mapping produced"}

    return [types.TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]


# ── Entry point ───────────────────────────────────────────────────────────────

async def main():
    print("LegalReport MCP Server starting...", file=sys.stderr)
    print("Tools: analyze_disclosure, assess_novelty, map_prior_art", file=sys.stderr)
    print("Waiting for MCP client connection...", file=sys.stderr)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
