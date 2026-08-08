
**Corrected file:**

```python name=tests/test_expiry_detection.py url=https://github.com/krishuagarwal/form-review-agent/blob/1d992155c2b447b4dbbb1c1c721ce588307d226e/tests/test_expiry_detection.py
from datetime import date, timedelta

from app.expiry_detection import ExpiryChecker


def _future_date_str(days_ahead: int) -> str:
    """Return a date string in DD/MM/YYYY format."""
    target_date = date.today() + timedelta(days=days_ahead)
    return target_date.strftime("%d/%m/%Y")


def test_not_applicable_doc_type():
    checker = ExpiryChecker()

    result = checker.check_expiry("PAN Card", {})

    assert result["applicable"] is False
    assert result["status"] == "not_applicable"


def test_valid_far_future_expiry():
    checker = ExpiryChecker()

    result = checker.check_expiry(
        "Passport",
        {"date_of_expiry": _future_date_str(200)}
    )

    assert result["status"] == "valid"
    assert result["days_remaining"] == 200


def test_expiring_soon():
    checker = ExpiryChecker()

    result = checker.check_expiry(
        "Passport",
        {"date_of_expiry": _future_date_str(10)}
    )

    assert result["status"] == "expiring_soon"


def test_expired_document():
    checker = ExpiryChecker()

    result = checker.check_expiry(
        "Passport",
        {"date_of_expiry": _future_date_str(-5)}
    )

    assert result["status"] == "expired"
    assert result["days_remaining"] == -5


def test_unknown_when_missing_date():
    checker = ExpiryChecker()

    result = checker.check_expiry("Passport", {})

    assert result["status"] == "unknown"


def test_unknown_when_unparseable_date():
    checker = ExpiryChecker()

    result = checker.check_expiry(
        "Passport",
        {"date_of_expiry": "not-a-date"}
    )

    assert result["status"] == "unknown"
