"""
Field extraction module for the Form Processing Agent.

This module extracts structured fields from raw, semi-structured text
(such as text extracted from a PDF form) using pattern-based parsing.
"""

import re
from typing import Optional, Dict


def extract_fields(text: str) -> Dict[str, Optional[str]]:
    """
    Extract structured fields from raw form text.

    Looks for lines in the format "Label: Value" and maps them to a
    fixed set of expected keys. If a field is not found in the text,
    its value is set to None rather than guessed.

    Args:
        text: Raw text extracted from a form or document (e.g. from a PDF).

    Returns:
        A dictionary with exactly these keys: name, dob, id_number,
        address, income, category. Any field not found in the input
        text will have a value of None.
    """
    fields: Dict[str, Optional[str]] = {
        'name': None,
        'dob': None,
        'id_number': None,
        'address': None,
        'income': None,
        'category': None,
    }

    if not text or not text.strip():
        return fields

    # Maps the labels that may appear in the text to our output keys
    label_map = {
        'name': 'name',
        'date of birth': 'dob',
        'dob': 'dob',
        'id number': 'id_number',
        'id no': 'id_number',
        'address': 'address',
        'income': 'income',
        'category': 'category',
    }

    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line or ':' not in line:
            continue

        label, _, value = line.partition(':')
        label = label.strip().lower()
        value = value.strip()

        if label in label_map and value:
            fields[label_map[label]] = value

    return fields
