"""
duplicate_detection.py
-----------------------
Detects duplicate document uploads by hashing file contents (SHA-256)
and checking whether the same file has already been submitted under a
different application ID — a common signal of document reuse or fraud.
"""

import hashlib
from typing import Optional, Dict


class DuplicateDetector:
    """
    Tracks file hashes across all uploads in the current process and
    flags when the same file content appears under a different
    application ID.
    """

    def __init__(self) -> None:
        # Maps file_hash -> {"application_id": str, "doc_type": str}
        self._hash_store: Dict[str, Dict[str, str]] = {}

    @staticmethod
    def _hash_file(file_path: str) -> str:
        """Return the SHA-256 hex digest of a file's contents."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def check_and_register(
        self, file_path: str, application_id: str, doc_type: str
    ) -> Dict[str, Optional[str]]:
        """
        Hash the file, check if it was already seen under a different
        application, and register it if not.

        Returns:
            {
              "file_hash": str,
              "is_duplicate": bool,
              "duplicate_of_application_id": str | None,
            }
        """
        file_hash = self._hash_file(file_path)
        existing = self._hash_store.get(file_hash)

        is_duplicate = existing is not None and existing["application_id"] != application_id
        duplicate_of = existing["application_id"] if is_duplicate else None

        if existing is None:
            self._hash_store[file_hash] = {
                "application_id": application_id,
                "doc_type": doc_type,
            }

        return {
            "file_hash": file_hash,
            "is_duplicate": is_duplicate,
            "duplicate_of_application_id": duplicate_of,
        }
