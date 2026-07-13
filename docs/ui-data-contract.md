# UI data contract v1

## Purpose and boundaries
UI-0 produces deterministic browser-safe JSON for `REPRESENTATIVE_12`. Pulse maps to `pulse_group_id`; Sensor ID is the string canonical key. The builder joins and normalizes upstream results. It never recalculates research metrics or generates causal prose. Evidence means overlap plus review state only, and every public causal flag is false. `storyCategory` is editorial and is currently null. `not_in_manual_review_scope` is not “unexplained”. Isolated episodes need not belong to a Pulse.

## Inputs
| Logical input | Source | Use |
|---|---|---|
|sensor selection|`data/metadata/analysis_sensor_selection.csv`|identity, coverage, coordinates|
|sensor locations|`data/raw/sensors/pedestrian_sensor_locations.csv`|installation date|
|baselines|`data/processed/representative_12/regular_baselines.csv`|7×24 rhythm|
|hour panel|`data/processed/representative_12/deviation_interpretation_panel.csv`|window series|
|episodes|`data/processed/representative_12/explanation_ready_candidate_episodes.csv`|member summaries|
|Pulses|`data/processed/representative_12/explanation_ready_pulse_groups.csv`|Pulse/context data|
|evidence facts/matches|`normalized_evidence_manual.csv`, `candidate_evidence_matches.csv`|evidence details|
|reviews|`data/manual/evidence_match_reviews.csv`|public decision/time when present|
|diagnostics|`data/processed/representative_12/*diagnostics.json`|counts/versions|

The large hourly CSV is streamed. The public manifest exposes sanitized logical names only.

## Normalization
`above_baseline→above`, `below_baseline→below`; series additionally maps `near_baseline→near`, `not_applicable→not_applicable`. Pulse scope maps `localized_pulse→localized`, `broad_pulse→broad`, `network_wide_pulse→network_wide`. Evidence confidence `medium→moderate`. Every vocabulary is explicitly allowlisted; unknown values fail.

## Contract rules
Generated files are under `public/data/ui/v1/`; TypeScript definitions are in `src/lib/types/ui-data.ts`. Derived values are month totals, clamped display windows, membership flags, spatial frames, source completeness, participation, and `dataVersion`—not new research metrics.

Missing observations use `observedCount=null` and `isMissing=true`; observed zero remains zero. Project-derived evidence may use a null URL only with `project_derived_without_url`. `reviewedAt` is null until real public review data exists. `mediaIds` is empty.

Regular rhythm has 168 cells, Monday=0 through Sunday=6, then hours 0–23. It retains median, p25, p75, p05, p95, sample size and baseline confidence. p25–p75 is an interquartile band, not a guaranteed normal range; upstream baselines are sensor/weekday/hour/context aware.

Pulse windows request ±6 hours and clamp to the study period. Requested and actual bounds plus `wasClamped` preserve that distinction. Spatial frames contain all 12 sensors; available sensor count is the observed denominator.

Automatic match confidence is not explanation confidence. Pending matches may only be presented as awaiting review. Reviewer identity/private notes, local paths, internal paths and generated causal prose are excluded. External sources require HTTP(S); project-derived null URLs are explicit.

`dataVersion` hashes schema, mode, normalized input identity and SHA-256, without clock/machine/random values. JSON and arrays are deterministically sorted and a staged directory is swapped only after completion.

Budgets: manifest 25 KB, annual 50 KB, Sensor index 10 KB, Sensor detail 75 KB, Pulse index 200 KB, Pulse detail warning 150 KB/hard 250 KB.

```powershell
python scripts/build_ui_data.py --sensor-mode REPRESENTATIVE_12 --output-dir public/data/ui/v1
python scripts/validate_ui_data.py --input-dir public/data/ui/v1
```

Known limitations: no story selection, media mapping, isolated-episode delivery, or reviewed decisions. Planned works are `deferred` with null overlap. Upstream/manual data remain research-owned; this builder owns only the public projection.
