"""Shared configuration helpers for Melbourne Urban Pulse analytical stages."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SENSOR_CONFIG = ROOT / "data" / "metadata" / "analysis_sensor_selection.csv"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "processed"
DEFAULT_SENSOR_MODE = "MVP_3"
MODE_DEFAULT_OUTPUT_DIRS = {
    "MVP_3": DEFAULT_OUTPUT_DIR,
    "REPRESENTATIVE_12": DEFAULT_OUTPUT_DIR / "representative_12",
    "HIGH_COVERAGE_ALL": DEFAULT_OUTPUT_DIR / "high_coverage_all",
}


def parse_enabled(value: str | None) -> bool:
    return bool(value) and value.strip().lower() in {"1", "true", "yes", "y"}


def load_sensor_selection(
    sensor_mode: str = DEFAULT_SENSOR_MODE,
    config_path: Path = DEFAULT_SENSOR_CONFIG,
) -> list[dict[str, Any]]:
    """Load and validate one named sensor set from the shared CSV config."""
    if not config_path.exists():
        raise FileNotFoundError(
            f"Sensor selection config not found: {config_path}. "
            "Run scripts/select_analysis_sensors.py first."
        )

    selected: list[dict[str, Any]] = []
    with config_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("selection_mode") != sensor_mode or not parse_enabled(
                row.get("enabled")
            ):
                continue
            selected.append(
                {
                    **row,
                    "sensor_id": row.get("sensor_id", "").strip(),
                    "available_2025_hours": int(row.get("available_2025_hours") or 0),
                    "missing_2025_hours": int(row.get("missing_2025_hours") or 0),
                    "coverage_rate": float(row.get("coverage_rate") or 0),
                    "latitude": float(row["latitude"]) if row.get("latitude") else None,
                    "longitude": float(row["longitude"]) if row.get("longitude") else None,
                }
            )

    if not selected:
        available_modes = list_sensor_modes(config_path)
        raise ValueError(
            f"No enabled sensors found for mode {sensor_mode!r}. "
            f"Available modes: {', '.join(available_modes) or 'none'}"
        )

    ids = [row["sensor_id"] for row in selected]
    if any(not sensor_id for sensor_id in ids):
        raise ValueError(f"Mode {sensor_mode!r} contains a blank sensor ID.")
    duplicates = sorted(
        {sensor_id for sensor_id in ids if ids.count(sensor_id) > 1},
        key=_sensor_sort_key,
    )
    if duplicates:
        raise ValueError(
            f"Mode {sensor_mode!r} contains duplicate sensor IDs: {duplicates}"
        )

    # Preserve the human-authored row order within each mode. Sensor ID remains
    # the canonical identity, while row order can carry a deliberate display or
    # inspection sequence (for example the original 4, 3, 133 MVP order).
    return selected


def list_sensor_modes(config_path: Path = DEFAULT_SENSOR_CONFIG) -> list[str]:
    if not config_path.exists():
        return []
    with config_path.open("r", encoding="utf-8-sig", newline="") as handle:
        return sorted(
            {
                row.get("selection_mode", "")
                for row in csv.DictReader(handle)
                if row.get("selection_mode")
            }
        )


def resolve_output_dir(
    value: str | None,
    sensor_mode: str = DEFAULT_SENSOR_MODE,
) -> Path:
    if not value:
        try:
            return MODE_DEFAULT_OUTPUT_DIRS[sensor_mode]
        except KeyError as error:
            raise ValueError(
                f"No default output directory configured for sensor mode "
                f"{sensor_mode!r}; provide --output-dir explicitly."
            ) from error
    candidate = Path(value)
    return candidate if candidate.is_absolute() else ROOT / candidate


def _sensor_sort_key(sensor_id: str) -> tuple[int, int | str]:
    return (0, int(sensor_id)) if sensor_id.isdigit() else (1, sensor_id)
