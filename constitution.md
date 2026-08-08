# Constitution — Form Review Agent

*The governing principles our AI agents and our team follow while building and operating this system.*

---

## Mission

Build a reliable, auditable, human-in-the-loop form processing agent that extracts data from messy application text, verifies its completeness and consistency, scores risk, and routes every application for human approval — never for automated final judgment.

---

## Non-Negotiable Principles

### 1. Human stays in control
No critical decision — approve or reject — is ever made automatically. The system's only outputs are a **"Ready for Approval"** or **"Needs Review"** flag, each with a clear reason. The human reviewer makes every final call.

### 2. Everything is traceable
Every extraction, verification, and routing decision is logged with a timestamp and a reason. Nothing happens silently. A reviewer — or a judge — can reconstruct exactly how and why any decision was reached.

### 3. No hallucinations
If a field cannot be confidently determined from the source text, the system returns `None` and records the uncertainty. It never invents, guesses, or fills in a plausible-sounding value.

### 4. Small, testable units
Every function is pure where possible, carries type hints and a docstring, and ships with at least one unit test. Complexity lives in composition, not in individual functions.

### 5. Fail safe
When in doubt, the system routes to **"Needs Review."** A false positive costs a reviewer two minutes; a silent false negative costs an applicant their eligibility. We optimize for the former.

### 6. Architecture for change
The three core modules — **extraction → verification → routing** — remain loosely coupled by design, communicating only through a well-defined data contract. This lets a Day-2 surprise requirement be added without breaking existing behavior.

### 7. Verification, not assumption
An uploaded document proves nothing on its own. Every uploaded proof must have its extracted fields cross-checked against the rest of the application using the same `cross_check_documents()` logic already applied between documents. The system verifies *what was uploaded matches the application* — not merely *that something was uploaded.*

### 8. AI assists the reviewer; it never replaces the evidence
Any AI-generated natural-language summary shown to a reviewer — e.g. *"All 4 required documents present. DOB matches across documents. Risk: low."* — is a convenience layer generated **from** the system's structured flags, mismatches, and risk score. It is never an independent source of truth, and it must never state a claim the structured data doesn't already support.

---

## Decision Hierarchy

When principles conflict or a new case isn't covered, resolve in this order:

1. **This Constitution**
2. `AGENTS.md` + `AGENTS_AND_SKILLS.md`
3. `ARCHITECTURE.md`
4. Individual function specifications

---

## Planned Extensions

*Documented transparently as roadmap — not yet implemented, and not claimed as built.*

**Auto cross-check on upload**
Wire `extraction.py`'s `extract_fields()` directly into the upload flow, so the moment a user uploads a "Proof of Identity" document, its name and DOB are extracted and immediately cross-checked against the rest of the application via `verification.py`'s `cross_check_documents()`. This turns document upload from a presence check into a correctness check, in real time.

**AI-generated review summary**
Once all required documents for an application are present, the AI backend generates a single, human-readable summary paragraph for the reviewer — built strictly from already-computed structured results, per Principle 8 — replacing the need to read raw JSON output.

Both extensions extend existing modules rather than requiring new architecture, in keeping with Principle 6.

---

## Success Criteria

- All five hackathon non-negotiable checkpoints pass
- CI is green on every push to `main`
- Every routing decision in the audit log has a corresponding, human-readable reason
