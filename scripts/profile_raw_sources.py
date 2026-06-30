"""
Profile raw data sources for Melbourne Urban Pulse.

This script is intentionally read-only for data/raw. It discovers raw files,
profiles CSV/JSON sources where practical, and writes:

- data/metadata/raw_data_profile.json
- docs/data-profile.md
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RAW_DIRS = [
    ROOT / "data" / "raw" / "pedestrian",
    ROOT / "data" / "raw" / "sensors",
    ROOT / "data" / "raw" / "weather",
    ROOT / "data" / "raw" / "calendar",
    ROOT / "data" / "raw" / "events",
]
PROFILE_JSON = ROOT / "data" / "metadata" / "raw_data_profile.json"
PROFILE_MD = ROOT / "docs" / "data-profile.md"

MISSING_VALUES = {"", "na", "n/a", "null", "none", "nan"}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def compact_counter(counter: Counter, limit: int = 12) -> list[dict[str, Any]]:
    return [{"value": str(k), "count": int(v)} for k, v in counter.most_common(limit)]


def safe_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(str(value).strip())
    except ValueError:
        return None


def parse_date(value: str | None) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    text = text.replace("Z", "")
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%m/%d/%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(text[:19], fmt)
        except ValueError:
            continue
    return None


def date_range_update(current: dict[str, str | None], value: str | None) -> None:
    parsed = parse_date(value)
    if parsed is None:
        return
    iso = parsed.isoformat(timespec="minutes")
    if current["min"] is None or iso < current["min"]:
        current["min"] = iso
    if current["max"] is None or iso > current["max"]:
        current["max"] = iso


def discover_files() -> list[Path]:
    files: list[Path] = []
    for directory in RAW_DIRS:
        if directory.exists():
            files.extend(path for path in directory.rglob("*") if path.is_file())
    return sorted(files)


def choose_csv_header(path: Path) -> int:
    rows: list[list[str]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        for i, row in enumerate(reader):
            rows.append(row)
            if i >= 20:
                break

    if not rows:
        return 0

    for i, row in enumerate(rows):
        lowered = [cell.strip().lower() for cell in row]
        if "time" in lowered and any(
            token in " ".join(lowered)
            for token in ["temperature", "weather", "humidity", "precipitation"]
        ):
            return i

    return 0


def infer_columns(columns: list[str]) -> dict[str, list[str]]:
    lowered = {col: col.lower() for col in columns}
    return {
        "date_time_columns": [
            col
            for col, low in lowered.items()
            if any(token in low for token in ["date", "time", "timestamp"])
        ],
        "id_columns": [
            col
            for col, low in lowered.items()
            if low.endswith("id") or low.endswith("_id") or "id" == low or "sensor" in low
        ],
        "count_columns": [
            col
            for col, low in lowered.items()
            if any(token in low for token in ["count", "volume", "pedestrian"])
        ],
        "location_columns": [
            col
            for col, low in lowered.items()
            if any(token in low for token in ["lat", "lon", "location", "geo", "address", "small_area"])
        ],
        "category_columns": [
            col
            for col, low in lowered.items()
            if any(token in low for token in ["type", "category", "classification", "status", "name"])
        ],
    }


def profile_csv(path: Path) -> dict[str, Any]:
    header_index = choose_csv_header(path)
    row_count = 0
    columns: list[str] = []
    missing: Counter = Counter()
    samples: dict[str, list[str]] = defaultdict(list)
    unique_values: dict[str, set[str]] = defaultdict(set)
    date_ranges: dict[str, dict[str, str | None]] = defaultdict(lambda: {"min": None, "max": None})
    numeric_ranges: dict[str, dict[str, float | None]] = defaultdict(lambda: {"min": None, "max": None})
    categorical_counts: dict[str, Counter] = defaultdict(Counter)

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        for _ in range(header_index):
            next(reader, None)
        try:
            columns = [cell.strip() for cell in next(reader)]
        except StopIteration:
            columns = []

        inferred = infer_columns(columns)
        id_columns = inferred["id_columns"][:4]
        date_columns = inferred["date_time_columns"]
        numeric_candidates = inferred["count_columns"] + [
            col
            for col in columns
            if col.lower() in {"latitude", "longitude", "hourday", "temperature", "rain"}
        ]
        category_columns = inferred["category_columns"][:8]

        for raw_row in reader:
            if not raw_row or not any(cell.strip() for cell in raw_row):
                continue
            row_count += 1
            row = {col: raw_row[i].strip() if i < len(raw_row) else "" for i, col in enumerate(columns)}

            for col in columns:
                value = row.get(col, "")
                if value.strip().lower() in MISSING_VALUES:
                    missing[col] += 1
                elif len(samples[col]) < 3:
                    samples[col].append(value)

            for col in id_columns:
                value = row.get(col, "")
                if value and len(unique_values[col]) <= 5000:
                    unique_values[col].add(value)

            for col in date_columns:
                date_range_update(date_ranges[col], row.get(col))

            if "sensing_date" in row and "hourday" in row:
                timestamp = f"{row.get('sensing_date', '')}T{str(row.get('hourday', '')).zfill(2)}:00"
                date_range_update(date_ranges["sensing_date + hourday"], timestamp)

            for col in numeric_candidates:
                num = safe_float(row.get(col))
                if num is None:
                    continue
                if numeric_ranges[col]["min"] is None or num < numeric_ranges[col]["min"]:
                    numeric_ranges[col]["min"] = num
                if numeric_ranges[col]["max"] is None or num > numeric_ranges[col]["max"]:
                    numeric_ranges[col]["max"] = num

            for col in category_columns:
                value = row.get(col, "")
                if value:
                    categorical_counts[col][value] += 1

    missing_percent = {
        col: round((missing[col] / row_count) * 100, 3) if row_count else 0
        for col in columns
        if missing[col]
    }
    unique_counts = {col: len(values) for col, values in unique_values.items()}

    return {
        "path": rel(path),
        "format": "csv",
        "parsed": True,
        "row_count": row_count,
        "columns": columns,
        "column_count": len(columns),
        "sample_values": dict(samples),
        "missing_values": dict(missing),
        "missing_percent": missing_percent,
        "inferred_columns": infer_columns(columns),
        "date_ranges": dict(date_ranges),
        "numeric_ranges": dict(numeric_ranges),
        "unique_counts": unique_counts,
        "top_categories": {
            col: compact_counter(counter)
            for col, counter in categorical_counts.items()
        },
    }


def profile_open_meteo_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    variables = [key for key in hourly.keys() if key != "time"]
    lengths = {key: len(value) for key, value in hourly.items() if isinstance(value, list)}
    return {
        "path": rel(path),
        "format": "json",
        "parsed": True,
        "source_type": "open_meteo_hourly",
        "timezone": data.get("timezone"),
        "timezone_abbreviation": data.get("timezone_abbreviation"),
        "utc_offset_seconds": data.get("utc_offset_seconds"),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "hourly_count": len(times),
        "first_timestamp": times[0] if times else None,
        "last_timestamp": times[-1] if times else None,
        "variables": variables,
        "hourly_units": data.get("hourly_units", {}),
        "series_lengths": lengths,
    }


def profile_planned_works_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    result = data.get("result", {})
    records = result.get("records", [])
    fields = [field.get("id") for field in result.get("fields", []) if field.get("id")]
    classification = Counter()
    status = Counter()
    small_area = Counter()
    date_ranges = {
        "start_date": {"min": None, "max": None},
        "end_date": {"min": None, "max": None},
    }
    missing = Counter()

    for record in records:
        classification[record.get("classification", "")] += 1
        status[record.get("status", "")] += 1
        small_area[record.get("small_area", "")] += 1
        date_range_update(date_ranges["start_date"], record.get("start_date"))
        date_range_update(date_ranges["end_date"], record.get("end_date"))
        for field in fields:
            if str(record.get(field, "")).strip().lower() in MISSING_VALUES:
                missing[field] += 1

    return {
        "path": rel(path),
        "format": "json",
        "parsed": True,
        "source_type": "planned_works_datavic",
        "success": data.get("success"),
        "reported_total": result.get("total"),
        "record_count": len(records),
        "fields": fields,
        "date_ranges": date_ranges,
        "classifications": compact_counter(classification),
        "statuses": compact_counter(status),
        "small_areas": compact_counter(small_area),
        "location_fields": [
            field
            for field in fields
            if any(token in field.lower() for token in ["location", "geo", "area", "geometry"])
        ],
        "missing_values": dict(missing),
    }


def profile_json(path: Path) -> dict[str, Any]:
    if "open_meteo" in path.name:
        return profile_open_meteo_json(path)
    if "planned_works" in path.name or "datavic" in path.name:
        return profile_planned_works_json(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "path": rel(path),
        "format": "json",
        "parsed": True,
        "source_type": "generic_json",
        "top_level_type": type(data).__name__,
        "top_level_keys": list(data.keys()) if isinstance(data, dict) else None,
    }


def profile_file(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    try:
        if suffix == ".csv":
            return profile_csv(path)
        if suffix == ".json":
            return profile_json(path)
        return {
            "path": rel(path),
            "format": suffix.lstrip(".") or "unknown",
            "parsed": False,
            "reason": "Unsupported for lightweight profiling in this script.",
            "size_bytes": path.stat().st_size,
        }
    except Exception as exc:  # noqa: BLE001 - profile should record parse failures.
        return {
            "path": rel(path),
            "format": suffix.lstrip(".") or "unknown",
            "parsed": False,
            "reason": f"{type(exc).__name__}: {exc}",
            "size_bytes": path.stat().st_size if path.exists() else None,
        }


def load_sensor_metadata() -> dict[str, dict[str, str]]:
    sensor_file = ROOT / "data" / "raw" / "sensors" / "pedestrian_sensor_locations.csv"
    if not sensor_file.exists():
        return {}
    sensors: dict[str, dict[str, str]] = {}
    with sensor_file.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            sensor_id = row.get("Location_ID", "")
            if not sensor_id:
                continue
            sensors[sensor_id] = {
                "sensor_id": sensor_id,
                "sensor_name": row.get("Sensor_Name", ""),
                "description": row.get("Sensor_Description", ""),
                "status": row.get("Status", ""),
                "latitude": row.get("Latitude", ""),
                "longitude": row.get("Longitude", ""),
                "location_type": row.get("Location_Type", ""),
            }
    return sensors


def recommend_pedestrian_sensors() -> list[dict[str, Any]]:
    path = ROOT / "data" / "raw" / "pedestrian" / "pedestrian_counts_hourly_full.csv"
    if not path.exists():
        return []

    sensor_meta = load_sensor_metadata()
    stats: dict[str, dict[str, Any]] = defaultdict(lambda: {"rows_2025": 0, "total_count_2025": 0})

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            date = row.get("sensing_date", "")
            if not date.startswith("2025-"):
                continue
            sensor_id = row.get("location_id", "")
            if not sensor_id:
                continue
            stats[sensor_id]["rows_2025"] += 1
            stats[sensor_id]["total_count_2025"] += int(safe_float(row.get("pedestriancount")) or 0)
            stats[sensor_id]["sensor_name_from_counts"] = row.get("sensor_name", "")

    ranked = sorted(
        stats.items(),
        key=lambda item: (item[1]["rows_2025"], item[1]["total_count_2025"]),
        reverse=True,
    )

    candidates: list[dict[str, Any]] = []
    for sensor_id, values in ranked:
        meta = sensor_meta.get(sensor_id, {})
        if meta and meta.get("status") != "A":
            continue
        candidates.append(
            {
                "sensor_id": sensor_id,
                "sensor_name": meta.get("sensor_name") or values.get("sensor_name_from_counts"),
                "description": meta.get("description"),
                "status": meta.get("status"),
                "latitude": meta.get("latitude"),
                "longitude": meta.get("longitude"),
                "rows_2025": values["rows_2025"],
                "total_count_2025": values["total_count_2025"],
            }
        )
        if len(candidates) >= 10:
            break

    return candidates


def build_overview(files: list[Path], profiles: list[dict[str, Any]]) -> dict[str, Any]:
    parsed = [profile for profile in profiles if profile.get("parsed")]
    failed = [profile for profile in profiles if not profile.get("parsed")]
    source_names = []
    for profile in parsed:
        path = profile.get("path", "")
        if "/pedestrian/" in path:
            source_names.append("pedestrian_counts")
        elif "/sensors/" in path:
            source_names.append("pedestrian_sensor_locations")
        elif "/weather/" in path:
            source_names.append("weather")
        elif "/calendar/" in path:
            source_names.append("calendar")
        elif "/events/" in path:
            source_names.append("events")

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "discovered_file_count": len(files),
        "parsed_file_count": len(parsed),
        "unparsed_file_count": len(failed),
        "successfully_profiled_source_groups": sorted(set(source_names)),
        "unparsed_files": failed,
        "recommended_mvp_study_period": {
            "period": "2025-01-01 to 2025-12-31",
            "reason": "Weather data covers 2025 hourly, calendar data includes 2025 context, and pedestrian counts include 2025 observations across active sensors.",
        },
        "candidate_pedestrian_sensors": recommend_pedestrian_sensors(),
    }


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    output = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        output.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(output)


def write_markdown(profile: dict[str, Any]) -> None:
    overview = profile["overview"]
    lines = [
        "# Raw Data Profile",
        "",
        f"Generated at: `{overview['generated_at']}`",
        "",
        "## Overview",
        "",
        markdown_table(
            ["Metric", "Value"],
            [
                ["Discovered files", overview["discovered_file_count"]],
                ["Parsed files", overview["parsed_file_count"]],
                ["Unparsed files", overview["unparsed_file_count"]],
                ["Recommended MVP study period", overview["recommended_mvp_study_period"]["period"]],
            ],
        ),
        "",
        "## Source Files",
        "",
    ]

    source_rows = []
    for item in profile["sources"]:
        source_rows.append(
            [
                item["path"],
                item.get("format"),
                item.get("parsed"),
                item.get("row_count", item.get("record_count", item.get("hourly_count", ""))),
                item.get("column_count", len(item.get("fields", [])) if item.get("fields") else ""),
            ]
        )
    lines.append(markdown_table(["Path", "Format", "Parsed", "Rows/Records", "Columns/Fields"], source_rows))

    lines.extend(["", "## Parsed Source Details", ""])
    for item in profile["sources"]:
        if not item.get("parsed"):
            continue
        lines.extend([f"### `{item['path']}`", ""])
        if item.get("format") == "csv":
            lines.append(f"- Rows: `{item.get('row_count')}`")
            lines.append(f"- Columns: `{', '.join(item.get('columns', []))}`")
            if item.get("date_ranges"):
                lines.append(f"- Date ranges: `{json.dumps(item['date_ranges'], ensure_ascii=False)}`")
            if item.get("unique_counts"):
                lines.append(f"- Unique identifier counts: `{json.dumps(item['unique_counts'], ensure_ascii=False)}`")
            if item.get("missing_percent"):
                lines.append(f"- Missing percent: `{json.dumps(item['missing_percent'], ensure_ascii=False)}`")
            if item.get("top_categories"):
                lines.append(f"- Top categories: `{json.dumps(item['top_categories'], ensure_ascii=False)}`")
        elif item.get("source_type") == "open_meteo_hourly":
            lines.append(f"- Timezone: `{item.get('timezone')}`")
            lines.append(f"- Hourly count: `{item.get('hourly_count')}`")
            lines.append(f"- First timestamp: `{item.get('first_timestamp')}`")
            lines.append(f"- Last timestamp: `{item.get('last_timestamp')}`")
            lines.append(f"- Variables: `{', '.join(item.get('variables', []))}`")
        elif item.get("source_type") == "planned_works_datavic":
            lines.append(f"- Reported total: `{item.get('reported_total')}`")
            lines.append(f"- Records loaded: `{item.get('record_count')}`")
            lines.append(f"- Fields: `{', '.join(item.get('fields', []))}`")
            lines.append(f"- Date ranges: `{json.dumps(item['date_ranges'], ensure_ascii=False)}`")
            lines.append(f"- Classifications: `{json.dumps(item['classifications'], ensure_ascii=False)}`")
            lines.append(f"- Statuses: `{json.dumps(item['statuses'], ensure_ascii=False)}`")
            lines.append(f"- Location fields: `{', '.join(item.get('location_fields', []))}`")
        lines.append("")

    lines.extend(["## Unparsed Files", ""])
    if overview["unparsed_files"]:
        lines.append(markdown_table(["Path", "Format", "Reason"], [[i["path"], i["format"], i["reason"]] for i in overview["unparsed_files"]]))
    else:
        lines.append("No unparsed files.")

    lines.extend(["", "## Candidate Pedestrian Sensors", ""])
    candidates = overview["candidate_pedestrian_sensors"]
    if candidates:
        lines.append(
            markdown_table(
                ["Sensor ID", "Name", "Description", "Rows 2025", "Total Count 2025"],
                [
                    [
                        item["sensor_id"],
                        item.get("sensor_name"),
                        item.get("description"),
                        item.get("rows_2025"),
                        item.get("total_count_2025"),
                    ]
                    for item in candidates
                ],
            )
        )
    else:
        lines.append("No candidate sensors found.")

    lines.extend(
        [
            "",
            "## Obvious Data Quality Notes",
            "",
            "- Raw pedestrian counts include multiple years; MVP filtering should explicitly constrain the study period.",
            "- Manual event annotations are not part of `data/raw` and currently need separate curation before they can explain anomalies.",
            "- The planned works JSON is useful for disruption context, but its date range may not align with a 2025 pedestrian/weather MVP without additional source updates.",
            "- Open-Meteo CSV contains metadata rows before the hourly table; the JSON file is cleaner for automated parsing.",
        ]
    )

    PROFILE_MD.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    files = discover_files()
    profiles = [profile_file(path) for path in files]
    profile = {
        "overview": build_overview(files, profiles),
        "sources": profiles,
    }

    PROFILE_JSON.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_JSON.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(profile)

    print(f"Discovered files: {profile['overview']['discovered_file_count']}")
    print(f"Parsed files: {profile['overview']['parsed_file_count']}")
    print(f"Unparsed files: {profile['overview']['unparsed_file_count']}")
    print(f"Wrote {rel(PROFILE_JSON)}")
    print(f"Wrote {rel(PROFILE_MD)}")


if __name__ == "__main__":
    main()
