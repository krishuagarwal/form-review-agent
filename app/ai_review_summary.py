"""
ai_review_summary.py
----------------------
Generates a human-readable review summary for a reviewer, built
strictly from already-computed structured application data (per
Constitution Principle 8 — AI assists the reviewer, it never replaces
the structured evidence).

A deterministic, template-based summary is used by default so this
module — and any test relying on it — never depends on a live AI
call or network access, keeping CI fast and reliable. A real AI
backend can optionally be plugged in via `ai_call_fn`.
"""

from typing import Dict, Any, List, Optional, Callable


def build_application_data(
    application_id: str,
    required_doc_types: List[str],
    present_doc_types: List[str],
    cross_check_result: Optional[Dict[str, Any]],
    expiry_results: List[Dict[str, Any]],
    duplicate_flag: bool,
    risk_score: Optional[int],
    risk_label: str,
) -> Dict[str, Any]:
    """Assembles a single structured dict describing an application's current state."""
    missing = [d for d in required_doc_types if d not in present_doc_types]
    return {
        "application_id": application_id,
        "required_doc_types": required_doc_types,
        "present_doc_types": present_doc_types,
        "missing_doc_types": missing,
        "cross_check": cross_check_result,
        "expiry_flags": expiry_results,
        "duplicate_flag": duplicate_flag,
        "risk_score": risk_score,
        "risk_label": risk_label,
    }


class ReviewSummaryGenerator:
    """
    Generates a one-paragraph summary for a human reviewer from
    structured application data.
    """

    def __init__(self, ai_call_fn: Optional[Callable[[str], str]] = None) -> None:
        """
        Args:
            ai_call_fn: Optional function that takes a prompt string and
                returns an AI-generated response. If not provided, a
                deterministic template-based summary is used instead —
                this is the default and CI-safe path.
        """
        self._ai_call_fn = ai_call_fn

    def generate_summary(self, application_id: str, application_data: Dict[str, Any]) -> str:
        """
        Returns a human-readable summary string for the reviewer.
        Never invents facts not present in application_data.
        """
        if self._ai_call_fn is not None:
            prompt = self._build_prompt(application_data)
            return self._ai_call_fn(prompt)
        return self._build_deterministic_summary(application_data)

    @staticmethod
    def _build_deterministic_summary(data: Dict[str, Any]) -> str:
        total_required = len(data["required_doc_types"])
        total_present = len(data["present_doc_types"])

        parts = [f"{total_present}/{total_required} required documents present."]

        if data["missing_doc_types"]:
            parts.append(f"Missing: {', '.join(data['missing_doc_types'])}.")

        cc = data.get("cross_check")
        if cc:
            if cc.get("all_match"):
                parts.append("All cross-checked fields match across documents.")
            else:
                parts.append(f"Mismatches found: {'; '.join(cc.get('mismatches', []))}.")

        for flag in data.get("expiry_flags", []):
            if flag.get("status") == "expired":
                parts.append(f"{flag.get('doc_type', 'A document')} has EXPIRED.")
            elif flag.get("status") == "expiring_soon":
                parts.append(
                    f"{flag.get('doc_type', 'A document')} expires in {flag.get('days_remaining')} days."
                )

        if data.get("duplicate_flag"):
            parts.append("Possible duplicate document detected — reused from another application.")

        parts.append(f"Risk: {data.get('risk_label', 'UNKNOWN')}.")

        return " ".join(parts)

    @staticmethod
    def _build_prompt(data: Dict[str, Any]) -> str:
        """Builds the prompt sent to a real AI backend, if one is configured."""
        return (
            "Summarize this application review data in one clear paragraph "
            "for a human reviewer. Only state facts present in the data below, "
            f"never invent information.\n\n{data}"
        )
