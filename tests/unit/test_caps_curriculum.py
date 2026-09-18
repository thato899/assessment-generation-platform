import pytest

from assessment_platform.core import Grade, Subject
from assessment_platform.curriculum.caps import CapsCurriculum, get_caps_physical_sciences


def test_grade_12_physical_sciences_topics_are_complete_and_ordered() -> None:
    curriculum = get_caps_physical_sciences()
    assert [topic.identifier for topic in curriculum.topics] == [
        "momentum-and-impulse", "vertical-projectile-motion-1d", "work-energy-and-power"
    ]
    assert all(topic.reference.grade == Grade(12) for topic in curriculum.topics)
    assert all(
        topic.reference.subject == Subject("physical-sciences") for topic in curriculum.topics
    )


def test_vertical_projectile_topic_contains_caps_constraints() -> None:
    topic = get_caps_physical_sciences().topic("vertical-projectile-motion-1d")
    assert topic.domain.identifier == "mechanics"
    assert "near the surface of the Earth" in topic.constraints
    assert "in the absence of air friction" in topic.constraints
    assert "equations and graphs" in topic.concepts[0]


def test_lookup_is_deterministic_and_unknown_topics_fail() -> None:
    curriculum = get_caps_physical_sciences()
    assert curriculum.topic("momentum-and-impulse") is curriculum.topic("momentum-and-impulse")
    with pytest.raises(KeyError, match="unknown CAPS"):
        curriculum.topic("not-a-caps-topic")


def test_subject_and_grade_filtering_rejects_mismatches() -> None:
    curriculum = get_caps_physical_sciences()
    assert curriculum.topics_for(Grade(11), Subject("physical-sciences")) == ()
    assert curriculum.topics_for(Grade(12), Subject("mathematics")) == ()


def test_curriculum_rejects_duplicate_identifiers() -> None:
    topics = get_caps_physical_sciences().topics
    with pytest.raises(ValueError, match="unique"):
        CapsCurriculum((topics[0], topics[0]))
