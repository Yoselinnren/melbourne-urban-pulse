"""Build the Phase 1A canonical long-form analytical hourly panel.

This stage joins observations and context only. It intentionally does not
calculate baselines, activity scores, anomaly scores, or pulse scores.
"""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PEDESTRIAN_FILE = ROOT / "data" / "raw" / "pedestrian" / "pedestrian_counts_hourly_full.csv"
SENSOR_FILE = ROOT / "data" / "raw" / "sensors" / "pedestrian_sensor_locations.csv"
WEATHER_FILE = ROOT / "data" / "raw" / "weather" / "open_meteo_melbourne_hourly_2025.json"
CALENDAR_FILE = ROOT / "data" / "raw" / "calendar" / "victoria_important_dates_2025.csv"
MANUAL_EVENTS_FILE = ROOT / "data" / "manual" / "events_manual.csv"
PROCESSED_DIR = ROOT / "data" / "processed"
CSV_OUTPUT = PROCESSED_DIR / "analytical_hourly_panel.csv"
JSON_OUTPUT = PROCESSED_DIR / "analytical_hourly_panel.json"

STUDY_START = datetime(2025, 1, 1, 0, 0)
STUDY_END = datetime(2025, 12, 31, 23, 0)
MELBOURNE_DST_END = datetime(2025, 4, 6, 3, 0)
MELBOURNE_DST_START = datetime(2025, 10, 5, 2, 0)
SELECTED_SENSOR_IDS = ("4", "3", "133")
SENSOR_DISPLAY_CONFIG = {
    "4": {"precinct": "Civic Core", "short_label": "Town Hall"},
    "3": {"precinct": "Retail / Transit", "short_label": "Melbourne Central"},
    "133": {"precinct": "Station Gateway", "short_label": "Southern Cross"},
}
PROCESSING_STAGE = "canonical_analytical_panel"
PROCESSING_VERSION = "phase1a-0.1.0"

LIST_FIELDS = {
    "source_dataset_ids",
    "calendar_labels",
    "school_related_labels",
    "daylight_saving_labels",
    "manual_event_ids",
    "manual_event_names",
    "manual_event_types",
    "manual_event_source_urls",
    "manual_event_expected_effects",
}


def parse_int(value: str | None) -> int | None:
    if value is None or value.strip() == "":
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def parse_float(value: str | None) -> float | None:
    if value is None or value.strip() == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    return None


def parse_time(value: str | None, default: time) -> time:
    if not value or not value.strip():
        return default
    cleaned = value.strip()
    for fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p"):
        try:
            return datetime.strptime(cleaned, fmt).time()
        except ValueError:
            continue
    return default


def local_iso(value: datetime) -> str:
    # The project uses one local key for each of the 8,760 nominal 2025 hours.
    # Explicit offsets avoid a runtime tzdata dependency on Windows while
    # preserving Melbourne's 2025 DST boundary semantics for those keys.
    offset_hours = (
        11
        if value < MELBOURNE_DST_END or value >= MELBOURNE_DST_START
        else 10
    )
    return value.replace(
        tzinfo=timezone(timedelta(hours=offset_hours))
    ).isoformat(timespec="seconds")


def hour_key(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:00")


def unique_nonempty(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def read_sensors() -> dict[str, dict[str, Any]]:
    sensors: dict[str, dict[str, Any]] = {}
    with SENSOR_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            sensor_id = row.get("Location_ID", "")
            if sensor_id not in SELECTED_SENSOR_IDS:
                continue
            display = SENSOR_DISPLAY_CONFIG[sensor_id]
            sensors[sensor_id] = {
                "sensor_id": sensor_id,
                "sensor_name": row.get("Sensor_Name", ""),
                "sensor_description": row.get("Sensor_Description", ""),
                "sensor_status": row.get("Status", ""),
                "sensor_location_type": row.get("Location_Type", ""),
                "latitude": parse_float(row.get("Latitude")),
                "longitude": parse_float(row.get("Longitude")),
                "sensor_location": row.get("Location", ""),
                "precinct": display["precinct"],
                "sensor_short_label": display["short_label"],
            }

    missing = [sensor_id for sensor_id in SELECTED_SENSOR_IDS if sensor_id not in sensors]
    if missing:
        raise ValueError(f"Selected sensors missing from metadata: {', '.join(missing)}")
    return sensors


def read_pedestrian_observations() -> dict[tuple[str, str], dict[str, Any]]:
    observations: dict[tuple[str, str], dict[str, Any]] = {}
    with PEDESTRIAN_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            sensing_date = row.get("sensing_date", "")
            sensor_id = row.get("location_id", "")
            if not sensing_date.startswith("2025-") or sensor_id not in SELECTED_SENSOR_IDS:
                continue
            hour = parse_int(row.get("hourday"))
            if hour is None or not 0 <= hour <= 23:
                continue
            key = (f"{sensing_date}T{hour:02d}:00", sensor_id)
            observations[key] = {
                "source_record_id": row.get("id", ""),
                "observed_count": parse_int(row.get("pedestriancount")),
                "direction_1_count": parse_int(row.get("direction_1")),
                "direction_2_count": parse_int(row.get("direction_2")),
            }
    return observations


def read_weather() -> dict[str, dict[str, Any]]:
    payload = json.loads(WEATHER_FILE.read_text(encoding="utf-8"))
    hourly = payload["hourly"]
    fields = (
        "temperature_2m",
        "apparent_temperature",
        "relative_humidity_2m",
        "precipitation",
        "rain",
        "wind_speed_10m",
        "weather_code",
    )
    return {
        timestamp: {field: hourly[field][index] for field in fields}
        for index, timestamp in enumerate(hourly["time"])
    }


def empty_calendar_day(value: date) -> dict[str, Any]:
    return {
        "is_weekend": value.weekday() >= 5,
        "is_public_holiday": False,
        "is_school_term": False,
        "is_school_holiday": False,
        "is_daylight_saving_transition": False,
        "calendar_labels": [],
        "school_related_labels": [],
        "daylight_saving_labels": [],
    }


def add_date_range(
    calendar: dict[str, dict[str, Any]],
    start: date,
    end: date,
    flag: str,
    label: str,
    label_field: str,
) -> None:
    current = max(start, STUDY_START.date())
    last = min(end, STUDY_END.date())
    while current <= last:
        context = calendar[current.isoformat()]
        context[flag] = True
        context[label_field].append(label)
        current += timedelta(days=1)


def read_calendar() -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    calendar: dict[str, dict[str, Any]] = {}
    current = STUDY_START.date()
    while current <= STUDY_END.date():
        calendar[current.isoformat()] = empty_calendar_day(current)
        current += timedelta(days=1)

    school_holiday_boundaries: dict[tuple[int, int], dict[str, date]] = defaultdict(dict)
    school_term_boundaries: dict[tuple[int, int], dict[str, date]] = defaultdict(dict)
    explicit_2025_dates: set[str] = set()

    with CALENDAR_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            parsed = parse_date(row.get("important_date"))
            if parsed is None or parsed.year != 2025:
                continue
            key = parsed.isoformat()
            explicit_2025_dates.add(key)
            date_type = row.get("dateType", "").strip()
            label = row.get("name", "").strip()
            context = calendar[key]
            context["calendar_labels"].append(label)

            if date_type == "PUBLIC_HOLIDAY":
                context["is_public_holiday"] = True
            if date_type in {"SCHOOL_TERM", "SCHOOL_HOLIDAY"}:
                context["school_related_labels"].append(label)
            if date_type == "DAYLIGHT_SAVING":
                context["is_daylight_saving_transition"] = True
                context["daylight_saving_labels"].append(label)

            holiday_match = re.search(
                r"Term\s+(\d)\s+(\d{4})\s+-\s+Holiday\s+(start|end)\s+date",
                label,
                re.IGNORECASE,
            )
            if holiday_match:
                term, year, boundary = holiday_match.groups()
                school_holiday_boundaries[(int(year), int(term))][boundary.lower()] = parsed

            term_match = re.search(
                r"Term\s+(\d)\s+(\d{4})\s+-\s+(Start|End)\s+date",
                label,
                re.IGNORECASE,
            )
            if term_match:
                term, year, boundary = term_match.groups()
                boundary_key = boundary.lower()
                current_value = school_term_boundaries[(int(year), int(term))].get(boundary_key)
                if current_value is None:
                    school_term_boundaries[(int(year), int(term))][boundary_key] = parsed
                elif boundary_key == "start":
                    school_term_boundaries[(int(year), int(term))][boundary_key] = min(
                        current_value, parsed
                    )
                else:
                    school_term_boundaries[(int(year), int(term))][boundary_key] = max(
                        current_value, parsed
                    )

    for (year, term_number), boundaries in school_holiday_boundaries.items():
        start = boundaries.get("start")
        end = boundaries.get("end")
        if start is None and end is not None and year < 2025:
            start = STUDY_START.date()
        if start is not None and end is None and year == 2025:
            end = STUDY_END.date()
        if start is not None and end is not None:
            label = f"School holiday: Term {term_number} {year}"
            add_date_range(
                calendar,
                start,
                end,
                "is_school_holiday",
                label,
                "school_related_labels",
            )

    for (year, term_number), boundaries in school_term_boundaries.items():
        start = boundaries.get("start")
        end = boundaries.get("end")
        if start is not None and end is not None:
            label = f"School term: Term {term_number} {year}"
            add_date_range(
                calendar,
                start,
                end,
                "is_school_term",
                label,
                "school_related_labels",
            )

    for context in calendar.values():
        for field in ("calendar_labels", "school_related_labels", "daylight_saving_labels"):
            context[field] = unique_nonempty(context[field])

    diagnostics = {
        "calendar_source_explicit_2025_dates": len(explicit_2025_dates),
        "calendar_matched_date_count": sum(
            1
            for context in calendar.values()
            if context["calendar_labels"]
            or context["is_school_holiday"]
            or context["is_school_term"]
        ),
    }
    return calendar, diagnostics


def parse_event_confidence(value: str | None) -> float | None:
    if not value or not value.strip():
        return None
    numeric = parse_float(value)
    if numeric is not None:
        return max(0.0, min(numeric, 1.0))
    mapping = {"low": 0.35, "medium": 0.6, "high": 0.85}
    return mapping.get(value.strip().lower())


def read_manual_events() -> list[dict[str, Any]]:
    if not MANUAL_EVENTS_FILE.exists():
        return []
    events: list[dict[str, Any]] = []
    with MANUAL_EVENTS_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            event_date = parse_date(row.get("date"))
            if event_date is None:
                continue
            start = datetime.combine(
                event_date, parse_time(row.get("start_time"), time.min)
            )
            end = datetime.combine(
                event_date, parse_time(row.get("end_time"), time(23, 59, 59))
            )
            if end < start:
                end += timedelta(days=1)
            events.append(
                {
                    **row,
                    "start": start,
                    "end": end,
                    "confidence_value": parse_event_confidence(row.get("confidence")),
                }
            )
    return events


def events_for_hour(events: list[dict[str, Any]], value: datetime) -> list[dict[str, Any]]:
    hour_end = value + timedelta(hours=1)
    return [event for event in events if event["start"] < hour_end and event["end"] >= value]


def build_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    sensors = read_sensors()
    observations = read_pedestrian_observations()
    weather = read_weather()
    calendar, calendar_diagnostics = read_calendar()
    events = read_manual_events()

    rows: list[dict[str, Any]] = []
    current = STUDY_START
    while current <= STUDY_END:
        timestamp_key = hour_key(current)
        date_key = current.date().isoformat()
        weather_record = weather.get(timestamp_key)
        calendar_record = calendar[date_key]
        matching_events = events_for_hour(events, current)

        for sensor_id in SELECTED_SENSOR_IDS:
            observation = observations.get((timestamp_key, sensor_id))
            source_hour_present = observation is not None
            observed_count = observation["observed_count"] if observation else None
            is_missing = observed_count is None
            event_confidences = [
                event["confidence_value"]
                for event in matching_events
                if event["confidence_value"] is not None
            ]
            source_ids = [
                "pedestrian_counts",
                "pedestrian_sensors",
                "victoria_important_dates",
            ]
            if weather_record is not None:
                source_ids.append("open_meteo_weather_json")
            if matching_events:
                source_ids.append("manual_events")

            row = {
                "timestamp": local_iso(current),
                "local_timestamp_key": timestamp_key,
                "date": date_key,
                "hour": current.hour,
                "weekday": current.strftime("%A"),
                "timezone": "Australia/Melbourne",
                **sensors[sensor_id],
                "source_record_id": observation["source_record_id"] if observation else "",
                "observed_count": observed_count,
                "direction_1_count": observation["direction_1_count"] if observation else None,
                "direction_2_count": observation["direction_2_count"] if observation else None,
                "is_missing": is_missing,
                "missing_reason": "source_hour_absent" if not source_hour_present else (
                    "source_count_missing" if is_missing else ""
                ),
                "source_hour_present": source_hour_present,
                "temperature_2m": weather_record.get("temperature_2m") if weather_record else None,
                "apparent_temperature": (
                    weather_record.get("apparent_temperature") if weather_record else None
                ),
                "relative_humidity_2m": (
                    weather_record.get("relative_humidity_2m") if weather_record else None
                ),
                "precipitation": weather_record.get("precipitation") if weather_record else None,
                "rain": weather_record.get("rain") if weather_record else None,
                "wind_speed_10m": weather_record.get("wind_speed_10m") if weather_record else None,
                "weather_code": weather_record.get("weather_code") if weather_record else None,
                **calendar_record,
                "manual_event_ids": unique_nonempty(
                    [event.get("event_id", "") for event in matching_events]
                ),
                "manual_event_names": unique_nonempty(
                    [event.get("event_name", "") for event in matching_events]
                ),
                "manual_event_types": unique_nonempty(
                    [event.get("event_type", "") for event in matching_events]
                ),
                "manual_event_source_urls": unique_nonempty(
                    [event.get("source_url", "") for event in matching_events]
                ),
                "manual_event_expected_effects": unique_nonempty(
                    [event.get("expected_effect", "") for event in matching_events]
                ),
                "manual_event_notes": " | ".join(
                    unique_nonempty([event.get("notes", "") for event in matching_events])
                ),
                "source_dataset_ids": source_ids,
                "processing_stage": PROCESSING_STAGE,
                "processing_version": PROCESSING_VERSION,
                "observation_confidence": 0.0 if is_missing else (
                    0.9 if sensors[sensor_id]["sensor_status"] == "A" else 0.65
                ),
                "weather_confidence": 0.9 if weather_record is not None else 0.0,
                "calendar_confidence": 0.8,
                "event_confidence": max(event_confidences) if event_confidences else (
                    0.0 if matching_events else None
                ),
            }
            rows.append(row)
        current += timedelta(hours=1)

    diagnostics = {
        **calendar_diagnostics,
        "manual_event_records_loaded": len(events),
        "source_observation_records_loaded": len(observations),
        "weather_hourly_records_loaded": len(weather),
    }
    return rows, diagnostics


def csv_value(field: str, value: Any) -> Any:
    if field in LIST_FIELDS:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value).lower()
    return value


def write_outputs(rows: list[dict[str, Any]]) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0])
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_value(field, row[field]) for field in fieldnames})

    with JSON_OUTPUT.open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def main() -> None:
    rows, diagnostics = build_rows()
    write_outputs(rows)
    expected_rows = 8760 * len(SELECTED_SENSOR_IDS)
    if len(rows) != expected_rows:
        raise ValueError(f"Expected {expected_rows} rows, generated {len(rows)}")
    print(
        json.dumps(
            {
                "processing_stage": PROCESSING_STAGE,
                "rows": len(rows),
                "expected_rows": expected_rows,
                "selected_sensors": list(SELECTED_SENSOR_IDS),
                "manual_event_records_loaded": diagnostics["manual_event_records_loaded"],
                "calendar_matched_date_count": diagnostics["calendar_matched_date_count"],
                "csv_output": str(CSV_OUTPUT),
                "json_output": str(JSON_OUTPUT),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
