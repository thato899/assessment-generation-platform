# Work, Energy & Power technical SVG rendering

Issue #77 adds an authored-only presentation boundary. `WorkEnergySvgRenderer`
accepts a `WorkEnergyScenario` and explicit `WorkEnergyRenderOptions`; it does
not accept or invoke a solver result and has no dependency on generation.

## Diagram kinds and family support

| Generation family | Diagram kind | Reason |
| --- | --- | --- |
| `work-by-force` | `WORK_CONTRIBUTIONS` | Force/displacement relationship is useful. |
| `net-work` | `WORK_CONTRIBUTIONS` | Contributions are separate rows in authored order. |
| `along-plane-work` | `ALONG_PLANE` | Signed resultant and displacement on a track are useful. |
| `kinetic-energy` | `MOTION_STATES` | A state marker communicates the authored speed. |
| `work-energy-net-work` | `MOTION_STATES` | Initial/final states and transition are useful. |
| `work-energy-final-speed` | `MOTION_STATES` | Unknown final speed is shown as `?`. |
| `work-energy-initial-speed` | `MOTION_STATES` | Unknown initial speed is shown as `?`. |
| `gravitational-potential-energy` | `HEIGHT_STATES` | Height relative to a reference is useful. |
| `mechanical-energy-non-conservative-work` | `HEIGHT_STATES` | Height and reference context are useful. |
| `mechanical-energy-final-speed` | `HEIGHT_STATES` | Height context avoids exposing derived speed. |
| `constant-speed-power` | `CONSTANT_SPEED_SURFACE` | Surface and force direction are useful. |
| `pumping-power` | `PUMPING` | A borehole and lift schematic are useful. |
| `average-power` | **no visual** | A diagram adds no technical information. |

The mapping is explicit; no automatic field inspection chooses a diagram.

## Safety and visibility

Defaults show semantic labels and reference structure but hide numeric givens
(`show_numeric_values=False`). Numeric authored givens are shown only after an
explicit opt-in. Unknown values remain unknown (`?`); they are never converted
to zero and no derived answer is rendered.

All magnitudes use fixed schematic arrow lengths, object sizes, pipe widths,
and coordinates. Signed force direction and the sign of relative height may
change orientation or semantic placement; magnitudes do not. Authored angles
may use sine and cosine only to place a fixed arrow. Inclined surfaces use one
fixed generic slope because no inclination angle is authored.

Net-work contributions are separate schematic rows, never a Newton free-body
diagram. Speed arrows are neutral because M5 does not author a signed velocity
direction. Height diagrams use an explicit reference line; unknown height is an
unresolved marker rather than the reference level.

Each SVG has `role="img"`, deterministic `<title>`, `<desc>`, and
`aria-labelledby`. Authored labels are XML escaped and IDs are sanitized. The
document is self-contained: no scripts, event handlers, `foreignObject`,
JavaScript URLs, external images, remote fonts, stylesheets, or links are
emitted. A shared `SvgDocument` contract keeps this renderer independent of
the projectile, momentum, and Newton solver modules.

Question generation (#78), conceptual templates (#82), API work (#83),
PDF/PNG conversion, and image generation are outside this boundary.

