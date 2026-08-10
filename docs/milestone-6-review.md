# Milestone 6 Researcher Review

## Review target

Approve the full-site visual direction before Milestone 7 implementation. The final public route remains:

`yoreny.com personal portfolio/CV -> project entry -> Melbourne Urban Pulse Hero and narrative -> Explorer`

The project must not replace the permanent portfolio homepage.

## Figma artifacts

| Artifact | Node | Review purpose |
| --- | --- | --- |
| Desktop Hero Final | `8:10` | Data-led thesis, New Year phase setup, navigation, study metrics |
| Desktop Full Narrative | `8:44` | Ten-chapter 1440 px research story |
| Mobile Hero Final | `136:387` | 390 x 844 first viewport |
| Mobile Full Narrative | `136:388` | Ten-chapter 390 px research story |
| Mobile Explorer Handoff | `136:389` | Dedicated 390 x 844 transition into the analytical experience |
| Hero States + Motion | `143:922` | Default, loading, static fallback, reduced motion, and implementation annotations |
| Motion Specification | `143:1319` | Trigger, property, timing, easing, repeat rules, and accessibility fallbacks |

## Narrative approval checklist

- The Hero communicates the research thesis rather than merely naming the topic.
- The New Year sequence is framed as a phase reversal, not as a holiday-causes-footfall claim.
- The January/July comparison shows different wet-weather duration and reach.
- The marathon/December comparison shows different event-linked temporal forms.
- The QVM episode remains explicitly unresolved.
- Method, limitations, provenance, and non-causal claim boundaries remain visible.
- The Explorer is presented as the audit trail for all 425 Pulses.
- Desktop and mobile preserve the same argument and evidence hierarchy.

## Motion approval checklist

- Hero trace reveal occurs once after verified data is ready: 300 ms per item, 60 ms stagger, under 800 ms total, ease-out.
- Only the selected sensor may use a restrained 3 s glow pulse; background tabs and offscreen views pause it.
- Chapters reveal once with opacity and a 20 px rise over 400 ms, ease-out.
- Loading uses a shape-accurate 1.5 s skeleton pulse in the default motion path.
- Reduced motion removes trace growth, glow loops, translation, and skeleton animation; content appears immediately or uses opacity only.
- Motion never delays navigation, hides keyboard focus, or implies a measured continuous city surface.

## Assistant verification

A read-only Figma file-context audit on 2026-08-11 verified the following current state:

- all seven review artifacts listed above exist at their recorded node IDs;
- the desktop narrative is a 1440 x 7440 frame with ten chapters and contains the research question, method, four case chapters, limitations, and Explorer handoff;
- the mobile narrative is a 390 x 7200 frame with the same ten-chapter evidence hierarchy;
- the dedicated mobile Explorer handoff is a 390 x 844 frame and explicitly routes selected cases into the Explorer;
- the Hero state section contains default, loading, static fallback, reduced-motion, and motion-specification children;
- every reviewed top-level artifact has `placeholder = false`.

This verifies design-file completeness, not researcher approval. Visual and narrative approval still belongs to the researcher.

## Gate

Milestone 6 passes only after the researcher has reviewed and approved the desktop narrative, mobile narrative, four Hero states, and motion specification. Any requested changes are resolved in Figma before production implementation begins.

## Approval

Researcher approval received on 2026-08-11. Milestone 6 is approved for Milestone 7 implementation.
