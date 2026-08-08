# Constitution — Form Review Agent (DocDesk)

*The governing principles our AI agents and our team follow while building and operating this system.*

---

## Mission

Build a reliable, auditable, human-in-the-loop form and document review agent that extracts data from messy application text, verifies its completeness and consistency across documents, detects duplicates and expired documents, scores risk, and routes every application for human approval — never for automated final judgment.

---

## Non-Negotiable Principles

### 1. Human stays in control
No critical decision — approve or reject — is ever made automatically. The system's only outputs are a **"Ready for Approval"** or **"Needs Review"** flag, each with a clear reason. The human reviewer makes every final call.

### 2. Everything is traceable
Every extraction, verification, duplicate check, expiry check, and routing decision is logged with a timestamp and a reason. Nothing happens silently. A reviewer — or a judge — can reconstruct exactly how and why any decision was reached.

### 3. No hallucinations
If a field cannot be confidently determined from the source text, the system returns `None` and records the uncertainty. It never invents, guesses, or fills in a plausible-sounding value.

### 4. Small, testable units
Every function is pure where possible, carries type hints and a docstring, and ships with at least one unit test covering a normal case and an edge case. Complexity lives in composition, not in individual functions.

### 5. Fail safe
When in doubt, the system routes to **"Needs Review."** A false positive costs a reviewer two minutes; a silent false negative costs an applicant their eligibility. We optimize for the former.

### 6. Architecture for change
Core modules — extraction, verification, duplicate detection, expiry detection, routing — remain loosely coupled, communicating only through a well-defined data contract. This lets a new requirement be added without breaking existing behavior.

### 7. Verification, not assumption
An uploaded document proves nothing on its own. Every uploaded proof has its extracted fields cross-checked against the rest of the application via `cross_check_documents()`, run automatically on upload through `cross_check_engine.py`. The system verifies *what was uploaded matches the application* — not merely *that something was uploaded.*

### 8. AI assists the reviewer; it never replaces the evidence
Any AI-generated natural-language summary shown to a reviewer — e.g. *"4/4 required documents present. DOB matches across documents. Risk: low."* — is generated **from** the system's already-computed structured flags, mismatches, duplicate checks, expiry checks, and risk score. It is never an independent source of truth, and it must never state a claim the structured data doesn't already support. By default, this summary is produced by a deterministic template, not a live model call, so the pipeline's behavior stays fully reproducible; a real AI backend may be plugged in without changing this principle.

### 9. Reused documents are treated as evidence, not proof of fraud
A duplicate file hash across two applications (`duplicate_detection.py`) is flagged for human review, never auto-rejected. The system surfaces the signal; it does not accuse.

### 10. Time-sensitive documents are checked, not assumed valid
Any document type carrying an expiry date (Passport, Driving License, Voter ID) is checked by `expiry_detection.py` on every upload. Expired documents are flagged as high-priority "Needs Review," not silently accepted.

---

## Decision Hierarchy

When principles conflict or a new case isn't covered, resolve in this order:

1. **This Constitution**
2. `AGENTS.md` + `AGENTS_AND_SKILLS.md`
3. `ARCHITECTURE.md`
4. Individual function specifications

---

## System Composition

The principles above are enforced across these modules, orchestrated end-to-end by `pipeline_integration.py`:

| Module | Enforces |
|---|---|
| `extraction.py` | Principle 3 (no hallucinations) |
| `verification.py`, `cross_check_engine.py` | Principle 7 (verification, not assumption) |
| `duplicate_detection.py` | Principle 9 (reused documents flagged, not accused) |
| `expiry_detection.py` | Principle 10 (time-sensitive checks, not assumptions) |
| `routing.py` | Principles 1, 2, 5 (human control, traceability, fail-safe) |
| `ai_review_summary.py` | Principle 8 (AI assists, never replaces evidence) |
| `security.py` | Data protection, independent of but supporting all principles above |

---

## What This System Deliberately Does Not Do

Documented honestly, not silently omitted:

- **General fraud-pattern detection beyond duplicate hashing** — too fuzzy to build reliably within a one-day build
- **OCR for handwritten or scanned forms** — the system works on typed/text-extractable input
- **Final approval or rejection authority** — by design, the system never holds this; a human always does

---

## Success Criteria

- All five hackathon non-negotiable checkpoints pass
- CI is green on every push to `main`
- Every routing decision in the audit log has a corresponding, human-readable reason
- No AI-generated summary ever states a fact the structured pipeline data doesn't support
