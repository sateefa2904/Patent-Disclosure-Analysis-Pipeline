# LegalReport — Patent Disclosure Analysis Pipeline

A five-stage AI-powered pipeline that processes patent disclosures and generates structured, attorney-ready analysis reports. Built with Claude (Anthropic) as the LLM foundation.

## What it does

Takes a patent disclosure as input — invention summary, claimed novelty, and prior art references — and runs it through five sequential analysis stages:

1. **Input validation** — flags missing or insufficient data before analysis begins
2. **Invention summarization** — generates a clean, neutral, attorney-ready technical summary
3. **Novelty assessment** — scores novelty 1–10 against provided prior art with rationale
4. **Claim mapping** — compares claimed elements against each prior art reference, identifying overlaps, distinguishing features, and risk level
5. **Prosecution strategy synthesis** — produces patentability outlook, claim drafting recommendations, and attorney notes

Output is available as **Markdown**, **JSON**, or a standalone **HTML report**.

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt

# Set your Anthropic API key
export ANTHROPIC_API_KEY=your_key_here

# Run the web interface
python app.py
# Open http://localhost:5000

# Or use the CLI
python cli.py --input sample_inputs/example.json --format html --output outputs/report.html
```

## Project structure

```
legalreport/
├── core/
│   ├── pipeline.py      # Five-stage analysis engine
│   └── formatter.py     # Markdown / JSON / HTML output
├── sample_inputs/
│   └── example.json     # Example patent disclosure
├── outputs/             # Generated reports saved here
├── app.py               # Flask web interface
├── cli.py               # Command-line interface
└── requirements.txt
```

## Input format

```json
{
  "invention_title": "Your invention title",
  "technical_summary": "Detailed technical description...",
  "claimed_novelty": "What is new and non-obvious...",
  "inventor_notes": "Optional additional context",
  "prior_art_references": [
    {
      "title": "Reference title",
      "source": "US Patent 10,000,000 or paper citation",
      "relevance_notes": "How this reference relates to the invention"
    }
  ]
}
```

## Why this exists

Prior art analysis in patent prosecution is time-intensive and error-prone when done manually. This pipeline applies structured prompt engineering across a multi-stage Claude workflow to produce consistent, auditable analysis outputs — reducing the time between disclosure intake and attorney review.

Built as a companion to real patent prosecution workflow experience at an IP law firm.

## Tech stack

- **LLM:** Claude (Anthropic) via `anthropic` Python SDK
- **Web:** Flask + vanilla JS
- **CLI:** argparse
- **Output:** Markdown, JSON, HTML
# LegalReporting
