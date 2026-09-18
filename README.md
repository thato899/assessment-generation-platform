# Assessment Generation Platform

An independent, open-source platform for deterministic, curriculum-aware assessment generation for South African education. The initial curriculum is CAPS, with Physical Sciences first and Mathematics second.

## Status

The repository is at **M0 — Repository & Architecture Bootstrap**. It contains the versioned FastAPI boundary, health endpoint, request validation, quality tooling, governance documents, and CI foundation. Subject generation is intentionally not implemented yet.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn assessment_platform.main:app --reload
pytest
ruff check .
mypy
```

API documentation is available at `/docs` when the server is running. See [ARCHITECTURE.md](ARCHITECTURE.md), [STATUS.md](STATUS.md), and [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache-2.0 is selected to encourage reuse while preserving explicit patent and attribution protections. A license file will be added before the first release milestone.
