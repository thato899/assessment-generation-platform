"""Deterministic policy-driven generation of vertical-projectile scenarios."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from random import Random

from assessment_platform.core import Difficulty, GenerationProvenance, GenerationSeed
from assessment_platform.domains.physical_sciences.mechanics.vertical_projectile import (
    LaunchDirection,
    Metres,
    MetresPerSecond,
    MetresPerSecondSquared,
    PositiveDirection,
    ScenarioType,
    VerticalProjectileScenario,
)

FACTORY_ID = "caps-grade-12-vertical-projectile-scenario-factory"
POLICY_VERSION = "1"


class ScenarioFamily(StrEnum):
    """Pedagogically distinct initial-condition families."""

    UPWARD_GROUND = "upward-ground"
    UPWARD_ELEVATED = "upward-elevated"
    DOWNWARD_ELEVATED = "downward-elevated"
    DROPPED_FROM_REST = "dropped-from-rest"


@dataclass(frozen=True, slots=True)
class ScenarioGenerationInput:
    """Explicit inputs for one deterministic scenario-generation request."""

    seed: GenerationSeed
    family: ScenarioFamily | None = None
    difficulty: Difficulty = Difficulty.MODERATE
    positive_direction: PositiveDirection = PositiveDirection.UP

    def __post_init__(self) -> None:
        if not isinstance(self.seed, GenerationSeed):
            raise ValueError("scenario generation seed must be a GenerationSeed")
        if self.family is not None and not isinstance(self.family, ScenarioFamily):
            raise ValueError("scenario generation family must be a ScenarioFamily")
        if not isinstance(self.difficulty, Difficulty):
            raise ValueError("scenario generation difficulty must be a Difficulty")
        if not isinstance(self.positive_direction, PositiveDirection):
            raise ValueError("scenario generation positive_direction must be explicit")


@dataclass(frozen=True, slots=True)
class DifficultyProfile:
    """Discrete platform-generation pools for one difficulty level.

    These values are generation policy, not a complete statement of CAPS
    curriculum constraints. Curriculum validation remains a separate concern.
    """

    initial_speeds: tuple[int, ...]
    elevated_heights: tuple[int, ...]

    def __post_init__(self) -> None:
        speeds = tuple(self.initial_speeds)
        heights = tuple(self.elevated_heights)
        if not speeds or any(
            isinstance(value, bool) or not isinstance(value, int) for value in speeds
        ):
            raise ValueError("initial speed pool must contain integers")
        if any(value <= 0 for value in speeds):
            raise ValueError("initial speed pool must contain positive values")
        if not heights or any(
            isinstance(value, bool) or not isinstance(value, int) for value in heights
        ):
            raise ValueError("elevated height pool must contain integers")
        if any(value <= 0 for value in heights):
            raise ValueError("elevated height pool must contain positive values")
        if len(speeds) != len(set(speeds)) or len(heights) != len(set(heights)):
            raise ValueError("generation pools must not contain duplicate values")
        object.__setattr__(self, "initial_speeds", speeds)
        object.__setattr__(self, "elevated_heights", heights)


@dataclass(frozen=True, slots=True)
class VerticalProjectileGenerationPolicy:
    """Versioned, immutable platform policy for scenario numeric generation."""

    policy_version: str = POLICY_VERSION
    gravity_magnitude: float = 10.0
    allowed_families: tuple[ScenarioFamily, ...] = (
        ScenarioFamily.UPWARD_GROUND,
        ScenarioFamily.UPWARD_ELEVATED,
        ScenarioFamily.DOWNWARD_ELEVATED,
        ScenarioFamily.DROPPED_FROM_REST,
    )
    introductory: DifficultyProfile = DifficultyProfile((10, 15), (5, 10))
    moderate: DifficultyProfile = DifficultyProfile((15, 20, 25), (10, 15, 20, 25))
    advanced: DifficultyProfile = DifficultyProfile((20, 25, 30), (15, 20, 25, 30))

    def __post_init__(self) -> None:
        if not isinstance(self.policy_version, str) or not self.policy_version.strip():
            raise ValueError("policy version must be a non-empty string")
        if (
            isinstance(self.gravity_magnitude, bool)
            or not isinstance(self.gravity_magnitude, (int, float))
            or not isfinite(self.gravity_magnitude)
            or self.gravity_magnitude <= 0
        ):
            raise ValueError("gravity magnitude must be a finite positive number")
        families = tuple(self.allowed_families)
        if not families or any(not isinstance(family, ScenarioFamily) for family in families):
            raise ValueError("allowed families must contain ScenarioFamily values")
        if len(families) != len(set(families)):
            raise ValueError("allowed families must not contain duplicates")
        for profile in (self.introductory, self.moderate, self.advanced):
            if not isinstance(profile, DifficultyProfile):
                raise ValueError("difficulty profiles must be DifficultyProfile values")
        object.__setattr__(self, "policy_version", self.policy_version.strip())
        object.__setattr__(self, "gravity_magnitude", float(self.gravity_magnitude))
        object.__setattr__(self, "allowed_families", families)

    def profile_for(self, difficulty: Difficulty) -> DifficultyProfile:
        if not isinstance(difficulty, Difficulty):
            raise ValueError("difficulty must be a Difficulty")
        return {
            Difficulty.INTRODUCTORY: self.introductory,
            Difficulty.MODERATE: self.moderate,
            Difficulty.ADVANCED: self.advanced,
        }[difficulty]


DEFAULT_GENERATION_POLICY = VerticalProjectileGenerationPolicy()


class VerticalProjectileScenarioFactory:
    """Create validated initial conditions without solving the trajectory."""

    def __init__(
        self, policy: VerticalProjectileGenerationPolicy = DEFAULT_GENERATION_POLICY
    ) -> None:
        if not isinstance(policy, VerticalProjectileGenerationPolicy):
            raise ValueError("policy must be a VerticalProjectileGenerationPolicy")
        self.policy = policy

    def generate(self, request: ScenarioGenerationInput) -> VerticalProjectileScenario:
        if not isinstance(request, ScenarioGenerationInput):
            raise ValueError("request must be a ScenarioGenerationInput")
        family = self._family_for(request)
        profile = self.policy.profile_for(request.difficulty)
        rng = Random(request.seed.value)
        speed = rng.choice(profile.initial_speeds)
        height = rng.choice(profile.elevated_heights)
        if (
            request.positive_direction is PositiveDirection.DOWN
            and family is not ScenarioFamily.UPWARD_GROUND
        ):
            raise ValueError(
                "down-positive generation currently supports only upward-ground scenarios"
            )

        position = 0.0 if family is ScenarioFamily.UPWARD_GROUND else float(height)
        launch_direction, scenario_type, signed_velocity = self._initial_conditions(
            family, request.positive_direction, speed
        )
        gravity_sign = -1.0 if request.positive_direction is PositiveDirection.UP else 1.0
        identifier = self._identifier(request, family)
        provenance = GenerationProvenance(
            FACTORY_ID,
            self.policy.policy_version,
            request.seed,
            (family.value, request.difficulty.value, request.positive_direction.value),
        )
        return VerticalProjectileScenario(
            identifier=identifier,
            launch_position=Metres(position),
            initial_velocity=MetresPerSecond(signed_velocity),
            gravitational_acceleration=MetresPerSecondSquared(
                gravity_sign * self.policy.gravity_magnitude
            ),
            positive_direction=request.positive_direction,
            launch_direction=launch_direction,
            scenario_type=scenario_type,
            seed=request.seed,
            provenance=provenance,
        )

    def _family_for(self, request: ScenarioGenerationInput) -> ScenarioFamily:
        if request.family is not None:
            if request.family not in self.policy.allowed_families:
                raise ValueError("requested scenario family is not allowed by the policy")
            return request.family
        allowed = self.policy.allowed_families
        if request.positive_direction is PositiveDirection.DOWN:
            allowed = tuple(family for family in allowed if family is ScenarioFamily.UPWARD_GROUND)
        if not allowed:
            raise ValueError("policy has no family compatible with the requested direction")
        return Random(request.seed.value).choice(allowed)

    @staticmethod
    def _initial_conditions(
        family: ScenarioFamily, positive_direction: PositiveDirection, speed: int
    ) -> tuple[LaunchDirection, ScenarioType, float]:
        if family in (ScenarioFamily.UPWARD_GROUND, ScenarioFamily.UPWARD_ELEVATED):
            launch_direction = LaunchDirection.UPWARD
            scenario_type = ScenarioType.PROJECTED_UPWARD
            signed_velocity = float(speed if positive_direction is PositiveDirection.UP else -speed)
        elif family is ScenarioFamily.DOWNWARD_ELEVATED:
            launch_direction = LaunchDirection.DOWNWARD
            scenario_type = ScenarioType.PROJECTED_DOWNWARD
            signed_velocity = float(-speed if positive_direction is PositiveDirection.UP else speed)
        else:
            launch_direction = LaunchDirection.REST
            scenario_type = ScenarioType.DROPPED_FROM_REST
            signed_velocity = 0.0
        return launch_direction, scenario_type, signed_velocity

    def _identifier(self, request: ScenarioGenerationInput, family: ScenarioFamily) -> str:
        return (
            f"vp-scenario-v{self.policy.policy_version}-{family.value}-"
            f"{request.difficulty.value}-{request.positive_direction.value}-seed-{request.seed.value}"
        )
