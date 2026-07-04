# Phase 1E: Candidate Episode Construction

## Purpose

Phase 1E converts Phase 1D row-level `review_ready` signals into
single-sensor temporal candidate episodes. An episode is a contiguous run of
strong or extreme deviations at one sensor in one direction.

`candidate_episodes.csv` contains candidate episode units, not confirmed
anomalies. Phase 1E performs structural temporal grouping only. It does not
rank, confirm, or explain episodes.

## Inputs and Outputs

Input in each mode-aware processed directory:

- `deviation_interpretation_panel.csv`

Outputs in the same directory:

- `candidate_episodes.csv`;
- `candidate_episodes.json`;
- `phase1e_diagnostics.json`.

Default directories remain:

- `MVP_3`: `data/processed/`;
- `REPRESENTATIVE_12`: `data/processed/representative_12/`;
- `HIGH_COVERAGE_ALL`: `data/processed/high_coverage_all/`.

Phase 1E validation currently runs only `MVP_3` and `REPRESENTATIVE_12`.

## Row Filtering

Only rows with:

```text
candidate_readiness == review_ready
```

are eligible.

The stage excludes `needs_context`, `not_candidate`, `data_quality_review`, and
`low_confidence_excluded` rows. These excluded rows are not used as bridges
between eligible hours.

## Grouping Rule

Rows belong to the same episode only when they:

1. have the same `sensor_id`;
2. have the same `deviation_direction`;
3. are both `review_ready`;
4. have local timestamp keys exactly one hour apart.

The project-local `local_timestamp_key` is used for temporal adjacency,
matching the nominal local-hour convention established in Phase 1A.

### No-Gap Rule

Phase 1E does not merge across a one-hour gap. Any absent, non-review-ready, or
different-direction hour ends the episode. A later qualifying row starts a new
episode.

### Direction Separation

Positive and negative deviations are grouped separately. A positive pulse and
a negative suppression cannot form one episode, even when they occur at the
same sensor in adjacent hours.

### Single-Hour Episodes

Single-hour episodes are preserved. They remain useful candidate units for
later review and prevent the temporal grouping stage from silently discarding
short extreme signals.

## Episode Identity and Fields

Episode IDs are deterministic:

```text
E1E_{sensor_mode}_{sensor_id}_{episode_direction}_{start_local_timestamp}
```

Repeated runs over unchanged inputs produce the same IDs.

Episode outputs include:

- sensor identity and label;
- direction, signal family, and dominant subtype;
- start/end timestamps and local keys;
- duration and source-row count;
- peak, mean, minimum, and maximum signed score summaries;
- observed-count minimum, maximum, mean, and total;
- strength band and duration class;
- baseline confidence and warning summary;
- `episode_readiness = candidate_episode`.

Dominant categorical values use highest frequency, with lexical ordering as a
deterministic tie-break.

## Episode Strength Bands

Because `review_ready` rows are strong or extreme:

- `strong`: every source row is strong;
- `extreme`: every source row is extreme;
- `mixed_strong_extreme`: both bands occur in the episode.

The mixed label is used whenever both strong and extreme rows are present.

## Episode Duration Classes

| Duration | Class |
| --- | --- |
| 1 hour | `single_hour` |
| 2–3 hours | `short_2_3h` |
| 4–6 hours | `medium_4_6h` |
| 7+ hours | `long_7h_plus` |

For a valid strict-hourly episode, `duration_hours` equals
`source_row_count`.

## Diagnostics and Safety

Diagnostics report input and review-ready row counts, episode counts,
directions, strength bands, duration classes, per-sensor counts, single- and
multi-hour counts, maximum duration, and score summaries.

Sanity checks ensure:

- only `review_ready` rows are used;
- all source rows are accounted for exactly once;
- every episode has one sensor and one direction;
- every episode is strictly hourly-contiguous;
- single-hour episodes remain one hour long;
- no `needs_context` or data-quality rows are used;
- no final anomaly-candidate file is created.

## Limitations and Non-Goals

- Candidate episodes are not confirmed anomalies.
- `peak_abs_score` is based on an unbounded robust-z-style score, so very large
  values can occur under low-baseline or small-MAD conditions. Phase 1E does not
  rank or confirm anomalies using raw `peak_abs_score` alone; later review or
  ranking phases should combine strength band, duration, observed volume,
  baseline confidence, and possible multi-sensor context.
- Phase 1E does not explain real-world causes.
- Phase 1E does not use external event data.
- Phase 1E does not produce top-N rankings.
- Phase 1E does not merge gaps.
- Phase 1E does not do cross-sensor or network-wide grouping.
- Cross-sensor grouping and network pulse detection are deferred to a later
  phase.
- Phase 1E does not modify frontend or public dashboard data.
- Phase 1E does not implement machine learning or edge-AI model training.
