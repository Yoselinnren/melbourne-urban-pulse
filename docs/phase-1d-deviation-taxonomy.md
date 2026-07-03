# Phase 1D: Deviation Interpretation Taxonomy

## Purpose

Phase 1D adds auditable interpretation labels to every Phase 1C scored
sensor-hour row. It converts a standardized baseline-relative score into a
direction, magnitude band, signal family, subtype, and readiness state.

This is not anomaly extraction. Phase 1D does not rank rows, select top-N
observations, group hours into episodes, or produce a final anomaly-candidate
table. It prepares consistently labelled rows for a later candidate-extraction
and episode-grouping stage.

## Inputs and Outputs

Input for each sensor mode:

- `scored_analytical_panel.csv`

Outputs in the same mode-aware processed directory:

- `deviation_interpretation_panel.csv`;
- `deviation_interpretation_panel.json`;
- `phase1d_diagnostics.json`.

Defaults remain:

- `MVP_3`: `data/processed/`;
- `REPRESENTATIVE_12`: `data/processed/representative_12/`;
- `HIGH_COVERAGE_ALL`: `data/processed/high_coverage_all/`.

An explicit `--output-dir` overrides the mode default.

## Primary Score Selection

The input schema is inspected before rows are interpreted. Phase 1D selects the
first available standardized field in this order:

1. `robust_z_score`;
2. `z_score`;
3. `standardized_deviation`.

The current Phase 1C schema provides `robust_z_score`, so it is the selected
source. The value is copied to `primary_deviation_score`, and its field name is
stored in `primary_score_source`.

Raw count difference is never used as a silent cross-sensor fallback. If no
standardized field exists, the stage fails with a clear error.

## Interpretation Fields

Phase 1D appends:

- `primary_deviation_score`;
- `primary_score_source`;
- `observation_validity_state`;
- `baseline_confidence_band`;
- `deviation_direction`;
- `deviation_magnitude_band`;
- `signal_family`;
- `signal_subtype`;
- `candidate_readiness`;
- `interpretation_warning`;
- `interpretation_notes`.

Original observations, contexts, baseline references, and Phase 1C scores are
preserved unchanged.

## Magnitude and Direction

Magnitude uses the absolute primary score:

| Absolute score | Band |
| --- | --- |
| `< 1` | `near_regular` |
| `1` to `< 2` | `mild` |
| `2` to `< 3` | `moderate` |
| `3` to `< 5` | `strong` |
| `>= 5` | `extreme` |
| unavailable | `not_scored` |

Direction is:

- `above_baseline` for positive mild-or-stronger scores;
- `below_baseline` for negative mild-or-stronger scores;
- `near_baseline` for the near-regular band;
- `not_applicable` for missing, invalid, unscored, or baseline-unavailable
  rows.

## Signal Taxonomy

Observed high- or medium-confidence rows are assigned regular, positive, or
negative signal families. Subtypes distinguish mild, moderate, strong, and
extreme positive or negative deviations.

Missing observations become `missingness_signal`. Invalid, unscored, or
baseline-unavailable rows become `uninterpretable_signal`. Scored rows backed
by low or unavailable baseline confidence become `low_confidence_signal`.

These labels describe statistical deviation only. They do not state that an
event, disruption, weather condition, tourism pattern, or infrastructure
failure caused the observation.

## Candidate Readiness

`candidate_readiness` is a gate for future work, not a candidate decision:

- `review_ready`: observed and scored, high baseline confidence, strong or
  extreme deviation;
- `needs_context`: observed and scored, medium baseline confidence, strong or
  extreme deviation;
- `not_candidate`: observed and scored, with near-regular, mild, or moderate
  magnitude;
- `data_quality_review`: missing, invalid, unscored, baseline-unavailable, or
  missing-primary-score row;
- `low_confidence_excluded`: otherwise interpretable row with low or
  unavailable baseline confidence.

Moderate deviations are intentionally not review-ready. Missing and unscored
observations can never be review-ready.

`review_ready` is row-level candidate readiness only; it is not a final anomaly
candidate. Final anomaly candidates require a later phase that performs
candidate extraction and episode grouping.

## Diagnostics and Safety

Diagnostics count every validity state, confidence band, direction, magnitude,
signal family, subtype, readiness state, and warning.

`interpretation_warning` uses precedence: `missing_raw_observation`,
`unscored_observation`, and `invalid_count` warnings take priority over
baseline-confidence warnings. Therefore `baseline_confidence_counts` may not
exactly match `interpretation_warning_counts`.

Sanity checks require:

- output row count to match the Phase 1C row count;
- every row to have source, validity, family, and readiness labels;
- missing, unscored, and low-confidence rows not to be review-ready;
- review-ready rows to be observed, scored, high-confidence, and have a primary
  score;
- no `anomaly_candidates` file to exist or be created.

## Limitations and Non-Goals

- Thresholds are transparent Phase 1D rules, not validated anomaly thresholds.
- `robust_z_score` inherits the raw-MAD methodology and limitations of Phase
  1C.
- A review-ready label does not establish that a row is anomalous.
- Phase 1D does not explain real-world causes.
- Phase 1D does not use external event data.
- Phase 1D does not produce final anomaly candidates.
- Phase 1D does not rank observations or group consecutive hours.
- Phase 1D does not modify frontend or public dashboard data.
- Phase 1D does not implement machine learning or edge-AI inference.
- Phase 1D only prepares rows for later candidate extraction and episode
  grouping.
