"""Build Phase 1B empirical regular baseline distributions.

The script consumes the Phase 1A context-classified panel and calculates
sensor-specific distributions. It intentionally does not score observations,
extract anomalies, or build dashboard summaries.
"""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import fmean, median
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "processed" / "context_classified_panel.csv"
PHASE1A_DIAGNOSTICS = ROOT / "data" / "processed" / "phase1a_diagnostics.json"
OUTPUT_DIR = ROOT / "data" / "processed"
CSV_OUTPUT = OUTPUT_DIR / "regular_baselines.csv"
JSON_OUTPUT = OUTPUT_DIR / "regular_baselines.json"
DIAGNOSTICS_OUTPUT = OUTPUT_DIR / "phase1b_diagnostics.json"

PROCESSING_VERSION = "phase1b-0.1.0"
BASELINE_METHOD = "eligible regular observations grouped by sensor_id + weekday + hour"
BASELINE_POPULATION = (
    "is_regular_baseline_eligible=true, is_missing=false, observed_count present"
)
QUANTILE_METHOD = "linear interpolation at index (n - 1) * probability (Hyndman-Fan type 7)"
MAD_METHOD = "median of absolute deviations from the group median; unscaled"
EXPECTED_BASELINE_GROUP_COUNT = 3 * 7 * 24
WEEKDAY_ORDER = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}

# Provisional data-sufficiency labels for a one-year study period.
HIGH_SAMPLE_MIN = 40
MEDIUM_SAMPLE_MIN = 30
LOW_SAMPLE_MIN = 15

DISALLOWED_EXCLUSION_REASONS = {
    "public_holiday",
    "manual_event_window",
    "weather_disruption",
    "daylight_saving_transition",
    "missing_observation",
    "low_confidence_observation",
}


def parse_bool(value: str | None) -> bool:
    return bool(value) and value.strip().lower() == "true"


def parse_int(value: str | None) -> int | None:
    if value is None or value.strip() == "":
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def parse_list(value: str | None) -> list[str]:
    if value is None or value.strip() == "":
        return []
    parsed = json.loads(value)
    if not isinstance(parsed, list):
        raise ValueError(f"Expected JSON list, received: {value}")
    return [str(item) for item in parsed]


def quantile(sorted_values: list[int], probability: float) -> float:
    """Return a type-7 linearly interpolated sample quantile."""
    if not sorted_values:
        raise ValueError("Quantile requires at least one value.")
    if not 0 <= probability <= 1:
        raise ValueError("Quantile probability must be between 0 and 1.")
    position = (len(sorted_values) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(sorted_values[lower])
    weight = position - lower
    return float(
        sorted_values[lower] + weight * (sorted_values[upper] - sorted_values[lower])
    )


def confidence_for_sample_size(sample_size: int) -> str:
    if sample_size >= HIGH_SAMPLE_MIN:
        return "high"
    if sample_size >= MEDIUM_SAMPLE_MIN:
        return "medium"
    if sample_size >= LOW_SAMPLE_MIN:
        return "low"
    return "insufficient"


def rounded(value: float) -> float:
    return round(value, 3)


def load_phase1a_metadata() -> dict[str, Any]:
    if not PHASE1A_DIAGNOSTICS.exists():
        return {}
    return json.loads(PHASE1A_DIAGNOSTICS.read_text(encoding="utf-8"))


def read_input() -> tuple[
    list[dict[str, Any]],
    dict[tuple[str, str, int], list[int]],
    dict[str, str],
    dict[str, Any],
]:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"{INPUT_FILE} does not exist. Run Phase 1A classification first."
        )

    rows: list[dict[str, Any]] = []
    grouped: dict[tuple[str, str, int], list[int]] = defaultdict(list)
    sensor_names: dict[str, str] = {}
    checks = {
        "eligible_rows_with_missing_observation": 0,
        "eligible_rows_with_disallowed_exclusion_reason": 0,
        "eligible_rows_with_disallowed_exclusion_details": Counter(),
        "included_ineligible_rows": 0,
        "included_missing_rows": 0,
    }

    with INPUT_FILE.open("r", encoding="utf-8", newline="") as handle:
        for raw in csv.DictReader(handle):
            eligible = parse_bool(raw.get("is_regular_baseline_eligible"))
            is_missing = parse_bool(raw.get("is_missing"))
            observed_count = parse_int(raw.get("observed_count"))
            exclusion_reasons = parse_list(raw.get("baseline_exclusion_reasons"))
            hour = parse_int(raw.get("hour"))
            sensor_id = raw.get("sensor_id", "")
            weekday = raw.get("weekday", "")

            row = {
                "sensor_id": sensor_id,
                "sensor_name": raw.get("sensor_name", ""),
                "weekday": weekday,
                "hour": hour,
                "observed_count": observed_count,
                "is_missing": is_missing,
                "is_regular_baseline_eligible": eligible,
                "baseline_exclusion_reasons": exclusion_reasons,
            }
            rows.append(row)
            sensor_names[sensor_id] = row["sensor_name"]

            disallowed = DISALLOWED_EXCLUSION_REASONS.intersection(exclusion_reasons)
            if eligible and is_missing:
                checks["eligible_rows_with_missing_observation"] += 1
            if eligible and disallowed:
                checks["eligible_rows_with_disallowed_exclusion_reason"] += 1
                checks["eligible_rows_with_disallowed_exclusion_details"].update(disallowed)

            include = eligible and not is_missing and observed_count is not None
            if include:
                if not eligible:
                    checks["included_ineligible_rows"] += 1
                if is_missing:
                    checks["included_missing_rows"] += 1
                if hour is None or weekday not in WEEKDAY_ORDER or not sensor_id:
                    raise ValueError(f"Invalid baseline group identity: {row}")
                grouped[(sensor_id, weekday, hour)].append(observed_count)

    checks["eligible_rows_with_disallowed_exclusion_details"] = dict(
        checks["eligible_rows_with_disallowed_exclusion_details"]
    )
    return rows, grouped, sensor_names, checks


def build_baselines(
    grouped: dict[tuple[str, str, int], list[int]],
    sensor_names: dict[str, str],
    study_period: dict[str, Any],
) -> list[dict[str, Any]]:
    baselines: list[dict[str, Any]] = []
    for (sensor_id, weekday, hour), values in grouped.items():
        sorted_values = sorted(values)
        group_median = float(median(sorted_values))
        p05 = quantile(sorted_values, 0.05)
        p25 = quantile(sorted_values, 0.25)
        p75 = quantile(sorted_values, 0.75)
        p95 = quantile(sorted_values, 0.95)
        p99 = quantile(sorted_values, 0.99)
        absolute_deviations = sorted(abs(value - group_median) for value in sorted_values)
        group_mad = float(median(absolute_deviations))
        sample_size = len(sorted_values)

        baselines.append(
            {
                "sensor_id": sensor_id,
                "sensor_name": sensor_names.get(sensor_id, ""),
                "weekday": weekday,
                "hour": hour,
                "sample_size": sample_size,
                "median": rounded(group_median),
                "mean": rounded(fmean(sorted_values)),
                "min": min(sorted_values),
                "max": max(sorted_values),
                "p05": rounded(p05),
                "p25": rounded(p25),
                "p75": rounded(p75),
                "p95": rounded(p95),
                "p99": rounded(p99),
                "iqr": rounded(p75 - p25),
                "mad": rounded(group_mad),
                "baseline_confidence": confidence_for_sample_size(sample_size),
                "baseline_method": BASELINE_METHOD,
                "quantile_method": QUANTILE_METHOD,
                "baseline_population": BASELINE_POPULATION,
                "fallback_used": False,
                "fallback_level": "none",
                "fallback_reason": "",
                "processing_version": PROCESSING_VERSION,
                "study_period_start": study_period.get("start", "2025-01-01T00:00:00"),
                "study_period_end": study_period.get("end", "2025-12-31T23:00:00"),
            }
        )

    return sorted(
        baselines,
        key=lambda row: (
            int(row["sensor_id"]),
            WEEKDAY_ORDER[row["weekday"]],
            row["hour"],
        ),
    )


def write_outputs(baselines: list[dict[str, Any]]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = list(baselines[0])
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(baselines)

    with JSON_OUTPUT.open("w", encoding="utf-8") as handle:
        json.dump(baselines, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def sample_size_summary(baselines: list[dict[str, Any]]) -> dict[str, float]:
    sizes = sorted(row["sample_size"] for row in baselines)
    if not sizes:
        return {"min": 0, "max": 0, "mean": 0.0, "median": 0.0}
    return {
        "min": min(sizes),
        "max": max(sizes),
        "mean": rounded(fmean(sizes)),
        "median": rounded(float(median(sizes))),
    }


def compact_group(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "sensor_id": row["sensor_id"],
        "weekday": row["weekday"],
        "hour": row["hour"],
        "sample_size": row["sample_size"],
        "baseline_confidence": row["baseline_confidence"],
    }


def build_diagnostics(
    input_rows: list[dict[str, Any]],
    baselines: list[dict[str, Any]],
    checks: dict[str, Any],
    phase1a: dict[str, Any],
) -> dict[str, Any]:
    eligible_count = sum(
        1 for row in input_rows if row["is_regular_baseline_eligible"]
    )
    baseline_population_count = sum(
        1
        for row in input_rows
        if row["is_regular_baseline_eligible"]
        and not row["is_missing"]
        and row["observed_count"] is not None
    )
    confidence_counts = Counter(row["baseline_confidence"] for row in baselines)
    groups_by_sensor = Counter(row["sensor_id"] for row in baselines)
    groups_by_weekday = Counter(row["weekday"] for row in baselines)
    low_groups = [
        compact_group(row) for row in baselines if row["baseline_confidence"] == "low"
    ]
    insufficient_groups = [
        compact_group(row)
        for row in baselines
        if row["baseline_confidence"] == "insufficient"
    ]
    missing_group_count = EXPECTED_BASELINE_GROUP_COUNT - len(baselines)
    implausible_groups = [
        compact_group(row)
        for row in baselines
        if row["sample_size"] < 1 or row["sample_size"] > 53
    ]

    warnings = [
        "Baseline confidence labels are provisional data-sufficiency labels, not a validated confidence model.",
        "School holidays remain in the eligible population when Phase 1A marks them eligible.",
        "No fallback baselines are substituted in Phase 1B.",
        "A one-year sensor_id + weekday + hour group can contain at most about 52-53 observations before exclusions.",
    ]
    if missing_group_count:
        warnings.append(
            f"{missing_group_count} expected sensor/weekday/hour groups have no baseline output."
        )
    if low_groups:
        warnings.append(f"{len(low_groups)} baseline groups have low sample sufficiency.")
    if insufficient_groups:
        warnings.append(
            f"{len(insufficient_groups)} baseline groups have insufficient sample sufficiency."
        )
    if implausible_groups:
        warnings.append(
            f"{len(implausible_groups)} groups have sample sizes outside the expected one-year range."
        )

    sanity_checks = {
        "no_ineligible_rows_used": checks["included_ineligible_rows"] == 0,
        "no_missing_rows_used": checks["included_missing_rows"] == 0,
        "no_eligible_rows_carry_disallowed_exclusions": (
            checks["eligible_rows_with_disallowed_exclusion_reason"] == 0
        ),
        "no_eligible_rows_marked_missing": (
            checks["eligible_rows_with_missing_observation"] == 0
        ),
        "baseline_group_count_not_above_expected": (
            len(baselines) <= EXPECTED_BASELINE_GROUP_COUNT
        ),
        "sample_sizes_plausible_for_one_year": not implausible_groups,
    }
    if not all(sanity_checks.values()):
        raise ValueError(f"Phase 1B sanity checks failed: {sanity_checks}; details={checks}")

    selected_sensor_ids = sorted(
        {row["sensor_id"] for row in input_rows}, key=int
    )
    study_period = phase1a.get(
        "study_period",
        {
            "start": "2025-01-01T00:00:00",
            "end": "2025-12-31T23:00:00",
            "timezone": "Australia/Melbourne",
        },
    )
    return {
        "processing_version": PROCESSING_VERSION,
        "input_file": INPUT_FILE.relative_to(ROOT).as_posix(),
        "output_files": [
            CSV_OUTPUT.relative_to(ROOT).as_posix(),
            JSON_OUTPUT.relative_to(ROOT).as_posix(),
        ],
        "study_period": study_period,
        "selected_sensor_ids": selected_sensor_ids,
        "input_row_count": len(input_rows),
        "eligible_input_row_count": eligible_count,
        "ineligible_input_row_count": len(input_rows) - eligible_count,
        "baseline_population_row_count": baseline_population_count,
        "baseline_group_count": len(baselines),
        "expected_baseline_group_count": EXPECTED_BASELINE_GROUP_COUNT,
        "missing_baseline_group_count": missing_group_count,
        "sample_size_summary": sample_size_summary(baselines),
        "baseline_confidence_counts": {
            label: confidence_counts.get(label, 0)
            for label in ("high", "medium", "low", "insufficient")
        },
        "low_sample_groups": low_groups,
        "insufficient_sample_groups": insufficient_groups,
        "groups_by_sensor": dict(sorted(groups_by_sensor.items(), key=lambda item: int(item[0]))),
        "groups_by_weekday": {
            weekday: groups_by_weekday.get(weekday, 0)
            for weekday in WEEKDAY_ORDER
        },
        "fallback_groups_count": sum(1 for row in baselines if row["fallback_used"]),
        "confidence_thresholds": {
            "high": f"sample_size >= {HIGH_SAMPLE_MIN}",
            "medium": f"{MEDIUM_SAMPLE_MIN} <= sample_size < {HIGH_SAMPLE_MIN}",
            "low": f"{LOW_SAMPLE_MIN} <= sample_size < {MEDIUM_SAMPLE_MIN}",
            "insufficient": f"sample_size < {LOW_SAMPLE_MIN}",
        },
        "sanity_checks": sanity_checks,
        "sanity_check_details": checks,
        "warnings": warnings,
        "notes": {
            "baseline_method": BASELINE_METHOD,
            "baseline_population": BASELINE_POPULATION,
            "quantile_method": QUANTILE_METHOD,
            "mad_method": MAD_METHOD,
            "mean_role": "descriptive only; median and percentiles define the baseline distribution",
            "fallback_policy": "no fallback substitution in Phase 1B",
        },
    }


def main() -> None:
    phase1a = load_phase1a_metadata()
    input_rows, grouped, sensor_names, checks = read_input()
    study_period = phase1a.get("study_period", {})
    baselines = build_baselines(grouped, sensor_names, study_period)
    if not baselines:
        raise ValueError("No regular baseline groups could be constructed.")
    write_outputs(baselines)
    diagnostics = build_diagnostics(input_rows, baselines, checks, phase1a)
    with DIAGNOSTICS_OUTPUT.open("w", encoding="utf-8") as handle:
        json.dump(diagnostics, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps(diagnostics, indent=2))


if __name__ == "__main__":
    main()
