"""
LegalReport Pipeline — Core Engine
Processes patent disclosures through a multi-stage analysis pipeline
and generates structured, attorney-ready reports.
"""

import anthropic
import json
import re
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime


# ── Data models ──────────────────────────────────────────────────────────────

@dataclass
class PriorArtReference:
    title: str
    source: str          # patent number, paper title, product name
    relevance_notes: str

@dataclass
class DisclosureInput:
    invention_title: str
    technical_summary: str
    claimed_novelty: str
    prior_art_references: list[PriorArtReference]
    inventor_notes: Optional[str] = None

@dataclass
class NoveltyAssessment:
    score: int           # 1-10
    label: str           # Strong / Moderate / Weak / Unclear
    rationale: str

@dataclass
class ClaimMapping:
    prior_art_source: str
    overlapping_elements: list[str]
    distinguishing_elements: list[str]
    risk_level: str      # High / Medium / Low

@dataclass
class AnalysisReport:
    disclosure_title: str
    generated_at: str
    invention_summary: str
    novelty_assessment: NoveltyAssessment
    claim_mappings: list[ClaimMapping]
    patentability_outlook: str
    recommended_claim_focus: str
    attorney_notes: str
    raw_prior_art_count: int


# ── Pipeline stages ───────────────────────────────────────────────────────────

class LegalReportPipeline:
    """
    Five-stage pipeline:
      1. Ingest & validate input
      2. Generate invention summary
      3. Assess novelty
      4. Map claims against prior art
      5. Synthesize final report
    """

    def __init__(self, api_key: Optional[str] = None):
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
        self.model = "claude-sonnet-4-6"

    def _call_claude(self, system: str, user: str, max_tokens: int = 1000) -> str:
        """Single Claude API call with structured system + user prompt."""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": user}],
            system=system
        )
        return message.content[0].text.strip()

    # Stage 1: Validate
    def stage_1_validate(self, disclosure: DisclosureInput) -> dict:
        """Validate input completeness and flag missing data."""
        issues = []
        if not disclosure.technical_summary or len(disclosure.technical_summary) < 50:
            issues.append("Technical summary too brief — analysis quality may be reduced")
        if not disclosure.claimed_novelty:
            issues.append("No claimed novelty provided — novelty assessment will be inferred")
        if not disclosure.prior_art_references:
            issues.append("No prior art references provided — comparative analysis unavailable")

        return {
            "valid": len([i for i in issues if "unavailable" in i]) == 0,
            "warnings": issues,
            "prior_art_count": len(disclosure.prior_art_references)
        }

    # Stage 2: Invention summary
    def stage_2_summarize(self, disclosure: DisclosureInput) -> str:
        """Generate a clean, attorney-ready invention summary."""
        system = (
            "You are a senior patent analyst at a top IP law firm. "
            "Write precise, neutral, attorney-ready technical summaries. "
            "No marketing language. No hedging. Factual and structured."
        )
        user = f"""Summarize this invention for inclusion in a patent disclosure report.
Write 2-3 sentences. Lead with the technical mechanism, not the benefit.

Invention title: {disclosure.invention_title}
Technical summary: {disclosure.technical_summary}
Claimed novelty: {disclosure.claimed_novelty}
Inventor notes: {disclosure.inventor_notes or 'None provided'}

Output only the summary paragraph. No headers, no preamble."""

        return self._call_claude(system, user, max_tokens=300)

    # Stage 3: Novelty assessment
    def stage_3_novelty(self, disclosure: DisclosureInput) -> NoveltyAssessment:
        """Score and assess the novelty of the claimed invention."""
        prior_art_text = "\n".join([
            f"- {r.title} ({r.source}): {r.relevance_notes}"
            for r in disclosure.prior_art_references
        ]) or "No prior art provided."

        system = (
            "You are a patent examiner with 15 years of experience at the USPTO. "
            "Assess novelty objectively. Return only valid JSON. No commentary outside JSON."
        )
        user = f"""Assess the novelty of this invention against the prior art references.

Invention: {disclosure.invention_title}
Claimed novelty: {disclosure.claimed_novelty}

Prior art references:
{prior_art_text}

Return a JSON object with exactly these fields:
{{
  "score": <integer 1-10>,
  "label": "<Strong | Moderate | Weak | Unclear>",
  "rationale": "<2-3 sentence assessment>"
}}"""

        raw = self._call_claude(system, user, max_tokens=400)

        # Parse JSON safely
        try:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            data = json.loads(match.group()) if match else {}
            return NoveltyAssessment(
                score=int(data.get("score", 5)),
                label=data.get("label", "Unclear"),
                rationale=data.get("rationale", raw)
            )
        except Exception:
            return NoveltyAssessment(score=5, label="Unclear", rationale=raw)

    # Stage 4: Claim mapping
    def stage_4_claim_mapping(self, disclosure: DisclosureInput) -> list[ClaimMapping]:
        """Map claimed elements against each prior art reference."""
        if not disclosure.prior_art_references:
            return []

        mappings = []
        system = (
            "You are a patent claims analyst. Compare inventions to prior art with precision. "
            "Return only valid JSON arrays. No commentary outside JSON."
        )

        for ref in disclosure.prior_art_references:
            user = f"""Compare this invention to the prior art reference. Identify what overlaps and what distinguishes.

Invention: {disclosure.invention_title}
Claimed novelty: {disclosure.claimed_novelty}
Technical summary: {disclosure.technical_summary}

Prior art reference: {ref.title} ({ref.source})
Relevance notes: {ref.relevance_notes}

Return JSON with exactly these fields:
{{
  "overlapping_elements": ["<element 1>", "<element 2>"],
  "distinguishing_elements": ["<element 1>", "<element 2>"],
  "risk_level": "<High | Medium | Low>"
}}"""

            raw = self._call_claude(system, user, max_tokens=500)
            try:
                match = re.search(r'\{.*\}', raw, re.DOTALL)
                data = json.loads(match.group()) if match else {}
                mappings.append(ClaimMapping(
                    prior_art_source=f"{ref.title} ({ref.source})",
                    overlapping_elements=data.get("overlapping_elements", []),
                    distinguishing_elements=data.get("distinguishing_elements", []),
                    risk_level=data.get("risk_level", "Medium")
                ))
            except Exception:
                mappings.append(ClaimMapping(
                    prior_art_source=f"{ref.title} ({ref.source})",
                    overlapping_elements=["Parse error — see raw output"],
                    distinguishing_elements=[],
                    risk_level="Unclear"
                ))

        return mappings

    # Stage 5: Final synthesis
    def stage_5_synthesize(
        self,
        disclosure: DisclosureInput,
        summary: str,
        novelty: NoveltyAssessment,
        mappings: list[ClaimMapping]
    ) -> tuple[str, str, str]:
        """Generate patentability outlook, claim focus recommendation, and attorney notes."""
        mapping_text = "\n".join([
            f"vs {m.prior_art_source}: overlaps={m.overlapping_elements}, "
            f"distinguishes={m.distinguishing_elements}, risk={m.risk_level}"
            for m in mappings
        ]) or "No prior art mapped."

        system = (
            "You are a senior IP attorney advising on patent prosecution strategy. "
            "Be direct, specific, and actionable. No boilerplate. "
            "Return only valid JSON."
        )
        user = f"""Based on this analysis, provide prosecution strategy guidance.

Invention: {disclosure.invention_title}
Novelty score: {novelty.score}/10 ({novelty.label})
Novelty rationale: {novelty.rationale}
Claim mappings: {mapping_text}

Return JSON with exactly these fields:
{{
  "patentability_outlook": "<1-2 sentence outlook>",
  "recommended_claim_focus": "<specific claim drafting recommendation>",
  "attorney_notes": "<flagged risks or considerations for prosecution>"
}}"""

        raw = self._call_claude(system, user, max_tokens=600)
        try:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            data = json.loads(match.group()) if match else {}
            return (
                data.get("patentability_outlook", "Assessment pending attorney review."),
                data.get("recommended_claim_focus", "See attorney notes."),
                data.get("attorney_notes", raw)
            )
        except Exception:
            return ("Assessment pending.", "See attorney notes.", raw)

    # ── Main run method ───────────────────────────────────────────────────────

    def run(self, disclosure: DisclosureInput) -> tuple[AnalysisReport, dict]:
        """Run all five pipeline stages and return the completed report + validation metadata."""
        print(f"\n{'='*60}")
        print(f"  LegalReport Pipeline")
        print(f"  Disclosure: {disclosure.invention_title}")
        print(f"{'='*60}")

        # Stage 1
        print("\n[Stage 1/5] Validating input...")
        validation = self.stage_1_validate(disclosure)
        for w in validation["warnings"]:
            print(f"  ⚠  {w}")

        # Stage 2
        print("[Stage 2/5] Generating invention summary...")
        summary = self.stage_2_summarize(disclosure)

        # Stage 3
        print("[Stage 3/5] Assessing novelty...")
        novelty = self.stage_3_novelty(disclosure)
        print(f"  → Novelty: {novelty.label} ({novelty.score}/10)")

        # Stage 4
        print(f"[Stage 4/5] Mapping claims against {len(disclosure.prior_art_references)} prior art reference(s)...")
        mappings = self.stage_4_claim_mapping(disclosure)

        # Stage 5
        print("[Stage 5/5] Synthesizing prosecution strategy...")
        outlook, claim_focus, attorney_notes = self.stage_5_synthesize(
            disclosure, summary, novelty, mappings
        )

        report = AnalysisReport(
            disclosure_title=disclosure.invention_title,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            invention_summary=summary,
            novelty_assessment=novelty,
            claim_mappings=mappings,
            patentability_outlook=outlook,
            recommended_claim_focus=claim_focus,
            attorney_notes=attorney_notes,
            raw_prior_art_count=len(disclosure.prior_art_references)
        )

        print("\n✓ Pipeline complete.\n")
        return report, validation
