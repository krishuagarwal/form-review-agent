"""Verification logic: missing field detection and cross-document checks."""

from typing import Dict, List


def check_missing_fields(fields_dict: Dict[str, str], required_fields_list: List[str]) -> List[str]:
    """
    Check which required fields are missing or blank in the extracted data.

    Args:
        fields_dict: Dictionary of extracted field values.
        required_fields_list: List of field names that are required.

    Returns:
        A list of field names that are missing or blank.
    """
    missing = []
    for field in required_fields_list:
        if field not in fields_dict or not fields_dict[field]:
            missing.append(field)
    return missing


def cross_check_documents(fields_dict_1: Dict[str, str], fields_dict_2: Dict[str, str]) -> List[str]:
    """
    Compare name and date of birth between two extracted documents.

    Args:
        fields_dict_1: Extracted fields from the first document (e.g. application form).
        fields_dict_2: Extracted fields from the second document (e.g. ID proof).

    Returns:
        A list of human-readable mismatch messages, empty if everything matches.
    """
    mismatch_messages = []

    if fields_dict_1.get("name") != fields_dict_2.get("name"):
        mismatch_messages.append(
            f"Name mismatch: form says '{fields_dict_1.get('name')}', ID says '{fields_dict_2.get('name')}'"
        )

    if fields_dict_1.get("dob") != fields_dict_2.get("dob"):
        mismatch_messages.append(
            f"DOB mismatch: form says '{fields_dict_1.get('dob')}', ID says '{fields_dict_2.get('dob')}'"
        )

    return mismatch_messages
