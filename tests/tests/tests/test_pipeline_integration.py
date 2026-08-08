import os
import tempfile
import pytest
import pipeline_integration as pi


@pytest.fixture(autouse=True)
def reset_state():
    """Give each test a fresh pipeline state (independent detector/engine instances)."""
    pi._duplicate_detector = pi.DuplicateDetector()
    pi._cross_check_engine = pi.CrossCheckEngine()
    pi._expiry_checker = pi.ExpiryChecker()
    pi._summary_generator = pi.ReviewSummaryGenerator()
    yield


@pytest.fixture(autouse=True)
def patch_extraction(monkeypatch):
    import cross_check_engine as cce

    fake_data = {
        "Aadhaar": {"name": "Jane Doe", "dob": "1994-05-12"},
        "PAN Card": {"name": "Jane Doe", "dob": "1994-05-12"},
    }

    def _fake(file_path, doc_type):
        return fake_data.get(doc_type, {})

    monkeypatch.setattr(cce, "extract_fields", _fake)
    yield


@pytest.fixture
def dummy_file():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    os.remove(path)


def test_incomplete_application_has_no_summary(dummy_file):
    outcome = pi.process_document_upload(dummy_file, "Aadhaar", "APP-100")
    assert outcome["application_status"] == "Incomplete"
    assert outcome["ai_summary"] is None


def test_duplicate_check_present_in_outcome(dummy_file):
    outcome = pi.process_document_upload(dummy_file, "Aadhaar", "APP-100")
    assert "is_duplicate" in outcome["duplicate_check"]
    assert outcome["duplicate_check"]["is_duplicate"] is False


def test_risk_score_and_label_present(dummy_file):
    outcome = pi.process_document_upload(dummy_file, "Aadhaar", "APP-100")
    assert isinstance(outcome["risk_score"], int)
    assert outcome["risk_label"] in ("LOW", "MEDIUM", "HIGH")
