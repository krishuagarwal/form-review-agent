from app.ai_review_summary import ReviewSummaryGenerator, build_application_data


def test_complete_clean_application_summary():
    data = build_application_data(
        application_id="APP-001",
        required_doc_types=["Aadhaar", "Passport"],
        present_doc_types=["Aadhaar", "Passport"],
        cross_check_result={"all_match": True, "mismatches": []},
        expiry_results=[],
        duplicate_flag=False,
        risk_score=0,
        risk_label="LOW",
    )
    generator = ReviewSummaryGenerator()
    summary = generator.generate_summary("APP-001", data)
    assert "2/2" in summary
    assert "match" in summary.lower()
    assert "LOW" in summary


def test_missing_documents_reflected_in_summary():
    data = build_application_data(
        application_id="APP-002",
        required_doc_types=["Aadhaar", "Passport", "PAN Card"],
        present_doc_types=["Aadhaar"],
        cross_check_result=None,
        expiry_results=[],
        duplicate_flag=False,
        risk_score=10,
        risk_label="MEDIUM",
    )
    generator = ReviewSummaryGenerator()
    summary = generator.generate_summary("APP-002", data)
    assert "Missing" in summary
    assert "Passport" in summary
    assert "PAN Card" in summary


def test_expired_document_flagged_in_summary():
    data = build_application_data(
        application_id="APP-003",
        required_doc_types=["Passport"],
        present_doc_types=["Passport"],
        cross_check_result=None,
        expiry_results=[{"doc_type": "Passport", "status": "expired"}],
        duplicate_flag=False,
        risk_score=30,
        risk_label="HIGH",
    )
    generator = ReviewSummaryGenerator()
    summary = generator.generate_summary("APP-003", data)
    assert "EXPIRED" in summary


def test_duplicate_flag_reflected_in_summary():
    data = build_application_data(
        application_id="APP-004",
        required_doc_types=["Aadhaar"],
        present_doc_types=["Aadhaar"],
        cross_check_result=None,
        expiry_results=[],
        duplicate_flag=True,
        risk_score=50,
        risk_label="HIGH",
    )
    generator = ReviewSummaryGenerator()
    summary = generator.generate_summary("APP-004", data)
    assert "duplicate" in summary.lower()
