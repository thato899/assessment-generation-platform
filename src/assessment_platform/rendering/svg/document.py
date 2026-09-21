"""Generic immutable SVG document return contract."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SvgDocument:
    """A deterministic self-contained SVG document."""

    markup: str
    width: int
    height: int

