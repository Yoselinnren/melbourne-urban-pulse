# Milestone 6: Full-site Design and Motion Audit

## Decision summary

The implemented product is an approved analytical Explorer surrounded by two legacy entry surfaces. It is not yet a complete research case-study website. The next design artifact must define the full narrative page and its responsive and motion states before production implementation begins.

Installed external Skill: the researcher approved [`joepUI/motion-ref-skill`](https://github.com/joepUI/motion-ref-skill), installed locally as `motion-ref` on 2026-08-10. It is a supervised motion-reference library and must not determine the visual concept or add dependencies by default.

## Implemented-site inventory

### `/` - legacy landing placeholder

Present:

- project title and generic research-prototype description;
- two calls to action, one pointing to the legacy dashboard;
- three cards sourced from the compact MVP dataset.

Missing or incorrect:

- no data-driven Urban Pulse Field Hero;
- no approved result thesis or selected cases;
- no narrative transition from regular rhythm to reviewed deviations;
- no methodology, limitations, researcher role, or Explorer entry sequence;
- no dark visual system shared with the Explorer;
- the main call to action points to `/dashboard`, not `/explore`;
- the page still presents the compact MVP vocabulary rather than the 2025 representative-sensor study.

### `/dashboard` - deprecated vertical slice

This route is an early implementation artifact, not part of the target public journey. It uses the compact dashboard data model, labels the Pulse Field as a placeholder, and retains MVP-era content. It should be removed from public navigation after any still-useful components have been evaluated.

### `/explore` - approved analytical experience

Present:

- annual 2025 Explorer with 12 representative sensors and 425 Pulses;
- spatial, temporal, filtering, Pulse, sensor, evidence, and uncertainty states;
- responsive layout, keyboard semantics, loading/error states, and reduced-motion override.

Integration gaps:

- Home returns to the placeholder landing page;
- Methodology is visibly disabled;
- no narrative handoff carries a selected case into the Explorer;
- no shared site navigation, case-study chapter state, or final project identity system exists.

## Required full-site logic

The first public release should use one continuous research narrative rather than a collection of disconnected dashboard pages:

1. **Hero / thesis** - a live Urban Pulse Field introduces expected rhythm and observed departure.
2. **Research question** - explain what is being compared and why named context is not itself the result.
3. **Method in brief** - move from hourly observations to regular baselines, episodes, Pulses, and reviewed evidence.
4. **New Year phase reversal** - show one date changing from network-wide above baseline to network-wide below baseline.
5. **Weather comparison** - contrast the short January and sustained July wet-weather signatures.
6. **Event-form comparison** - contrast the compact marathon Pulse with the longer December event window.
7. **Unresolved local episode** - retain the QVM signal without forcing an explanation.
8. **Limitations and provenance** - state purposive case selection, observational evidence, and non-causal boundaries.
9. **Explorer handoff** - invite inspection of all 425 Pulses while preserving the selected case in the URL where practical.
10. **Researcher role and contact** - identify authorship, research interest, contribution, and application context.

The methodology may be a dedicated route or an anchored chapter, but it must be directly reachable from both the narrative and Explorer navigation.

## Figma gap audit status

The connected Figma file `Melbourne Urban Pulse - UI Design` was inspected on 2026-08-10. It contains one top-level page, `00 - Cover`, and one 1440 x 900 frame, `Cover / Melbourne Urban Pulse` (`24:3`). No Annual Explorer, Hero, narrative, methodology, mobile, or motion-design frames are present in this file.

The cover establishes useful shared tokens - the Explorer dark background, cyan research label, Geist typography, muted explanatory copy, and pale-yellow version marker - but it is a design-file cover rather than a website Hero. The Figma-to-code gap is therefore not a matter of missing implementation: the complete website screens still need to be designed.

The Figma review must account for these nodes or equivalent frames:

- full desktop narrative page;
- full mobile narrative page;
- Hero default, active, loading, fallback, and reduced-motion states;
- all four selected-case chapters;
- method/provenance and limitation presentation;
- narrative-to-Explorer transition;
- shared navigation and footer;
- Explorer entry with and without a selected Pulse;
- motion annotations specifying trigger, duration, easing, property, and fallback.

## Motion and dynamic-art boundary

Use at most three motion roles per view:

1. **Hero atmosphere** - restrained sensor pulses, vertical traces, glow, and temporal sweep tied to real project data.
2. **Narrative transition** - section-level reveal or state change that explains comparison, not decoration on every element.
3. **Interaction feedback** - hover, focus, selection, loading, and route continuity.

Implementation order:

1. accessible SVG plus CSS/WAAPI for the first Urban Pulse Field prototype;
2. Canvas only if measured density or continuous animation makes SVG unsuitable;
3. WebGL only if a reviewed prototype demonstrates a material narrative or performance advantage.

Every motion state must have a static, immediately legible `prefers-reduced-motion` path. Animation must not delay content, imply unmeasured precision, or turn sensor points into a claimed continuous city surface.

## GitHub Skill review

Review date: 2026-08-10.

| Candidate | Fit | Maintenance and licence | Security/dependency surface | Decision |
| --- | --- | --- | --- | --- |
| [`joepUI/motion-ref-skill`](https://github.com/joepUI/motion-ref-skill) | Strong motion implementation reference: 119 effects across UI, atmosphere, data visualisation, scroll, and entry states | MIT; 23 commits; latest reviewed commit 2026-06-26; one GitHub star at review time | Skill and Markdown references; no executable-install pattern found in reviewed source; large demo/reference footprint; young project with little independent adoption evidence | **Approved and installed as `motion-ref`.** Use only relevant categories under assistant supervision |
| [`anthropics/skills` frontend-design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md) | Strong visual-direction and anti-template guidance; treats the Hero as the page thesis | Apache 2.0; highly active parent repository | Instruction-only skill with no runtime dependency for this use | Useful optional design critic, but not a substitute for Figma or a dynamic-art implementation skill |
| [`simota/agent-skills` Flow](https://github.com/simota/agent-skills/blob/main/flow/SKILL.md) | Detailed CSS/JS motion, performance, accessibility, and browser fallback guidance | MIT; parent repository active on 2026-08-10 | The parent contains roughly 137 agents and extensive cross-references; much broader instruction surface than this project needs | Do not install the full repository. Reconsider only if the smaller candidate proves insufficient |

## Approval gates

Before visual implementation:

- the connected Figma file is confirmed as the intended project file, or the researcher supplies a different file if the missing screens exist elsewhere;
- `joepUI/motion-ref-skill` is approved and installed as `motion-ref`;
- assistant designs the missing frames and proposes the Hero art direction using the approved result narrative;
- researcher sees and approves desktop, mobile, motion, and reduced-motion designs.
