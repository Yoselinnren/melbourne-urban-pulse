# Data Model

This document defines the working data model for Melbourne Urban Pulse.

## Purpose

The data model should support an interpretable urban signal interface, not only one-off charts. It should allow observed, derived, contextual, and future simulated or edge-generated signals to share a consistent structure.

## Source Layers

### Observed Mobility Signals

Initial signal:

- Pedestrian hourly counts

Later extensions:

- Vehicle flow
- Cycling activity
- Public transport activity

### Sensor Metadata

Expected fields:

- `sensor_id`
- `sensor_name`
- `description`
- `latitude`
- `longitude`
- `status`
- `direction_1`
- `direction_2`
- `installation_date`

### Environmental Context

Expected fields:

- `timestamp`
- `temperature`
- `apparent_temperature`
- `humidity`
- `precipitation`
- `rain`
- `wind_speed`
- `weather_code`

### Calendar Context

Expected fields:

- `date`
- `date_type`
- `name`
- `description`
- `source`
- derived flags such as `is_weekend`, `is_public_holiday`, and `season`

### Event and Disruption Context

Expected fields:

- `event_id`
- `date`
- `start_time`
- `end_time`
- `event_name`
- `event_type`
- `location`
- `precinct`
- `source_url`
- `expected_effect`
- `confidence`
- `notes`

## Dashboard Output Schema

The frontend should consume a small processed JSON export rather than reading raw files directly.

Candidate top-level structure:

```json
{
  "metadata": {},
  "timeRange": {},
  "sensors": [],
  "observations": [],
  "context": [],
  "metrics": [],
  "explanations": []
}
```

This schema will be refined after data profiling.

## Open Questions

- Which sensor subset should be used for the first vertical slice?
- What date range best demonstrates the urban pulse story?
- How should event confidence be represented in the UI?
- Which processed fields are required for the 2.5D Urban Pulse Field?
