# Assessment Generation Platform

An independent, open-source platform for deterministic, curriculum-aware assessment generation for South African education. The initial curriculum is CAPS, with Physical Sciences first and Mathematics second.

## Status

M2 Vertical Projectile Motion is implemented, M3 Momentum & Impulse is complete, and M4 Newton's Laws has completed implementation and final verification pending merge of PR #72. The public v1 API supports the approved deterministic Physical Sciences routes for vertical projectile motion, Momentum & Impulse, and Grade 11 Newton's Laws. M5 Work, Energy & Power is next; Mathematics remains later in the roadmap. See [STATUS.md](STATUS.md) and [PLANNING.md](PLANNING.md) for the current milestone details.

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
