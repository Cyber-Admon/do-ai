import re
from pathlib import Path

BLOCKLIST_PATH = Path(__file__).parent / "blocklist.txt"

REQUEST_PATTERNS = [
    r"\bcan you\b",
    r"\bcould you\b",
    r"\bwould you\b",
    r"\bplease\b",
    r"\bpls\b",
    r"\bkindly\b",
    r"\babeg\b",
    r"\bneed you to\b",
    r"\bi need\b",
    r"\bmake sure\b",
    r"\bdon'?t forget\b",
    r"\bremember to\b",
    r"\bfollow up\b",
    r"\bhandle\b",
    r"\btake care of\b",
    r"\bwork on\b",
    r"\bsort (out|this|that|the)\b",
    r"\bsend (me|the|over|out)\b",
    r"\bshare (the|your)\b",
    r"\bupdate (me|the)\b",
    r"\bprepare\b",
    r"\bdeadline\b",
    r"\bdue\b",
    r"\bassigned?\b",
    r"\bby (monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    r"\bby (tomorrow|tonight|eod|end of day|end of week|next week)\b",
]

_REQUEST_RE = re.compile("|".join(REQUEST_PATTERNS), re.IGNORECASE)


def _load_blocklist() -> list[re.Pattern]:
    patterns = []
    for line in BLOCKLIST_PATH.read_text(encoding="utf-8").splitlines():
        term = line.strip()
        if not term or term.startswith("#"):
            continue
        patterns.append(re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE))
    return patterns


def classify(text: str) -> str:
    """Return 'blocked', 'flagged' or 'ignored'. Never stores or logs the text."""
    if not text or not text.strip():
        return "ignored"
    for pattern in _load_blocklist():
        if pattern.search(text):
            return "blocked"
    if _REQUEST_RE.search(text):
        return "flagged"
    return "ignored"