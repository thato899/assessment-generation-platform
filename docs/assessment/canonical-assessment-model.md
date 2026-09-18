# Canonical assessment model

The assessment definition is the source of truth for three future views: question content, learner content with semantic response space, and the memorandum. A `QuestionPart` has a stable `QuestionPartId`, prompt, maximum marks, `ResponseSpecification`, machine-readable `ExpectedAnswer`, and machine-readable `MarkingScheme`.

```text
Assessment definition
  └─ Question
      └─ QuestionPartId
          ├─ ResponseSpecification
          ├─ ExpectedAnswer
          └─ MarkingScheme

LearnerSubmission ── LearnerResponse ──> QuestionPartId
Marking            ── MarkingResult  ──> QuestionPartId
Memorandum         ── MemoEntry      ──> QuestionPartId
```

Response specifications describe learner intent (kind, semantic working space, fields, and unit expectations), not correctness. Expected answers represent typed answer data without performing subject-specific evaluation. Marking criteria are declarative and their marks must total the question-part maximum. Learner responses and marking results are separate immutable aggregates and cannot mutate authored assessment definitions.

The first implementation supports short/long text, numeric, calculation, choice, equation, drawing, graph, and table response kinds; typed text, numeric, choice, calculation, and equation answer kinds; and unmarked, auto-marked, requires-review, and manually-marked result states. Subject-specific markers and PDF/HTML/LMS adapters remain outside the core.
