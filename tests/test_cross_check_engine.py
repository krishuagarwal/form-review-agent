import os
import tempfile
import pytest
import cross_check_engine as cce
from cross_check_engine import CrossCheckEngine


@pytest.fixture(autouse=True)
def patch_extract_fields(monkeypatch):
    """Deterministic fake extraction so tests don't depend on real parsing."""
    fake_data = {
        "Aadhaar": {"name": "Jane Doe", "dob": "1994-05-12"},
        "Passport": {"name": "Jane Doe", "dob": "1994-05-12"},
        "MismatchDoc": {"name": "Jayne Doe", "dob": "1994-05-12"},
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


def test_first_document_has_no_cross_check(dummy_file):
    engine = CrossCheckEngine()
    result = engine.process_upload(dummy_file, "Aadhaar", "APP-001")
    assert result["extracted_fields"]["name"] == "Jane Doe"
    assert result["cross_check"] is None


def test_second_matching_document_passes_cross_check(dummy_file):
    engine = CrossCheckEngine()
    engine.process_upload(dummy_file, "Aadhaar", "APP-001")
    result = engine.process_upload(dummy_file, "Passport", "APP-001")
    assert result["cross_check"]["all_match"] is True
    assert result["cross_check"]["mismatches"] == []


def test_mismatched_document_flags_discrepancy(dummy_file):
    engine = CrossCheckEngine()
    engine.process_upload(dummy_file, "Aadhaar", "APP-001")
    result = engine.process_upload(dummy_file, "MismatchDoc", "APP-001")
    assert result["cross_check"]["all_match"] is False
    assert len(result["cross_check"]["mismatches"]) > 0


def test_get_all_extracted_fields(dummy_file):
    engine = CrossCheckEngine()
    engine.process_upload(dummy_file, "Aadhaar", "APP-001")
    engine.process_upload(dummy_file, "Passport", "APP-001")
    all_fields = engine.get_all_extracted_fields("APP-001")
    assert set(all_fields.keys()) == {"Aadhaar", "Passport"}


def test_different_applications_are_isolated(dummy_file):
    engine = CrossCheckEngine()
    engine.process_upload(dummy_file, "Aadhaar", "APP-001")
    engine.process_upload(dummy_file, "Aadhaar", "APP-002")
    assert "Aadhaar" in engine.get_all_extracted_fields("APP-001")
    assert "Aadhaar" in engine.get_all_extracted_fields("APP-002")
    assert engine.get_all_extracted_fields("APP-001") is not engine.get_all_extracted_fields("APP-002")
