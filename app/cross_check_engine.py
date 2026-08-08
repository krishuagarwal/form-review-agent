"""
cross_check_engine.py
-----------------------
Wraps field extraction and cross-document verification into a stateful
engine that tracks all documents uploaded so far for a given
application, so each new upload can be checked against the others.
"""

from typing import Dict, Any, List

try:
    from app.extraction import extract_fields as _extract_fields_from_text  # type: ignore
except ImportError:
    _extract_fields_from_text = None

try:
    from app.verification import cross_check_documents as _cross_check_documents  # type: ignore
except ImportError:
    def _cross_check_documents(fields_1: dict, fields_2: dict) -> List[str]:
        """Stand-in cross-checker: compares name and dob between two field sets."""
        mismatches = []
        for key in ("name", "dob"):
            v1, v2 = fields_1.get(key), fields_2.get(key)
            if v1 and v2 and v1 != v2:
                mismatches.append(f"{key} mismatch: '{v1}' vs '{v2}'")
        return mismatches


def extract_fields(file_path: str, doc_type: str) -> Dict[str, Any]:
    """
    Extract fields from an uploaded document.

    This is a module-level function (not a method) so it can be
    monkeypatched in tests/demos without needing real OCR/file parsing.
    """
    if _extract_fields_from_text is not None:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        return _extract_fields_from_text(text)
    # Fallback used only when app.extraction isn't available (standalone testing)
    return {}


class CrossCheckEngine:
    """Stateful engine tracking extracted fields per application, across documents."""

    def __init__(self) -> None:
        # application_id -> {doc_type: extracted_fields}
        self._store: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def process_upload(self, file_path: str, doc_type: str, application_id: str) -> Dict[str, Any]:
        """
        Extracts fields from the newly uploaded document and cross-checks
        them against any other documents already uploaded for this
        application.

        Returns:
            {
              "extracted_fields": dict,
              "cross_check": {"all_match": bool, "mismatches": list[str]} | None
            }
        """
        fields = extract_fields(file_path, doc_type)

        app_docs = self._store.setdefault(application_id, {})
        app_docs[doc_type] = fields

        cross_check_result = None
        other_docs = {k: v for k, v in app_docs.items() if k != doc_type}
        if other_docs:
            all_mismatches: List[str] = []
            for other_type, other_fields in other_docs.items():
                all_mismatches.extend(_cross_check_documents(fields, other_fields))
            cross_check_result = {
                "all_match": len(all_mismatches) == 0,
                "mismatches": all_mismatches,
            }

        return {"extracted_fields": fields, "cross_check": cross_check_result}

    def get_all_extracted_fields(self, application_id: str) -> Dict[str, Dict[str, Any]]:
        """Returns {doc_type: extracted_fields} for every document uploaded so far."""
        return self._store.get(application_id, {})
