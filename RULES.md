# Engineering rules

Use SOLID, DRY, KISS, YAGNI, separation of concerns, dependency inversion, composition, explicit domain boundaries, cohesive modules, meaningful names, and no dead code or unexplained magic numbers.

Domain logic must not depend on the web framework. API code must not calculate subject results. Renderers consume scenario data and never invent values. Solvers do not depend on renderers. Curriculum rules are separate from presentation, and integrations are adapters.

Deterministic solvers are authoritative. Units, sign conventions, rounding, and seeds are explicit. Invalid scenarios are rejected. Tests cover domain behaviour, API contracts, reproducibility, invalid inputs, and valuable properties.

No secrets in source control; validate input; use least privilege and safe errors. Document authentication and rate limiting before production. Public API and architectural changes require documentation and ADRs.

Use feature branches, focused conventional commits (`type(scope): summary`), linked PRs, and no unrelated changes.
