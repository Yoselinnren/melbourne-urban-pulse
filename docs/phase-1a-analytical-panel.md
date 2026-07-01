# Phase 1A: Analytical Panel and Context Classification

## Purpose

Phase 1A implements the first foundation of the analytical framework:

1. a canonical long-form hourly panel; and
2. explicit context classification and regular-baseline eligibility.

It separates analytical data preparation from the existing frontend delivery
builder. It does not calculate baseline distributions or anomaly scores.

## Inputs

| Source | Role |
| --- | --- |
| `data/raw/pedestrian/pedestrian_counts_hourly_full.csv` | Hourly pedestrian observations |
| `data/raw/sensors/pedestrian_sensor_locations.csv` | Sensor identity, status, and coordinates |
| `data/raw/weather/open_meteo_melbourne_hourly_2025.json` | Hourly weather context |
| `data/raw/calendar/victoria_important_dates_2025.csv` | Public holidays, school periods, and daylight-saving context |
| `data/manual/events_manual.csv` | Optional manually verified event windows |

The manual event file may contain only its header. Phase 1A treats that state as
zero loaded events and does not invent event context.

Planned works are not active in Phase 1A. They require date-range, status, and
spatial-relevance validation before they can affect baseline eligibility or
explain unusual observations.

## Study Period and Sensors

The panel covers every local hour from `2025-01-01 00:00` through
`2025-12-31 23:00` using `Australia/Melbourne` timezone semantics.

The selected sensor IDs are:

- `4` — Town Hall;
- `3` — Melbourne Central;
- `133` — Southern Cross.

The selection is defined as a top-level configuration constant in
`scripts/build_analytical_panel.py` so it can be expanded later.

With 8,760 local hourly keys and three sensors, the expected canonical panel
contains 26,280 rows.

## Processing Stages

### `scripts/build_analytical_panel.py`

This stage:

- generates one row for every selected sensor and hourly key;
- joins pedestrian observations without filling missing values with zero;
- joins sensor metadata;
- joins Open-Meteo weather by hourly key;
- joins calendar context by date;
- expands paired school-term and school-holiday boundaries into daily windows;
- preserves explicit daylight-saving transition dates;
- joins overlapping manual event windows when records exist;
- adds source provenance and separate confidence components;
- writes the canonical CSV and JSON panels.

It does not calculate activity or anomaly metrics.

### `scripts/classify_contexts.py`

This stage reads the canonical CSV panel and adds:

- `context_tags`;
- `primary_context`;
- `is_regular_baseline_eligible`;
- `baseline_exclusion_reasons`;
- `context_confidence`.

A row may carry multiple context tags. `primary_context` follows the explicit
precedence recorded in `phase1a_diagnostics.json`.

`unknown_anomaly_candidate` is intentionally absent. It belongs to a later
anomaly-extraction stage.

## Generated Outputs

All outputs are generated under the ignored `data/processed/` directory:

- `analytical_hourly_panel.csv`;
- `analytical_hourly_panel.json`;
- `context_classified_panel.csv`;
- `context_classified_panel.json`;
- `phase1a_diagnostics.json`.

CSV list fields are encoded as JSON arrays. JSON outputs preserve them as
arrays. Empty observed values remain blank in CSV and `null` in JSON.

## Missingness Handling

For each expected sensor-hour:

- `source_hour_present` records whether a source observation row exists;
- `observed_count` preserves the source value or remains missing;
- `is_missing` is true when no usable observed count exists;
- `missing_reason` distinguishes an absent source hour from a present row with
  a missing count;
- missing observations are never converted to zero;
- observation confidence is zero for missing readings.

Missing observations remain in the panel but are not eligible for a regular
baseline.

## Calendar and Event Handling

Public holidays are matched from explicit calendar dates.

School-term and school-holiday records with identifiable start/end boundary
labels are expanded into daily windows before context classification. The
expanded labels remain distinguishable from the original source labels.

Daylight-saving transition dates are tagged from explicit calendar records.
Phase 1A follows the project's existing 8,760-key local-time convention; it
does not attempt to represent the repeated autumn clock hour as an additional
row. The 2025 UTC offsets are applied with explicit Melbourne transition
boundaries so the scripts do not require an additional timezone-data package
on Windows.

Manual events are expanded to overlapping hourly windows. If an end time is
earlier than its start time, the event is treated as crossing midnight.
Current manual events without a sensor-specific field apply as contextual
event windows to all selected sensors.

## Context Rules

Supported Phase 1A tags are:

- `regular_weekday`;
- `regular_weekend`;
- `public_holiday`;
- `school_holiday`;
- `daylight_saving_transition`;
- `weather_disruption`;
- `manual_event_window`;
- `low_confidence_observation`.

`planned_work_context` is reserved but inactive until source validation is
implemented.

The provisional weather-disruption rule is:

```text
rain > 0 OR wind_speed_10m >= 30
```

This flag provides context only. It does not establish that weather caused an
activity change.

## Regular-Baseline Eligibility

A row is eligible when it:

- has a valid observed count;
- has observation confidence at or above the Phase 1A threshold;
- is not a public holiday;
- is not in a manual event window;
- is not a weather-disruption period;
- is not a daylight-saving transition.

Exclusion reasons are retained as a list. A row can have more than one reason.

School holidays are tagged but not automatically excluded in Phase 1A. Their
effect should be evaluated empirically before a final baseline policy is
chosen.

The regular weekday/weekend tags describe calendar rhythm. A special-context
row can retain one of these tags while also being ineligible; downstream work
must use the eligibility field rather than the presence of a regular tag alone.

## Confidence Components

Phase 1A keeps reliability separate from activity:

- `observation_confidence` reflects availability and basic sensor status;
- `weather_confidence` reflects whether hourly weather is present;
- `calendar_confidence` is a provisional source-level reliability value;
- `event_confidence` reflects loaded manual annotation confidence and is not
  applicable when no manual event overlaps;
- `context_confidence` is a simple mean of applicable reliability components.

These are provisional operational values. They are not activity scores and
must not be interpreted as validated probabilistic confidence.

## Intentional Non-Goals

Phase 1A does not implement:

- `baseline_count` or regular-baseline distributions;
- percentiles, IQR, MAD, or robust z-scores;
- activity normalisation;
- anomaly strength or anomaly candidates;
- pulse scores or infrastructure-pressure proxies;
- dashboard summaries;
- planned-works classification;
- frontend exports or visual changes;
- edge-AI inference.

## Difference from the MVP Builder

`scripts/build_mvp_dashboard_data.py` is an end-to-end delivery
proof-of-concept that combines source loading, provisional metrics, explanation
cards, and frontend JSON generation.

Phase 1A instead creates a long-form analytical contract and an explicit
context/eligibility stage. It preserves one row per sensor-hour, expands
supported calendar intervals, records exclusion reasons, and stops before
baseline or anomaly calculation. Future baseline work should consume the
context-classified panel rather than extend the MVP builder's provisional
scoring logic.
