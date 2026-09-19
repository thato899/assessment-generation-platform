"""Deterministic policy-driven generation of Momentum & Impulse scenarios."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from random import Random

from assessment_platform.core import Difficulty, GenerationProvenance, GenerationSeed
from assessment_platform.domains.physical_sciences.mechanics.momentum_impulse import (
    Impulse,
    Kilograms,
    MetresPerSecond,
    MomentumBody,
    MomentumScenario,
    PhysicalDirection,
    PositiveAxis,
    SystemBoundary,
)

FACTORY_ID = "caps-grade-12-momentum-impulse-scenario-factory"
POLICY_VERSION = "1"


class MomentumScenarioFamily(StrEnum):
    """Supported pedagogical initial-condition families."""

    SINGLE_BODY = "single-body"
    OPPOSITE_MOVING_ISOLATED = "opposite-moving-isolated"
    EXTERNAL_IMPULSE = "external-impulse"


@dataclass(frozen=True, slots=True)
class MomentumScenarioGenerationInput:
    """Immutable inputs for one deterministic scenario-generation request."""

    seed: GenerationSeed
    family: MomentumScenarioFamily | None = None
    difficulty: Difficulty = Difficulty.MODERATE
    positive_axis: PositiveAxis | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.seed, GenerationSeed):
            raise ValueError("scenario generation seed must be a GenerationSeed")
        if self.family is not None and not isinstance(self.family, MomentumScenarioFamily):
            raise ValueError("scenario generation family must be a MomentumScenarioFamily")
        if not isinstance(self.difficulty, Difficulty):
            raise ValueError("scenario generation difficulty must be a Difficulty")
        if self.positive_axis is not None and not isinstance(self.positive_axis, PositiveAxis):
            raise ValueError("positive_axis must be explicit when supplied")


@dataclass(frozen=True, slots=True)
class MomentumDifficultyProfile:
    """Bounded platform-generation pools for one difficulty level."""

    masses_kg: tuple[float, ...]
    speed_magnitudes_m_per_s: tuple[float, ...]
    external_impulse_magnitudes_n_s: tuple[float, ...]

    def __post_init__(self) -> None:
        masses = tuple(self.masses_kg)
        speeds = tuple(self.speed_magnitudes_m_per_s)
        impulses = tuple(self.external_impulse_magnitudes_n_s)
        if not masses or any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not isfinite(value)
            or value <= 0
            for value in masses
        ):
            raise ValueError("mass pool must contain finite positive values")
        if not speeds or any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not isfinite(value)
            or value <= 0
            for value in speeds
        ):
            raise ValueError("speed pool must contain finite positive values")
        if not impulses or any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not isfinite(value)
            or value < 0
            for value in impulses
        ):
            raise ValueError("external impulse pool must contain finite non-negative values")
        if any(len(values) != len(set(values)) for values in (masses, speeds, impulses)):
            raise ValueError("generation pools must not contain duplicate values")
        object.__setattr__(self, "masses_kg", masses)
        object.__setattr__(self, "speed_magnitudes_m_per_s", speeds)
        object.__setattr__(self, "external_impulse_magnitudes_n_s", impulses)


@dataclass(frozen=True, slots=True)
class MomentumGenerationPolicy:
    """Versioned platform policy, separate from CAPS curriculum metadata."""

    policy_version: str = POLICY_VERSION
    allowed_families: tuple[MomentumScenarioFamily, ...] = (
        MomentumScenarioFamily.SINGLE_BODY,
        MomentumScenarioFamily.OPPOSITE_MOVING_ISOLATED,
        MomentumScenarioFamily.EXTERNAL_IMPULSE,
    )
    allowed_axes: tuple[PositiveAxis, ...] = (PositiveAxis.RIGHT, PositiveAxis.LEFT)
    introductory: MomentumDifficultyProfile = MomentumDifficultyProfile(
        (1.0, 2.0), (2.0, 4.0), (0.0, 2.0)
    )
    moderate: MomentumDifficultyProfile = MomentumDifficultyProfile(
        (2.0, 3.0, 4.0), (3.0, 5.0, 7.0), (0.0, 3.0, 6.0)
    )
    advanced: MomentumDifficultyProfile = MomentumDifficultyProfile(
        (3.0, 4.0, 5.0), (4.0, 6.0, 8.0), (0.0, 4.0, 8.0)
    )

    def __post_init__(self) -> None:
        if not isinstance(self.policy_version, str) or not self.policy_version.strip():
            raise ValueError("policy version must be a non-empty string")
        families = tuple(self.allowed_families)
        axes = tuple(self.allowed_axes)
        if not families or any(
            not isinstance(family, MomentumScenarioFamily) for family in families
        ):
            raise ValueError("allowed families must contain MomentumScenarioFamily values")
        if len(families) != len(set(families)):
            raise ValueError("allowed families must not contain duplicates")
        if not axes or any(not isinstance(axis, PositiveAxis) for axis in axes):
            raise ValueError("allowed axes must contain PositiveAxis values")
        if len(axes) != len(set(axes)):
            raise ValueError("allowed axes must not contain duplicates")
        for profile in (self.introductory, self.moderate, self.advanced):
            if not isinstance(profile, MomentumDifficultyProfile):
                raise ValueError("difficulty profiles must be MomentumDifficultyProfile values")
        object.__setattr__(self, "policy_version", self.policy_version.strip())
        object.__setattr__(self, "allowed_families", families)
        object.__setattr__(self, "allowed_axes", axes)

    def profile_for(self, difficulty: Difficulty) -> MomentumDifficultyProfile:
        if not isinstance(difficulty, Difficulty):
            raise ValueError("difficulty must be a Difficulty")
        return {
            Difficulty.INTRODUCTORY: self.introductory,
            Difficulty.MODERATE: self.moderate,
            Difficulty.ADVANCED: self.advanced,
        }[difficulty]


DEFAULT_MOMENTUM_GENERATION_POLICY = MomentumGenerationPolicy()


class MomentumScenarioFactory:
    """Create valid initial conditions without invoking the solver."""

    def __init__(
        self, policy: MomentumGenerationPolicy = DEFAULT_MOMENTUM_GENERATION_POLICY
    ) -> None:
        if not isinstance(policy, MomentumGenerationPolicy):
            raise ValueError("policy must be a MomentumGenerationPolicy")
        self.policy = policy

    def generate(self, request: MomentumScenarioGenerationInput) -> MomentumScenario:
        if not isinstance(request, MomentumScenarioGenerationInput):
            raise ValueError("request must be a MomentumScenarioGenerationInput")
        if request.family is not None and request.family not in self.policy.allowed_families:
            raise ValueError("requested scenario family is not allowed by the policy")
        if (
            request.positive_axis is not None
            and request.positive_axis not in self.policy.allowed_axes
        ):
            raise ValueError("requested positive axis is not allowed by the policy")

        profile = self.policy.profile_for(request.difficulty)
        rng = Random(request.seed.value)
        family = request.family or rng.choice(self.policy.allowed_families)
        positive_axis = request.positive_axis or rng.choice(self.policy.allowed_axes)
        bodies, system = self._initial_state(family, positive_axis, profile, rng)
        provenance = GenerationProvenance(
            FACTORY_ID,
            self.policy.policy_version,
            request.seed,
            (family, request.difficulty.value, positive_axis.value),
        )
        return MomentumScenario(
            identifier=self._identifier(request, family, positive_axis),
            bodies=bodies,
            positive_axis=positive_axis,
            system=system,
            seed=request.seed,
            provenance=provenance,
        )

    @classmethod
    def _initial_state(
        cls,
        family: MomentumScenarioFamily,
        positive_axis: PositiveAxis,
        profile: MomentumDifficultyProfile,
        rng: Random,
    ) -> tuple[tuple[MomentumBody, ...], SystemBoundary]:
        if family is MomentumScenarioFamily.SINGLE_BODY:
            speed = rng.choice(profile.speed_magnitudes_m_per_s)
            direction = rng.choice(
                (PhysicalDirection.RIGHT, PhysicalDirection.LEFT, PhysicalDirection.REST)
            )
            return (
                (cls._body("body-a", profile, positive_axis, speed, direction, rng),),
                SystemBoundary(isolated=True),
            )

        first_speed = rng.choice(profile.speed_magnitudes_m_per_s)
        second_speed = rng.choice(profile.speed_magnitudes_m_per_s)
        bodies = (
            cls._body("body-a", profile, positive_axis, first_speed, PhysicalDirection.RIGHT, rng),
            cls._body("body-b", profile, positive_axis, second_speed, PhysicalDirection.LEFT, rng),
        )
        if family is MomentumScenarioFamily.OPPOSITE_MOVING_ISOLATED:
            return bodies, SystemBoundary(isolated=True)
        if family is MomentumScenarioFamily.EXTERNAL_IMPULSE:
            magnitude = rng.choice(profile.external_impulse_magnitudes_n_s)
            direction = rng.choice((PhysicalDirection.RIGHT, PhysicalDirection.LEFT))
            signed_impulse = cls._signed_value(magnitude, direction, positive_axis)
            return bodies, SystemBoundary(False, Impulse(signed_impulse))
        raise ValueError("unsupported MomentumScenarioFamily")

    @staticmethod
    def _body(
        identifier: str,
        profile: MomentumDifficultyProfile,
        positive_axis: PositiveAxis,
        speed: float,
        direction: PhysicalDirection,
        rng: Random,
    ) -> MomentumBody:
        mass = rng.choice(profile.masses_kg)
        return MomentumBody(
            identifier,
            Kilograms(mass),
            MetresPerSecond(MomentumScenarioFactory._signed_value(speed, direction, positive_axis)),
        )

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

    def _identifier(
        self,
        request: MomentumScenarioGenerationInput,
        family: MomentumScenarioFamily,
        positive_axis: PositiveAxis,
    ) -> str:
        return (
            f"mi-scenario-v{self.policy.policy_version}-{family}-"
            f"{request.difficulty.value}-{positive_axis.value}-seed-{request.seed.value}"
        )
