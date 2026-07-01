# Phase 1B: Regular Baseline Distributions

## Purpose

Phase 1B constructs empirical regular-activity distributions from the
context-classified Phase 1A panel. It establishes sensor-specific statistical
references for later observation scoring without calculating scores or
anomalies in this phase.

Baseline values are derived from all eligible observations. Dates and values
are not manually selected.

## Inputs

The primary input is:

- `data/processed/context_classified_panel.csv`

The stage also reads `data/processed/phase1a_diagnostics.json`, when available,
for study-period and configuration metadata.

Phase 1B assumes that Phase 1A has already generated every expected
sensor-hour, classified contexts, and recorded regular-baseline eligibility.

## Outputs

Generated artifacts remain under the ignored `data/processed/` directory:

- `regular_baselines.csv`;
- `regular_baselines.json`;
- `phase1b_diagnostics.json`.

Each baseline output row represents one `sensor_id + weekday + hour` group.
With three sensors, seven weekdays, and 24 hours, the expected maximum is 504
groups.

## Baseline Population

An input row is used only when:

- `is_regular_baseline_eligible` is true;
- `is_missing` is false;
- `observed_count` is present.

Phase 1A makes public holidays, manual event windows, severe weather
disruptions, daylight-saving transitions, missing observations, and
low-confidence observations ineligible. Phase 1B verifies that eligible input
rows do not carry these exclusion reasons.

School holidays remain included when Phase 1A marks them eligible. This is an
explicit Phase 1A policy, not evidence that school holidays have no effect.
Their baseline treatment should be evaluated in later sensitivity work.

## Grouping

The primary grouping is:

- `sensor_id`;
- `weekday`;
- `hour`.

This grouping preserves sensor-specific scale and recurring weekly/hourly
rhythm. Raw counts from different sensors are not pooled or directly treated
as equivalent.

## Distribution Statistics

For each non-empty group, Phase 1B calculates:

- `sample_size`;
- median;
- descriptive mean;
- minimum and maximum;
- `p05`;
- `p25`;
- `p75`;
- `p95`;
- `p99`;
- IQR;
- MAD.

The median and percentiles are the primary description of normal activity.
Mean is retained only as a descriptive statistic.

IQR is calculated as:

```text
p75 - p25
```

### Quantile Method

Quantiles use linear interpolation at:

```text
(n - 1) × probability
```

When the position falls between two ordered observations, the value is
linearly interpolated. This corresponds to the commonly used Hyndman–Fan type
7 convention. The convention is stored in every baseline row and in
diagnostics so future implementations can reproduce it.

### MAD Method

MAD is the median of absolute deviations from the group median:

```text
median(abs(observed_count - group_median))
```

Phase 1B stores raw, unscaled MAD. It does not apply a normal-consistency scale
factor and does not calculate robust z-scores.

## Baseline Confidence

`baseline_confidence` is a provisional data-sufficiency label based only on
`sample_size`:

| Label | Phase 1B rule |
| --- | --- |
| `high` | `sample_size >= 40` |
| `medium` | `30 <= sample_size < 40` |
| `low` | `15 <= sample_size < 30` |
| `insufficient` | `sample_size < 15` |

These cut-offs are transparent implementation assumptions, not a validated
confidence model. They can be revised after sensitivity analysis. Every
baseline retains its actual sample size.

A one-year `sensor_id + weekday + hour` group typically has only 52–53
possible observations before exclusions. High confidence therefore means
relatively sufficient coverage for this Phase 1B study period, not universal
statistical certainty.

## Fallback Policy

Phase 1B does not silently substitute broader fallback distributions.
Available low- or insufficient-sample groups remain in the output and retain
their confidence label.

The output fields are:

- `fallback_used`: normally `false`;
- `fallback_level`: `none`;
- `fallback_reason`: empty unless a future explicit fallback is introduced.

Groups with no eligible observations are absent and counted as missing baseline
groups in diagnostics. A broader weekday/weekend or sensor-hour fallback may
be designed later, but it must be explicit and versioned.

## Diagnostics

`phase1b_diagnostics.json` records:

- input and output paths;
- study period and selected sensors;
- total, eligible, and ineligible input rows;
- baseline population row count;
- actual, expected, and missing group counts;
- minimum, maximum, mean, and median group sample sizes;
- confidence-label counts;
- low and insufficient group details;
- group counts by sensor and weekday;
- fallback use;
- confidence thresholds;
- warnings and method notes.

Sanity checks verify:

- no ineligible row enters a baseline;
- no missing observation enters a baseline;
- eligible rows do not carry Phase 1A exclusion reasons;
- group count does not exceed 504;
- sample sizes remain plausible for a one-year weekday/hour grouping.

The script stops with an error if these core checks fail.

## Limitations

- Only one calendar year is available, limiting each group to approximately
  52–53 observations before exclusions.
- Baseline confidence reflects sample sufficiency only.
- Phase 1A weather and context rules remain provisional.
- School holidays remain in eligible groups unless excluded by another
  context.
- Sensor relocation, calibration, or unrecorded quality changes may affect the
  distributions.
- Quantiles and MAD describe observed variation but do not by themselves
  establish whether a future observation is anomalous.
- No fallback distribution is available for an empty group.

## Intentional Non-Goals

Phase 1B does not:

- score observations;
- calculate activity percentile, baseline ratio, robust z-score, anomaly
  strength, or pulse score;
- extract anomaly candidates;
- build dashboard summaries;
- modify the frontend;
- claim causal explanations;
- implement machine learning;
- implement edge-AI inference.

Future scoring should consume these versioned baseline distributions rather
than recreate statistics independently.
