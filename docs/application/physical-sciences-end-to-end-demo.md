# Physical Sciences end-to-end demonstration

The supported Physical Sciences mechanics routes already share the same
application pipeline:

```text
request + seed
    -> deterministic scenario/problem generation
    -> solver-backed or conceptual question generation
    -> canonical Question/Assessment
    -> learner-safe projection
    -> trusted teacher memorandum projection
```

The trusted local demo makes this pipeline visible without adding a memo API
endpoint. It accepts the same request concepts as the v1 generation route and
prints separate `learner` and `teacher_memo` sections. The learner section is
an allowlisted projection; expected answers, marking schemes, rubrics,
solutions, scenarios, provenance, and solver data remain in the teacher-side
section or internal domain object only.

## Run all supported topics

From the repository root:

```bash
python scripts/demo_physical_sciences.py --seed 42 --no-visuals
```

The command produces one deterministic example for:

- `vertical-projectile-motion-1d` (Grade 12);
- `momentum-and-impulse` (Grade 12);
- `newtons-laws` (Grade 11); and
- `work-energy-and-power` (Grade 12).

To include learner-safe SVG assets, omit `--no-visuals`. To demonstrate one
route only, pass `--topic` with one of the identifiers above.

The same seed and request reproduce the same learner question and memorandum.
The web endpoint remains learner-facing only; memorandum data is available
through the trusted application/demo path and is not serialized by
`POST /api/v1/assessments/generate`.
