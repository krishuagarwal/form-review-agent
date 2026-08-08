"""
expiry_detection.py
--------------------
Checks whether a document's expiry date (if applicable) has already
passed or is approaching, so expired documents are flagged
automatically instead of requiring a manual check.
"""

from datetime import datetime, date
from typing import Optional, Dict, Any

EXPIRY_APPLICABLE_DOCS = {"Passport", "Driving License", "Voter ID"}
WARNING_WINDOW_DAYS = 30

# Formats we attempt to parse, in order.
_DATE_FORMATS = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]


class ExpiryChecker:
    """Determines expiry status for documents that carry an expiry date."""

    def check_expiry(self, doc_type: str, extracted_fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Args:
            doc_type: The type of document (e.g. "Passport").
            extracted_fields: Fields extracted from the document, expected
                to contain "date_of_expiry" as a string if applicable.

        Returns:
            {
              "applicable": bool,
              "status": "not_applicable" | "valid" | "expiring_soon" | "expired" | "unknown",
              "expiry_date": str | None,
              "days_remaining": int | None,
            }
        """
        if doc_type not in EXPIRY_APPLICABLE_DOCS:
            return {
                "applicable": False,
                "status": "not_applicable",
                "expiry_date": None,
                "days_remaining": None,
            }

        raw_date = extracted_fields.get("date_of_expiry")
        parsed = self._parse_date(raw_date) if raw_date else None

        if parsed is None:
            return {
                "applicable": True,
                "status": "unknown",
                "expiry_date": raw_date,
                "days_remaining": None,
            }

        days_remaining = (parsed - date.today()).days

        if days_remaining < 0:
            status = "expired"
        elif days_remaining <= WARNING_WINDOW_DAYS:
            status = "expiring_soon"
        else:
            status = "valid"

        return {
            "applicable": True,
            "status": status,
            "expiry_date": raw_date,
            "days_remaining": days_remaining,
        }

    @staticmethod
    def _parse_date(raw_date: Optional[str]) -> Optional[date]:
        """Attempt to parse a date string using known formats. Returns None if unparseable."""
        if not raw_date:
            return None
        for fmt in _DATE_FORMATS:
            try:
                return datetime.strptime(raw_date, fmt).date()
            except ValueError:
                continue
        return None
