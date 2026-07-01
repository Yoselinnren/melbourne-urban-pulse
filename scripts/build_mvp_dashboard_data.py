"""
Build the first real processed MVP dashboard dataset.

Inputs are read-only raw data sources. Outputs are written to:

- data/processed/mvp_dashboard_data.json
- public/dashboard-data/mvp_dashboard_data.json
- docs/processing-pipeline.md
"""

from __future__ import annotations

import csv
import json
import math
import shutil
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import median
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
PEDESTRIAN_FILE = ROOT / "data" / "raw" / "pedestrian" / "pedestrian_counts_hourly_full.csv"
SENSOR_FILE = ROOT / "data" / "raw" / "sensors" / "pedestrian_sensor_locations.csv"
WEATHER_FILE = ROOT / "data" / "raw" / "weather" / "open_meteo_melbourne_hourly_2025.json"
CALENDAR_FILE = ROOT / "data" / "raw" / "calendar" / "victoria_important_dates_2025.csv"
PROCESSED_OUTPUT = ROOT / "data" / "processed" / "mvp_dashboard_data.json"
PUBLIC_OUTPUT = ROOT / "public" / "dashboard-data" / "mvp_dashboard_data.json"
PIPELINE_DOC = ROOT / "docs" / "processing-pipeline.md"

TZ = ZoneInfo("Australia/Melbourne")
STUDY_START = datetime(2025, 1, 1, 0, 0)
STUDY_END = datetime(2025, 12, 31, 23, 0)
MVP_SENSORS = {
    "4": {
        "display_precinct": "Civic Core",
        "short_label": "Town Hall",
        "selection_reason": "High-activity central CBD sensor suitable for a civic pulse story.",
    },
    "3": {
        "display_precinct": "Retail / Transit",
        "short_label": "Melbourne Central",
        "selection_reason": "High-activity retail and transit-adjacent location.",
    },
    "133": {
        "display_precinct": "Station Gateway",
        "short_label": "Southern Cross",
        "selection_reason": "Transport-oriented comparison point west of the CBD core.",
    },
}


@dataclass
class BuildStats:
    pedestrian_rows_total: int = 0
    pedestrian_rows_2025: int = 0
    pedestrian_rows_selected_sensors: int = 0
    output_hourly_records: int = 0
    output_sensor_readings: int = 0
    missing_sensor_readings: int = 0
    weather_hourly_records: int = 0
    calendar_rows_total: int = 0
    calendar_rows_2025: int = 0


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def local_iso(dt: datetime) -> str:
    return dt.replace(tzinfo=TZ).isoformat(timespec="seconds")


def hour_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:00")


def date_key(value: date | datetime) -> str:
    return value.strftime("%Y-%m-%d")


def parse_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def parse_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def round_or_none(value: float | None, digits: int = 3) -> float | None:
    if value is None or math.isnan(value):
        return None
    return round(value, digits)


def parse_calendar_date(value: str) -> date | None:
    value = value.strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def season_for(dt: date) -> str:
    month = dt.month
    if month in (12, 1, 2):
        return "summer"
    if month in (3, 4, 5):
        return "autumn"
    if month in (6, 7, 8):
        return "winter"
    return "spring"


def read_sensors() -> list[dict[str, Any]]:
    sensor_by_id: dict[str, dict[str, str]] = {}
    with SENSOR_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            sensor_id = row.get("Location_ID", "")
            if sensor_id in MVP_SENSORS:
                sensor_by_id[sensor_id] = row

    sensors: list[dict[str, Any]] = []
    for sensor_id, config in MVP_SENSORS.items():
        row = sensor_by_id[sensor_id]
        sensors.append(
            {
                "sensor_id": sensor_id,
                "sensor_name": row["Sensor_Name"],
                "description": row["Sensor_Description"],
                "status": row["Status"],
                "location_type": row["Location_Type"],
                "coordinates": {
                    "latitude": float(row["Latitude"]),
                    "longitude": float(row["Longitude"]),
                },
                "display": {
                    "precinct": config["display_precinct"],
                    "short_label": config["short_label"],
                },
                "selection_reason": config["selection_reason"],
                "confidence": {
                    "metadata_confidence": 0.95 if row["Status"] == "A" else 0.7,
                    "coverage_note": "Selected from profiled active sensors with 2025 hourly coverage.",
                },
            }
        )
    return sensors


def read_pedestrian_counts(stats: BuildStats) -> dict[str, dict[str, dict[str, Any]]]:
    readings: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)

    with PEDESTRIAN_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            stats.pedestrian_rows_total += 1
            sensing_date = row.get("sensing_date", "")
            if not sensing_date.startswith("2025-"):
                continue
            stats.pedestrian_rows_2025 += 1

            sensor_id = row.get("location_id", "")
            if sensor_id not in MVP_SENSORS:
                continue

            hour = parse_int(row.get("hourday"))
            if hour is None:
                continue
            timestamp_key = f"{sensing_date}T{hour:02d}:00"
            readings[timestamp_key][sensor_id] = {
                "sensor_id": sensor_id,
                "observed_count": parse_int(row.get("pedestriancount")),
                "direction_1_count": parse_int(row.get("direction_1")),
                "direction_2_count": parse_int(row.get("direction_2")),
                "source_row_id": row.get("id"),
            }
            stats.pedestrian_rows_selected_sensors += 1

    return readings


def compute_baseline_stats(
    readings: dict[str, dict[str, dict[str, Any]]],
) -> dict[tuple[str, int, int], dict[str, float]]:
    grouped: dict[tuple[str, int, int], list[int]] = defaultdict(list)
    sensor_max: dict[str, int] = defaultdict(int)

    for timestamp_key, sensor_map in readings.items():
        dt = datetime.strptime(timestamp_key, "%Y-%m-%dT%H:%M")
        for sensor_id, reading in sensor_map.items():
            count = reading.get("observed_count")
            if count is None:
                continue
            grouped[(sensor_id, dt.weekday(), dt.hour)].append(count)
            sensor_max[sensor_id] = max(sensor_max[sensor_id], count)

    baseline: dict[tuple[str, int, int], dict[str, float]] = {}
    for key, values in grouped.items():
        sorted_values = sorted(values)
        q1 = sorted_values[len(sorted_values) // 4]
        q3 = sorted_values[(len(sorted_values) * 3) // 4]
        iqr = max(q3 - q1, 1)
        sensor_id = key[0]
        baseline[key] = {
            "median": float(median(sorted_values)),
            "iqr": float(iqr),
            "sensor_max": float(max(sensor_max[sensor_id], 1)),
        }
    return baseline


def read_weather(stats: BuildStats) -> dict[str, dict[str, Any]]:
    data = json.loads(WEATHER_FILE.read_text(encoding="utf-8"))
    hourly = data["hourly"]
    times = hourly["time"]
    stats.weather_hourly_records = len(times)

    weather_by_time: dict[str, dict[str, Any]] = {}
    for index, timestamp_key in enumerate(times):
        weather_by_time[timestamp_key] = {
            "temperature_2m": hourly["temperature_2m"][index],
            "apparent_temperature": hourly["apparent_temperature"][index],
            "relative_humidity_2m": hourly["relative_humidity_2m"][index],
            "precipitation": hourly["precipitation"][index],
            "rain": hourly["rain"][index],
            "wind_speed_10m": hourly["wind_speed_10m"][index],
            "weather_code": hourly["weather_code"][index],
        }
    return weather_by_time


def weather_comfort_score(weather: dict[str, Any]) -> float:
    apparent = float(weather["apparent_temperature"])
    rain = float(weather["rain"])
    wind = float(weather["wind_speed_10m"])

    temp_penalty = min(abs(apparent - 21) / 18, 1)
    rain_penalty = min(rain / 5, 1)
    wind_penalty = min(max(wind - 15, 0) / 25, 1)
    score = 1 - (0.55 * temp_penalty + 0.3 * rain_penalty + 0.15 * wind_penalty)
    return round(max(min(score, 1), 0), 3)


def read_calendar(stats: BuildStats) -> dict[str, dict[str, Any]]:
    context: dict[str, dict[str, Any]] = {}
    current = STUDY_START.date()
    while current <= STUDY_END.date():
        context[date_key(current)] = {
            "date": date_key(current),
            "weekday": current.strftime("%A"),
            "is_weekend": current.weekday() >= 5,
            "is_public_holiday": False,
            "is_school_term": False,
            "is_school_holiday": False,
            "season": season_for(current),
            "important_dates": [],
            "source_quality": {
                "origin": "calendar_context",
                "confidence_score": 0.75,
            },
        }
        current += timedelta(days=1)

    with CALENDAR_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            stats.calendar_rows_total += 1
            parsed = parse_calendar_date(row.get("important_date", ""))
            if parsed is None or parsed.year != 2025:
                continue
            stats.calendar_rows_2025 += 1
            key = date_key(parsed)
            if key not in context:
                continue

            date_type = row.get("dateType", "")
            name = row.get("name", "")
            if date_type == "PUBLIC_HOLIDAY":
                context[key]["is_public_holiday"] = True
            elif date_type == "SCHOOL_TERM":
                context[key]["is_school_term"] = True
            elif date_type == "SCHOOL_HOLIDAY":
                context[key]["is_school_holiday"] = True

            if len(context[key]["important_dates"]) < 6:
                context[key]["important_dates"].append(
                    {
                        "name": name,
                        "type": date_type,
                        "source_status": "observed_calendar_source",
                    }
                )

    return context


def build_sensor_reading(
    sensor_id: str,
    dt: datetime,
    source_reading: dict[str, Any] | None,
    baseline_stats: dict[tuple[str, int, int], dict[str, float]],
) -> dict[str, Any]:
    key = (sensor_id, dt.weekday(), dt.hour)
    baseline = baseline_stats.get(key)
    baseline_count = round_or_none(baseline["median"], 1) if baseline else None

    if source_reading is None or source_reading.get("observed_count") is None:
        return {
            "sensor_id": sensor_id,
            "observed_count": None,
            "direction_1_count": None,
            "direction_2_count": None,
            "baseline_count": baseline_count,
            "activity_intensity": None,
            "baseline_deviation": None,
            "pulse_score": None,
            "anomaly_score": None,
            "is_missing": True,
            "missing_reason": "source_hour_absent",
            "quality": {
                "observed_data_available": False,
                "confidence_score": 0.25,
            },
        }

    observed = source_reading["observed_count"]
    sensor_max = baseline["sensor_max"] if baseline else max(observed, 1)
    iqr = baseline["iqr"] if baseline else 1
    deviation = (observed - baseline_count) / baseline_count if baseline_count else None
    activity_intensity = observed / sensor_max
    anomaly_score = abs(observed - (baseline_count or observed)) / (iqr * 3)
    pulse_score = min(max((activity_intensity * 0.75) + (min(anomaly_score, 1) * 0.25), 0), 1)

    return {
        "sensor_id": sensor_id,
        "observed_count": observed,
        "direction_1_count": source_reading["direction_1_count"],
        "direction_2_count": source_reading["direction_2_count"],
        "baseline_count": baseline_count,
        "activity_intensity": round_or_none(activity_intensity),
        "baseline_deviation": round_or_none(deviation),
        "pulse_score": round_or_none(pulse_score),
        "anomaly_score": round_or_none(min(anomaly_score, 1)),
        "is_missing": False,
        "quality": {
            "observed_data_available": True,
            "confidence_score": 0.85,
        },
    }


def build_hourly_records(
    readings: dict[str, dict[str, dict[str, Any]]],
    baseline_stats: dict[tuple[str, int, int], dict[str, float]],
    weather: dict[str, dict[str, Any]],
    calendar: dict[str, dict[str, Any]],
    stats: BuildStats,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    current = STUDY_START
    while current <= STUDY_END:
        key = hour_key(current)
        date_str = date_key(current)
        raw_weather = weather[key]
        comfort = weather_comfort_score(raw_weather)
        weather_disruption = bool(raw_weather["rain"] > 0 or raw_weather["wind_speed_10m"] >= 30)
        enriched_weather = {
            **raw_weather,
            "weather_comfort_score": comfort,
            "weather_disruption_flag": weather_disruption,
        }

        sensor_readings = [
            build_sensor_reading(sensor_id, current, readings.get(key, {}).get(sensor_id), baseline_stats)
            for sensor_id in MVP_SENSORS
        ]

        observed_counts = [
            reading["observed_count"]
            for reading in sensor_readings
            if reading["observed_count"] is not None
        ]
        pulse_scores = [
            reading["pulse_score"]
            for reading in sensor_readings
            if reading["pulse_score"] is not None
        ]
        anomaly_scores = [
            reading["anomaly_score"]
            for reading in sensor_readings
            if reading["anomaly_score"] is not None
        ]
        missing_count = sum(1 for reading in sensor_readings if reading["is_missing"])
        complete_count = len(sensor_readings) - missing_count

        total_observed = sum(observed_counts)
        mean_pulse = sum(pulse_scores) / len(pulse_scores) if pulse_scores else None
        max_anomaly = max(anomaly_scores) if anomaly_scores else None

        if weather_disruption:
            dominant_context = "weather_disruption"
        elif calendar[date_str]["is_public_holiday"]:
            dominant_context = "public_holiday"
        elif current.hour < 6:
            dominant_context = "late_night"
        elif current.hour < 10:
            dominant_context = "morning"
        elif current.hour < 17:
            dominant_context = "daytime"
        else:
            dominant_context = "evening"

        confidence = 0.85 if missing_count == 0 else max(0.35, 0.85 - missing_count * 0.2)
        records.append(
            {
                "timestamp": local_iso(current),
                "date": date_str,
                "hour": current.hour,
                "calendar": {
                    "is_weekend": calendar[date_str]["is_weekend"],
                    "is_public_holiday": calendar[date_str]["is_public_holiday"],
                    "season": calendar[date_str]["season"],
                },
                "weather": enriched_weather,
                "sensor_readings": sensor_readings,
                "city_summary": {
                    "total_observed_count": total_observed,
                    "mean_pulse_score": round_or_none(mean_pulse),
                    "max_anomaly_score": round_or_none(max_anomaly),
                    "dominant_context": dominant_context,
                },
                "pulse_field_frame": {
                    "frame_id": current.strftime("%Y-%m-%dT%H"),
                    "render_mode": "sensor_spikes",
                    "confidence_surface_available": False,
                },
                "record_quality": {
                    "complete_sensor_count": complete_count,
                    "missing_sensor_count": missing_count,
                    "confidence_score": round(confidence, 3),
                },
            }
        )
        stats.output_hourly_records += 1
        stats.output_sensor_readings += len(sensor_readings)
        stats.missing_sensor_readings += missing_count
        current += timedelta(hours=1)

    return records


def build_calendar_context(calendar: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [calendar[key] for key in sorted(calendar.keys())]


def build_explanation_cards(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    peak = max(records, key=lambda record: record["city_summary"]["total_observed_count"])
    weather_disruptions = [
        record for record in records if record["weather"]["weather_disruption_flag"]
    ]
    cards = [
        {
            "card_id": "mvp-peak-activity",
            "timestamp": peak["timestamp"],
            "sensor_id": None,
            "severity": "medium",
            "title": "Peak observed activity in selected MVP sensors",
            "summary": "This card is generated from the provisional MVP dataset and highlights the hour with the highest combined observed pedestrian count across selected sensors.",
            "evidence": [
                {
                    "field": "total_observed_count",
                    "value": peak["city_summary"]["total_observed_count"],
                    "origin": "observed_data_aggregate",
                },
                {
                    "field": "mean_pulse_score",
                    "value": peak["city_summary"]["mean_pulse_score"],
                    "origin": "derived_indicator",
                },
            ],
            "possible_causes": [
                {
                    "label": "Routine city activity pattern or context-driven peak; manual event verification not yet linked.",
                    "origin": "manual_annotation_placeholder",
                    "confidence": 0.35,
                }
            ],
            "annotation_status": "placeholder_not_verified",
            "confidence": {
                "score": 0.45,
                "reason": "Derived from processed observations but not manually explained yet.",
            },
        }
    ]

    if weather_disruptions:
        first = weather_disruptions[0]
        cards.append(
            {
                "card_id": "mvp-weather-context",
                "timestamp": first["timestamp"],
                "sensor_id": None,
                "severity": "low",
                "title": "Weather disruption context detected",
                "summary": "Weather disruption flags are derived from rain or high wind thresholds and can be used as contextual explanations, not causal proof.",
                "evidence": [
                    {
                        "field": "rain",
                        "value": first["weather"]["rain"],
                        "origin": "weather_context",
                    },
                    {
                        "field": "wind_speed_10m",
                        "value": first["weather"]["wind_speed_10m"],
                        "origin": "weather_context",
                    },
                ],
                "possible_causes": [
                    {
                        "label": "Rain or high wind may reduce pedestrian comfort.",
                        "origin": "derived_context_placeholder",
                        "confidence": 0.45,
                    }
                ],
                "annotation_status": "placeholder_not_verified",
                "confidence": {
                    "score": 0.45,
                    "reason": "Weather context is observed; behavioural interpretation remains provisional.",
                },
            }
        )

    return cards


def build_pulse_field(records: list[dict[str, Any]]) -> dict[str, Any]:
    selected_frames = []
    for record in records:
        if record["hour"] not in {0, 6, 12, 18, 23}:
            continue
        points = []
        for reading in record["sensor_readings"]:
            points.append(
                {
                    "sensor_id": reading["sensor_id"],
                    "height": reading["pulse_score"],
                    "ripple_radius": reading["activity_intensity"],
                    "color_value": reading["anomaly_score"],
                    "confidence_score": reading["quality"]["confidence_score"],
                    "infrastructure_pressure_proxy": reading["pulse_score"],
                    "edge_density_estimate": None,
                    "is_missing": reading["is_missing"],
                }
            )
        selected_frames.append({"timestamp": record["timestamp"], "points": points})

    return {
        "field_type": "sensor_based_2_5d_pulse_field",
        "coordinate_mode": "lat_lon_projected_to_local_view",
        "rendering_strategy": "spikes_and_ripples",
        "interpolated_surface_enabled": False,
        "legend": {
            "height": "pulse_score",
            "ripple_radius": "activity_intensity",
            "color": "anomaly_score",
            "opacity": "confidence_score",
        },
        "frames": selected_frames,
        "uncertainty_model": {
            "sensor_observation_confidence": "Lower when source hourly observation is missing.",
            "interpolation_confidence": "Not applicable; interpolation is not implemented in this MVP dataset.",
            "manual_explanation_confidence": "Low until event explanations are manually verified.",
        },
    }


def build_dataset(stats: BuildStats) -> dict[str, Any]:
    sensors = read_sensors()
    readings = read_pedestrian_counts(stats)
    baseline_stats = compute_baseline_stats(readings)
    weather = read_weather(stats)
    calendar = read_calendar(stats)
    hourly_records = build_hourly_records(readings, baseline_stats, weather, calendar, stats)

    return {
        "schema_version": "0.1.0",
        "metadata": {
            "project": "Melbourne Urban Pulse",
            "dataset_name": "mvp_dashboard_data",
            "created_at": local_iso(datetime.now().replace(microsecond=0)),
            "created_by": "scripts/build_mvp_dashboard_data.py",
            "description": "First real processed MVP dashboard dataset for selected 2025 Melbourne pedestrian sensors with weather and calendar context.",
            "is_mock": False,
            "timezone": "Australia/Melbourne",
            "spatial_reference": "WGS84 latitude/longitude",
        },
        "provenance": {
            "profile_inputs": [
                "data/metadata/raw_data_profile.json",
                "docs/data-profile.md",
            ],
            "sources": [
                {
                    "source_id": "pedestrian_counts",
                    "source_type": "observed_data",
                    "local_path": rel(PEDESTRIAN_FILE),
                    "used_in_mvp": True,
                    "field_role": "hourly pedestrian observations",
                    "notes": "Filtered to selected MVP sensors and 2025 study period.",
                },
                {
                    "source_id": "pedestrian_sensors",
                    "source_type": "source_metadata",
                    "local_path": rel(SENSOR_FILE),
                    "used_in_mvp": True,
                    "field_role": "sensor names, status, coordinates, and location metadata",
                    "notes": "Used to describe selected active MVP sensors.",
                },
                {
                    "source_id": "open_meteo_weather_json",
                    "source_type": "context_data",
                    "local_path": rel(WEATHER_FILE),
                    "used_in_mvp": True,
                    "field_role": "hourly weather context",
                    "notes": "Primary weather source because JSON has complete aligned hourly arrays for 2025.",
                },
                {
                    "source_id": "victoria_important_dates",
                    "source_type": "context_data",
                    "local_path": rel(CALENDAR_FILE),
                    "used_in_mvp": True,
                    "field_role": "calendar flags and important dates",
                    "notes": "Filtered to 2025 dates; range parsing is not expanded beyond explicit important_date rows.",
                },
                {
                    "source_id": "planned_works_datavic",
                    "source_type": "auxiliary_reference",
                    "local_path": "data/raw/events/city_activities_planned_works_datavic.json",
                    "used_in_mvp": False,
                    "field_role": "future disruption context and manual explanation support",
                    "notes": "Not forced into MVP because profiled local copy does not align cleanly with 2025.",
                },
            ],
        },
        "study_period": {
            "start": local_iso(STUDY_START),
            "end": local_iso(STUDY_END),
            "display_label": "Calendar year 2025",
            "selected_reason": "Weather data fully covers 2025 hourly, calendar context includes 2025, and pedestrian counts include 2025 observations across active sensors.",
        },
        "field_definitions": {
            "observed": [
                "observed_count",
                "direction_1_count",
                "direction_2_count",
                "temperature_2m",
                "apparent_temperature",
                "relative_humidity_2m",
                "precipitation",
                "rain",
                "wind_speed_10m",
                "weather_code",
                "sensor.coordinates",
                "sensor.status",
            ],
            "derived": [
                "baseline_count",
                "activity_intensity",
                "baseline_deviation",
                "weather_comfort_score",
                "weather_disruption_flag",
                "pulse_score",
                "anomaly_score",
                "confidence_score",
            ],
            "manual_annotation": [
                "explanation_cards",
                "possible_causes",
                "event_reference",
            ],
            "future_edge_signal_placeholder": [
                "edge_density_estimate",
                "infrastructure_pressure_proxy",
                "interpolated_surface_value",
            ],
        },
        "sensors": sensors,
        "calendar_context": build_calendar_context(calendar),
        "hourly_records": hourly_records,
        "explanation_cards": build_explanation_cards(hourly_records),
        "pulse_field": build_pulse_field(hourly_records),
        "quality_notes": [
            "This is the first real processed MVP dataset; indicators are provisional and designed for interpretability.",
            "Missing sensor observations remain explicit with observed_count null and is_missing true.",
            "Missing observations are not treated as observed zero activity.",
            "Baseline is a simple median by sensor, weekday, and hour within the 2025 selected data.",
            "Anomaly score is a provisional IQR-scaled deviation and should not be treated as validated anomaly detection.",
            "Open-Meteo JSON is the primary weather source.",
            "Planned works are auxiliary only and are not joined into this MVP output.",
            "Future edge-signal fields are placeholders and do not represent implemented edge AI inference.",
        ],
    }


def write_pipeline_doc(stats: BuildStats, output_size: int) -> None:
    selected_rows = []
    for sensor_id, config in MVP_SENSORS.items():
        selected_rows.append(f"| {sensor_id} | {config['short_label']} | selected MVP sensor |")

    doc = f"""# Processing Pipeline

Generated by `scripts/build_mvp_dashboard_data.py`.

## Inputs

| Source | Role |
| --- | --- |
| `{rel(PEDESTRIAN_FILE)}` | observed hourly pedestrian counts |
| `{rel(SENSOR_FILE)}` | sensor metadata and coordinates |
| `{rel(WEATHER_FILE)}` | primary hourly weather context |
| `{rel(CALENDAR_FILE)}` | calendar and important-date context |

Planned works are intentionally auxiliary only for this MVP because profiling showed the local source does not align cleanly with 2025.

## Study Period

The MVP is filtered to **2025-01-01 00:00 through 2025-12-31 23:00** in the `Australia/Melbourne` timezone.

## Selected Sensors

| Sensor ID | Label | Role |
| --- | --- | --- |
{chr(10).join(selected_rows)}

## Transformations

1. Read raw pedestrian counts without modifying `data/raw`.
2. Filter pedestrian rows to 2025 and MVP sensors `4`, `3`, and `133`.
3. Read sensor metadata and attach names, coordinates, status, and display labels.
4. Read Open-Meteo weather JSON as the primary weather source.
5. Read Victorian important dates and derive daily calendar flags.
6. Generate one hourly dashboard record for every hour in 2025.
7. Keep missing pedestrian observations explicit with `observed_count: null` and `is_missing: true`.
8. Compute provisional baseline and signal indicators.
9. Write identical JSON to `data/processed/` and `public/dashboard-data/`.

## Provisional Metrics

- `baseline_count`: median count by `sensor_id + weekday + hour` within selected 2025 data.
- `activity_intensity`: observed count normalised by the selected sensor's 2025 maximum.
- `baseline_deviation`: `(observed_count - baseline_count) / baseline_count`.
- `anomaly_score`: IQR-scaled absolute deviation, capped to 1.
- `pulse_score`: simple prototype blend of activity intensity and anomaly score.

These indicators are suitable for a first vertical slice but should be documented as provisional.

## Row Counts

| Metric | Count |
| --- | ---: |
| Pedestrian raw rows scanned | {stats.pedestrian_rows_total} |
| Pedestrian rows in 2025 | {stats.pedestrian_rows_2025} |
| Pedestrian rows for selected MVP sensors | {stats.pedestrian_rows_selected_sensors} |
| Weather hourly rows | {stats.weather_hourly_records} |
| Calendar raw rows scanned | {stats.calendar_rows_total} |
| Calendar rows in 2025 | {stats.calendar_rows_2025} |
| Output hourly records | {stats.output_hourly_records} |
| Output sensor readings | {stats.output_sensor_readings} |
| Explicit missing sensor readings | {stats.missing_sensor_readings} |

## Outputs

| Output | Notes |
| --- | --- |
| `{rel(PROCESSED_OUTPUT)}` | internal processed output |
| `{rel(PUBLIC_OUTPUT)}` | frontend-readable static output |

Output JSON size: **{output_size:,} bytes**.

## Assumptions and Limitations

- Missing observations are not treated as observed zero activity.
- Calendar flags are derived from explicit `important_date` rows; multi-day range expansion is not implemented yet.
- Planned works are not joined because the current local source does not provide clean 2025 coverage.
- Event explanation cards remain placeholders until manual event annotation is completed.
- No spatial interpolation or real edge AI inference is implemented.
"""
    PIPELINE_DOC.parent.mkdir(parents=True, exist_ok=True)
    PIPELINE_DOC.write_text(doc, encoding="utf-8")


def main() -> None:
    stats = BuildStats()
    dataset = build_dataset(stats)

    PROCESSED_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    PROCESSED_OUTPUT.write_text(
        json.dumps(dataset, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    shutil.copyfile(PROCESSED_OUTPUT, PUBLIC_OUTPUT)
    output_size = PROCESSED_OUTPUT.stat().st_size
    write_pipeline_doc(stats, output_size)

    print("MVP dashboard data built")
    print(f"Pedestrian raw rows scanned: {stats.pedestrian_rows_total}")
    print(f"Pedestrian rows in 2025: {stats.pedestrian_rows_2025}")
    print(f"Selected MVP sensor rows: {stats.pedestrian_rows_selected_sensors}")
    print(f"Output hourly records: {stats.output_hourly_records}")
    print(f"Output sensor readings: {stats.output_sensor_readings}")
    print(f"Explicit missing sensor readings: {stats.missing_sensor_readings}")
    print(f"Output JSON size bytes: {output_size}")
    print(f"Wrote {rel(PROCESSED_OUTPUT)}")
    print(f"Wrote {rel(PUBLIC_OUTPUT)}")
    print(f"Wrote {rel(PIPELINE_DOC)}")


if __name__ == "__main__":
    main()
