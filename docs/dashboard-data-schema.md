# Dashboard Data Schema

This document defines the proposed dashboard data contract for the first Melbourne Urban Pulse frontend vertical slice.

The schema is designed from the raw profiling results in:

- `data/metadata/raw_data_profile.json`
- `docs/data-profile.md`

It is intentionally frontend-friendly: the dashboard should read one small processed JSON export rather than loading raw CSV/JSON files directly.

## Design Goals

The dashboard JSON should support:

- project metadata
- data sources and provenance
- selected MVP study period
- selected sensors and locations
- hourly sensor activity
- hourly weather context
- daily calendar context
- anomaly placeholders
- event explanation placeholders
- 2.5D Urban Pulse Field placeholders
- confidence and uncertainty fields

## Proposed Top-Level Structure

```json
{
  "schema_version": "0.1.0",
  "metadata": {},
  "provenance": {},
  "study_period": {},
  "field_definitions": {},
  "sensors": [],
  "calendar_context": [],
  "hourly_records": [],
  "explanation_cards": [],
  "pulse_field": {},
  "quality_notes": []
}
```

## Sections

### `schema_version`

String version for this dashboard data contract. The first proposed version is `0.1.0`.

### `metadata`

Describes the export itself.

Recommended fields:

- `project`
- `dataset_name`
- `created_at`
- `created_by`
- `description`
- `is_mock`
- `timezone`
- `spatial_reference`

### `provenance`

Documents source files and source roles.

Each source should include:

- `source_id`
- `source_type`
- `local_path`
- `status`
- `used_in_mvp`
- `field_role`
- `notes`

Source roles should distinguish:

- `observed_data`
- `source_metadata`
- `context_data`
- `manual_annotation`
- `auxiliary_reference`
- `future_extension`

### `study_period`

The MVP study period is:

- `start`: `2025-01-01T00:00:00+11:00`
- `end`: `2025-12-31T23:00:00+11:00`
- `display_label`: `Calendar year 2025`

The profiling layer recommends 2025 because Open-Meteo weather has complete 2025 hourly coverage, the calendar source contains 2025 context, and pedestrian counts include 2025 observations across active sensors.

### `field_definitions`

Documents whether dashboard fields are observed, derived, manual, or placeholder.

Recommended categories:

- `observed`: directly measured or reported from source data.
- `derived`: calculated during processing.
- `manual`: curated by the project author.
- `placeholder`: included for interface design before final processing.
- `future_edge_signal`: reserved for future edge-generated sensing data.

### `sensors`

Contains selected MVP sensors and location metadata.

Recommended fields:

- `sensor_id`
- `sensor_name`
- `description`
- `status`
- `location_type`
- `coordinates.latitude`
- `coordinates.longitude`
- `display.precinct`
- `display.short_label`
- `source_fields`
- `selection_reason`
- `confidence`

The first MVP should use a small subset of active high-coverage sensors before expanding.

### `calendar_context`

Daily context records.

Recommended fields:

- `date`
- `weekday`
- `is_weekend`
- `is_public_holiday`
- `is_school_term`
- `is_school_holiday`
- `season`
- `important_dates`
- `source_quality`

The raw calendar file spans 2018 to 2030, so processing should filter it to the study period.

### `hourly_records`

The main time-series structure. Each row represents one hour.

Recommended fields:

- `timestamp`
- `date`
- `hour`
- `calendar`
- `weather`
- `sensor_readings`
- `city_summary`
- `pulse_field_frame`
- `record_quality`

Each `sensor_readings` item should include:

- `sensor_id`
- `observed_count`
- `direction_1_count`
- `direction_2_count`
- `baseline_count`
- `activity_intensity`
- `baseline_deviation`
- `pulse_score`
- `anomaly_score`
- `is_missing`
- `quality`

Missing hourly observations should be represented explicitly:

```json
{
  "sensor_id": "4",
  "observed_count": null,
  "is_missing": true,
  "missing_reason": "source_hour_absent",
  "quality": {
    "observed_data_available": false,
    "confidence_score": 0.25
  }
}
```

Do not silently fill missing pedestrian observations in the dashboard export. If interpolation or imputation is later used for a derived visual, keep the observed value as `null` and place the estimated value in a separate derived field.

### `weather`

Weather should be sourced from Open-Meteo JSON where possible.

Preferred fields:

- `temperature_2m`
- `apparent_temperature`
- `relative_humidity_2m`
- `precipitation`
- `rain`
- `wind_speed_10m`
- `weather_code`
- `weather_comfort_score`
- `weather_disruption_flag`

The JSON source is preferred over the CSV because it has a cleaner nested hourly structure, complete 2025 hourly arrays, and avoids CSV metadata/header handling issues.

### `explanation_cards`

Cards used by the dashboard to explain unusual activity or contextual patterns.

Recommended fields:

- `card_id`
- `timestamp`
- `sensor_id`
- `severity`
- `title`
- `summary`
- `evidence`
- `possible_causes`
- `confidence`
- `annotation_status`

These cards may start as placeholders before real anomaly detection and manual event curation are complete.

### `pulse_field`

Supports the 2.5D Urban Pulse Field.

Recommended fields:

- `field_type`
- `coordinate_mode`
- `rendering_strategy`
- `frames`
- `legend`
- `uncertainty_model`

For the first frontend vertical slice, use sensor-based spikes and ripples rather than interpolated surfaces.

### `quality_notes`

A human-readable list of limitations carried into the dashboard export.

## Planned Works as Auxiliary Context

The planned works JSON should be auxiliary only for the MVP because profiling shows its current local copy does not align cleanly with 2025. It contains records mostly between 2015 and 2023, inconsistent status casing, and one suspicious max end date in year 2921.

It may still be useful as:

- a future disruption-context source
- a schema reference for event/disruption fields
- a source for manually verified explanation cards if specific records are relevant

## Field Origin Classification

| Field group | Origin |
| --- | --- |
| pedestrian counts | observed |
| direction counts | observed |
| sensor coordinates | observed metadata |
| sensor status | observed metadata |
| weather variables | observed/context source |
| calendar flags | derived from context source |
| baseline count | derived |
| activity intensity | derived |
| baseline deviation | derived |
| pulse score | derived prototype indicator |
| anomaly score | derived placeholder until method is final |
| explanation cards | manual or placeholder |
| event links | manual annotation or auxiliary context |
| pulse field height/ripple | derived visual encoding |
| confidence score | derived uncertainty indicator |
| edge signal fields | future placeholder |
