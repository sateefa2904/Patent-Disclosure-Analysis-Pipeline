"""
LegalReport — Security Layer
Rate limiting, input sanitization, and request validation.
"""

import bleach
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# ── Allowed HTML tags (none — we strip everything) ───────────────────────────
ALLOWED_TAGS = []
ALLOWED_ATTRIBUTES = {}
MAX_FIELD_LENGTH = 5000
MAX_TITLE_LENGTH = 200
MAX_PRIOR_ART_REFS = 10


def init_limiter(app):
    """Initialize rate limiter on the Flask app."""
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
    )
    return limiter


def sanitize_string(value: str, max_length: int = MAX_FIELD_LENGTH) -> str:
    """Strip HTML tags, dangerous characters, and enforce length limits."""
    if not isinstance(value, str):
        return ""
    # Strip all HTML
    clean = bleach.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
    # Strip null bytes and control characters
    clean = clean.replace("\x00", "").strip()
    # Enforce length
    return clean[:max_length]


def sanitize_disclosure(data: dict) -> tuple[dict, list[str]]:
    """
    Sanitize all fields in a disclosure payload.
    Returns (sanitized_data, list_of_errors).
    """
    errors = []

    # Required fields
    invention_title = sanitize_string(data.get("invention_title", ""), MAX_TITLE_LENGTH)
    technical_summary = sanitize_string(data.get("technical_summary", ""))
    claimed_novelty = sanitize_string(data.get("claimed_novelty", ""))
    inventor_notes = sanitize_string(data.get("inventor_notes", ""))

    if not invention_title:
        errors.append("Invention title is required.")
    if not technical_summary or len(technical_summary) < 50:
        errors.append("Technical summary must be at least 50 characters.")

    # Prior art references
    raw_refs = data.get("prior_art_references", [])
    if not isinstance(raw_refs, list):
        errors.append("Prior art references must be a list.")
        raw_refs = []

    if len(raw_refs) > MAX_PRIOR_ART_REFS:
        errors.append(f"Maximum {MAX_PRIOR_ART_REFS} prior art references allowed.")
        raw_refs = raw_refs[:MAX_PRIOR_ART_REFS]

    clean_refs = []
    for i, ref in enumerate(raw_refs):
        if not isinstance(ref, dict):
            continue
        clean_ref = {
            "title": sanitize_string(ref.get("title", ""), MAX_TITLE_LENGTH),
            "source": sanitize_string(ref.get("source", ""), MAX_TITLE_LENGTH),
            "relevance_notes": sanitize_string(ref.get("relevance_notes", ""))
        }
        if clean_ref["title"]:
            clean_refs.append(clean_ref)

    return {
        "invention_title": invention_title,
        "technical_summary": technical_summary,
        "claimed_novelty": claimed_novelty,
        "inventor_notes": inventor_notes,
        "prior_art_references": clean_refs
    }, errors
