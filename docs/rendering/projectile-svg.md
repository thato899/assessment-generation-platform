# Vertical projectile SVG renderer

`ProjectileSvgRenderer` accepts a validated `VerticalProjectileScenario` and its `VerticalProjectileSolution`, then returns an in-memory `SvgDocument`. It transforms domain coordinates into screen coordinates; it never calculates trajectory values or invents events.

The display keeps physical upward visually upward even when the mathematical positive direction is down. Gravity is always drawn downward; its numeric sign comes from the scenario. Events come only from structured solver events. Same-position events share the same screen coordinate and are distinguished by labels. Maximum-height velocity arrows are omitted when velocity is zero, and dropped objects are labelled as released from rest without an initial velocity arrow.

Scaling preserves vertical ordering and uses a proportional range with fixed margins. The renderer does not claim the diagram is drawn to physical scale. SVG output uses deterministic dimensions, stable IDs, vector primitives, escaped text, no scripts, no external references, and neutral deterministic accessibility title/description text. PDF, HTML, answer-sheet, and question generation remain outside this renderer.

Representative SVG files were generated locally under `.dist/projectile-examples/` for upward ground, upward elevated, downward, dropped, and downward-positive cases. XML parsing and semantic tests passed. Manual visual inspection was not performed because the available browser surface blocked local SVG URLs; this is recorded rather than claimed as complete.
