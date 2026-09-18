# Contributing

Read CODEX.md, RULES.md, STATUS.md, PLANNING.md, and relevant architecture docs first. Create or select a GitHub issue, use a feature branch, make focused conventional commits, and link the PR with `Closes #N` only when acceptance criteria are met.

Run `pip install -e ".[dev]"`, then `pytest`, `ruff check .`, and `mypy`. CI runs the same checks plus build and dependency review. Update documentation and STATUS.md with behaviour changes. Do not add secrets or claim external actions that were not verified.
