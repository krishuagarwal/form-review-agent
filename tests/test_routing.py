import os
import pytest
from app.routing import (
    calculate_risk_and_route,
    log_decision,
    get_history,
    _AUDIT_LOG,
    _LOG_FILE,
)


@pytest.fixture(autouse=True)
def clear_log():
    """Clear the audit log before every test."""
    _AUDIT_LOG.clear()
    if os.path.exists(_LOG_FILE):
        os.remove(_LOG_FILE)
    yield
    # cleanup after test
    if os.path.exists(_LOG_FILE):
        os.remove(_LOG_FILE)


def test_clean_case():
    """0 issues → low risk → Ready for Approval"""
    result = calculate_risk_and_route([], [])
    
    assert result["risk_level"] == "low"
    assert result["route"] == "Ready for Approval"
    assert result["issue_count"] == 0
    assert "No missing fields" in result["reason"]


def test_flagged_case_medium():
    """1-2 issues → medium risk → Needs Review"""
    missing = ["income"]
    mismatches = ["Name mismatch: form says John, ID says Jon"]
    
    result = calculate_risk_and_route(missing, mismatches)
    
    assert result["risk_level"] == "medium"
    assert result["route"] == "Needs Review"
    assert result["issue_count"] == 2


def test_flagged_case_high():
    """3+ issues → high risk → Needs Review"""
    missing = ["income", "address", "category"]
    mismatches = ["Name mismatch: form says A, ID says B"]
    
    result = calculate_risk_and_route(missing, mismatches)
    
    assert result["risk_level"] == "high"
    assert result["route"] == "Needs Review"
    assert result["issue_count"] == 4


def test_log_and_get_history_order():
    """Log multiple actions and check history is returned in order"""
    app_id = "APP-001"
    
    log_decision(app_id, "auto-flag", "High risk detected")
    log_decision(app_id, "resubmit", "User asked to correct details")
    log_decision(app_id, "approve", "All issues resolved")
    
    history = get_history(app_id)
    
    assert len(history) == 3
    assert history[0]["action"] == "auto-flag"
    assert history[1]["action"] == "resubmit"
    assert history[2]["action"] == "approve"
    
    # Check timestamps are in order
    timestamps = [entry["timestamp"] for entry in history]
    assert timestamps == sorted(timestamps)


def test_get_history_empty():
    """No history for unknown application"""
    history = get_history("UNKNOWN-999")
    assert history == []
