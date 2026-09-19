"""Deterministic authored Momentum & Impulse problem generation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from random import Random

from assessment_platform.core import Difficulty, GenerationProvenance, GenerationSeed
from assessment_platform.domains.physical_sciences.mechanics.momentum_constrained_solver import (
    ConstrainedMomentumSolver,
)
from assessment_platform.domains.physical_sciences.mechanics.momentum_impulse import (
    Impulse,
    Kilograms,
    MetresPerSecond,
    MomentumScenario,
    Newtons,
    PhysicalDirection,
    PositiveAxis,
    Seconds,
)
from assessment_platform.domains.physical_sciences.mechanics.momentum_impulse_relationships import (
    ForceTimeInput,
    MomentumChangeInput,
)
from assessment_platform.domains.physical_sciences.mechanics.momentum_interaction import (
    CommonFinalVelocityConstraint,
    CompleteFinalStateConstraint,
    FinalBodyState,
    KnownFinalVelocityConstraint,
    MomentumInteraction,
)

from .momentum_impulse_scenario_factory import (
    DEFAULT_MOMENTUM_GENERATION_POLICY,
    MomentumGenerationPolicy,
    MomentumScenarioFactory,
    MomentumScenarioFamily,
    MomentumScenarioGenerationInput,
)

PROBLEM_FACTORY_ID = "caps-grade-12-momentum-impulse-problem-factory"
PROBLEM_POLICY_VERSION = "2"


class MomentumGenerationFamily(StrEnum):
    """Authored problem families supported by the generation policy."""

    INITIAL_MOMENTUM = "initial-momentum"
    MOMENTUM_CHANGE = "momentum-change"
    IMPULSE_FORCE_TIME = "impulse-force-time"
    FORCE_FROM_MOMENTUM_CHANGE = "force-from-momentum-change"
    CONTACT_TIME_FROM_IMPULSE_FORCE = "contact-time-from-impulse-force"
    KNOWN_FINAL_VELOCITY_COLLISION = "known-final-velocity-collision"
    STICKING_COLLISION = "sticking-collision"
    COMPLETE_FINAL_STATE_COLLISION = "complete-final-state-collision"


@dataclass(frozen=True, slots=True)
class MomentumProblemGenerationInput:
    """Framework-independent inputs for one deterministic authored problem."""

    seed: GenerationSeed
    family: MomentumGenerationFamily | None = None
    difficulty: Difficulty = Difficulty.MODERATE
    positive_axis: PositiveAxis | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.seed, GenerationSeed):
            raise ValueError("problem generation seed must be a GenerationSeed")
        if self.family is not None and not isinstance(self.family, MomentumGenerationFamily):
            raise ValueError("problem generation family must be a MomentumGenerationFamily")
        if not isinstance(self.difficulty, Difficulty):
            raise ValueError("problem generation difficulty must be a Difficulty")
        if self.positive_axis is not None and not isinstance(self.positive_axis, PositiveAxis):
            raise ValueError("positive_axis must be explicit when supplied")


@dataclass(frozen=True, slots=True)
class MomentumProblemDifficultyProfile:
    """Bounded platform pools for one authored-problem difficulty."""

    masses_kg: tuple[float, ...]
    speed_magnitudes_m_per_s: tuple[float, ...]
    force_magnitudes_n: tuple[float, ...]
    contact_times_s: tuple[float, ...]
    impulse_magnitudes_n_s: tuple[float, ...]

    def __post_init__(self) -> None:
        pools = (
            (self.masses_kg, "mass", True),
            (self.speed_magnitudes_m_per_s, "speed", True),
            (self.force_magnitudes_n, "force", True),
            (self.contact_times_s, "contact time", True),
            (self.impulse_magnitudes_n_s, "impulse", True),
        )
        for raw_values, name, strictly_positive in pools:
            values = tuple(raw_values)
            if not values or any(
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or value <= 0
                for value in values
            ):
                qualifier = "positive" if strictly_positive else "non-negative"
                raise ValueError(f"{name} pool must contain finite {qualifier} values")
            if len(values) != len(set(values)):
                raise ValueError(f"{name} pool must not contain duplicate values")
            if any(not isfinite(value) for value in values):
                raise ValueError(f"{name} pool must contain finite values")
            object.__setattr__(self, self._field_for(name), values)

    @staticmethod
    def _field_for(name: str) -> str:
        return {
            "mass": "masses_kg",
            "speed": "speed_magnitudes_m_per_s",
            "force": "force_magnitudes_n",
            "contact time": "contact_times_s",
            "impulse": "impulse_magnitudes_n_s",
        }[name]


@dataclass(frozen=True, slots=True)
class MomentumProblemGenerationPolicy:
    """Versioned generation policy composed with the Issue #32 factory."""

    policy_version: str = PROBLEM_POLICY_VERSION
    allowed_families: tuple[MomentumGenerationFamily, ...] = tuple(MomentumGenerationFamily)
    allowed_axes: tuple[PositiveAxis, ...] = (PositiveAxis.RIGHT, PositiveAxis.LEFT)
    scenario_policy: MomentumGenerationPolicy = DEFAULT_MOMENTUM_GENERATION_POLICY
    introductory: MomentumProblemDifficultyProfile = MomentumProblemDifficultyProfile(
        (1.0, 2.0), (2.0, 4.0), (2.0, 4.0), (1.0, 2.0), (2.0, 4.0)
    )
    moderate: MomentumProblemDifficultyProfile = MomentumProblemDifficultyProfile(
        (2.0, 3.0, 4.0), (3.0, 5.0, 7.0), (3.0, 5.0, 7.0), (0.5, 1.0, 2.0), (3.0, 5.0, 7.0)
    )
    advanced: MomentumProblemDifficultyProfile = MomentumProblemDifficultyProfile(
        (3.0, 4.0, 5.0), (4.0, 6.0, 8.0), (4.0, 6.0, 8.0), (0.2, 0.5, 1.0), (4.0, 6.0, 8.0)
    )

    def __post_init__(self) -> None:
        if not isinstance(self.policy_version, str) or not self.policy_version.strip():
            raise ValueError("policy version must be a non-empty string")
        families = tuple(self.allowed_families)
        axes = tuple(self.allowed_axes)
        if not families or any(not isinstance(item, MomentumGenerationFamily) for item in families):
            raise ValueError("allowed families must contain MomentumGenerationFamily values")
        if len(families) != len(set(families)):
            raise ValueError("allowed families must not contain duplicates")
        if not axes or any(not isinstance(item, PositiveAxis) for item in axes):
            raise ValueError("allowed axes must contain PositiveAxis values")
        if len(axes) != len(set(axes)):
            raise ValueError("allowed axes must not contain duplicates")
        if not isinstance(self.scenario_policy, MomentumGenerationPolicy):
            raise ValueError("scenario_policy must be a MomentumGenerationPolicy")
        for profile in (self.introductory, self.moderate, self.advanced):
            if not isinstance(profile, MomentumProblemDifficultyProfile):
                raise ValueError(
                    "difficulty profiles must be MomentumProblemDifficultyProfile values"
                )
        object.__setattr__(self, "policy_version", self.policy_version.strip())
        object.__setattr__(self, "allowed_families", families)
        object.__setattr__(self, "allowed_axes", axes)

    def profile_for(self, difficulty: Difficulty) -> MomentumProblemDifficultyProfile:
        if not isinstance(difficulty, Difficulty):
            raise ValueError("difficulty must be a Difficulty")
        return {
            Difficulty.INTRODUCTORY: self.introductory,
            Difficulty.MODERATE: self.moderate,
            Difficulty.ADVANCED: self.advanced,
        }[difficulty]


DEFAULT_MOMENTUM_PROBLEM_GENERATION_POLICY = MomentumProblemGenerationPolicy()


@dataclass(frozen=True, slots=True)
class _GeneratedMetadata:
    identifier: str
    family: MomentumGenerationFamily
    difficulty: Difficulty
    provenance: GenerationProvenance

    def __post_init__(self) -> None:
        if not isinstance(self.identifier, str) or not self.identifier.strip():
            raise ValueError("generated problem identifier must be non-empty")
        if not isinstance(self.family, MomentumGenerationFamily):
            raise ValueError("generated problem family must be MomentumGenerationFamily")
        if not isinstance(self.difficulty, Difficulty):
            raise ValueError("generated problem difficulty must be Difficulty")
        if not isinstance(self.provenance, GenerationProvenance):
            raise ValueError("generated problem provenance must be GenerationProvenance")


@dataclass(frozen=True, slots=True)
class GeneratedInitialMomentumProblem:
    metadata: _GeneratedMetadata
    scenario: MomentumScenario

    def __post_init__(self) -> None:
        _validate_metadata(self.metadata, MomentumGenerationFamily.INITIAL_MOMENTUM)
        if not isinstance(self.scenario, MomentumScenario):
            raise ValueError("initial momentum problem scenario must be MomentumScenario")


@dataclass(frozen=True, slots=True)
class GeneratedMomentumChangeProblem:
    metadata: _GeneratedMetadata
    input_data: MomentumChangeInput

    def __post_init__(self) -> None:
        _validate_metadata(self.metadata, MomentumGenerationFamily.MOMENTUM_CHANGE)
        if not isinstance(self.input_data, MomentumChangeInput):
            raise ValueError("momentum-change problem input must be MomentumChangeInput")


@dataclass(frozen=True, slots=True)
class GeneratedImpulseForceTimeProblem:
    metadata: _GeneratedMetadata
    input_data: ForceTimeInput

    def __post_init__(self) -> None:
        _validate_metadata(self.metadata, MomentumGenerationFamily.IMPULSE_FORCE_TIME)
        if not isinstance(self.input_data, ForceTimeInput):
            raise ValueError("impulse force-time problem input must be ForceTimeInput")


@dataclass(frozen=True, slots=True)
class GeneratedForceFromMomentumChangeProblem:
    metadata: _GeneratedMetadata
    momentum_change_input: MomentumChangeInput
    contact_time: Seconds

    def __post_init__(self) -> None:
        _validate_metadata(self.metadata, MomentumGenerationFamily.FORCE_FROM_MOMENTUM_CHANGE)
        if not isinstance(self.momentum_change_input, MomentumChangeInput):
            raise ValueError("force problem input must be MomentumChangeInput")
        if not isinstance(self.contact_time, Seconds):
            raise ValueError("force problem contact_time must be Seconds")


@dataclass(frozen=True, slots=True)
class GeneratedContactTimeProblem:
    metadata: _GeneratedMetadata
    impulse: Impulse
    force: Newtons
    positive_axis: PositiveAxis

    def __post_init__(self) -> None:
        _validate_metadata(self.metadata, MomentumGenerationFamily.CONTACT_TIME_FROM_IMPULSE_FORCE)
        if not isinstance(self.impulse, Impulse):
            raise ValueError("contact-time problem impulse must be Impulse")
        if not isinstance(self.force, Newtons):
            raise ValueError("contact-time problem force must be Newtons")
        if not isinstance(self.positive_axis, PositiveAxis):
            raise ValueError("contact-time problem axis must be PositiveAxis")
        if self.impulse.value == 0 or self.force.value == 0:
            raise ValueError("contact-time problem requires non-zero impulse and force")
        if self.impulse.value * self.force.value < 0:
            raise ValueError("contact-time problem impulse and force must have compatible signs")


@dataclass(frozen=True, slots=True)
class GeneratedCollisionProblem:
    metadata: _GeneratedMetadata
    scenario: MomentumScenario
    interaction: MomentumInteraction

    def __post_init__(self) -> None:
        if self.metadata.family not in {
            MomentumGenerationFamily.KNOWN_FINAL_VELOCITY_COLLISION,
            MomentumGenerationFamily.STICKING_COLLISION,
            MomentumGenerationFamily.COMPLETE_FINAL_STATE_COLLISION,
        }:
            raise ValueError("collision problem family is not supported")
        if not isinstance(self.scenario, MomentumScenario):
            raise ValueError("collision problem scenario must be MomentumScenario")
        if not isinstance(self.interaction, MomentumInteraction):
            raise ValueError("collision problem interaction must be MomentumInteraction")
        if self.interaction.scenario != self.scenario:
            raise ValueError("collision interaction must use the generated scenario")
        known_family = (
            self.metadata.family is MomentumGenerationFamily.KNOWN_FINAL_VELOCITY_COLLISION
        )
        if known_family and not isinstance(
            self.interaction.constraint, KnownFinalVelocityConstraint
        ):
            raise ValueError("known-final-velocity problem requires its matching constraint")
        if self.metadata.family is MomentumGenerationFamily.STICKING_COLLISION and not isinstance(
            self.interaction.constraint, CommonFinalVelocityConstraint
        ):
            raise ValueError("sticking problem requires its matching constraint")
        complete_family = (
            self.metadata.family is MomentumGenerationFamily.COMPLETE_FINAL_STATE_COLLISION
        )
        if complete_family and not isinstance(
            self.interaction.constraint, CompleteFinalStateConstraint
        ):
            raise ValueError("complete-state problem requires its matching constraint")


MomentumGeneratedProblem = (
    GeneratedInitialMomentumProblem
    | GeneratedMomentumChangeProblem
    | GeneratedImpulseForceTimeProblem
    | GeneratedForceFromMomentumChangeProblem
    | GeneratedContactTimeProblem
    | GeneratedCollisionProblem
)


def _validate_metadata(metadata: _GeneratedMetadata, expected: MomentumGenerationFamily) -> None:
    if not isinstance(metadata, _GeneratedMetadata):
        raise ValueError("generated problem metadata must be _GeneratedMetadata")
    if metadata.family is not expected:
        raise ValueError("generated problem metadata family does not match its output type")


class MomentumProblemFactory:
    """Compose deterministic authored problem generation from existing policy and solvers."""

    def __init__(
        self,
        policy: MomentumProblemGenerationPolicy = DEFAULT_MOMENTUM_PROBLEM_GENERATION_POLICY,
    ) -> None:
        if not isinstance(policy, MomentumProblemGenerationPolicy):
            raise ValueError("policy must be a MomentumProblemGenerationPolicy")
        self.policy = policy
        self._scenario_factory = MomentumScenarioFactory(policy.scenario_policy)

    def generate(self, request: MomentumProblemGenerationInput) -> MomentumGeneratedProblem:
        if not isinstance(request, MomentumProblemGenerationInput):
            raise ValueError("request must be a MomentumProblemGenerationInput")
        if request.family is not None and request.family not in self.policy.allowed_families:
            raise ValueError("requested problem family is not allowed by the policy")
        if (
            request.positive_axis is not None
            and request.positive_axis not in self.policy.allowed_axes
        ):
            raise ValueError("requested positive axis is not allowed by the policy")

        rng = Random(request.seed.value)
        family = request.family or rng.choice(self.policy.allowed_families)
        axis = request.positive_axis or rng.choice(self.policy.allowed_axes)
        profile = self.policy.profile_for(request.difficulty)
        metadata = self._metadata(request, family, axis)

        if family is MomentumGenerationFamily.INITIAL_MOMENTUM:
            scenario = self._scenario(request, MomentumScenarioFamily.SINGLE_BODY, axis)
            return GeneratedInitialMomentumProblem(metadata, scenario)
        if family is MomentumGenerationFamily.MOMENTUM_CHANGE:
            return GeneratedMomentumChangeProblem(
                metadata, self._momentum_change_input(profile, axis, request.difficulty, rng)
            )
        if family is MomentumGenerationFamily.IMPULSE_FORCE_TIME:
            return GeneratedImpulseForceTimeProblem(
                metadata, self._force_time_input(profile, axis, rng)
            )
        if family is MomentumGenerationFamily.FORCE_FROM_MOMENTUM_CHANGE:
            return GeneratedForceFromMomentumChangeProblem(
                metadata,
                self._momentum_change_input(profile, axis, request.difficulty, rng),
                Seconds(rng.choice(profile.contact_times_s)),
            )
        if family is MomentumGenerationFamily.CONTACT_TIME_FROM_IMPULSE_FORCE:
            magnitude = rng.choice(profile.impulse_magnitudes_n_s)
            direction = rng.choice((PhysicalDirection.RIGHT, PhysicalDirection.LEFT))
            sign = self._signed_value(magnitude, direction, axis)
            force = self._signed_value(rng.choice(profile.force_magnitudes_n), direction, axis)
            return GeneratedContactTimeProblem(
                metadata, Impulse(sign), Newtons(force), axis
            )
        if family is MomentumGenerationFamily.KNOWN_FINAL_VELOCITY_COLLISION:
            return self._known_collision(metadata, request, profile, axis, rng)
        if family is MomentumGenerationFamily.STICKING_COLLISION:
            return self._sticking_collision(metadata, request, axis)
        if family is MomentumGenerationFamily.COMPLETE_FINAL_STATE_COLLISION:
            return self._complete_collision(metadata, request, profile, axis, rng)
        raise ValueError("unsupported MomentumGenerationFamily")

    def _scenario(
        self,
        request: MomentumProblemGenerationInput,
        family: MomentumScenarioFamily,
        axis: PositiveAxis,
    ) -> MomentumScenario:
        return self._scenario_factory.generate(
            MomentumScenarioGenerationInput(
                seed=request.seed,
                family=family,
                difficulty=request.difficulty,
                positive_axis=axis,
            )
        )

    def _known_collision(
        self,
        metadata: _GeneratedMetadata,
        request: MomentumProblemGenerationInput,
        profile: MomentumProblemDifficultyProfile,
        axis: PositiveAxis,
        rng: Random,
    ) -> GeneratedCollisionProblem:
        scenario = self._scenario(request, MomentumScenarioFamily.OPPOSITE_MOVING_ISOLATED, axis)
        body = rng.choice(scenario.bodies)
        magnitude = rng.choice(profile.speed_magnitudes_m_per_s)
        direction = rng.choice((PhysicalDirection.RIGHT, PhysicalDirection.LEFT))
        constraint = KnownFinalVelocityConstraint(
            body.identifier,
            MetresPerSecond(self._signed_value(magnitude, direction, axis)),
        )
        interaction = MomentumInteraction(
            f"{metadata.identifier}-interaction", scenario, constraint
        )
        return GeneratedCollisionProblem(metadata, scenario, interaction)

    def _sticking_collision(
        self,
        metadata: _GeneratedMetadata,
        request: MomentumProblemGenerationInput,
        axis: PositiveAxis,
    ) -> GeneratedCollisionProblem:
        scenario = self._scenario(
            request, MomentumScenarioFamily.OPPOSITE_MOVING_ISOLATED, axis
        )
        constraint = CommonFinalVelocityConstraint(
            tuple(body.identifier for body in scenario.bodies)
        )
        interaction = MomentumInteraction(
            f"{metadata.identifier}-interaction", scenario, constraint
        )
        return GeneratedCollisionProblem(metadata, scenario, interaction)

    def _complete_collision(
        self,
        metadata: _GeneratedMetadata,
        request: MomentumProblemGenerationInput,
        profile: MomentumProblemDifficultyProfile,
        axis: PositiveAxis,
        rng: Random,
    ) -> GeneratedCollisionProblem:
        scenario = self._scenario(request, MomentumScenarioFamily.OPPOSITE_MOVING_ISOLATED, axis)
        candidates = self._complete_state_candidates(scenario, profile, axis)
        start = rng.randrange(len(candidates))
        for offset in range(len(candidates)):
            candidate = candidates[(start + offset) % len(candidates)]
            constraint = CompleteFinalStateConstraint(
                tuple(
                    FinalBodyState(body.identifier, candidate[index])
                    for index, body in enumerate(scenario.bodies)
                )
            )
            interaction = MomentumInteraction(
                f"{metadata.identifier}-interaction", scenario, constraint
            )
            solver = ConstrainedMomentumSolver(interaction)
            if solver.validate(solver.solve()).valid:
                return GeneratedCollisionProblem(metadata, scenario, interaction)
        raise ValueError("policy could not produce a solver-valid complete final state")

    @staticmethod
    def _complete_state_candidates(
        scenario: MomentumScenario,
        profile: MomentumProblemDifficultyProfile,
        axis: PositiveAxis,
    ) -> tuple[tuple[MetresPerSecond, ...], ...]:
        initial = tuple(body.initial_velocity for body in scenario.bodies)
        reversed_values = tuple(MetresPerSecond(-velocity.value) for velocity in initial)
        pool_values = tuple(
            MetresPerSecond(MomentumProblemFactory._signed_value(speed, direction, axis))
            for speed in profile.speed_magnitudes_m_per_s
            for direction in (PhysicalDirection.RIGHT, PhysicalDirection.LEFT)
        )
        return (initial, reversed_values) + tuple(
            (first, second) for first in pool_values for second in pool_values
        )

    @staticmethod
    def _momentum_change_input(
        profile: MomentumProblemDifficultyProfile,
        axis: PositiveAxis,
        difficulty: Difficulty,
        rng: Random,
    ) -> MomentumChangeInput:
        speeds = profile.speed_magnitudes_m_per_s
        mass = Kilograms(rng.choice(profile.masses_kg))
        mode = {
            Difficulty.INTRODUCTORY: "speeding-up",
            Difficulty.MODERATE: rng.choice(("speeding-up", "slowing-down", "stopping", "rest")),
            Difficulty.ADVANCED: rng.choice(
                ("speeding-up", "slowing-down", "stopping", "rest", "reversal")
            ),
        }[difficulty]
        low, high = min(speeds), max(speeds)
        if mode == "speeding-up":
            initial, final = low, high
            initial_direction = final_direction = PhysicalDirection.RIGHT
        elif mode == "slowing-down":
            initial, final = high, low
            initial_direction = final_direction = PhysicalDirection.RIGHT
        elif mode == "stopping":
            initial, final = high, 0.0
            initial_direction, final_direction = PhysicalDirection.RIGHT, PhysicalDirection.REST
        elif mode == "rest":
            initial, final = 0.0, low
            initial_direction, final_direction = PhysicalDirection.REST, PhysicalDirection.RIGHT
        else:
            initial, final = high, low
            initial_direction, final_direction = PhysicalDirection.RIGHT, PhysicalDirection.LEFT
        return MomentumChangeInput(
            mass,
            MetresPerSecond(MomentumProblemFactory._signed_value(initial, initial_direction, axis)),
            MetresPerSecond(MomentumProblemFactory._signed_value(final, final_direction, axis)),
            axis,
        )

    @staticmethod
    def _force_time_input(
        profile: MomentumProblemDifficultyProfile,
        axis: PositiveAxis,
        rng: Random,
    ) -> ForceTimeInput:
        direction = rng.choice((PhysicalDirection.RIGHT, PhysicalDirection.LEFT))
        force = MomentumProblemFactory._signed_value(
            rng.choice(profile.force_magnitudes_n), direction, axis
        )
        return ForceTimeInput(Newtons(force), Seconds(rng.choice(profile.contact_times_s)), axis)

    def _metadata(
        self,
        request: MomentumProblemGenerationInput,
        family: MomentumGenerationFamily,
        axis: PositiveAxis,
    ) -> _GeneratedMetadata:
        identifier = (
            f"mi-problem-v{self.policy.policy_version}-{family.value}-"
            f"{request.difficulty.value}-{axis.value}-seed-{request.seed.value}"
        )
        provenance = GenerationProvenance(
            PROBLEM_FACTORY_ID,
            self.policy.policy_version,
            request.seed,
            (family.value, request.difficulty.value, axis.value),
        )
        return _GeneratedMetadata(identifier, family, request.difficulty, provenance)

    @staticmethod
    def _signed_value(
        magnitude: float, direction: PhysicalDirection, positive_axis: PositiveAxis
    ) -> float:
        if direction is PhysicalDirection.REST:
            return 0.0
        if direction not in (PhysicalDirection.RIGHT, PhysicalDirection.LEFT):
            raise ValueError("direction must be a physical axis direction")
        is_positive = (
            direction is PhysicalDirection.RIGHT and positive_axis is PositiveAxis.RIGHT
        ) or (direction is PhysicalDirection.LEFT and positive_axis is PositiveAxis.LEFT)
        return magnitude if is_positive else -magnitude
