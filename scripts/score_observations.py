"""Score Phase 1A observations against Phase 1B regular baselines.

This Phase 1C stage preserves every context-classified row and adds transparent
baseline-relative measures. It does not extract anomaly candidates, generate
event explanations, or build dashboard summaries.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path
from statistics import fmean, median
from typing import Any

from analysis_config import (
    DEFAULT_SENSOR_MODE,
    ROOT,
    load_sensor_selection,
    resolve_output_dir,
)

PROCESSING_VERSION = "phase1c-0.1.0"
SCORING_CONFIDENCE_BY_BASELINE_LABEL = {
    "high": 0.9,
    "medium": 0.75,
    "low": 0.5,
    "insufficient": 0.25,
}
ROBUST_Z_NEAR_NORMAL_LIMIT = 0.5
ROBUST_Z_FULL_STRENGTH = 3.0

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
}
INTEGER_FIELDS = {
    "hour",
    "observed_count",
    "direction_1_count",
    "direction_2_count",
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
}
BASELINE_FLOAT_FIELDS = {
    "median",
    "mean",
    "p05",
    "p25",
    "p75",
    "p95",
    "p99",
    "iqr",
    "mad",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Score observations against regular baselines."
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
        return int(float(value))
    except ValueError:
        return None


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


def rounded(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value, 4)


def load_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_baselines(
    baseline_input: Path,
) -> dict[tuple[str, str, int], dict[str, Any]]:
    if not baseline_input.exists():
        raise FileNotFoundError(
            f"{baseline_input} does not exist. Run Phase 1B first."
        )

    baselines: dict[tuple[str, str, int], dict[str, Any]] = {}
    with baseline_input.open("r", encoding="utf-8", newline="") as handle:
        for raw in csv.DictReader(handle):
            hour = parse_int(raw.get("hour"))
            if hour is None:
                raise ValueError(f"Baseline row has invalid hour: {raw}")
            key = (raw.get("sensor_id", ""), raw.get("weekday", ""), hour)
            if key in baselines:
                raise ValueError(f"Duplicate baseline join key: {key}")
            baseline = {
                "baseline_sample_size": parse_int(raw.get("sample_size")),
                "baseline_median": parse_float(raw.get("median")),
                "baseline_mean": parse_float(raw.get("mean")),
                "baseline_p05": parse_float(raw.get("p05")),
                "baseline_p25": parse_float(raw.get("p25")),
                "baseline_p75": parse_float(raw.get("p75")),
                "baseline_p95": parse_float(raw.get("p95")),
                "baseline_p99": parse_float(raw.get("p99")),
                "baseline_iqr": parse_float(raw.get("iqr")),
                "baseline_mad": parse_float(raw.get("mad")),
                "baseline_confidence": raw.get("baseline_confidence", ""),
                "baseline_method": raw.get("baseline_method", ""),
                "quantile_method": raw.get("quantile_method", ""),
                "baseline_processing_version": raw.get("processing_version", ""),
            }
            if any(
                baseline[f"baseline_{field}"] is None
                for field in BASELINE_FLOAT_FIELDS
            ):
                raise ValueError(f"Baseline contains missing statistics for key {key}.")
            baselines[key] = baseline
    return baselines


def read_panel(panel_input: Path) -> list[dict[str, Any]]:
    if not panel_input.exists():
        raise FileNotFoundError(
            f"{panel_input} does not exist. Run Phase 1A classification first."
        )

    rows: list[dict[str, Any]] = []
    with panel_input.open("r", encoding="utf-8", newline="") as handle:
        for raw in csv.DictReader(handle):
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
    return rows


def interpolate(x: float, x0: float, p0: float, x1: float, p1: float) -> float:
    if x1 <= x0:
        return p1
    fraction = (x - x0) / (x1 - x0)
    return p0 + fraction * (p1 - p0)


def approximate_activity_percentile(
    observed: float, baseline: dict[str, Any]
) -> float:
    """Map an observation monotonically through stored percentile anchors."""
    anchors = [
        (baseline["baseline_p05"], 0.05),
        (baseline["baseline_p25"], 0.25),
        (baseline["baseline_median"], 0.50),
        (baseline["baseline_p75"], 0.75),
        (baseline["baseline_p95"], 0.95),
        (baseline["baseline_p99"], 0.99),
    ]

    first_value = anchors[0][0]
    if observed <= first_value:
        if first_value > 0:
            return max(0.0, min(0.05, 0.05 * max(observed, 0.0) / first_value))
        return 0.05 if observed == first_value else 0.0

    for (lower_value, lower_percentile), (
        upper_value,
        upper_percentile,
    ) in zip(anchors, anchors[1:]):
        if observed <= upper_value:
            return max(
                0.0,
                min(
                    1.0,
                    interpolate(
                        observed,
                        lower_value,
                        lower_percentile,
                        upper_value,
                        upper_percentile,
                    ),
                ),
            )

    p95 = baseline["baseline_p95"]
    p99 = baseline["baseline_p99"]
    upper_span = max(p99 - p95, 1.0)
    return min(1.0, 0.99 + 0.01 * (observed - p99) / upper_span)


def anomaly_strength_from_robust_z(robust_z: float) -> float:
    magnitude = abs(robust_z)
    if magnitude <= ROBUST_Z_NEAR_NORMAL_LIMIT:
        return 0.0
    return min(
        1.0,
        (magnitude - ROBUST_Z_NEAR_NORMAL_LIMIT)
        / (ROBUST_Z_FULL_STRENGTH - ROBUST_Z_NEAR_NORMAL_LIMIT),
    )


def anomaly_strength_from_percentile(activity_percentile: float) -> float:
    extremeness = abs(activity_percentile - 0.5)
    if extremeness <= 0.25:
        return 0.0
    return min(1.0, (extremeness - 0.25) / 0.25)


def score_row(
    row: dict[str, Any],
    baselines: dict[tuple[str, str, int], dict[str, Any]],
) -> dict[str, Any]:
    key = (row["sensor_id"], row["weekday"], row["hour"])
    baseline = baselines.get(key)
    baseline_available = baseline is not None
    notes: list[str] = []

    baseline_fields = baseline or {
        "baseline_sample_size": None,
        "baseline_median": None,
        "baseline_mean": None,
        "baseline_p05": None,
        "baseline_p25": None,
        "baseline_p75": None,
        "baseline_p95": None,
        "baseline_p99": None,
        "baseline_iqr": None,
        "baseline_mad": None,
        "baseline_confidence": "",
        "baseline_method": "",
        "quantile_method": "",
        "baseline_processing_version": "",
    }

    observed = row.get("observed_count")
    signed_deviation: float | None = None
    baseline_ratio: float | None = None
    signed_deviation_ratio: float | None = None
    robust_z_score: float | None = None
    activity_percentile: float | None = None
    anomaly_strength: float | None = None
    anomaly_direction = "unavailable"
    scoring_confidence = 0.0

    if observed is None or row.get("is_missing"):
        notes.append("missing_observation_no_numeric_scores")
    elif not baseline_available:
        notes.append("baseline_unavailable_for_join_key")
    else:
        baseline_median = baseline_fields["baseline_median"]
        if baseline_median is None:
            notes.append("baseline_median_unavailable")
        else:
            signed_deviation = observed - baseline_median
            if signed_deviation > 0:
                anomaly_direction = "above"
            elif signed_deviation < 0:
                anomaly_direction = "below"
            else:
                anomaly_direction = "none"

            if baseline_median == 0:
                notes.append("baseline_median_zero_ratio_unavailable")
            else:
                baseline_ratio = observed / baseline_median
                signed_deviation_ratio = signed_deviation / baseline_median

            activity_percentile = approximate_activity_percentile(observed, baseline_fields)

            mad = baseline_fields["baseline_mad"]
            iqr = baseline_fields["baseline_iqr"]
            if mad is not None and mad > 0:
                robust_z_score = signed_deviation / mad
                notes.append("robust_z_scale_mad")
            elif iqr is not None and iqr > 0:
                robust_z_score = signed_deviation / iqr
                notes.append("robust_z_scale_iqr_fallback")
            else:
                notes.append("robust_z_scale_unavailable")

            if robust_z_score is not None:
                anomaly_strength = anomaly_strength_from_robust_z(robust_z_score)
            elif activity_percentile is not None:
                anomaly_strength = anomaly_strength_from_percentile(activity_percentile)
                notes.append("anomaly_strength_percentile_fallback")

            baseline_confidence_value = SCORING_CONFIDENCE_BY_BASELINE_LABEL.get(
                baseline_fields["baseline_confidence"], 0.0
            )
            observation_confidence = row.get("observation_confidence") or 0.0
            scoring_confidence = min(
                max(observation_confidence, 0.0),
                baseline_confidence_value,
            )

    return {
        **row,
        **baseline_fields,
        "baseline_available": baseline_available,
        "activity_percentile": rounded(activity_percentile),
        "baseline_ratio": rounded(baseline_ratio),
        "signed_deviation": rounded(signed_deviation),
        "signed_deviation_ratio": rounded(signed_deviation_ratio),
        "robust_z_score": rounded(robust_z_score),
        "anomaly_strength": rounded(anomaly_strength),
        "anomaly_direction": anomaly_direction,
        "scoring_confidence": rounded(scoring_confidence),
        "scoring_notes": notes,
        "scoring_processing_version": PROCESSING_VERSION,
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
    csv_output: Path,
    json_output: Path,
) -> None:
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0])
    with csv_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_value(field, row[field]) for field in fieldnames})

    with json_output.open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def numeric_summary(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"min": None, "max": None, "mean": None, "median": None}
    ordered = sorted(values)
    return {
        "min": rounded(min(ordered)),
        "max": rounded(max(ordered)),
        "mean": rounded(fmean(ordered)),
        "median": rounded(float(median(ordered))),
    }


def build_diagnostics(
    input_rows: list[dict[str, Any]],
    output_rows: list[dict[str, Any]],
    baselines: dict[tuple[str, str, int], dict[str, Any]],
    sensor_mode: str,
    panel_input: Path,
    baseline_input: Path,
    csv_output: Path,
    json_output: Path,
    phase1a_diagnostics: Path,
    phase1b_diagnostics: Path,
) -> dict[str, Any]:
    baseline_join_success_count = sum(
        1 for row in output_rows if row["baseline_available"]
    )
    baseline_join_missing_count = len(output_rows) - baseline_join_success_count
    missing_observation_count = sum(1 for row in output_rows if row["is_missing"])
    scored_observation_count = sum(
        1
        for row in output_rows
        if row["observed_count"] is not None
        and row["baseline_available"]
        and row["signed_deviation"] is not None
    )
    unscored_observation_count = len(output_rows) - scored_observation_count
    zero_or_invalid_baseline_median_count = sum(
        1
        for row in output_rows
        if row["observed_count"] is not None
        and row["baseline_available"]
        and (
            row["baseline_median"] is None
            or row["baseline_median"] == 0
        )
    )
    zero_or_invalid_scale_count = sum(
        1
        for row in output_rows
        if row["observed_count"] is not None
        and row["baseline_available"]
        and not (
            (row["baseline_mad"] is not None and row["baseline_mad"] > 0)
            or (row["baseline_iqr"] is not None and row["baseline_iqr"] > 0)
        )
    )
    mad_fallback_count = sum(
        1
        for row in output_rows
        if "robust_z_scale_iqr_fallback" in row["scoring_notes"]
    )
    direction_counts = Counter(row["anomaly_direction"] for row in output_rows)
    baseline_confidence_counts = Counter(
        row["baseline_confidence"]
        for row in output_rows
        if row["baseline_available"]
    )
    primary_context_counts = Counter(row["primary_context"] for row in output_rows)
    anomaly_strength_values = [
        row["anomaly_strength"]
        for row in output_rows
        if row["anomaly_strength"] is not None
    ]
    scoring_confidence_values = [
        row["scoring_confidence"]
        for row in output_rows
        if row["scoring_confidence"] is not None
    ]

    missing_rows_with_scores = [
        row
        for row in output_rows
        if row["is_missing"]
        and any(
            row[field] is not None
            for field in (
                "activity_percentile",
                "baseline_ratio",
                "signed_deviation",
                "signed_deviation_ratio",
                "robust_z_score",
                "anomaly_strength",
            )
        )
    ]
    nonmissing_rows_without_baseline = [
        row
        for row in output_rows
        if not row["is_missing"]
        and row["observed_count"] is not None
        and not row["baseline_available"]
    ]
    direction_mismatches = [
        row
        for row in output_rows
        if row["signed_deviation"] is not None
        and (
            (row["signed_deviation"] > 0 and row["anomaly_direction"] != "above")
            or (row["signed_deviation"] < 0 and row["anomaly_direction"] != "below")
            or (row["signed_deviation"] == 0 and row["anomaly_direction"] != "none")
            or (
                row["robust_z_score"] is not None
                and row["signed_deviation"] * row["robust_z_score"] < 0
            )
        )
    ]
    invalid_strength_rows = [
        row
        for row in output_rows
        if row["anomaly_strength"] is not None
        and not 0 <= row["anomaly_strength"] <= 1
    ]
    invalid_percentile_rows = [
        row
        for row in output_rows
        if row["activity_percentile"] is not None
        and not 0 <= row["activity_percentile"] <= 1
    ]
    panel_join_keys = {
        (row["sensor_id"], row["weekday"], row["hour"]) for row in input_rows
    }
    baseline_sensor_ids = {key[0] for key in baselines}
    expected_baseline_group_count = len(baseline_sensor_ids) * 7 * 24

    sanity_checks = {
        "output_row_count_equals_input": len(output_rows) == len(input_rows),
        "no_rows_dropped": len(output_rows) == len(input_rows),
        "missing_observations_have_no_numeric_scores": not missing_rows_with_scores,
        "all_nonmissing_rows_have_baseline": not nonmissing_rows_without_baseline,
        "baseline_file_has_expected_dynamic_key_count": len(baselines)
        == expected_baseline_group_count,
        "all_panel_join_keys_covered": panel_join_keys.issubset(baselines.keys()),
        "score_direction_preserved": not direction_mismatches,
        "anomaly_strength_within_unit_interval": not invalid_strength_rows,
        "activity_percentile_within_unit_interval": not invalid_percentile_rows,
    }
    if not all(sanity_checks.values()):
        raise ValueError(
            "Phase 1C sanity checks failed: "
            f"{sanity_checks}; missing-score rows={len(missing_rows_with_scores)}, "
            f"nonmissing without baseline={len(nonmissing_rows_without_baseline)}, "
            f"direction mismatches={len(direction_mismatches)}"
        )

    warnings = [
        "Activity percentile is an approximation from stored percentile anchors, not an empirical rank from the full baseline sample.",
        "Robust z-score uses raw unscaled MAD and falls back to IQR only when MAD is zero or unavailable.",
        "Anomaly strength is a provisional bounded encoding, not anomaly detection or a candidate classification.",
        "Scoring confidence is a provisional reliability measure and is not activity intensity.",
        "Special-context observations are compared with regular baselines while retaining their original context tags.",
    ]
    if baseline_join_missing_count:
        warnings.append(
            f"{baseline_join_missing_count} rows did not match a regular baseline."
        )
    if zero_or_invalid_baseline_median_count:
        warnings.append(
            f"{zero_or_invalid_baseline_median_count} scored rows have a zero or invalid baseline median."
        )
    if zero_or_invalid_scale_count:
        warnings.append(
            f"{zero_or_invalid_scale_count} scored rows have no valid MAD or IQR scale."
        )

    return {
        "processing_version": PROCESSING_VERSION,
        "sensor_mode": sensor_mode,
        "input_files": [
            panel_input.relative_to(ROOT).as_posix(),
            baseline_input.relative_to(ROOT).as_posix(),
        ],
        "output_files": [
            csv_output.relative_to(ROOT).as_posix(),
            json_output.relative_to(ROOT).as_posix(),
        ],
        "input_row_count": len(input_rows),
        "output_row_count": len(output_rows),
        "baseline_join_success_count": baseline_join_success_count,
        "baseline_join_missing_count": baseline_join_missing_count,
        "scored_observation_count": scored_observation_count,
        "unscored_observation_count": unscored_observation_count,
        "missing_observation_count": missing_observation_count,
        "baseline_unavailable_count": baseline_join_missing_count,
        "zero_or_invalid_baseline_median_count": zero_or_invalid_baseline_median_count,
        "zero_or_invalid_scale_count": zero_or_invalid_scale_count,
        "mad_to_iqr_fallback_count": mad_fallback_count,
        "activity_percentile_null_count": sum(
            1 for row in output_rows if row["activity_percentile"] is None
        ),
        "robust_z_score_null_count": sum(
            1 for row in output_rows if row["robust_z_score"] is None
        ),
        "anomaly_direction_counts": {
            label: direction_counts.get(label, 0)
            for label in ("above", "below", "none", "unavailable")
        },
        "anomaly_strength_summary": numeric_summary(anomaly_strength_values),
        "scoring_confidence_summary": numeric_summary(scoring_confidence_values),
        "baseline_confidence_counts_in_scored_panel": {
            label: baseline_confidence_counts.get(label, 0)
            for label in ("high", "medium", "low", "insufficient")
        },
        "rows_by_primary_context": dict(sorted(primary_context_counts.items())),
        "baseline_join_key_count": len(baselines),
        "expected_baseline_join_key_count": expected_baseline_group_count,
        "panel_join_key_count": len(panel_join_keys),
        "selected_sensor_count": len(baseline_sensor_ids),
        "selected_sensor_ids": sorted(baseline_sensor_ids, key=int),
        "sanity_checks": sanity_checks,
        "warnings": warnings,
        "notes": {
            "signed_deviation": "observed_count - baseline_median",
            "baseline_ratio": "observed_count / baseline_median",
            "signed_deviation_ratio": "(observed_count - baseline_median) / baseline_median",
            "robust_z_score": "signed_deviation / MAD; IQR fallback when MAD <= 0 or unavailable",
            "activity_percentile": "monotonic piecewise-linear approximation through p05, p25, median, p75, p95, and p99",
            "anomaly_strength": "0 through |robust_z| <= 0.5, linear to 1 at |robust_z| = 3, then capped; percentile fallback only when robust scale is unavailable",
            "scoring_confidence": "minimum of observation confidence and baseline-label reliability weight",
            "baseline_confidence_weights": SCORING_CONFIDENCE_BY_BASELINE_LABEL,
            "phase1a_diagnostics_available": phase1a_diagnostics.exists(),
            "phase1b_diagnostics_available": phase1b_diagnostics.exists(),
        },
    }


def main() -> None:
    args = parse_args()
    output_dir = resolve_output_dir(args.output_dir, args.sensor_mode)
    panel_input = output_dir / "context_classified_panel.csv"
    baseline_input = output_dir / "regular_baselines.csv"
    phase1a_diagnostics = output_dir / "phase1a_diagnostics.json"
    phase1b_diagnostics = output_dir / "phase1b_diagnostics.json"
    csv_output = output_dir / "scored_analytical_panel.csv"
    json_output = output_dir / "scored_analytical_panel.json"
    diagnostics_output = output_dir / "phase1c_diagnostics.json"
    configured_sensor_ids = {
        row["sensor_id"] for row in load_sensor_selection(args.sensor_mode)
    }
    # Read optional diagnostics to verify that upstream metadata remains valid
    # and available, while keeping the scored-row contract driven by CSV inputs.
    load_optional_json(phase1a_diagnostics)
    load_optional_json(phase1b_diagnostics)
    baselines = read_baselines(baseline_input)
    input_rows = read_panel(panel_input)
    input_sensor_ids = {row["sensor_id"] for row in input_rows}
    baseline_sensor_ids = {key[0] for key in baselines}
    if not (
        configured_sensor_ids
        == input_sensor_ids
        == baseline_sensor_ids
    ):
        raise ValueError(
            "Sensor-set mismatch for scoring mode "
            f"{args.sensor_mode}: "
            f"configured_sensor_ids={sorted(configured_sensor_ids, key=int)}, "
            f"input_sensor_ids={sorted(input_sensor_ids, key=int)}, "
            f"baseline_sensor_ids={sorted(baseline_sensor_ids, key=int)}"
        )
    output_rows = [score_row(row, baselines) for row in input_rows]
    diagnostics = build_diagnostics(
        input_rows,
        output_rows,
        baselines,
        args.sensor_mode,
        panel_input,
        baseline_input,
        csv_output,
        json_output,
        phase1a_diagnostics,
        phase1b_diagnostics,
    )
    write_outputs(output_rows, csv_output, json_output)
    with diagnostics_output.open("w", encoding="utf-8") as handle:
        json.dump(diagnostics, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps(diagnostics, indent=2))


if __name__ == "__main__":
    main()
