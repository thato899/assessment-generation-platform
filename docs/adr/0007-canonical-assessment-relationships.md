# ADR 0007: Stable question-part relationships

Status: accepted. Canonical assessment authoring data owns stable `QuestionPartId` values and typed response, answer, and marking definitions. Memorandum entries are derived from the authored question parts rather than maintained as a separately keyed document. Learner responses and marking results reference the same ID explicitly. This keeps renderers, LMS adapters, and future markers independent of display order and presentation geometry.
