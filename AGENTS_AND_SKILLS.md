# Agents and Skills

This document describes the custom AI agent and custom skill built for this
project, as required by the hackathon's non-negotiable checklist.

## Custom Agent: Form Validator Agent

**Purpose:**
A Cline agent configuration focused specifically on validating extracted
form data — checking completeness and consistency — rather than acting as
a generic coding assistant.

**What it does:**
Given a structured fields dictionary (output of `extract_fields`), the
agent reasons about whether the data is complete and internally
consistent, and produces a structured explanation of any issues found
(missing fields, format problems, suspicious values) before the rule-based
checks in `verification.py` and `routing.py` run.

**How it's invoked:**
Used during development inside Cline to help build and refine the
validation logic in `app/verification.py` and `app/routing.py` — instructed
via `constitution.md` to always explain *why* a field looks wrong, never to
silently auto-correct or auto-approve.

**Where it's defined:**
`.clinerules` / `constitution.md` — sets the rules this agent follows
(e.g. "never auto-approve a flagged case," "always cite the specific field
and reason for a flag").

## Custom Skill: Cross-Document Matcher

**Purpose:**
A reusable skill for comparing shared fields (name, date of birth) across
two extracted documents and producing a clear, human-readable mismatch
report.

**What it does:**
Takes two field dictionaries (e.g. application form output and ID proof
output) and returns a list of mismatches, each with the specific
conflicting values shown — for example:
`"Name mismatch: form says 'Krishu Sharma', ID says 'Krishu S.'"`

**Where it lives in code:**
`app/verification.py` → `cross_check_documents(fields_dict_1, fields_dict_2)`

**Sample input/output:**

Input:
```json
{"name": "Krishu Sharma", "date_of_birth": "2004-05-01"}
{"name": "Krishu S.", "date_of_birth": "2004-05-01"}
```

Output:
```json
[
  {
    "field": "name",
    "form_value": "Krishu Sharma",
    "id_value": "Krishu S.",
    "status": "mismatch"
  }
]
```

## Why These Count as "Custom"

Both go beyond a generic AI coding assistant prompt: the agent is
constrained by project-specific rules (never auto-approve, always explain
flags) documented in `constitution.md`, and the skill implements
domain-specific logic (cross-document field matching with structured
mismatch output) that is reused across the pipeline rather than a one-off
script.
