# MVP Scope

This document defines the first Melbourne Urban Pulse MVP scope after raw data profiling.

## MVP Objective

Create a small, credible vertical slice that proves the project can connect:

1. observed pedestrian activity,
2. sensor location metadata,
3. weather context,
4. calendar context,
5. interpretable pulse/anomaly placeholders,
6. a frontend-ready schema for the future 2.5D Urban Pulse Field.

The MVP should avoid trying to use every collected data source at once.

## Study Period

The selected MVP study period is:

**2025-01-01 to 2025-12-31**

Reasons:

- Open-Meteo weather data has complete hourly coverage for 2025.
- The calendar source includes 2025-relevant public holidays, school terms, school holidays, and daylight-saving context.
- Pedestrian counts include 2025 observations across active sensors.
- A single calendar year is easier to explain in the methodology and interface.

## MVP Sensor Selection

The profiling layer identified high-coverage active sensors with 8,759 hourly rows in 2025. Candidate MVP sensors include:

| Sensor ID | Name | Description | Reason |
| --- | --- | --- | --- |
| 4 | Swa123_T | Town Hall (West) | High activity, central CBD location |
| 66 | QVN_T | QV2 Apartments, 300 Swanston Street | High activity, Swanston Street / QV context |
| 3 | Swa295_T | Melbourne Central | High activity, major retail/transit area |
| 47 | Eli250_T | Melbourne Central-Elizabeth St (East) | Strong central comparison point |
| 209 | FliS_T | Flinders Underpass - Walkway | Important station/underpass movement |
| 133 | Spen229_T | Southern Cross Station / Lonsdale entrance | Major station precinct |

The first frontend mock can use 2–3 sensors. A practical initial trio is:

- `4` — Town Hall (West)
- `3` — Melbourne Central
- `133` — Southern Cross Station / Lonsdale entrance

This creates a simple spatial story across civic, retail, and transport-oriented locations.

## Included in MVP

- Selected pedestrian sensors
- Hourly pedestrian counts
- Sensor coordinates
- Weather context from Open-Meteo JSON
- Calendar flags derived from Victorian important dates
- Derived baseline placeholders
- Derived pulse score placeholders
- Derived anomaly score placeholders
- Placeholder explanation cards
- 2.5D sensor-spike/ripple placeholders
- Confidence and uncertainty fields

## Excluded from MVP

- Full frontend UI implementation
- Final processed dashboard dataset
- Vehicle-flow integration
- Cycling integration
- Public transport integration
- Real edge AI inference
- Spatial interpolation surfaces
- Automated event explanation pipeline
- Heavy modelling or black-box anomaly detection

## Why Weather JSON Is Preferred

The Open-Meteo JSON file is preferred over the weather CSV because:

- it has a clean `hourly` object;
- every hourly variable has 8,760 aligned values;
- timestamps run from `2025-01-01T00:00` to `2025-12-31T23:00`;
- the CSV contains metadata rows before the actual hourly table;
- JSON is less likely to require fragile header handling.

The weather CSV can remain useful for manual inspection.

## Why Planned Works Is Auxiliary Only

The planned works JSON is not a primary MVP source because:

- the current local records do not align cleanly with 2025;
- most profiled start dates fall before 2025;
- one profiled end date appears suspicious: `2921-11-19`;
- statuses use inconsistent casing, such as `CONFIRMED` and `Confirmed`;
- it is more useful as optional disruption context than as a dependable hourly signal.

It can later support manually reviewed explanation cards.

## Missing Hourly Observations

Missing pedestrian observations should be represented explicitly in the dashboard JSON.

Rules:

- Use `observed_count: null` when an observed hourly value is missing.
- Set `is_missing: true`.
- Add `missing_reason` when known.
- Do not overwrite observed fields with interpolated values.
- If a derived visual needs continuity, put estimates in separate fields such as `estimated_count` or `pulse_score`.
- Lower the confidence score for missing or estimated records.

## Field Origin Rules

The dashboard schema must clearly separate:

- **Observed data**: source-reported pedestrian counts, direction counts, weather variables, sensor coordinates.
- **Derived indicators**: baseline count, activity intensity, baseline deviation, weather comfort score, pulse score, anomaly score, confidence score.
- **Manual annotations**: event explanation cards, verified anomaly causes, curated source links.
- **Future placeholders**: edge signal estimates, infrastructure pressure proxy, interpolated pulse surface values.

## First Frontend Vertical Slice

The first frontend vertical slice should be able to render:

- a study-period label;
- sensor cards or a sensor selector;
- a small hourly time-series chart;
- weather context for each hour;
- simple calendar labels;
- placeholder pulse and anomaly scores;
- a basic explanation card;
- a first 2.5D pulse-field mock using sensor positions and spike heights.

The frontend should use `public/dashboard-data/example_dashboard_data.json` only as a structural mock, not as final analytical output.
