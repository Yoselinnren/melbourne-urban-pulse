"""Classify Phase 1A contexts and regular-baseline eligibility.

This stage reads the canonical CSV panel. It intentionally does not calculate
baseline distributions, normalised scores, or anomaly candidates.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
INPUT_CSV = PROCESSED_DIR / "analytical_hourly_panel.csv"
CSV_OUTPUT = PROCESSED_DIR / "context_classified_panel.csv"
JSON_OUTPUT = PROCESSED_DIR / "context_classified_panel.json"
DIAGNOSTICS_OUTPUT = PROCESSED_DIR / "phase1a_diagnostics.json"

PROCESSING_STAGE = "context_classification"
PROCESSING_VERSION = "phase1a-0.1.0"
SELECTED_SENSOR_IDS = ("4", "3", "133")
EXPECTED_HOURS = 8760
EXPECTED_ROWS = EXPECTED_HOURS * len(SELECTED_SENSOR_IDS)

# Provisional Phase 1A context rule; it is context, not causal evidence.
WEATHER_DISRUPTION_RAIN_THRESHOLD = 0.0
WEATHER_DISRUPTION_WIND_THRESHOLD = 30.0
LOW_CONFIDENCE_OBSERVATION_THRESHOLD = 0.5

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
    "context_tags",
    "baseline_exclusion_reasons",
}
BOOLEAN_FIELDS = {
    "is_missing",
    "source_hour_present",
    "is_weekend",
    "is_public_holiday",
    "is_school_term",
    "is_school_holiday",
    "is_daylight_saving_transition",
}
FLOAT_FIELDS = {
    "latitude",
    "longitude",
    "temperature_2m",
    "apparent_temperature",
    "relative_humidity_2m",
    "precipitation",
    "rain",
    "wind_speed_10m",
    "weather_code",
    "observation_confidence",
    "weather_confidence",
    "calendar_confidence",
    "event_confidence",
}
INT_FIELDS = {"hour", "observed_count", "direction_1_count", "direction_2_count"}

PRIMARY_CONTEXT_PRECEDENCE = (
    "low_confidence_observation",
    "manual_event_window",
    "public_holiday",
    "daylight_saving_transition",
    "weather_disruption",
    "planned_work_context",
    "school_holiday",
    "regular_weekend",
    "regular_weekday",
)


def parse_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def parse_float(value: str) -> float | None:
    if value.strip() == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_int(value: str) -> int | None:
    if value.strip() == "":
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def parse_list(value: str) -> list[str]:
    if not value.strip():
        return []
    parsed = json.loads(value)
    if not isinstance(parsed, list):
        raise ValueError(f"Expected a JSON list, received: {value}")
    return [str(item) for item in parsed]


def read_panel() -> list[dict[str, Any]]:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(
            f"{INPUT_CSV} does not exist. Run build_analytical_panel.py first."
        )
    rows: list[dict[str, Any]] = []
    with INPUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        for raw in csv.DictReader(handle):
            row: dict[str, Any] = dict(raw)
            for field in LIST_FIELDS.intersection(row):
                row[field] = parse_list(raw[field])
            for field in BOOLEAN_FIELDS.intersection(row):
                row[field] = parse_bool(raw[field])
            for field in FLOAT_FIELDS.intersection(row):
                row[field] = parse_float(raw[field])
            for field in INT_FIELDS.intersection(row):
                row[field] = parse_int(raw[field])
            rows.append(row)
    return rows


def classify_row(row: dict[str, Any]) -> dict[str, Any]:
    tags: list[str] = []
    exclusions: list[str] = []

    missing = bool(row["is_missing"])
    observation_confidence = row.get("observation_confidence") or 0.0
    low_confidence = missing or observation_confidence < LOW_CONFIDENCE_OBSERVATION_THRESHOLD
    rain = row.get("rain")
    wind = row.get("wind_speed_10m")
    weather_disruption = (
        (rain is not None and rain > WEATHER_DISRUPTION_RAIN_THRESHOLD)
        or (wind is not None and wind >= WEATHER_DISRUPTION_WIND_THRESHOLD)
    )
    has_manual_event = bool(row.get("manual_event_ids") or row.get("manual_event_names"))

    tags.append("regular_weekend" if row["is_weekend"] else "regular_weekday")
    if row["is_public_holiday"]:
        tags.append("public_holiday")
        exclusions.append("public_holiday")
    if row["is_school_holiday"]:
        tags.append("school_holiday")
    if row["is_daylight_saving_transition"]:
        tags.append("daylight_saving_transition")
        exclusions.append("daylight_saving_transition")
    if weather_disruption:
        tags.append("weather_disruption")
        exclusions.append("weather_disruption")
    if has_manual_event:
        tags.append("manual_event_window")
        exclusions.append("manual_event_window")
    # Planned works are deliberately inactive until validation is implemented.
    if low_confidence:
        tags.append("low_confidence_observation")
        exclusions.append("missing_observation" if missing else "low_confidence_observation")

    primary_context = next(tag for tag in PRIMARY_CONTEXT_PRECEDENCE if tag in tags)
    eligible = not exclusions

    confidence_components = [
        value
        for value in (
            row.get("observation_confidence"),
            row.get("weather_confidence"),
            row.get("calendar_confidence"),
        )
        if value is not None
    ]
    if has_manual_event and row.get("event_confidence") is not None:
        confidence_components.append(row["event_confidence"])
    context_confidence = (
        round(sum(confidence_components) / len(confidence_components), 3)
        if confidence_components
        else 0.0
    )

    return {
        **row,
        "context_tags": tags,
        "primary_context": primary_context,
        "is_regular_baseline_eligible": eligible,
        "baseline_exclusion_reasons": exclusions,
        "context_confidence": context_confidence,
        "processing_stage": PROCESSING_STAGE,
        "processing_version": PROCESSING_VERSION,
    }


def csv_value(field: str, value: Any) -> Any:
    if field in LIST_FIELDS:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value).lower()
    return value


def write_panels(rows: list[dict[str, Any]]) -> None:
    fieldnames = list(rows[0])
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_value(field, row[field]) for field in fieldnames})

    with JSON_OUTPUT.open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def build_diagnostics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    missing_by_sensor: Counter[str] = Counter()
    tag_counts: Counter[str] = Counter()
    exclusion_counts: Counter[str] = Counter()
    sensor_row_counts: Counter[str] = Counter()
    dates_with_calendar_match: set[str] = set()
    manual_event_ids: set[str] = set()
    warnings: list[str] = []

    weather_missing_count = 0
    eligible_count = 0
    for row in rows:
        sensor_id = row["sensor_id"]
        sensor_row_counts[sensor_id] += 1
        if row["is_missing"]:
            missing_by_sensor[sensor_id] += 1
        if row.get("temperature_2m") is None:
            weather_missing_count += 1
        if row.get("calendar_labels") or row.get("is_school_term") or row.get("is_school_holiday"):
            dates_with_calendar_match.add(row["date"])
        manual_event_ids.update(row.get("manual_event_ids", []))
        tag_counts.update(row["context_tags"])
        exclusion_counts.update(row["baseline_exclusion_reasons"])
        if row["is_regular_baseline_eligible"]:
            eligible_count += 1

    unique_timestamps = {row["local_timestamp_key"] for row in rows}
    sensors = sorted(sensor_row_counts)
    if len(rows) != EXPECTED_ROWS:
        warnings.append(f"Expected {EXPECTED_ROWS} rows but found {len(rows)}.")
    if len(unique_timestamps) != EXPECTED_HOURS:
        warnings.append(
            f"Expected {EXPECTED_HOURS} hourly timestamps but found {len(unique_timestamps)}."
        )
    unexpected_sensors = sorted(set(sensors) - set(SELECTED_SENSOR_IDS))
    if unexpected_sensors:
        warnings.append(f"Unexpected sensors present: {', '.join(unexpected_sensors)}.")
    if weather_missing_count:
        warnings.append(f"{weather_missing_count} rows have missing hourly weather context.")

    warnings.extend(
        [
            "Weather disruption uses a provisional rule: rain > 0 or wind_speed_10m >= 30.",
            "School holidays are tagged but are not automatically excluded from regular baselines.",
            "Planned works are not active: date range, status, and spatial relevance validation is not implemented.",
            "Confidence components are simple Phase 1A reliability indicators and are not activity scores.",
        ]
    )

    return {
        "processing_version": PROCESSING_VERSION,
        "study_period": {
            "start": "2025-01-01T00:00:00",
            "end": "2025-12-31T23:00:00",
            "timezone": "Australia/Melbourne",
        },
        "row_count": len(rows),
        "expected_row_count": EXPECTED_ROWS,
        "selected_sensor_count": len(sensors),
        "selected_sensor_ids": sensors,
        "hourly_timestamp_count": len(unique_timestamps),
        "expected_hourly_timestamp_count": EXPECTED_HOURS,
        "sensor_row_counts": dict(sorted(sensor_row_counts.items())),
        "missing_observation_count": sum(missing_by_sensor.values()),
        "missing_observation_counts_by_sensor": dict(sorted(missing_by_sensor.items())),
        "weather_missing_count": weather_missing_count,
        "calendar_matched_date_count": len(dates_with_calendar_match),
        "manual_event_records_loaded": len(manual_event_ids),
        "manual_event_ids_loaded": sorted(manual_event_ids),
        "context_tag_counts": dict(sorted(tag_counts.items())),
        "regular_baseline_eligible_count": eligible_count,
        "regular_baseline_ineligible_count": len(rows) - eligible_count,
        "baseline_exclusion_reason_counts": dict(sorted(exclusion_counts.items())),
        "planned_works_status": "not_active_pending_date_status_spatial_validation",
        "configuration": {
            "weather_disruption_rule": "rain > 0 OR wind_speed_10m >= 30",
            "low_confidence_observation_threshold": LOW_CONFIDENCE_OBSERVATION_THRESHOLD,
            "primary_context_precedence": list(PRIMARY_CONTEXT_PRECEDENCE),
            "school_holiday_baseline_policy": "tag_only_not_automatically_excluded",
        },
        "warnings": warnings,
    }


def main() -> None:
    source_rows = read_panel()
    rows = [classify_row(row) for row in source_rows]
    write_panels(rows)
    diagnostics = build_diagnostics(rows)
    with DIAGNOSTICS_OUTPUT.open("w", encoding="utf-8") as handle:
        json.dump(diagnostics, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps(diagnostics, indent=2))


if __name__ == "__main__":
    main()
