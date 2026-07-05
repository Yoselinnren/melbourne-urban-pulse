# Phase 1G — Automatic Context Enrichment

## Purpose and boundary

Phase 1G attaches programmatically available weather, calendar, sensor,
baseline, pulse, and optional manual-event-window context to Phase 1E candidate
episodes and Phase 1F pulse groups.

**Phase 1G expresses co-occurrence only.** Phase 1G does not make causal claims.
Phase 1G does not verify or explain events. Phase 1G does not rank anomalies or
pulses. Phase 1G does not produce top-N outputs. Context fields support statements
such as “this pulse overlaps rainfall”, never “rain caused this pulse”.

Final anomaly confirmation, review-priority scoring, spatial clustering,
transport-disruption analysis, planned-works activation, and ML or edge-AI
training are non-goals.

## Inputs

Each sensor mode uses its existing processed output directory:

- `candidate_episodes.csv`
- `episode_pulse_context.csv`
- `pulse_groups.csv`
- `deviation_interpretation_panel.csv`
- `data/metadata/analysis_sensor_selection.csv`
- `data/manual/events_manual.csv`, only when the file exists

The deviation interpretation panel is the primary sensor-hour context source.
Phase 1G fails loudly when required processed weather, calendar, DST, baseline,
or sensor fields are missing; it does not invent them or reread raw context.

## Outputs and row-count contract

Each mode directory receives:

- `context_enriched_candidate_episodes.csv` and `.json`
- `context_enriched_pulse_groups.csv` and `.json`
- `phase1g_context_diagnostics.json`

Enrichment is one-to-one. No record is dropped, duplicated, filtered, merged,
or ranked. MVP_3 must retain 1,215 episodes and 69 pulses.
REPRESENTATIVE_12 must retain 4,647 episodes and 425 pulses.

## Time and aggregation semantics

Nominal `Australia/Melbourne` local hourly keys are canonical for analytical
joins. Offset-bearing timestamps remain provenance/interchange values. Existing
start and end timestamps are inclusive; internally each interval is represented
as `[start, end + 1 hour)` and expanded to inclusive hourly keys. Exact-hour
joins supply hourly weather and sensor context. Calendar fields are aggregated
as date/hour overlap. Existing DST transition flags and labels are retained.
Phase 1G follows the established 8,760 nominal-local-hour convention and does
not remodel duplicated or missing DST wall-clock hours.

Episode weather is aggregated across the single sensor’s inclusive hours. Pulse
weather is city-level context and each local hour is counted exactly once.
Weather values are never multiplied by active sensors or member episodes.
Totals are used for precipitation and rain; means/minima/maxima and counts are
reported where appropriate. Calendar booleans indicate any overlap, while label
sets serialize the distinct overlapping labels.

Calendar label fields preserve category semantics. `public_holiday_labels`
contains only raw Victoria calendar records classified with
`dateType == PUBLIC_HOLIDAY`. `school_holiday_labels` comes from the processed
school-related labels, and `dst_transition_labels` comes from the processed
daylight-saving labels. Broader `MULTI_FAITH` and other important-date labels
may remain in `calendar_context_labels`. This prevents religious-date records
such as Hanukkah or Christmas from being misclassified as public holidays when
they share a date with an official public-holiday record.

The provisional weather disruption rule is true for an hour when `rain > 0` or
`wind_speed_10m >= 30`. This is an engineering co-occurrence flag, not causal
interpretation and not a verified disruption.

## Sensor and pulse metadata

Candidate episodes attach metadata by canonical `sensor_id`: coordinates,
location type/label, selection tier, and inclusion reason. Pulse groups parse
their member sensor IDs and attach deterministic parallel member lists.
Phase 1G assigns no single pulse coordinate, calculates no centroid, and
performs no distance clustering. Episode pulse context is carried forward from
Phase 1F; pulse member baseline and episode properties are aggregated without
changing pulse structure.

## Manual events and deferred sources

Manual events are only overlap windows if records exist. Temporal overlap does
not establish spatial relevance, verification, explanation, or causation.
Since the current manual event file has zero records, no verified event
explanation is possible; all overlap fields are false/zero/blank and diagnostics
record the empty source.

Planned works are not activated because date/status/spatial validation is not
yet safe. Transport disruptions and the event PDF are not used for automatic
interpretation. Verified event explanation is deferred to Phase 1H, where
manual evidence can be checked explicitly.

## Limitations

Weather is city-level rather than sensor-specific. Context completeness reports
availability, not correctness or explanatory power. Co-occurrence labels must
not be read as confirmed anomalies, real-world causes, or verified event
attribution. Frontend integration and dashboard JSON changes are outside
Phase 1G.
