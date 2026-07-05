# Phase 1H: Manual Evidence Verification and Explanation Layer

## Purpose

Phase 1H prepares selected pedestrian-signal candidates for structured human
evidence research. It covers more than events: relevant evidence may include
calendar conditions, weather warnings, transport disruptions, road closures,
planned works, public activities, data-quality issues, or an explicitly
unresolved context.

Phase 1H-A defines the manual data contracts. Phase 1H-B creates a small,
deterministic and stratified review queue. Neither stage asserts that a
candidate has been explained.

The review queue is **not a ranking**, **not a priority score**, and **not a top
anomaly list**. No cause has been verified, and no explanation-ready output is
produced. Manual evidence collection is required before matching or
explanation readiness.

## Relationship to Phase 1G

Phase 1H-B reads the Phase 1G context-enriched candidate episodes, pulse groups,
and diagnostics. `REPRESENTATIVE_12` is the primary mode; `MVP_3` is supported
as a smoke test. `HIGH_COVERAGE_ALL` is not supported.

Phase 1G already supplies observed or official context including hourly
weather, public-holiday labels, school-calendar labels, daylight-saving labels,
sensor metadata, and co-occurrence summaries. These fields describe overlap.
They do not establish why a pedestrian signal occurred. Phase 1H-A/B does not
change Phase 1G files or logic.

## Manual evidence facts

`data/manual/evidence_manual.csv` stores external facts and provenance. It does
not primarily store episode or pulse-group identifiers.

| Field | Meaning |
| --- | --- |
| `evidence_id` | Stable manual evidence identifier |
| `evidence_name` | Short factual label |
| `evidence_type` | Controlled evidence category |
| `source_name`, `source_url` | Evidence provenance |
| `source_accessed_date` | Date the source was checked |
| `start_timestamp`, `end_timestamp` | Evidence interval |
| `timezone` | Source timezone; default is `Australia/Melbourne` |
| `location_name`, `precinct` | Human-readable spatial context |
| `latitude`, `longitude` | Optional point coordinates |
| `spatial_scope` | Controlled spatial coverage |
| `expected_pedestrian_impact` | Cautious prior expectation |
| `expected_direction` | Controlled expected direction |
| `evidence_confidence` | Confidence in the external fact |
| `notes` | Research notes |
| `created_by`, `created_at` | Manual provenance |

When populated, timestamps must use ISO 8601 with an explicit UTC offset.
Header-only manual files may contain no values.

### Controlled vocabularies

`evidence_type`:

- `public_holiday`
- `school_holiday`
- `weather_warning`
- `major_event`
- `sports_event`
- `concert`
- `festival`
- `parade`
- `transport_disruption`
- `road_closure`
- `planned_works`
- `commercial_activity`
- `cultural_activity`
- `data_quality_issue`
- `unknown_context`
- `other`

`spatial_scope`: `point`, `precinct`, `corridor`, `venue`, `citywide`,
`unknown`.

`expected_direction`: `above`, `below`, `mixed`, `none`, `unknown`.

`evidence_confidence`: `low`, `moderate`, `high`.

## Manual match reviews

`data/manual/evidence_match_reviews.csv` is reserved for later human judgments.
Phase 1H-A creates only its header and Phase 1H-B does not populate it.

| Field | Meaning |
| --- | --- |
| `candidate_type` | `episode` or `pulse_group` |
| `candidate_id` | Stable analytical candidate identifier |
| `evidence_id` | Identifier from the manual evidence table |
| `review_status` | Human review decision |
| `explanation_strength` | `none`, `weak`, `moderate`, or `strong` |
| `reviewer_notes` | Human rationale |
| `reviewed_by`, `reviewed_at` | Review provenance |

Future `review_status` values are `pending_review`, `verified_overlap`,
`plausible_association`, `insufficient_evidence`, `unexplained`,
`data_quality_issue`, and `rejected`. These values are not assigned in
Phase 1H-A/B.

## Legacy events file

`data/manual/events_manual.csv` remains a narrow legacy compatibility file. It
is not reinterpreted as the general evidence table and is not modified by this
phase. The new evidence schema supports non-event evidence and separates
external facts from candidate-specific review judgments.

## Review queue generation

`scripts/build_evidence_review_queue.py` writes:

- `phase1h_review_queue.csv`
- `phase1h_review_queue.json`
- `phase1h_review_queue_diagnostics.json`

Outputs are written to the selected mode's processed directory. The queue uses
stable ordering and transparent inclusion reasons. It prefers pulse groups and
adds a small number of isolated or paired episodes when available.

The selection aims to cover broad or network-wide pulses, longer intervals,
context-light cases, public and school holidays, rain or provisional weather
disruption, both deviation directions, daylight-saving overlap, and an
isolated or paired episode. A candidate may carry multiple inclusion reasons.
No combined score, rank, priority band, or random selection is used.

Suggested evidence types are research prompts derived from existing context.
They do not imply that the suggested evidence exists. In particular, an
official context overlap is not a behavioural explanation.

## Language guardrails

Permitted cautious phrases include:

- coincided with
- occurred during
- overlapped with
- plausibly associated with
- consistent with

Generated interpretation must not use the following causal phrases:

- caused
- due to
- because of
- explained by
- attributed to

The queue contains no generated explanation prose.

## What the researcher does next

After Phase 1H-A/B, the researcher must:

1. inspect each queued case;
2. locate authoritative, time-specific and location-specific sources;
3. enter external facts and provenance in `evidence_manual.csv`;
4. record uncertainty and leave unsupported cases unresolved;
5. avoid entering candidate-match judgments in the evidence facts table.

## Deferred Phase 1H work

- **1H-C:** manually collect and validate evidence facts.
- **1H-D:** generate candidate/evidence matches using documented temporal and
  spatial rules.
- **1H-E:** record human match reviews and build explanation-ready datasets.

Candidate/evidence matching is intentionally absent because the evidence table
is empty and matching rules require separately validated facts. Phase 1H-A/B
does not create match outputs, explanation-ready datasets, causal cards,
infrastructure-pressure conclusions, an Urban Pulse Index, or frontend changes.

## Limitations and non-goals

- Queue inclusion means “worth researching,” not “important” or “confirmed.”
- Phase 1G weather and calendar overlap remains contextual.
- Evidence-type suggestions can be irrelevant and require human judgment.
- The queue is intentionally small and does not represent every candidate.
- No planned-works, event-PDF, transport, raw-data, or web source is activated.
- No automatic evidence matching or explanation generation is implemented.
