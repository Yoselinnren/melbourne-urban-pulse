# Phase 1S: Configurable Sensor Selection

## Purpose

Phase 1S removes the independent three-sensor assumptions from the analytical
pipeline and introduces reproducible named sensor sets.

The original `MVP_3` run remains the default for backward compatibility.
`REPRESENTATIVE_12` provides a broader but still inspectable analytical set,
while `HIGH_COVERAGE_ALL` records the larger coverage-qualified population for
future scaling work.

Phase 1S changes pipeline configuration and validation. It does not change the
Phase 1A context methodology, Phase 1B baseline methodology, or Phase 1C
scoring formulas.

## Raw 2025 Coverage

`scripts/select_analysis_sensors.py` reads:

- `data/raw/pedestrian/pedestrian_counts_hourly_full.csv`;
- `data/raw/sensors/pedestrian_sensor_locations.csv`.

Coverage is based on unique observed sensor-hour keys between 2025-01-01 and
2025-12-31. The expected maximum is 8,760 hours per sensor.

The current coverage profile contains:

- 102 sensors observed in 2025;
- 102 observed sensors with metadata;
- 30 near-complete sensors with at least 8,750 hours;
- 67 sensors with at least 95% coverage, including the near-complete tier;
- 32 sensors with 50% to less than 95% coverage;
- 3 sensors below 50% coverage;
- 10 sensor IDs whose sensor name is shared with another metadata ID.

Sensor ID is therefore the canonical identity. Sensor name alone is not safe
for joins or selection.

The generated, ignored coverage artifacts are:

- `data/processed/phase1s_sensor_coverage.csv`;
- `data/processed/phase1s_sensor_coverage.json`;
- `data/processed/phase1s_diagnostics.json`.

## Coverage Tiers

| Tier | Rule |
| --- | --- |
| `near_complete` | `available_2025_hours >= 8750` |
| `high_coverage` | `coverage_rate >= 0.95`, after the near-complete tier |
| `partial_coverage` | `0.50 <= coverage_rate < 0.95` |
| `low_coverage` | `coverage_rate < 0.50` |

The tier is a data-availability classification. It does not validate count
plausibility, sensor calibration, relocation history, or spatial
representativeness.

## Shared Selection Configuration

The committed configuration source is:

`data/metadata/analysis_sensor_selection.csv`

Sensors can appear once per selection mode. This intentionally avoids
comma-separated mode lists and keeps each mode directly filterable.

The config records:

- sensor ID and name;
- 2025 available and missing hours;
- coverage rate;
- coordinates and current status;
- metadata location label;
- selection mode and tier;
- enabled state;
- inclusion reason and notes.

`scripts/analysis_config.py` is the shared standard-library loader. It:

- defaults to `MVP_3`;
- validates that a mode exists;
- returns enabled sensors only;
- rejects blank or duplicate IDs within a mode;
- resolves optional output directories.

## Selection Modes

### `MVP_3`

The original validated set:

- `4` — Town Hall (West);
- `3` — Melbourne Central;
- `133` — Southern Cross Station / Lonsdale entrance.

This mode preserves the existing 26,280-row annual panel and remains the
default.

### `REPRESENTATIVE_12`

The selected sensors are:

| ID | Location role | Selection reason |
| ---: | --- | --- |
| 4 | Town Hall West | Civic-core anchor |
| 3 | Melbourne Central | Central retail and transport anchor |
| 133 | Southern Cross / Lonsdale | West-CBD station anchor |
| 209 | Flinders Underpass | Major station movement context |
| 79 | Flinders Street South | Southern CBD street activity |
| 59 | RMIT Building 80 | Education precinct |
| 49 | QVM / Therry Street | Market context |
| 212 | Southbank Promenade | River, leisure, and Southbank context |
| 66 | QV / Swanston | Central retail and pedestrian corridor |
| 58 | Bourke / Spencer | West-CBD street context |
| 23 | Spencer / Collins | Station-adjacent and office context |
| 132 | King / La Trobe | North-west CBD comparison point |

All twelve have near-complete 2025 coverage. The set prioritises coverage,
spatial spread, and urban-function diversity while remaining small enough for
manual inspection. IDs `209` and `212` have names shared by other sensor IDs;
the configuration deliberately uses their IDs as canonical identity.

This is a research/dashboard subset, not a claim that twelve locations fully
represent Melbourne.

### `HIGH_COVERAGE_ALL`

This mode contains all 67 sensors with at least 95% 2025 coverage.

It is configured for reproducibility but is not run through Phase 1A–1C during
Phase 1S. The current pipeline materialises complete CSV and JSON copies at
multiple stages and holds full panels in memory. Running 67 sensors would
produce 586,920 annual sensor-hour rows and potentially multi-gigabyte
aggregate output.

Before using this mode analytically, the pipeline should adopt streaming or
columnar internal storage, lifecycle validation, and a deliberate output
retention policy.

## Configurable Pipeline

The following scripts now accept:

```text
--sensor-mode MODE
--output-dir PATH
```

- `build_analytical_panel.py`;
- `classify_contexts.py`;
- `build_regular_baselines.py`;
- `score_observations.py`.

The analytical panel reads sensor IDs and display metadata from the shared
config and sensor metadata file. Context classification validates the panel
against the configured set. Baseline and scoring stages derive expected group
counts dynamically:

```text
expected panel rows = selected sensors × observed hourly keys
expected baseline groups = selected sensors × 7 weekdays × 24 hours
```

Phase 1B and Phase 1C reject a panel whose sensor IDs do not match the requested
mode.

## Running the Modes

### Coverage and Config Generation

```powershell
python scripts/select_analysis_sensors.py
```

This refreshes the ignored coverage diagnostics and the small shared selection
CSV.

### Default `MVP_3`

```powershell
python scripts/build_analytical_panel.py
python scripts/classify_contexts.py
python scripts/build_regular_baselines.py
python scripts/score_observations.py
```

Explicit mode arguments are also accepted:

```powershell
python scripts/build_analytical_panel.py --sensor-mode MVP_3
```

Without `--output-dir`, output is mode-aware:

- `MVP_3` uses `data/processed/`;
- `REPRESENTATIVE_12` uses `data/processed/representative_12/`;
- `HIGH_COVERAGE_ALL` uses `data/processed/high_coverage_all/`.

An explicitly supplied `--output-dir` overrides these defaults.

### Isolated `REPRESENTATIVE_12`

Run each stage with the same mode and directory:

```powershell
python scripts/build_analytical_panel.py `
  --sensor-mode REPRESENTATIVE_12 `
  --output-dir data/processed/representative_12

python scripts/classify_contexts.py `
  --sensor-mode REPRESENTATIVE_12 `
  --output-dir data/processed/representative_12

python scripts/build_regular_baselines.py `
  --sensor-mode REPRESENTATIVE_12 `
  --output-dir data/processed/representative_12

python scripts/score_observations.py `
  --sensor-mode REPRESENTATIVE_12 `
  --output-dir data/processed/representative_12
```

The output directory must be consistent across stages.

## Validation Results

### `MVP_3`

- selected sensors: 3;
- panel rows: 26,280 expected and generated;
- missing observations: 3;
- baseline-eligible rows: 21,321;
- baseline groups: 504/504;
- scored rows: 26,277;
- baseline joins: 26,280 successful, 0 missing.

These values reproduce the validated pre-Phase-1S behavior.

### `REPRESENTATIVE_12`

- selected sensors: 12;
- panel rows: 105,120 expected and generated;
- missing observations: 16;
- baseline-eligible rows: 85,281;
- baseline groups: 2,016/2,016;
- group sample size: minimum 33, median 43, maximum 51;
- baseline confidence: 1,584 high and 432 medium groups;
- scored rows: 105,104;
- unscored rows: 16 missing observations;
- baseline joins: 105,120 successful, 0 missing;
- no baseline fallbacks used.

All Phase 1A–1C sanity checks passed.

## Scaling and Delivery Risks

- Each analytical stage currently loads complete row collections into memory.
- CSV and JSON are both written for each large panel.
- JSON is substantially larger than CSV and should not be the preferred
  internal format at broader scales.
- Partial-year sensors need installation and lifecycle-aware eligibility.
- Shared sensor names require ID-based joins.
- A larger set can introduce spatial redundancy without improving
  representativeness.
- Full analytical panels are internal research artifacts and should not be
  statically imported by the frontend.

Frontend delivery should continue to use compact, purpose-built summaries and
selected windows rather than full annual analytical panels.

## Limitations and Non-Goals

- Selection uses coverage and manually documented urban-function diversity; it
  is not an optimised spatial sampling model.
- Metadata status is a current snapshot, not historical uptime evidence.
- Coverage does not validate the plausibility of counts.
- The configured representative set remains concentrated in central
  Melbourne.
- Phase 1S does not extract anomalies.
- Phase 1S does not modify the frontend.
- Phase 1S does not implement edge AI.
- Phase 1S does not solve event explanation.
- Phase 1S only removes the three-sensor hardcoding and enables broader
  analytical runs.
