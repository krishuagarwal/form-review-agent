# Architecture — DocDesk (Form Review Agent)

*Deploy or Die — HowToAlgo x GDG on Campus KIIT Hackathon | Track A: Business Process Automation*

---

## 1. Overview

DocDesk is an agent-driven system that takes a government/institutional application (Aadhaar, PAN, Passport, Bank Account Opening, Driving License, Voter ID) plus its supporting documents, and determines whether the application is **"Ready for Approval"** or **"Needs Review"** — with a clear, traceable reason attached to every decision. A human reviewer always makes the final call; the system only extracts, verifies, scores, and routes.

---

## 2. Design Principles

The full reasoning behind these lives in [`constitution.md`](./constitution.md). In summary:

- The agent never makes a final approve/reject decision — only flags and routes
- Every decision is logged with a timestamp and reason — nothing happens silently
- Uncertain fields return `None`, never a guessed value
- Modules are loosely coupled so requirements can change without breaking the system
- When in doubt, fail toward "Needs Review," not toward silent approval

---

## 3. Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.11+ | Team familiarity, strong text-processing ecosystem |
| Coding Agent | Cline (VS Code) | Human-approved, step-by-step agent execution |
| AI Backend | Groq / NVIDIA Build (OpenAI-compatible) | Free tier, fast inference, swappable via one interface |
| Encryption | `cryptography` (Fernet/AES) | Industry-standard symmetric encryption for files at rest |
| Config | `python-dotenv`, `pydantic` | Safe environment variable handling and data validation |
| Testing | `pytest` | Simple, widely supported, integrates cleanly with CI |
| CI/CD | GitHub Actions | Free for public repos, native GitHub integration |
| Frontend | Lightweight web UI ("DocDesk") | Category picker → checklist → upload → review, no heavy framework needed |

---

## 4. High-Level Data Flow 
┌─────────────────────┐
                 │   User selects a     │
                 │  document category   │
                 └──────────┬───────────┘
                            │
                 ┌──────────▼───────────┐
                 │  Official checklist   │
                 │   shown to user       │
                 └──────────┬───────────┘
                            │
                 ┌──────────▼───────────┐
                 │  Documents uploaded    │
                 │  (encrypted at rest)   │
                 └──────────┬───────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                                     ▼
          ┌─────────────────────┐ ┌─────────────────────┐
│ Field Extraction │ │ Auto Cross-Check │
│ (extraction.py) │──────────────▶ on Upload │
│ extract_fields() │ │ (verification.py) │
└──────────┬───────────┘ └──────────┬───────────┘
│ │
▼ ▼
┌─────────────────────┐ ┌─────────────────────┐
│ Missing Field Check │ │ Cross-Document │
│ (verification.py) │ │ Verification │
│ check_missing_fields()│ │ cross_check_documents()│
└──────────┬───────────┘ └──────────┬───────────┘
│ │
└──────────────────┬────────────────────┘
▼
┌─────────────────────┐
│ Risk Scoring & │
│ Routing │
│ (routing.py) │
│ calculate_risk_and_ │
│ route() │
└──────────┬───────────┘
│
┌──────────▼───────────┐
│ AI Review Summary │
│ (generated from │
│ structured results │
│ only — never a new │
│ source of truth) │
└──────────┬───────────┘
│
┌──────────▼───────────┐
│ Decision & Audit Log │
│ (routing.py) │
│ log_decision() │
│ get_history() │
└──────────┬───────────┘
│
┌──────────▼───────────┐
│ Output: Ready for │
│ Approval / Needs │
│ Review + reason │
└─────────────────────┘
---

## 5. Module Breakdown

### 5.1 `app/extraction.py` — Field Extraction
**Custom Agent: Form Field Extractor**

- `extract_fields(text: str) -> dict` — parses raw form/document text and returns a dictionary with exactly these keys: `name`, `dob`, `id_number`, `address`, `income`, `category`
- Uses deterministic, rule-based label parsing (`"Label: Value"` pattern matching) rather than a live AI call for this core function — this was a deliberate design decision (see §8) to keep extraction fast, reliable, and 100% reproducible in CI
- Any field not found in the source text is returned as `None` — never guessed

### 5.2 `app/verification.py` — Verification
**Custom Skill: Cross-Document Verifier**

- `check_missing_fields(fields_dict, required_fields_list) -> list` — returns which required fields are missing or blank for the selected document category
- `cross_check_documents(fields_dict_1, fields_dict_2) -> list` — compares fields (name, DOB) across two documents, returning human-readable mismatch messages (e.g. *"Name mismatch: form says 'Krishu Sharma', ID says 'Krishu S.'"*)
- **Auto cross-check on upload (planned extension):** wires `extract_fields()` directly into the upload flow, so the moment a document is uploaded, its fields are extracted and immediately cross-checked against the rest of the application — turning "did they upload something" into "does what they uploaded actually match"

### 5.3 `app/routing.py` — Risk Scoring, Routing & Audit
- `calculate_risk_and_route(missing_fields_list, mismatches_list) -> dict` — counts issues and assigns a risk level (0 issues = low, 1–2 = medium, 3+ = high), returning `"Ready for Approval"` or `"Needs Review"` with the reason
- `log_decision(application_id, action, reason)` — records every action (auto-flag, human approve/reject/resubmit) with a timestamp
- `get_history(application_id) -> list` — returns the full, ordered decision history for one application
- **AI-generated review summary (planned extension):** once all required documents are present, the AI backend generates a single human-readable paragraph (e.g. *"All 4 required docs present, DOB matches across documents, risk: low"*) built strictly from the already-computed structured results — never an independent source of truth (Constitution, Principle 8)

### 5.4 `app/security.py` — Security Layer
- File encryption at rest using Fernet/AES; the encryption key is stored outside the codebase (environment variable / secrets manager)
- Uploaded files are renamed to random tokens on storage — original filenames are never persisted, preventing path traversal or metadata leakage
- Every API route requires an `X-API-Key` header, checked via constant-time comparison to prevent timing attacks
- Upload validation restricts file types to PDF/JPG/PNG and caps size at 10 MB
- PII-safe logging: the logger auto-redacts Aadhaar, PAN, phone, and email patterns before anything is written to disk

### 5.5 Frontend — DocDesk UI
- Category selector (Aadhaar, PAN, Passport, Bank Account Opening, Driving License, Voter ID)
- Displays the official checklist and accepted proof types per category
- File upload with drag-and-drop, connected to the encrypted storage pipeline
- "Run review" triggers the full backend pipeline and displays the completeness/risk result
- A "Play the demo" mode runs the flow against sample files with no real upload, for safe live demonstration

### 5.6 `main.py` — Pipeline Orchestration
Connects all modules end-to-end: extract → verify → cross-check → score & route → log. Runs against three demo scenarios (clean, missing-field, mismatch) to validate the full pipeline in one command.

---

## 6. Data Contract

To let 4 team members build independent modules in parallel without integration conflicts, every function that produces or consumes extracted fields uses this exact dictionary shape, agreed on before any feature code was written:

```python
{
    "name": str | None,
    "dob": str | None,
    "id_number": str | None,
    "address": str | None,
    "income": str | None,
    "category": str | None
}
```

---

## 7. What's Deliberately Out of Scope (MVP Boundaries)

Documented honestly rather than silently ignored:

- **Fraud/suspicious-pattern detection** — too fuzzy to build reliably within a one-day build; see Roadmap
- **OCR for handwritten/scanned forms** — the MVP works on typed/text-extractable PDFs; handwriting recognition needs more validation time than available
- **Final approval/rejection authority** — by design, the system never holds this authority; a human always does

---

## 8. Key Design Decisions & Trade-offs

**Why rule-based extraction instead of a live AI call inside `extract_fields()`?**
An earlier version called an AI model directly inside the extraction function. This made tests flaky — the same input could produce slightly different output between runs (different phrasing, casing, whitespace), which is unacceptable for a function whose output feeds directly into verification and risk scoring. Switching to deterministic label-pattern parsing made the function 100% reproducible, faster, and reliable in CI, at the cost of not handling wildly unstructured or handwritten input — an explicit, documented trade-off, not an oversight.

**Why keep AI-generated summaries separate from the decision logic?**
It would be tempting to let an AI model directly decide "Ready for Approval" vs "Needs Review." We deliberately did not do this. The AI summary is generated *after* and *from* the structured, deterministic risk-scoring output — never the other way around — so a hallucinated summary can never change an actual routing decision (Constitution, Principle 8).

**Why loosely couple extraction, verification, and routing?**
Each module only depends on the shared data contract (§6), not on each other's internals. This was a deliberate choice to survive the hackathon's Day 2 "surprise requirement" — a new field or check can be added to one module without needing to touch or retest the others.

---

## 9. Roadmap

Planned but not yet built — see [`constitution.md`](./constitution.md) for the governing principles behind these:

1. **Auto expiry-date detection** — for documents like Passport or Driving License, extract the expiry date during processing and automatically flag "expires in 20 days" or reject if already expired
2. **Auto status notifications** — when an application's status changes (Incomplete → Complete, or a risk score changes), automatically fire an email/webhook notification instead of requiring the applicant to check manually
3. **Duplicate-upload / fraud detection** — hash every uploaded file (SHA-256) before storing it; if the same hash appears under a different application ID, automatically flag it as possible document reuse

---

## 10. Testing Strategy

- Every module ships with unit tests covering: a complete/clean case, a missing-field case, a mismatch case, and empty/garbage input
- Security module includes dedicated encryption/decryption round-trip tests
- All tests run automatically in CI (`.github/workflows/ci.yml`) on every push
- Local verification before every push: `pytest -v`
