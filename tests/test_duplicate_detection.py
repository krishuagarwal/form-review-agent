import os
import tempfile
import pytest
from duplicate_detection import DuplicateDetector


@pytest.fixture
def sample_file():
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, "wb") as f:
        f.write(b"sample document content")
    yield path
    os.remove(path)


def test_first_upload_is_not_duplicate(sample_file):
    detector = DuplicateDetector()
    result = detector.check_and_register(sample_file, "APP-001", "Aadhaar")
    assert result["is_duplicate"] is False
    assert result["duplicate_of_application_id"] is None
    assert len(result["file_hash"]) == 64  # sha256 hex length


def test_same_file_different_application_flagged(sample_file):
    detector = DuplicateDetector()
    detector.check_and_register(sample_file, "APP-001", "Aadhaar")
    result = detector.check_and_register(sample_file, "APP-002", "Aadhaar")
    assert result["is_duplicate"] is True
    assert result["duplicate_of_application_id"] == "APP-001"


def test_same_file_same_application_not_flagged(sample_file):
    detector = DuplicateDetector()
    detector.check_and_register(sample_file, "APP-001", "Aadhaar")
    result = detector.check_and_register(sample_file, "APP-001", "Aadhaar")
    assert result["is_duplicate"] is False
