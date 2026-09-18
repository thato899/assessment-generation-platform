# Security

Do not commit secrets. Report vulnerabilities privately through GitHub Security Advisories when enabled; do not open a public issue with exploitable details. API inputs are schema-validated and errors should not expose internals. Dependency review, Dependabot, CodeQL, and secret scanning are configured/planned through repository settings and workflow. Authentication, authorization, rate limiting, audit logging, and tenant isolation are production prerequisites and are intentionally deferred from M0.
