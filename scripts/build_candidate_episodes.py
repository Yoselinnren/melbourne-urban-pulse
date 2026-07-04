"""Build single-sensor temporal candidate episodes from Phase 1D rows.

Phase 1E groups only row-level ``review_ready`` signals. It does not confirm
anomalies, rank episodes, infer causes, or perform cross-sensor grouping.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from statistics import fmean
from typing import Any

from analysis_config import (
    DEFAULT_SENSOR_MODE,
    ROOT,
    load_sensor_selection,
    resolve_output_dir,
)


PROCESSING_VERSION = "phase1e-0.1.0"
REQUIRED_COLUMNS = {
    "timestamp",
    "local_timestamp_key",
    "date",
    "hour",
    "weekday",
    "sensor_mode",
    "sensor_id",
    "observed_count",
    "deviation_direction",
    "deviation_magnitude_band",
    "primary_deviation_score",
    "primary_score_source",
    "signal_family",
    "signal_subtype",
    "candidate_readiness",
    "baseline_confidence_band",
    "interpretation_warning",
}
VALID_DIRECTIONS = {"above_baseline", "below_baseline"}
VALID_STRENGTH_BANDS = {"strong", "extreme"}
EPISODE_FIELDS = (
    "episode_id",
    "sensor_mode",
    "sensor_id",
    "sensor_name",
    "sensor_short_label",
    "episode_direction",
    "signal_family",
    "signal_subtype_dominant",
    "source_row_count",
    "start_timestamp",
    "end_timestamp",
    "duration_hours",
    "start_local_timestamp_key",
    "end_local_timestamp_key",
    "start_date",
    "end_date",
    "start_hour",
    "end_hour",
    "start_weekday",
    "end_weekday",
    "peak_abs_score",
    "peak_signed_score",
    "mean_abs_score",
    "mean_signed_score",
    "min_signed_score",
    "max_signed_score",
    "score_source",
    "max_observed_count",
    "mean_observed_count",
    "min_observed_count",
    "total_observed_count",
    "episode_strength_band",
    "episode_duration_class",
    "baseline_confidence_band",
    "interpretation_warning_summary",
    "episode_readiness",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Group review-ready rows into single-sensor episodes."
    )
    parser.add_argument("--sensor-mode", default=DEFAULT_SENSOR_MODE)
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Override the sensor-mode-aware processed output directory.",
    )
    return parser.parse_args()


def parse_int(value: str | None) -> int | None:
    if value is None or value.strip() == "":
        return None
    try:
        parsed = float(value)
    except ValueError:
        return None
    if not math.isfinite(parsed) or not parsed.is_integer():
        return None
    return int(parsed)


def parse_float(value: str | None) -> float | None:
    if value is None or value.strip() == "":
        return None
    try:
        parsed = float(value)
    except ValueError:
        return None
    return parsed if math.isfinite(parsed) else None


def parse_local_hour(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M")
    except ValueError as error:
        raise ValueError(
            f"Invalid local_timestamp_key {value!r}; expected YYYY-MM-DDTHH:MM"
        ) from error


def read_input(
    input_file: Path,
) -> tuple[list[dict[str, Any]], int, list[str]]:
    if not input_file.exists():
        raise FileNotFoundError(
            f"Phase 1D interpretation panel not found: {input_file}"
        )

    review_rows: list[dict[str, Any]] = []
    with input_file.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        missing_columns = sorted(REQUIRED_COLUMNS - set(fieldnames))
        if missing_columns:
            raise ValueError(
                "Phase 1E input is missing required interpretation columns: "
                f"{', '.join(missing_columns)}"
            )

        input_row_count = 0
        for raw in reader:
            input_row_count += 1
            if raw.get("candidate_readiness") != "review_ready":
                continue

            score = parse_float(raw.get("primary_deviation_score"))
            observed_count = parse_int(raw.get("observed_count"))
            hour = parse_int(raw.get("hour"))
            if score is None:
                raise ValueError(
                    "Review-ready row has no valid primary deviation score: "
                    f"sensor={raw.get('sensor_id')}, "
                    f"timestamp={raw.get('timestamp')}"
                )
            if observed_count is None or observed_count < 0:
                raise ValueError(
                    "Review-ready row has no valid observed count: "
                    f"sensor={raw.get('sensor_id')}, "
                    f"timestamp={raw.get('timestamp')}"
                )
            if hour is None or not 0 <= hour <= 23:
                raise ValueError(
                    f"Review-ready row has invalid hour: {raw.get('hour')!r}"
                )
            direction = raw.get("deviation_direction", "")
            if direction not in VALID_DIRECTIONS:
                raise ValueError(
                    "Review-ready row has invalid deviation direction: "
                    f"{direction!r}"
                )
            magnitude = raw.get("deviation_magnitude_band", "")
            if magnitude not in VALID_STRENGTH_BANDS:
                raise ValueError(
                    "Review-ready row must be strong or extreme, received "
                    f"{magnitude!r}"
                )

            review_rows.append(
                {
                    "timestamp": raw["timestamp"],
                    "local_timestamp_key": raw["local_timestamp_key"],
                    "_local_datetime": parse_local_hour(
                        raw["local_timestamp_key"]
                    ),
                    "date": raw["date"],
                    "hour": hour,
                    "weekday": raw["weekday"],
                    "sensor_mode": raw["sensor_mode"],
                    "sensor_id": raw["sensor_id"],
                    "sensor_name": raw.get("sensor_name", ""),
                    "sensor_short_label": (
                        raw.get("sensor_short_label")
                        or raw.get("location_label")
                        or raw.get("sensor_description", "")
                    ),
                    "observed_count": observed_count,
                    "deviation_direction": direction,
                    "deviation_magnitude_band": magnitude,
                    "primary_deviation_score": score,
                    "primary_score_source": raw["primary_score_source"],
                    "signal_family": raw["signal_family"],
                    "signal_subtype": raw["signal_subtype"],
                    "candidate_readiness": raw["candidate_readiness"],
                    "baseline_confidence_band": raw[
                        "baseline_confidence_band"
                    ],
                    "interpretation_warning": raw[
                        "interpretation_warning"
                    ],
                }
            )

    return review_rows, input_row_count, fieldnames


def dominant(values: list[str]) -> str:
    counts = Counter(values)
    return sorted(counts, key=lambda value: (-counts[value], value))[0]


def strength_band(rows: list[dict[str, Any]]) -> str:
    bands = {row["deviation_magnitude_band"] for row in rows}
    if bands == {"strong", "extreme"}:
        return "mixed_strong_extreme"
    if bands == {"extreme"}:
        return "extreme"
    if bands == {"strong"}:
        return "strong"
    raise ValueError(f"Unexpected episode strength bands: {sorted(bands)}")


def duration_class(duration_hours: int) -> str:
    if duration_hours == 1:
        return "single_hour"
    if duration_hours <= 3:
        return "short_2_3h"
    if duration_hours <= 6:
        return "medium_4_6h"
    return "long_7h_plus"


def compact_timestamp(value: str) -> str:
    return re.sub(r"[^0-9]", "", value)[:12]


def build_episode(
    sensor_mode: str,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    first = rows[0]
    last = rows[-1]
    scores = [row["primary_deviation_score"] for row in rows]
    observed_counts = [row["observed_count"] for row in rows]
    source_row_count = len(rows)
    duration_hours = int(
        (last["_local_datetime"] - first["_local_datetime"]).total_seconds()
        / 3600
    ) + 1
    if duration_hours != source_row_count:
        raise ValueError(
            "Episode source rows are not strictly contiguous: "
            f"sensor={first['sensor_id']}, "
            f"start={first['local_timestamp_key']}, "
            f"end={last['local_timestamp_key']}"
        )

    peak_signed_score = max(scores, key=lambda value: (abs(value), value))
    warnings = sorted(
        {row["interpretation_warning"] for row in rows}
    )
    score_sources = {row["primary_score_source"] for row in rows}
    if len(score_sources) != 1:
        raise ValueError(
            f"Episode contains mixed score sources: {sorted(score_sources)}"
        )
    baseline_bands = {row["baseline_confidence_band"] for row in rows}
    if baseline_bands != {"high"}:
        raise ValueError(
            "Review-ready episode contains non-high baseline confidence: "
            f"{sorted(baseline_bands)}"
        )

    return {
        "episode_id": (
            f"E1E_{sensor_mode}_{first['sensor_id']}_"
            f"{first['deviation_direction']}_"
            f"{compact_timestamp(first['local_timestamp_key'])}"
        ),
        "sensor_mode": sensor_mode,
        "sensor_id": first["sensor_id"],
        "sensor_name": first["sensor_name"],
        "sensor_short_label": first["sensor_short_label"],
        "episode_direction": first["deviation_direction"],
        "signal_family": dominant(
            [row["signal_family"] for row in rows]
        ),
        "signal_subtype_dominant": dominant(
            [row["signal_subtype"] for row in rows]
        ),
        "source_row_count": source_row_count,
        "start_timestamp": first["timestamp"],
        "end_timestamp": last["timestamp"],
        "duration_hours": duration_hours,
        "start_local_timestamp_key": first["local_timestamp_key"],
        "end_local_timestamp_key": last["local_timestamp_key"],
        "start_date": first["date"],
        "end_date": last["date"],
        "start_hour": first["hour"],
        "end_hour": last["hour"],
        "start_weekday": first["weekday"],
        "end_weekday": last["weekday"],
        "peak_abs_score": round(max(abs(value) for value in scores), 4),
        "peak_signed_score": round(peak_signed_score, 4),
        "mean_abs_score": round(
            fmean(abs(value) for value in scores), 4
        ),
        "mean_signed_score": round(fmean(scores), 4),
        "min_signed_score": round(min(scores), 4),
        "max_signed_score": round(max(scores), 4),
        "score_source": next(iter(score_sources)),
        "max_observed_count": max(observed_counts),
        "mean_observed_count": round(fmean(observed_counts), 3),
        "min_observed_count": min(observed_counts),
        "total_observed_count": sum(observed_counts),
        "episode_strength_band": strength_band(rows),
        "episode_duration_class": duration_class(duration_hours),
        "baseline_confidence_band": "high",
        "interpretation_warning_summary": "|".join(warnings),
        "episode_readiness": "candidate_episode",
        "_source_sensor_ids": sorted(
            {row["sensor_id"] for row in rows}
        ),
        "_source_directions": sorted(
            {row["deviation_direction"] for row in rows}
        ),
        "_source_readiness_values": sorted(
            {row["candidate_readiness"] for row in rows}
        ),
        "_source_local_timestamp_keys": [
            row["local_timestamp_key"] for row in rows
        ],
    }


def build_episodes(
    review_rows: list[dict[str, Any]],
    sensor_mode: str,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in review_rows:
        if row["sensor_mode"] != sensor_mode:
            raise ValueError(
                "Input row sensor mode does not match requested mode: "
                f"requested={sensor_mode}, row={row['sensor_mode']}"
            )
        grouped[
            (row["sensor_id"], row["deviation_direction"])
        ].append(row)

    episodes: list[dict[str, Any]] = []
    for key in sorted(grouped, key=lambda item: (int(item[0]), item[1])):
        rows = sorted(
            grouped[key], key=lambda row: row["_local_datetime"]
        )
        seen_hours: set[datetime] = set()
        current_episode: list[dict[str, Any]] = []
        previous_time: datetime | None = None

        for row in rows:
            current_time = row["_local_datetime"]
            if current_time in seen_hours:
                raise ValueError(
                    "Duplicate review-ready sensor-hour encountered: "
                    f"sensor={row['sensor_id']}, "
                    f"direction={row['deviation_direction']}, "
                    f"hour={row['local_timestamp_key']}"
                )
            seen_hours.add(current_time)

            if (
                current_episode
                and previous_time is not None
                and current_time != previous_time + timedelta(hours=1)
            ):
                episodes.append(
                    build_episode(sensor_mode, current_episode)
                )
                current_episode = []

            current_episode.append(row)
            previous_time = current_time

        if current_episode:
            episodes.append(build_episode(sensor_mode, current_episode))

    return sorted(
        episodes,
        key=lambda episode: (
            episode["start_local_timestamp_key"],
            int(episode["sensor_id"]),
            episode["episode_direction"],
        ),
    )


def output_episode(episode: dict[str, Any]) -> dict[str, Any]:
    return {field: episode[field] for field in EPISODE_FIELDS}


def write_outputs(
    episodes: list[dict[str, Any]],
    csv_output: Path,
    json_output: Path,
) -> None:
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    with csv_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(EPISODE_FIELDS))
        writer.writeheader()
        writer.writerows(output_episode(episode) for episode in episodes)

    with json_output.open("w", encoding="utf-8") as handle:
        json.dump(
            [output_episode(episode) for episode in episodes],
            handle,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )
        handle.write("\n")


def build_diagnostics(
    input_row_count: int,
    review_rows: list[dict[str, Any]],
    episodes: list[dict[str, Any]],
    sensor_mode: str,
    input_file: Path,
    csv_output: Path,
    json_output: Path,
    output_dir: Path,
) -> dict[str, Any]:
    direction_counts = Counter(
        episode["episode_direction"] for episode in episodes
    )
    strength_counts = Counter(
        episode["episode_strength_band"] for episode in episodes
    )
    duration_counts = Counter(
        episode["episode_duration_class"] for episode in episodes
    )
    readiness_counts = Counter(
        episode["episode_readiness"] for episode in episodes
    )
    episodes_by_sensor = Counter(
        episode["sensor_id"] for episode in episodes
    )
    single_hour_count = sum(
        episode["source_row_count"] == 1 for episode in episodes
    )
    anomaly_files = list(output_dir.glob("anomaly_candidates*"))

    strict_contiguity = all(
        all(
            parse_local_hour(current)
            == parse_local_hour(previous) + timedelta(hours=1)
            for previous, current in zip(
                episode["_source_local_timestamp_keys"],
                episode["_source_local_timestamp_keys"][1:],
            )
        )
        for episode in episodes
    )
    sanity_checks = {
        "only_review_ready_rows_used": all(
            row["candidate_readiness"] == "review_ready"
            for row in review_rows
        )
        and all(
            episode["_source_readiness_values"] == ["review_ready"]
            for episode in episodes
        ),
        "output_episode_count_positive_when_review_ready_rows_exist": (
            not review_rows or bool(episodes)
        ),
        "every_episode_has_valid_sensor_id": all(
            bool(episode["sensor_id"]) for episode in episodes
        ),
        "every_episode_has_valid_direction": all(
            episode["episode_direction"] in VALID_DIRECTIONS
            for episode in episodes
        ),
        "every_episode_duration_positive": all(
            episode["duration_hours"] > 0 for episode in episodes
        ),
        "every_episode_source_row_count_positive": all(
            episode["source_row_count"] > 0 for episode in episodes
        ),
        "single_hour_episodes_preserved": all(
            episode["duration_hours"] == 1
            for episode in episodes
            if episode["source_row_count"] == 1
        ),
        "no_cross_sensor_grouping": all(
            len(episode["_source_sensor_ids"]) == 1
            for episode in episodes
        ),
        "no_cross_direction_grouping": all(
            len(episode["_source_directions"]) == 1
            for episode in episodes
        ),
        "no_needs_context_rows_used": all(
            "needs_context"
            not in episode["_source_readiness_values"]
            for episode in episodes
        ),
        "no_data_quality_rows_used": all(
            "data_quality_review"
            not in episode["_source_readiness_values"]
            for episode in episodes
        ),
        "strict_hourly_contiguity": strict_contiguity,
        "all_review_ready_rows_accounted_for": sum(
            episode["source_row_count"] for episode in episodes
        )
        == len(review_rows),
        "no_final_anomaly_file_created": not anomaly_files,
    }
    if not all(sanity_checks.values()):
        raise ValueError(
            f"Phase 1E sanity checks failed: {sanity_checks}"
        )

    durations = [episode["duration_hours"] for episode in episodes]
    peak_scores = [episode["peak_abs_score"] for episode in episodes]
    return {
        "processing_version": PROCESSING_VERSION,
        "sensor_mode": sensor_mode,
        "input_file": input_file.relative_to(ROOT).as_posix(),
        "output_files": [
            csv_output.relative_to(ROOT).as_posix(),
            json_output.relative_to(ROOT).as_posix(),
        ],
        "input_row_count": input_row_count,
        "review_ready_input_rows": len(review_rows),
        "episode_count": len(episodes),
        "sensor_count": len(episodes_by_sensor),
        "episode_direction_counts": dict(sorted(direction_counts.items())),
        "episode_strength_band_counts": dict(
            sorted(strength_counts.items())
        ),
        "episode_duration_class_counts": dict(
            sorted(duration_counts.items())
        ),
        "episode_readiness_counts": dict(
            sorted(readiness_counts.items())
        ),
        "episodes_by_sensor": dict(
            sorted(episodes_by_sensor.items(), key=lambda item: int(item[0]))
        ),
        "single_hour_episode_count": single_hour_count,
        "multi_hour_episode_count": len(episodes) - single_hour_count,
        "longest_episode_duration_hours": max(durations, default=0),
        "max_peak_abs_score": max(peak_scores, default=None),
        "mean_episode_duration_hours": (
            round(fmean(durations), 3) if durations else None
        ),
        "sanity_checks": sanity_checks,
        "notes": [
            "Episodes use strict consecutive local hourly keys with no gap merge.",
            "Episodes are single-sensor and single-direction only.",
            "Candidate episodes are not confirmed anomalies.",
        ],
    }


def main() -> None:
    args = parse_args()
    output_dir = resolve_output_dir(args.output_dir, args.sensor_mode)
    input_file = output_dir / "deviation_interpretation_panel.csv"
    csv_output = output_dir / "candidate_episodes.csv"
    json_output = output_dir / "candidate_episodes.json"
    diagnostics_output = output_dir / "phase1e_diagnostics.json"

    configured_sensor_ids = {
        row["sensor_id"] for row in load_sensor_selection(args.sensor_mode)
    }
    review_rows, input_row_count, _ = read_input(input_file)
    input_sensor_ids = {row["sensor_id"] for row in review_rows}
    if not input_sensor_ids.issubset(configured_sensor_ids):
        raise ValueError(
            "Phase 1E review-ready sensors are outside the configured mode: "
            f"configured={sorted(configured_sensor_ids, key=int)}, "
            f"input={sorted(input_sensor_ids, key=int)}"
        )

    episodes = build_episodes(review_rows, args.sensor_mode)
    diagnostics = build_diagnostics(
        input_row_count,
        review_rows,
        episodes,
        args.sensor_mode,
        input_file,
        csv_output,
        json_output,
        output_dir,
    )
    write_outputs(episodes, csv_output, json_output)
    with diagnostics_output.open("w", encoding="utf-8") as handle:
        json.dump(
            diagnostics,
            handle,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )
        handle.write("\n")
    print(json.dumps(diagnostics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
