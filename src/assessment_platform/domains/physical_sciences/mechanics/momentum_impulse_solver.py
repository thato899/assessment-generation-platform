"""Deterministic calculation and validation for Momentum & Impulse scenarios."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from assessment_platform.core import GenerationSeed, ValidationResult
from assessment_platform.domains.physical_sciences.mechanics.momentum_impulse import (
    Impulse,
    Momentum,
    MomentumBody,
    MomentumScenario,
    PositiveAxis,
)

SOLVER_ID = "caps-grade-12-momentum-impulse-solver"
SOLVER_VERSION = "1"
VALIDATION_TOLERANCE = 1e-9


def _identifier(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True, slots=True)
class BodyMomentumResult:
    """The signed initial momentum derived for one scenario body."""

    body_identifier: str
    momentum: Momentum

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "body_identifier", _identifier(self.body_identifier, "body identifier")
        )
        if not isinstance(self.momentum, Momentum):
            raise ValueError("body momentum must be Momentum")


@dataclass(frozen=True, slots=True)
class MomentumImpulseSolution:
    """Typed aggregate results derivable from one initial-state scenario.

    The solution intentionally has no final body velocities. Conservation of
    total momentum alone cannot determine those velocities for a general
    multi-body collision.
    """

    scenario_identifier: str
    body_momenta: tuple[BodyMomentumResult, ...]
    initial_total_momentum: Momentum
    external_impulse: Impulse
    final_total_momentum: Momentum
    positive_axis: PositiveAxis
    seed: GenerationSeed | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "scenario_identifier",
            _identifier(self.scenario_identifier, "scenario identifier"),
        )
        body_momenta = tuple(self.body_momenta)
        if not body_momenta or any(
            not isinstance(result, BodyMomentumResult) for result in body_momenta
        ):
            raise ValueError("solution must contain BodyMomentumResult values")
        identifiers = tuple(result.body_identifier for result in body_momenta)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("solution body identifiers must be unique")
        object.__setattr__(self, "body_momenta", body_momenta)
        if not isinstance(self.initial_total_momentum, Momentum):
            raise ValueError("initial_total_momentum must be Momentum")
        if not isinstance(self.external_impulse, Impulse):
            raise ValueError("external_impulse must be Impulse")
        if not isinstance(self.final_total_momentum, Momentum):
            raise ValueError("final_total_momentum must be Momentum")
        if not isinstance(self.positive_axis, PositiveAxis):
            raise ValueError("positive_axis must be explicit")
        if self.seed is not None and not isinstance(self.seed, GenerationSeed):
            raise ValueError("solution seed must be a GenerationSeed")


class MomentumImpulseSolver:
    """Calculate only the uniquely derivable Momentum & Impulse quantities."""

    def __init__(self, scenario: MomentumScenario) -> None:
        if not isinstance(scenario, MomentumScenario):
            raise ValueError("scenario must be a MomentumScenario")
        self.scenario = scenario

    def solve(self) -> MomentumImpulseSolution:
        body_momenta = tuple(
            BodyMomentumResult(body.identifier, self._body_momentum(body))
            for body in self.scenario.bodies
        )
        initial_total = Momentum(sum(result.momentum.value for result in body_momenta))
        external_impulse = self.scenario.system.external_impulse or Impulse(0.0)
        final_total = Momentum(initial_total.value + external_impulse.value)
        return MomentumImpulseSolution(
            scenario_identifier=self.scenario.identifier,
            body_momenta=body_momenta,
            initial_total_momentum=initial_total,
            external_impulse=external_impulse,
            final_total_momentum=final_total,
            positive_axis=self.scenario.positive_axis,
            seed=self.scenario.seed,
        )

    def validate(self, solution: MomentumImpulseSolution) -> ValidationResult:
        """Validate independent physical and structural solution invariants."""

        errors: list[str] = []
        if not isinstance(solution, MomentumImpulseSolution):
            return ValidationResult(False, ("solution must be a MomentumImpulseSolution",))
        if solution.scenario_identifier != self.scenario.identifier:
            errors.append("solution scenario identifier does not match the scenario")
        if solution.positive_axis is not self.scenario.positive_axis:
            errors.append("solution positive axis does not match the scenario")
        if solution.seed != self.scenario.seed:
            errors.append("solution seed does not match the scenario")
        if any(
            not isfinite(result.momentum.value) for result in solution.body_momenta
        ) or not all(
            isfinite(value)
            for value in (
                solution.initial_total_momentum.value,
                solution.external_impulse.value,
                solution.final_total_momentum.value,
            )
        ):
            errors.append("solution values must be finite")

        expected_body_ids = tuple(body.identifier for body in self.scenario.bodies)
        actual_body_ids = tuple(result.body_identifier for result in solution.body_momenta)
        if actual_body_ids != expected_body_ids:
            errors.append("solution body identifiers do not match the scenario")
        expected_by_id = {
            body.identifier: self._body_momentum(body) for body in self.scenario.bodies
        }
        for result in solution.body_momenta:
            expected = expected_by_id.get(result.body_identifier)
            if expected is None or not self._close(result.momentum.value, expected.value):
                errors.append(f"body momentum is invalid for {result.body_identifier}")

        expected_initial = sum(expected.value for expected in expected_by_id.values())
        if not self._close(solution.initial_total_momentum.value, expected_initial):
            errors.append("initial total momentum does not equal the signed body sum")

        expected_impulse = self.scenario.system.external_impulse or Impulse(0.0)
        if not self._close(solution.external_impulse.value, expected_impulse.value):
            errors.append("external impulse does not match the system boundary")
        expected_final = expected_initial + expected_impulse.value
        if not self._close(solution.final_total_momentum.value, expected_final):
            errors.append("final total momentum does not match impulse change")
        if (
            self.scenario.system.isolated
            and not self._close(solution.final_total_momentum.value, expected_initial)
        ):
            errors.append("isolated-system total momentum is not conserved")
        return ValidationResult(not errors, tuple(errors))

    @staticmethod
    def _body_momentum(body: MomentumBody) -> Momentum:
        return Momentum(body.mass.value * body.initial_velocity.value)

    @staticmethod
    def _close(first: float, second: float) -> bool:
        return isfinite(first) and isfinite(second) and abs(first - second) <= VALIDATION_TOLERANCE
