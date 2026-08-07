# Constitution — Form Review Agent

## Mission
Build a reliable, auditable, human-in-the-loop form processing agent that extracts data from messy form text, verifies completeness and consistency, scores risk, and routes applications for human approval.

## Non-Negotiable Principles

1. **Human stays in control**  
   No critical decision (approve / reject) is ever made automatically without a clear “Ready for Approval” or “Needs Review” flag.

2. **Everything is traceable**  
   Every extraction, verification, and routing decision must be logged with a timestamp and reason.

3. **No hallucinations**  
   If the model is unsure about a field, it must return `None` / empty and record the uncertainty. Never invent values.

4. **Small, testable units**  
   Every function is pure where possible, has type hints, docstrings, and at least one unit test.

5. **Fail safe**  
   When in doubt, route to “Needs Review”. Prefer false positives over silent errors.

6. **Architecture for change**  
   The three modules (extraction → verification → routing) must remain loosely coupled so a Day-2 surprise requirement can be added without breaking existing behaviour.

## Decision Hierarchy
1. Constitution (this file)
2. AGENTS.md + AGENTS_AND_SKILLS.md
3. Architecture document
4. Individual function specifications

## Success Criteria
- All five hackathon checkpoints pass
- Green CI on every push
- Live demo can process a clean form, a missing-field form, and a mismatched form
- Full audit trail is visible for any application ID
