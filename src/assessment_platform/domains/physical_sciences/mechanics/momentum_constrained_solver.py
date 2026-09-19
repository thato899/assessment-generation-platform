"""Deterministic solutions for explicitly constrained two-body interactions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite

from assessment_platform.core import GenerationSeed, ValidationResult
from assessment_platform.domains.physical_sciences.mechanics.momentum_impulse import (
    Impulse,
    KineticEnergy,
    MetresPerSecond,
    Momentum,
    MomentumBody,
    MomentumScenario,
    PositiveAxis,
)
from assessment_platform.domains.physical_sciences.mechanics.momentum_impulse_solver import (
    VALIDATION_TOLERANCE,
    MomentumImpulseSolver,
)
from assessment_platform.domains.physical_sciences.mechanics.momentum_interaction import (
    CommonFinalVelocityConstraint,
    CompleteFinalStateConstraint,
    InteractionConstraintKind,
    KnownFinalVelocityConstraint,
    MomentumInteraction,
)


class CollisionClassification(StrEnum):
    """Classification for a validated isolated two-body final state."""

    ELASTIC = "elastic"
    INELASTIC = "inelastic"
    PERFECTLY_INELASTIC = "perfectly-inelastic"


def _identifier(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True, slots=True)
class DerivedFinalBodyState:
    """A solver-derived final state for one identified body."""

    body_identifier: str
    final_velocity: MetresPerSecond
    final_momentum: Momentum

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "body_identifier", _identifier(self.body_identifier, "body identifier")
        )
        if not isinstance(self.final_velocity, MetresPerSecond):
            raise ValueError("final velocity must be MetresPerSecond")
        if not isinstance(self.final_momentum, Momentum):
            raise ValueError("final momentum must be Momentum")


@dataclass(frozen=True, slots=True)
class ConstrainedCollisionSolution:
    """Typed results from one explicitly constrained interaction."""

    interaction_identifier: str
    final_states: tuple[DerivedFinalBodyState, ...]
    initial_total_momentum: Momentum
    external_impulse: Impulse
    final_total_momentum: Momentum
    positive_axis: PositiveAxis
    seed: GenerationSeed | None
    constraint_kind: InteractionConstraintKind
    initial_kinetic_energy: KineticEnergy
    final_kinetic_energy: KineticEnergy
    classification: CollisionClassification | None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "interaction_identifier",
            _identifier(self.interaction_identifier, "interaction identifier"),
        )
        states = tuple(self.final_states)
        if not states or any(not isinstance(state, DerivedFinalBodyState) for state in states):
            raise ValueError("solution must contain DerivedFinalBodyState values")
        identifiers = tuple(state.body_identifier for state in states)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("solution final body identifiers must be unique")
        object.__setattr__(self, "final_states", states)
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
        if not isinstance(self.constraint_kind, InteractionConstraintKind):
            raise ValueError("constraint_kind must be InteractionConstraintKind")
        if not isinstance(self.initial_kinetic_energy, KineticEnergy):
            raise ValueError("initial_kinetic_energy must be KineticEnergy")
        if not isinstance(self.final_kinetic_energy, KineticEnergy):
            raise ValueError("final_kinetic_energy must be KineticEnergy")
        if self.classification is not None and not isinstance(
            self.classification, CollisionClassification
        ):
            raise ValueError("classification must be CollisionClassification or None")


class ConstrainedMomentumSolver:
    """Solve only final states justified by an authored interaction constraint."""

    def __init__(self, interaction: MomentumInteraction | None) -> None:
        if interaction is not None and not isinstance(interaction, MomentumInteraction):
            raise ValueError("interaction must be a MomentumInteraction or None")
        self.interaction = interaction

    def solve(self) -> ConstrainedCollisionSolution:
        if self.interaction is None:
            raise ValueError(
                "interaction constraint is required; collision final states are underdetermined"
            )

        interaction = self.interaction
        scenario = interaction.scenario
        aggregate = MomentumImpulseSolver(scenario).solve()
        final_velocities = self._final_velocities(interaction, aggregate.final_total_momentum)
        final_states = tuple(
            DerivedFinalBodyState(
                body.identifier,
                velocity,
                Momentum(body.mass.value * velocity.value),
            )
            for body, velocity in final_velocities
        )
        initial_energy = KineticEnergy(
            sum(
                self._kinetic_energy(body.mass.value, body.initial_velocity.value)
                for body in scenario.bodies
            )
        )
        final_energy = KineticEnergy(
            sum(
                self._kinetic_energy(body.mass.value, velocity.value)
                for body, velocity in final_velocities
            )
        )
        return ConstrainedCollisionSolution(
            interaction_identifier=interaction.identifier,
            final_states=final_states,
            initial_total_momentum=aggregate.initial_total_momentum,
            external_impulse=aggregate.external_impulse,
            final_total_momentum=aggregate.final_total_momentum,
            positive_axis=aggregate.positive_axis,
            seed=aggregate.seed,
            constraint_kind=interaction.constraint.kind,
            initial_kinetic_energy=initial_energy,
            final_kinetic_energy=final_energy,
            classification=self._classify(
                scenario,
                interaction.constraint.kind,
                final_velocities,
                initial_energy,
                final_energy,
            ),
        )

    def validate(self, solution: ConstrainedCollisionSolution) -> ValidationResult:
        """Validate aggregate, authored, and derived final-state invariants."""

        if not isinstance(solution, ConstrainedCollisionSolution):
            return ValidationResult(
                False, ("solution must be a ConstrainedCollisionSolution",)
            )
        if self.interaction is None:
            return ValidationResult(False, ("interaction constraint is required",))

        errors: list[str] = []
        interaction = self.interaction
        scenario = interaction.scenario
        aggregate = MomentumImpulseSolver(scenario).solve()
        if solution.interaction_identifier != interaction.identifier:
            errors.append("solution interaction identifier does not match the interaction")
        if solution.positive_axis is not scenario.positive_axis:
            errors.append("solution positive axis does not match the scenario")
        if solution.seed != scenario.seed:
            errors.append("solution seed does not match the scenario")
        if solution.constraint_kind is not interaction.constraint.kind:
            errors.append("solution constraint kind does not match the interaction")
        if not self._close(
            solution.initial_total_momentum.value, aggregate.initial_total_momentum.value
        ):
            errors.append("initial total momentum does not match the aggregate solution")
        if not self._close(solution.external_impulse.value, aggregate.external_impulse.value):
            errors.append("external impulse does not match the system boundary")
        if not self._close(
            solution.final_total_momentum.value, aggregate.final_total_momentum.value
        ):
            errors.append("final total momentum does not match the aggregate solution")

        body_by_id = {body.identifier: body for body in scenario.bodies}
        state_by_id = {state.body_identifier: state for state in solution.final_states}
        if set(state_by_id) != set(body_by_id):
            errors.append("solution final body identifiers do not match the scenario")
        for identifier, state in state_by_id.items():
            body = body_by_id.get(identifier)
            if body is None:
                continue
            expected_momentum = body.mass.value * state.final_velocity.value
            if not self._close(state.final_momentum.value, expected_momentum):
                errors.append(f"final momentum is invalid for {identifier}")

        expected_final_total = sum(state.final_momentum.value for state in solution.final_states)
        if not self._close(solution.final_total_momentum.value, expected_final_total):
            errors.append("final total momentum does not equal the signed final body sum")
        if scenario.system.isolated and not self._close(
            solution.final_total_momentum.value, solution.initial_total_momentum.value
        ):
            errors.append("isolated-system total momentum is not conserved")

        self._validate_authored_constraint(errors, interaction, state_by_id)
        expected_initial_energy = sum(
            self._kinetic_energy(body.mass.value, body.initial_velocity.value)
            for body in scenario.bodies
        )
        expected_final_energy = sum(
            self._kinetic_energy(body_by_id[identifier].mass.value, state.final_velocity.value)
            for identifier, state in state_by_id.items()
            if identifier in body_by_id
        )
        if not self._close(solution.initial_kinetic_energy.value, expected_initial_energy):
            errors.append("initial kinetic energy is invalid")
        if not self._close(solution.final_kinetic_energy.value, expected_final_energy):
            errors.append("final kinetic energy is invalid")
        final_velocities: list[tuple[MomentumBody, MetresPerSecond]] = []
        for body in scenario.bodies:
            current_state = state_by_id.get(body.identifier)
            if current_state is not None:
                final_velocities.append((body, current_state.final_velocity))
        expected_classification = self._classify(
            scenario,
            interaction.constraint.kind,
            tuple(final_velocities),
            KineticEnergy(expected_initial_energy),
            KineticEnergy(expected_final_energy),
        )
        if solution.classification is not expected_classification:
            errors.append("collision classification is invalid")
        return ValidationResult(not errors, tuple(errors))

    def _final_velocities(
        self,
        interaction: MomentumInteraction,
        target_momentum: Momentum,
    ) -> tuple[tuple[MomentumBody, MetresPerSecond], ...]:
        scenario = interaction.scenario
        if len(scenario.bodies) != 2:
            raise ValueError("constrained collision solving requires exactly two bodies")
        body_by_id = {body.identifier: body for body in scenario.bodies}
        constraint = interaction.constraint
        if isinstance(constraint, KnownFinalVelocityConstraint):
            known_body = body_by_id[constraint.body_identifier]
            unknown_body = next(
                body for body in scenario.bodies if body.identifier != known_body.identifier
            )
            unknown_value = (
                target_momentum.value
                - known_body.mass.value * constraint.final_velocity.value
            ) / unknown_body.mass.value
            values = {
                known_body.identifier: constraint.final_velocity,
                unknown_body.identifier: MetresPerSecond(unknown_value),
            }
        elif isinstance(constraint, CommonFinalVelocityConstraint):
            if set(constraint.body_identifiers) != set(body_by_id):
                raise ValueError("common final velocity must cover both scenario bodies")
            total_mass = sum(body.mass.value for body in scenario.bodies)
            common_velocity = MetresPerSecond(target_momentum.value / total_mass)
            values = {identifier: common_velocity for identifier in body_by_id}
        elif isinstance(constraint, CompleteFinalStateConstraint):
            values = {
                state.body_identifier: state.final_velocity for state in constraint.final_states
            }
        else:
            raise ValueError("unsupported interaction constraint")
        return tuple((body, values[body.identifier]) for body in scenario.bodies)

    def _validate_authored_constraint(
        self,
        errors: list[str],
        interaction: MomentumInteraction,
        states: dict[str, DerivedFinalBodyState],
    ) -> None:
        constraint = interaction.constraint
        if isinstance(constraint, KnownFinalVelocityConstraint):
            state = states.get(constraint.body_identifier)
            if state is None or not self._close(
                state.final_velocity.value, constraint.final_velocity.value
            ):
                errors.append("known final velocity was not preserved")
        elif isinstance(constraint, CommonFinalVelocityConstraint):
            velocities = [
                states[identifier].final_velocity.value
                for identifier in constraint.body_identifiers
                if identifier in states
            ]
            if len(velocities) != 2 or not self._close(velocities[0], velocities[1]):
                errors.append("common final velocity was not preserved")
        elif isinstance(constraint, CompleteFinalStateConstraint):
            authored = {
                state.body_identifier: state.final_velocity.value
                for state in constraint.final_states
            }
            for identifier, velocity in authored.items():
                actual = states.get(identifier)
                if actual is None or not self._close(actual.final_velocity.value, velocity):
                    errors.append(f"authored final velocity was not preserved for {identifier}")

    @classmethod
    def _classify(
        cls,
        scenario: MomentumScenario,
        constraint_kind: InteractionConstraintKind,
        final_velocities: tuple[tuple[MomentumBody, MetresPerSecond], ...],
        initial_energy: KineticEnergy,
        final_energy: KineticEnergy,
    ) -> CollisionClassification | None:
        if not scenario.system.isolated:
            return None
        values = tuple(velocity.value for _, velocity in final_velocities)
        if constraint_kind is InteractionConstraintKind.COMMON_FINAL_VELOCITY or (
            values and all(cls._close(values[0], value) for value in values[1:])
        ):
            return CollisionClassification.PERFECTLY_INELASTIC
        if cls._close(initial_energy.value, final_energy.value):
            return CollisionClassification.ELASTIC
        return CollisionClassification.INELASTIC

    @staticmethod
    def _kinetic_energy(mass: float, velocity: float) -> float:
        return 0.5 * mass * velocity * velocity

    @staticmethod
    def _close(first: float, second: float) -> bool:
        return isfinite(first) and isfinite(second) and abs(first - second) <= VALIDATION_TOLERANCE
