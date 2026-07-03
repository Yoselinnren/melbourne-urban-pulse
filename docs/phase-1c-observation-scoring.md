# Phase 1C: Baseline-Relative Observation Scoring

## Purpose

Phase 1C joins every row in the context-classified analytical panel to its
matching regular baseline distribution and calculates transparent,
baseline-relative measures.

All contexts are retained. Public holidays, weather disruptions, school
holidays, and other special periods can therefore be compared with the regular
reference distribution without being reclassified as regular observations.

Phase 1C produces descriptive scores. It does not decide which observations
are anomaly candidates.

## Inputs

The required inputs are:

- `data/processed/context_classified_panel.csv`;
- `data/processed/regular_baselines.csv`.

Phase 1A and Phase 1B diagnostics are read when available as upstream
provenance checks, but row-level scoring is determined by the two CSV
contracts.

## Outputs

Generated artifacts remain under the ignored `data/processed/` directory:

- `scored_analytical_panel.csv`;
- `scored_analytical_panel.json`;
- `phase1c_diagnostics.json`.

The scored panel preserves every input row and all Phase 1A fields. It adds
baseline references, scoring fields, notes, and a Phase 1C processing version.
CSV list fields are JSON-encoded; JSON output preserves arrays and null values.

## Baseline Join

Each observation joins to a baseline using:

- `sensor_id`;
- `weekday`;
- `hour`.

The join applies to baseline-eligible and baseline-ineligible observations.
This is intentional: special-context observations are compared against the
regular distribution for the same sensor, weekday, and hour.

The output retains:

- baseline sample size;
- median and descriptive mean;
- `p05`, `p25`, `p75`, `p95`, and `p99`;
- IQR and raw MAD;
- baseline confidence, method, quantile convention, and processing version.

`baseline_available` explicitly records join success. A missing observation can
still have an available baseline, but it receives no numeric activity score.

## Scoring Formulas

### Signed Deviation

```text
signed_deviation = observed_count - baseline_median
```

Positive values indicate above-baseline activity and negative values indicate
below-baseline activity.

### Baseline Ratio

```text
baseline_ratio = observed_count / baseline_median
```

When the baseline median is zero or unavailable, the result remains null and a
scoring note records the reason.

### Signed Deviation Ratio

```text
signed_deviation_ratio =
    (observed_count - baseline_median) / baseline_median
```

This field preserves direction. It is null when the baseline median is zero or
unavailable.

### Robust Z-Score

The primary Phase 1C scale is raw, unscaled MAD:

```text
robust_z_score =
    (observed_count - baseline_median) / baseline_mad
```

If MAD is zero or unavailable and IQR is positive, Phase 1C uses:

```text
robust_z_score =
    (observed_count - baseline_median) / baseline_iqr
```

The row's `scoring_notes` records whether MAD or the IQR fallback was used. If
neither scale is positive and available, robust z-score remains null. Division
by zero is never performed silently.

This project uses the term `robust_z_score` as a baseline-relative robust
deviation measure. Because Phase 1B MAD is unscaled, it should not be
interpreted as a standard-normal z-score.

## Activity Percentile Approximation

Phase 1C does not reload every observation from the original baseline sample.
It approximates distribution position using the stored anchors:

| Baseline anchor | Assigned percentile |
| --- | ---: |
| `p05` | 0.05 |
| `p25` | 0.25 |
| median | 0.50 |
| `p75` | 0.75 |
| `p95` | 0.95 |
| `p99` | 0.99 |

Values between anchors use linear interpolation. The mapping is monotonic and
bounded to `[0, 1]`.

Below `p05`, non-negative counts are mapped between 0 and 0.05 using `p05` as
the upper anchor. Above `p99`, the `p95`–`p99` span provides a short
extrapolation from 0.99 toward 1, after which the result is capped.

Repeated percentile values can create a step at a flat distribution segment.
This approximation is suitable for transparent display and ranking, but it is
not the exact empirical rank that would be calculated from the full sample.

## Anomaly Direction

`anomaly_direction` is derived only from signed deviation:

- `above` when signed deviation is positive;
- `below` when signed deviation is negative;
- `none` when signed deviation is zero;
- `unavailable` when the observation or baseline median is unavailable.

The label does not declare that an observation is an anomaly.

## Provisional Anomaly Strength

`anomaly_strength` is a bounded display/ranking encoding, not anomaly
detection.

Using robust z-score magnitude:

- strength is 0 when `|robust_z_score| <= 0.5`;
- it increases linearly between 0.5 and 3;
- it is capped at 1 when magnitude reaches or exceeds 3.

If robust z-score cannot be calculated but activity percentile is available,
Phase 1C uses percentile extremeness as a documented fallback:

- strength is 0 inside the approximate interquartile range;
- it increases toward 1 as the percentile approaches 0 or 1.

The score does not create an anomaly candidate and must not be interpreted as a
probability.

## Scoring Confidence

Phase 1C maps Phase 1B baseline labels to provisional reliability values:

| Baseline confidence | Reliability value |
| --- | ---: |
| `high` | 0.90 |
| `medium` | 0.75 |
| `low` | 0.50 |
| `insufficient` | 0.25 |

For a valid scored observation:

```text
scoring_confidence =
    min(observation_confidence, baseline_reliability_value)
```

This weakest-component rule avoids inflating confidence when either the
observation or reference distribution is less reliable. Missing observations
and unavailable baselines receive zero scoring confidence.

Scoring confidence represents provisional reliability only. It is not mixed
with activity intensity or anomaly strength.

## Diagnostics

`phase1c_diagnostics.json` records:

- input and output row counts;
- baseline join success and failure;
- scored and unscored observations;
- missing observations;
- invalid baseline median and scale counts;
- MAD-to-IQR fallback use;
- null percentile and robust-score counts;
- anomaly direction counts;
- anomaly-strength and scoring-confidence summaries;
- baseline confidence counts across panel rows;
- rows by primary context;
- baseline and panel join-key coverage;
- warnings, method notes, and sanity checks.

The stage fails when any core invariant is violated:

- output row count differs from input;
- a missing observation receives numeric scores;
- a non-missing observation lacks a baseline;
- the baseline file does not contain all 504 expected keys;
- a panel join key is uncovered;
- score direction is inconsistent;
- activity percentile or anomaly strength is outside `[0, 1]`.

## Limitations

- Activity percentile is reconstructed from summary anchors rather than the
  full baseline sample.
- Raw unscaled MAD affects the numerical interpretation of robust z-score.
- Phase 1A context and weather-disruption rules remain provisional.
- School holidays remain in regular baselines under the current Phase 1A
  policy.
- Baseline confidence is based on sample sufficiency rather than a validated
  uncertainty model.
- Special-context comparison shows association with a regular baseline, not
  the cause of a difference.
- Anomaly strength is a visual encoding and has not been calibrated against
  reviewed events or sensor faults.

## Intentional Non-Goals

Phase 1C does not:

- extract anomaly candidates;
- generate event explanations;
- build dashboard summaries;
- modify the frontend;
- calculate pulse score or infrastructure pressure;
- implement machine learning;
- implement edge-AI inference;
- claim causal relationships.

Future anomaly extraction should consume this scored panel, retain its context
and provenance, and apply separately configurable candidate rules.
