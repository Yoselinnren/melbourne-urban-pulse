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

## Phase 1H-E Explanation-Ready Aggregation

Phase 1H-E reads the Phase 1G context-enriched candidate episodes and pulse
groups, the Phase 1H-D `candidate_evidence_matches.csv`, the normalized manual
evidence table, and the human-maintained `evidence_match_reviews.csv`. It writes
full-row-count outputs:

- `explanation_ready_candidate_episodes.csv/json`
- `explanation_ready_pulse_groups.csv/json`
- `phase1h_explanation_ready_diagnostics.json`

The row-count contract is strict: every context-enriched episode and every pulse
group is retained exactly once. Candidates are not dropped, duplicated, merged,
ranked, or filtered. Candidates with no evidence links are retained with
scope-aware readiness metadata.

`not_in_manual_review_scope` means the candidate was not in the Phase 1H manual
review queue and was not manually researched in this phase. It must not be
interpreted as unexplained or evidence-free. If a candidate was in the manual
review queue but no evidence was linked, it is marked
`review_queue_no_evidence_linked` instead.

Explanation-ready means frontend-ready evidence metadata, not final explanation
prose. The outputs add structured fields such as evidence counts, evidence IDs,
source names and URLs, auto-match confidence, direction consistency, spatial
relevance, review-status summaries, and conservative readiness flags.

Auto-matched pending evidence is different from reviewed evidence:

- `auto_matched_pending_review` means Phase 1H-D found temporal and spatial
  candidate/evidence links, but no human review has upgraded them.
- `reviewed_verified_overlap` means a human review has confirmed overlap.
- `reviewed_plausible_association` means a human review has marked the evidence
  as plausibly associated with the candidate.
- `reviewed_insufficient_evidence`, `reviewed_unexplained`, and
  `reviewed_data_quality_issue` are review outcomes that must not be presented
  as explanations.

`causal_claim_allowed` remains `false` for every row. `generated_explanation_text`
is intentionally blank. A future UI may show the structured evidence metadata
and review status, but must not show causal explanation cards, an Urban Pulse
Index, infrastructure-pressure conclusions, or ranking language from this stage.

Limitations:

- Evidence links exist only where Phase 1H-D generated candidate/evidence
  matches.
- Empty manual review rows leave all links as `pending_review`.
- Source confidence and auto-match confidence are metadata for review, not proof.
- Human review of `candidate_evidence_matches.csv` remains the next step before
  optional final UI explanation cards.

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
- **After 1H-E:** review `candidate_evidence_matches.csv` manually and, only
  after review, optionally build final UI explanation cards.

Phase 1H-D and 1H-E create match and explanation-ready metadata outputs after
manual evidence exists. They still do not create causal cards,
infrastructure-pressure conclusions, an Urban Pulse Index, or frontend changes.

## Limitations and non-goals

- Queue inclusion means “worth researching,” not “important” or “confirmed.”
- Phase 1G weather and calendar overlap remains contextual.
- Evidence-type suggestions can be irrelevant and require human judgment.
- The queue is intentionally small and does not represent every candidate.
- No planned-works, event-PDF, transport, raw-data, or web source is activated.
- No automatic evidence matching or explanation generation is implemented.
