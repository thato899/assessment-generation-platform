"""Deterministic authored Work, Energy & Power scenario generation.

The factory chooses bounded authored facts and asks the authoritative M5 solver
to accept each candidate.  It never calculates or stores a derived answer.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from random import Random

from assessment_platform.core import Difficulty, GenerationProvenance, GenerationSeed

from .work_energy_power import (
    AlongPlaneWorkInput,
    AngleDegrees,
    AveragePowerInput,
    ConstantSpeedPowerInput,
    Displacement,
    EnergyState,
    ForceMagnitude,
    GravitationalFieldMagnitude,
    HeightState,
    KineticState,
    Mass,
    MassFlowRate,
    MechanicalEnergyContext,
    NetWorkInput,
    PumpingPowerInput,
    ReferenceLevel,
    RelativeHeight,
    SignedEnergy,
    SignedForce,
    Speed,
    SurfaceContext,
    TimeInterval,
    UnknownValue,
    WorkContribution,
    WorkEnergyAssumptions,
    WorkEnergyContext,
    WorkEnergyScenario,
)
from .work_energy_power_solver import FailureReason, WorkEnergySolveError, WorkEnergySolver

GENERATOR_ID = "caps-m5-work-energy-power-scenario-factory"
GENERATOR_VERSION = "1"
POLICY_VERSION = "1"
MAX_GENERATION_ATTEMPTS = 64


class WorkEnergyGenerationFamily(StrEnum):
    """Bounded authored problem families accepted by the M5 solver."""

    WORK_BY_FORCE = "work-by-force"
    NET_WORK = "net-work"
    ALONG_PLANE_WORK = "along-plane-work"
    KINETIC_ENERGY = "kinetic-energy"
    GRAVITATIONAL_POTENTIAL_ENERGY = "gravitational-potential-energy"
    WORK_ENERGY_NET_WORK = "work-energy-net-work"
    WORK_ENERGY_FINAL_SPEED = "work-energy-final-speed"
    WORK_ENERGY_INITIAL_SPEED = "work-energy-initial-speed"
    MECHANICAL_ENERGY_NON_CONSERVATIVE_WORK = "mechanical-energy-non-conservative-work"
    MECHANICAL_ENERGY_FINAL_SPEED = "mechanical-energy-final-speed"
    AVERAGE_POWER = "average-power"
    CONSTANT_SPEED_POWER = "constant-speed-power"
    PUMPING_POWER = "pumping-power"


@dataclass(frozen=True, slots=True)
class WorkEnergyGenerationInput:
    """Immutable inputs for one deterministic generation request."""

    seed: GenerationSeed
    family: WorkEnergyGenerationFamily | None = None
    difficulty: Difficulty = Difficulty.MODERATE

    def __post_init__(self) -> None:
        if not isinstance(self.seed, GenerationSeed):
            raise ValueError("Work, Energy & Power generation seed must be a GenerationSeed")
        if self.family is not None and not isinstance(self.family, WorkEnergyGenerationFamily):
            raise ValueError(
                "Work, Energy & Power generation family must be a WorkEnergyGenerationFamily"
            )
        if not isinstance(self.difficulty, Difficulty):
            raise ValueError("Work, Energy & Power generation difficulty must be a Difficulty")


def _numeric_pool(
    values: tuple[float, ...], name: str, *, minimum: float | None = None
) -> tuple[float, ...]:
    result = tuple(values)
    if not result:
        raise ValueError(f"{name} pool must not be empty")
    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not isfinite(value)
        or (minimum is not None and value < minimum)
        for value in result
    ):
        qualifier = f" >= {minimum}" if minimum is not None else ""
        raise ValueError(f"{name} pool must contain finite numeric values{qualifier}")
    if len(result) != len(set(result)):
        raise ValueError(f"{name} pool must not contain duplicates")
    return tuple(float(value) for value in result)


@dataclass(frozen=True, slots=True)
class WorkEnergyDifficultyProfile:
    """Immutable finite pools for one pedagogical difficulty level."""

    masses_kg: tuple[float, ...]
    force_magnitudes_n: tuple[float, ...]
    displacements_m: tuple[float, ...]
    angles_degrees: tuple[float, ...]
    speeds_m_per_s: tuple[float, ...]
    relative_heights_m: tuple[float, ...]
    gravitational_fields_m_per_s2: tuple[float, ...]
    time_intervals_s: tuple[float, ...]
    mass_flow_rates_kg_per_s: tuple[float, ...]
    along_motion_force_magnitudes_n: tuple[float, ...]
    non_conservative_work_j: tuple[float, ...]
    net_contribution_counts: tuple[int, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "masses_kg", _numeric_pool(self.masses_kg, "mass", minimum=0.0))
        if any(value == 0 for value in self.masses_kg):
            raise ValueError("mass pool must contain positive values")
        object.__setattr__(
            self,
            "force_magnitudes_n",
            _numeric_pool(self.force_magnitudes_n, "force magnitude", minimum=0.0),
        )
        object.__setattr__(
            self,
            "displacements_m",
            _numeric_pool(self.displacements_m, "displacement", minimum=0.0),
        )
        angles = _numeric_pool(self.angles_degrees, "angle", minimum=0.0)
        if any(value > 180 for value in angles):
            raise ValueError("angle pool must be between 0 and 180 degrees")
        object.__setattr__(self, "angles_degrees", angles)
        object.__setattr__(
            self, "speeds_m_per_s", _numeric_pool(self.speeds_m_per_s, "speed", minimum=0.0)
        )
        object.__setattr__(
            self,
            "relative_heights_m",
            _numeric_pool(self.relative_heights_m, "relative height"),
        )
        object.__setattr__(
            self,
            "gravitational_fields_m_per_s2",
            _numeric_pool(self.gravitational_fields_m_per_s2, "gravitational field", minimum=0.0),
        )
        if any(value == 0 for value in self.gravitational_fields_m_per_s2):
            raise ValueError("gravitational field pool must contain positive values")
        object.__setattr__(
            self,
            "time_intervals_s",
            _numeric_pool(self.time_intervals_s, "time interval", minimum=0.0),
        )
        if any(value == 0 for value in self.time_intervals_s):
            raise ValueError("time interval pool must contain positive values")
        object.__setattr__(
            self,
            "mass_flow_rates_kg_per_s",
            _numeric_pool(self.mass_flow_rates_kg_per_s, "mass-flow rate", minimum=0.0),
        )
        if any(value == 0 for value in self.mass_flow_rates_kg_per_s):
            raise ValueError("mass-flow rate pool must contain positive values")
        object.__setattr__(
            self,
            "along_motion_force_magnitudes_n",
            _numeric_pool(
                self.along_motion_force_magnitudes_n,
                "along-motion force magnitude",
                minimum=0.0,
            ),
        )
        object.__setattr__(
            self,
            "non_conservative_work_j",
            _numeric_pool(self.non_conservative_work_j, "non-conservative work"),
        )
        counts = tuple(self.net_contribution_counts)
        if not counts or any(
            isinstance(value, bool) or not isinstance(value, int) or value < 1 for value in counts
        ):
            raise ValueError("net contribution count pool must contain positive integers")
        if len(counts) != len(set(counts)):
            raise ValueError("net contribution count pool must not contain duplicates")
        object.__setattr__(self, "net_contribution_counts", counts)

    @property
    def speed_magnitudes_m_per_s(self) -> tuple[float, ...]:
        """Compatibility spelling used by the other mechanics factories."""

        return self.speeds_m_per_s

    @property
    def relative_height_values_m(self) -> tuple[float, ...]:
        return self.relative_heights_m

    @property
    def gravitational_fields_m_s2(self) -> tuple[float, ...]:
        return self.gravitational_fields_m_per_s2

    @property
    def mass_flow_rates_kg_s(self) -> tuple[float, ...]:
        return self.mass_flow_rates_kg_per_s


@dataclass(frozen=True, slots=True)
class WorkEnergyGenerationPolicy:
    """Versioned policy defining supported families and finite value pools."""

    policy_version: str = POLICY_VERSION
    allowed_families: tuple[WorkEnergyGenerationFamily, ...] = tuple(WorkEnergyGenerationFamily)
    introductory: WorkEnergyDifficultyProfile = WorkEnergyDifficultyProfile(
        (2.0, 3.0),
        (0.0, 4.0, 8.0),
        (1.0, 2.0),
        (0.0, 90.0, 180.0),
        (1.0, 3.0),
        (-1.0, 0.0, 2.0),
        (9.8,),
        (2.0, 4.0),
        (1.0, 2.0),
        (4.0, 8.0),
        (-8.0, 0.0, 8.0),
        (1, 2),
    )
    moderate: WorkEnergyDifficultyProfile = WorkEnergyDifficultyProfile(
        (2.0, 3.0, 4.0),
        (0.0, 6.0, 9.0, 12.0),
        (1.0, 2.0, 3.0),
        (0.0, 45.0, 90.0, 135.0, 180.0),
        (2.0, 4.0),
        (-2.0, 1.0, 3.0),
        (9.8, 10.0),
        (3.0, 5.0),
        (2.0, 4.0),
        (6.0, 9.0, 12.0),
        (-12.0, 0.0, 12.0),
        (2, 3),
    )
    advanced: WorkEnergyDifficultyProfile = WorkEnergyDifficultyProfile(
        (3.0, 4.0, 5.0),
        (0.0, 4.0, 8.0, 10.0, 12.0),
        (1.0, 2.0, 3.0, 4.0),
        (0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0),
        (1.0, 3.0, 5.0),
        (-3.0, 2.0, 5.0),
        (9.8, 10.0),
        (2.5, 4.5),
        (3.0, 6.0),
        (4.0, 8.0, 10.0, 12.0),
        (-16.0, -8.0, 0.0, 8.0, 16.0),
        (2, 3),
    )

    def __post_init__(self) -> None:
        if not isinstance(self.policy_version, str) or not self.policy_version.strip():
            raise ValueError("policy version must be a non-empty string")
        families = tuple(self.allowed_families)
        if not families or any(
            not isinstance(item, WorkEnergyGenerationFamily) for item in families
        ):
            raise ValueError("allowed families must contain WorkEnergyGenerationFamily values")
        if len(families) != len(set(families)):
            raise ValueError("allowed families must not contain duplicates")
        for profile in (self.introductory, self.moderate, self.advanced):
            if not isinstance(profile, WorkEnergyDifficultyProfile):
                raise ValueError("difficulty profiles must be WorkEnergyDifficultyProfile values")
        object.__setattr__(self, "policy_version", self.policy_version.strip())
        object.__setattr__(self, "allowed_families", families)

    def profile_for(self, difficulty: Difficulty) -> WorkEnergyDifficultyProfile:
        if not isinstance(difficulty, Difficulty):
            raise ValueError("difficulty must be a Difficulty")
        return {
            Difficulty.INTRODUCTORY: self.introductory,
            Difficulty.MODERATE: self.moderate,
            Difficulty.ADVANCED: self.advanced,
        }[difficulty]


DEFAULT_WORK_ENERGY_GENERATION_POLICY = WorkEnergyGenerationPolicy()


def _text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True, slots=True)
class GeneratedWorkEnergyMetadata:
    identifier: str
    family: WorkEnergyGenerationFamily
    difficulty: Difficulty
    policy_version: str
    provenance: GenerationProvenance

    def __post_init__(self) -> None:
        object.__setattr__(self, "identifier", _text(self.identifier, "generated identifier"))
        if not isinstance(self.family, WorkEnergyGenerationFamily):
            raise ValueError("generated family must be WorkEnergyGenerationFamily")
        if not isinstance(self.difficulty, Difficulty):
            raise ValueError("generated difficulty must be Difficulty")
        object.__setattr__(self, "policy_version", _text(self.policy_version, "policy version"))
        if not isinstance(self.provenance, GenerationProvenance):
            raise ValueError("generated provenance must be GenerationProvenance")


@dataclass(frozen=True, slots=True)
class GeneratedWorkEnergyProblem:
    """Generated authored scenario plus non-answer target metadata."""

    metadata: GeneratedWorkEnergyMetadata
    scenario: WorkEnergyScenario
    target_id: str | None = None
    authored_mass: Mass | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.metadata, GeneratedWorkEnergyMetadata):
            raise ValueError("generated metadata must be GeneratedWorkEnergyMetadata")
        if not isinstance(self.scenario, WorkEnergyScenario):
            raise ValueError("generated scenario must be WorkEnergyScenario")
        if self.scenario.identifier != self.metadata.identifier:
            raise ValueError("generated scenario and metadata identifiers must agree")
        if self.target_id is not None:
            object.__setattr__(self, "target_id", _text(self.target_id, "target ID"))
        if self.authored_mass is not None and not isinstance(self.authored_mass, Mass):
            raise ValueError("authored mass must be Mass or None")

    @property
    def identifier(self) -> str:
        return self.metadata.identifier

    @property
    def family(self) -> WorkEnergyGenerationFamily:
        return self.metadata.family

    @property
    def difficulty(self) -> Difficulty:
        return self.metadata.difficulty

    @property
    def provenance(self) -> GenerationProvenance:
        return self.metadata.provenance

    @property
    def target(self) -> str | None:
        """Answer-free target identity for downstream family routing."""

        return self.target_id

    @property
    def mass(self) -> Mass | None:
        """Authored mass needed by the standalone potential-energy operation."""

        return self.authored_mass


# These aliases keep downstream family naming flexible without adding answer-bearing
# subclasses or duplicating the wrapper semantics.
GeneratedWorkProblem = GeneratedWorkEnergyProblem
GeneratedWorkEnergyTheoremProblem = GeneratedWorkEnergyProblem
GeneratedMechanicalEnergyProblem = GeneratedWorkEnergyProblem
GeneratedPowerProblem = GeneratedWorkEnergyProblem


class WorkEnergyProblemFactory:
    """Create solver-accepted authored scenarios from a versioned local policy."""

    def __init__(
        self, policy: WorkEnergyGenerationPolicy = DEFAULT_WORK_ENERGY_GENERATION_POLICY
    ) -> None:
        if not isinstance(policy, WorkEnergyGenerationPolicy):
            raise ValueError("policy must be a WorkEnergyGenerationPolicy")
        self.policy = policy

    def generate(self, request: WorkEnergyGenerationInput) -> GeneratedWorkEnergyProblem:
        if not isinstance(request, WorkEnergyGenerationInput):
            raise ValueError("request must be a WorkEnergyGenerationInput")
        family = self._family_for(request)
        profile = self.policy.profile_for(request.difficulty)
        rng = Random(request.seed.value)
        scenario, target_id, authored_mass = self._generate_family(family, request, profile, rng)
        metadata = self._metadata(request, family)
        if scenario.identifier != metadata.identifier:
            raise ValueError("generated scenario identifier was not policy-stable")
        problem = GeneratedWorkEnergyProblem(metadata, scenario, target_id, authored_mass)
        self._validate_generated(problem)
        return problem

    def _family_for(self, request: WorkEnergyGenerationInput) -> WorkEnergyGenerationFamily:
        if request.family is not None:
            if request.family not in self.policy.allowed_families:
                raise ValueError("requested Work, Energy & Power family is not allowed by policy")
            return request.family
        return Random(request.seed.value).choice(self.policy.allowed_families)

    def _metadata(
        self, request: WorkEnergyGenerationInput, family: WorkEnergyGenerationFamily
    ) -> GeneratedWorkEnergyMetadata:
        identifier = (
            f"wep-problem-v{self.policy.policy_version}-{family.value}-"
            f"{request.difficulty.value}-seed-{request.seed.value}"
        )
        provenance = GenerationProvenance(
            GENERATOR_ID,
            GENERATOR_VERSION,
            request.seed,
            (family.value, request.difficulty.value, f"policy-{self.policy.policy_version}"),
        )
        return GeneratedWorkEnergyMetadata(
            identifier, family, request.difficulty, self.policy.policy_version, provenance
        )

    def _generate_family(
        self,
        family: WorkEnergyGenerationFamily,
        request: WorkEnergyGenerationInput,
        profile: WorkEnergyDifficultyProfile,
        rng: Random,
    ) -> tuple[WorkEnergyScenario, str | None, Mass | None]:
        identifier = self._identifier(request, family)
        if family is WorkEnergyGenerationFamily.WORK_BY_FORCE:
            contribution = self._contribution("force-a", profile, rng)
            work_input = NetWorkInput((contribution,))
            return (
                self._scenario(
                    identifier,
                    work_inputs=(work_input,),
                    assumptions=WorkEnergyAssumptions(constant_force=True),
                ),
                None,
                None,
            )
        if family is WorkEnergyGenerationFamily.NET_WORK:
            count = max(2, rng.choice(profile.net_contribution_counts))
            contributions = tuple(
                self._contribution(f"force-{chr(97 + index)}", profile, rng)
                for index in range(count)
            )
            work_input = NetWorkInput(contributions)
            return (
                self._scenario(
                    identifier,
                    work_inputs=(work_input,),
                    assumptions=WorkEnergyAssumptions(constant_force=True),
                ),
                None,
                None,
            )
        if family is WorkEnergyGenerationFamily.ALONG_PLANE_WORK:
            along_input = AlongPlaneWorkInput(
                self._signed_force(profile, rng),
                Displacement(rng.choice(profile.displacements_m)),
            )
            return (
                self._scenario(
                    identifier,
                    work_inputs=(along_input,),
                    assumptions=WorkEnergyAssumptions(constant_force=True),
                ),
                None,
                None,
            )
        if family is WorkEnergyGenerationFamily.KINETIC_ENERGY:
            kinetic_state = self._kinetic_state("kinetic-state", EnergyState.INITIAL, profile, rng)
            return (
                self._scenario(
                    identifier,
                    kinetic_states=(kinetic_state,),
                    assumptions=WorkEnergyAssumptions(constant_mass=True),
                ),
                None,
                None,
            )
        if family is WorkEnergyGenerationFamily.GRAVITATIONAL_POTENTIAL_ENERGY:
            mass = Mass(rng.choice(profile.masses_kg))
            level = ReferenceLevel("reference-ground")
            height_state = HeightState(
                "potential-state",
                EnergyState.INITIAL,
                level,
                RelativeHeight(rng.choice(profile.relative_heights_m)),
                GravitationalFieldMagnitude(rng.choice(profile.gravitational_fields_m_per_s2)),
            )
            return (
                self._scenario(
                    identifier,
                    reference_levels=(level,),
                    height_states=(height_state,),
                    assumptions=WorkEnergyAssumptions(
                        near_earth_field=True, reference_level_declared=True
                    ),
                ),
                None,
                mass,
            )
        if family is WorkEnergyGenerationFamily.WORK_ENERGY_NET_WORK:
            return self._work_energy_net_work(identifier, profile, rng)
        if family is WorkEnergyGenerationFamily.WORK_ENERGY_FINAL_SPEED:
            return self._work_energy_speed(identifier, profile, rng, final_unknown=True)
        if family is WorkEnergyGenerationFamily.WORK_ENERGY_INITIAL_SPEED:
            return self._work_energy_speed(identifier, profile, rng, final_unknown=False)
        if family is WorkEnergyGenerationFamily.MECHANICAL_ENERGY_NON_CONSERVATIVE_WORK:
            return self._mechanical_energy_non_conservative(identifier, profile, rng)
        if family is WorkEnergyGenerationFamily.MECHANICAL_ENERGY_FINAL_SPEED:
            return self._mechanical_energy_speed(identifier, profile, rng)
        if family is WorkEnergyGenerationFamily.AVERAGE_POWER:
            average_input = AveragePowerInput(
                SignedEnergy(rng.choice(profile.non_conservative_work_j)),
                TimeInterval(rng.choice(profile.time_intervals_s)),
            )
            return self._scenario(identifier, average_power_inputs=(average_input,)), None, None
        if family is WorkEnergyGenerationFamily.CONSTANT_SPEED_POWER:
            constant_speed_input = ConstantSpeedPowerInput(
                self._signed_force(profile, rng),
                Speed(rng.choice(profile.speeds_m_per_s)),
                SurfaceContext.INCLINED if rng.randrange(2) else SurfaceContext.HORIZONTAL,
            )
            return (
                self._scenario(
                    identifier,
                    constant_speed_power_inputs=(constant_speed_input,),
                    assumptions=WorkEnergyAssumptions(constant_speed=True),
                ),
                None,
                None,
            )
        if family is WorkEnergyGenerationFamily.PUMPING_POWER:
            pumping_input = PumpingPowerInput(
                MassFlowRate(rng.choice(profile.mass_flow_rates_kg_per_s)),
                Displacement(rng.choice(profile.displacements_m)),
                GravitationalFieldMagnitude(rng.choice(profile.gravitational_fields_m_per_s2)),
            )
            return (
                self._scenario(
                    identifier,
                    pumping_power_inputs=(pumping_input,),
                    assumptions=WorkEnergyAssumptions(near_earth_field=True),
                ),
                None,
                None,
            )
        raise ValueError("unsupported WorkEnergyGenerationFamily")

    @staticmethod
    def _scenario(
        identifier: str,
        *,
        work_inputs: tuple[NetWorkInput | AlongPlaneWorkInput, ...] = (),
        kinetic_states: tuple[KineticState, ...] = (),
        reference_levels: tuple[ReferenceLevel, ...] = (),
        height_states: tuple[HeightState, ...] = (),
        work_energy_contexts: tuple[WorkEnergyContext, ...] = (),
        mechanical_energy_contexts: tuple[MechanicalEnergyContext, ...] = (),
        average_power_inputs: tuple[AveragePowerInput, ...] = (),
        constant_speed_power_inputs: tuple[ConstantSpeedPowerInput, ...] = (),
        pumping_power_inputs: tuple[PumpingPowerInput, ...] = (),
        assumptions: WorkEnergyAssumptions | None = None,
    ) -> WorkEnergyScenario:
        return WorkEnergyScenario(
            identifier,
            work_inputs,
            kinetic_states,
            reference_levels,
            height_states,
            work_energy_contexts,
            mechanical_energy_contexts,
            average_power_inputs,
            constant_speed_power_inputs,
            pumping_power_inputs,
            WorkEnergyAssumptions() if assumptions is None else assumptions,
        )

    @staticmethod
    def _kinetic_state(
        identifier: str,
        state: EnergyState,
        profile: WorkEnergyDifficultyProfile,
        rng: Random,
        *,
        speed_unknown: bool = False,
    ) -> KineticState:
        return KineticState(
            identifier,
            state,
            Mass(rng.choice(profile.masses_kg)),
            UnknownValue.UNKNOWN if speed_unknown else Speed(rng.choice(profile.speeds_m_per_s)),
        )

    @staticmethod
    def _contribution(
        identifier: str, profile: WorkEnergyDifficultyProfile, rng: Random
    ) -> WorkContribution:
        return WorkContribution(
            identifier,
            ForceMagnitude(rng.choice(profile.force_magnitudes_n)),
            Displacement(rng.choice(profile.displacements_m)),
            AngleDegrees(rng.choice(profile.angles_degrees)),
        )

    @staticmethod
    def _signed_force(profile: WorkEnergyDifficultyProfile, rng: Random) -> SignedForce:
        magnitude = rng.choice(profile.along_motion_force_magnitudes_n)
        return SignedForce(magnitude if rng.randrange(2) else -magnitude)

    def _work_energy_net_work(
        self, identifier: str, profile: WorkEnergyDifficultyProfile, rng: Random
    ) -> tuple[WorkEnergyScenario, str | None, Mass | None]:
        for _ in range(MAX_GENERATION_ATTEMPTS):
            mass = rng.choice(profile.masses_kg)
            initial = KineticState(
                "initial-state",
                EnergyState.INITIAL,
                Mass(mass),
                Speed(rng.choice(profile.speeds_m_per_s)),
            )
            final = KineticState(
                "final-state",
                EnergyState.FINAL,
                Mass(mass),
                Speed(rng.choice(profile.speeds_m_per_s)),
            )
            contribution = self._contribution("work-input", profile, rng)
            work_input = NetWorkInput((contribution,))
            context = WorkEnergyContext(initial, final, UnknownValue.UNKNOWN, work_input)
            scenario = self._scenario(
                identifier,
                work_inputs=(work_input,),
                kinetic_states=(initial, final),
                work_energy_contexts=(context,),
                assumptions=WorkEnergyAssumptions(
                    inertial_frame=True, constant_mass=True, constant_force=True
                ),
            )
            try:
                WorkEnergySolver().work_energy(context)
                return scenario, "net-work", None
            except WorkEnergySolveError as error:
                if error.reason not in (FailureReason.INCONSISTENT, FailureReason.NUMERICAL_RANGE):
                    raise
        raise ValueError("policy could not produce a solver-accepted work-energy net-work case")

    def _work_energy_speed(
        self,
        identifier: str,
        profile: WorkEnergyDifficultyProfile,
        rng: Random,
        *,
        final_unknown: bool,
    ) -> tuple[WorkEnergyScenario, str | None, Mass | None]:
        for _ in range(MAX_GENERATION_ATTEMPTS):
            mass = Mass(rng.choice(profile.masses_kg))
            initial_speed = (
                UnknownValue.UNKNOWN
                if not final_unknown
                else Speed(rng.choice(profile.speeds_m_per_s))
            )
            final_speed = (
                UnknownValue.UNKNOWN if final_unknown else Speed(rng.choice(profile.speeds_m_per_s))
            )
            initial = KineticState("initial-state", EnergyState.INITIAL, mass, initial_speed)
            final = KineticState("final-state", EnergyState.FINAL, mass, final_speed)
            context = WorkEnergyContext(
                initial,
                final,
                SignedEnergy(rng.choice(profile.non_conservative_work_j)),
            )
            scenario = self._scenario(
                identifier,
                kinetic_states=(initial, final),
                work_energy_contexts=(context,),
                assumptions=WorkEnergyAssumptions(inertial_frame=True, constant_mass=True),
            )
            try:
                WorkEnergySolver().work_energy(context)
                target = "final-speed" if final_unknown else "initial-speed"
                return scenario, target, None
            except WorkEnergySolveError as error:
                if error.reason not in (FailureReason.INCONSISTENT, FailureReason.NUMERICAL_RANGE):
                    raise
        raise ValueError("policy could not produce a solver-accepted work-energy speed case")

    def _mechanical_energy_non_conservative(
        self, identifier: str, profile: WorkEnergyDifficultyProfile, rng: Random
    ) -> tuple[WorkEnergyScenario, str | None, Mass | None]:
        mass = Mass(rng.choice(profile.masses_kg))
        level = ReferenceLevel("reference-ground")
        field = GravitationalFieldMagnitude(rng.choice(profile.gravitational_fields_m_per_s2))
        initial = self._kinetic_state("initial-state", EnergyState.INITIAL, profile, rng)
        final = KineticState(
            "final-state",
            EnergyState.FINAL,
            mass,
            Speed(rng.choice(profile.speeds_m_per_s)),
        )
        initial = KineticState(initial.identifier, initial.state, mass, initial.speed)
        initial_height = HeightState(
            "initial-height",
            EnergyState.INITIAL,
            level,
            RelativeHeight(rng.choice(profile.relative_heights_m)),
            field,
        )
        final_height = HeightState(
            "final-height",
            EnergyState.FINAL,
            level,
            RelativeHeight(rng.choice(profile.relative_heights_m)),
            field,
        )
        context = MechanicalEnergyContext(initial, final, initial_height, final_height)
        scenario = self._scenario(
            identifier,
            kinetic_states=(initial, final),
            reference_levels=(level,),
            height_states=(initial_height, final_height),
            mechanical_energy_contexts=(context,),
            assumptions=WorkEnergyAssumptions(
                inertial_frame=True,
                constant_mass=True,
                near_earth_field=True,
                reference_level_declared=True,
            ),
        )
        WorkEnergySolver().mechanical_energy(context)
        return scenario, "non-conservative-work", None

    def _mechanical_energy_speed(
        self, identifier: str, profile: WorkEnergyDifficultyProfile, rng: Random
    ) -> tuple[WorkEnergyScenario, str | None, Mass | None]:
        for _ in range(MAX_GENERATION_ATTEMPTS):
            mass = Mass(rng.choice(profile.masses_kg))
            level = ReferenceLevel("reference-ground")
            field = GravitationalFieldMagnitude(rng.choice(profile.gravitational_fields_m_per_s2))
            initial = KineticState(
                "initial-state",
                EnergyState.INITIAL,
                mass,
                Speed(rng.choice(profile.speeds_m_per_s)),
            )
            final = KineticState("final-state", EnergyState.FINAL, mass, UnknownValue.UNKNOWN)
            initial_height = HeightState(
                "initial-height",
                EnergyState.INITIAL,
                level,
                RelativeHeight(rng.choice(profile.relative_heights_m)),
                field,
            )
            final_height = HeightState(
                "final-height",
                EnergyState.FINAL,
                level,
                RelativeHeight(rng.choice(profile.relative_heights_m)),
                field,
            )
            context = MechanicalEnergyContext(
                initial,
                final,
                initial_height,
                final_height,
                SignedEnergy(rng.choice(profile.non_conservative_work_j)),
            )
            scenario = self._scenario(
                identifier,
                kinetic_states=(initial, final),
                reference_levels=(level,),
                height_states=(initial_height, final_height),
                mechanical_energy_contexts=(context,),
                assumptions=WorkEnergyAssumptions(
                    inertial_frame=True,
                    constant_mass=True,
                    near_earth_field=True,
                    reference_level_declared=True,
                ),
            )
            try:
                WorkEnergySolver().mechanical_energy(context)
                return scenario, "final-speed", None
            except WorkEnergySolveError as error:
                if error.reason not in (FailureReason.INCONSISTENT, FailureReason.NUMERICAL_RANGE):
                    raise
        raise ValueError("policy could not produce a solver-accepted mechanical-energy case")

    def _identifier(
        self, request: WorkEnergyGenerationInput, family: WorkEnergyGenerationFamily
    ) -> str:
        return (
            f"wep-problem-v{self.policy.policy_version}-{family.value}-"
            f"{request.difficulty.value}-seed-{request.seed.value}"
        )

    @staticmethod
    def _validate_generated(problem: GeneratedWorkEnergyProblem) -> None:
        solver = WorkEnergySolver()
        scenario = problem.scenario
        family = problem.family
        if family is WorkEnergyGenerationFamily.WORK_BY_FORCE:
            authored = scenario.work_inputs[0]
            assert isinstance(authored, NetWorkInput)
            solver.work_by_force(authored.contributions[0])
        elif family is WorkEnergyGenerationFamily.NET_WORK:
            authored = scenario.work_inputs[0]
            assert isinstance(authored, NetWorkInput)
            solver.net_work(authored)
        elif family is WorkEnergyGenerationFamily.ALONG_PLANE_WORK:
            authored = scenario.work_inputs[0]
            assert isinstance(authored, AlongPlaneWorkInput)
            solver.along_plane_work(authored)
        elif family is WorkEnergyGenerationFamily.KINETIC_ENERGY:
            solver.kinetic_energy(scenario.kinetic_states[0])
        elif family is WorkEnergyGenerationFamily.GRAVITATIONAL_POTENTIAL_ENERGY:
            assert problem.authored_mass is not None
            solver.potential_energy(problem.authored_mass, scenario.height_states[0])
        elif family in (
            WorkEnergyGenerationFamily.WORK_ENERGY_NET_WORK,
            WorkEnergyGenerationFamily.WORK_ENERGY_FINAL_SPEED,
            WorkEnergyGenerationFamily.WORK_ENERGY_INITIAL_SPEED,
        ):
            solver.work_energy(scenario.work_energy_contexts[0])
        elif family in (
            WorkEnergyGenerationFamily.MECHANICAL_ENERGY_NON_CONSERVATIVE_WORK,
            WorkEnergyGenerationFamily.MECHANICAL_ENERGY_FINAL_SPEED,
        ):
            solver.mechanical_energy(scenario.mechanical_energy_contexts[0])
        elif family is WorkEnergyGenerationFamily.AVERAGE_POWER:
            solver.average_power(scenario.average_power_inputs[0])
        elif family is WorkEnergyGenerationFamily.CONSTANT_SPEED_POWER:
            solver.constant_speed_power(scenario.constant_speed_power_inputs[0])
        elif family is WorkEnergyGenerationFamily.PUMPING_POWER:
            solver.pumping_power(scenario.pumping_power_inputs[0])
        else:
            raise ValueError("unsupported generated family")


__all__ = [
    "DEFAULT_WORK_ENERGY_GENERATION_POLICY",
    "GeneratedMechanicalEnergyProblem",
    "GeneratedPowerProblem",
    "GeneratedWorkEnergyMetadata",
    "GeneratedWorkEnergyProblem",
    "GeneratedWorkEnergyTheoremProblem",
    "GeneratedWorkProblem",
    "GENERATOR_ID",
    "GENERATOR_VERSION",
    "MAX_GENERATION_ATTEMPTS",
    "POLICY_VERSION",
    "WorkEnergyDifficultyProfile",
    "WorkEnergyGenerationFamily",
    "WorkEnergyGenerationInput",
    "WorkEnergyGenerationPolicy",
    "WorkEnergyProblemFactory",
]
