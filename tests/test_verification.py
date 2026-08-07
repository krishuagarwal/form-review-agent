"""Tests for form verification: missing fields and cross-document checks."""

import unittest

from app.verification import check_missing_fields, cross_check_documents


class TestVerification(unittest.TestCase):
    """Test cases for verification.py functions."""

    def test_check_missing_fields_complete(self):
        """All required fields present should return an empty list."""
        fields_dict = {
            'name': 'John Doe',
            'dob': '1990-01-01',
            'id_number': '1234567890',
            'address': '123 Main St, Anytown, USA',
            'income': '50000',
            'category': 'Employee'
        }
        required_fields_list = ['name', 'dob', 'id_number', 'address', 'income', 'category']
        self.assertEqual(check_missing_fields(fields_dict, required_fields_list), [])

    def test_check_missing_fields_missing(self):
        """Missing required fields should be returned in a list."""
        fields_dict = {
            'name': 'Jane Doe',
            'dob': '1995-06-15',
            'address': '456 Elm St, Othertown, USA'
        }
        required_fields_list = ['name', 'dob', 'id_number', 'address', 'income', 'category']
        expected_output = ['id_number', 'income', 'category']
        self.assertEqual(check_missing_fields(fields_dict, required_fields_list), expected_output)

    def test_cross_check_documents_match(self):
        """Matching fields across two documents should return no mismatches."""
        fields_dict_1 = {'name': 'John Doe', 'dob': '1990-01-01'}
        fields_dict_2 = {'name': 'John Doe', 'dob': '1990-01-01'}
        self.assertEqual(cross_check_documents(fields_dict_1, fields_dict_2), [])

    def test_cross_check_documents_mismatch(self):
        """Mismatched fields across two documents should be reported clearly."""
        fields_dict_1 = {'name': 'John Doe', 'dob': '1990-01-01'}
        fields_dict_2 = {'name': 'Jane Doe', 'dob': '1995-06-15'}
        expected_output = [
            "Name mismatch: form says 'John Doe', ID says 'Jane Doe'",
            "DOB mismatch: form says '1990-01-01', ID says '1995-06-15'"
        ]
        self.assertEqual(cross_check_documents(fields_dict_1, fields_dict_2), expected_output)


if __name__ == '__main__':
    unittest.main()
