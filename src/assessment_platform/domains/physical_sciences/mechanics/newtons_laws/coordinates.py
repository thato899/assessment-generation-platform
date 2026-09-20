"""Declared one-/two-dimensional bases and authored components, without transforms."""

from dataclasses import dataclass
from enum import StrEnum

from .values import (
    MetresPerSecondSquared,
    Newtons,
    UnknownValue,
    identifier,
    require_type,
    typed_tuple,
)


class CartesianDirection(StrEnum):
    RIGHT = "right"
    LEFT = "left"
    UP = "up"
    DOWN = "down"


class SurfaceDirection(StrEnum):
    """Tangent points toward physical right/left; normal points away/into the surface."""

    ALONG_RIGHT = "along-right"
    ALONG_LEFT = "along-left"
    NORMAL_OUT = "normal-out"
    NORMAL_IN = "normal-in"


@dataclass(frozen=True, slots=True)
class CartesianCoordinates:
    """Positive directions in component order (x, then y if present)."""

    axes: tuple[CartesianDirection, ...]

    def __post_init__(self) -> None:
        axes = typed_tuple(self.axes, CartesianDirection, "Cartesian axes")
        horizontal = {CartesianDirection.RIGHT, CartesianDirection.LEFT}
        if len(axes) not in (1, 2) or (
            len(axes) == 2 and (axes[0] in horizontal) == (axes[1] in horizontal)
        ):
            raise ValueError("Cartesian axes must declare one axis or two perpendicular axes")
        object.__setattr__(self, "axes", axes)


@dataclass(frozen=True, slots=True)
class SurfaceCoordinates:
    """Surface tangent x and optional normal y; surface supplies physical inclination."""

    surface_id: str
    axes: tuple[SurfaceDirection, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "surface_id", identifier(self.surface_id))
        axes = typed_tuple(self.axes, SurfaceDirection, "surface axes")
        if (
            len(axes) not in (1, 2)
            or axes[0] not in (SurfaceDirection.ALONG_RIGHT, SurfaceDirection.ALONG_LEFT)
            or (
                len(axes) == 2
                and axes[1] not in (SurfaceDirection.NORMAL_OUT, SurfaceDirection.NORMAL_IN)
            )
        ):
            raise ValueError("surface axes must declare tangent x and optional normal y")
        object.__setattr__(self, "axes", axes)


type Coordinates = CartesianCoordinates | SurfaceCoordinates


@dataclass(frozen=True, slots=True)
class ForceVector:
    """Components in newtons; UNKNOWN is distinct from an authored zero."""

    coordinates: Coordinates
    components: tuple[Newtons | UnknownValue, ...]

    def __post_init__(self) -> None:
        require_type(self.coordinates, (CartesianCoordinates, SurfaceCoordinates), "coordinates")
        if not isinstance(self.components, (tuple, list)):
            raise ValueError("force components must be an ordered sequence")
        components = tuple(self.components)
        if len(components) != len(self.coordinates.axes):
            raise ValueError("force components must match the coordinate dimension")
        for component in components:
            require_type(component, (Newtons, UnknownValue), "force component")
        object.__setattr__(self, "components", components)


@dataclass(frozen=True, slots=True)
class AccelerationVector:
    """Given components in metres per second squared; absence is modeled separately."""

    coordinates: Coordinates
    components: tuple[MetresPerSecondSquared, ...]

    def __post_init__(self) -> None:
        require_type(self.coordinates, (CartesianCoordinates, SurfaceCoordinates), "coordinates")
        components = typed_tuple(self.components, MetresPerSecondSquared, "acceleration components")
        if len(components) != len(self.coordinates.axes):
            raise ValueError("acceleration components must match the coordinate dimension")
        object.__setattr__(self, "components", components)
