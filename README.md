# 📄 DocDesk — AI Form & Document Review Agent

**Deploy or Die — HowToAlgo x GDG on Campus KIIT Hackathon**
**Track A: Business Process Automation**

> Know exactly which documents you need — before you queue up.

DocDesk is an agent-driven system that takes a government/institutional application (Aadhaar, PAN, Passport, Bank Account Opening, Driving License, Voter ID, and more) along with its supporting documents, extracts the required fields, detects missing information, cross-checks details across documents, calculates a risk score, and routes incomplete or suspicious cases to a human reviewer — with every decision logged and fully traceable.

The agent never approves or rejects on its own. It flags, explains, and routes. A human always makes the final call.

---

## 🎯 The Problem

Manual processing of government scheme, subsidy, and institutional forms is slow, inconsistent, and error-prone. Genuinely eligible applicants are frequently rejected or delayed — not because they're actually ineligible, but because a document was missing, mismatched, or expired. This is a real, large-scale, unsolved operational problem, not an invented hackathon scenario.

---

## ✨ Core Features

| Feature | Description |
|---|---|
| **Field Extraction** | Extracts structured fields (name, DOB, ID number, address, income, category) from raw form/document text |
| **Missing Field Detector** | Checks extracted data against a required-fields checklist for the selected document category |
| **Cross-Document Verification** | Compares fields across multiple uploaded documents and flags mismatches with the exact discrepancy |
| **Risk Scoring & Routing** | Scores each application (low / medium / high risk) and routes it to "Ready for Approval" or "Needs Review" with a clear reason |
| **Decision & Audit Log** | Every action — auto-flag, human approve/reject/resubmit — is logged with a timestamp, giving a full traceable history per application |
| **Security Layer** | Uploaded files are encrypted at rest (Fernet/AES), renamed to random tokens (no path traversal / filename leaks), and all API routes require key-based access control |
| **PII-Safe Logging** | Logs automatically redact Aadhaar, PAN, phone, and email patterns before anything is written to disk |

---

## 🖥️ Frontend

A lightweight web UI lets a user:
1. Pick a document category (Aadhaar, PAN, Passport, Bank Account, Driving License, Voter ID)
2. See the official checklist of required documents for that category
3. Upload proofs (PDF / JPG / PNG, up to 10 MB)
4. Run an instant completeness + risk review

A **"Play the demo"** mode is available with sample files, so reviewers can try the full flow without uploading anything real.

---

## 🏗️ Architecture 
Full design decisions and reasoning are documented in [`ARCHITECTURE.md`](./ARCHITECTURE.md).

---

## 🤖 Custom Agent & Skill

| Type | Name | Purpose |
|---|---|---|
| **Custom Agent** | Form Field Extractor | Reads raw, messy document text and returns structured field data |
| **Custom Skill** | Cross-Document Verifier | Compares field values across two or more documents and flags mismatches with human-readable reasons |

Full documentation: [`AGENTS_AND_SKILLS.md`](./AGENTS_AND_SKILLS.md)

Agent behavior rules and coding conventions: [`.clinerules`](./.clinerules) / [`AGENTS.md`](./AGENTS.md) / [`constitution.md`](./constitution.md)

---

## 🛠️ Tech Stack

- **Language:** Python 3.11+
- **Coding Agent:** Cline (VS Code)
- **AI Backend:** NVDIA BUILD 
- **Security:** `cryptography` (Fernet/AES encryption)
- **Config:** `python-dotenv`, `pydantic`
- **Testing:** `pytest`
- **CI/CD:** GitHub Actions

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
Create a `.env` file in the project root (never commit this file):
NVDIA API KEY- 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
### 4. Run the backend pipeline
```bash
python main.py
```
This runs 3 sample cases (clean, missing-field, mismatch) through the full pipeline and prints the results.

### 5. Run the tests
```bash
pytest -v
```

---

## ✅ Testing

The test suite covers:
- Clean/complete applications
- Applications with missing required fields
- Applications with cross-document mismatches
- Empty/garbage input handling
- Security module round-trip encryption/decryption

Run locally before every push:
```bash
pytest -v
```

CI runs the full suite automatically on every push via [`.github/workflows/ci.yml`](./.github/workflows/ci.yml).

---

## 🔒 How Files Are Protected

- **Encryption at rest** — every uploaded file is encrypted with Fernet/AES before it touches disk
- **No original filenames** — uploads are renamed to a random token to prevent path traversal or metadata leaks
- **API key access control** — every API route requires an `X-API-Key` header, verified with a constant-time comparison
- **PII-safe logging** — the logger auto-redacts Aadhaar, PAN, phone, and email patterns before writing logs
- **Upload validation** — only PDF, JPG, and PNG accepted, capped at 10 MB

---

## 🗺️ Roadmap / Planned Enhancements

These are intentionally scoped **out** of the current MVP to keep the hackathon build reliable and testable, but are the natural next steps:

- **Auto expiry-date detection** — for documents like Passport or Driving License, extract the expiry date during processing and automatically flag "expires in 20 days" or reject if already expired, without requiring manual review
- **Auto status notifications** — when an application flips from "Incomplete" to "Complete," or its risk score changes, automatically fire an email/webhook notification instead of requiring the applicant to manually check status
- **Duplicate-upload / fraud detection** — hash every uploaded file (SHA-256) before storing it; if the same file hash appears under a different application ID, automatically flag it as possible document reuse or fraud

We deliberately did not build fraud/suspicious-pattern detection or OCR for handwritten forms in the MVP — these require more validation time than a one-day build allows, and are documented here as honest, known limitations rather than left unaddressed.

---

## 👥 Team

Built by a 4-person team for the Deploy or Die hackathon, split across:
- **Field Extraction**
- **Missing Field & Cross-Document Verification**
- **Risk Scoring, Routing & Audit Logging**
- **CI/CD, Security, Frontend & Documentation**

---

## 📄 License

Built for educational/hackathon purposes as part of Deploy or Die — HowToAlgo x GDG on Campus KIIT.
