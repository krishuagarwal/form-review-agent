# AGENTS.md — Form Review Agent

## Overview
This repository uses a multi-agent style workflow driven by Cline (or compatible coding agents).  
Each agent has a clear responsibility corresponding to the three core modules.

---

### Agent 1: Extraction Agent
**File**: `app/extraction.py`  
**Responsibility**:  
Take raw text from a PDF/form and intelligently extract structured fields.

**Key Function**:
```python
def extract_fields(text: str) -> dict[str, str | None]
