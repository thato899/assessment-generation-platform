"""Deterministic authored Newton scenario generation.

The factory selects bounded authored facts only.  All physical results are
obtained from :mod:`newton_solver` after a scenario has been constructed.
"""

# ruff: noqa: E501

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
from math import isfinite
from random import Random

from assessment_platform.core import Difficulty, GenerationProvenance, GenerationSeed

from .newton_solver import ComponentSign, NewtonSolver, StraightStringRequest
from .newtons_laws import (
    AccelerationVector,
    AuthoredAcceleration,
    BodyReference,
    CartesianCoordinates,
    CartesianDirection,
    Contact,
    EnvironmentReference,
    Force,
    ForceKind,
    ForceVector,
    Friction,
    FrictionCoefficient,
    FrictionRegime,
    GravitationalField,
    GravitationalInteraction,
    Kilograms,
    Metres,
    MetresPerSecondSquared,
    NewtonAssumptions,
    NewtonBody,
    Newtons,
    NewtonScenario,
    StringConnection,
    Surface,
    SurfaceCoordinates,
    SurfaceDirection,
    SystemBoundary,
    ThirdLawPair,
    UnknownValue,
)
from .newtons_laws.values import require_type

GENERATOR_ID = "caps-m4-newton-scenario-factory"
GENERATOR_VERSION = "1"
POLICY_VERSION = "1"
ENVIRONMENT = EnvironmentReference("environment")
EARTH = EnvironmentReference("earth")
CORD = EnvironmentReference("cord")
UNKNOWN = UnknownValue.UNKNOWN


class NewtonGenerationFamily(StrEnum):
    NEWTON_II = "newton-ii"
    UNKNOWN_FORCE = "unknown-force"
    EQUILIBRIUM = "equilibrium"
    WEIGHT = "weight"
    CONTACT_NORMAL = "contact-normal"
    STATIC_FRICTION = "static-friction"
    LIMITING_STATIC_FRICTION = "limiting-static-friction"
    KINETIC_FRICTION = "kinetic-friction"
    INCLINED_PLANE = "inclined-plane"
    CONNECTED_BODIES = "connected-bodies"
    UNIVERSAL_GRAVITATION = "universal-gravitation"
    THIRD_LAW = "third-law"


@dataclass(frozen=True, slots=True)
class NewtonGenerationInput:
    seed: GenerationSeed
    family: NewtonGenerationFamily | None = None
    difficulty: Difficulty = Difficulty.MODERATE

    def __post_init__(self) -> None:
        if not isinstance(self.seed, GenerationSeed):
            raise ValueError("Newton generation seed must be a GenerationSeed")
        if self.family is not None and not isinstance(self.family, NewtonGenerationFamily):
            raise ValueError("Newton generation family must be a NewtonGenerationFamily")
        if not isinstance(self.difficulty, Difficulty):
            raise ValueError("Newton generation difficulty must be a Difficulty")


@dataclass(frozen=True, slots=True)
class NewtonDifficultyProfile:
    masses_kg: tuple[float, ...]
    force_magnitudes_n: tuple[float, ...]
    normal_magnitudes_n: tuple[float, ...]
    acceleration_magnitudes_m_s2: tuple[float, ...]
    gravitational_fields_m_s2: tuple[float, ...]
    friction_coefficients: tuple[float, ...]
    inclinations_degrees: tuple[float, ...]
    separations_m: tuple[float, ...]

    def __post_init__(self) -> None:
        fields = (
            (self.masses_kg, "mass", True),
            (self.force_magnitudes_n, "force", True),
            (self.normal_magnitudes_n, "normal force", True),
            (self.acceleration_magnitudes_m_s2, "acceleration", True),
            (self.gravitational_fields_m_s2, "gravitational field", True),
            (self.friction_coefficients, "friction coefficient", False),
            (self.inclinations_degrees, "inclination", False),
            (self.separations_m, "separation", True),
        )
        for values, name, positive in fields:
            values = tuple(values)
            if not values or any(
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not isfinite(value)
                or (value <= 0 if positive else value < 0)
                for value in values
            ):
                qualifier = "positive" if positive else "non-negative"
                raise ValueError(f"{name} pool must contain finite {qualifier} values")
            if len(values) != len(set(values)):
                raise ValueError(f"{name} pool must not contain duplicates")
            object.__setattr__(self, self._field_for(name), values)

    @staticmethod
    def _field_for(name: str) -> str:
        return {
            "mass": "masses_kg",
            "force": "force_magnitudes_n",
            "normal force": "normal_magnitudes_n",
            "acceleration": "acceleration_magnitudes_m_s2",
            "gravitational field": "gravitational_fields_m_s2",
            "friction coefficient": "friction_coefficients",
            "inclination": "inclinations_degrees",
            "separation": "separations_m",
        }[name]


@dataclass(frozen=True, slots=True)
class NewtonGenerationPolicy:
    policy_version: str = POLICY_VERSION
    allowed_families: tuple[NewtonGenerationFamily, ...] = tuple(NewtonGenerationFamily)
    introductory: NewtonDifficultyProfile = NewtonDifficultyProfile(
        (2.0, 4.0), (4.0, 8.0), (10.0, 20.0), (2.0, 4.0), (10.0,), (0.5,), (0.0,), (2.0, 4.0)
    )
    moderate: NewtonDifficultyProfile = NewtonDifficultyProfile(
        (2.0, 4.0, 5.0),
        (4.0, 6.0, 10.0),
        (10.0, 20.0, 30.0),
        (2.0, 3.0, 5.0),
        (9.8, 10.0),
        (0.3, 0.5, 1.0),
        (20.0, 30.0),
        (2.0, 5.0, 10.0),
    )
    advanced: NewtonDifficultyProfile = NewtonDifficultyProfile(
        (3.0, 4.0, 6.0),
        (6.0, 10.0, 12.0),
        (12.0, 24.0, 36.0),
        (2.0, 4.0, 6.0),
        (9.8, 10.0),
        (0.4, 0.6, 1.2),
        (25.0, 35.0, 45.0),
        (5.0, 10.0, 20.0),
    )

    def __post_init__(self) -> None:
        if not isinstance(self.policy_version, str) or not self.policy_version.strip():
            raise ValueError("policy version must be a non-empty string")
        families = tuple(self.allowed_families)
        if not families or any(not isinstance(item, NewtonGenerationFamily) for item in families):
            raise ValueError("allowed families must contain NewtonGenerationFamily values")
        if len(families) != len(set(families)):
            raise ValueError("allowed families must not contain duplicates")
        for profile in (self.introductory, self.moderate, self.advanced):
            if not isinstance(profile, NewtonDifficultyProfile):
                raise ValueError("difficulty profiles must be NewtonDifficultyProfile values")
        object.__setattr__(self, "policy_version", self.policy_version.strip())
        object.__setattr__(self, "allowed_families", families)

    def profile_for(self, difficulty: Difficulty) -> NewtonDifficultyProfile:
        if not isinstance(difficulty, Difficulty):
            raise ValueError("difficulty must be a Difficulty")
        return {
            Difficulty.INTRODUCTORY: self.introductory,
            Difficulty.MODERATE: self.moderate,
            Difficulty.ADVANCED: self.advanced,
        }[difficulty]


DEFAULT_NEWTON_GENERATION_POLICY = NewtonGenerationPolicy()


@dataclass(frozen=True, slots=True)
class NewtonGeneratedMetadata:
    identifier: str
    family: NewtonGenerationFamily
    difficulty: Difficulty
    policy_version: str
    provenance: GenerationProvenance

    def __post_init__(self) -> None:
        if not isinstance(self.identifier, str) or not self.identifier.strip():
            raise ValueError("generated Newton identifier must be non-empty")
        require_type(self.family, NewtonGenerationFamily, "generated family")
        require_type(self.difficulty, Difficulty, "generated difficulty")
        if not isinstance(self.policy_version, str) or not self.policy_version.strip():
            raise ValueError("generated policy version must be non-empty")
        require_type(self.provenance, GenerationProvenance, "generated provenance")


@dataclass(frozen=True, slots=True)
class NewtonGeneratedProblem:
    metadata: NewtonGeneratedMetadata
    scenario: NewtonScenario

    def __post_init__(self) -> None:
        require_type(self.metadata, NewtonGeneratedMetadata, "generated metadata")
        require_type(self.scenario, NewtonScenario, "generated scenario")

    @property
    def identifier(self) -> str:
        return self.metadata.identifier

    @property
    def family(self) -> NewtonGenerationFamily:
        return self.metadata.family

    @property
    def difficulty(self) -> Difficulty:
        return self.metadata.difficulty

    @property
    def provenance(self) -> GenerationProvenance:
        return self.metadata.provenance


@dataclass(frozen=True, slots=True)
class GeneratedNewtonIIProblem(NewtonGeneratedProblem):
    pass


@dataclass(frozen=True, slots=True)
class GeneratedEquilibriumProblem(NewtonGeneratedProblem):
    pass


@dataclass(frozen=True, slots=True)
class GeneratedWeightProblem(NewtonGeneratedProblem):
    field_source: EnvironmentReference = EARTH


@dataclass(frozen=True, slots=True)
class GeneratedUnknownForceProblem(NewtonGeneratedProblem):
    force_id: str


@dataclass(frozen=True, slots=True)
class GeneratedContactProblem(NewtonGeneratedProblem):
    contact_id: str


@dataclass(frozen=True, slots=True)
class GeneratedConnectedBodiesProblem(NewtonGeneratedProblem):
    request: StraightStringRequest


@dataclass(frozen=True, slots=True)
class GeneratedGravitationProblem(NewtonGeneratedProblem):
    interaction_id: str


@dataclass(frozen=True, slots=True)
class GeneratedThirdLawProblem(NewtonGeneratedProblem):
    pair: ThirdLawPair


GeneratedNewtonProblem = NewtonGeneratedProblem


class NewtonProblemFactory:
    """Create solver-valid authored scenarios from a versioned local policy."""

    def __init__(self, policy: NewtonGenerationPolicy = DEFAULT_NEWTON_GENERATION_POLICY) -> None:
        if not isinstance(policy, NewtonGenerationPolicy):
            raise ValueError("policy must be a NewtonGenerationPolicy")
        self.policy = policy

    def generate(self, request: NewtonGenerationInput) -> GeneratedNewtonProblem:
        if not isinstance(request, NewtonGenerationInput):
            raise ValueError("request must be a NewtonGenerationInput")
        family = self._family_for(request)
        profile = self.policy.profile_for(request.difficulty)
        rng = Random(request.seed.value)
        scenario, target = self._scenario(family, request, profile, rng)
        metadata = self._metadata(request, family)
        scenario = replace(scenario, identifier=metadata.identifier)
        result: NewtonGeneratedProblem
        if family is NewtonGenerationFamily.UNKNOWN_FORCE:
            if not isinstance(target, str):
                raise ValueError("unknown-force generation target is invalid")
            result = GeneratedUnknownForceProblem(metadata, scenario, target)
        elif family is NewtonGenerationFamily.NEWTON_II:
            result = GeneratedNewtonIIProblem(metadata, scenario)
        elif family is NewtonGenerationFamily.EQUILIBRIUM:
            result = GeneratedEquilibriumProblem(metadata, scenario)
        elif family is NewtonGenerationFamily.WEIGHT:
            result = GeneratedWeightProblem(metadata, scenario)
        elif family in (
            NewtonGenerationFamily.CONTACT_NORMAL,
            NewtonGenerationFamily.STATIC_FRICTION,
            NewtonGenerationFamily.LIMITING_STATIC_FRICTION,
            NewtonGenerationFamily.KINETIC_FRICTION,
            NewtonGenerationFamily.INCLINED_PLANE,
        ):
            if not isinstance(target, str):
                raise ValueError("contact generation target is invalid")
            result = GeneratedContactProblem(metadata, scenario, target)
        elif family is NewtonGenerationFamily.CONNECTED_BODIES:
            if not isinstance(target, StraightStringRequest):
                raise ValueError("connected-body generation target is invalid")
            result = GeneratedConnectedBodiesProblem(metadata, scenario, target)
        elif family is NewtonGenerationFamily.UNIVERSAL_GRAVITATION:
            if not isinstance(target, str):
                raise ValueError("gravitation generation target is invalid")
            result = GeneratedGravitationProblem(metadata, scenario, target)
        elif family is NewtonGenerationFamily.THIRD_LAW:
            if not isinstance(target, ThirdLawPair):
                raise ValueError("third-law generation target is invalid")
            result = GeneratedThirdLawProblem(metadata, scenario, target)
        else:
            raise ValueError("unsupported generated family")
        self._validate_generated(result)
        return result

    def _family_for(self, request: NewtonGenerationInput) -> NewtonGenerationFamily:
        if request.family is not None:
            if request.family not in self.policy.allowed_families:
                raise ValueError("requested Newton family is not allowed by policy")
            return request.family
        return Random(request.seed.value).choice(self.policy.allowed_families)

    def _metadata(
        self, request: NewtonGenerationInput, family: NewtonGenerationFamily
    ) -> NewtonGeneratedMetadata:
        identifier = (
            f"newton-problem-v{self.policy.policy_version}-{family.value}-"
            f"{request.difficulty.value}-seed-{request.seed.value}"
        )
        provenance = GenerationProvenance(
            GENERATOR_ID,
            GENERATOR_VERSION,
            request.seed,
            (family.value, request.difficulty.value, f"policy-{self.policy.policy_version}"),
        )
        return NewtonGeneratedMetadata(
            identifier, family, request.difficulty, self.policy.policy_version, provenance
        )

    def _scenario(
        self,
        family: NewtonGenerationFamily,
        request: NewtonGenerationInput,
        profile: NewtonDifficultyProfile,
        rng: Random,
    ) -> tuple[NewtonScenario, str | StraightStringRequest | ThirdLawPair | None]:
        if family is NewtonGenerationFamily.NEWTON_II:
            return self._newton_ii(request, profile, rng, False)
        if family is NewtonGenerationFamily.EQUILIBRIUM:
            return self._newton_ii(request, profile, rng, True)
        if family is NewtonGenerationFamily.UNKNOWN_FORCE:
            return self._unknown_force(request, profile, rng)
        if family is NewtonGenerationFamily.WEIGHT:
            return self._weight(request, profile, rng)
        if family in (
            NewtonGenerationFamily.CONTACT_NORMAL,
            NewtonGenerationFamily.STATIC_FRICTION,
            NewtonGenerationFamily.LIMITING_STATIC_FRICTION,
            NewtonGenerationFamily.KINETIC_FRICTION,
            NewtonGenerationFamily.INCLINED_PLANE,
        ):
            return self._contact(request, family, profile, rng)
        if family is NewtonGenerationFamily.CONNECTED_BODIES:
            return self._connected(request, profile, rng)
        if family is NewtonGenerationFamily.UNIVERSAL_GRAVITATION:
            return self._gravitation(request, profile, rng)
        if family is NewtonGenerationFamily.THIRD_LAW:
            return self._third_law(request, profile, rng)
        raise ValueError("unsupported NewtonGenerationFamily")

    @staticmethod
    def _basis() -> CartesianCoordinates:
        return CartesianCoordinates((CartesianDirection.RIGHT,))

    @staticmethod
    def _basis_xy() -> CartesianCoordinates:
        return CartesianCoordinates((CartesianDirection.RIGHT, CartesianDirection.UP))

    @staticmethod
    def _vector(
        basis: CartesianCoordinates | SurfaceCoordinates, values: tuple[float | UnknownValue, ...]
    ) -> ForceVector:
        return ForceVector(
            basis,
            tuple(UNKNOWN if value is UNKNOWN else Newtons(value) for value in values),
        )

    @staticmethod
    def _acceleration(
        basis: CartesianCoordinates | SurfaceCoordinates, values: tuple[float, ...]
    ) -> AccelerationVector:
        return AccelerationVector(basis, tuple(MetresPerSecondSquared(value) for value in values))

    @staticmethod
    def _body(identifier: str, mass: float) -> NewtonBody:
        return NewtonBody(identifier, Kilograms(mass))

    @staticmethod
    def _base(
        identifier: str,
        bodies: tuple[NewtonBody, ...],
        basis: CartesianCoordinates | SurfaceCoordinates,
        environment: tuple[EnvironmentReference, ...],
        forces: tuple[Force, ...] = (),
        surfaces: tuple[Surface, ...] = (),
        contacts: tuple[Contact, ...] = (),
        strings: tuple[StringConnection, ...] = (),
        gravitation: tuple[GravitationalInteraction, ...] = (),
        gravitational_fields: tuple[GravitationalField, ...] = (),
        accelerations: tuple[AuthoredAcceleration, ...] = (),
        third_law_pairs: tuple[ThirdLawPair, ...] = (),
    ) -> NewtonScenario:
        return NewtonScenario(
            identifier,
            bodies,
            basis,
            SystemBoundary(tuple(body.identifier for body in bodies)),
            NewtonAssumptions(True, True, True),
            environment=environment,
            forces=forces,
            surfaces=surfaces,
            contacts=contacts,
            strings=strings,
            gravitation=gravitation,
            gravitational_fields=gravitational_fields,
            accelerations=accelerations,
            third_law_pairs=third_law_pairs,
        )

    def _newton_ii(
        self,
        request: NewtonGenerationInput,
        profile: NewtonDifficultyProfile,
        rng: Random,
        equilibrium: bool,
    ) -> tuple[NewtonScenario, None]:
        basis = self._basis()
        body = self._body("body-a", rng.choice(profile.masses_kg))
        magnitude = rng.choice(profile.force_magnitudes_n)
        signed = -magnitude if rng.randrange(2) else magnitude
        forces = (
            Force(
                "force-a",
                ForceKind.APPLIED,
                body.identifier,
                ENVIRONMENT,
                self._vector(basis, (signed,)),
            ),
            Force(
                "force-b",
                ForceKind.APPLIED,
                body.identifier,
                EARTH,
                self._vector(basis, (-signed if equilibrium else 0.0,)),
            ),
        )
        return self._base(
            "authored-newton", (body,), basis, (ENVIRONMENT, EARTH), forces=forces
        ), None

    def _unknown_force(
        self, request: NewtonGenerationInput, profile: NewtonDifficultyProfile, rng: Random
    ) -> tuple[NewtonScenario, str]:
        basis = self._basis()
        body = self._body("body-a", rng.choice(profile.masses_kg))
        acceleration = rng.choice(profile.acceleration_magnitudes_m_s2)
        known = rng.choice(profile.force_magnitudes_n)
        scenario = self._base(
            "authored-newton",
            (body,),
            basis,
            (ENVIRONMENT,),
            forces=(
                Force(
                    "known-force",
                    ForceKind.APPLIED,
                    body.identifier,
                    ENVIRONMENT,
                    self._vector(basis, (known,)),
                ),
                Force(
                    "unknown-force",
                    ForceKind.APPLIED,
                    body.identifier,
                    ENVIRONMENT,
                    self._vector(basis, (UNKNOWN,)),
                ),
            ),
            accelerations=(
                AuthoredAcceleration(body.identifier, self._acceleration(basis, (acceleration,))),
            ),
        )
        return scenario, "unknown-force"

    def _weight(
        self, request: NewtonGenerationInput, profile: NewtonDifficultyProfile, rng: Random
    ) -> tuple[NewtonScenario, None]:
        basis = self._basis_xy()
        body = self._body("body-a", rng.choice(profile.masses_kg))
        field = rng.choice(profile.gravitational_fields_m_s2)
        scenario = self._base(
            "authored-newton",
            (body,),
            basis,
            (EARTH,),
            gravitational_fields=(
                GravitationalField(
                    EARTH, (body.identifier,), self._acceleration(basis, (0.0, -field))
                ),
            ),
        )
        return scenario, None

    def _contact(
        self,
        request: NewtonGenerationInput,
        family: NewtonGenerationFamily,
        profile: NewtonDifficultyProfile,
        rng: Random,
    ) -> tuple[NewtonScenario, str]:
        inclined = family is NewtonGenerationFamily.INCLINED_PLANE
        basis: CartesianCoordinates | SurfaceCoordinates = (
            SurfaceCoordinates(
                "surface", (SurfaceDirection.ALONG_RIGHT, SurfaceDirection.NORMAL_OUT)
            )
            if inclined
            else self._basis_xy()
        )
        body = self._body("body-a", rng.choice(profile.masses_kg))
        field = rng.choice(profile.gravitational_fields_m_s2)
        regime = {
            NewtonGenerationFamily.CONTACT_NORMAL: FrictionRegime.NONE,
            NewtonGenerationFamily.STATIC_FRICTION: FrictionRegime.STATIC,
            NewtonGenerationFamily.LIMITING_STATIC_FRICTION: FrictionRegime.LIMITING_STATIC,
            NewtonGenerationFamily.KINETIC_FRICTION: FrictionRegime.KINETIC,
            NewtonGenerationFamily.INCLINED_PLANE: FrictionRegime.NONE,
        }[family]
        coefficient = (
            None
            if regime is FrictionRegime.NONE
            else FrictionCoefficient(rng.choice(profile.friction_coefficients))
        )
        surface = Surface(
            "surface", ENVIRONMENT, rng.choice(profile.inclinations_degrees) if inclined else 0.0
        )
        contact = Contact(
            "contact", body.identifier, surface.identifier, Friction(regime, coefficient)
        )
        normal_values: tuple[float | UnknownValue, ...] = (0.0, UNKNOWN)
        friction_value: float | UnknownValue = UNKNOWN
        if inclined:
            normal_values = (0.0, UNKNOWN)
        elif regime in (FrictionRegime.LIMITING_STATIC, FrictionRegime.KINETIC):
            normal_values = (0.0, rng.choice(profile.normal_magnitudes_n))
        forces: list[Force] = [
            Force(
                "weight",
                ForceKind.WEIGHT,
                body.identifier,
                EARTH,
                self._vector(basis, (UNKNOWN, UNKNOWN)),
            ),
            Force(
                "normal",
                ForceKind.NORMAL,
                body.identifier,
                ENVIRONMENT,
                self._vector(basis, normal_values),
                contact.identifier,
            ),
            Force(
                "push",
                ForceKind.APPLIED,
                body.identifier,
                ENVIRONMENT,
                self._vector(basis, (0.0, 0.0)),
            ),
        ]
        if regime is not FrictionRegime.NONE:
            forces.append(
                Force(
                    "friction",
                    ForceKind.FRICTION,
                    body.identifier,
                    ENVIRONMENT,
                    self._vector(basis, (friction_value, 0.0)),
                    contact.identifier,
                )
            )
        accelerations = (
            ()
            if regime in (FrictionRegime.LIMITING_STATIC, FrictionRegime.KINETIC)
            else (AuthoredAcceleration(body.identifier, self._acceleration(basis, (0.0, 0.0))),)
        )
        scenario = self._base(
            "authored-newton",
            (body,),
            basis,
            (ENVIRONMENT, EARTH),
            forces=tuple(forces),
            surfaces=(surface,),
            contacts=(contact,),
            gravitational_fields=(
                GravitationalField(
                    EARTH, (body.identifier,), self._acceleration(basis, (0.0, -field))
                ),
            ),
            accelerations=accelerations,
        )
        return scenario, contact.identifier

    def _connected(
        self, request: NewtonGenerationInput, profile: NewtonDifficultyProfile, rng: Random
    ) -> tuple[NewtonScenario, StraightStringRequest]:
        basis = self._basis()
        first = self._body("body-a", rng.choice(profile.masses_kg))
        second = self._body("body-b", rng.choice(profile.masses_kg))
        string = StringConnection(
            "string", (first.identifier, second.identifier), CORD, True, True, True
        )
        forces = (
            Force(
                "external-a",
                ForceKind.APPLIED,
                first.identifier,
                ENVIRONMENT,
                self._vector(basis, (-rng.choice(profile.force_magnitudes_n),)),
            ),
            Force(
                "tension-a",
                ForceKind.TENSION,
                first.identifier,
                CORD,
                self._vector(basis, (UNKNOWN,)),
                string.identifier,
            ),
            Force(
                "external-b",
                ForceKind.APPLIED,
                second.identifier,
                ENVIRONMENT,
                self._vector(basis, (0.0,)),
            ),
            Force(
                "tension-b",
                ForceKind.TENSION,
                second.identifier,
                CORD,
                self._vector(basis, (UNKNOWN,)),
                string.identifier,
            ),
        )
        scenario = self._base(
            "authored-newton",
            (first, second),
            basis,
            (ENVIRONMENT, CORD),
            forces=forces,
            strings=(string,),
        )
        return scenario, StraightStringRequest(string.identifier, ComponentSign.POSITIVE)

    def _gravitation(
        self, request: NewtonGenerationInput, profile: NewtonDifficultyProfile, rng: Random
    ) -> tuple[NewtonScenario, str]:
        basis = self._basis()
        first = self._body("body-a", rng.choice(profile.masses_kg))
        second = self._body("body-b", rng.choice(profile.masses_kg))
        interaction = GravitationalInteraction(
            "gravity",
            (first.identifier, second.identifier),
            Metres(rng.choice(profile.separations_m)),
        )
        scenario = self._base(
            "authored-newton", (first, second), basis, (), gravitation=(interaction,)
        )
        return scenario, interaction.identifier

    def _third_law(
        self, request: NewtonGenerationInput, profile: NewtonDifficultyProfile, rng: Random
    ) -> tuple[NewtonScenario, ThirdLawPair]:
        basis = self._basis()
        first = self._body("body-a", rng.choice(profile.masses_kg))
        second = self._body("body-b", rng.choice(profile.masses_kg))
        magnitude = rng.choice(profile.force_magnitudes_n)
        first_force = Force(
            "a-on-b",
            ForceKind.APPLIED,
            second.identifier,
            BodyReference(first.identifier),
            self._vector(basis, (magnitude,)),
        )
        second_force = Force(
            "b-on-a",
            ForceKind.APPLIED,
            first.identifier,
            BodyReference(second.identifier),
            self._vector(basis, (-magnitude,)),
        )
        pair = ThirdLawPair((first_force.identifier, second_force.identifier))
        scenario = self._base(
            "authored-newton",
            (first, second),
            basis,
            (),
            forces=(first_force, second_force),
            third_law_pairs=(pair,),
        )
        return scenario, pair

    def _validate_generated(self, result: GeneratedNewtonProblem) -> None:
        solver = NewtonSolver(result.scenario)
        family = result.family
        if family in (NewtonGenerationFamily.NEWTON_II, NewtonGenerationFamily.EQUILIBRIUM):
            dynamics = solver.body_dynamics("body-a")
            if not solver.validate_dynamics(dynamics).valid:
                raise ValueError("generated Newton II result failed solver validation")
        elif family is NewtonGenerationFamily.UNKNOWN_FORCE:
            assert isinstance(result, GeneratedUnknownForceProblem)
            solver.solve_force(result.force_id)
        elif family is NewtonGenerationFamily.WEIGHT:
            solver.weight("body-a", EARTH)
        elif family in (
            NewtonGenerationFamily.CONTACT_NORMAL,
            NewtonGenerationFamily.STATIC_FRICTION,
            NewtonGenerationFamily.LIMITING_STATIC_FRICTION,
            NewtonGenerationFamily.KINETIC_FRICTION,
            NewtonGenerationFamily.INCLINED_PLANE,
        ):
            assert isinstance(result, GeneratedContactProblem)
            solver.contact_forces(result.contact_id)
        elif family is NewtonGenerationFamily.CONNECTED_BODIES:
            assert isinstance(result, GeneratedConnectedBodiesProblem)
            solver.connected_bodies(result.request)
        elif family is NewtonGenerationFamily.UNIVERSAL_GRAVITATION:
            assert isinstance(result, GeneratedGravitationProblem)
            solver.gravitational_force(result.interaction_id)
        elif family is NewtonGenerationFamily.THIRD_LAW:
            assert isinstance(result, GeneratedThirdLawProblem)
            if not solver.validate_third_law(result.pair).valid:
                raise ValueError("generated third-law result failed solver validation")


DEFAULT_NEWTON_PROBLEM_FACTORY = NewtonProblemFactory()
