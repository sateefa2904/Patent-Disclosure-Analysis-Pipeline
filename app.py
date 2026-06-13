"""
LegalReport — Web Interface
Run: python3 app.py
Then open http://localhost:5000
"""

import json
import os
import sys
import tempfile

from pathlib import Path

from flask import Flask, render_template_string, request, jsonify, send_file

sys.path.insert(0, str(Path(__file__).parent))

from core.pipeline import LegalReportPipeline, DisclosureInput, PriorArtReference
from core.formatter import to_markdown, to_json, to_html
from core.security import init_limiter, sanitize_disclosure
from core.legal_pages import render_terms, render_privacy
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))
limiter = init_limiter(app)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LegalReport — Patent Disclosure Analysis</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Georgia', serif; background: #f8f7f4; color: #1a1a1a; min-height: 100vh; }
    .topbar {
      background: #0f1923; color: white; padding: 1rem 2.5rem;
      display: flex; align-items: center; justify-content: space-between;
      border-bottom: 2px solid #c9a84c;
    }
    .topbar-left { display: flex; align-items: center; gap: 1rem; }
    .topbar-brand { font-family: 'Courier New', monospace; font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase; color: #c9a84c; }
    .topbar-title { font-size: 1rem; font-weight: 400; color: white; }
    .topbar-badge { font-family: 'Courier New', monospace; font-size: 0.65rem; padding: 0.2rem 0.6rem; background: #c9a84c20; color: #c9a84c; border: 1px solid #c9a84c40; border-radius: 3px; }
    .topbar-nav a { font-family: 'Courier New', monospace; font-size: 0.65rem; color: #9ca3af; text-decoration: none; margin-left: 1.25rem; letter-spacing: 0.08em; }
    .topbar-nav a:hover { color: #c9a84c; }
    .layout { display: grid; grid-template-columns: 420px 1fr; min-height: calc(100vh - 56px); }
    .sidebar { background: white; border-right: 1px solid #e5e7eb; padding: 2rem; overflow-y: auto; }
    .sidebar h2 { font-size: 0.75rem; font-family: 'Courier New', monospace; letter-spacing: 0.15em; text-transform: uppercase; color: #9ca3af; margin-bottom: 1.5rem; }
    .field { margin-bottom: 1.25rem; }
    .field label { display: block; font-size: 0.8rem; font-weight: 600; color: #374151; margin-bottom: 0.4rem; font-family: 'Courier New', monospace; }
    .field input, .field textarea { width: 100%; padding: 0.6rem 0.75rem; border: 1px solid #d1d5db; border-radius: 4px; font-family: 'Georgia', serif; font-size: 0.875rem; color: #1a1a1a; background: white; transition: border-color 0.15s; }
    .field input:focus, .field textarea:focus { outline: none; border-color: #0f1923; }
    .field textarea { resize: vertical; min-height: 80px; }
    .char-count { font-family: 'Courier New', monospace; font-size: 0.65rem; color: #9ca3af; text-align: right; margin-top: 0.25rem; }
    .prior-art-section { margin-top: 1.5rem; }
    .prior-art-section h3 { font-size: 0.75rem; font-family: 'Courier New', monospace; letter-spacing: 0.1em; text-transform: uppercase; color: #9ca3af; margin-bottom: 1rem; }
    .prior-art-entry { border: 1px solid #e5e7eb; border-radius: 4px; padding: 1rem; margin-bottom: 0.75rem; position: relative; }
    .remove-btn { position: absolute; top: 0.5rem; right: 0.5rem; background: none; border: none; color: #9ca3af; cursor: pointer; font-size: 1rem; }
    .remove-btn:hover { color: #ef4444; }
    .add-btn { width: 100%; padding: 0.6rem; background: white; border: 1px dashed #d1d5db; border-radius: 4px; color: #6b7280; font-family: 'Courier New', monospace; font-size: 0.75rem; cursor: pointer; transition: all 0.15s; }
    .add-btn:hover { border-color: #0f1923; color: #0f1923; }
    .run-btn { width: 100%; padding: 0.85rem; background: #0f1923; color: white; border: none; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 0.8rem; letter-spacing: 0.1em; text-transform: uppercase; cursor: pointer; margin-top: 1.5rem; transition: background 0.15s; }
    .run-btn:hover { background: #1a2d40; }
    .run-btn:disabled { background: #9ca3af; cursor: not-allowed; }
    .disclaimer-bar { font-family: 'Courier New', monospace; font-size: 0.65rem; color: #9ca3af; text-align: center; padding: 0.75rem 1rem; border-top: 1px solid #e5e7eb; margin-top: 1.5rem; line-height: 1.6; }
    .disclaimer-bar a { color: #9ca3af; }
    .disclaimer-bar a:hover { color: #0f1923; }
    .main { padding: 2rem 2.5rem; overflow-y: auto; }
    .main h2 { font-size: 0.75rem; font-family: 'Courier New', monospace; letter-spacing: 0.15em; text-transform: uppercase; color: #9ca3af; margin-bottom: 1.5rem; }
    .empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 400px; color: #9ca3af; text-align: center; }
    .empty-icon { font-size: 2.5rem; margin-bottom: 1rem; opacity: 0.4; }
    .empty-state p { font-family: 'Courier New', monospace; font-size: 0.75rem; letter-spacing: 0.1em; }
    .loading { display: none; flex-direction: column; align-items: center; justify-content: center; height: 400px; color: #6b7280; text-align: center; }
    .spinner { width: 32px; height: 32px; border: 2px solid #e5e7eb; border-top-color: #0f1923; border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 1rem; }
    @keyframes spin { to { transform: rotate(360deg); } }
    .loading p { font-family: 'Courier New', monospace; font-size: 0.75rem; }
    .stage-log { font-family: 'Courier New', monospace; font-size: 0.7rem; color: #9ca3af; margin-top: 0.5rem; }
    .report-output { display: none; }
    .report-header { background: #0f1923; color: white; padding: 1.5rem 2rem; border-radius: 4px 4px 0 0; }
    .report-eyebrow { font-family: 'Courier New', monospace; font-size: 0.65rem; letter-spacing: 0.2em; color: #c9a84c; margin-bottom: 0.35rem; }
    .report-title { font-size: 1.1rem; font-weight: 400; }
    .report-meta { font-family: 'Courier New', monospace; font-size: 0.7rem; color: #9ca3af; margin-top: 0.35rem; }
    .report-section { background: white; border: 1px solid #e5e7eb; border-top: none; padding: 1.5rem 2rem; }
    .report-section:last-of-type { border-radius: 0 0 4px 4px; }
    .section-eyebrow { font-family: 'Courier New', monospace; font-size: 0.65rem; letter-spacing: 0.18em; text-transform: uppercase; color: #9ca3af; margin-bottom: 0.75rem; }
    .novelty-row { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem; }
    .badge { font-family: 'Courier New', monospace; font-size: 0.75rem; font-weight: 700; padding: 0.3rem 0.75rem; border-radius: 3px; }
    .score-label { font-family: 'Courier New', monospace; font-size: 0.75rem; color: #6b7280; }
    .mapping-card { border: 1px solid #e5e7eb; border-radius: 4px; padding: 1rem 1.25rem; margin-bottom: 0.75rem; }
    .mapping-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
    .mapping-source { font-size: 0.85rem; font-weight: 600; color: #0f1923; }
    .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
    .col-label { font-family: 'Courier New', monospace; font-size: 0.65rem; letter-spacing: 0.1em; text-transform: uppercase; color: #9ca3af; margin-bottom: 0.4rem; }
    ul { padding-left: 1.25rem; }
    li { font-size: 0.875rem; color: #374151; margin-bottom: 0.3rem; }
    .body-text { font-size: 0.925rem; color: #374151; line-height: 1.7; }
    .export-bar { display: flex; gap: 0.75rem; margin-top: 1.5rem; }
    .export-btn { padding: 0.5rem 1rem; border: 1px solid #e5e7eb; border-radius: 4px; background: white; font-family: 'Courier New', monospace; font-size: 0.7rem; letter-spacing: 0.08em; cursor: pointer; color: #374151; transition: all 0.15s; }
    .export-btn:hover { border-color: #0f1923; color: #0f1923; }
    .report-disclaimer { font-family: 'Courier New', monospace; font-size: 0.65rem; color: #9ca3af; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e5e7eb; line-height: 1.6; }
    .report-disclaimer a { color: #9ca3af; }
    .error-banner { background: #fef2f2; border: 1px solid #fecaca; border-radius: 4px; padding: 1rem 1.25rem; margin-bottom: 1rem; font-family: 'Courier New', monospace; font-size: 0.75rem; color: #dc2626; display: none; }
  </style>
</head>
<body>
  <div class="topbar">
    <div class="topbar-left">
      <div>
        <div class="topbar-brand">LegalReport</div>
        <div class="topbar-title">Patent Disclosure Analysis Pipeline</div>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:1rem;">
      <nav class="topbar-nav">
        <a href="/terms">Terms of Use</a>
        <a href="/privacy">Privacy Notice</a>
      </nav>
      <span class="topbar-badge">v1.0.0</span>
    </div>
  </div>

  <div class="layout">
    <div class="sidebar">
      <h2>Disclosure Input</h2>

      <div class="field">
        <label>Invention Title *</label>
        <input type="text" id="invention_title" maxlength="200"
          placeholder="e.g. Adaptive Document Routing System"
          oninput="updateChar(this, 'tc-title', 200)">
        <div class="char-count" id="tc-title">0 / 200</div>
      </div>

      <div class="field">
        <label>Technical Summary *</label>
        <textarea id="technical_summary" rows="4" maxlength="5000"
          placeholder="Describe the technical mechanism of the invention..."
          oninput="updateChar(this, 'tc-summary', 5000)"></textarea>
        <div class="char-count" id="tc-summary">0 / 5000</div>
      </div>

      <div class="field">
        <label>Claimed Novelty</label>
        <textarea id="claimed_novelty" rows="3" maxlength="5000"
          placeholder="What is new and non-obvious about this invention?"
          oninput="updateChar(this, 'tc-novelty', 5000)"></textarea>
        <div class="char-count" id="tc-novelty">0 / 5000</div>
      </div>

      <div class="field">
        <label>Inventor Notes <span style="color:#9ca3af;font-weight:400">(optional)</span></label>
        <textarea id="inventor_notes" rows="2" maxlength="5000"
          placeholder="Any additional context from the inventor..."
          oninput="updateChar(this, 'tc-notes', 5000)"></textarea>
        <div class="char-count" id="tc-notes">0 / 5000</div>
      </div>

      <div class="prior-art-section">
        <h3>Prior Art References <span style="font-weight:400">(max 10)</span></h3>
        <div id="prior-art-container"></div>
        <button class="add-btn" onclick="addPriorArt()">+ Add Prior Art Reference</button>
      </div>

      <button class="run-btn" id="run-btn" onclick="runPipeline()">
        Run Analysis Pipeline
      </button>

      <div class="disclaimer-bar">
        Not legal advice. All outputs require attorney review.<br>
        <a href="/terms">Terms of Use</a> &nbsp;·&nbsp; <a href="/privacy">Privacy Notice</a>
      </div>
    </div>

    <div class="main">
      <h2>Analysis Output</h2>

      <div class="error-banner" id="error-banner"></div>

      <div class="empty-state" id="empty-state">
        <div class="empty-icon">⚖</div>
        <p>Fill in the disclosure details and run<br>the pipeline to generate a report.</p>
      </div>

      <div class="loading" id="loading">
        <div class="spinner"></div>
        <p>Running analysis pipeline...</p>
        <div class="stage-log" id="stage-log"></div>
      </div>

      <div class="report-output" id="report-output"></div>
    </div>
  </div>

  <script>
    let priorArtCount = 0;

    function updateChar(el, counterId, max) {
      document.getElementById(counterId).textContent = el.value.length + ' / ' + max;
    }

    function addPriorArt() {
      const entries = document.querySelectorAll('.prior-art-entry');
      if (entries.length >= 10) { alert('Maximum 10 prior art references allowed.'); return; }
      priorArtCount++;
      const id = priorArtCount;
      const container = document.getElementById('prior-art-container');
      const div = document.createElement('div');
      div.className = 'prior-art-entry';
      div.id = 'pa-' + id;
      div.innerHTML = `
        <button class="remove-btn" onclick="removePriorArt(${id})">×</button>
        <div class="field"><label>Title</label>
          <input type="text" id="pa-title-${id}" maxlength="200" placeholder="Reference title"></div>
        <div class="field"><label>Source</label>
          <input type="text" id="pa-source-${id}" maxlength="200" placeholder="e.g. US Patent 10,891,423"></div>
        <div class="field"><label>Relevance Notes</label>
          <textarea id="pa-notes-${id}" rows="2" maxlength="5000"
            placeholder="How does this reference relate to the invention?"></textarea></div>`;
      container.appendChild(div);
    }

    function removePriorArt(id) { document.getElementById('pa-' + id).remove(); }

    function collectPriorArt() {
      const refs = [];
      document.querySelectorAll('.prior-art-entry').forEach(entry => {
        const id = entry.id.replace('pa-', '');
        const title = document.getElementById('pa-title-' + id)?.value || '';
        const source = document.getElementById('pa-source-' + id)?.value || '';
        const notes = document.getElementById('pa-notes-' + id)?.value || '';
        if (title) refs.push({ title, source, relevance_notes: notes });
      });
      return refs;
    }

    function showError(msg) {
      const banner = document.getElementById('error-banner');
      banner.textContent = '⚠ ' + msg;
      banner.style.display = 'block';
    }
    function hideError() { document.getElementById('error-banner').style.display = 'none'; }

    const stages = [
      'Stage 1/5 — Validating input...',
      'Stage 2/5 — Generating invention summary...',
      'Stage 3/5 — Assessing novelty...',
      'Stage 4/5 — Mapping claims against prior art...',
      'Stage 5/5 — Synthesizing prosecution strategy...'
    ];

    function animateStages() {
      let i = 0;
      const log = document.getElementById('stage-log');
      const interval = setInterval(() => {
        if (i < stages.length) log.textContent = stages[i++];
        else clearInterval(interval);
      }, 1800);
    }

    async function runPipeline() {
      hideError();
      const payload = {
        invention_title: document.getElementById('invention_title').value.trim(),
        technical_summary: document.getElementById('technical_summary').value.trim(),
        claimed_novelty: document.getElementById('claimed_novelty').value.trim(),
        inventor_notes: document.getElementById('inventor_notes').value.trim(),
        prior_art_references: collectPriorArt()
      };

      if (!payload.invention_title) { showError('Invention title is required.'); return; }
      if (!payload.technical_summary || payload.technical_summary.length < 50) {
        showError('Technical summary must be at least 50 characters.'); return;
      }

      document.getElementById('empty-state').style.display = 'none';
      document.getElementById('report-output').style.display = 'none';
      document.getElementById('loading').style.display = 'flex';
      document.getElementById('run-btn').disabled = true;
      animateStages();

      try {
        const res = await fetch('/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        document.getElementById('loading').style.display = 'none';
        document.getElementById('run-btn').disabled = false;

        if (data.error) { showError(data.error); document.getElementById('empty-state').style.display = 'flex'; return; }
        if (data.validation_errors && data.validation_errors.length) {
          showError(data.validation_errors.join(' · '));
        }
        renderReport(data.report);
      } catch (err) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('run-btn').disabled = false;
        document.getElementById('empty-state').style.display = 'flex';
        showError('Pipeline error: ' + err.message);
      }
    }

    function nc(label) { return { Strong:'#22c55e', Moderate:'#f59e0b', Weak:'#ef4444', Unclear:'#9ca3af' }[label] || '#9ca3af'; }
    function rc(r) { return { High:'#ef4444', Medium:'#f59e0b', Low:'#22c55e', Unclear:'#9ca3af' }[r] || '#9ca3af'; }

    function renderReport(report) {
      const n = nc(report.novelty_assessment.label);
      let mappingsHtml = '';
      (report.claim_mappings || []).forEach(m => {
        const c = rc(m.risk_level);
        const ov = (m.overlapping_elements||[]).map(e=>`<li>${e}</li>`).join('');
        const di = (m.distinguishing_elements||[]).map(e=>`<li>${e}</li>`).join('');
        mappingsHtml += `<div class="mapping-card">
          <div class="mapping-header">
            <span class="mapping-source">${m.prior_art_source}</span>
            <span class="badge" style="background:${c}20;color:${c};border:1px solid ${c}40">${m.risk_level} Risk</span>
          </div>
          <div class="two-col">
            <div><div class="col-label">Overlapping</div><ul>${ov||'<li>None identified</li>'}</ul></div>
            <div><div class="col-label">Distinguishing</div><ul>${di||'<li>None identified</li>'}</ul></div>
          </div></div>`;
      });

      document.getElementById('report-output').innerHTML = `
        <div class="report-header">
          <div class="report-eyebrow">Patent Disclosure Analysis Report</div>
          <div class="report-title">${report.disclosure_title}</div>
          <div class="report-meta">Generated ${report.generated_at} &nbsp;·&nbsp; ${report.raw_prior_art_count} prior art reference(s) analyzed</div>
        </div>
        <div class="report-section">
          <div class="section-eyebrow">Invention Summary</div>
          <p class="body-text">${report.invention_summary}</p>
        </div>
        <div class="report-section">
          <div class="section-eyebrow">Novelty Assessment</div>
          <div class="novelty-row">
            <span class="badge" style="background:${n}20;color:${n};border:1px solid ${n}40">${report.novelty_assessment.label}</span>
            <span class="score-label">${report.novelty_assessment.score} / 10</span>
          </div>
          <p class="body-text">${report.novelty_assessment.rationale}</p>
        </div>
        ${mappingsHtml ? `<div class="report-section"><div class="section-eyebrow">Prior Art Claim Mapping</div>${mappingsHtml}</div>` : ''}
        <div class="report-section">
          <div class="section-eyebrow">Patentability Outlook</div>
          <p class="body-text">${report.patentability_outlook}</p>
        </div>
        <div class="report-section">
          <div class="section-eyebrow">Recommended Claim Focus</div>
          <p class="body-text">${report.recommended_claim_focus}</p>
        </div>
        <div class="report-section">
          <div class="section-eyebrow">Attorney Notes</div>
          <p class="body-text">${report.attorney_notes}</p>
          <div class="export-bar">
            <button class="export-btn" onclick="downloadMarkdown()">↓ Markdown</button>
            <button class="export-btn" onclick="downloadJSON()">↓ JSON</button>
          </div>
          <div class="report-disclaimer">
            This report was generated by LegalReport Pipeline v1.0.0 and does not constitute legal advice.
            Review by a licensed patent attorney is required before reliance in prosecution or any legal matter.
            &nbsp;·&nbsp; <a href="/terms">Terms of Use</a> &nbsp;·&nbsp; <a href="/privacy">Privacy Notice</a>
          </div>
        </div>`;

      document.getElementById('report-output').style.display = 'block';
      window._currentReport = report;
    }

    function downloadMarkdown() {
      fetch('/export/markdown', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(window._currentReport)
      }).then(r=>r.blob()).then(blob=>{
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'legal_report.md'; a.click();
      });
    }

    function downloadJSON() {
      const blob = new Blob([JSON.stringify(window._currentReport,null,2)],{type:'application/json'});
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'legal_report.json'; a.click();
    }
  </script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/terms")
def terms():
    return render_terms()


@app.route("/privacy")
def privacy():
    return render_privacy()


@app.route("/analyze", methods=["POST"])
@limiter.limit("10 per minute")
def analyze():
    try:
        raw = request.get_json(force=True)
        if not raw:
            return jsonify({"error": "Invalid request body."}), 400

        data, errors = sanitize_disclosure(raw)
        if errors and any("required" in e.lower() for e in errors):
            return jsonify({"error": errors[0], "validation_errors": errors}), 400

        prior_art = [
            PriorArtReference(
                title=r["title"],
                source=r.get("source", ""),
                relevance_notes=r.get("relevance_notes", "")
            )
            for r in data.get("prior_art_references", [])
        ]

        disclosure = DisclosureInput(
            invention_title=data["invention_title"],
            technical_summary=data["technical_summary"],
            claimed_novelty=data.get("claimed_novelty", ""),
            prior_art_references=prior_art,
            inventor_notes=data.get("inventor_notes")
        )

        pipeline = LegalReportPipeline()
        report, validation = pipeline.run(disclosure)

        report_dict = {
            "disclosure_title": report.disclosure_title,
            "generated_at": report.generated_at,
            "invention_summary": report.invention_summary,
            "novelty_assessment": {
                "score": report.novelty_assessment.score,
                "label": report.novelty_assessment.label,
                "rationale": report.novelty_assessment.rationale
            },
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
            "raw_prior_art_count": report.raw_prior_art_count
        }

        return jsonify({
            "report": report_dict,
            "validation": validation,
            "validation_errors": errors
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/export/markdown", methods=["POST"])
@limiter.limit("20 per minute")
def export_markdown():
    data = request.get_json()
    report = _dict_to_report(data)
    content = to_markdown(report)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        return send_file(f.name, as_attachment=True, download_name='legal_report.md')


@app.route("/export/html", methods=["POST"])
@limiter.limit("20 per minute")
def export_html():
    data = request.get_json()
    report = _dict_to_report(data)
    content = to_html(report)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(content)
        return send_file(f.name, as_attachment=True, download_name='legal_report.html')


def _dict_to_report(data):
    from core.pipeline import AnalysisReport, NoveltyAssessment, ClaimMapping
    return AnalysisReport(
        disclosure_title=data["disclosure_title"],
        generated_at=data["generated_at"],
        invention_summary=data["invention_summary"],
        novelty_assessment=NoveltyAssessment(
            score=data["novelty_assessment"]["score"],
            label=data["novelty_assessment"]["label"],
            rationale=data["novelty_assessment"]["rationale"]
        ),
        claim_mappings=[
            ClaimMapping(
                prior_art_source=m["prior_art_source"],
                overlapping_elements=m["overlapping_elements"],
                distinguishing_elements=m["distinguishing_elements"],
                risk_level=m["risk_level"]
            )
            for m in data.get("claim_mappings", [])
        ],
        patentability_outlook=data["patentability_outlook"],
        recommended_claim_focus=data["recommended_claim_focus"],
        attorney_notes=data["attorney_notes"],
        raw_prior_art_count=data["raw_prior_art_count"]
    )


if __name__ == "__main__":
    print("\nLegalReport Web Interface")
    print("Open http://localhost:5000\n")
    app.run(debug=True, port=5000)
