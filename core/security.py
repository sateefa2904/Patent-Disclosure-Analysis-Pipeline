"""
LegalReport — Security Layer
CORS, rate limiting, input sanitization, request validation,
and security headers.
"""

import os
import bleach
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS


# ── Field limits ──────────────────────────────────────────────────────────────
ALLOWED_TAGS = []
ALLOWED_ATTRIBUTES = {}
MAX_FIELD_LENGTH = 5000
MAX_TITLE_LENGTH = 200
MAX_PRIOR_ART_REFS = 10


# ── CORS configuration ────────────────────────────────────────────────────────
# In development: allow localhost. In production: lock to your domain.
# Set ALLOWED_ORIGINS in your .env to restrict to your deployed domain.
# Example: ALLOWED_ORIGINS=https://legalreport.yourdomain.com
def get_allowed_origins():
    origins_env = os.environ.get("ALLOWED_ORIGINS", "")
    if origins_env:
        return [o.strip() for o in origins_env.split(",")]
    # Default: allow localhost only in development
    return [
        "http://localhost:5000",
        "http://127.0.0.1:5000",
    ]


def init_cors(app):
    """
    Initialize CORS — controls which domains can call this API.
    Prevents other websites from using your Anthropic API key.
    """
    CORS(
        app,
        resources={
            r"/analyze": {"origins": get_allowed_origins()},
            r"/export/*": {"origins": get_allowed_origins()},
        },
        methods=["POST", "OPTIONS"],
        allow_headers=["Content-Type"],
        max_age=3600
    )


def init_limiter(app):
    """Initialize rate limiter — prevents API abuse and runaway bills."""
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
    )
    return limiter


def add_security_headers(response):
    """
    Add security headers to every response.
    These protect against common web attacks.
    """
    # Prevent browsers from MIME-sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    # XSS protection for older browsers
    response.headers["X-XSS-Protection"] = "1; mode=block"
    # Don't send referrer to external sites
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Content Security Policy — only load resources from our own domain
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self';"
    )
    # Remove server fingerprint
    response.headers.pop("Server", None)
    return response


def sanitize_string(value: str, max_length: int = MAX_FIELD_LENGTH) -> str:
    """Strip HTML, dangerous characters, and enforce length limits."""
    if not isinstance(value, str):
        return ""
    clean = bleach.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
    clean = clean.replace("\x00", "").strip()
    return clean[:max_length]


def sanitize_disclosure(data: dict) -> tuple[dict, list[str]]:
    """
    Sanitize all fields in a disclosure payload.
    Returns (sanitized_data, list_of_errors).
    """
    errors = []

    invention_title = sanitize_string(
        data.get("invention_title", ""), MAX_TITLE_LENGTH
    )
    technical_summary = sanitize_string(data.get("technical_summary", ""))
    claimed_novelty = sanitize_string(data.get("claimed_novelty", ""))
    inventor_notes = sanitize_string(data.get("inventor_notes", ""))

    if not invention_title:
        errors.append("Invention title is required.")
    if not technical_summary or len(technical_summary) < 50:
        errors.append("Technical summary must be at least 50 characters.")

    raw_refs = data.get("prior_art_references", [])
    if not isinstance(raw_refs, list):
        errors.append("Prior art references must be a list.")
        raw_refs = []

    if len(raw_refs) > MAX_PRIOR_ART_REFS:
        errors.append(f"Maximum {MAX_PRIOR_ART_REFS} prior art references allowed.")
        raw_refs = raw_refs[:MAX_PRIOR_ART_REFS]

    clean_refs = []
    for ref in raw_refs:
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
