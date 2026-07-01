# Analytical Framework

## Purpose

Melbourne Urban Pulse requires an analytical layer that distinguishes normal urban
rhythms from special conditions. The objective is not to average all activity in
a calendar year into a single notion of normality. Public holidays, major events,
severe weather, planned disruptions, and unexplained extremes can have
systematically different activity patterns and should not be mixed into the
reference population without qualification.

Full-year data should instead be used to construct empirical distributions of
regular activity for each sensor and time context. Special days and anomaly
candidates can then be compared with those regular baselines. This makes
deviations interpretable: the system can describe whether an observation is
typical for that sensor, weekday, and hour before considering weather, events,
or other explanations.

The framework is intended to support transparent research, reproducible
processing, and visual explanation. It prioritises explicit statistical
references and provenance over opaque composite scores.

## Current Implementation Boundary

The existing `scripts/build_mvp_dashboard_data.py` pipeline is an engineering
MVP. It demonstrates that local raw pedestrian, sensor, weather, and calendar
data can be transformed into a coherent, frontend-readable JSON contract. It
also preserves missing observations and generates a compact real-data dataset
for the current frontend vertical slice.

Its `baseline_count`, `activity_intensity`, `baseline_deviation`,
`anomaly_score`, `pulse_score`, and confidence fields are provisional. They are
useful for interface development and pipeline validation, but they should not
be treated as final, validated, research-grade indicators.

In particular, the current pipeline does not construct context-aware
regular-day baseline distributions. Its baseline population can include public
holidays, event periods, and weather disruptions. The framework below defines
the intended next analytical layer; it does not describe functionality that is
already implemented.

The current MVP builder should remain a delivery proof-of-concept. Future
analytical processing should not simply extend its provisional scoring logic
without first implementing regular-baseline separation and explicit anomaly
workflows.

## Canonical Unified Hourly Panel

The canonical analytical dataset should be a long-form hourly panel. Each row
should represent one sensor at one timestamp. This table should be the common
input to baseline construction, anomaly detection, comparisons, summaries, and
visualisation exports.

The intended field groups are:

| Group | Example fields |
| --- | --- |
| Time identity | `timestamp`, `date`, `hour`, `weekday`, timezone, daylight-saving offset |
| Sensor identity | `sensor_id`, sensor name, status, location type, latitude, longitude, precinct, installation or relocation metadata |
| Observation | `observed_count`, directional counts, source record identifier |
| Missingness and quality | `is_missing`, `missing_reason`, validity flags, sensor-active flag, source-quality flags |
| Weather | temperature, apparent temperature, humidity, precipitation, rain, wind speed, weather code |
| Calendar | weekend flag, public-holiday flag, school-term flag, school-holiday flag, daylight-saving transition flag, season |
| Manual events | `event_id`, event type, location or precinct, start/end time, expected effect, source URL, verification confidence |
| Disruption context | planned works, closures, service disruptions, spatial relevance, source confidence |
| Derived context | cohort label, regular/special flag, weather-disruption flag, event-overlap flag, context tags |
| Analytical references | baseline sample size, baseline median, percentiles, IQR, MAD, baseline ratio, signed deviation, robust z-score |
| Confidence | observation confidence, context confidence, baseline confidence, explanation confidence |

Raw source values should remain identifiable. Derived fields must not overwrite
observed values, and each derived field should have a documented method and
version.

## Context Separation

Each day or hourly observation should be assigned one or more explicit context
tags. At minimum, the system should distinguish:

- regular weekday;
- regular weekend;
- public holiday;
- school holiday or school break;
- daylight-saving transition;
- weather disruption period;
- manual event day or event window;
- planned works or other known disruption context;
- unknown anomaly candidate.

These tags are not merely display labels. They should determine:

1. whether an observation is eligible for a regular baseline;
2. which reference distribution is appropriate;
3. which comparison cohort should be used;
4. which explanations can be offered with evidence;
5. whether an unusual value is a known special condition or an unresolved
   anomaly.

Context tags may overlap. For example, an event can occur on a public holiday
during rain. The canonical panel should preserve all applicable tags and also
derive a documented primary cohort when a mutually exclusive grouping is
needed. Precedence rules for that primary cohort must be explicit rather than
implicit in code.

Calendar sources that provide start and end dates should be expanded into daily
or hourly context windows before cohort assignment. This is especially
important for school terms, school breaks, event windows, and daylight-saving
periods, which cannot be represented reliably by tagging only their start date.

Planned works and disruption datasets should pass date-range, status, and
spatial-relevance validation before they are used to exclude observations from
a baseline or explain anomaly candidates.

## Regular Baseline Cohort

The regular baseline cohort represents observations suitable for estimating
ordinary recurring activity. Eligibility should be calculated for every
sensor-hour record and recorded through fields such as
`is_regular_baseline_eligible` and `baseline_exclusion_reasons`.

The cohort should generally include:

- valid, non-missing observations;
- observations from sensors active at that timestamp;
- readings that pass source and sensor-quality checks;
- regular weekdays and regular weekends;
- observations with sufficient temporal and sensor metadata confidence.

The cohort should generally exclude, or place into separately modelled cohorts:

- public holidays;
- verified manual event windows;
- severe weather disruption periods;
- known planned works, closures, or disruptions when they are relevant to the
  sensor or precinct;
- ambiguous daylight-saving transition hours;
- invalid, low-confidence, or implausible sensor readings;
- periods affected by sensor installation, relocation, outage, or known
  calibration changes.

School holidays require empirical treatment rather than automatic exclusion in
all cases. They should be tagged and compared with regular periods; the project
can then decide whether they form a separate baseline cohort for sensors where
their effect is material.

Exclusion from a regular baseline must not mean deletion from the analytical
panel. Special observations remain available for comparison and explanation.

## Baseline Distribution Methodology

The primary baseline grouping should be:

- `sensor_id`;
- `weekday`;
- `hour`.

For each eligible group, the pipeline should calculate:

- `sample_size`;
- `median`;
- `p05`;
- `p25`;
- `p75`;
- `p95`;
- `p99`;
- interquartile range (`IQR = p75 - p25`);
- optionally, median absolute deviation (`MAD`);
- optionally, the centre and scale needed for a robust z-score.

Median and percentiles are preferred to a simple arithmetic mean because urban
counts can be skewed and affected by genuine high-activity periods. Means may
still be reported as descriptive statistics, but they should not be the sole
definition of normal activity.

All statistics must be computed from eligible observations, not selected
manually. Quantile conventions, minimum sample requirements, fallback behavior,
and baseline version should be documented. Groups with insufficient sample
size should be marked low-confidence or use an explicitly defined broader
fallback, such as sensor plus weekday/weekend class and hour. They should not
silently inherit an unrelated baseline.

One year provides a limited sample for this grouping: after exclusions, each
`sensor_id + weekday + hour` group may contain only around 40–50 eligible
observations. Every baseline must therefore retain `sample_size` and baseline
confidence metadata. Groups below a defined minimum sample threshold should use
an explicitly documented fallback rather than silently producing
high-confidence scores.

Counts from different sensors should not be directly compared as though they
share the same scale. Location, sensor geometry, local land use, and pedestrian
catchment can produce very different distributions. Baselines and normalised
scores must therefore remain sensor-specific.

## Normalisation Strategy

Normalisation should preserve raw values while making within-sensor patterns
comparable.

### Pedestrian Activity

Pedestrian activity should be positioned relative to the sensor's own
historical distribution for the appropriate time context. `activity_intensity`
can be expressed as a percentile rank or another bounded measure of distribution
position. Annual maximum scaling should not be the preferred research method
because one extreme observation can compress the rest of the series.

`baseline_deviation` should preserve direction. The analytical output must
distinguish below-normal from above-normal activity rather than reducing both to
an unsigned magnitude. Useful representations include:

- signed count difference;
- signed percentage or ratio deviation where the baseline is non-zero;
- percentile position;
- signed robust z-score.

`anomaly_strength` may be mapped to a 0–1 scale for visual encoding, but it
should derive from a documented robust distribution deviation. The signed
underlying statistic should remain available.

### Weather

Weather comfort should use interpretable comfort-band and penalty logic rather
than min-max scaling over the observed year. Comfortable temperature ranges,
rain intensity, and wind penalties should be documented separately so the
combined result can be explained.

Rain and wind disruption should use explicit threshold or continuous penalty
functions. Threshold choices should be sourced, sensitivity-tested, or clearly
labelled as project assumptions. A weather-disruption flag is context, not
proof that weather caused an activity change.

### Calendar and Events

Calendar and event variables should primarily remain categorical. An optional
`context_specialness_score` may summarise how far a context is from an ordinary
day for visual prioritisation, but it must not replace the underlying flags or
imply causal strength.

### Confidence

Confidence should represent reliability, completeness, and evidential support;
it must not represent activity intensity. Observation, baseline, context, and
explanation confidence should remain separate where possible. A composite
confidence score may be provided for interface use only when its components and
weighting are retained.

## Extreme Values and Anomaly Workflow

Extreme values should not be deleted automatically. An extreme observation may
be:

- a source or sensor error;
- a valid response to a known event or disruption;
- a city-wide or local behavioural change;
- an unexplained anomaly that warrants review.

The analytical process should first identify anomaly candidates and then
classify them using data quality and context. Candidate criteria may include:

- activity above `p95` or `p99`, or below `p05`;
- a high absolute robust z-score;
- a strong signed baseline ratio or percentage deviation;
- consecutive anomalous hours at one sensor;
- simultaneous anomalies at multiple nearby sensors;
- an unusual spatial pattern relative to neighbouring sensors;
- persistence beyond a minimum duration.

Candidate extraction should retain the triggering rules, baseline version,
signed direction, magnitude, duration, affected sensors, known contexts, and
confidence. Thresholds should be configurable and evaluated against the number
and quality of candidates they produce.

Low-confidence or invalid readings should be routed to a data-quality review
category rather than presented as true urban anomalies. Known event-related
extremes should remain analytically visible but can be classified as explained
special activity.

## Manual Event Explanation Workflow

Manual event annotation should follow anomaly detection rather than being used
to invent anomalies in advance:

1. The algorithm detects and ranks anomaly candidates.
2. Selected dates, hours, sensors, and precincts are reviewed.
3. Reviewers search authoritative event or disruption sources.
4. Verified information is added to `data/manual/events_manual.csv`.
5. The analytical panel is rebuilt with event-window and spatial-overlap tags.
6. Candidate classifications and explanation confidence are updated.
7. Dashboard explanation cards are generated from the reviewed evidence.

Manual event records should include, at minimum:

- event identity and type;
- date and start/end times;
- location and relevant precinct or sensors;
- `source_url`;
- `expected_effect`;
- confidence;
- review notes.

Where possible, records should also capture source publisher, retrieval date,
spatial relevance, and verification status. An event match indicates plausible
context, not demonstrated causality.

UI explanation cards must visibly distinguish:

- verified explanations supported by a cited source;
- plausible but unverified contextual matches;
- algorithmic hypotheses;
- unexplained anomaly candidates.

## Edge-AI-Ready Framing

The current public pedestrian sensors are proxy urban signals. Melbourne Urban
Pulse is not currently a deployed edge-AI system and should not claim local
model inference.

The framework can nevertheless be edge-AI-ready by accepting future
edge-generated observations through the same canonical panel. An edge node
might provide:

- local pedestrian or crowd density;
- vehicle flow;
- cycling flow;
- crowd-state estimates;
- model confidence;
- `model_version`;
- `signal_type`;
- aggregation interval and device metadata.

The central analytical layer would continue to handle baseline comparison,
context interpretation, provenance, confidence, anomaly classification, and
visual explanation. Statistical baselines must remain explicit and auditable.
AI can assist with candidate classification, cross-source matching, and
explanation drafting, but it should not obscure source evidence or replace
documented statistical references.

## Intended Analytical Outputs

Future processing should produce distinct, versioned outputs rather than one
monolithic dashboard artifact:

| Output | Purpose |
| --- | --- |
| `analytical_hourly_panel` | Canonical sensor-hour observations, context, quality, and derived references |
| `regular_baselines` | Sensor/weekday/hour baseline distributions and sample diagnostics |
| `sensor_distributions` | Broader per-sensor distribution and continuity summaries |
| `calendar_comparisons` | Regular, weekend, holiday, school-break, and transition comparisons |
| `weather_effect_summaries` | Activity deviations grouped by documented weather conditions |
| `anomaly_candidates` | Ranked, rule-traceable high/low anomaly windows |
| `event_explanation_candidates` | Candidate event matches awaiting or recording review |
| `dashboard_summary` | Small aggregate metrics and research-facing summaries |
| `compact_frontend_windows` | Size-controlled time windows for interactive delivery |
| `spatial_pulse_frames` | Sensor-based spatial frames with confidence and provenance |

Analytical outputs should include schema and methodology versions, study
period, creation time, source provenance, and quality notes.

## Relationship to Visualisations

The analytical layer should support:

- weekday-hour heatmaps;
- sensor distribution charts;
- regular-day versus public-holiday comparisons;
- weather versus activity-deviation scatterplots;
- anomaly timelines;
- event-linked explanation cards;
- the 2.5D Urban Pulse Field.

These visualisations should be derived from the analytical outputs and their
documented semantics. They should not define independent metrics that exist
only in frontend code. For example, heatmaps should use baseline-relative
sensor values, anomaly timelines should reference retained candidate records,
and explanation cards should reflect verification status.

The 2.5D field should distinguish observed location-specific signals from
interpolated or inferred surfaces. Height, colour, ripple, and opacity should
each map to a documented field, with missingness and confidence visible rather
than hidden.

## Limitations

- Public pedestrian counts are a proxy for urban activity, not a complete
  measure of population movement or infrastructure demand.
- Baseline quality depends on sensor continuity, metadata accuracy, timestamp
  consistency, and sufficient eligible observations.
- Event explanations require manual verification and generally establish
  plausible association rather than causality.
- Available weather context is city-level and may not represent street-level
  microclimates around each sensor.
- The current project is not a deployed edge-AI system.
- Sensor installation, relocation, replacement, or calibration changes can
  invalidate comparisons unless they are represented in metadata.
- Model and baseline drift will require monitoring, versioning, and periodic
  recomputation.
- Upstream schema and source changes require validation and compatibility
  mechanisms.
- Nearby sensors are not necessarily independent, and spatial relationships
  require careful interpretation.
- One year may be sufficient for an MVP distribution but is limited for
  estimating longer-term seasonality and year-to-year variation.

## Implementation Implications

Future code should likely evolve from the current single MVP builder into
modular, independently testable stages. Possible responsibilities include:

- `build_analytical_panel.py`;
- `build_regular_baselines.py`;
- `extract_anomaly_candidates.py`;
- `build_dashboard_summaries.py`;
- `build_frontend_compact_dataset.py`.

These names describe likely separation of concerns, not an implementation
commitment. No such scripts are implemented by this document. The eventual
pipeline should keep source ingestion, context classification, baseline
estimation, candidate extraction, manual review inputs, and frontend export
logically distinct.

## Current Status

### Implemented

- [x] Raw data collection
- [x] Raw data profiling
- [x] First real-data MVP pipeline
- [x] Compact frontend dataset
- [x] Frontend vertical slice

### Provisional

- `baseline_count` — provisional
- `pulse_score` — provisional
- `anomaly_score` — provisional
- `confidence_score` — provisional
- Explanation cards — provisional
- Infrastructure pressure proxy — provisional

### Not Yet Implemented

- [ ] Context-aware regular baseline cohort
- [ ] Percentile/MAD/robust-z anomaly workflow
- [ ] Anomaly candidate review table
- [ ] Manual event verification workflow
- [ ] Full analytical summary outputs
- [ ] Edge signal ingestion
