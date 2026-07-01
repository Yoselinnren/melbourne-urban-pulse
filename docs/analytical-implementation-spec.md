# Analytical Implementation Specification

## 1. Purpose

This document translates the research methodology in
`docs/analytical-framework.md` into requirements for a future analytical
pipeline. It defines conceptual modules, data contracts, stage dependencies,
expected outputs, and implementation priorities so that subsequent work can be
developed and reviewed against an explicit specification.

This is not an implementation. The module names below are proposed boundaries,
not scripts that currently exist. Algorithms, thresholds, storage formats, and
operational details remain subject to implementation review and empirical
validation.

## 2. Current Pipeline Boundary

`scripts/build_mvp_dashboard_data.py` is the current delivery
proof-of-concept. It reads selected pedestrian, sensor, weather, and calendar
sources; creates a full-year hourly dataset; calculates provisional metrics;
and writes frontend-readable JSON. It proves the end-to-end path from local raw
sources to the current compact frontend vertical slice.

The builder is primarily a frontend data builder, not the final research
pipeline. Its baseline, anomaly, pulse, weather, and confidence logic remains
provisional. Future analytical processing should not simply extend that
scoring logic. It should first establish a canonical analytical panel,
context classification, regular-baseline eligibility, distribution outputs,
and traceable anomaly workflows.

The current builder may remain available as a delivery reference while the
analytical stages are developed separately. Migration to new frontend exports
should occur only after the new analytical contracts are validated.

## 3. Proposed Modular Pipeline

The future pipeline should separate source integration, context
classification, baseline estimation, scoring, anomaly extraction, analytical
summaries, and delivery exports. Each stage should consume documented outputs
from earlier stages rather than reimplementing their logic.

### 3.1 `build_analytical_panel.py`

**Purpose**

Construct the canonical long-form sensor-hour panel while preserving source
values, provenance, and missingness.

**Inputs**

- hourly pedestrian observations;
- pedestrian sensor metadata;
- hourly weather observations;
- expanded calendar context;
- manual event annotations;
- validated planned-works or disruption context, when available;
- source-profile and schema metadata.

**Outputs**

- `analytical_hourly_panel`;
- source-coverage and join-quality diagnostics;
- rejected or unresolved source records, where applicable.

**Key fields produced**

- time and sensor identity fields;
- observed pedestrian values;
- sensor metadata;
- explicit missingness and source-quality fields;
- weather, calendar, event, and disruption fields;
- source identifiers and provenance.

**Dependencies**

This is the first analytical stage. It depends on validated source schemas and
calendar/event interval expansion, but not on baselines or anomaly scores.

### 3.2 `classify_contexts.py`

**Purpose**

Assign explicit, potentially overlapping context tags and determine whether
each observation is eligible for a regular baseline.

**Inputs**

- `analytical_hourly_panel`;
- documented context precedence rules;
- weather-disruption rules;
- sensor-validity and confidence rules.

**Outputs**

- context-enriched analytical panel;
- context classification summary;
- baseline eligibility and exclusion diagnostics.

**Key fields produced**

- individual context flags;
- `context_tags`;
- optional `primary_context`;
- `is_regular_baseline_eligible`;
- `baseline_exclusion_reasons`;
- context and eligibility confidence fields.

**Dependencies**

Requires the canonical panel and expanded context intervals. It must run before
regular baselines are calculated.

### 3.3 `build_regular_baselines.py`

**Purpose**

Calculate sensor-specific empirical distributions from observations that pass
regular-baseline eligibility rules.

**Inputs**

- context-enriched analytical panel;
- baseline grouping specification;
- minimum-sample and fallback policy;
- quantile and robust-statistic conventions.

**Outputs**

- `regular_baselines`;
- baseline coverage diagnostics;
- fallback-use report.

**Key fields produced**

- baseline group keys;
- sample size;
- median and percentile statistics;
- IQR and optional MAD;
- baseline confidence;
- baseline method, version, and fallback metadata.

**Dependencies**

Requires completed context classification and baseline eligibility. It must not
derive its population directly from unclassified annual observations.

### 3.4 `score_observations.py`

**Purpose**

Join each observation to the appropriate baseline and calculate transparent,
sensor-relative activity and deviation measures.

**Inputs**

- context-enriched analytical panel;
- `regular_baselines`;
- documented normalisation and confidence rules.

**Outputs**

- scored analytical panel;
- unmatched-baseline and low-confidence scoring diagnostics.

**Key fields produced**

- baseline reference and baseline version;
- activity percentile;
- baseline ratio;
- signed deviation;
- robust z-score, when supported;
- anomaly strength and direction;
- separate observation, baseline, context, and composite confidence fields.

**Dependencies**

Requires validated regular-baseline outputs. It should not independently
recalculate baseline distributions.

### 3.5 `extract_anomaly_candidates.py`

**Purpose**

Identify, group, and rank unusual observation windows while preserving the
rules and evidence that triggered each candidate.

**Inputs**

- scored analytical panel;
- configurable candidate rules;
- sensor-neighbour or precinct relationships, if spatial rules are enabled;
- known context and data-quality fields.

**Outputs**

- `anomaly_candidates`;
- candidate-rule diagnostics;
- data-quality review candidates separated from urban-activity anomalies.

**Key fields produced**

- anomaly identity and time window;
- direction and severity;
- triggering rules and supporting statistics;
- affected and related sensors;
- known contexts;
- confidence and review status.

**Dependencies**

Requires scored observations. Manual event verification is not required for
initial detection; known context may inform classification without suppressing
the original candidate evidence.

### 3.6 `build_dashboard_summaries.py`

**Purpose**

Create compact research-facing aggregate outputs from validated analytical
datasets.

**Inputs**

- scored analytical panel;
- regular baselines;
- anomaly candidates;
- reviewed event links;
- sensor and source metadata.

**Outputs**

- annual summary;
- regular-baseline summaries;
- sensor-distribution summaries;
- calendar comparisons;
- weather-effect summaries;
- anomaly timeline;
- event-explanation candidates;
- metadata, provenance, and quality summaries.

**Key fields produced**

- aggregate values required by dashboard visualisations;
- display-ready comparison groups;
- method and confidence metadata;
- explicit verified, speculative, and unexplained statuses.

**Dependencies**

Requires stable analytical outputs. Summaries must reference their underlying
method and dataset versions.

### 3.7 `build_frontend_compact_dataset.py`

**Purpose**

Package selected analytical summaries, time windows, and spatial frames into
size-controlled frontend delivery artifacts.

**Inputs**

- dashboard summaries;
- scored analytical panel for approved display windows;
- reviewed explanations;
- frontend data-contract configuration.

**Outputs**

- compact frontend windows;
- spatial pulse frames;
- a frontend-readable dashboard dataset;
- delivery metadata and full-dataset summary references.

**Key fields produced**

- selected observations and derived scores;
- display labels and legends;
- source and method references;
- confidence and missingness fields;
- compact-window metadata.

**Dependencies**

This is the final delivery stage. It must consume analytical outputs rather
than reproduce research calculations for convenience.

## 4. Canonical Analytical Panel Schema

Each row should represent one sensor at one local hourly timestamp. Field names
may be refined during implementation, but their meanings and origins must
remain explicit.

| Field group | Intended fields |
| --- | --- |
| Record identity | `timestamp`, `date`, `hour`, `weekday`, `timezone`, UTC offset |
| Sensor identity | `sensor_id`, sensor name, status, location type, precinct, latitude, longitude |
| Sensor lifecycle | active-at-timestamp flag, installation date, relocation/version metadata where available |
| Observation | `observed_count`, directional counts, source record ID |
| Missingness | `is_missing`, `missing_reason`, source-hour-present flag |
| Observation quality | validity flag, source quality, sensor quality, observation confidence |
| Weather | temperature, apparent temperature, humidity, precipitation, rain, wind speed, weather code |
| Calendar | weekend, public-holiday, school-term, school-holiday, season, daylight-saving transition |
| Manual events | event ID, event type, event start/end, location, expected effect, source URL, verification status and confidence |
| Disruptions | planned-work ID, disruption type, status, date overlap, spatial relevance, source confidence |
| Context classification | individual flags, `context_tags`, optional `primary_context` |
| Baseline eligibility | `is_regular_baseline_eligible`, `baseline_exclusion_reasons` |
| Confidence | observation, sensor, weather, calendar, context, event, baseline, and composite confidence |
| Provenance | source IDs, schema version, processing version, creation timestamp |

Observed values must be retained alongside derived fields. Missing observations
must remain `null` rather than becoming zero. Estimated or imputed values, if
introduced later, require separate fields and method metadata.

Calendar, event, school-period, planned-work, and daylight-saving sources that
contain start and end times must be expanded into daily or hourly intervals
before they are joined to this panel.

## 5. Context Classification Rules

The classifier should support these planned tags:

- `regular_weekday`;
- `regular_weekend`;
- `public_holiday`;
- `school_holiday`;
- `daylight_saving_transition`;
- `weather_disruption`;
- `manual_event_window`;
- `planned_work_context`;
- `unknown_anomaly_candidate`.

Context tags may overlap. A record can, for example, be both a public holiday
and a weather-disruption period. The pipeline should retain all tags rather
than force an early mutually exclusive classification.

If a `primary_context` is required for summaries, its precedence order must be
documented and versioned. It must not replace the complete tag list.
`unknown_anomaly_candidate` should be assigned after anomaly extraction, not
used as an initial calendar classification.

Calendar intervals must be expanded before tagging. A school break, event
window, planned-work period, or daylight-saving transition must affect every
applicable date or hour, not only a source start date.

Planned-work context must pass date-range, status, source-quality, and spatial
relevance validation before it can affect baseline eligibility or anomaly
explanations.

## 6. Regular Baseline Eligibility

The context-classified panel should include:

- `is_regular_baseline_eligible`: a Boolean decision;
- `baseline_exclusion_reasons`: a list of stable reason codes.

Observations should generally be eligible when they:

- are valid and non-missing;
- come from a sensor active at that timestamp;
- pass source and sensor-quality checks;
- occur on a regular weekday or regular weekend;
- have sufficient timestamp and context confidence.

Observations should generally be excluded or separately modelled when they:

- occur on a public holiday;
- overlap a verified manual event;
- occur during severe weather disruption;
- overlap a validated and spatially relevant planned work or disruption;
- fall in an ambiguous daylight-saving transition;
- are invalid or low-confidence;
- fall within a known sensor outage, installation, relocation, or calibration
  transition.

School holidays should always be tagged. Whether they are excluded or assigned
to a separate cohort should be determined empirically and documented.

Exclusion reasons should use stable codes such as
`missing_observation`, `inactive_sensor`, or `public_holiday`, while retaining
human-readable descriptions in schema documentation. Exclusion removes a
record only from a baseline population, not from the analytical panel.

## 7. Baseline Distribution Outputs

The primary grouping should be:

- `sensor_id`;
- `weekday`;
- `hour`.

Each row in `regular_baselines` should include:

- `sensor_id`;
- `weekday`;
- `hour`;
- `sample_size`;
- `median`;
- `p05`;
- `p25`;
- `p75`;
- `p95`;
- `p99`;
- `iqr`;
- optional `mad`;
- `baseline_confidence`;
- baseline eligibility-policy version;
- quantile-method version;
- study-period start and end;
- fallback level and fallback reason, if used.

One year may leave only around 40–50 observations in a
`sensor_id + weekday + hour` group before exclusions and fewer afterward.
Therefore, `sample_size` and baseline confidence are required analytical
fields, not optional diagnostics.

Minimum sample thresholds should be selected during implementation review and
remain configurable. This specification does not set final thresholds.
Insufficient groups should use an explicitly documented broader fallback, such
as a weekday/weekend-class hourly distribution, or remain unscored. The
pipeline must not silently report high-confidence statistics from inadequate
samples.

## 8. Normalisation and Scoring Outputs

The scored panel should include:

- `activity_percentile`;
- `baseline_ratio`;
- `signed_deviation`;
- `robust_z_score`, when the baseline supports it;
- `anomaly_strength`;
- `anomaly_direction`;
- `confidence_score`.

`activity_percentile` should locate the observation within the relevant
sensor-specific baseline distribution.

`baseline_ratio` and `signed_deviation` must preserve direction. They should
distinguish below-normal from above-normal activity and retain their raw
analytical value.

`robust_z_score` should also remain signed. Its centre and scale must come from
the baseline output, with explicit behavior when MAD or another robust scale
is zero or unavailable.

`anomaly_strength` may be a bounded 0–1 encoding for ranking or UI display. It
must be derived from a documented deviation measure and must not replace the
signed source statistic.

`anomaly_direction` should use explicit values such as `above`, `below`, or
`none`.

`confidence_score` should measure reliability, not activity. Where practical,
the panel should retain separate component confidences for the observation,
context, baseline, and explanation. Any combined score must document its
inputs, weighting, and version.

Raw observations, baseline statistics, and normalised scores must coexist so
that results remain auditable.

## 9. Anomaly Candidate Extraction

The future `anomaly_candidates` output should include:

- `anomaly_id`;
- `sensor_id` or a primary sensor identifier;
- `start_time`;
- `end_time`;
- `direction`;
- `triggering_rules`;
- `severity`;
- `affected_sensors`;
- `known_contexts`;
- `confidence`;
- `review_status`.

It should also retain supporting values such as peak percentile, robust
z-score, baseline ratio, duration, baseline version, and data-quality flags.

Candidate rules may consider:

- upper or lower baseline percentiles;
- absolute robust z-score;
- signed baseline ratio;
- consecutive anomalous hours;
- simultaneous anomalies across multiple or nearby sensors;
- persistence and spatial coherence.

All thresholds are configurable policy, not fixed research facts in this
specification. Each candidate must record which rules and configured versions
triggered it.

Low-confidence or invalid readings should be separated into a data-quality
review path. Known event or weather context may classify a candidate as
potentially explained, but should not erase the underlying observation or
trigger evidence.

Suggested `review_status` values include `unreviewed`, `in_review`,
`verified_context`, `speculative_context`, `data_quality_issue`, and
`unexplained`. The final controlled vocabulary should be fixed with the output
schema.

## 10. Manual Event Review Integration

Anomaly detection should produce candidates before manual event verification.
Reviewers can then investigate selected candidate windows and add verified
context to `data/manual/events_manual.csv`.

Required manual event fields should include:

- `event_id`;
- `date`;
- `start_time`;
- `end_time`;
- `event_name`;
- `event_type`;
- `location`;
- `precinct`;
- `source_url`;
- `expected_effect`;
- `confidence`;
- `notes`.

Future schema revisions may add source publisher, retrieval date, review
status, reviewer, relevant sensor IDs, and spatial confidence. Any extension
should preserve compatibility or include a schema migration.

After annotation:

1. event intervals should be expanded and joined to relevant sensor-hours;
2. temporal and spatial relevance should be recorded;
3. anomaly candidates should retain their original trigger evidence;
4. candidate review status and explanation confidence should be updated;
5. dashboard explanations should cite verified sources where available.

Verified event overlap provides evidence for a plausible explanation, not
proof of causality. Outputs must distinguish verified context, speculative
matches, and unexplained candidates.

## 11. Dashboard Output Strategy

Future frontend-facing analytical outputs should include:

- annual summary;
- regular-baseline summaries;
- sensor-distribution summaries;
- calendar comparisons;
- weather-effect summaries;
- anomaly timeline;
- selected compact windows;
- spatial pulse frames.

These products should be generated from versioned analytical outputs. The
frontend should consume prepared summaries and display fields; it should not
recalculate research metrics in React.

The annual summary should report coverage, missingness, cohort counts,
baseline-quality information, and high-level activity patterns.

Regular-baseline and sensor-distribution summaries should support
weekday-hour heatmaps and distribution views without shipping the full
analytical panel.

Calendar and weather summaries should preserve comparison cohorts and sample
sizes so that visual differences are not shown without analytical context.

The anomaly timeline should expose candidate direction, severity, known
context, confidence, and review status.

Compact windows should include the observations, baseline references, scores,
and explanations needed for selected stories. Spatial frames should retain
sensor-level values, missingness, and confidence and should identify any
interpolation explicitly.

Frontend contracts should remain size-controlled and should carry provenance,
schema versions, method versions, and quality notes.

## 12. Edge-AI-Ready Signal Extension

Future edge-generated signals could enter a general observation contract with:

- `signal_type`;
- `source_type`;
- `model_version`;
- `observed_value`;
- `unit`;
- `confidence`;
- `location_id`;
- `timestamp`.

Additional provenance may include device ID, aggregation window, model
deployment version, calibration state, and privacy-preserving processing
metadata.

The canonical panel should allow such signals to share time, location,
context, baseline, scoring, and confidence concepts without assuming that all
signals are pedestrian counts. Signal-specific units and distribution methods
must remain explicit.

The current project uses public pedestrian sensors as proxy urban signals. It
does not ingest real edge-AI output or perform edge inference. Edge readiness
is a schema and architectural objective, not a claim about current capability.

## 13. Implementation Priority

### Phase 1: Analytical Foundation

- build the canonical analytical panel;
- classify contexts and expand interval-based context;
- calculate regular-baseline distributions;
- validate missingness, joins, eligibility, sample sizes, and fallback use.

### Phase 2: Scoring and Candidate Detection

- score observations against versioned regular baselines;
- implement signed deviations and robust distribution measures;
- extract traceable anomaly candidates;
- separate data-quality candidates from activity anomalies.

### Phase 3: Review and Analytical Summaries

- integrate the manual event review workflow;
- link verified context without claiming causality;
- build annual, sensor, calendar, weather, and anomaly summaries;
- define stable analytical output schemas.

### Phase 4: Delivery and Extension

- upgrade frontend visualisations to consume analytical summaries;
- produce compact windows and spatial pulse frames;
- define and validate the generic edge-signal abstraction;
- retain backward compatibility or document frontend contract migrations.

Each phase should be reviewed before the next begins. Phase 1 is the necessary
foundation; delivery pressure should not bypass baseline-population and
sample-quality validation.

## 14. Non-Goals for the Next Coding Step

The next coding step should not:

- implement machine learning;
- implement WebGL;
- rewrite frontend visuals;
- ingest real edge-AI signals;
- add heavy dependencies;
- claim causal explanations.

It should focus on transparent data integration, context classification,
regular-baseline eligibility, and empirical distribution outputs. More complex
models or visual systems should be considered only after those foundations are
validated.
