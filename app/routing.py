from datetime import datetime
from typing import List, Dict, Any
import json
import os

# Simple in-memory store + optional file persistence
_AUDIT_LOG: List[Dict[str, Any]] = []
_LOG_FILE = "audit_log.json"


def _load_log() -> None:
    """Load existing audit log from file if it exists."""
    global _AUDIT_LOG
    if os.path.exists(_LOG_FILE):
        try:
            with open(_LOG_FILE, "r", encoding="utf-8") as f:
                _AUDIT_LOG = json.load(f)
        except (json.JSONDecodeError, IOError):
            _AUDIT_LOG = []


def _save_log() -> None:
    """Persist the audit log to a file."""
    with open(_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(_AUDIT_LOG, f, indent=2, ensure_ascii=False)


def calculate_risk_and_route(
    missing_fields_list: List[str],
    mismatches_list: List[str]
) -> Dict[str, Any]:
    """
    Calculate risk score and decide the routing action.

    Risk rules:
    - 0 issues  → low      → "Ready for Approval"
    - 1-2 issues → medium  → "Needs Review"
    - 3+ issues → high     → "Needs Review"

    Args:
        missing_fields_list: List of missing or blank required fields.
        mismatches_list: List of cross-document mismatch messages.

    Returns:
        A dictionary containing:
        - risk_level: "low" | "medium" | "high"
        - route: "Ready for Approval" | "Needs Review"
        - reason: Human-readable explanation
        - issue_count: Total number of issues
    """
    issue_count = len(missing_fields_list) + len(mismatches_list)

    if issue_count == 0:
        risk_level = "low"
        route = "Ready for Approval"
        reason = "No missing fields or mismatches found."
    elif issue_count <= 2:
        risk_level = "medium"
        route = "Needs Review"
        reason = f"{issue_count} issue(s) detected. Manual review required."
    else:
        risk_level = "high"
        route = "Needs Review"
        reason = f"{issue_count} issue(s) detected. High risk – manual review required."

    return {
        "risk_level": risk_level,
        "route": route,
        "reason": reason,
        "issue_count": issue_count,
        "missing_fields": missing_fields_list,
        "mismatches": mismatches_list,
    }


def log_decision(
    application_id: str,
    action: str,
    reason: str
) -> None:
    """
    Record a decision in the audit log with a timestamp.

    Allowed actions: auto-flag | approve | reject | resubmit

    Args:
        application_id: Unique identifier of the application.
        action: The action being recorded.
        reason: Why this action was taken.
    """
    _load_log()

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "application_id": application_id,
        "action": action,
        "reason": reason,
    }

    _AUDIT_LOG.append(entry)
    _save_log()


def get_history(application_id: str) -> List[Dict[str, Any]]:
    """
    Return the full audit history for a given application, in chronological order.

    Args:
        application_id: The application to retrieve history for.

    Returns:
        A list of audit entries for that application, sorted by timestamp.
    """
    _load_log()

    history = [
        entry for entry in _AUDIT_LOG
        if entry.get("application_id") == application_id
    ]

    history.sort(key=lambda x: x.get("timestamp", ""))
    return history
