# Raw Data Profile

Generated at: `2026-06-30T20:45:35`

## Overview

| Metric | Value |
| --- | --- |
| Discovered files | 7 |
| Parsed files | 6 |
| Unparsed files | 1 |
| Recommended MVP study period | 2025-01-01 to 2025-12-31 |

## Source Files

| Path | Format | Parsed | Rows/Records | Columns/Fields |
| --- | --- | --- | --- | --- |
| data/raw/calendar/victoria_important_dates_2025.csv | csv | True | 2879 | 7 |
| data/raw/events/city_activities_planned_works_datavic.json | json | True | 605 | 12 |
| data/raw/events/melbourne_events_calendar_2025.pdf | pdf | False |  |  |
| data/raw/pedestrian/pedestrian_counts_hourly_full.csv | csv | True | 1607116 | 9 |
| data/raw/sensors/pedestrian_sensor_locations.csv | csv | True | 136 | 12 |
| data/raw/weather/open_meteo_melbourne_hourly_2025.csv | csv | True | 8760 | 8 |
| data/raw/weather/open_meteo_melbourne_hourly_2025.json | json | True | 8760 |  |

## Parsed Source Details

### `data/raw/calendar/victoria_important_dates_2025.csv`

- Rows: `2879`
- Columns: `arun, dateType, name, important_date, publisher, description, source`
- Date ranges: `{"dateType": {"min": null, "max": null}, "important_date": {"min": "2018-10-07T00:00", "max": "2030-12-20T00:00"}}`
- Missing percent: `{"arun": 60.924, "description": 41.403, "source": 1.945}`
- Top categories: `{"dateType": [{"value": "MULTI_FAITH", "count": 2247}, {"value": "PARLIAMENT_SITTING", "count": 333}, {"value": "PUBLIC_HOLIDAY", "count": 128}, {"value": "SCHOOL_TERM", "count": 102}, {"value": "SCHOOL_HOLIDAY", "count": 55}, {"value": "DAYLIGHT_SAVING", "count": 14}], "name": [{"value": "Both Houses sitting", "count": 317}, {"value": "Great Lent (Orthodox)", "count": 287}, {"value": "Ramadan", "count": 268}, {"value": "Advent", "count": 202}, {"value": "Lent", "count": 132}, {"value": "Lent begins", "count": 132}, {"value": "Ridvan", "count": 96}, {"value": "Lent begins on Ash Wednesday", "count": 88}, {"value": "Navaratri", "count": 75}, {"value": "Pesach", "count": 64}, {"value": "Hanukkah", "count": 64}, {"value": "Holy Week", "count": 57}]}`

### `data/raw/events/city_activities_planned_works_datavic.json`

- Reported total: `605`
- Records loaded: `605`
- Fields: `_id, activity_id, classification, end_date, location, notes, source_id, start_date, status, small_area, geo_point_2d, json_geometry_geometry`
- Date ranges: `{"start_date": {"min": "2015-10-11T00:00", "max": "2023-05-01T00:00"}, "end_date": {"min": "2022-05-12T00:00", "max": "2921-11-19T00:00"}}`
- Classifications: `[{"value": "Structures", "count": 415}, {"value": "Traffic Management", "count": 85}, {"value": "Reserved Parking", "count": 69}, {"value": "Event", "count": 21}, {"value": "Public Event", "count": 14}, {"value": "Private Event", "count": 1}]`
- Statuses: `[{"value": "CONFIRMED", "count": 378}, {"value": "Confirmed", "count": 118}, {"value": "PROPOSED", "count": 74}, {"value": "PROVISIONAL", "count": 14}, {"value": "WARNING", "count": 12}, {"value": "REINSTATEMENT", "count": 7}, {"value": "PROVISIONAL MULTIPLE", "count": 2}]`
- Location fields: `location, small_area, geo_point_2d, json_geometry_geometry`

### `data/raw/pedestrian/pedestrian_counts_hourly_full.csv`

- Rows: `1607116`
- Columns: `id, location_id, sensing_date, hourday, direction_1, direction_2, pedestriancount, sensor_name, location`
- Date ranges: `{"sensing_date": {"min": "2024-06-29T00:00", "max": "2026-06-28T00:00"}, "sensing_date + hourday": {"min": "2024-06-29T00:00", "max": "2026-06-28T03:00"}}`
- Unique identifier counts: `{"id": 5001, "location_id": 102, "sensor_name": 97}`
- Top categories: `{"sensor_name": [{"value": "SouthB_T", "count": 34892}, {"value": "FliS_T", "count": 34872}, {"value": "Lat526_T", "count": 32135}, {"value": "WatCit_T", "count": 31903}, {"value": "BirBridge_T", "count": 17915}, {"value": "Swa295_T", "count": 17498}, {"value": "King335_T", "count": 17495}, {"value": "261Will_T", "count": 17493}, {"value": "Col623_T", "count": 17493}, {"value": "Spen161_T", "count": 17492}, {"value": "Lon189_T", "count": 17492}, {"value": "RMIT14_T", "count": 17490}]}`

### `data/raw/sensors/pedestrian_sensor_locations.csv`

- Rows: `136`
- Columns: `Location_ID, Sensor_Description, Sensor_Name, Installation_Date, Note, Location_Type, Status, Direction_1, Direction_2, Latitude, Longitude, Location`
- Date ranges: `{"Installation_Date": {"min": "2009-01-20T00:00", "max": "2025-10-18T00:00"}}`
- Unique identifier counts: `{"Location_ID": 136, "Sensor_Description": 135, "Sensor_Name": 131}`
- Missing percent: `{"Installation_Date": 0.735, "Note": 71.324, "Direction_1": 22.794, "Direction_2": 22.794}`
- Top categories: `{"Sensor_Name": [{"value": "BirBridge_T", "count": 2}, {"value": "WatCit_T", "count": 2}, {"value": "FliS_T", "count": 2}, {"value": "Lat526_T", "count": 2}, {"value": "SouthB_T", "count": 2}, {"value": "PriNW_T", "count": 1}, {"value": "Col700_T", "count": 1}, {"value": "NewQ_T", "count": 1}, {"value": "SanBri_T", "count": 1}, {"value": "Col12_T", "count": 1}, {"value": "Swa31", "count": 1}, {"value": "UM3_T", "count": 1}], "Location_Type": [{"value": "Outdoor", "count": 102}, {"value": "Indoor", "count": 34}], "Status": [{"value": "A", "count": 136}]}`

### `data/raw/weather/open_meteo_melbourne_hourly_2025.csv`

- Rows: `8760`
- Columns: `time, temperature_2m (°C), relative_humidity_2m (%), apparent_temperature (°C), precipitation (mm), rain (mm), wind_speed_10m (km/h), weather_code (wmo code)`
- Date ranges: `{"time": {"min": "2025-01-01T00:00", "max": "2025-12-31T23:00"}}`

### `data/raw/weather/open_meteo_melbourne_hourly_2025.json`

- Timezone: `Australia/Melbourne`
- Hourly count: `8760`
- First timestamp: `2025-01-01T00:00`
- Last timestamp: `2025-12-31T23:00`
- Variables: `temperature_2m, relative_humidity_2m, apparent_temperature, precipitation, rain, wind_speed_10m, weather_code`

## Unparsed Files

| Path | Format | Reason |
| --- | --- | --- |
| data/raw/events/melbourne_events_calendar_2025.pdf | pdf | Unsupported for lightweight profiling in this script. |

## Candidate Pedestrian Sensors

| Sensor ID | Name | Description | Rows 2025 | Total Count 2025 |
| --- | --- | --- | --- | --- |
| 4 | Swa123_T | Town Hall (West) | 8759 | 13586917 |
| 66 | QVN_T | QV2 Apartments, 300 Swanston Street | 8759 | 10526946 |
| 3 | Swa295_T | Melbourne Central | 8759 | 9515455 |
| 47 | Eli250_T | Melbourne Central-Elizabeth St (East) | 8759 | 7971626 |
| 209 | FliS_T | Flinders Underpass - Walkway | 8759 | 6375159 |
| 59 | RMIT_T | Building 80 RMIT | 8759 | 6111033 |
| 133 | Spen229_T | I-Hub Southern Cross Station - Lonsdale Street Entrance - South | 8759 | 5571993 |
| 79 | FliSS_T | Flinders St (South) | 8759 | 4823050 |
| 134 | Spen201_T | I-Hub Southern Cross Station - Bourke Street Entrance - North | 8759 | 4465504 |
| 30 | Lon189_T | Lonsdale St (South) | 8759 | 3684457 |

## Obvious Data Quality Notes

- Raw pedestrian counts include multiple years; MVP filtering should explicitly constrain the study period.
- Manual event annotations are not part of `data/raw` and currently need separate curation before they can explain anomalies.
- The planned works JSON is useful for disruption context, but its date range may not align with a 2025 pedestrian/weather MVP without additional source updates.
- Open-Meteo CSV contains metadata rows before the hourly table; the JSON file is cleaner for automated parsing.
