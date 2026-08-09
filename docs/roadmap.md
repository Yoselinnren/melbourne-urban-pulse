# Research Portfolio Roadmap

## Goal

Deliver Melbourne Urban Pulse as an English-language research case study for research-degree applications. There is no fixed deadline; work proceeds milestone by milestone, with scope held to the smallest credible first release.

## Current baseline

Completed:

- reproducible analytical phases from source profiling through explanation-ready aggregation;
- 12-sensor representative mode with 4,647 episodes and 425 Pulses;
- deterministic UI data v1 and independent validation;
- working annual Explorer with spatial, temporal, filter, Pulse, and sensor states;
- initial Figma workspace and Annual Explorer capture.

Still required:

- human review of automatic evidence matches;
- an approved visual system and complete Explorer state designs;
- narrative homepage and methodology presentation;
- responsive, accessibility, and browser acceptance;
- public-release and research-application handoff material.

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

## Milestone 5 - Narrative case study

Assistant:

- design and implement the English homepage, methodology, data sources, limitations, selected cases, and Explorer entry point;
- write draft copy from verified project evidence and researcher-provided personal context;
- connect the narrative to the Explorer without duplicating the analytical interface.

Researcher:

- provide name, academic background, intended research direction, contact links, acknowledgements, and a short personal motivation;
- approve the final wording and selected cases.

Gate: an admissions reviewer can understand the question, method, contribution, limitations, and researcher's role without opening the repository.

## Milestone 6 - Release

Assistant:

- run final accessibility, performance, responsive, data-safety, and clean-build checks;
- prepare deployment configuration and repository handoff;
- publish only after explicit approval.

Researcher:

- select and authorise hosting;
- approve the public URL and final release;
- later decide how the project sits beneath a personal portfolio and custom domain.

Gate: the public build is accurate, navigable, safe, and approved.

## Visual direction

Use Shopify Editions Winter '26 as a mood reference, not a layout template:

- borrow editorial scale, chapter navigation, deep atmospheric backgrounds, fine technical grids, and deliberate pacing;
- translate Renaissance imagery into Melbourne-specific research material such as archival map texture, restrained civic colour, sensor geometry, and temporal traces;
- keep analytical controls calm, readable, and accessible;
- avoid copied assets, novelty interaction, heavy WebGL, and animation that competes with evidence.

## Deferred on purpose

- personal portfolio shell and custom-domain architecture;
- additional transport, cycling, or edge-sensing modes;
- a continuous interpolated 2.5D surface;
- causal explanation generation;
- rankings or a composite Urban Pulse Index.

Add these only after the research case study passes its release gate.
