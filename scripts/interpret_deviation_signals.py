"""Add an auditable deviation interpretation taxonomy to scored observations.

Phase 1D labels every sensor-hour row. It does not extract, rank, or group
final anomaly candidates and does not infer real-world causes.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

from analysis_config import (
    DEFAULT_SENSOR_MODE,
    ROOT,
    load_sensor_selection,
    resolve_output_dir,
)


PROCESSING_VERSION = "phase1d-0.1.0"
PRIMARY_SCORE_PRIORITY = (
    "robust_z_score",
    "z_score",
    "standardized_deviation",
)
REQUIRED_COLUMNS = {
    "sensor_id",
    "observed_count",
    "is_missing",
    "baseline_available",
    "baseline_confidence",
}
INTERPRETATION_FIELDS = (
    "primary_deviation_score",
    "primary_score_source",
    "observation_validity_state",
    "baseline_confidence_band",
    "deviation_direction",
    "deviation_magnitude_band",
    "signal_family",
    "signal_subtype",
    "candidate_readiness",
    "interpretation_warning",
    "interpretation_notes",
)

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
    "scoring_notes",
}
BOOLEAN_FIELDS = {
    "is_missing",
    "source_hour_present",
    "is_weekend",
    "is_public_holiday",
    "is_school_term",
    "is_school_holiday",
    "is_daylight_saving_transition",
    "is_regular_baseline_eligible",
    "baseline_available",
}
INTEGER_FIELDS = {
    "hour",
    "observed_count",
    "direction_1_count",
    "direction_2_count",
    "baseline_sample_size",
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
    "context_confidence",
    "baseline_median",
    "baseline_mean",
    "baseline_p05",
    "baseline_p25",
    "baseline_p75",
    "baseline_p95",
    "baseline_p99",
    "baseline_iqr",
    "baseline_mad",
    "activity_percentile",
    "baseline_ratio",
    "signed_deviation",
    "signed_deviation_ratio",
    "robust_z_score",
    "z_score",
    "standardized_deviation",
    "anomaly_strength",
    "scoring_confidence",
}

VALIDITY_STATES = {
    "observed_scored",
    "missing_observation",
    "unscored_observation",
    "baseline_unavailable",
    "invalid_count",
}
SIGNAL_FAMILIES = {
    "regular_pattern",
    "positive_deviation_signal",
    "negative_deviation_signal",
    "missingness_signal",
    "low_confidence_signal",
    "uninterpretable_signal",
}
CANDIDATE_READINESS_VALUES = {
    "not_candidate",
    "review_ready",
    "needs_context",
    "data_quality_review",
    "low_confidence_excluded",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Interpret scored deviations without extracting anomalies."
    )
    parser.add_argument("--sensor-mode", default=DEFAULT_SENSOR_MODE)
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Override the sensor-mode-aware processed output directory.",
    )
    return parser.parse_args()


def parse_bool(value: str | None) -> bool:
    return bool(value) and value.strip().lower() == "true"


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


def parse_list(value: str | None) -> list[str]:
    if value is None or value.strip() == "":
        return []
    parsed = json.loads(value)
    if not isinstance(parsed, list):
        raise ValueError(f"Expected JSON list, received: {value}")
    return [str(item) for item in parsed]


def select_primary_score(fieldnames: list[str]) -> str:
    missing_required = sorted(REQUIRED_COLUMNS - set(fieldnames))
    if "timestamp" not in fieldnames and "local_timestamp_key" not in fieldnames:
        missing_required.append("timestamp_or_local_timestamp_key")
    if missing_required:
        raise ValueError(
            "Phase 1D input is missing required scored-panel columns: "
            f"{', '.join(missing_required)}"
        )
    for field in PRIMARY_SCORE_PRIORITY:
        if field in fieldnames:
            return field
    raise ValueError(
        "Phase 1D requires a standardized deviation score. None of these "
        f"columns are available: {', '.join(PRIMARY_SCORE_PRIORITY)}"
    )


def read_scored_panel(
    input_file: Path,
) -> tuple[list[dict[str, Any]], list[str], str]:
    if not input_file.exists():
        raise FileNotFoundError(
            f"Scored panel not found: {input_file}. Run Phase 1C first."
        )

    rows: list[dict[str, Any]] = []
    with input_file.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        primary_score_source = select_primary_score(fieldnames)
        existing_interpretation = sorted(
            set(fieldnames).intersection(INTERPRETATION_FIELDS)
        )
        if existing_interpretation:
            raise ValueError(
                "Phase 1D input already contains interpretation fields: "
                f"{', '.join(existing_interpretation)}"
            )

        for raw in reader:
            row: dict[str, Any] = dict(raw)
            for field in LIST_FIELDS.intersection(row):
                row[field] = parse_list(raw[field])
            for field in BOOLEAN_FIELDS.intersection(row):
                row[field] = parse_bool(raw[field])
            for field in INTEGER_FIELDS.intersection(row):
                row[field] = parse_int(raw[field])
            for field in FLOAT_FIELDS.intersection(row):
                row[field] = parse_float(raw[field])
            rows.append(row)

    return rows, fieldnames, primary_score_source


def confidence_band(value: str | None) -> str:
    normalized = (value or "").strip().lower()
    if normalized == "high":
        return "high"
    if normalized == "medium":
        return "medium"
    if normalized in {"low", "insufficient"}:
        return "low"
    return "unavailable"


def validity_state(
    row: dict[str, Any],
    primary_score: float | None,
) -> str:
    if row.get("is_missing"):
        return "missing_observation"
    observed_count = row.get("observed_count")
    if observed_count is None or observed_count < 0:
        return "invalid_count"
    if not row.get("baseline_available"):
        return "baseline_unavailable"
    if primary_score is None:
        return "unscored_observation"
    return "observed_scored"


def magnitude_band(primary_score: float | None) -> str:
    if primary_score is None:
        return "not_scored"
    magnitude = abs(primary_score)
    if magnitude < 1:
        return "near_regular"
    if magnitude < 2:
        return "mild"
    if magnitude < 3:
        return "moderate"
    if magnitude < 5:
        return "strong"
    return "extreme"


def deviation_direction(
    primary_score: float | None,
    magnitude: str,
    validity: str,
) -> str:
    if validity != "observed_scored" or primary_score is None:
        return "not_applicable"
    if magnitude == "near_regular":
        return "near_baseline"
    return "above_baseline" if primary_score > 0 else "below_baseline"


def signal_classification(
    validity: str,
    baseline_band: str,
    direction: str,
    magnitude: str,
) -> tuple[str, str]:
    if validity == "missing_observation":
        return "missingness_signal", "missing_observation"
    if validity in {
        "invalid_count",
        "unscored_observation",
        "baseline_unavailable",
    }:
        subtype = (
            "unscored"
            if validity == "unscored_observation"
            else "invalid_or_uninterpretable"
        )
        return "uninterpretable_signal", subtype
    if baseline_band in {"low", "unavailable"}:
        return "low_confidence_signal", "baseline_confidence_limited"
    if magnitude == "near_regular":
        return "regular_pattern", "regular_flow"

    positive = direction == "above_baseline"
    if magnitude == "mild":
        subtype = (
            "mild_positive_variation"
            if positive
            else "mild_negative_variation"
        )
    elif magnitude == "moderate":
        subtype = (
            "moderate_positive_variation"
            if positive
            else "moderate_negative_variation"
        )
    elif magnitude == "strong":
        subtype = (
            "strong_positive_pulse"
            if positive
            else "strong_negative_suppression"
        )
    else:
        subtype = (
            "extreme_positive_pulse"
            if positive
            else "extreme_negative_suppression"
        )
    family = (
        "positive_deviation_signal"
        if positive
        else "negative_deviation_signal"
    )
    return family, subtype


def candidate_readiness(
    validity: str,
    baseline_band: str,
    magnitude: str,
    primary_score: float | None,
) -> str:
    if validity in {
        "missing_observation",
        "unscored_observation",
        "invalid_count",
        "baseline_unavailable",
    } or primary_score is None:
        return "data_quality_review"
    if baseline_band in {"low", "unavailable"}:
        return "low_confidence_excluded"
    if magnitude in {"near_regular", "mild", "moderate"}:
        return "not_candidate"
    if baseline_band == "high":
        return "review_ready"
    if baseline_band == "medium":
        return "needs_context"
    return "low_confidence_excluded"


def interpretation_warning(
    validity: str,
    baseline_band: str,
    primary_score: float | None,
) -> str:
    if validity == "missing_observation":
        return "missing_raw_observation"
    if validity == "invalid_count":
        return "invalid_count"
    if validity == "baseline_unavailable":
        return "baseline_unavailable"
    if primary_score is None:
        return "missing_primary_score"
    if validity == "unscored_observation":
        return "unscored_observation"
    if baseline_band == "low":
        return "low_baseline_confidence"
    if baseline_band == "unavailable":
        return "baseline_unavailable"
    if baseline_band == "medium":
        return "medium_baseline_confidence"
    return "none"


def interpret_row(
    row: dict[str, Any],
    primary_score_source: str,
) -> dict[str, Any]:
    primary_score = row.get(primary_score_source)
    validity = validity_state(row, primary_score)
    baseline_band = confidence_band(row.get("baseline_confidence"))
    magnitude = magnitude_band(primary_score)
    direction = deviation_direction(
        primary_score, magnitude, validity
    )
    family, subtype = signal_classification(
        validity, baseline_band, direction, magnitude
    )
    readiness = candidate_readiness(
        validity, baseline_band, magnitude, primary_score
    )
    warning = interpretation_warning(
        validity, baseline_band, primary_score
    )
    notes = (
        f"taxonomy=phase1d_v1;"
        f"score={primary_score_source};"
        f"state={validity};"
        f"band={magnitude}"
    )

    return {
        **row,
        "primary_deviation_score": primary_score,
        "primary_score_source": primary_score_source,
        "observation_validity_state": validity,
        "baseline_confidence_band": baseline_band,
        "deviation_direction": direction,
        "deviation_magnitude_band": magnitude,
        "signal_family": family,
        "signal_subtype": subtype,
        "candidate_readiness": readiness,
        "interpretation_warning": warning,
        "interpretation_notes": notes,
    }


def csv_value(field: str, value: Any) -> Any:
    if field in LIST_FIELDS:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value).lower()
    return value


def write_outputs(
    rows: list[dict[str, Any]],
    original_fieldnames: list[str],
    csv_output: Path,
    json_output: Path,
) -> None:
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [*original_fieldnames, *INTERPRETATION_FIELDS]
    with csv_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {field: csv_value(field, row[field]) for field in fieldnames}
            )

    with json_output.open("w", encoding="utf-8") as handle:
        json.dump(
            rows,
            handle,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        )


def build_diagnostics(
    rows: list[dict[str, Any]],
    input_row_count: int,
    sensor_mode: str,
    input_file: Path,
    csv_output: Path,
    json_output: Path,
    expected_row_count: int | None,
    primary_score_source: str,
    output_dir: Path,
) -> dict[str, Any]:
    validity_counts = Counter(
        row["observation_validity_state"] for row in rows
    )
    baseline_counts = Counter(
        row["baseline_confidence_band"] for row in rows
    )
    direction_counts = Counter(row["deviation_direction"] for row in rows)
    magnitude_counts = Counter(
        row["deviation_magnitude_band"] for row in rows
    )
    family_counts = Counter(row["signal_family"] for row in rows)
    subtype_counts = Counter(row["signal_subtype"] for row in rows)
    readiness_counts = Counter(row["candidate_readiness"] for row in rows)
    warning_counts = Counter(row["interpretation_warning"] for row in rows)

    missing_rows = [
        row
        for row in rows
        if row["observation_validity_state"] == "missing_observation"
    ]
    unscored_rows = [
        row
        for row in rows
        if row["observation_validity_state"] == "unscored_observation"
    ]
    low_confidence_rows = [
        row
        for row in rows
        if row["baseline_confidence_band"] in {"low", "unavailable"}
    ]
    review_ready_rows = [
        row for row in rows if row["candidate_readiness"] == "review_ready"
    ]
    anomaly_files = list(output_dir.glob("anomaly_candidates*"))

    sanity_checks = {
        "output_rows_equal_input_rows": len(rows) == input_row_count,
        "all_rows_have_primary_score_source": all(
            row["primary_score_source"] for row in rows
        ),
        "all_rows_have_validity_state": all(
            row["observation_validity_state"] in VALIDITY_STATES
            for row in rows
        ),
        "all_rows_have_signal_family": all(
            row["signal_family"] in SIGNAL_FAMILIES for row in rows
        ),
        "all_rows_have_candidate_readiness": all(
            row["candidate_readiness"] in CANDIDATE_READINESS_VALUES
            for row in rows
        ),
        "missing_observations_not_review_ready": all(
            row["candidate_readiness"] != "review_ready"
            for row in missing_rows
        ),
        "unscored_rows_not_review_ready": all(
            row["candidate_readiness"] != "review_ready"
            for row in unscored_rows
        ),
        "low_confidence_rows_not_review_ready": all(
            row["candidate_readiness"] != "review_ready"
            for row in low_confidence_rows
        ),
        "review_ready_rows_have_primary_score": all(
            row["primary_deviation_score"] is not None
            for row in review_ready_rows
        ),
        "review_ready_rows_are_observed_scored": all(
            row["observation_validity_state"] == "observed_scored"
            for row in review_ready_rows
        ),
        "review_ready_rows_have_high_baseline_confidence": all(
            row["baseline_confidence_band"] == "high"
            for row in review_ready_rows
        ),
        "no_final_anomaly_file_created": not anomaly_files,
    }
    if not all(sanity_checks.values()):
        raise ValueError(
            f"Phase 1D sanity checks failed: {sanity_checks}"
        )

    return {
        "processing_version": PROCESSING_VERSION,
        "sensor_mode": sensor_mode,
        "input_file": input_file.relative_to(ROOT).as_posix(),
        "output_files": [
            csv_output.relative_to(ROOT).as_posix(),
            json_output.relative_to(ROOT).as_posix(),
        ],
        "row_count": len(rows),
        "sensor_count": len({row["sensor_id"] for row in rows}),
        "expected_row_count": expected_row_count,
        "primary_score_source": primary_score_source,
        "validity_state_counts": dict(sorted(validity_counts.items())),
        "baseline_confidence_counts": dict(sorted(baseline_counts.items())),
        "deviation_direction_counts": dict(sorted(direction_counts.items())),
        "deviation_magnitude_band_counts": dict(
            sorted(magnitude_counts.items())
        ),
        "signal_family_counts": dict(sorted(family_counts.items())),
        "signal_subtype_counts": dict(sorted(subtype_counts.items())),
        "candidate_readiness_counts": dict(
            sorted(readiness_counts.items())
        ),
        "interpretation_warning_counts": dict(
            sorted(warning_counts.items())
        ),
        "review_ready_count": readiness_counts["review_ready"],
        "needs_context_count": readiness_counts["needs_context"],
        "data_quality_review_count": readiness_counts[
            "data_quality_review"
        ],
        "low_confidence_excluded_count": readiness_counts[
            "low_confidence_excluded"
        ],
        "sanity_checks": sanity_checks,
        "notes": [
            "Interpretation is rule-based and does not constitute anomaly extraction.",
            "Moderate deviations are not review-ready in Phase 1D.",
            "No real-world cause is inferred.",
        ],
    }


def main() -> None:
    args = parse_args()
    output_dir = resolve_output_dir(args.output_dir, args.sensor_mode)
    input_file = output_dir / "scored_analytical_panel.csv"
    csv_output = output_dir / "deviation_interpretation_panel.csv"
    json_output = output_dir / "deviation_interpretation_panel.json"
    diagnostics_output = output_dir / "phase1d_diagnostics.json"
    phase1c_diagnostics = output_dir / "phase1c_diagnostics.json"

    configured_sensor_ids = {
        row["sensor_id"] for row in load_sensor_selection(args.sensor_mode)
    }
    rows, original_fieldnames, primary_score_source = read_scored_panel(
        input_file
    )
    input_sensor_ids = {row["sensor_id"] for row in rows}
    if input_sensor_ids != configured_sensor_ids:
        raise ValueError(
            "Phase 1D input sensors do not match configured mode "
            f"{args.sensor_mode}: "
            f"configured={sorted(configured_sensor_ids, key=int)}, "
            f"input={sorted(input_sensor_ids, key=int)}"
        )

    expected_row_count: int | None = None
    if phase1c_diagnostics.exists():
        upstream = json.loads(
            phase1c_diagnostics.read_text(encoding="utf-8")
        )
        expected_row_count = int(upstream["output_row_count"])

    interpreted_rows = [
        interpret_row(row, primary_score_source) for row in rows
    ]
    diagnostics = build_diagnostics(
        interpreted_rows,
        len(rows),
        args.sensor_mode,
        input_file,
        csv_output,
        json_output,
        expected_row_count,
        primary_score_source,
        output_dir,
    )
    write_outputs(
        interpreted_rows,
        original_fieldnames,
        csv_output,
        json_output,
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
