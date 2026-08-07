"""
app/security.py

Centralizes everything that keeps uploaded documents and personal data safe:

1. Encryption at rest (Fernet/AES) for every uploaded file.
2. A key manager that keeps the encryption key OUT of the codebase.
3. Safe, random filenames on disk (never the user's original filename).
4. A simple API-key access-control check for the Flask app.
5. A PII-safe logger that redacts sensitive fields before writing logs.
6. File-type / file-size validation to block malicious or oversized uploads.

Design notes for the team:
- Never commit `secure_storage/` or the encryption key file to git. Add both
  to .gitignore.
- In a real deployment, swap the local key file for a proper secrets manager
  (AWS KMS / GCP Secret Manager / HashiCorp Vault) instead of a local file.
"""

from __future__ import annotations

import logging
import os
import re
import secrets
import stat
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

# --------------------------------------------------------------------------
# 1. Key management
# --------------------------------------------------------------------------

_KEY_ENV_VAR = "FORM_AGENT_ENCRYPTION_KEY"
_KEY_FILE = Path(__file__).resolve().parent.parent / "secure_storage" / ".master.key"


def _load_or_create_key() -> bytes:
    """
    Load the Fernet encryption key from an environment variable if present
    (preferred for production), otherwise from a local key file, creating
    one with restrictive permissions if it doesn't exist yet (fine for a
    hackathon demo — swap for a real secrets manager before going live).
    """
    env_key = os.environ.get(_KEY_ENV_VAR)
    if env_key:
        return env_key.encode()

    _KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if _KEY_FILE.exists():
        return _KEY_FILE.read_bytes()

    key = Fernet.generate_key()
    _KEY_FILE.write_bytes(key)
    # Owner read/write only — no group/other access.
    os.chmod(_KEY_FILE, stat.S_IRUSR | stat.S_IWUSR)
    return key


_FERNET = Fernet(_load_or_create_key())


# --------------------------------------------------------------------------
# 2. Encrypt / decrypt file bytes
# --------------------------------------------------------------------------

def encrypt_bytes(data: bytes) -> bytes:
    """Encrypt raw file bytes before writing them to disk."""
    return _FERNET.encrypt(data)


def decrypt_bytes(token: bytes) -> bytes:
    """Decrypt file bytes read from disk. Raises ValueError if tampered/corrupt."""
    try:
        return _FERNET.decrypt(token)
    except InvalidToken as exc:
        raise ValueError(
            "File failed integrity check — possibly corrupted or tampered."
        ) from exc


# --------------------------------------------------------------------------
# 3. Safe filenames + upload validation
# --------------------------------------------------------------------------

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB per document


def validate_upload(original_filename: str, size_bytes: int) -> None:
    """Raise ValueError if the upload fails basic safety checks."""
    ext = Path(original_filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"File type '{ext}' not allowed. Allowed: {sorted(ALLOWED_EXTENSIONS)}"
        )
    if size_bytes <= 0:
        raise ValueError("Empty file.")
    if size_bytes > MAX_FILE_SIZE_BYTES:
        raise ValueError(
            f"File too large ({size_bytes} bytes). Max is {MAX_FILE_SIZE_BYTES} bytes."
        )


def generate_secure_filename(original_filename: str) -> str:
    """
    Never trust or reuse the user's original filename on disk (avoids path
    traversal like '../../etc/passwd' and avoids leaking info via filenames).
    Returns a random token + the original extension only.
    """
    ext = Path(original_filename).suffix.lower()
    token = secrets.token_hex(16)
    return f"{token}{ext}"


# --------------------------------------------------------------------------
# 4. Access control (simple API-key check for the demo)
# --------------------------------------------------------------------------

def is_valid_api_key(provided_key: Optional[str]) -> bool:
    """
    Compares against a server-side secret (set via env var). Uses a
    constant-time comparison to avoid timing attacks.
    """
    expected = os.environ.get("FORM_AGENT_API_KEY", "")
    if not expected or not provided_key:
        return False
    return secrets.compare_digest(provided_key, expected)


# --------------------------------------------------------------------------
# 5. PII-safe logging
# --------------------------------------------------------------------------

_PII_PATTERNS = [
    # Aadhaar-style 12 digit (with optional spaces or hyphens)
    re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
    # PAN format
    re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),
    # Indian mobile numbers (10 digits, optional +91)
    re.compile(r"\b(?:\+91[\s-]?)?\d{10}\b"),
    # Emails
    re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
]


def redact_pii(text: str) -> str:
    """Redact common PII patterns before anything gets logged."""
    redacted = text
    for pattern in _PII_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def get_safe_logger(name: str) -> logging.Logger:
    """
    Returns a logger whose messages are automatically scrubbed of common PII
    patterns before being written out. Use this everywhere instead of
    print() or logging.getLogger() directly.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    class _RedactFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            record.msg = redact_pii(str(record.msg))
            return True

    if not any(isinstance(f, _RedactFilter) for f in logger.filters):
        logger.addFilter(_RedactFilter())
    return logger


# --------------------------------------------------------------------------
# 6. High-level helper: save an uploaded file securely
# --------------------------------------------------------------------------

def save_encrypted_upload(
    original_filename: str,
    file_bytes: bytes,
    storage_dir: Optional[Path] = None,
) -> Path:
    """
    Validate → generate safe name → encrypt → write to disk.

    Returns the full path of the encrypted file that was written.
    Raises ValueError on validation failure.
    """
    validate_upload(original_filename, len(file_bytes))

    if storage_dir is None:
        storage_dir = Path(__file__).resolve().parent.parent / "secure_storage"
    storage_dir.mkdir(parents=True, exist_ok=True)

    safe_name = generate_secure_filename(original_filename)
    target = storage_dir / safe_name

    encrypted = encrypt_bytes(file_bytes)
    target.write_bytes(encrypted)

    # Restrict permissions on the stored file too
    os.chmod(target, stat.S_IRUSR | stat.S_IWUSR)

    return target
