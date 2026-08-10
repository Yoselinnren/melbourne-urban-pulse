# Milestone 7 Researcher Review

## Implemented routes

- `/` - personal portfolio/CV entry shell; the project does not occupy the domain root.
- `/projects/melbourne-urban-pulse` - complete Hero and nine-chapter research narrative.
- `/explore` - existing analytical Explorer, now linked back to the project and methodology.

## Implemented experience

- data-driven New Year Hero using the verified Pulse detail payload;
- a twelve-trace, shape-accurate 1.5-second loading skeleton and deterministic static fallback with all looping motion disabled;
- desktop and mobile narrative containing the research question, method, four case groups, limitations, provenance, Explorer handoff, and researcher-role chapter;
- direct Explorer links for both New Year phases, January rain, July rain, Melbourne Marathon, the December evening Pulse, and QVM sensor 49;
- once-only 400 ms chapter reveal, grouped sensor-trace reveal, restrained selected-sensor glow, static fallbacks, visible keyboard focus, and `prefers-reduced-motion` overrides;
- no interpolation or causal-attribution language added.

## Verification

- `pnpm lint` passes.
- `pnpm build` passes and statically generates `/`, `/projects/melbourne-urban-pulse`, and `/explore`.
- 1440 x 900 project Hero has no horizontal overflow and loads the verified Pulse state.
- 390 x 844 project layout has no horizontal overflow and preserves the approved content hierarchy.
- Browser navigation from portfolio entry to project Hero to the selected New Year Explorer state succeeds.
- The selected Explorer route loads 425 Pulses, twelve representative sensors, the six-hour network-wide New Year Pulse, and its evidence panel without console errors.
- Semantic inspection finds one `h1`, a valid `h1` -> `h2` -> `h3` hierarchy, one `main` landmark, a semantic route footer, and no unlabeled links.
- The first keyboard focus targets follow the intended document order: project brand, Project, Methodology, Open Explorer, then the Hero call to action. Each remains in the native tab order and the compiled stylesheet contains the three-pixel `:focus-visible` treatment.
- The compiled project stylesheet contains the `prefers-reduced-motion: reduce` overrides that remove chapter, trace, glow, and skeleton motion while keeping the content visible.
- The selected-sensor glow is gated by both current intersection and document visibility, so returning to a backgrounded tab cannot restart the loop while the Hero remains offscreen.

## Researcher approval

The researcher reviewed the implemented project in the physical browser and approved the M7 visual result, wording, and page behaviour on 2026-08-11.

Personal portfolio/CV identity content remains a separate input for the later portfolio and release work; it does not block the approved Melbourne Urban Pulse project implementation.
