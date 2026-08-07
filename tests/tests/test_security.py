"""Tests for app/security.py — encryption, validation, filenames, API key, PII redaction."""

import os
import stat
from pathlib import Path

import pytest
from cryptography.fernet import Fernet

from app.security import (
    encrypt_bytes,
    decrypt_bytes,
    validate_upload,
    generate_secure_filename,
    is_valid_api_key,
    redact_pii,
    get_safe_logger,
    save_encrypted_upload,
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE_BYTES,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_storage(tmp_path):
    """Temporary directory used instead of real secure_storage/."""
    return tmp_path / "secure_storage"


# ---------------------------------------------------------------------------
# 1. Encryption round-trip
# ---------------------------------------------------------------------------

def test_encrypt_decrypt_roundtrip():
    original = b"Hello, Form Review Agent - confidential PDF bytes"
    token = encrypt_bytes(original)
    assert token != original
    recovered = decrypt_bytes(token)
    assert recovered == original

def test_decrypt_tampered_raises():
    original = b"secret data"
    token = encrypt_bytes(original)
    # Flip one byte to simulate tampering
    tampered = token[:-1] + bytes([(token[-1] + 1) % 256])
    with pytest.raises(ValueError, match="integrity check"):
        decrypt_bytes(tampered)


# ---------------------------------------------------------------------------
# 2. Upload validation
# ---------------------------------------------------------------------------

def test_validate_upload_allowed_extensions():
    for ext in ALLOWED_EXTENSIONS:
        validate_upload(f"document{ext}", 1024)  # should not raise


def test_validate_upload_rejects_bad_extension():
    with pytest.raises(ValueError, match="not allowed"):
        validate_upload("malware.exe", 1024)


def test_validate_upload_rejects_empty():
    with pytest.raises(ValueError, match="Empty file"):
        validate_upload("form.pdf", 0)


def test_validate_upload_rejects_too_large():
    with pytest.raises(ValueError, match="too large"):
        validate_upload("big.pdf", MAX_FILE_SIZE_BYTES + 1)


# ---------------------------------------------------------------------------
# 3. Secure filenames
# ---------------------------------------------------------------------------

def test_generate_secure_filename_keeps_extension():
    name = generate_secure_filename("Rahul_Aadhaar_scan.pdf")
    assert name.endswith(".pdf")
    assert "Rahul" not in name
    assert "Aadhaar" not in name
    assert len(name) > 10  # random token is long


def test_generate_secure_filename_blocks_path_traversal():
    name = generate_secure_filename("../../etc/passwd")
    assert ".." not in name
    assert "/" not in name
    assert "\\" not in name


def test_generate_secure_filename_unique():
    names = {generate_secure_filename("doc.pdf") for _ in range(20)}
    assert len(names) == 20  # all unique


# ---------------------------------------------------------------------------
# 4. API-key check
# ---------------------------------------------------------------------------

def test_is_valid_api_key_correct(monkeypatch):
    monkeypatch.setenv("FORM_AGENT_API_KEY", "super-secret-key-123")
    assert is_valid_api_key("super-secret-key-123") is True


def test_is_valid_api_key_wrong(monkeypatch):
    monkeypatch.setenv("FORM_AGENT_API_KEY", "super-secret-key-123")
    assert is_valid_api_key("wrong-key") is False


def test_is_valid_api_key_missing_env(monkeypatch):
    monkeypatch.delenv("FORM_AGENT_API_KEY", raising=False)
    assert is_valid_api_key("any-key") is False


def test_is_valid_api_key_none():
    assert is_valid_api_key(None) is False


# ---------------------------------------------------------------------------
# 5. PII redaction
# ---------------------------------------------------------------------------

def test_redact_aadhaar():
    text = "Aadhaar number is 1234 5678 9012"
    assert "[REDACTED]" in redact_pii(text)
    assert "1234" not in redact_pii(text)


def test_redact_pan():
    text = "PAN: ABCDE1234F"
    assert "[REDACTED]" in redact_pii(text)


def test_redact_phone():
    text = "Call me on 9876543210 or +91 9876543210"
    redacted = redact_pii(text)
    assert "9876543210" not in redacted
    assert "[REDACTED]" in redacted


def test_redact_email():
    text = "Contact user@example.com for details"
    assert "user@example.com" not in redact_pii(text)
    assert "[REDACTED]" in redact_pii(text)


def test_redact_leaves_safe_text():
    text = "Application status is Ready for Approval"
    assert redact_pii(text) == text


# ---------------------------------------------------------------------------
# 6. Safe logger
# ---------------------------------------------------------------------------

def test_get_safe_logger_redacts(capsys):
    logger = get_safe_logger("test_security_logger")
    logger.info("User Aadhaar 1234 5678 9012 submitted form")
    captured = capsys.readouterr()
    assert "1234" not in captured.err and "1234" not in captured.out
    assert "[REDACTED]" in captured.err or "[REDACTED]" in captured.out


# ---------------------------------------------------------------------------
# 7. High-level save_encrypted_upload
# ---------------------------------------------------------------------------

def test_save_encrypted_upload_happy_path(tmp_storage):
    content = b"%PDF-1.4 fake form content"
    path = save_encrypted_upload("applicant_form.pdf", content, storage_dir=tmp_storage)

    assert path.exists()
    assert path.parent == tmp_storage
    assert path.suffix == ".pdf"
    assert "applicant" not in path.name  # original name not used

    # File should be encrypted (not equal to original bytes)
    assert path.read_bytes() != content

    # Round-trip decrypt works
    recovered = decrypt_bytes(path.read_bytes())
    assert recovered == content

    # Permissions should be owner-only (0600)
    mode = path.stat().st_mode
    assert mode & stat.S_IRUSR
    assert mode & stat.S_IWUSR
    assert not (mode & stat.S_IRGRP)
    assert not (mode & stat.S_IROTH)


def test_save_encrypted_upload_rejects_bad_type(tmp_storage):
    with pytest.raises(ValueError, match="not allowed"):
        save_encrypted_upload("virus.exe", b"bad", storage_dir=tmp_storage)
