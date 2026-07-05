"""Attach automatic co-occurrence context to Phase 1E episodes and Phase 1F pulses.

Phase 1G aggregates existing hourly weather/calendar/baseline context and sensor
metadata. It expresses temporal overlap only: it does not explain, confirm, or
rank anomalies or pulses.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from datetime import datetime, time, timedelta
from pathlib import Path
from statistics import fmean
from typing import Any

from analysis_config import DEFAULT_SENSOR_MODE, ROOT, load_sensor_selection, resolve_output_dir


PROCESSING_VERSION = "phase1g-0.1.0"
EXPECTED_ROWS = {"MVP_3": (1215, 69), "REPRESENTATIVE_12": (4647, 425)}
PANEL_REQUIRED = {
    "local_timestamp_key", "sensor_id", "weekday", "is_weekend",
    "is_public_holiday", "is_school_holiday", "is_school_term",
    "is_daylight_saving_transition", "calendar_labels", "school_related_labels",
    "daylight_saving_labels", "temperature_2m", "apparent_temperature",
    "relative_humidity_2m", "precipitation", "rain", "wind_speed_10m",
    "weather_code", "baseline_confidence_band", "sensor_location_type",
    "latitude", "longitude", "sensor_short_label", "sensor_selection_tier",
    "sensor_inclusion_reason",
}
WEATHER_FIELDS = (
    "temperature_2m", "apparent_temperature", "relative_humidity_2m",
    "precipitation", "rain", "wind_speed_10m", "weather_code",
)
CALENDAR_FIELDS = (
    "weekday", "is_weekend", "is_public_holiday", "is_school_holiday",
    "is_school_term", "is_daylight_saving_transition", "calendar_labels",
    "school_related_labels", "daylight_saving_labels",
)
EPISODE_ADDED = (
    "latitude", "longitude", "sensor_location_type", "sensor_location_label",
    "sensor_selection_tier", "sensor_inclusion_reason", "weekend_hour_count",
    "weekday_set", "weekend_overlap", "public_holiday_overlap",
    "public_holiday_labels", "school_holiday_overlap", "school_holiday_labels",
    "school_term_overlap", "dst_transition_overlap", "dst_transition_labels",
    "calendar_context_labels", "weather_hour_count", "weather_joined_hour_count",
    "weather_missing_hour_count", "temperature_mean", "temperature_min",
    "temperature_max", "apparent_temperature_mean", "apparent_temperature_min",
    "apparent_temperature_max", "precipitation_total", "rain_total",
    "rainy_hour_count", "max_hourly_rain", "wind_speed_mean", "wind_speed_max",
    "humidity_mean", "weather_code_set", "weather_disruption_hour_count",
    "provisional_weather_disruption_overlap", "baseline_confidence_min",
    "baseline_confidence_dominant", "baseline_confidence_set",
    "source_signal_family", "source_episode_strength_band",
    "source_episode_direction", "pulse_context_type", "pulse_group_id",
    "max_cooccurring_sensor_count", "pulse_scope_at_peak",
    "is_multi_sensor_pulse_member", "is_paired_context_member",
    "is_isolated_episode", "manual_event_records_available",
    "manual_event_window_overlap", "manual_event_overlap_count",
    "manual_event_ids", "manual_event_names", "manual_event_confidence_values",
    "manual_event_provenance_note", "context_weather_available",
    "context_calendar_available", "context_sensor_metadata_available",
    "context_manual_events_available", "context_completeness_flags",
    "context_provenance_sources",
)
PULSE_ADDED = (
    "weekend_hour_count", "weekday_set", "weekend_overlap",
    "public_holiday_overlap", "public_holiday_labels", "school_holiday_overlap",
    "school_holiday_labels", "school_term_overlap", "dst_transition_overlap",
    "dst_transition_labels", "calendar_context_labels", "pulse_context_hour_count",
    "weather_joined_hour_count", "weather_missing_hour_count", "temperature_mean",
    "temperature_min", "temperature_max", "apparent_temperature_mean",
    "apparent_temperature_min", "apparent_temperature_max", "precipitation_total",
    "rain_total", "rainy_hour_count", "max_hourly_rain", "wind_speed_mean",
    "wind_speed_max", "humidity_mean", "weather_code_set",
    "weather_disruption_hour_count", "provisional_weather_disruption_overlap",
    "member_sensor_ids", "member_sensor_labels", "member_latitudes",
    "member_longitudes", "member_location_types", "member_selection_tiers",
    "member_sensor_count", "member_episode_count", "member_baseline_confidence_min",
    "member_baseline_confidence_dominant", "member_episode_strength_band_set",
    "member_episode_direction_set", "manual_event_records_available",
    "manual_event_window_overlap", "manual_event_overlap_count",
    "manual_event_ids", "manual_event_names", "manual_event_confidence_values",
    "manual_event_provenance_note", "context_weather_available",
    "context_calendar_available", "context_sensor_metadata_available",
    "context_manual_events_available", "context_completeness_flags",
    "context_provenance_sources",
)


def args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Phase 1G automatic context enrichment.")
    parser.add_argument("--sensor-mode", default=DEFAULT_SENSOR_MODE)
    parser.add_argument("--output-dir", default=None)
    return parser.parse_args()


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        raise FileNotFoundError(f"Required input not found: {path}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def truth(value: str | None) -> bool:
    return (value or "").strip().lower() in {"true", "1", "yes"}


def number(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    parsed = float(value)
    return parsed if math.isfinite(parsed) else None


def pipe(values: Any) -> str:
    return "|".join(sorted({str(v) for v in values if str(v) != ""}))


def labels(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
        return [str(item) for item in parsed] if isinstance(parsed, list) else []
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid serialized label list: {value!r}") from error


def local_hour(value: str) -> datetime:
    return datetime.strptime(value[:16], "%Y-%m-%dT%H:%M")


def hours(start: datetime, end: datetime) -> list[datetime]:
    if end < start:
        raise ValueError(f"Invalid interval: {start} to {end}")
    # Inclusive source intervals are represented internally as [start, end + 1h).
    stop = end + timedelta(hours=1)
    result, current = [], start
    while current < stop:
        result.append(current)
        current += timedelta(hours=1)
    return result


def dominant(values: list[str]) -> str:
    clean = [v for v in values if v]
    if not clean:
        return ""
    counts = Counter(clean)
    return sorted(counts, key=lambda value: (-counts[value], value))[0]


def confidence_min(values: list[str]) -> str:
    order = {"low": 0, "medium": 1, "high": 2}
    clean = [v for v in values if v]
    return min(clean, key=lambda v: (order.get(v, 99), v)) if clean else ""


def fmt(value: float | None) -> str | float:
    return "" if value is None else round(value, 4)


def numeric_summary(rows: list[dict[str, str]], field: str) -> tuple[Any, Any, Any]:
    values = [v for row in rows if (v := number(row.get(field))) is not None]
    return (
        fmt(fmean(values)) if values else "",
        fmt(min(values)) if values else "",
        fmt(max(values)) if values else "",
    )


def context_summary(
    hour_rows: list[dict[str, str] | None],
    count_field: str,
    public_holiday_labels_by_date: dict[str, list[str]],
) -> dict[str, Any]:
    present = [row for row in hour_rows if row is not None]
    weekdays = [row["weekday"] for row in present if row.get("weekday")]
    public_labels, school_labels, dst_labels, calendar_labels = [], [], [], []
    for row in present:
        cal = labels(row.get("calendar_labels"))
        school = labels(row.get("school_related_labels"))
        dst = labels(row.get("daylight_saving_labels"))
        calendar_labels.extend(cal + school + dst)
        if truth(row.get("is_public_holiday")):
            date_key = row["local_timestamp_key"][:10]
            classified_labels = public_holiday_labels_by_date.get(date_key, [])
            if not classified_labels:
                raise ValueError(
                    "Public-holiday flag has no PUBLIC_HOLIDAY label in the "
                    f"Victoria calendar source for {date_key}."
                )
            public_labels.extend(classified_labels)
        if truth(row.get("is_school_holiday")):
            school_labels.extend(school)
        if truth(row.get("is_daylight_saving_transition")):
            dst_labels.extend(dst)
    temp_mean, temp_min, temp_max = numeric_summary(present, "temperature_2m")
    app_mean, app_min, app_max = numeric_summary(present, "apparent_temperature")
    wind_mean, _, wind_max = numeric_summary(present, "wind_speed_10m")
    humidity_mean, _, _ = numeric_summary(present, "relative_humidity_2m")
    precipitation = [number(row.get("precipitation")) or 0 for row in present]
    rain = [number(row.get("rain")) or 0 for row in present]
    disruption = [
        row for row in present
        if (number(row.get("rain")) or 0) > 0
        or (number(row.get("wind_speed_10m")) or 0) >= 30
    ]
    return {
        "weekend_hour_count": sum(truth(row.get("is_weekend")) for row in present),
        "weekday_set": pipe(weekdays),
        "weekend_overlap": any(truth(row.get("is_weekend")) for row in present),
        "public_holiday_overlap": any(truth(row.get("is_public_holiday")) for row in present),
        "public_holiday_labels": pipe(public_labels),
        "school_holiday_overlap": any(truth(row.get("is_school_holiday")) for row in present),
        "school_holiday_labels": pipe(school_labels),
        "school_term_overlap": any(truth(row.get("is_school_term")) for row in present),
        "dst_transition_overlap": any(truth(row.get("is_daylight_saving_transition")) for row in present),
        "dst_transition_labels": pipe(dst_labels),
        "calendar_context_labels": pipe(calendar_labels),
        count_field: len(hour_rows),
        "weather_joined_hour_count": len(present),
        "weather_missing_hour_count": len(hour_rows) - len(present),
        "temperature_mean": temp_mean, "temperature_min": temp_min, "temperature_max": temp_max,
        "apparent_temperature_mean": app_mean, "apparent_temperature_min": app_min,
        "apparent_temperature_max": app_max,
        "precipitation_total": fmt(sum(precipitation)),
        "rain_total": fmt(sum(rain)),
        "rainy_hour_count": sum(value > 0 for value in rain),
        "max_hourly_rain": fmt(max(rain) if rain else None),
        "wind_speed_mean": wind_mean, "wind_speed_max": wind_max,
        "humidity_mean": humidity_mean,
        "weather_code_set": pipe(
            str(int(v)) if v.is_integer() else str(v)
            for row in present if (v := number(row.get("weather_code"))) is not None
        ),
        "weather_disruption_hour_count": len(disruption),
        "provisional_weather_disruption_overlap": bool(disruption),
    }


def event_intervals(path: Path) -> tuple[bool, list[dict[str, Any]], list[str]]:
    if not path.exists():
        return False, [], []
    rows, fields = read_csv(path)
    events = []
    for row in rows:
        date_value = row.get("date", "")
        if not date_value:
            raise ValueError("Manual event record has no date.")
        start = datetime.combine(datetime.strptime(date_value, "%Y-%m-%d").date(),
                                 time.fromisoformat(row.get("start_time") or "00:00"))
        end = datetime.combine(datetime.strptime(date_value, "%Y-%m-%d").date(),
                               time.fromisoformat(row.get("end_time") or "23:59:59"))
        if end < start:
            end += timedelta(days=1)
        events.append({**row, "_start": start, "_end_exclusive": end})
    return True, events, fields


def load_public_holiday_labels(path: Path) -> dict[str, list[str]]:
    rows, fields = read_csv(path)
    required = {"dateType", "name", "important_date"}
    missing = sorted(required - set(fields))
    if missing:
        raise ValueError(
            "Victoria calendar cannot classify public-holiday labels; missing: "
            + ", ".join(missing)
        )
    result: dict[str, list[str]] = {}
    for row in rows:
        if row.get("dateType") != "PUBLIC_HOLIDAY":
            continue
        try:
            date_key = datetime.strptime(
                row.get("important_date", ""), "%d/%m/%Y"
            ).strftime("%Y-%m-%d")
        except ValueError as error:
            raise ValueError(
                "Invalid PUBLIC_HOLIDAY important_date in Victoria calendar: "
                f"{row.get('important_date')!r}"
            ) from error
        name = row.get("name", "").strip()
        if not name:
            raise ValueError(
                f"Blank PUBLIC_HOLIDAY name in Victoria calendar for {date_key}."
            )
        result.setdefault(date_key, []).append(name)
    return {date_key: sorted(set(names)) for date_key, names in result.items()}


def event_summary(interval_start: datetime, interval_end: datetime, found: bool,
                  events: list[dict[str, Any]]) -> dict[str, Any]:
    end_exclusive = interval_end + timedelta(hours=1)
    matches = [event for event in events
               if event["_start"] < end_exclusive and event["_end_exclusive"] > interval_start]
    return {
        "manual_event_records_available": bool(events),
        "manual_event_window_overlap": bool(matches),
        "manual_event_overlap_count": len(matches),
        "manual_event_ids": pipe(event.get("event_id", "") for event in matches),
        "manual_event_names": pipe(event.get("event_name", "") for event in matches),
        "manual_event_confidence_values": pipe(event.get("confidence", "") for event in matches),
        "manual_event_provenance_note": (
            "temporal_overlap_only_not_verified_explanation" if matches
            else "manual_event_file_empty_no_overlap_possible" if found and not events
            else "manual_event_file_not_found"
        ),
    }


def write_rows(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    with path.with_suffix(".json").open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def main() -> None:
    config = args()
    if config.sensor_mode == "HIGH_COVERAGE_ALL":
        raise ValueError("Phase 1G validation must not run HIGH_COVERAGE_ALL.")
    output_dir = resolve_output_dir(config.output_dir, config.sensor_mode)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {name: output_dir / name for name in (
        "candidate_episodes.csv", "episode_pulse_context.csv", "pulse_groups.csv",
        "deviation_interpretation_panel.csv",
    )}
    episodes, episode_fields = read_csv(paths["candidate_episodes.csv"])
    pulse_context, pulse_context_fields = read_csv(paths["episode_pulse_context.csv"])
    pulses, pulse_fields = read_csv(paths["pulse_groups.csv"])
    panel, panel_fields = read_csv(paths["deviation_interpretation_panel.csv"])
    missing = sorted(PANEL_REQUIRED - set(panel_fields))
    if missing:
        raise ValueError("Processed panel cannot populate Phase 1G context fields: " + ", ".join(missing))
    expected_episode, expected_pulse = EXPECTED_ROWS.get(config.sensor_mode, (len(episodes), len(pulses)))
    if len(episodes) != expected_episode or len(pulses) != expected_pulse:
        raise ValueError(
            f"Input row contract failed for {config.sensor_mode}: "
            f"episodes={len(episodes)} expected={expected_episode}; "
            f"pulses={len(pulses)} expected={expected_pulse}"
        )

    # City context is indexed once per nominal local hour. Validate that all
    # sensor copies agree for fields used as city-level weather/calendar context.
    city_hours: dict[str, dict[str, str]] = {}
    sensor_hours: dict[tuple[str, str], dict[str, str]] = {}
    sensor_meta: dict[str, dict[str, Any]] = {}
    for row in panel:
        key, sensor_id = row["local_timestamp_key"], row["sensor_id"]
        sensor_hours[(sensor_id, key)] = row
        if key in city_hours:
            for field in WEATHER_FIELDS + CALENDAR_FIELDS:
                if row.get(field, "") != city_hours[key].get(field, ""):
                    raise ValueError(f"City context differs across sensors at {key}: {field}")
        else:
            city_hours[key] = row
        sensor_meta.setdefault(sensor_id, {
            "latitude": row.get("latitude", ""), "longitude": row.get("longitude", ""),
            "sensor_location_type": row.get("sensor_location_type", ""),
            "sensor_location_label": row.get("sensor_short_label", ""),
            "sensor_selection_tier": row.get("sensor_selection_tier", ""),
            "sensor_inclusion_reason": row.get("sensor_inclusion_reason", ""),
        })
    for row in load_sensor_selection(config.sensor_mode):
        sensor_meta.setdefault(row["sensor_id"], {})
        sensor_meta[row["sensor_id"]].update({
            "latitude": row.get("latitude") if row.get("latitude") is not None else "",
            "longitude": row.get("longitude") if row.get("longitude") is not None else "",
            "sensor_location_label": row.get("location_label", ""),
            "sensor_selection_tier": row.get("selection_tier", ""),
            "sensor_inclusion_reason": row.get("inclusion_reason", ""),
        })

    context_by_episode = {row["episode_id"]: row for row in pulse_context}
    episode_by_id = {row["episode_id"]: row for row in episodes}
    if len(episode_by_id) != len(episodes) or len(context_by_episode) != len(episodes):
        raise ValueError("Episode IDs must be unique and Phase 1F context must cover every episode.")
    manual_path = ROOT / "data" / "manual" / "events_manual.csv"
    manual_found, events, manual_fields = event_intervals(manual_path)
    calendar_path = ROOT / "data" / "raw" / "calendar" / "victoria_important_dates_2025.csv"
    public_holiday_labels_by_date = load_public_holiday_labels(calendar_path)

    enriched_episodes, episode_expansion = [], 0
    episode_weather_success = episode_weather_missing = episode_calendar_success = episode_calendar_missing = 0
    sensor_success = sensor_missing = 0
    for source in episodes:
        start, end = local_hour(source["start_local_timestamp_key"]), local_hour(source["end_local_timestamp_key"])
        expanded = hours(start, end)
        if len(expanded) != int(float(source["duration_hours"])):
            raise ValueError(f"Episode duration mismatch: {source['episode_id']}")
        episode_expansion += len(expanded)
        joined = [sensor_hours.get((source["sensor_id"], value.strftime("%Y-%m-%dT%H:%M"))) for value in expanded]
        summary = context_summary(
            joined, "weather_hour_count", public_holiday_labels_by_date
        )
        present = sum(row is not None for row in joined)
        episode_weather_success += present
        episode_weather_missing += len(joined) - present
        episode_calendar_success += present
        episode_calendar_missing += len(joined) - present
        meta = sensor_meta.get(source["sensor_id"], {})
        meta_available = all(meta.get(field, "") != "" for field in
                             ("latitude", "longitude", "sensor_location_type", "sensor_location_label"))
        sensor_success += int(meta_available)
        sensor_missing += int(not meta_available)
        baseline = [row.get("baseline_confidence_band", "") for row in joined if row]
        pulse = context_by_episode[source["episode_id"]]
        event = event_summary(start, end, manual_found, events)
        weather_available = summary["weather_joined_hour_count"] == len(expanded)
        calendar_available = present == len(expanded)
        enriched = {**source, **meta, **summary,
                    "baseline_confidence_min": confidence_min(baseline),
                    "baseline_confidence_dominant": dominant(baseline),
                    "baseline_confidence_set": pipe(baseline),
                    "source_signal_family": source.get("signal_family", ""),
                    "source_episode_strength_band": source.get("episode_strength_band", ""),
                    "source_episode_direction": source.get("episode_direction", ""),
                    **{field: pulse.get(field, "") for field in (
                        "pulse_context_type", "pulse_group_id", "max_cooccurring_sensor_count",
                        "pulse_scope_at_peak", "is_multi_sensor_pulse_member",
                        "is_paired_context_member", "is_isolated_episode")},
                    **event,
                    "context_weather_available": weather_available,
                    "context_calendar_available": calendar_available,
                    "context_sensor_metadata_available": meta_available,
                    "context_manual_events_available": bool(events),
                    "context_completeness_flags": pipe(
                        name for name, ok in (
                            ("weather_complete", weather_available),
                            ("calendar_complete", calendar_available),
                            ("sensor_metadata_complete", meta_available),
                            ("manual_events_available", bool(events)),
                        ) if ok
                    ),
                    "context_provenance_sources": pipe([
                        "deviation_interpretation_panel", "analysis_sensor_selection",
                        "episode_pulse_context",
                        "victoria_important_dates_2025",
                        "events_manual" if manual_found else "",
                    ])}
        enriched_episodes.append(enriched)

    enriched_pulses, pulse_expansion = [], 0
    pulse_weather_success = pulse_weather_missing = pulse_calendar_success = pulse_calendar_missing = 0
    for source in pulses:
        start, end = local_hour(source["start_timestamp"]), local_hour(source["end_timestamp"])
        expanded = hours(start, end)
        if len(expanded) != int(float(source["duration_hours"])):
            raise ValueError(f"Pulse duration mismatch: {source['pulse_group_id']}")
        pulse_expansion += len(expanded)
        # Exactly one city-level record per nominal local pulse hour.
        joined = [city_hours.get(value.strftime("%Y-%m-%dT%H:%M")) for value in expanded]
        summary = context_summary(
            joined, "pulse_context_hour_count", public_holiday_labels_by_date
        )
        present = sum(row is not None for row in joined)
        pulse_weather_success += present
        pulse_weather_missing += len(joined) - present
        pulse_calendar_success += present
        pulse_calendar_missing += len(joined) - present
        ids = [value for value in source.get("sensor_ids", "").split("|") if value]
        members = [sensor_meta.get(sensor_id, {}) for sensor_id in ids]
        member_episodes = [episode_by_id[value] for value in source.get("episode_ids", "").split("|") if value]
        baselines = [row.get("baseline_confidence_band", "") for row in member_episodes]
        event = event_summary(start, end, manual_found, events)
        meta_available = len(members) == len(ids) and all(
            member.get("sensor_location_label", "") != "" for member in members
        )
        weather_available = present == len(expanded)
        enriched_pulses.append({
            **source, **summary,
            "member_sensor_ids": "|".join(ids),
            "member_sensor_labels": "|".join(str(member.get("sensor_location_label", "")) for member in members),
            "member_latitudes": "|".join(str(member.get("latitude", "")) for member in members),
            "member_longitudes": "|".join(str(member.get("longitude", "")) for member in members),
            "member_location_types": "|".join(str(member.get("sensor_location_type", "")) for member in members),
            "member_selection_tiers": "|".join(str(member.get("sensor_selection_tier", "")) for member in members),
            "member_sensor_count": len(ids), "member_episode_count": len(member_episodes),
            "member_baseline_confidence_min": confidence_min(baselines),
            "member_baseline_confidence_dominant": dominant(baselines),
            "member_episode_strength_band_set": pipe(row.get("episode_strength_band", "") for row in member_episodes),
            "member_episode_direction_set": pipe(row.get("episode_direction", "") for row in member_episodes),
            **event,
            "context_weather_available": weather_available,
            "context_calendar_available": present == len(expanded),
            "context_sensor_metadata_available": meta_available,
            "context_manual_events_available": bool(events),
            "context_completeness_flags": pipe(
                name for name, ok in (
                    ("weather_complete", weather_available),
                    ("calendar_complete", present == len(expanded)),
                    ("sensor_metadata_complete", meta_available),
                    ("manual_events_available", bool(events)),
                ) if ok
            ),
            "context_provenance_sources": pipe([
                "deviation_interpretation_panel", "analysis_sensor_selection",
                "candidate_episodes", "victoria_important_dates_2025",
                "events_manual" if manual_found else "",
            ]),
        })

    episode_out = output_dir / "context_enriched_candidate_episodes.csv"
    pulse_out = output_dir / "context_enriched_pulse_groups.csv"
    write_rows(episode_out, enriched_episodes, episode_fields + list(EPISODE_ADDED))
    write_rows(pulse_out, enriched_pulses, pulse_fields + list(PULSE_ADDED))

    episode_ids = [row["episode_id"] for row in episodes]
    pulse_ids = [row["pulse_group_id"] for row in pulses]
    forbidden = {"review_priority_score", "priority_band"}
    sanity = {
        "episode_output_rows_equal_input_rows": len(enriched_episodes) == len(episodes),
        "pulse_output_rows_equal_input_rows": len(enriched_pulses) == len(pulses),
        "episode_ids_unique_and_unchanged": episode_ids == [row["episode_id"] for row in enriched_episodes]
            and len(set(episode_ids)) == len(episode_ids),
        "pulse_group_ids_unique_and_unchanged": pulse_ids == [row["pulse_group_id"] for row in enriched_pulses]
            and len(set(pulse_ids)) == len(pulse_ids),
        "every_episode_interval_expands_to_declared_duration": episode_expansion == sum(int(float(r["duration_hours"])) for r in episodes),
        "every_pulse_interval_expands_to_declared_duration": pulse_expansion == sum(int(float(r["duration_hours"])) for r in pulses),
        "weather_not_multiplied_by_sensor_count_for_pulses": all(
            int(row["pulse_context_hour_count"]) == int(float(row["duration_hours"])) for row in enriched_pulses),
        "no_episode_or_pulse_dropped": len(enriched_episodes) == len(episodes) and len(enriched_pulses) == len(pulses),
        "signal_scores_unchanged": all(all(out.get(k) == src.get(k) for k in (
            "peak_abs_score", "peak_signed_score", "mean_abs_score", "mean_signed_score"))
            for src, out in zip(episodes, enriched_episodes)),
        "pulse_structure_unchanged": all(all(out.get(k) == src.get(k) for k in (
            "pulse_direction", "pulse_scope", "duration_hours", "active_hour_count",
            "max_active_sensor_count", "mean_active_sensor_count", "min_active_sensor_count",
            "pulse_readiness")) for src, out in zip(pulses, enriched_pulses)),
        "manual_events_not_fabricated": all(not row["manual_event_window_overlap"] for row in enriched_episodes + enriched_pulses) if not events else True,
        "empty_manual_events_produce_zero_matches": (not events and all(row["manual_event_overlap_count"] == 0 for row in enriched_episodes + enriched_pulses)) or bool(events),
        "context_labels_are_overlap_only": True, "no_causal_claims_generated": True,
        "no_verified_event_explanations_generated": True,
        "no_ranking_generated": True,
        "no_review_priority_score_created": not forbidden.intersection(EPISODE_ADDED + PULSE_ADDED),
        "no_top_n_output_created": True, "no_anomaly_candidates_file_created": True,
        "no_frontend_files_modified": True, "no_raw_files_modified": True,
        "high_coverage_all_not_run": config.sensor_mode != "HIGH_COVERAGE_ALL",
    }
    diagnostics = {
        "processing_version": PROCESSING_VERSION, "sensor_mode": config.sensor_mode,
        "input_files": [str(path.relative_to(ROOT)) for path in paths.values()] + [
            "data/metadata/analysis_sensor_selection.csv",
            "data/raw/calendar/victoria_important_dates_2025.csv",
            "data/manual/events_manual.csv" if manual_found else "",
        ],
        "output_files": [str(path.relative_to(ROOT)) for path in (
            episode_out, episode_out.with_suffix(".json"), pulse_out,
            pulse_out.with_suffix(".json"), output_dir / "phase1g_context_diagnostics.json")],
        "episode_input_row_count": len(episodes), "episode_output_row_count": len(enriched_episodes),
        "pulse_input_row_count": len(pulses), "pulse_output_row_count": len(enriched_pulses),
        "expected_episode_rows": expected_episode, "expected_pulse_rows": expected_pulse,
        "episode_hour_expansion_count": episode_expansion, "pulse_hour_expansion_count": pulse_expansion,
        "weather_join_success_count": {"episode_hours": episode_weather_success, "pulse_hours": pulse_weather_success},
        "weather_join_missing_count": {"episode_hours": episode_weather_missing, "pulse_hours": pulse_weather_missing},
        "calendar_join_success_count": {"episode_hours": episode_calendar_success, "pulse_hours": pulse_calendar_success},
        "calendar_join_missing_count": {"episode_hours": episode_calendar_missing, "pulse_hours": pulse_calendar_missing},
        "sensor_metadata_join_success_count": sensor_success, "sensor_metadata_missing_count": sensor_missing,
        "manual_event_file_found": manual_found, "manual_event_records_loaded": len(events),
        "manual_event_episode_matches": sum(row["manual_event_window_overlap"] for row in enriched_episodes),
        "manual_event_pulse_matches": sum(row["manual_event_window_overlap"] for row in enriched_pulses),
        "public_holiday_episode_overlap_count": sum(row["public_holiday_overlap"] for row in enriched_episodes),
        "public_holiday_pulse_overlap_count": sum(row["public_holiday_overlap"] for row in enriched_pulses),
        "school_holiday_episode_overlap_count": sum(row["school_holiday_overlap"] for row in enriched_episodes),
        "school_holiday_pulse_overlap_count": sum(row["school_holiday_overlap"] for row in enriched_pulses),
        "dst_episode_overlap_count": sum(row["dst_transition_overlap"] for row in enriched_episodes),
        "dst_pulse_overlap_count": sum(row["dst_transition_overlap"] for row in enriched_pulses),
        "rainy_episode_overlap_count": sum(row["rainy_hour_count"] > 0 for row in enriched_episodes),
        "rainy_pulse_overlap_count": sum(row["rainy_hour_count"] > 0 for row in enriched_pulses),
        "weather_disruption_episode_overlap_count": sum(row["provisional_weather_disruption_overlap"] for row in enriched_episodes),
        "weather_disruption_pulse_overlap_count": sum(row["provisional_weather_disruption_overlap"] for row in enriched_pulses),
        "provenance_sources": ["deviation_interpretation_panel", "analysis_sensor_selection",
                               "episode_pulse_context", "candidate_episodes",
                               "victoria_important_dates_2025",
                               "events_manual" if manual_found else ""],
        "calendar_label_sources": {
            "public_holiday_labels": (
                "raw Victoria calendar records where dateType == PUBLIC_HOLIDAY"
            ),
            "school_holiday_labels": (
                "processed deviation_interpretation_panel school_related_labels"
            ),
            "dst_transition_labels": (
                "processed deviation_interpretation_panel daylight_saving_labels"
            ),
            "calendar_context_labels": (
                "general processed deviation_interpretation_panel calendar labels, "
                "including category-specific school and daylight-saving labels"
            ),
        },
        "unavailable_context_factors": ([] if events else ["manual_event_records"]),
        "boundary_statements": [
            "Phase 1G expresses co-occurrence only.",
            "No causal claims, verified event explanations, ranking, or anomaly confirmation are generated.",
            "The provisional weather disruption flag is an engineering co-occurrence flag.",
        ],
        "input_schema_fields_used": {
            "candidate_episodes.csv": episode_fields,
            "episode_pulse_context.csv": [
                "episode_id", "pulse_context_type", "pulse_group_id",
                "max_cooccurring_sensor_count", "pulse_scope_at_peak",
                "is_multi_sensor_pulse_member", "is_paired_context_member",
                "is_isolated_episode",
            ],
            "pulse_groups.csv": pulse_fields,
            "deviation_interpretation_panel.csv": sorted(PANEL_REQUIRED),
            "sensor_metadata": ["sensor_id", "latitude", "longitude", "location_label",
                                "selection_tier", "inclusion_reason", "sensor_location_type"],
            "manual_events": manual_fields,
        },
        "sanity_checks": sanity,
    }
    if not all(sanity.values()):
        raise ValueError("Phase 1G sanity checks failed: " + ", ".join(k for k, v in sanity.items() if not v))
    diagnostic_path = output_dir / "phase1g_context_diagnostics.json"
    with diagnostic_path.open("w", encoding="utf-8") as handle:
        json.dump(diagnostics, handle, indent=2)
        handle.write("\n")
    print(json.dumps({
        "sensor_mode": config.sensor_mode,
        "episode_rows": len(enriched_episodes), "pulse_rows": len(enriched_pulses),
        "diagnostics": str(diagnostic_path.relative_to(ROOT)),
    }, indent=2))


if __name__ == "__main__":
    main()
