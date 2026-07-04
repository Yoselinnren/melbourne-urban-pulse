# Phase 1F: Cross-Sensor Pulse Context

## Purpose

Phase 1F adds same-direction, cross-sensor temporal context to the
single-sensor candidate episodes produced by Phase 1E. It determines whether
an episode is temporally isolated, paired with one other sensor, or overlaps a
localized, broad, or network-wide pulse.

This stage is not final anomaly extraction. `pulse_groups.csv` contains
cross-sensor pulse-context candidates, not confirmed anomalies.
`episode_pulse_context.csv` annotates every Phase 1E episode with its
cross-sensor context.

## Inputs and Outputs

The input in each mode-aware processed directory is:

- `candidate_episodes.csv`.

Outputs in the same directory are:

- `pulse_groups.csv`;
- `pulse_groups.json`;
- `episode_pulse_context.csv`;
- `episode_pulse_context.json`;
- `phase1f_diagnostics.json`.

Default directories remain:

- `MVP_3`: `data/processed/`;
- `REPRESENTATIVE_12`: `data/processed/representative_12/`;
- `HIGH_COVERAGE_ALL`: `data/processed/high_coverage_all/`.

Phase 1F validation currently runs only `MVP_3` and `REPRESENTATIVE_12`.

## Why Phase 1F Uses Phase 1E Episodes

Phase 1E has already filtered row-level interpretation results to
`review_ready` observations and grouped strictly contiguous, same-sensor,
same-direction hours. Phase 1F therefore operates on stable temporal episode
units rather than repeating row-level scoring or interpretation.

All input episodes must have `episode_readiness = candidate_episode`. Phase 1F
does not alter those input records.

## Episode-Hour Expansion

Each episode is expanded into one active row for every local hour from
`start_local_timestamp_key` through `end_local_timestamp_key`, inclusive.
Expanded rows retain:

- episode and sensor identity;
- sensor mode;
- deviation direction;
- active local hour;
- episode score, strength, and observed-volume summaries.

Phase 1F groups pulse context using nominal Melbourne local hourly keys derived
from the episode timestamps. Timestamp fields preserve source traceability, but
local hourly order is the analytical grouping basis, matching the convention
used by the analytical panel.

## Temporal Co-Occurrence

Expanded rows are grouped by:

```text
sensor_mode + episode_direction + active local hour
```

Each hour records its distinct active sensor and episode counts. Positive and
negative directions remain separate because simultaneous elevation and
suppression represent different deviation structures and must not form one
pulse group.

The pulse-context classes are:

| Active sensors | Context |
| ---: | --- |
| 1 | `isolated_episode` |
| 2 | `paired_context` |
| 3–4 | `localized_pulse` |
| 5–7 | `broad_pulse` |
| 8+ | `network_wide_pulse` |

The default pulse-group threshold is at least three active sensors. Isolated
and paired hours contribute to episode annotations but do not create
`pulse_groups` in Phase 1F.

## Pulse Group Construction

Consecutive pulse-active hours form one group only when they share:

1. the same sensor mode;
2. the same deviation direction;
3. at least three active sensors in every hour;
4. strict one-hour adjacency.

There is no gap merge. Sensor membership may vary between consecutive hours;
the pulse group summarizes the union of participating sensors and episodes.
Its `pulse_scope` is determined by the maximum active sensor count reached:

- 3–4: `localized_pulse`;
- 5–7: `broad_pulse`;
- 8+: `network_wide_pulse`.

This classification is peak-based: a group can be labelled
`network_wide_pulse` when `max_active_sensor_count` reaches 8 or more even if
its `min_active_sensor_count` is lower. The minimum, mean, and maximum active
sensor counts should be interpreted together to understand participation
changes across the pulse duration.

`total_observed_count` sums the full observed-count totals of the unique member
episodes once each. It is not restricted to only the hours where those episodes
overlap the pulse group, so it should be interpreted as member-episode volume
rather than pulse-overlap-hour volume.

Pulse group IDs are deterministic:

```text
P1F_{sensor_mode}_{direction}_{start_local_timestamp}
```

Every group has `pulse_readiness = pulse_context_candidate`; this is not a
confirmation label.

## Episode Context Assignment

Every Phase 1E episode receives one context row.

If an episode overlaps one or more pulse groups, assignment uses:

1. most overlapping hours;
2. highest maximum active sensor count;
3. highest group maximum `peak_abs_score`;
4. earliest pulse-group start;
5. pulse-group ID as a final deterministic tie-break.

If no pulse group overlaps, an episode is `paired_context` when its peak
same-direction overlap contains exactly two sensors, otherwise it is
`isolated_episode`.

The output also records the maximum co-occurring sensor and episode counts,
the sensor and episode IDs at the deterministic peak hour, membership flags,
and the assigned pulse-group ID when applicable.

## Diagnostics

Diagnostics include episode and expanded-hour counts, pulse-active hours,
groups by direction and scope, episode context counts, maximum participation,
duration summaries, and threshold sensitivity at 2, 3, 4, 6, and 8 active
sensors.

Sanity checks verify:

- every input episode receives exactly one context row;
- pulse groups meet the three-sensor threshold;
- directions and modes are never mixed;
- isolated and paired episodes have no pulse-group ID;
- paired contexts are not emitted as pulse groups;
- pulse members have matching directions;
- no final anomaly or top-N ranking output is created.

## Limitations and Non-Goals

- `pulse_groups.csv` contains pulse-context candidates, not confirmed
  anomalies.
- Phase 1F uses temporal overlap only and performs no geographical distance
  clustering.
- A network-wide label describes concurrent coverage within the selected
  sensor mode, not the whole city.
- Phase 1F does not use external event data.
- Phase 1F does not explain or attribute real-world causes.
- Phase 1F does not rank final anomalies.
- Raw `peak_abs_score` is an unbounded robust-z-style value and should not be
  used alone for later importance ranking. Later review or ranking should
  combine pulse scope, duration, active sensor count, observed volume, score
  bands, and baseline confidence.
- Phase 1F does not modify frontend or public dashboard data.
- Phase 1F does not train machine-learning or edge-AI models.
- Spatial clustering, event explanation, and final candidate review are
  deferred to later phases.
