"""
LegalReport — Legal Pages
Terms of Use and Privacy Notice templates.
"""

SHARED_STYLES = """
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Georgia', serif;
    background: #f8f7f4;
    color: #1a1a1a;
    line-height: 1.8;
  }
  .topbar {
    background: #0f1923;
    color: white;
    padding: 1rem 2.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 2px solid #c9a84c;
  }
  .topbar-brand {
    font-family: 'Courier New', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #c9a84c;
  }
  .topbar-title { font-size: 1rem; font-weight: 400; color: white; }
  .topbar-nav a {
    font-family: 'Courier New', monospace;
    font-size: 0.7rem;
    color: #9ca3af;
    text-decoration: none;
    margin-left: 1.5rem;
    letter-spacing: 0.08em;
  }
  .topbar-nav a:hover { color: #c9a84c; }
  .container {
    max-width: 760px;
    margin: 3rem auto;
    padding: 0 2rem 4rem;
  }
  .page-eyebrow {
    font-family: 'Courier New', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #c9a84c;
    margin-bottom: 0.5rem;
  }
  h1 {
    font-size: 1.75rem;
    font-weight: 400;
    color: #0f1923;
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
  }
  .effective-date {
    font-family: 'Courier New', monospace;
    font-size: 0.7rem;
    color: #9ca3af;
    margin-bottom: 2.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #e5e7eb;
  }
  h2 {
    font-size: 1rem;
    font-weight: 600;
    color: #0f1923;
    margin: 2rem 0 0.75rem;
    letter-spacing: -0.01em;
  }
  p { font-size: 0.925rem; color: #374151; margin-bottom: 1rem; }
  ul { padding-left: 1.5rem; margin-bottom: 1rem; }
  li { font-size: 0.925rem; color: #374151; margin-bottom: 0.4rem; }
  .highlight-box {
    background: #fff8e6;
    border: 1px solid #c9a84c40;
    border-left: 3px solid #c9a84c;
    border-radius: 0 4px 4px 0;
    padding: 1rem 1.25rem;
    margin: 1.5rem 0;
    font-size: 0.9rem;
    color: #374151;
  }
  .contact-box {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 4px;
    padding: 1.25rem 1.5rem;
    margin-top: 2.5rem;
  }
  .contact-box p { margin: 0; font-size: 0.875rem; }
  a { color: #0f1923; }
  a:hover { color: #c9a84c; }
"""


TERMS_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Terms of Use — LegalReport</title>
  <style>{styles}</style>
</head>
<body>
  <div class="topbar">
    <div>
      <div class="topbar-brand">LegalReport</div>
      <div class="topbar-title">Patent Disclosure Analysis Pipeline</div>
    </div>
    <nav class="topbar-nav">
      <a href="/">← Back to App</a>
      <a href="/privacy">Privacy Notice</a>
    </nav>
  </div>

  <div class="container">
    <div class="page-eyebrow">Legal</div>
    <h1>Terms of Use</h1>
    <div class="effective-date">Effective date: June 2026 &nbsp;·&nbsp; Version 1.0</div>

    <div class="highlight-box">
      <strong>Important:</strong> LegalReport is a research and productivity tool.
      It does not provide legal advice. All outputs must be reviewed by a licensed
      patent attorney before reliance in any legal proceeding or prosecution.
    </div>

    <h2>1. Acceptance of Terms</h2>
    <p>
      By accessing or using LegalReport ("the Tool"), you agree to be bound by
      these Terms of Use. If you do not agree, do not use the Tool.
    </p>

    <h2>2. Not Legal Advice</h2>
    <p>
      LegalReport generates automated analysis of patent disclosures using
      artificial intelligence. The outputs produced by this Tool — including
      novelty assessments, claim mappings, patentability outlooks, and attorney
      notes — are <strong>not legal advice</strong> and do not constitute the
      practice of law.
    </p>
    <p>
      No attorney-client relationship is created by your use of this Tool.
      All analysis must be independently reviewed and verified by a licensed
      patent attorney before use in prosecution, litigation, or any legal matter.
    </p>

    <h2>3. Permitted Use</h2>
    <p>You may use LegalReport for:</p>
    <ul>
      <li>Internal research and productivity purposes</li>
      <li>Preliminary analysis of patent disclosures prior to attorney review</li>
      <li>Educational and demonstration purposes</li>
    </ul>
    <p>You may not use LegalReport to:</p>
    <ul>
      <li>Substitute for qualified legal counsel</li>
      <li>Process confidential client information without appropriate safeguards</li>
      <li>Circumvent any applicable laws or regulations</li>
      <li>Reverse engineer, scrape, or systematically extract data from the Tool</li>
    </ul>

    <h2>4. Accuracy and Limitations</h2>
    <p>
      LegalReport uses large language models (LLMs) to generate analysis.
      LLMs can produce inaccurate, incomplete, or misleading outputs. The Tool
      makes no warranty, express or implied, regarding the accuracy, completeness,
      or fitness for purpose of any generated report.
    </p>
    <p>
      You assume full responsibility for evaluating the accuracy of any output
      before relying on it for any purpose.
    </p>

    <h2>5. Intellectual Property</h2>
    <p>
      You retain all rights to the disclosure information you submit. LegalReport
      does not claim ownership of your input data or the reports generated from it.
    </p>

    <h2>6. Confidentiality Warning</h2>
    <p>
      Do not submit confidential attorney-client privileged information, trade
      secrets, or sensitive client data through this Tool unless you have
      implemented appropriate technical and legal safeguards. This Tool is
      provided as-is without enterprise security guarantees.
    </p>

    <h2>7. Limitation of Liability</h2>
    <p>
      To the fullest extent permitted by law, LegalReport and its developers
      shall not be liable for any direct, indirect, incidental, or consequential
      damages arising from your use of this Tool or reliance on its outputs.
    </p>

    <h2>8. Changes to Terms</h2>
    <p>
      These Terms may be updated at any time. Continued use of the Tool
      following any update constitutes acceptance of the revised Terms.
    </p>

    <div class="contact-box">
      <p><strong>Questions?</strong> Contact the development team at
      <a href="mailto:sateefa2904@gmail.com">sateefa2904@gmail.com</a></p>
    </div>
  </div>
</body>
</html>"""


PRIVACY_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Privacy Notice — LegalReport</title>
  <style>{styles}</style>
</head>
<body>
  <div class="topbar">
    <div>
      <div class="topbar-brand">LegalReport</div>
      <div class="topbar-title">Patent Disclosure Analysis Pipeline</div>
    </div>
    <nav class="topbar-nav">
      <a href="/">← Back to App</a>
      <a href="/terms">Terms of Use</a>
    </nav>
  </div>

  <div class="container">
    <div class="page-eyebrow">Legal</div>
    <h1>Privacy Notice</h1>
    <div class="effective-date">Effective date: June 2026 &nbsp;·&nbsp; Version 1.0</div>

    <div class="highlight-box">
      <strong>Summary:</strong> LegalReport does not store, log, or share your
      disclosure data. Input is processed in memory and discarded after your
      session. Reports exist only in your browser until you download them.
    </div>

    <h2>1. What We Collect</h2>
    <p>
      When you use LegalReport, you submit patent disclosure information including
      invention titles, technical summaries, claimed novelty, and prior art
      references. This information is:
    </p>
    <ul>
      <li>Transmitted to Anthropic's API for AI-powered analysis</li>
      <li>Processed in server memory during your session</li>
      <li>Never written to a database or persistent storage</li>
      <li>Never logged to disk in identifiable form</li>
      <li>Discarded when your session ends</li>
    </ul>

    <h2>2. Third-Party AI Processing</h2>
    <p>
      LegalReport uses the Anthropic Claude API to generate analysis. When you
      submit a disclosure, the content is transmitted to Anthropic's servers
      for processing. Your use of this Tool is therefore also subject to
      <a href="https://www.anthropic.com/privacy" target="_blank">
      Anthropic's Privacy Policy</a>.
    </p>
    <p>
      We strongly recommend reviewing Anthropic's data handling practices before
      submitting confidential or privileged information through this Tool.
    </p>

    <h2>3. What We Do Not Collect</h2>
    <ul>
      <li>We do not create user accounts or collect personal information</li>
      <li>We do not use cookies for tracking or analytics</li>
      <li>We do not sell, share, or monetize your data</li>
      <li>We do not retain reports after your session ends</li>
      <li>We do not use your input to train AI models</li>
    </ul>

    <h2>4. Data Security</h2>
    <p>
      All API communication is encrypted in transit via HTTPS. The Anthropic
      API key used to power this Tool is stored as a server-side environment
      variable and is never exposed to the browser or client side.
    </p>
    <p>
      This Tool is provided for research and productivity purposes. It has not
      undergone a formal security audit. Do not process highly sensitive,
      classified, or privileged information without appropriate independent
      security review.
    </p>

    <h2>5. Your Reports</h2>
    <p>
      Generated reports exist only in your browser session. When you download
      a report (Markdown, JSON, or HTML), it is saved to your local device.
      We have no access to downloaded reports and retain no copy of them.
    </p>

    <h2>6. Children's Privacy</h2>
    <p>
      This Tool is intended for professional use and is not directed at
      individuals under the age of 18.
    </p>

    <h2>7. Changes to This Notice</h2>
    <p>
      This Privacy Notice may be updated periodically. The effective date
      at the top of this page reflects the most recent revision.
    </p>

    <div class="contact-box">
      <p><strong>Privacy questions?</strong> Contact
      <a href="mailto:sateefa2904@gmail.com">sateefa2904@gmail.com</a></p>
    </div>
  </div>
</body>
</html>"""


def render_terms():
    return TERMS_PAGE.replace("{styles}", SHARED_STYLES)


def render_privacy():
    return PRIVACY_PAGE.replace("{styles}", SHARED_STYLES)
