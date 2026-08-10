# Research Portfolio Roadmap

## Goal

Deliver Melbourne Urban Pulse as a complete English-language research case-study website for research-degree applications. The final experience must combine a data-driven Hero, an evidence-backed narrative, transparent methodology, selected cases, and the analytical Explorer. The project should show how known urban conditions produce different spatial and temporal signatures, rather than presenting the existence of holidays, weather, or events as the result.

The final portfolio architecture is intentionally broader than this repository: `yoreny.com` will open on the researcher's personal portfolio and CV, then link into the Melbourne Urban Pulse project Hero, research narrative, and Explorer. This project must not permanently occupy the domain root. The portfolio shell is reserved for a later implementation decision and is not part of Milestone 6.

## Current baseline

Completed:

- reproducible analytical phases from source profiling through explanation-ready aggregation;
- 12-sensor representative mode with 4,647 episodes and 425 Pulses;
- deterministic UI data v1 and independent validation;
- an approved annual Explorer visual system with spatial, temporal, filter, Pulse, and sensor states;
- responsive Explorer behaviour, accessible interaction semantics, and browser acceptance;
- 64 reviewed evidence matches covering 15 Pulses and one isolated episode;
- connected Figma workspace containing the project cover, Explorer design system and screens, and scaffolded narrative and methodology pages;
- GitHub-to-Vercel deployment, custom-domain DNS, and SSL for `yoreny.com`, established early as release infrastructure.

Still required:

- research-result framing and selected-case narrative;
- a complete Figma visual and motion system for the Hero, narrative, methodology, and responsive states;
- implementation and acceptance of the full website outside the Explorer;
- public-release and research-application handoff material.

## Working workflow

The remaining work follows this order. A later stage does not begin until the previous gate is approved.

1. **Result framing** — compare reviewed cases by spatial scope, direction, duration, evidence combination, ambiguity, and departure from expectation.
2. **Case selection** — choose a small contrasting set that includes an unexpected spatial pattern, a contrasting response, an ambiguous multi-factor case, and unresolved context where evidence permits.
3. **Figma-to-code audit** — identify every missing page, section, responsive state, visual asset, and motion state; the existing Explorer is not treated as the complete website.
4. **Dynamic-art skill review** — search GitHub, inspect source, dependencies, licence, maintenance, and security, then present candidates before installing or adopting one. Figma defines composition and motion intent; the selected skill may assist implementation but does not replace design approval.
5. **Full visual design** — complete and review the Hero, narrative chapters, selected cases, methodology, Explorer transition, mobile layouts, loading, reduced-motion, and fallback states in Figma.
6. **Vertical-slice implementation** — implement the Hero, one selected case, and the transition into methodology/Explorer before expanding the full site.
7. **Full implementation and acceptance** — finish the narrative site, verify claims against project data, and run responsive, accessibility, performance, browser, and physical-display checks.

Assistant responsibilities:

- maintain the roadmap and evidence boundary;
- synthesise the result matrix and draft claims from verified project outputs;
- audit Figma and code, research candidate skills, and disclose trade-offs before adoption;
- design, implement, test, and document the approved site;
- never promote overlap into causation or install a third-party skill without review.

Researcher responsibilities:

- approve the research question, selected cases, visual direction, and final claims;
- choose whether an evaluated dynamic-art skill may be installed and used;
- provide identity, academic direction, contact, acknowledgement, and motivation content;
- inspect the complete Hero and page flow in Figma and the physical browser before each implementation gate passes.

## Milestone 1 - Foundation

Assistant:

- keep root documentation aligned with the actual repository;
- repair and verify the local Python environment;
- retain a repeatable lint, build, and UI-data validation baseline.

Researcher:

- confirm the English-only research-application audience;
- provide later identity, programme, contact, and attribution details.

Gate: documentation and current checks agree with the tracked implementation.

## Milestone 2 - Explorer visual system

Status: gate passed. The researcher approved the desktop Explorer direction; paid-team Figma library handoff remains deferred.

Assistant:

- audit the current Explorer and existing Figma workspace;
- define the minimum type, colour, spacing, grid, and interaction tokens;
- design Annual, Pulse selected, Sensor selected, Filters open, loading, error, and empty states;
- preserve the current data contract and non-causal language.

Researcher:

- arrange a Professional Full seat for the connected Figma account and place the file in that paid team;
- review frames with comments;
- approve one design direction for implementation.

Gate: the researcher explicitly approves the desktop Explorer direction.

## Milestone 3 - Explorer implementation

Status: complete. Core journeys passed automated checks, browser acceptance, and researcher physical-display acceptance.

Assistant:

- implement the approved visual system using the existing React structure;
- add responsive behaviour without a new UI dependency;
- verify keyboard use, accessible names, loading, error, and empty states;
- run lint, production build, data validation, and browser acceptance.

Researcher:

- test the visible result on the physical display;
- report screenshot, browser, window size, action, expected result, and actual result for any issue;
- approve the implemented Explorer.

Gate: core Explorer journeys pass automated and researcher acceptance.

## Milestone 4 - Human evidence review

Status: complete. The original evidence researcher confirmed all 64 links; downstream explanation-ready and UI data were regenerated and validated.

Assistant:

- generate a review-friendly workbook from the current evidence matches;
- include source links, temporal and spatial context, controlled vocabularies, and three completed examples;
- validate and import the completed review decisions;
- regenerate downstream explanation-ready and UI data.

Researcher:

- open each source and judge overlap, relevance, and evidence strength;
- choose the documented review status and add a short rationale;
- leave unsupported cases unresolved rather than forcing an explanation.

Gate: reviewed and automatic evidence are visibly and structurally distinct.

## Milestone 5 - Research result framing

Status: complete. The researcher approved the result thesis, four core cases, non-causal claim boundary, and narrative order documented in [result-framing.md](result-framing.md).

Assistant:

- build a comparison matrix for the reviewed cases using spatial scope, direction, duration, evidence combination, confidence, and ambiguity;
- draft a result thesis that explains variation in urban response rather than rediscovering predictable calendar or weather conditions;
- propose three to four contrasting cases and document what each case can and cannot support.

Researcher:

- challenge the usefulness of the proposed result;
- approve the research question, claim boundaries, and selected cases.

Gate: the result remains interesting after removing the trivial statement that holidays, weather, and events are predictable.

## Milestone 6 - Full-site visual and motion design

Status: complete and researcher-approved on 2026-08-11. The code-side gap audit, connected Figma file audit, and GitHub Skill review are documented in [milestone-6-audit.md](milestone-6-audit.md). The approved `motion-ref` Skill is installed. The Figma file contains the complete desktop narrative, complete mobile narrative, four reviewed-case chapters, method and limitation chapters, Explorer handoff, Hero default/loading/static/reduced-motion states, and motion implementation annotations. The completed review checklist and approval record are in [milestone-6-review.md](milestone-6-review.md).

Assistant:

- audit the implemented pages against all Figma pages and document the missing Hero and site logic;
- search and vet GitHub dynamic-art skills, then present a shortlist before installation;
- complete the English Hero, narrative chapters, selected-case layouts, methodology, Explorer entry, mobile layouts, motion, reduced-motion, loading, and fallback states in Figma;
- prototype the data-driven Urban Pulse Field with the lightest suitable browser technology.

Researcher:

- approve or reject the skill shortlist;
- review the complete desktop and mobile page flow, not only the Explorer;
- approve the Hero art direction and motion behaviour before implementation.

Gate: the researcher has seen and approved the complete Hero and full-site logic in Figma, plus one feasible motion prototype.

## Milestone 7 - Narrative site implementation

Status: complete and researcher-approved on 2026-08-11. The approved M6 desktop/mobile narrative is available at `/projects/melbourne-urban-pulse`; `/` is reserved as the personal portfolio/CV entry and `/explore` remains the analytical audit trail. The Hero loads the verified New Year Pulse payload with shape-accurate loading and deterministic static fallback states, while native CSS and IntersectionObserver implement the approved reveal, selected-sensor, offscreen/background pause, and reduced-motion behaviour without a new motion dependency. Lint, production build, 1440 px and 390 px responsive checks, and the portfolio → project → selected Explorer route handoff pass. Review evidence and researcher approval are recorded in [milestone-7-review.md](milestone-7-review.md).

Assistant:

- implement the approved Hero and narrative system;
- connect selected cases, methodology, data sources, limitations, and the Explorer without duplicating the analytical interface;
- write draft English copy from verified project evidence and researcher-provided personal context;
- verify responsive behaviour, reduced motion, keyboard use, performance, and browser states.

Researcher:

- provide name, academic background, intended research direction, contact links, acknowledgements, and a short personal motivation;
- approve the final wording, selected cases, visual result, and physical-display behaviour.

Gate: an admissions reviewer can understand the question, method, contribution, limitations, and researcher's role without opening the repository.

## Milestone 8 - Release

Status: infrastructure established early. GitHub deployment, Vercel production, Spaceship DNS, SSL, `yoreny.com`, and `www.yoreny.com` are connected; final content release and portfolio routing remain gated on Milestones 6 and 7.

Assistant:

- run final accessibility, performance, responsive, data-safety, and clean-build checks;
- prepare deployment configuration and repository handoff;
- publish only after explicit approval.

Researcher:

- select and authorise hosting;
- approve the public URL and final release;
- approve the eventual personal-portfolio entry and route handoff without making this project the permanent domain root.

Gate: the public build is accurate, navigable, safe, and approved.

## Visual direction

Use Shopify Editions Winter '26 as a mood reference, not a layout template:

- borrow editorial scale, chapter navigation, deep atmospheric backgrounds, fine technical grids, and deliberate pacing;
- translate Renaissance imagery into Melbourne-specific research material such as archival map texture, restrained civic colour, sensor geometry, and temporal traces;
- keep analytical controls calm, readable, and accessible;
- prefer accessible SVG, Canvas, and CSS motion; use WebGL only if a reviewed prototype proves it materially improves the story;
- avoid copied assets, novelty interaction, and animation that competes with evidence.

## Deferred on purpose

- personal portfolio shell design and implementation; reserve the final route hierarchy as personal portfolio/CV → project Hero → research narrative → Explorer;
- additional transport, cycling, or edge-sensing modes;
- a continuous interpolated 2.5D surface;
- causal explanation generation;
- rankings or a composite Urban Pulse Index.

Add these only after the research case study passes its release gate.
