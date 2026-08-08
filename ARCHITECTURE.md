# 📄 DocDesk — AI Form & Document Review Agent

**Deploy or Die — HowToAlgo x GDG on Campus KIIT Hackathon**
**Track A: Business Process Automation**

> Know exactly which documents you need — before you queue up.

DocDesk is an agent-driven system that takes a government/institutional application (Aadhaar, PAN, Passport, Bank Account Opening, Driving License, Voter ID) along with its supporting documents, and automatically extracts the required fields, detects missing information, cross-checks details across documents, flags expired or duplicate documents, calculates a risk score, and routes incomplete or suspicious cases to a human reviewer — with every decision logged and fully traceable.

**The agent never approves or rejects on its own.** It flags, explains, and routes. A human always makes the final call.

---

## 🎯 The Problem

Manual processing of government scheme, subsidy, and institutional forms is slow, inconsistent, and error-prone. Genuinely eligible applicants are frequently rejected or delayed — not because they're ineligible, but because a document was missing, mismatched, expired, or reused across applications, and nobody caught it early. This is a real, large-scale, unsolved operational problem, not an invented hackathon scenario.

---

## ✨ Core Features

| Feature | Module | Description |
|---|---|---|
| **Field Extraction** | `extraction.py` | Deterministic, rule-based extraction of name, DOB, ID number, address, income, and category from raw document text |
| **Missing Field Detection** | `verification.py` | Checks extracted data against the required-fields checklist for the selected category |
| **Cross-Document Verification** | `verification.py`, `cross_check_engine.py` | Compares fields across every document uploaded for an application and flags mismatches with the exact discrepancy |
| **Duplicate Upload Detection** | `duplicate_detection.py` | Hashes every file (SHA-256) — flags if the same file appears under a different application ID |
| **Expiry Detection** | `expiry_detection.py` | For Passport, Driving License, and Voter ID, flags documents that are expired or expiring within 30 days |
| **Risk Scoring & Routing** | `routing.py` | Scores each application and routes it to "Ready for Approval" or "Needs Review" with a clear reason |
| **AI Review Summary** | `ai_review_summary.py` | Generates a human-readable summary for the reviewer, built strictly from already-computed structured results |
| **Decision & Audit Log** | `routing.py` | Every action is logged with a timestamp, giving a full traceable history per application |
| **Pipeline Orchestration** | `pipeline_integration.py` | Wires every module above into a single end-to-end flow triggered on each upload |
| **Security Layer** | `security.py` | Encrypts files at rest, randomizes stored filenames, enforces API key access, and redacts PII from logs |

---

## 🏗️ Architecture 
Upload (form + documents)
│
▼
Duplicate Check ── flags reused documents across applications
│
▼
Field Extraction + Cross-Document Check ── extracts & compares against
│ everything already on file
▼
Expiry Check ── for Passport / Driving License / Voter ID
│
▼
Risk Scoring & Routing ── Ready for Approval / Needs Review + reason
│
▼
AI Review Summary ── generated from the structured results above,
│ never an independent source of truth
▼
Decision & Audit Log ── timestamped, reasoned, fully traceable 
Full design decisions and trade-offs are documented in [`ARCHITECTURE.md`](./ARCHITECTURE.md).

---

## 🤖 Custom Agent & Skill

| Type | Name | Purpose |
|---|---|---|
| **Custom Agent** | Form Field Extractor | Reads raw, messy document text and returns structured field data |
| **Custom Skill** | Cross-Document Verifier | Compares field values across two or more documents and flags mismatches with human-readable reasons |

Full documentation: [`AGENTS_AND_SKILLS.md`](./AGENTS_AND_SKILLS.md)
Agent behavior rules: [`.clinerules`](./.clinerules) · [`AGENTS.md`](./AGENTS.md) · [`constitution.md`](./constitution.md)

---

## 🛠️ Tech Stack

- **Language:** Python 3.11+
- **Coding Agent:** Cline (VS Code)
- **AI Backend:** Groq / NVIDIA Build (OpenAI-compatible)
- **Security:** `cryptography` (Fernet/AES)
- **Config:** `python-dotenv`, `pydantic`
- **Testing:** `pytest`
- **CI/CD:** GitHub Actions

---

## 📁 Project Structure
form-review-agent/
├── app/
│ ├── init.py
│ ├── extraction.py
│ ├── verification.py
│ ├── routing.py
│ ├── security.py
│ ├── duplicate_detection.py
│ ├── expiry_detection.py
│ ├── cross_check_engine.py
│ ├── ai_review_summary.py
│ └── pipeline_integration.py
├── tests/
│ └── (one test file per module)
├── .github/workflows/ci.yml
├── .clinerules
├── .gitignore
├── AGENTS.md
├── AGENTS_AND_SKILLS.md
├── ARCHITECTURE.md
├── constitution.md
├── main.py
├── requirements.txt
└── README.md 
---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/krishuagarwal/form-review-agent.git
cd form-review-agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file in the project root (this is git-ignored, never commit it): 

NVDIA KEY-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 
### 4. Run the full pipeline
```bash
python main.py
```
This runs sample applications through the complete pipeline — extraction, verification, duplicate check, expiry check, risk scoring, and audit logging — and prints the results.

### 5. Run the tests
```bash
pytest -v
```

---

## ✅ Testing

The test suite covers, per module:
- A clean/complete case
- A missing-field or edge case
- Invalid/empty input handling
- Security round-trip encryption/decryption
- Duplicate detection across applications
- Expiry status (valid / expiring soon / expired / unknown)
- AI summary generation from structured data

Run locally before every push:
```bash
pytest -v
```

CI runs the full suite automatically on every push via [`.github/workflows/ci.yml`](./.github/workflows/ci.yml). All modules are fully deterministic — no test depends on live AI output or network access, so CI results are reliable and reproducible every time.

---

## 🔒 How Files Are Protected

- **Encryption at rest** — every uploaded file is encrypted with Fernet/AES before it touches disk
- **No original filenames** — uploads are renamed to a random token, preventing path traversal or metadata leaks
- **API key access control** — every route requires an `X-API-Key` header, verified with a constant-time comparison
- **PII-safe logging** — Aadhaar, PAN, phone, and email patterns are auto-redacted before anything is written to logs
- **Upload validation** — only PDF, JPG, and PNG accepted, capped at 10 MB

---

## 🗺️ Roadmap

Documented transparently as planned, not yet built:

1. **Auto notifications** — fire an email/webhook automatically when an application's status changes from "Incomplete" to "Complete," or its risk score changes
2. **Live AI backend for review summaries** — plug a real LLM call into `ai_review_summary.py` (currently template-based by default) for richer natural-language summaries, while keeping the structured data as the source of truth
3. **OCR support** — extend `extraction.py` to handle scanned/handwritten documents, not just typed/text-extractable input

We deliberately did not build general fraud-pattern detection or OCR in the MVP — both require more validation time than a one-day build allows, and are documented here as honest, known limitations rather than left unaddressed.

---

## 👥 Team

Built by a 4-person team for the Deploy or Die hackathon:
- **Field Extraction**
- **Missing Field & Cross-Document Verification**
- **Risk Scoring, Routing & Audit Logging**
- **CI/CD, Security, Pipeline Integration & Documentation**

---

## 📄 License

Built for educational/hackathon purposes as part of Deploy or Die — HowToAlgo x GDG on Campus KIIT.
