"""Build cross-sensor temporal pulse context from Phase 1E episodes.

Phase 1F expands candidate episodes to active hours, measures same-direction
sensor co-occurrence, builds pulse-context groups at a three-sensor threshold,
and annotates every input episode. It does not confirm or rank anomalies,
infer causes, use external events, or perform spatial clustering.
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


PROCESSING_VERSION = "phase1f-0.1.0"
MULTI_SENSOR_THRESHOLD = 3
VALID_DIRECTIONS = {"above_baseline", "below_baseline"}
REQUIRED_COLUMNS = {
    "episode_id",
    "sensor_mode",
    "sensor_id",
    "sensor_name",
    "sensor_short_label",
    "episode_direction",
    "start_timestamp",
    "end_timestamp",
    "duration_hours",
    "start_local_timestamp_key",
    "end_local_timestamp_key",
    "peak_abs_score",
    "mean_abs_score",
    "total_observed_count",
    "episode_strength_band",
    "episode_readiness",
}
PULSE_GROUP_FIELDS = (
    "pulse_group_id",
    "sensor_mode",
    "pulse_direction",
    "pulse_scope",
    "start_timestamp",
    "end_timestamp",
    "duration_hours",
    "active_hour_count",
    "max_active_sensor_count",
    "min_active_sensor_count",
    "mean_active_sensor_count",
    "sensor_count",
    "sensor_ids",
    "sensor_labels",
    "episode_count",
    "episode_ids",
    "max_peak_abs_score",
    "mean_peak_abs_score",
    "max_mean_abs_score",
    "total_observed_count",
    "dominant_strength_band",
    "pulse_readiness",
)
EPISODE_CONTEXT_FIELDS = (
    "episode_id",
    "sensor_mode",
    "sensor_id",
    "episode_direction",
    "episode_start_timestamp",
    "episode_end_timestamp",
    "episode_duration_hours",
    "episode_strength_band",
    "pulse_context_type",
    "pulse_group_id",
    "max_cooccurring_sensor_count",
    "max_cooccurring_episode_count",
    "cooccurring_sensor_ids_at_peak",
    "cooccurring_episode_ids_at_peak",
    "is_multi_sensor_pulse_member",
    "is_paired_context_member",
    "is_isolated_episode",
    "pulse_scope_at_peak",
    "pulse_context_notes",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build cross-sensor pulse context from Phase 1E episodes."
    )
    parser.add_argument("--sensor-mode", default=DEFAULT_SENSOR_MODE)
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Override the sensor-mode-aware processed output directory.",
    )
    return parser.parse_args()


def parse_int(value: str | None, field: str, episode_id: str) -> int:
    try:
        parsed = float(value or "")
    except ValueError as error:
        raise ValueError(
            f"Episode {episode_id!r} has invalid {field}: {value!r}"
        ) from error
    if not math.isfinite(parsed) or not parsed.is_integer():
        raise ValueError(
            f"Episode {episode_id!r} has invalid {field}: {value!r}"
        )
    return int(parsed)


def parse_float(value: str | None, field: str, episode_id: str) -> float:
    try:
        parsed = float(value or "")
    except ValueError as error:
        raise ValueError(
            f"Episode {episode_id!r} has invalid {field}: {value!r}"
        ) from error
    if not math.isfinite(parsed):
        raise ValueError(
            f"Episode {episode_id!r} has invalid {field}: {value!r}"
        )
    return parsed


def parse_local_hour(value: str, field: str, episode_id: str) -> datetime:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M")
    except ValueError as error:
        raise ValueError(
            f"Episode {episode_id!r} has invalid {field}: {value!r}"
        ) from error
    if parsed.minute or parsed.second or parsed.microsecond:
        raise ValueError(
            f"Episode {episode_id!r} {field} is not hour-aligned: {value!r}"
        )
    return parsed


def parse_aware_timestamp(value: str, field: str, episode_id: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError(
            f"Episode {episode_id!r} has invalid {field}: {value!r}"
        ) from error
    if parsed.tzinfo is None:
        raise ValueError(
            f"Episode {episode_id!r} {field} lacks a timezone offset."
        )
    return parsed


def sensor_sort_key(sensor_id: str) -> tuple[int, int | str]:
    return (0, int(sensor_id)) if sensor_id.isdigit() else (1, sensor_id)


def compact_timestamp(value: datetime) -> str:
    return re.sub(r"[^0-9]", "", value.strftime("%Y-%m-%dT%H:%M"))[:12]


def joined(values: list[str] | set[str], *, sensor_ids: bool = False) -> str:
    if sensor_ids:
        ordered = sorted(set(values), key=sensor_sort_key)
    else:
        ordered = sorted(set(values))
    return "|".join(ordered)


def pulse_scope(active_sensor_count: int) -> str:
    if active_sensor_count >= 8:
        return "network_wide_pulse"
    if active_sensor_count >= 5:
        return "broad_pulse"
    if active_sensor_count >= 3:
        return "localized_pulse"
    if active_sensor_count == 2:
        return "paired_context"
    return "isolated_episode"


def dominant(values: list[str]) -> str:
    counts = Counter(values)
    return sorted(counts, key=lambda value: (-counts[value], value))[0]


def read_episodes(
    input_file: Path,
    sensor_mode: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    if not input_file.exists():
        raise FileNotFoundError(f"Phase 1E episode file not found: {input_file}")

    episodes: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    with input_file.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        missing = sorted(REQUIRED_COLUMNS - set(fieldnames))
        if missing:
            raise ValueError(
                "Phase 1F input is missing required episode columns: "
                f"{', '.join(missing)}"
            )

        for raw in reader:
            episode_id = raw.get("episode_id", "")
            if not episode_id:
                raise ValueError("Phase 1F input contains a blank episode_id.")
            if episode_id in seen_ids:
                raise ValueError(f"Duplicate episode_id: {episode_id!r}")
            seen_ids.add(episode_id)

            if raw.get("sensor_mode") != sensor_mode:
                raise ValueError(
                    "Input episode sensor mode does not match requested mode: "
                    f"requested={sensor_mode!r}, "
                    f"episode={episode_id!r}, "
                    f"input={raw.get('sensor_mode')!r}"
                )
            if raw.get("episode_readiness") != "candidate_episode":
                raise ValueError(
                    f"Episode {episode_id!r} is not a candidate_episode."
                )
            direction = raw.get("episode_direction", "")
            if direction not in VALID_DIRECTIONS:
                raise ValueError(
                    f"Episode {episode_id!r} has invalid direction: "
                    f"{direction!r}"
                )

            duration = parse_int(
                raw.get("duration_hours"), "duration_hours", episode_id
            )
            if duration <= 0:
                raise ValueError(
                    f"Episode {episode_id!r} has non-positive duration."
                )
            start_local = parse_local_hour(
                raw["start_local_timestamp_key"],
                "start_local_timestamp_key",
                episode_id,
            )
            end_local = parse_local_hour(
                raw["end_local_timestamp_key"],
                "end_local_timestamp_key",
                episode_id,
            )
            expected_duration = int(
                (end_local - start_local).total_seconds() / 3600
            ) + 1
            if duration != expected_duration:
                raise ValueError(
                    f"Episode {episode_id!r} duration does not match its "
                    f"inclusive local timestamp range: duration={duration}, "
                    f"range={expected_duration}"
                )

            start_timestamp = parse_aware_timestamp(
                raw["start_timestamp"], "start_timestamp", episode_id
            )
            end_timestamp = parse_aware_timestamp(
                raw["end_timestamp"], "end_timestamp", episode_id
            )
            peak_abs_score = parse_float(
                raw.get("peak_abs_score"), "peak_abs_score", episode_id
            )
            mean_abs_score = parse_float(
                raw.get("mean_abs_score"), "mean_abs_score", episode_id
            )
            total_observed_count = parse_float(
                raw.get("total_observed_count"),
                "total_observed_count",
                episode_id,
            )
            if peak_abs_score < 0 or mean_abs_score < 0:
                raise ValueError(
                    f"Episode {episode_id!r} has a negative absolute score."
                )
            if total_observed_count < 0:
                raise ValueError(
                    f"Episode {episode_id!r} has negative observed volume."
                )

            episodes.append(
                {
                    **raw,
                    "duration_hours": duration,
                    "peak_abs_score": peak_abs_score,
                    "mean_abs_score": mean_abs_score,
                    "total_observed_count": total_observed_count,
                    "_start_local": start_local,
                    "_end_local": end_local,
                    "_start_timestamp": start_timestamp,
                    "_end_timestamp": end_timestamp,
                }
            )

    return episodes, fieldnames


def expand_episode_hours(
    episodes: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, list[datetime]]]:
    expanded: list[dict[str, Any]] = []
    hours_by_episode: dict[str, list[datetime]] = {}
    seen_sensor_direction_hours: set[tuple[str, str, datetime]] = set()

    for episode in episodes:
        active_hours: list[datetime] = []
        for offset in range(episode["duration_hours"]):
            local_hour = episode["_start_local"] + timedelta(hours=offset)
            key = (
                episode["sensor_id"],
                episode["episode_direction"],
                local_hour,
            )
            if key in seen_sensor_direction_hours:
                raise ValueError(
                    "Overlapping Phase 1E episodes found for the same "
                    "sensor, direction, and hour: "
                    f"sensor={episode['sensor_id']}, "
                    f"direction={episode['episode_direction']}, "
                    f"hour={local_hour.isoformat(timespec='minutes')}"
                )
            seen_sensor_direction_hours.add(key)
            active_hours.append(local_hour)
            expanded.append(
                {
                    "episode_id": episode["episode_id"],
                    "sensor_mode": episode["sensor_mode"],
                    "sensor_id": episode["sensor_id"],
                    "sensor_label": (
                        episode.get("sensor_short_label")
                        or episode.get("sensor_name")
                        or episode["sensor_id"]
                    ),
                    "episode_direction": episode["episode_direction"],
                    "active_local_hour": local_hour,
                    "active_timestamp": (
                        episode["_start_timestamp"] + timedelta(hours=offset)
                    ).isoformat(),
                    "peak_abs_score": episode["peak_abs_score"],
                    "mean_abs_score": episode["mean_abs_score"],
                    "total_observed_count": episode[
                        "total_observed_count"
                    ],
                    "episode_strength_band": episode[
                        "episode_strength_band"
                    ],
                }
            )
        if active_hours[-1] != episode["_end_local"]:
            raise ValueError(
                f"Expanded hours do not reach episode {episode['episode_id']!r} "
                "end_local_timestamp_key."
            )
        hours_by_episode[episode["episode_id"]] = active_hours

    return expanded, hours_by_episode


def build_hour_groups(
    expanded: list[dict[str, Any]],
) -> dict[tuple[str, str, datetime], dict[str, Any]]:
    grouped: dict[
        tuple[str, str, datetime], list[dict[str, Any]]
    ] = defaultdict(list)
    for row in expanded:
        grouped[
            (
                row["sensor_mode"],
                row["episode_direction"],
                row["active_local_hour"],
            )
        ].append(row)

    hour_groups: dict[tuple[str, str, datetime], dict[str, Any]] = {}
    for key, rows in grouped.items():
        sensor_ids = {row["sensor_id"] for row in rows}
        episode_ids = {row["episode_id"] for row in rows}
        if len(sensor_ids) != len(rows) or len(episode_ids) != len(rows):
            raise ValueError(
                "An active hour contains duplicate sensor or episode rows: "
                f"mode={key[0]}, direction={key[1]}, hour={key[2]}"
            )
        timestamps = {row["active_timestamp"] for row in rows}
        # Local-hour keys are canonical. Offset differences are retained only
        # as a diagnostic note because Phase 1A uses nominal local-hour panels.
        display_timestamp = sorted(timestamps)[0]
        hour_groups[key] = {
            "sensor_mode": key[0],
            "episode_direction": key[1],
            "active_local_hour": key[2],
            "active_timestamp": display_timestamp,
            "timestamp_variant_count": len(timestamps),
            "active_sensor_count": len(sensor_ids),
            "active_episode_count": len(episode_ids),
            "sensor_ids": sensor_ids,
            "sensor_labels": {
                row["sensor_label"] for row in rows if row["sensor_label"]
            },
            "episode_ids": episode_ids,
            "max_peak_abs_score": max(
                row["peak_abs_score"] for row in rows
            ),
            "mean_peak_abs_score": fmean(
                row["peak_abs_score"] for row in rows
            ),
            "rows": rows,
        }
    return hour_groups


def build_pulse_group(
    sensor_mode: str,
    direction: str,
    hour_rows: list[dict[str, Any]],
    episodes_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    start_hour = hour_rows[0]["active_local_hour"]
    end_hour = hour_rows[-1]["active_local_hour"]
    duration = int((end_hour - start_hour).total_seconds() / 3600) + 1
    if duration != len(hour_rows):
        raise ValueError("Pulse group hours are not strictly contiguous.")

    sensor_ids = {
        sensor_id for hour in hour_rows for sensor_id in hour["sensor_ids"]
    }
    sensor_labels = {
        label for hour in hour_rows for label in hour["sensor_labels"]
    }
    episode_ids = {
        episode_id
        for hour in hour_rows
        for episode_id in hour["episode_ids"]
    }
    member_episodes = [episodes_by_id[value] for value in episode_ids]
    active_counts = [hour["active_sensor_count"] for hour in hour_rows]
    max_count = max(active_counts)

    return {
        "pulse_group_id": (
            f"P1F_{sensor_mode}_{direction}_{compact_timestamp(start_hour)}"
        ),
        "sensor_mode": sensor_mode,
        "pulse_direction": direction,
        "pulse_scope": pulse_scope(max_count),
        "start_timestamp": hour_rows[0]["active_timestamp"],
        "end_timestamp": hour_rows[-1]["active_timestamp"],
        "duration_hours": duration,
        "active_hour_count": len(hour_rows),
        "max_active_sensor_count": max_count,
        "min_active_sensor_count": min(active_counts),
        "mean_active_sensor_count": round(fmean(active_counts), 3),
        "sensor_count": len(sensor_ids),
        "sensor_ids": joined(sensor_ids, sensor_ids=True),
        "sensor_labels": joined(sensor_labels),
        "episode_count": len(episode_ids),
        "episode_ids": joined(episode_ids),
        "max_peak_abs_score": round(
            max(episode["peak_abs_score"] for episode in member_episodes), 4
        ),
        "mean_peak_abs_score": round(
            fmean(
                episode["peak_abs_score"] for episode in member_episodes
            ),
            4,
        ),
        "max_mean_abs_score": round(
            max(episode["mean_abs_score"] for episode in member_episodes), 4
        ),
        # Episode totals are counted once per unique member episode, not once
        # per expanded active hour.
        "total_observed_count": round(
            sum(
                episode["total_observed_count"]
                for episode in member_episodes
            ),
            3,
        ),
        "dominant_strength_band": dominant(
            [
                episode["episode_strength_band"]
                for episode in member_episodes
            ]
        ),
        "pulse_readiness": "pulse_context_candidate",
        "_start_local": start_hour,
        "_end_local": end_hour,
        "_hour_rows": hour_rows,
        "_sensor_ids": sensor_ids,
        "_episode_ids": episode_ids,
    }


def build_pulse_groups(
    hour_groups: dict[tuple[str, str, datetime], dict[str, Any]],
    episodes: list[dict[str, Any]],
    sensor_mode: str,
) -> list[dict[str, Any]]:
    episodes_by_id = {episode["episode_id"]: episode for episode in episodes}
    by_direction: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for hour in hour_groups.values():
        if hour["active_sensor_count"] >= MULTI_SENSOR_THRESHOLD:
            by_direction[hour["episode_direction"]].append(hour)

    pulse_groups: list[dict[str, Any]] = []
    for direction in sorted(by_direction):
        hours = sorted(
            by_direction[direction], key=lambda row: row["active_local_hour"]
        )
        current: list[dict[str, Any]] = []
        previous: datetime | None = None
        for hour in hours:
            if (
                current
                and previous is not None
                and hour["active_local_hour"] != previous + timedelta(hours=1)
            ):
                pulse_groups.append(
                    build_pulse_group(
                        sensor_mode,
                        direction,
                        current,
                        episodes_by_id,
                    )
                )
                current = []
            current.append(hour)
            previous = hour["active_local_hour"]
        if current:
            pulse_groups.append(
                build_pulse_group(
                    sensor_mode, direction, current, episodes_by_id
                )
            )

    return sorted(
        pulse_groups,
        key=lambda group: (
            group["_start_local"],
            group["pulse_direction"],
        ),
    )


def annotate_episodes(
    episodes: list[dict[str, Any]],
    hours_by_episode: dict[str, list[datetime]],
    hour_groups: dict[tuple[str, str, datetime], dict[str, Any]],
    pulse_groups: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    groups_by_episode: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for group in pulse_groups:
        for episode_id in group["_episode_ids"]:
            groups_by_episode[episode_id].append(group)

    contexts: list[dict[str, Any]] = []
    for episode in episodes:
        episode_id = episode["episode_id"]
        direction = episode["episode_direction"]
        active_hours = hours_by_episode[episode_id]
        relevant_hours = [
            hour_groups[(episode["sensor_mode"], direction, active_hour)]
            for active_hour in active_hours
        ]
        peak_hour = sorted(
            relevant_hours,
            key=lambda hour: (
                -hour["active_sensor_count"],
                -hour["active_episode_count"],
                -hour["max_peak_abs_score"],
                hour["active_local_hour"],
            ),
        )[0]

        overlapping_groups: list[tuple[dict[str, Any], int]] = []
        active_set = set(active_hours)
        for group in groups_by_episode.get(episode_id, []):
            overlap = sum(
                hour["active_local_hour"] in active_set
                for hour in group["_hour_rows"]
            )
            if overlap:
                overlapping_groups.append((group, overlap))

        selected_group: dict[str, Any] | None = None
        if overlapping_groups:
            selected_group = sorted(
                overlapping_groups,
                key=lambda item: (
                    -item[1],
                    -item[0]["max_active_sensor_count"],
                    -item[0]["max_peak_abs_score"],
                    item[0]["_start_local"],
                    item[0]["pulse_group_id"],
                ),
            )[0][0]

        maximum = peak_hour["active_sensor_count"]
        if selected_group is not None:
            context_type = selected_group["pulse_scope"]
            note = "assigned_to_strongest_overlap_pulse_group"
        elif maximum == 2:
            context_type = "paired_context"
            note = "two_sensor_temporal_overlap_only"
        else:
            context_type = "isolated_episode"
            note = "no_same_direction_cross_sensor_overlap"

        contexts.append(
            {
                "episode_id": episode_id,
                "sensor_mode": episode["sensor_mode"],
                "sensor_id": episode["sensor_id"],
                "episode_direction": direction,
                "episode_start_timestamp": episode["start_timestamp"],
                "episode_end_timestamp": episode["end_timestamp"],
                "episode_duration_hours": episode["duration_hours"],
                "episode_strength_band": episode[
                    "episode_strength_band"
                ],
                "pulse_context_type": context_type,
                "pulse_group_id": (
                    selected_group["pulse_group_id"]
                    if selected_group is not None
                    else ""
                ),
                "max_cooccurring_sensor_count": maximum,
                "max_cooccurring_episode_count": peak_hour[
                    "active_episode_count"
                ],
                "cooccurring_sensor_ids_at_peak": joined(
                    peak_hour["sensor_ids"], sensor_ids=True
                ),
                "cooccurring_episode_ids_at_peak": joined(
                    peak_hour["episode_ids"]
                ),
                "is_multi_sensor_pulse_member": selected_group is not None,
                "is_paired_context_member": (
                    selected_group is None and maximum == 2
                ),
                "is_isolated_episode": (
                    selected_group is None and maximum == 1
                ),
                "pulse_scope_at_peak": pulse_scope(maximum),
                "pulse_context_notes": note,
                "_selected_group_direction": (
                    selected_group["pulse_direction"]
                    if selected_group is not None
                    else None
                ),
            }
        )

    return sorted(
        contexts,
        key=lambda row: (
            row["episode_start_timestamp"],
            sensor_sort_key(row["sensor_id"]),
            row["episode_direction"],
        ),
    )


def public_row(row: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
    return {field: row[field] for field in fields}


def write_table(
    rows: list[dict[str, Any]],
    fields: tuple[str, ...],
    csv_output: Path,
    json_output: Path,
) -> None:
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    with csv_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields))
        writer.writeheader()
        writer.writerows(public_row(row, fields) for row in rows)
    with json_output.open("w", encoding="utf-8") as handle:
        json.dump(
            [public_row(row, fields) for row in rows],
            handle,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )
        handle.write("\n")


def build_diagnostics(
    sensor_mode: str,
    input_file: Path,
    output_files: list[Path],
    output_dir: Path,
    episodes: list[dict[str, Any]],
    expanded: list[dict[str, Any]],
    hour_groups: dict[tuple[str, str, datetime], dict[str, Any]],
    pulse_groups: list[dict[str, Any]],
    contexts: list[dict[str, Any]],
) -> dict[str, Any]:
    group_direction_counts = Counter(
        group["pulse_direction"] for group in pulse_groups
    )
    group_scope_counts = Counter(
        group["pulse_scope"] for group in pulse_groups
    )
    context_counts = Counter(
        context["pulse_context_type"] for context in contexts
    )
    active_hour_counts = [
        hour["active_sensor_count"] for hour in hour_groups.values()
    ]
    pulse_durations = [
        group["duration_hours"] for group in pulse_groups
    ]
    input_snapshot = [
        tuple(sorted((key, str(value)) for key, value in episode.items()))
        for episode in episodes
    ]

    isolated = [
        context
        for context in contexts
        if context["pulse_context_type"] == "isolated_episode"
    ]
    paired = [
        context
        for context in contexts
        if context["pulse_context_type"] == "paired_context"
    ]
    group_ids = {group["pulse_group_id"] for group in pulse_groups}
    anomaly_files = list(output_dir.glob("anomaly_candidates*"))
    ranking_files = list(output_dir.glob("*top*n*"))
    sanity_checks = {
        "input_episodes_not_modified": input_snapshot
        == [
            tuple(sorted((key, str(value)) for key, value in episode.items()))
            for episode in episodes
        ],
        "output_episode_context_rows_equal_input_episodes": (
            len(contexts) == len(episodes)
        ),
        "every_episode_has_context": all(
            context["pulse_context_type"] for context in contexts
        ),
        "every_pulse_group_has_at_least_threshold_sensors": all(
            group["min_active_sensor_count"] >= MULTI_SENSOR_THRESHOLD
            for group in pulse_groups
        ),
        "every_pulse_group_duration_positive": all(
            group["duration_hours"] > 0 for group in pulse_groups
        ),
        "positive_negative_not_mixed": all(
            {
                hour["episode_direction"]
                for hour in group["_hour_rows"]
            }
            == {group["pulse_direction"]}
            for group in pulse_groups
        ),
        "no_cross_direction_grouping": all(
            len(
                {
                    hour["episode_direction"]
                    for hour in group["_hour_rows"]
                }
            )
            == 1
            for group in pulse_groups
        ),
        "no_cross_sensor_mode_grouping": all(
            {
                hour["sensor_mode"] for hour in group["_hour_rows"]
            }
            == {sensor_mode}
            for group in pulse_groups
        ),
        "isolated_episodes_have_no_pulse_group_id": all(
            not context["pulse_group_id"] for context in isolated
        ),
        "paired_context_not_written_as_pulse_group": all(
            not context["pulse_group_id"] for context in paired
        )
        and all(
            group["min_active_sensor_count"] >= MULTI_SENSOR_THRESHOLD
            for group in pulse_groups
        ),
        "pulse_group_members_have_matching_direction": all(
            context["_selected_group_direction"]
            in {None, context["episode_direction"]}
            for context in contexts
        ),
        "all_referenced_pulse_groups_exist": all(
            not context["pulse_group_id"]
            or context["pulse_group_id"] in group_ids
            for context in contexts
        ),
        "no_final_anomaly_file_created": not anomaly_files,
        "no_top_n_ranking_created": not ranking_files,
    }
    if not all(sanity_checks.values()):
        raise ValueError(
            f"Phase 1F sanity checks failed: {sanity_checks}"
        )

    sensitivity = {
        f"hours_with_{threshold}plus_sensors": sum(
            count >= threshold for count in active_hour_counts
        )
        for threshold in (2, 3, 4, 6, 8)
    }
    return {
        "processing_version": PROCESSING_VERSION,
        "sensor_mode": sensor_mode,
        "input_file": input_file.relative_to(ROOT).as_posix(),
        "output_files": [
            path.relative_to(ROOT).as_posix() for path in output_files
        ],
        "input_episode_count": len(episodes),
        "expanded_episode_hour_count": len(expanded),
        "multi_sensor_threshold": MULTI_SENSOR_THRESHOLD,
        "pulse_active_hour_count": sensitivity[
            "hours_with_3plus_sensors"
        ],
        "pulse_group_count": len(pulse_groups),
        "pulse_groups_by_direction": dict(
            sorted(group_direction_counts.items())
        ),
        "pulse_groups_by_scope": dict(sorted(group_scope_counts.items())),
        "episode_context_counts": dict(sorted(context_counts.items())),
        "episodes_in_pulse_groups": sum(
            context["is_multi_sensor_pulse_member"] for context in contexts
        ),
        "isolated_episode_count": context_counts["isolated_episode"],
        "paired_context_episode_count": context_counts["paired_context"],
        "localized_pulse_episode_count": context_counts["localized_pulse"],
        "broad_pulse_episode_count": context_counts["broad_pulse"],
        "network_wide_pulse_episode_count": context_counts[
            "network_wide_pulse"
        ],
        "longest_pulse_duration_hours": max(pulse_durations, default=0),
        "max_active_sensor_count": max(active_hour_counts, default=0),
        "mean_pulse_duration_hours": (
            round(fmean(pulse_durations), 3) if pulse_durations else None
        ),
        "threshold_sensitivity_hours": sensitivity,
        "sanity_checks": sanity_checks,
        "notes": [
            "Co-occurrence uses same-direction nominal local episode hours.",
            "Pulse groups require at least three active sensors in every hour.",
            "No gap merging, spatial clustering, ranking, or cause inference is used.",
        ],
    }


def main() -> None:
    args = parse_args()
    output_dir = resolve_output_dir(args.output_dir, args.sensor_mode)
    input_file = output_dir / "candidate_episodes.csv"
    pulse_csv = output_dir / "pulse_groups.csv"
    pulse_json = output_dir / "pulse_groups.json"
    context_csv = output_dir / "episode_pulse_context.csv"
    context_json = output_dir / "episode_pulse_context.json"
    diagnostics_output = output_dir / "phase1f_diagnostics.json"

    configured_sensor_ids = {
        row["sensor_id"] for row in load_sensor_selection(args.sensor_mode)
    }
    episodes, _ = read_episodes(input_file, args.sensor_mode)
    input_sensor_ids = {episode["sensor_id"] for episode in episodes}
    if not input_sensor_ids.issubset(configured_sensor_ids):
        raise ValueError(
            "Phase 1F input sensors are outside the configured mode: "
            f"configured={sorted(configured_sensor_ids, key=sensor_sort_key)}, "
            f"input={sorted(input_sensor_ids, key=sensor_sort_key)}"
        )

    expanded, hours_by_episode = expand_episode_hours(episodes)
    hour_groups = build_hour_groups(expanded)
    pulse_groups = build_pulse_groups(
        hour_groups, episodes, args.sensor_mode
    )
    contexts = annotate_episodes(
        episodes,
        hours_by_episode,
        hour_groups,
        pulse_groups,
    )

    output_files = [pulse_csv, pulse_json, context_csv, context_json]
    diagnostics = build_diagnostics(
        args.sensor_mode,
        input_file,
        output_files,
        output_dir,
        episodes,
        expanded,
        hour_groups,
        pulse_groups,
        contexts,
    )
    write_table(
        pulse_groups,
        PULSE_GROUP_FIELDS,
        pulse_csv,
        pulse_json,
    )
    write_table(
        contexts,
        EPISODE_CONTEXT_FIELDS,
        context_csv,
        context_json,
    )
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
