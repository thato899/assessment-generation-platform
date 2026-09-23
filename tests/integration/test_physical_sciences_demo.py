import pytest

from assessment_platform.application.physical_sciences_demo import (
    MOMENTUM_TOPIC_ID,
    NEWTON_TOPIC_ID,
    SUPPORTED_DEMO_TOPICS,
    VERTICAL_PROJECTILE_TOPIC_ID,
    WORK_ENERGY_POWER_TOPIC_ID,
    PhysicalSciencesDemoRequest,
    generate_demo,
)


@pytest.mark.parametrize("topic", SUPPORTED_DEMO_TOPICS)
def test_demo_runs_the_complete_pipeline_for_each_supported_topic(topic: str) -> None:
    result = generate_demo(PhysicalSciencesDemoRequest(topic=topic, seed=42))

    assert result["request"]["topic"] == topic
    assert result["effective_seed"] == 42
    learner = result["learner"]
    teacher_memo = result["teacher_memo"]
    assert learner["questions"]
    assert teacher_memo
    assert tuple(entry["question_part_id"] for entry in teacher_memo) == tuple(
        part["question_part_id"] for part in learner["questions"][0]["parts"]
    )


@pytest.mark.parametrize("topic", SUPPORTED_DEMO_TOPICS)
def test_demo_is_deterministic_and_separates_learner_from_teacher_data(topic: str) -> None:
    request = PhysicalSciencesDemoRequest(topic=topic, seed=42, include_visuals=False)
    first = generate_demo(request)
    second = generate_demo(request)

    assert first == second
    forbidden = {
        "expected_answer",
        "marking_scheme",
        "worked_solution",
        "memorandum",
        "scenario",
        "solution",
        "rubric",
        "provenance",
        "solver",
    }

    def keys(value: object):
        if isinstance(value, dict):
            yield from value.keys()
            for child in value.values():
                yield from keys(child)
        elif isinstance(value, list):
            for child in value:
                yield from keys(child)

    assert not forbidden & set(keys(first["learner"]))
    assert first["teacher_memo"]


def test_demo_request_uses_exact_grade_routes() -> None:
    assert PhysicalSciencesDemoRequest(NEWTON_TOPIC_ID).grade == 11
    assert PhysicalSciencesDemoRequest(VERTICAL_PROJECTILE_TOPIC_ID).grade == 12
    assert PhysicalSciencesDemoRequest(MOMENTUM_TOPIC_ID).grade == 12
    assert PhysicalSciencesDemoRequest(WORK_ENERGY_POWER_TOPIC_ID).grade == 12


@pytest.mark.parametrize("topic", ("mathematics", "newtons-laws-unsupported"))
def test_demo_rejects_unsupported_topics(topic: str) -> None:
    with pytest.raises(ValueError, match="not supported"):
        PhysicalSciencesDemoRequest(topic=topic)


def test_demo_validates_seed_and_difficulty() -> None:
    with pytest.raises(ValueError):
        PhysicalSciencesDemoRequest(topic=NEWTON_TOPIC_ID, seed=-1)
    with pytest.raises(ValueError, match="difficulty"):
        PhysicalSciencesDemoRequest(
            topic=NEWTON_TOPIC_ID,
            difficulty="impossible",  # type: ignore[arg-type]
        )
