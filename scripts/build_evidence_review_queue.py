"""Build a deterministic, stratified queue for Phase 1H manual research.

This stage selects cases for human evidence collection. It does not rank
candidates, match evidence, verify explanations, or alter Phase 1G outputs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from analysis_config import ROOT, resolve_output_dir


PROCESSING_VERSION = "phase1h-ab-0.1.0"
SUPPORTED_MODES = {"MVP_3", "REPRESENTATIVE_12"}
TARGET_SIZE = {"MVP_3": 12, "REPRESENTATIVE_12": 16}

EVIDENCE_MANUAL = ROOT / "data" / "manual" / "evidence_manual.csv"
EVIDENCE_REVIEWS = ROOT / "data" / "manual" / "evidence_match_reviews.csv"

OUTPUT_FIELDS = [
    "review_queue_id",
    "sensor_mode",
    "candidate_type",
    "candidate_id",
    "candidate_direction",
    "candidate_scope_or_context",
    "start_timestamp",
    "end_timestamp",
    "duration_hours",
    "active_sensor_count_or_blank",
    "sensor_ids_or_blank",
    "sensor_labels_or_blank",
    "public_holiday_overlap",
    "public_holiday_labels",
    "school_holiday_overlap",
    "school_holiday_labels",
    "dst_transition_overlap",
    "dst_transition_labels",
    "rain_total",
    "rainy_hour_count",
    "wind_speed_max",
    "temperature_mean",
    "weather_disruption_hour_count",
    "provisional_weather_disruption_overlap",
    "manual_event_window_overlap",
    "evidence_review_status",
    "selection_reasons",
    "suggested_evidence_types_to_check",
    "human_research_notes",
    "source_search_status",
]

REQUIRED_PULSE_FIELDS = {
    "pulse_group_id",
    "sensor_mode",
    "pulse_direction",
    "pulse_scope",
    "start_timestamp",
    "end_timestamp",
    "duration_hours",
    "max_active_sensor_count",
    "sensor_ids",
    "sensor_labels",
    "public_holiday_overlap",
    "school_holiday_overlap",
    "dst_transition_overlap",
    "rain_total",
    "rainy_hour_count",
    "weather_disruption_hour_count",
    "provisional_weather_disruption_overlap",
    "manual_event_window_overlap",
}

REQUIRED_EPISODE_FIELDS = {
    "episode_id",
    "sensor_mode",
    "episode_direction",
    "pulse_context_type",
    "start_timestamp",
    "end_timestamp",
    "duration_hours",
    "sensor_id",
    "sensor_short_label",
    "public_holiday_overlap",
    "school_holiday_overlap",
    "dst_transition_overlap",
    "rain_total",
    "rainy_hour_count",
    "weather_disruption_hour_count",
    "provisional_weather_disruption_overlap",
    "manual_event_window_overlap",
    "is_isolated_episode",
    "is_paired_context_member",
}

CAUSAL_PHRASES = (
    "caused",
    "due to",
    "because of",
    "explained by",
    "attributed to",
)
TOP_N_PHRASES = ("top anomaly", "top anomalies", "top-n", "top n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Phase 1H manual evidence review queue."
    )
    parser.add_argument(
        "--sensor-mode",
        choices=sorted(SUPPORTED_MODES),
        default="REPRESENTATIVE_12",
    )
    parser.add_argument("--output-dir", default=None)
    return parser.parse_args()


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        raise FileNotFoundError(f"Required input not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def validate_fields(path: Path, actual: list[str], required: set[str]) -> None:
    missing = sorted(required.difference(actual))
    if missing:
        raise ValueError(f"{path} is missing required fields: {missing}")


def truth(value: str | None) -> bool:
    return (value or "").strip().lower() in {"true", "1", "yes"}


def number(value: str | None) -> float:
    if value in (None, ""):
        return 0.0
    parsed = float(value)
    return parsed if math.isfinite(parsed) else 0.0


def manual_row_count(path: Path) -> int:
    if not path.exists():
        return 0
    rows, _ = read_csv(path)
    return len(rows)


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_digest(path: Path) -> str:
    digest = hashlib.sha256()
    if not path.exists():
        return digest.hexdigest()
    for file_path in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(str(file_path.relative_to(path)).encode("utf-8"))
        digest.update(file_digest(file_path).encode("ascii"))
    return digest.hexdigest()


def pulse_sort_key(row: dict[str, str]) -> tuple[Any, ...]:
    scope_order = {
        "network_wide_pulse": 0,
        "broad_multi_sensor_pulse": 1,
        "localized_multi_sensor_pulse": 2,
    }
    return (
        scope_order.get(row.get("pulse_scope", ""), 9),
        -number(row.get("max_active_sensor_count")),
        -number(row.get("duration_hours")),
        row.get("start_timestamp", ""),
        row.get("pulse_group_id", ""),
    )


def duration_sort_key(row: dict[str, str]) -> tuple[Any, ...]:
    return (
        -number(row.get("duration_hours")),
        row.get("start_timestamp", ""),
        row.get("pulse_group_id", row.get("episode_id", "")),
    )


def chronological_key(row: dict[str, str]) -> tuple[str, str]:
    return (
        row.get("start_timestamp", ""),
        row.get("pulse_group_id", row.get("episode_id", "")),
    )


def is_context_light(row: dict[str, str]) -> bool:
    return not any(
        (
            truth(row.get("public_holiday_overlap")),
            truth(row.get("school_holiday_overlap")),
            truth(row.get("dst_transition_overlap")),
            number(row.get("rainy_hour_count")) > 0,
            truth(row.get("provisional_weather_disruption_overlap")),
            truth(row.get("manual_event_window_overlap")),
        )
    )


def add_reason(
    selected: dict[tuple[str, str], dict[str, Any]],
    candidate_type: str,
    row: dict[str, str],
    reason: str,
) -> None:
    id_field = "pulse_group_id" if candidate_type == "pulse_group" else "episode_id"
    key = (candidate_type, row[id_field])
    if key not in selected:
        selected[key] = {
            "candidate_type": candidate_type,
            "source": row,
            "reasons": [],
        }
    if reason not in selected[key]["reasons"]:
        selected[key]["reasons"].append(reason)


def ensure_pulse_coverage(
    selected: dict[tuple[str, str], dict[str, Any]],
    pulses: list[dict[str, str]],
    predicate: Callable[[dict[str, str]], bool],
    reason: str,
    count: int,
    key: Callable[[dict[str, str]], Any] = chronological_key,
) -> None:
    eligible = sorted((row for row in pulses if predicate(row)), key=key)
    already = [
        row
        for row in eligible
        if ("pulse_group", row["pulse_group_id"]) in selected
    ]
    for row in already:
        add_reason(selected, "pulse_group", row, reason)
    covered = len(already)
    for row in eligible:
        if covered >= count:
            break
        candidate_key = ("pulse_group", row["pulse_group_id"])
        if candidate_key in selected:
            continue
        add_reason(selected, "pulse_group", row, reason)
        covered += 1


def select_candidates(
    pulses: list[dict[str, str]],
    episodes: list[dict[str, str]],
    sensor_mode: str,
) -> list[dict[str, Any]]:
    selected: dict[tuple[str, str], dict[str, Any]] = {}

    broad_scopes = {"network_wide_pulse", "broad_multi_sensor_pulse"}
    ensure_pulse_coverage(
        selected,
        pulses,
        lambda row: row.get("pulse_scope") in broad_scopes,
        "broad_pulse",
        4 if sensor_mode == "REPRESENTATIVE_12" else 3,
        pulse_sort_key,
    )
    for item in selected.values():
        row = item["source"]
        if row.get("pulse_scope") == "network_wide_pulse":
            add_reason(
                selected, "pulse_group", row, "network_wide_pulse"
            )

    ensure_pulse_coverage(
        selected,
        pulses,
        lambda row: number(row.get("duration_hours")) >= 2,
        "long_duration",
        2,
        duration_sort_key,
    )
    ensure_pulse_coverage(
        selected,
        pulses,
        lambda row: row.get("pulse_scope")
        in {
            "network_wide_pulse",
            "broad_multi_sensor_pulse",
            "localized_multi_sensor_pulse",
        }
        and is_context_light(row),
        "context_light_broad_pulse",
        2,
        pulse_sort_key,
    )
    ensure_pulse_coverage(
        selected,
        pulses,
        lambda row: truth(row.get("public_holiday_overlap")),
        "public_holiday_overlap",
        2,
    )
    ensure_pulse_coverage(
        selected,
        pulses,
        lambda row: truth(row.get("school_holiday_overlap")),
        "school_holiday_overlap",
        2,
    )
    ensure_pulse_coverage(
        selected,
        pulses,
        lambda row: number(row.get("rainy_hour_count")) > 0,
        "rain_overlap",
        2,
    )
    ensure_pulse_coverage(
        selected,
        pulses,
        lambda row: truth(row.get("provisional_weather_disruption_overlap")),
        "weather_disruption_overlap",
        2,
    )
    ensure_pulse_coverage(
        selected,
        pulses,
        lambda row: row.get("pulse_direction") == "above_baseline",
        "positive_deviation",
        1,
    )
    ensure_pulse_coverage(
        selected,
        pulses,
        lambda row: row.get("pulse_direction") == "below_baseline",
        "negative_deviation",
        1,
    )
    ensure_pulse_coverage(
        selected,
        pulses,
        lambda row: truth(row.get("dst_transition_overlap")),
        "dst_overlap",
        1,
    )

    isolated = sorted(
        (row for row in episodes if truth(row.get("is_isolated_episode"))),
        key=duration_sort_key,
    )
    paired = sorted(
        (row for row in episodes if truth(row.get("is_paired_context_member"))),
        key=duration_sort_key,
    )
    if isolated:
        add_reason(selected, "episode", isolated[0], "isolated_episode")
    elif paired:
        add_reason(selected, "episode", paired[0], "paired_context")

    target = TARGET_SIZE[sensor_mode]
    for row in sorted(pulses, key=pulse_sort_key):
        if len(selected) >= target:
            break
        if ("pulse_group", row["pulse_group_id"]) not in selected:
            add_reason(
                selected,
                "pulse_group",
                row,
                "unexplained_candidate_for_review",
            )

    if len(selected) < 12:
        for row in isolated + paired:
            if len(selected) >= 12:
                break
            reason = (
                "isolated_episode"
                if truth(row.get("is_isolated_episode"))
                else "paired_context"
            )
            add_reason(selected, "episode", row, reason)

    if sensor_mode == "REPRESENTATIVE_12" and not 12 <= len(selected) <= 18:
        raise ValueError(
            f"REPRESENTATIVE_12 queue must contain 12-18 rows; got {len(selected)}"
        )
    return list(selected.values())


def suggestions(row: dict[str, str], candidate_type: str) -> str:
    values: list[str] = []

    def add(*items: str) -> None:
        for item in items:
            if item not in values:
                values.append(item)

    if truth(row.get("public_holiday_overlap")):
        add("public_holiday")
    if truth(row.get("school_holiday_overlap")):
        add("school_holiday")
    if truth(row.get("provisional_weather_disruption_overlap")):
        add("weather_warning")

    scope = (
        row.get("pulse_scope", "")
        if candidate_type == "pulse_group"
        else row.get("pulse_context_type", "")
    )
    if is_context_light(row) and scope in {
        "network_wide_pulse",
        "broad_multi_sensor_pulse",
    }:
        add(
            "sports_event",
            "concert",
            "festival",
            "cultural_activity",
        )
    if scope in {
        "localized_multi_sensor_pulse",
        "isolated_episode",
        "paired_context",
    } or row.get(
        "pulse_direction", row.get("episode_direction")
    ) == "below_baseline":
        add("transport_disruption", "road_closure")

    completeness = set(
        item
        for item in row.get("context_completeness_flags", "").split("|")
        if item
    )
    expected = {"weather_complete", "calendar_complete", "sensor_metadata_complete"}
    warnings = row.get("interpretation_warning_summary", "")
    if not expected.issubset(completeness) or (
        warnings and warnings.lower() != "none"
    ):
        add("data_quality_issue")

    if not values:
        add(
            "major_event",
            "commercial_activity",
            "cultural_activity",
            "unknown_context",
        )
    return "|".join(values)


def queue_row(
    item: dict[str, Any], index: int, sensor_mode: str
) -> dict[str, Any]:
    row = item["source"]
    candidate_type = item["candidate_type"]
    is_pulse = candidate_type == "pulse_group"
    return {
        "review_queue_id": f"HQ_{sensor_mode}_{index:03d}",
        "sensor_mode": sensor_mode,
        "candidate_type": candidate_type,
        "candidate_id": row["pulse_group_id"] if is_pulse else row["episode_id"],
        "candidate_direction": (
            row.get("pulse_direction", "")
            if is_pulse
            else row.get("episode_direction", "")
        ),
        "candidate_scope_or_context": (
            row.get("pulse_scope", "")
            if is_pulse
            else row.get("pulse_context_type", "")
        ),
        "start_timestamp": row.get("start_timestamp", ""),
        "end_timestamp": row.get("end_timestamp", ""),
        "duration_hours": row.get("duration_hours", ""),
        "active_sensor_count_or_blank": (
            row.get("max_active_sensor_count", "") if is_pulse else ""
        ),
        "sensor_ids_or_blank": (
            row.get("sensor_ids", "") if is_pulse else row.get("sensor_id", "")
        ),
        "sensor_labels_or_blank": (
            row.get("sensor_labels", "")
            if is_pulse
            else row.get("sensor_short_label", "")
        ),
        "public_holiday_overlap": row.get("public_holiday_overlap", ""),
        "public_holiday_labels": row.get("public_holiday_labels", ""),
        "school_holiday_overlap": row.get("school_holiday_overlap", ""),
        "school_holiday_labels": row.get("school_holiday_labels", ""),
        "dst_transition_overlap": row.get("dst_transition_overlap", ""),
        "dst_transition_labels": row.get("dst_transition_labels", ""),
        "rain_total": row.get("rain_total", ""),
        "rainy_hour_count": row.get("rainy_hour_count", ""),
        "wind_speed_max": row.get("wind_speed_max", ""),
        "temperature_mean": row.get("temperature_mean", ""),
        "weather_disruption_hour_count": row.get(
            "weather_disruption_hour_count", ""
        ),
        "provisional_weather_disruption_overlap": row.get(
            "provisional_weather_disruption_overlap", ""
        ),
        "manual_event_window_overlap": row.get(
            "manual_event_window_overlap", ""
        ),
        "evidence_review_status": "pending_manual_research",
        "selection_reasons": "|".join(item["reasons"]),
        "suggested_evidence_types_to_check": suggestions(row, candidate_type),
        "human_research_notes": "",
        "source_search_status": "not_started",
    }


def write_outputs(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    with path.with_suffix(".json").open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def count_reasons(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        counts.update(
            item for item in row["selection_reasons"].split("|") if item
        )
    return dict(sorted(counts.items()))


def main() -> None:
    config = parse_args()
    if config.sensor_mode not in SUPPORTED_MODES:
        raise ValueError("HIGH_COVERAGE_ALL is not supported by Phase 1H-A/B.")

    output_dir = resolve_output_dir(config.output_dir, config.sensor_mode)
    pulse_path = output_dir / "context_enriched_pulse_groups.csv"
    episode_path = output_dir / "context_enriched_candidate_episodes.csv"
    phase1g_diagnostics_path = output_dir / "phase1g_context_diagnostics.json"
    protected_input_paths = (
        pulse_path,
        episode_path,
        phase1g_diagnostics_path,
    )
    protected_input_digests = {
        path: file_digest(path) for path in protected_input_paths
    }
    manual_digests = {
        path: file_digest(path)
        for path in (EVIDENCE_MANUAL, EVIDENCE_REVIEWS)
        if path.exists()
    }
    frontend_digest = tree_digest(ROOT / "src")
    raw_digest = tree_digest(ROOT / "data" / "raw")

    pulses, pulse_fields = read_csv(pulse_path)
    episodes, episode_fields = read_csv(episode_path)
    validate_fields(pulse_path, pulse_fields, REQUIRED_PULSE_FIELDS)
    validate_fields(episode_path, episode_fields, REQUIRED_EPISODE_FIELDS)
    if not phase1g_diagnostics_path.exists():
        raise FileNotFoundError(
            f"Required input not found: {phase1g_diagnostics_path}"
        )
    with phase1g_diagnostics_path.open("r", encoding="utf-8") as handle:
        phase1g_diagnostics = json.load(handle)
    if phase1g_diagnostics.get("sensor_mode") != config.sensor_mode:
        raise ValueError("Phase 1G diagnostics sensor mode does not match.")

    selected = select_candidates(pulses, episodes, config.sensor_mode)
    selected.sort(
        key=lambda item: (
            0 if item["candidate_type"] == "pulse_group" else 1,
            item["source"].get("start_timestamp", ""),
            item["source"].get(
                "pulse_group_id", item["source"].get("episode_id", "")
            ),
        )
    )
    queue = [
        queue_row(item, index, config.sensor_mode)
        for index, item in enumerate(selected, start=1)
    ]

    output_path = output_dir / "phase1h_review_queue.csv"
    diagnostics_path = output_dir / "phase1h_review_queue_diagnostics.json"
    write_outputs(output_path, queue)

    candidate_keys = [
        (row["candidate_type"], row["candidate_id"]) for row in queue
    ]
    text = "\n".join(
        str(value).lower() for row in queue for value in row.values()
    )
    output_names = {
        output_path.name,
        output_path.with_suffix(".json").name,
        diagnostics_path.name,
    }
    forbidden_columns = {"review_priority_score", "priority_band"}
    sanity_checks = {
        "review_queue_size_between_12_and_18_for_representative_12": (
            12 <= len(queue) <= 18
            if config.sensor_mode == "REPRESENTATIVE_12"
            else True
        ),
        "no_duplicate_candidate_ids": len(candidate_keys)
        == len(set(candidate_keys)),
        "no_review_priority_score_created": "review_priority_score"
        not in OUTPUT_FIELDS,
        "no_priority_band_created": "priority_band" not in OUTPUT_FIELDS,
        "no_ranking_created": not forbidden_columns.intersection(OUTPUT_FIELDS),
        "no_top_n_language": not any(term in text for term in TOP_N_PHRASES),
        "no_causal_language": not any(
            phrase in text for phrase in CAUSAL_PHRASES
        ),
        "no_evidence_matches_generated": not any(
            "match" in name for name in output_names
        ),
        "no_explanation_ready_outputs_created": not any(
            "explanation_ready" in name for name in output_names
        ),
        "manual_evidence_not_fabricated": manual_digests
        == {
            path: file_digest(path)
            for path in (EVIDENCE_MANUAL, EVIDENCE_REVIEWS)
            if path.exists()
        },
        "review_status_pending_only": {
            row["evidence_review_status"] for row in queue
        }
        == {"pending_manual_research"},
        "phase1g_inputs_not_modified": protected_input_digests
        == {path: file_digest(path) for path in protected_input_paths},
        "frontend_not_modified": frontend_digest == tree_digest(ROOT / "src"),
        "raw_data_not_modified": raw_digest
        == tree_digest(ROOT / "data" / "raw"),
        "high_coverage_all_not_run": config.sensor_mode
        != "HIGH_COVERAGE_ALL",
    }
    if not all(sanity_checks.values()):
        failures = [
            name for name, passed in sanity_checks.items() if not passed
        ]
        raise ValueError(f"Phase 1H sanity checks failed: {failures}")

    candidate_type_counts = Counter(
        row["candidate_type"] for row in queue
    )
    direction_counts = Counter(
        row["candidate_direction"] for row in queue
    )
    pulse_scope_counts = Counter(
        row["candidate_scope_or_context"]
        for row in queue
        if row["candidate_type"] == "pulse_group"
    )
    diagnostics = {
        "processing_version": PROCESSING_VERSION,
        "sensor_mode": config.sensor_mode,
        "input_files": [
            str(pulse_path.relative_to(ROOT)),
            str(episode_path.relative_to(ROOT)),
            str(phase1g_diagnostics_path.relative_to(ROOT)),
        ],
        "output_files": [
            str(output_path.relative_to(ROOT)),
            str(output_path.with_suffix(".json").relative_to(ROOT)),
            str(diagnostics_path.relative_to(ROOT)),
        ],
        "input_pulse_count": len(pulses),
        "input_episode_count": len(episodes),
        "review_queue_row_count": len(queue),
        "candidate_type_counts": dict(sorted(candidate_type_counts.items())),
        "selection_reason_counts": count_reasons(queue),
        "direction_counts": dict(sorted(direction_counts.items())),
        "pulse_scope_counts": dict(sorted(pulse_scope_counts.items())),
        "public_holiday_overlap_count": sum(
            truth(row["public_holiday_overlap"]) for row in queue
        ),
        "school_holiday_overlap_count": sum(
            truth(row["school_holiday_overlap"]) for row in queue
        ),
        "rain_overlap_count": sum(
            number(row["rainy_hour_count"]) > 0 for row in queue
        ),
        "weather_disruption_overlap_count": sum(
            truth(row["provisional_weather_disruption_overlap"])
            for row in queue
        ),
        "dst_overlap_count": sum(
            truth(row["dst_transition_overlap"]) for row in queue
        ),
        "isolated_episode_count": sum(
            "isolated_episode" in row["selection_reasons"].split("|")
            for row in queue
        ),
        "paired_context_count": sum(
            "paired_context" in row["selection_reasons"].split("|")
            for row in queue
        ),
        "evidence_manual_file_exists": EVIDENCE_MANUAL.exists(),
        "evidence_manual_row_count": manual_row_count(EVIDENCE_MANUAL),
        "evidence_match_reviews_file_exists": EVIDENCE_REVIEWS.exists(),
        "evidence_match_reviews_row_count": manual_row_count(EVIDENCE_REVIEWS),
        "boundary_statements": [
            "The review queue is a stratified manual-research sample, not a ranking.",
            "Suggestions identify evidence types to investigate; they do not assert that evidence exists.",
            "No evidence matching, verified explanation, or causal interpretation is produced.",
            "Phase 1G signal and context outputs remain unchanged.",
        ],
        "sanity_checks": sanity_checks,
    }
    with diagnostics_path.open("w", encoding="utf-8") as handle:
        json.dump(diagnostics, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(
        f"Wrote {len(queue)} review cases for {config.sensor_mode} "
        f"to {output_path.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
