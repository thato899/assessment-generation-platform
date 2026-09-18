"""Deterministic kinematics for a validated vertical projectile scenario."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite, sqrt

from assessment_platform.core import ValidationResult
from assessment_platform.domains.physical_sciences.mechanics.vertical_projectile import (
    VerticalProjectileScenario,
)

TIME_TOLERANCE_SECONDS = 1e-9
VALUE_TOLERANCE = 1e-9


@dataclass(frozen=True, slots=True)
class Seconds:
    value: float

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, (int, float)):
            raise ValueError("time must be a number")
        if not isfinite(self.value) or self.value < 0:
            raise ValueError("time must be a finite non-negative number of seconds")
        object.__setattr__(self, "value", float(self.value))


class EventType(StrEnum):
    LAUNCH = "launch"
    MAXIMUM_HEIGHT = "maximum-height"
    RETURN_TO_LAUNCH_POSITION = "return-to-launch-position"
    GROUND_IMPACT = "ground-impact"


@dataclass(frozen=True, slots=True)
class TrajectoryEvent:
    event_type: EventType
    time: Seconds
    position: float
    velocity: float


@dataclass(frozen=True, slots=True)
class VerticalProjectileSolution:
    scenario_identifier: str
    events: tuple[TrajectoryEvent, ...]

    def event(self, event_type: EventType) -> TrajectoryEvent | None:
        return next((event for event in self.events if event.event_type is event_type), None)


class VerticalProjectileSolver:
    """Solve the 1D constant-acceleration relationships without rounding."""

    def __init__(self, scenario: VerticalProjectileScenario) -> None:
        self.scenario = scenario

    def position_at(self, time: Seconds) -> float:
        t = time.value
        return self._position(t)

    def velocity_at(self, time: Seconds) -> float:
        return self.scenario.initial_velocity.value + (
            self.scenario.gravitational_acceleration.value * time.value
        )

    def displacement_over(self, time: Seconds) -> float:
        return self.position_at(time) - self.scenario.launch_position.value

    def solve(self) -> VerticalProjectileSolution:
        launch_time = Seconds(0)
        launch_position = self.scenario.launch_position.value
        launch_velocity = self.scenario.initial_velocity.value
        events = [TrajectoryEvent(EventType.LAUNCH, launch_time, launch_position, launch_velocity)]

        maximum_time = self._maximum_height_time()
        if maximum_time is not None:
            events.append(self._event(EventType.MAXIMUM_HEIGHT, maximum_time))

        return_time = self._positive_root_for_position(launch_position)
        if return_time is not None:
            events.append(self._event(EventType.RETURN_TO_LAUNCH_POSITION, return_time))

        impact_time = self._positive_root_for_position(0.0)
        if impact_time is not None:
            events.append(self._event(EventType.GROUND_IMPACT, impact_time))

        return VerticalProjectileSolution(self.scenario.identifier, tuple(events))

    def validate(self, solution: VerticalProjectileSolution) -> ValidationResult:
        errors: list[str] = []
        if solution.scenario_identifier != self.scenario.identifier:
            errors.append("solution scenario identifier does not match input scenario")
        for event in solution.events:
            if not isfinite(event.time.value) or event.time.value < 0:
                errors.append(f"{event.event_type} has an invalid time")
            expected_position = self._position(event.time.value)
            expected_velocity = self.velocity_at(event.time)
            if abs(event.position - expected_position) > VALUE_TOLERANCE:
                errors.append(f"{event.event_type} position is inconsistent with the scenario")
            if abs(event.velocity - expected_velocity) > VALUE_TOLERANCE:
                errors.append(f"{event.event_type} velocity is inconsistent with the scenario")
            if (
                event.event_type is EventType.MAXIMUM_HEIGHT
                and abs(event.velocity) > VALUE_TOLERANCE
            ):
                errors.append("maximum-height velocity must be approximately zero")
            if (
                event.event_type is EventType.GROUND_IMPACT
                and abs(event.position) > VALUE_TOLERANCE
            ):
                errors.append("ground-impact position must be the reference level")
            if event.event_type is EventType.RETURN_TO_LAUNCH_POSITION and abs(
                event.position - self.scenario.launch_position.value
            ) > VALUE_TOLERANCE:
                errors.append("return position must equal launch position")
        return ValidationResult(not errors, tuple(errors))

    def _position(self, time: float) -> float:
        return (
            self.scenario.launch_position.value
            + self.scenario.initial_velocity.value * time
            + 0.5 * self.scenario.gravitational_acceleration.value * time**2
        )

    def _event(self, event_type: EventType, time: float) -> TrajectoryEvent:
        seconds = Seconds(time)
        return TrajectoryEvent(event_type, seconds, self._position(time), self.velocity_at(seconds))

    def _maximum_height_time(self) -> float | None:
        time = -self.scenario.initial_velocity.value / (
            self.scenario.gravitational_acceleration.value
        )
        return time if time > TIME_TOLERANCE_SECONDS else None

    def _positive_root_for_position(self, target_position: float) -> float | None:
        a = 0.5 * self.scenario.gravitational_acceleration.value
        b = self.scenario.initial_velocity.value
        c = self.scenario.launch_position.value - target_position
        discriminant = b**2 - 4 * a * c
        if discriminant < 0:
            return None
        root = sqrt(max(discriminant, 0.0))
        candidates = ((-b - root) / (2 * a), (-b + root) / (2 * a))
        positive = [candidate for candidate in candidates if candidate > TIME_TOLERANCE_SECONDS]
        return min(positive) if positive else None
