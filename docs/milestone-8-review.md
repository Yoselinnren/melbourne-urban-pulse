# Milestone 8 Release Review

Date: 2026-08-12

## Release scope

The first public release is limited to the existing lightweight entry at `/`, the complete research narrative at `/projects/melbourne-urban-pulse`, and the analytical Explorer at `/explore`. Personal portfolio/CV content is deferred to a separate phase and does not block this release.

## Acceptance results

- `pnpm lint`: passed.
- `pnpm build`: passed, including TypeScript and static generation of all routes.
- Lighthouse mobile simulation: project narrative performance 93 and accessibility 100; Explorer performance 92 and accessibility 96. Both pages have zero cumulative layout shift.
- UI data validation: passed for 441 JSON files and 425 Pulse detail payloads; no Pulse exceeds the 250 KB hard limit.
- Data safety scan: no credential or private-key material found; the validator rejects private reviewer fields, absolute paths, causal flags, and forbidden source paths.
- Desktop check at 1440 x 1000: `/`, the project narrative, and `/explore` have one H1 and main landmark, accessible control names, no broken images, no horizontal overflow, and no console warnings or errors.
- Mobile check at 390 x 844: the same route and accessibility checks passed with no horizontal overflow.
- Route check: `/`, `/projects/melbourne-urban-pulse`, `/explore`, and `/dashboard` return HTTP 200.
- Internal handoff check: all rendered internal links, including the seven selected Pulse/sensor Explorer links, return HTTP 200.

## Fix made during review

The independent UI-data validator still expected the pre-review baseline. Its assertions now match the approved evidence state: 64 human reviews, zero pending-review Pulses, and 63 reviewed evidence matches represented inside Pulse payloads. The remaining reviewed match belongs to an isolated episode outside the Pulse detail set.

Lighthouse also found an invalid `aria-label` on the narrative Pulse plot. The plot now has `role="img"`, and its accessibility score increased from 96 to 100.

## Accepted limitation

Explorer's only weighted Lighthouse accessibility failure is target size on the 425 interactive marks in the annual timeline. Each mark retains a descriptive accessible name and keyboard selection semantics, but the dense year-scale view cannot provide 24 x 24 px pointer targets without overlapping adjacent Pulses and making selection ambiguous. A future zoomed or grouped timeline may remove this limitation; it is not expanded in this release because that would change the approved analytical interface.

## Approval and publication

The researcher explicitly approved publication on 2026-08-12. The approved commits were pushed to GitHub `main` and deployed through Vercel.

Production verification passed:

- `https://yoreny.com` redirects permanently to `https://www.yoreny.com` with HSTS enabled;
- `/`, `/projects/melbourne-urban-pulse`, and `/explore` return HTTP 200 with the expected titles;
- the narrative contains the released New Year case and the corrected Pulse-plot image role;
- the public UI manifest returns HTTP 200 with data version `c4dcfd0022f903296c5f0d4f`, 64 human reviews, and zero pending-review Pulses;
- the selected New Year Explorer route returns HTTP 200.
