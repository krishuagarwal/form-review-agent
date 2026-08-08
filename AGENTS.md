# AGENTS.md — Form Review Agent (DocDesk)

*Rules and conventions for any AI coding agent (Cline, Roo Code, or similar) working in this repository.*

---

## 1. Purpose of This File

This file tells an AI coding agent how to behave while working on this codebase — what to build, how to build it, and what to never do. It sits below the [Constitution](./constitution.md) in our decision hierarchy and applies to every file, every commit, and every session.

---

## 2. Project Context

DocDesk is a human-in-the-loop form/document review agent. It extracts fields from application documents, checks completeness, cross-checks details across documents, scores risk, and routes applications to a human reviewer. **The agent never makes a final approve/reject decision.**

---

## 3. Core Coding Rules

1. **Every function must have type hints and a docstring.** No exceptions, including test helper functions.
2. **Every new function must ship with at least one unit test** in the corresponding `tests/` file, covering both a normal case and an edge case.
3. **Never guess a value.** If a field can't be confidently extracted or verified, return `None` — do not invent a plausible-sounding value.
4. **Never make functions impure without reason.** Prefer functions that take inputs and return outputs over functions that silently read/write global state.
5. **Keep functions small and single-purpose.** If a function is doing more than one clearly describable thing, split it.
6. **Never hardcode secrets, API keys, or credentials** in any file. All secrets come from environment variables via `.env` (which is git-ignored).
7. **Match the existing data contract exactly.** Any function producing or consuming extracted fields must use exactly these keys: `name`, `dob`, `id_number`, `address`, `income`, `category`. Do not rename, add, or remove keys without updating this file and `ARCHITECTURE.md` first.
8. **Prefer deterministic logic over live AI calls inside core decision functions** (extraction, verification, risk scoring). AI calls are reserved for generating human-readable summaries *from* already-computed structured data — never for producing the structured data or the routing decision itself.
9. **Log, don't silently fail.** Any error, uncertainty, or fallback path must be logged with a clear reason — see `routing.py`'s `log_decision()`.
10. **When in doubt, fail toward "Needs Review," never toward silent approval.**

---

## 4. File & Module Ownership

| File | Owns |
|---|---|
| `app/extraction.py` | Field extraction (Custom Agent: Form Field Extractor) |
| `app/verification.py` | Missing field checks + cross-document checks (Custom Skill: Cross-Document Verifier) |
| `app/routing.py` | Risk scoring, routing, decision logging, audit history |
| `app/security.py` | Encryption, file handling, API key auth, PII-safe logging |
| `main.py` | End-to-end pipeline orchestration |
| `tests/` | One test file per module, mirroring the same filename |

**An agent working on one module should not modify another module's file** unless explicitly asked to, and should always mention if a change in one file requires a corresponding change elsewhere (e.g. a new field added to the data contract).

---

## 5. Before Writing Any Code

An agent must first:
1. Confirm the exact function signature and inputs/outputs being asked for
2. Confirm which existing keys/contracts the new code must match
3. Propose a plan (files to create/edit) and wait for approval before acting — this is our human-in-the-loop checkpoint, not optional

---

## 6. After Writing Code

An agent should:
1. Explain what was created/changed, in plain language
2. Confirm tests were included and what they cover
3. Never claim something "works" without the tests actually having been run

---

## 7. Testing & CI Requirements

- All tests must pass locally via `pytest` before a commit is suggested
- Tests must be deterministic — no test should depend on live AI model output that could vary between runs
- CI (`.github/workflows/ci.yml`) runs the full suite on every push; an agent should never suggest a commit expected to break CI

---

## 8. Git Conventions

- Commit messages are short, specific, and describe *what* changed (e.g. `"add missing field detection with edge case tests"`, not `"update code"` or `"fix stuff"`)
- One logical change per commit where practical
- Never commit `.env`, encryption keys, or any file listed in `.gitignore`

---

## 9. What This Agent Must Never Do

- Never make the final approve/reject decision on an application — only flag and route
- Never fabricate a field value, a test result, or a claim about what code does
- Never remove or weaken a test to make CI pass
- Never introduce a new dependency without adding it to `requirements.txt`
- Never bypass the security layer (encryption, API key checks) for convenience, even temporarily

---

## 10. Related Documents

- [`constitution.md`](./constitution.md) — the governing principles behind these rules
- [`AGENTS_AND_SKILLS.md`](./AGENTS_AND_SKILLS.md) — documentation of our custom agent and custom skill
- [`ARCHITECTURE.md`](./ARCHITECTURE.md) — full system design and data flow
- [`.clinerules`](./.clinerules) — Cline-specific behavioral configuration
