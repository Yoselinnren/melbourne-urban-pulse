"""Profile 2025 sensor coverage and generate named analytical sensor sets."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from analysis_config import DEFAULT_OUTPUT_DIR, ROOT, resolve_output_dir


PEDESTRIAN_FILE = (
    ROOT / "data" / "raw" / "pedestrian" / "pedestrian_counts_hourly_full.csv"
)
SENSOR_FILE = (
    ROOT / "data" / "raw" / "sensors" / "pedestrian_sensor_locations.csv"
)
SELECTION_CONFIG = (
    ROOT / "data" / "metadata" / "analysis_sensor_selection.csv"
)
STUDY_START = date(2025, 1, 1)
STUDY_END = date(2025, 12, 31)
EXPECTED_HOURS = 8760
PROCESSING_VERSION = "phase1s-0.1.0"

MVP_3_IDS = ("4", "3", "133")
REPRESENTATIVE_12_IDS = (
    "4",    # civic core
    "3",    # central retail/transit
    "133",  # Southern Cross / Lonsdale
    "209",  # Flinders transport underpass
    "79",   # Flinders Street south
    "59",   # RMIT / education
    "49",   # Queen Victoria Market
    "212",  # Southbank / river
    "66",   # QV / Swanston retail
    "58",   # Bourke / Spencer west CBD
    "23",   # Spencer / Collins transport-west
    "132",  # King / La Trobe north-west CBD
)
REPRESENTATIVE_REASONS = {
    "4": "Civic core anchor with near-complete coverage.",
    "3": "Central retail and Melbourne Central transport anchor.",
    "133": "Southern Cross Lonsdale entrance; west-CBD station anchor.",
    "209": "Flinders transport underpass; major station movement context.",
    "79": "Flinders Street south; southern CBD street activity.",
    "59": "RMIT education precinct with near-complete coverage.",
    "49": "Queen Victoria Market / Therry Street market context.",
    "212": "Southbank Promenade river and leisure context.",
    "66": "QV / Swanston retail and central pedestrian corridor.",
    "58": "Bourke / Spencer west-CBD street context.",
    "23": "Spencer / Collins station-adjacent and office context.",
    "132": "King / La Trobe north-west CBD comparison point.",
}

SELECTION_COLUMNS = (
    "sensor_id",
    "sensor_name",
    "available_2025_hours",
    "missing_2025_hours",
    "coverage_rate",
    "latitude",
    "longitude",
    "status",
    "location_label",
    "selection_mode",
    "selection_tier",
    "enabled",
    "inclusion_reason",
    "notes",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Profile 2025 pedestrian sensor coverage and sensor modes."
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)),
        help="Directory for generated Phase 1S diagnostics.",
    )
    return parser.parse_args()


def read_metadata() -> tuple[
    dict[str, dict[str, str]], set[str], dict[str, set[str]]
]:
    rows: list[dict[str, str]]
    with SENSOR_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    metadata = {row["Location_ID"]: row for row in rows}
    name_ids: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        name_ids[row.get("Sensor_Name", "")].add(row["Location_ID"])
    duplicate_names = {
        name for name, ids in name_ids.items() if name and len(ids) > 1
    }
    return metadata, duplicate_names, name_ids


def coverage_tier(available_hours: int) -> str:
    rate = available_hours / EXPECTED_HOURS
    if available_hours >= 8750:
        return "near_complete"
    if rate >= 0.95:
        return "high_coverage"
    if rate >= 0.50:
        return "partial_coverage"
    return "low_coverage"


def profile_coverage() -> list[dict[str, Any]]:
    metadata, duplicate_names, name_ids = read_metadata()
    sensor_hours: dict[str, set[str]] = defaultdict(set)
    sensor_names: dict[str, Counter[str]] = defaultdict(Counter)
    first_dates: dict[str, str] = {}
    last_dates: dict[str, str] = {}

    with PEDESTRIAN_FILE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as handle:
        for row in csv.DictReader(handle):
            sensing_date = row.get("sensing_date", "")
            if not sensing_date.startswith("2025-"):
                continue
            sensor_id = row.get("location_id", "")
            hour = row.get("hourday", "")
            if not sensor_id or not hour:
                continue
            sensor_hours[sensor_id].add(
                f"{sensing_date}T{int(float(hour)):02d}:00"
            )
            sensor_names[sensor_id][row.get("sensor_name", "")] += 1
            first_dates[sensor_id] = min(
                sensing_date, first_dates.get(sensor_id, sensing_date)
            )
            last_dates[sensor_id] = max(
                sensing_date, last_dates.get(sensor_id, sensing_date)
            )

    coverage: list[dict[str, Any]] = []
    for sensor_id, hours in sensor_hours.items():
        meta = metadata.get(sensor_id)
        raw_name = sensor_names[sensor_id].most_common(1)[0][0]
        sensor_name = meta.get("Sensor_Name", "") if meta else raw_name
        available = len(hours)
        duplicate_name = sensor_name in duplicate_names
        notes: list[str] = []
        if meta is None:
            notes.append("metadata_missing")
        if duplicate_name:
            ids = sorted(
                name_ids[sensor_name],
                key=lambda value: int(value) if value.isdigit() else value,
            )
            notes.append(f"sensor_name_shared_by_ids:{'|'.join(ids)}")
        if meta and meta.get("Installation_Date", "").startswith("2025-"):
            notes.append("installed_during_2025")
        if available < EXPECTED_HOURS and not notes:
            notes.append("incomplete_2025_coverage")

        coverage.append(
            {
                "sensor_id": sensor_id,
                "sensor_name": sensor_name,
                "available_2025_hours": available,
                "missing_2025_hours": EXPECTED_HOURS - available,
                "coverage_rate": round(available / EXPECTED_HOURS, 6),
                "first_2025_observation_date": first_dates[sensor_id],
                "last_2025_observation_date": last_dates[sensor_id],
                "metadata_found": meta is not None,
                "status": meta.get("Status", "") if meta else "",
                "latitude": meta.get("Latitude", "") if meta else "",
                "longitude": meta.get("Longitude", "") if meta else "",
                "location_type": meta.get("Location_Type", "") if meta else "",
                "location_label": (
                    meta.get("Sensor_Description", "") if meta else ""
                ),
                "installation_date": (
                    meta.get("Installation_Date", "") if meta else ""
                ),
                "duplicate_sensor_name": duplicate_name,
                "coverage_tier": coverage_tier(available),
                "notes": "; ".join(notes),
            }
        )

    return sorted(
        coverage,
        key=lambda row: (
            -row["available_2025_hours"],
            int(row["sensor_id"])
            if row["sensor_id"].isdigit()
            else row["sensor_id"],
        ),
    )


def selection_row(
    coverage: dict[str, Any],
    mode: str,
    tier: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "sensor_id": coverage["sensor_id"],
        "sensor_name": coverage["sensor_name"],
        "available_2025_hours": coverage["available_2025_hours"],
        "missing_2025_hours": coverage["missing_2025_hours"],
        "coverage_rate": coverage["coverage_rate"],
        "latitude": coverage["latitude"],
        "longitude": coverage["longitude"],
        "status": coverage["status"],
        "location_label": coverage["location_label"],
        "selection_mode": mode,
        "selection_tier": tier,
        "enabled": "true",
        "inclusion_reason": reason,
        "notes": coverage["notes"],
    }


def build_selection_config(
    coverage: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_id = {row["sensor_id"]: row for row in coverage}
    missing_required = sorted(
        (set(MVP_3_IDS) | set(REPRESENTATIVE_12_IDS)) - set(by_id)
    )
    if missing_required:
        raise ValueError(
            f"Required configured sensors lack 2025 observations: {missing_required}"
        )

    rows: list[dict[str, Any]] = []
    for sensor_id in MVP_3_IDS:
        rows.append(
            selection_row(
                by_id[sensor_id],
                "MVP_3",
                "mvp_core",
                "Existing validated MVP sensor retained for backward compatibility.",
            )
        )
    for sensor_id in REPRESENTATIVE_12_IDS:
        rows.append(
            selection_row(
                by_id[sensor_id],
                "REPRESENTATIVE_12",
                "representative",
                REPRESENTATIVE_REASONS[sensor_id],
            )
        )
    for item in coverage:
        if item["coverage_rate"] < 0.95:
            continue
        rows.append(
            selection_row(
                item,
                "HIGH_COVERAGE_ALL",
                item["coverage_tier"],
                "Included automatically because 2025 coverage is at least 95%.",
            )
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def build_diagnostics(
    coverage: list[dict[str, Any]],
    output_dir: Path,
    config_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    tier_counts = Counter(row["coverage_tier"] for row in coverage)
    missing_metadata = [
        row["sensor_id"] for row in coverage if not row["metadata_found"]
    ]
    duplicate_name_sensors = [
        row for row in coverage if row["duplicate_sensor_name"]
    ]
    duplicate_names = sorted(
        {row["sensor_name"] for row in duplicate_name_sensors}
    )
    mode_counts = Counter(row["selection_mode"] for row in config_rows)
    warnings = [
        "Coverage measures unique observed sensor-hour keys; it does not validate count plausibility.",
        "Sensor status is current metadata and is not a historical active-at-timestamp record.",
        "Duplicate sensor names exist; sensor_id is the canonical identity.",
        "HIGH_COVERAGE_ALL is configured but is not run through Phase 1A-1C in Phase 1S.",
    ]
    if missing_metadata:
        warnings.append(
            f"{len(missing_metadata)} observed sensors have no metadata record."
        )
    return {
        "processing_version": PROCESSING_VERSION,
        "study_period": {
            "start": STUDY_START.isoformat(),
            "end": STUDY_END.isoformat(),
            "expected_hours_per_sensor": EXPECTED_HOURS,
        },
        "input_files": [
            PEDESTRIAN_FILE.relative_to(ROOT).as_posix(),
            SENSOR_FILE.relative_to(ROOT).as_posix(),
        ],
        "output_files": [
            (output_dir / "phase1s_sensor_coverage.csv")
            .relative_to(ROOT)
            .as_posix(),
            (output_dir / "phase1s_sensor_coverage.json")
            .relative_to(ROOT)
            .as_posix(),
            SELECTION_CONFIG.relative_to(ROOT).as_posix(),
        ],
        "total_sensors_observed_in_2025": len(coverage),
        "sensors_with_metadata": len(coverage) - len(missing_metadata),
        "sensors_missing_metadata": len(missing_metadata),
        "sensor_ids_missing_metadata": missing_metadata,
        "near_complete_count": tier_counts["near_complete"],
        "high_coverage_count": sum(
            1 for row in coverage if row["coverage_rate"] >= 0.95
        ),
        "high_coverage_tier_only_count": tier_counts["high_coverage"],
        "partial_coverage_count": tier_counts["partial_coverage"],
        "low_coverage_count": tier_counts["low_coverage"],
        "duplicate_sensor_name_count": len(duplicate_names),
        "duplicate_sensor_names": duplicate_names,
        "sensors_with_duplicate_name_count": len(duplicate_name_sensors),
        "duplicate_sensor_name_sensor_ids": [
            row["sensor_id"] for row in duplicate_name_sensors
        ],
        "selection_mode_counts": dict(sorted(mode_counts.items())),
        "top_20_sensors_by_coverage": coverage[:20],
        "warnings": warnings,
    }


def main() -> None:
    args = parse_args()
    output_dir = resolve_output_dir(args.output_dir)
    coverage = profile_coverage()
    config_rows = build_selection_config(coverage)
    coverage_csv = output_dir / "phase1s_sensor_coverage.csv"
    coverage_json = output_dir / "phase1s_sensor_coverage.json"
    diagnostics_path = output_dir / "phase1s_diagnostics.json"

    write_csv(coverage_csv, coverage)
    write_json(coverage_json, coverage)
    write_csv(SELECTION_CONFIG, config_rows)
    diagnostics = build_diagnostics(coverage, output_dir, config_rows)
    write_json(diagnostics_path, diagnostics)
    print(json.dumps(diagnostics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
