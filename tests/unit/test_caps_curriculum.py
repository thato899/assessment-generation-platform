import pytest

from assessment_platform.core import Grade, Subject
from assessment_platform.curriculum.caps import (
    CAPS,
    WORK_ENERGY_POWER_TOPIC_ID,
    CapsCurriculum,
    get_caps_physical_sciences,
)


def test_grade_12_physical_sciences_topics_are_complete_and_ordered() -> None:
    curriculum = get_caps_physical_sciences()
    grade_12_topics = curriculum.topics_for(Grade(12), Subject("physical-sciences"))
    assert [topic.identifier for topic in grade_12_topics] == [
        "momentum-and-impulse", "vertical-projectile-motion-1d", "work-energy-and-power"
    ]
    assert all(topic.reference.grade == Grade(12) for topic in grade_12_topics)
    assert all(
        topic.reference.subject == Subject("physical-sciences") for topic in grade_12_topics
    )


def test_newtons_laws_is_a_grade_11_topic_with_grade_12_assessment_relevance() -> None:
    topic = get_caps_physical_sciences().topic("newtons-laws")
    assert topic.reference.grade == Grade(11)
    assert topic.reference.subject == Subject("physical-sciences")
    assert "Newton's first, second and third laws" in topic.concepts
    assert (
        "Grade 11 core instruction" in topic.assessment_metadata
    )
    assert (
        "Grade 12 consolidation" in topic.assessment_metadata
    )
    assert (
        "selected Grade 11 content examinable in the Grade 12 final examination"
        in topic.assessment_metadata
    )


def test_vertical_projectile_topic_contains_caps_constraints() -> None:
    topic = get_caps_physical_sciences().topic("vertical-projectile-motion-1d")
    assert topic.domain.identifier == "mechanics"
    assert "near the surface of the Earth" in topic.constraints
    assert "in the absence of air friction" in topic.constraints
    assert "equations and graphs" in topic.concepts[0]


def test_work_energy_power_topic_has_stable_grade_12_caps_contract() -> None:
    curriculum = get_caps_physical_sciences()
    topic = curriculum.topic(WORK_ENERGY_POWER_TOPIC_ID)

    assert WORK_ENERGY_POWER_TOPIC_ID == "work-energy-and-power"
    assert topic.identifier == WORK_ENERGY_POWER_TOPIC_ID
    assert topic.reference.curriculum == CAPS
    assert topic.reference.grade == Grade(12)
    assert topic.reference.subject == Subject("physical-sciences")
    assert topic.reference.topic.value == WORK_ENERGY_POWER_TOPIC_ID
    assert topic.domain.identifier == "mechanics"
    assert {
        "work as a scalar quantity",
        "individual work contributions and scalar net work",
        "work-energy theorem",
        "conservative and non-conservative forces",
        "mechanical-energy conservation when only conservative forces act",
        "power as the rate of doing work",
        "constant-speed rough horizontal and inclined-plane power",
        "minimum power to pump water from a borehole",
    }.issubset(topic.concepts)
    assert {
        "Grade 12 Physics Mechanics Work, Energy & Power in Term 2",
        "work is scalar and net work is the scalar sum of individual contributions",
        "horizontal and inclined planes, both frictionless and rough",
        "constant-speed power on rough horizontal and inclined planes",
        "minimum electric-motor power for a borehole depth and pumping rate",
    }.issubset(topic.constraints)
    assert topic.assessment_metadata == (
        "Grade 12", "Physics", "Mechanics", "Term 2", "10 hours"
    )


def test_work_energy_power_has_no_alias_and_preserves_topic_order() -> None:
    curriculum = get_caps_physical_sciences()
    grade_12 = curriculum.topics_for(Grade(12), Subject("physical-sciences"))

    assert [topic.identifier for topic in grade_12] == [
        "momentum-and-impulse", "vertical-projectile-motion-1d", WORK_ENERGY_POWER_TOPIC_ID
    ]
    with pytest.raises(KeyError, match="unknown CAPS"):
        curriculum.topic("work-energy-power")


def test_lookup_is_deterministic_and_unknown_topics_fail() -> None:
    curriculum = get_caps_physical_sciences()
    assert curriculum.topic("momentum-and-impulse") is curriculum.topic("momentum-and-impulse")
    with pytest.raises(KeyError, match="unknown CAPS"):
        curriculum.topic("not-a-caps-topic")


def test_subject_and_grade_filtering_rejects_mismatches() -> None:
    curriculum = get_caps_physical_sciences()
    assert [topic.identifier for topic in curriculum.topics_for(
        Grade(11), Subject("physical-sciences")
    )] == ["newtons-laws"]
    assert curriculum.topics_for(Grade(12), Subject("mathematics")) == ()


def test_curriculum_rejects_duplicate_identifiers() -> None:
    topics = get_caps_physical_sciences().topics
    with pytest.raises(ValueError, match="unique"):
        CapsCurriculum((topics[0], topics[0]))
