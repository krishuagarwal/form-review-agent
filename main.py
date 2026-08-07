# main.py
"""
End-to-end form-processing pipeline demo.
Run with:  python main.py
"""

from app.extraction import extract_fields
from app.verification import check_missing_fields, cross_check_documents
from app.routing import calculate_risk_and_route, log_decision, get_audit_history


# ---------------------------------------------------------------------------
# Sample application cases
# ---------------------------------------------------------------------------
SAMPLE_CASES = [
    {
        "app_id": "APP-001-CLEAN",
        "form_text": """
            Full Name: Priya Sharma
            Date of Birth: 15-03-1992
            Address: 42 Lakeview Road, Bengaluru 560001
            Annual Income: 850000
            ID Number: AADHAAR-1234-5678-9012
        """,
        "id_text": """
            Name: Priya Sharma
            DOB: 15/03/1992
            Address: 42 Lakeview Road, Bengaluru 560001
            Aadhaar: 1234 5678 9012
        """,
        "description": "Complete & matching case"
    },
    {
        "app_id": "APP-002-MISSING",
        "form_text": """
            Full Name: Rahul Verma
            Date of Birth: 22-07-1988
            Address: 17 MG Road, Mumbai 400001
            ID Number: AADHAAR-9876-5432-1098
        """,
        "id_text": """
            Name: Rahul Verma
            DOB: 22/07/1988
            Address: 17 MG Road, Mumbai 400001
            Aadhaar: 9876 5432 1098
        """,
        "description": "Missing income field"
    },
    {
        "app_id": "APP-003-MISMATCH",
        "form_text": """
            Full Name: Ananya Patel
            Date of Birth: 05-11-1995
            Address: 8 Park Street, Kolkata 700016
            Annual Income: 620000
            ID Number: AADHAAR-4567-8901-2345
        """,
        "id_text": """
            Name: Ananya Sharma          # ← name mismatch
            DOB: 05/11/1995
            Address: 8 Park Street, Kolkata 700016
            Aadhaar: 4567 8901 2345
        """,
        "description": "Name mismatch between form and ID"
    },
]


def run_pipeline(case: dict) -> None:
    """Execute the full pipeline for one application and print a clean report."""
    app_id = case["app_id"]
    print("\n" + "=" * 70)
    print(f"APPLICATION: {app_id}  ({case['description']})")
    print("=" * 70)

    # 1. Extract fields
    form_fields = extract_fields(case["form_text"], source="form")
    id_fields = extract_fields(case["id_text"], source="id_document")

    print("\n[Extracted Fields – Form]")
    for k, v in form_fields.items():
        print(f"  {k:20}: {v}")

    print("\n[Extracted Fields – ID Document]")
    for k, v in id_fields.items():
        print(f"  {k:20}: {v}")

    # 2. Check missing fields
    missing = check_missing_fields(form_fields)
    print("\n[Missing Fields]")
    if missing:
        for field in missing:
            print(f"  • {field}")
    else:
        print("  None")

    # 3. Cross-check documents
    mismatches = cross_check_documents(form_fields, id_fields)
    print("\n[Mismatches]")
    if mismatches:
        for m in mismatches:
            print(f"  • {m}")
    else:
        print("  None")

    # 4. Calculate risk & route
    risk_level, status, reason = calculate_risk_and_route(
        form_fields, missing, mismatches
    )

    print("\n[Decision]")
    print(f"  Risk Level : {risk_level}")
    print(f"  Status     : {status}")
    if reason:
        print(f"  Reason     : {reason}")

    # 5. Log the decision
    log_decision(
        app_id=app_id,
        form_fields=form_fields,
        id_fields=id_fields,
        missing=missing,
        mismatches=mismatches,
        risk_level=risk_level,
        status=status,
        reason=reason,
    )
    print("\n  → Decision logged to audit trail.")


def main():
    print("FORM-PROCESSING PIPELINE – LIVE DEMO")
    print("Running three sample cases...\n")

    for case in SAMPLE_CASES:
        run_pipeline(case)

    # ------------------------------------------------------------------
    # Audit log history for one application
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("AUDIT LOG HISTORY – APP-001-CLEAN")
    print("=" * 70)

    history = get_audit_history("APP-001-CLEAN")
    if not history:
        print("  (no history found)")
    else:
        for entry in history:
            print(f"\n  Timestamp : {entry.get('timestamp', 'N/A')}")
            print(f"  Action    : {entry.get('action', 'N/A')}")
            print(f"  Status    : {entry.get('status', 'N/A')}")
            if entry.get("details"):
                print(f"  Details   : {entry['details']}")

    print("\n" + "=" * 70)
    print("Demo complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()
