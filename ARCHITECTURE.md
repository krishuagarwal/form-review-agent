# Architecture — Form Review Agent

## Overview
Form Review Agent is an AI-assisted pipeline that ingests application forms
and supporting documents, extracts structured data, checks for missing or
mismatched information, calculates a risk score, and routes uncertain or
flagged cases to a human reviewer. Every automated and human decision is
logged, so any outcome can be traced back to its cause.

## Tech Stack
- **Language:** Python 3.11+
- **Testing:** pytest
- **CI/CD:** GitHub Actions (runs pytest on every push)
- **AI Backend:** Groq (via OpenAI-compatible API), used for field extraction
- **Agent tooling:** Cline (VS Code extension), custom agent + skill (see AGENTS_AND_SKILLS.md)
- **Frontend/Interface:** TBD (CLI or simple web UI — decide based on time remaining)

## Data Model

Extracted form data is represented as a dictionary with this shape:

```json
{
  "name": "string",
  "date_of_birth": "string",
  "id_number": "string",
  "address": "string",
  "income": "string",
  "category": "string"
}
```

An audit log entry has this shape:

```json
{
  "application_id": "string",
  "action": "auto-flag | approve | reject | resubmit",
  "reason": "string",
  "timestamp": "ISO 8601 datetime"
}
```

## Pipeline Stages

1. **Upload** — raw form text/PDF is provided as input
2. **Extraction** (`app/extraction.py`) — `extract_fields(text)` pulls structured
   fields out of raw text using the AI model
3. **Missing Field Detection** (`app/verification.py`) — `check_missing_fields(fields_dict, required_fields_list)`
   flags which required fields are blank or absent
4. **Cross-Document Verification** (`app/verification.py`) — `cross_check_documents(fields_dict_1, fields_dict_2)`
   compares two extracted documents (e.g. form vs ID proof) and returns any mismatches
5. **Risk Scoring & Routing** (`app/routing.py`) — `calculate_risk_and_route(missing_fields_list, mismatches_list)`
   scores the case (0 issues = low, 1-2 = medium, 3+ = high) and returns
   `"Ready for Approval"` or `"Needs Review"` with a reason
6. **Human Decision & Audit Log** (`app/routing.py`) — `log_decision(application_id, action, reason)`
   records every action with a timestamp; `get_history(application_id)`
   returns the full decision trail for one application

## Module Ownership

| File | Owns | Built by |
|---|---|---|
| `app/extraction.py` | Field extraction | Person A |
| `app/verification.py` | Missing field check + cross-document check | Person B |
| `app/routing.py` | Risk scoring, routing, audit logging | Person C |
| `.github/workflows/ci.yml` | CI/CD pipeline | Person D |

## Human-in-the-Loop Principle
The system never auto-approves or auto-rejects a flagged or high-risk case.
Automated steps (extraction, validation, scoring) may run unsupervised.
Final approve/reject/resubmit decisions always require a human action,
recorded via `log_decision`.

## Decisions Log
*(Add entries here as the team makes key design choices during the build.)*

- 2026-08-XX — Chose Groq (llama-3.3-70b-versatile) as the AI backend for extraction, for speed and free-tier availability.
