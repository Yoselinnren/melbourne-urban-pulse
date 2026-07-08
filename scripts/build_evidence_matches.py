"""Validate manual evidence and build Phase 1H-D candidate/evidence matches.

This stage normalizes the human-authored evidence table and generates
candidate/evidence overlap records for manual review. It does not create
explanation-ready outputs, rankings, scores, or causal interpretations.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from analysis_config import ROOT, resolve_output_dir


PROCESSING_VERSION = "phase1h-d-0.1.0"
SUPPORTED_MODES = {"MVP_3", "REPRESENTATIVE_12"}

EVIDENCE_MANUAL = ROOT / "data" / "manual" / "evidence_manual.csv"
EVIDENCE_REVIEWS = ROOT / "data" / "manual" / "evidence_match_reviews.csv"

REQUIRED_EVIDENCE_FIELDS = {
    "evidence_id",
    "evidence_type",
    "source_name",
    "source_url",
    "start_timestamp",
    "end_timestamp",
    "spatial_scope",
    "expected_pedestrian_impact",
    "expected_direction",
    "evidence_confidence",
    "notes",
    "created_at",
}

NORMALIZED_EVIDENCE_FIELDS = [
    "evidence_type_normalized",
    "spatial_scope_normalized",
    "expected_pedestrian_impact_normalized",
    "expected_direction_normalized",
    "evidence_confidence_normalized",
    "start_timestamp_normalized",
    "end_timestamp_normalized",
    "created_at_normalized",
    "source_category",
    "evidence_validation_status",
    "evidence_validation_warnings",
]

MATCH_FIELDS = [
    "match_id",
    "candidate_type",
    "candidate_id",
    "sensor_mode",
    "evidence_id",
    "evidence_type_normalized",
    "temporal_overlap",
    "temporal_overlap_hours",
    "temporal_overlap_ratio_candidate",
    "temporal_overlap_ratio_evidence",
    "spatial_relevance",
    "relevant_sensor_count",
    "relevant_sensor_proportion",
    "direction_consistency",
    "candidate_direction",
    "expected_direction_normalized",
    "match_basis",
    "auto_match_confidence",
    "auto_match_warnings",
    "review_status",
    "explanation_strength",
    "reviewer_notes",
]

TYPE_MAP = {
    "MAJOR_EVENT": "major_event",
    "PUBLIC_HOLIDAY": "public_holiday",
    "SCHOOL_HOLIDAY": "school_holiday",
    "WEATHER": "weather",
    "PUBLIC_TRANSPORT": "public_transport",
    "ROAD_CLOSURE": "road_closure",
    "BUSINESS_CLOSURE": "business_closure",
    "CROWD_OBSERVATION": "crowd_observation",
    "DST_TRANSITION": "dst_transition",
    "SPORTS_EVENT": "sports_event",
    "FESTIVAL_EVENT": "festival_event",
    "NIGHTLIFE_EVENT": "nightlife_event",
    "NIGHT_MARKET": "night_market",
    "MELBOURNE_EVENT": "melbourne_event",
    "UNKNOWN_CONTEXT": "unknown_context",
}

SPATIAL_MAP = {
    "NETWORK_WIDE": "network_wide",
    "STATE_WIDE": "state_wide",
    "CITY_WIDE": "city_wide",
    "PRECINCT": "precinct",
    "SITE_SPECIFIC": "site_specific",
    "SENSOR_SPECIFIC": "sensor_specific",
}

IMPACT_MAP = {
    "INCREASE": "increase",
    "DECREASE": "decrease",
    "MIXED": "mixed",
}

DIRECTION_MAP = {
    "ABOVE_BASELINE": "above",
    "BELOW_BASELINE": "below",
    "UNCLEAR": "unknown",
}

CONFIDENCE_MAP = {
    "HIGH": "high",
    "MEDIUM": "moderate",
    "LOW": "low",
}

CAUSAL_PHRASES = (
    "caused",
    "due to",
    "because of",
    "explained by",
    "attributed to",
)
TOP_N_PHRASES = ("top anomaly", "top anomalies", "top-n", "top n")

OFFICIAL_GOV = {
    "VIC_GOV",
    "PREMIER_OF_VICTORIA",
    "BUSINESS_VICTORIA",
    "FAIR_WORK",
    "BOM",
    "TRANSPORT_VIC",
    "YARRA_TRAMS",
    "RMIT",
}
MEDIA_SOURCES = {"ABC_NEWS", "THE_GUARDIAN"}
SOCIAL_OR_EVENT_SOURCES = {"EVENTBRITE", "QVM_INSTAGRAM", "TO_THOT_OR_NOT"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Phase 1H-D normalized evidence and review matches."
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


def write_csv_json(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    with path.with_suffix(".json").open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


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


def simple_normalize(value: str | None) -> str:
    cleaned = (value or "").strip()
    return re.sub(r"[^a-z0-9]+", "_", cleaned.lower()).strip("_")


def timestamp_text(value: str | None) -> str:
    text = (value or "").strip()
    return re.sub(r"([+-]\d{2})\.(\d{2})$", r"\1:\2", text)


def parse_timestamp(value: str | None) -> datetime | None:
    text = timestamp_text(value)
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    return datetime.fromisoformat(text)


def iso_or_blank(value: str | None) -> str:
    parsed = parse_timestamp(value)
    return parsed.isoformat() if parsed else ""


def truth(value: str | None) -> bool:
    return (value or "").strip().lower() in {"true", "1", "yes"}


def number(value: str | None) -> float:
    if value in (None, ""):
        return 0.0
    parsed = float(value)
    return parsed if math.isfinite(parsed) else 0.0


def fmt_number(value: float, digits: int = 3) -> str:
    rounded = round(value, digits)
    text = f"{rounded:.{digits}f}".rstrip("0").rstrip(".")
    return text or "0"


def split_pipe(value: str | None) -> list[str]:
    return [item.strip() for item in (value or "").split("|") if item.strip()]


def source_category(source_name: str) -> str:
    source = source_name.strip().upper()
    if source in OFFICIAL_GOV:
        if source == "BOM":
            return "official_weather"
        if source in {"TRANSPORT_VIC", "YARRA_TRAMS"}:
            return "official_transport"
        return "official_government"
    if source in MEDIA_SOURCES:
        return "media"
    if source in SOCIAL_OR_EVENT_SOURCES:
        return "social_or_event_platform"
    if source == "PROJECT_WEATHER_FEATURES":
        return "project_derived"
    if any(term in source for term in ("QVM", "VRC", "MARATHON", "FED_SQUARE")):
        return "official_event_or_venue"
    if source in {"TOURISM_AUSTRALIA", "ANZ", "AUSTRALIAN_RETAILERS_ASSOCIATION"}:
        return "commercial_or_industry"
    return "other"


def normalize_evidence(
    rows: list[dict[str, str]], fields: list[str]
) -> tuple[list[dict[str, str]], list[str], list[str]]:
    missing_fields = sorted(REQUIRED_EVIDENCE_FIELDS.difference(fields))
    if missing_fields:
        raise ValueError(f"{EVIDENCE_MANUAL} is missing fields: {missing_fields}")

    id_counts = Counter((row.get("evidence_id") or "").strip() for row in rows)
    duplicate_ids = {key for key, count in id_counts.items() if key and count > 1}
    normalized_rows: list[dict[str, str]] = []
    critical_errors: list[str] = []

    for index, row in enumerate(rows, start=2):
        out = dict(row)
        warnings: list[str] = []
        row_id = (row.get("evidence_id") or "").strip()

        for field in (
            "evidence_id",
            "start_timestamp",
            "end_timestamp",
            "evidence_type",
            "expected_direction",
            "evidence_confidence",
        ):
            if not (row.get(field) or "").strip():
                critical_errors.append(f"row {index}: missing {field}")
        if row_id in duplicate_ids:
            critical_errors.append(f"row {index}: duplicate evidence_id {row_id}")

        evidence_type = TYPE_MAP.get(
            (row.get("evidence_type") or "").strip().upper(),
            simple_normalize(row.get("evidence_type")),
        )
        spatial_scope = SPATIAL_MAP.get(
            (row.get("spatial_scope") or "").strip().upper(),
            simple_normalize(row.get("spatial_scope")),
        )
        impact = IMPACT_MAP.get(
            (row.get("expected_pedestrian_impact") or "").strip().upper(),
            simple_normalize(row.get("expected_pedestrian_impact")),
        )
        direction = DIRECTION_MAP.get(
            (row.get("expected_direction") or "").strip().upper(),
            simple_normalize(row.get("expected_direction")),
        )
        confidence = CONFIDENCE_MAP.get(
            (row.get("evidence_confidence") or "").strip().upper(),
            simple_normalize(row.get("evidence_confidence")),
        )

        start_normalized = ""
        end_normalized = ""
        try:
            start_normalized = iso_or_blank(row.get("start_timestamp"))
        except ValueError:
            critical_errors.append(f"row {index}: unparseable start_timestamp")
        try:
            end_normalized = iso_or_blank(row.get("end_timestamp"))
        except ValueError:
            critical_errors.append(f"row {index}: unparseable end_timestamp")
        try:
            created_normalized = iso_or_blank(row.get("created_at"))
        except ValueError:
            created_normalized = timestamp_text(row.get("created_at"))
            warnings.append("created_at_unparseable")

        category = source_category(row.get("source_name") or "")
        if not (row.get("source_url") or "").strip():
            warnings.append("blank_source_url")
        if confidence == "low":
            warnings.append("low_confidence_source")
        if category == "social_or_event_platform":
            warnings.append("non_official_social_or_event_source")
        notes = (row.get("notes") or "").lower()
        if any(term in notes for term in ("conceptual", "not direct", "indirect")):
            warnings.append("broad_interpretive_note")

        out.update(
            {
                "evidence_type_normalized": evidence_type,
                "spatial_scope_normalized": spatial_scope,
                "expected_pedestrian_impact_normalized": impact,
                "expected_direction_normalized": direction,
                "evidence_confidence_normalized": confidence,
                "start_timestamp_normalized": start_normalized,
                "end_timestamp_normalized": end_normalized,
                "created_at_normalized": created_normalized,
                "source_category": category,
                "evidence_validation_status": "warning" if warnings else "valid",
                "evidence_validation_warnings": "|".join(warnings),
            }
        )
        normalized_rows.append(out)

    return normalized_rows, critical_errors, missing_fields


def candidate_total_sensors(row: dict[str, str]) -> int:
    ids = split_pipe(row.get("sensor_ids_or_blank"))
    if ids:
        return len(ids)
    return 1 if row.get("candidate_type") == "episode" else 0


def candidate_text(row: dict[str, str]) -> str:
    return " ".join(
        [
            row.get("candidate_scope_or_context", ""),
            row.get("sensor_ids_or_blank", ""),
            row.get("sensor_labels_or_blank", ""),
        ]
    ).lower()


def evidence_tokens(row: dict[str, str]) -> set[str]:
    text = " ".join(
        [
            row.get("location_name", ""),
            row.get("precinct", ""),
            row.get("evidence_name", ""),
        ]
    ).lower()
    aliases = {
        "mel_cbd": "cbd",
        "mel cbd": "cbd",
        "state_wide": "victoria",
        "state wide": "victoria",
        "city_wide": "melbourne",
        "city wide": "melbourne",
    }
    for old, new in aliases.items():
        text = text.replace(old, new)
    return {
        token
        for token in re.split(r"[^a-z0-9]+", text)
        if len(token) >= 3 and token not in {"mel", "the", "and", "event"}
    }


def label_match_count(tokens: set[str], candidate: dict[str, str]) -> int:
    labels = split_pipe(candidate.get("sensor_labels_or_blank"))
    if not labels:
        labels = [candidate.get("sensor_labels_or_blank", "")]
    count = 0
    for label in labels:
        label_text = label.lower()
        if any(token in label_text for token in tokens):
            count += 1
    return count


def sensor_id_match(row: dict[str, str], candidate: dict[str, str]) -> int:
    text = " ".join(
        [
            row.get("location_name", ""),
            row.get("precinct", ""),
            row.get("notes", ""),
        ]
    )
    ids = set(re.findall(r"\b\d+\b", text))
    candidate_ids = set(split_pipe(candidate.get("sensor_ids_or_blank")))
    return len(ids.intersection(candidate_ids))


def spatial_match(
    evidence: dict[str, str], candidate: dict[str, str]
) -> tuple[str, int, float, list[str]]:
    scope = evidence["spatial_scope_normalized"]
    total = candidate_total_sensors(candidate)
    cand_scope = candidate.get("candidate_scope_or_context", "")
    warnings: list[str] = []

    if scope == "network_wide":
        relevance = "network_context" if "pulse" in cand_scope else "broad_context"
        return relevance, total, 1.0 if total else 0.0, warnings
    if scope in {"city_wide", "state_wide"}:
        return "broad_context", total, 1.0 if total else 0.0, warnings
    if scope == "unknown":
        warnings.append("spatial_scope_unknown")
        return "pending_manual_review", 0, 0.0, warnings

    tokens = evidence_tokens(evidence)
    matches = label_match_count(tokens, candidate)
    if "cbd" in tokens and (
        "network_wide" in cand_scope
        or "broad" in cand_scope
        or "cbd" in candidate_text(candidate)
    ):
        matches = max(matches, total)

    if scope == "precinct":
        if matches:
            return "precinct_context", matches, matches / total if total else 0.0, warnings
        return "no_spatial_match", 0, 0.0, warnings

    direct_matches = max(matches, sensor_id_match(evidence, candidate))
    if scope == "sensor_specific" and direct_matches:
        return (
            "sensor_specific_match",
            direct_matches,
            direct_matches / total if total else 0.0,
            warnings,
        )
    if scope == "site_specific" and direct_matches:
        return (
            "direct_site_match",
            direct_matches,
            direct_matches / total if total else 0.0,
            warnings,
        )
    return "no_spatial_match", 0, 0.0, warnings


def direction_consistency(candidate_direction: str, evidence: dict[str, str]) -> str:
    expected = evidence["expected_direction_normalized"]
    impact = evidence["expected_pedestrian_impact_normalized"]
    candidate = candidate_direction.replace("_baseline", "")
    if expected == "unknown" or impact == "mixed":
        return "indeterminate"
    if candidate == expected:
        return "consistent"
    if candidate in {"above", "below"} and expected in {"above", "below"}:
        return "inconsistent"
    return "indeterminate"


def overlap_hours(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> float:
    latest_start = max(a_start, b_start)
    earliest_end = min(a_end, b_end)
    seconds = (earliest_end - latest_start).total_seconds()
    return max(0.0, seconds / 3600)


def interval_hours(start: datetime, end: datetime) -> float:
    return max(0.0, (end - start).total_seconds() / 3600)


def auto_confidence(
    spatial_relevance: str,
    direction: str,
    evidence_confidence: str,
    candidate_ratio: float,
    warnings: list[str],
) -> str:
    if spatial_relevance == "pending_manual_review":
        return "pending_manual_review"
    if direction == "inconsistent" or evidence_confidence == "low":
        return "low"
    if candidate_ratio >= 0.5 and spatial_relevance in {
        "network_context",
        "direct_site_match",
        "sensor_specific_match",
        "precinct_context",
    }:
        return "high" if evidence_confidence == "high" else "moderate"
    if "partial_temporal_overlap" in warnings:
        return "moderate"
    return "moderate"


def build_matches(
    evidence_rows: list[dict[str, str]],
    queue_rows: list[dict[str, str]],
    sensor_mode: str,
) -> list[dict[str, str]]:
    matches: list[dict[str, str]] = []
    for candidate in queue_rows:
        candidate_start = parse_timestamp(candidate.get("start_timestamp"))
        candidate_end = parse_timestamp(candidate.get("end_timestamp"))
        if not candidate_start or not candidate_end:
            raise ValueError(f"Unparseable candidate interval: {candidate}")
        candidate_duration = interval_hours(candidate_start, candidate_end)

        for evidence in evidence_rows:
            evidence_start = parse_timestamp(evidence["start_timestamp_normalized"])
            evidence_end = parse_timestamp(evidence["end_timestamp_normalized"])
            if not evidence_start or not evidence_end:
                continue
            hours = overlap_hours(
                candidate_start, candidate_end, evidence_start, evidence_end
            )
            if hours <= 0:
                continue

            spatial_relevance, sensor_count, sensor_prop, warnings = spatial_match(
                evidence, candidate
            )
            if spatial_relevance == "no_spatial_match":
                continue

            evidence_duration = interval_hours(evidence_start, evidence_end)
            candidate_ratio = hours / candidate_duration if candidate_duration else 0.0
            evidence_ratio = hours / evidence_duration if evidence_duration else 0.0
            if candidate_ratio < 0.5 or evidence_ratio < 0.5:
                warnings.append("partial_temporal_overlap")

            direction = direction_consistency(candidate["candidate_direction"], evidence)
            if direction == "inconsistent":
                warnings.append("direction_inconsistent")
            if evidence["evidence_confidence_normalized"] == "low":
                warnings.append("low_confidence_evidence")

            basis = [
                "temporal_overlap",
                spatial_relevance,
                f"direction_{direction}",
            ]
            confidence = auto_confidence(
                spatial_relevance,
                direction,
                evidence["evidence_confidence_normalized"],
                candidate_ratio,
                warnings,
            )
            matches.append(
                {
                    "match_id": f"M1H_{sensor_mode}_{len(matches) + 1:04d}",
                    "candidate_type": candidate["candidate_type"],
                    "candidate_id": candidate["candidate_id"],
                    "sensor_mode": sensor_mode,
                    "evidence_id": evidence["evidence_id"],
                    "evidence_type_normalized": evidence["evidence_type_normalized"],
                    "temporal_overlap": "true",
                    "temporal_overlap_hours": fmt_number(hours),
                    "temporal_overlap_ratio_candidate": fmt_number(candidate_ratio),
                    "temporal_overlap_ratio_evidence": fmt_number(evidence_ratio),
                    "spatial_relevance": spatial_relevance,
                    "relevant_sensor_count": str(sensor_count),
                    "relevant_sensor_proportion": fmt_number(sensor_prop),
                    "direction_consistency": direction,
                    "candidate_direction": candidate["candidate_direction"],
                    "expected_direction_normalized": evidence[
                        "expected_direction_normalized"
                    ],
                    "match_basis": "|".join(basis),
                    "auto_match_confidence": confidence,
                    "auto_match_warnings": "|".join(dict.fromkeys(warnings)),
                    "review_status": "pending_review",
                    "explanation_strength": "",
                    "reviewer_notes": "",
                }
            )
    return matches


def count_values(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(row.get(field, "") for row in rows).items()))


def main() -> None:
    config = parse_args()
    if config.sensor_mode not in SUPPORTED_MODES:
        raise ValueError("HIGH_COVERAGE_ALL is not supported by Phase 1H-D.")

    output_dir = resolve_output_dir(config.output_dir, config.sensor_mode)
    queue_path = output_dir / "phase1h_review_queue.csv"
    pulse_path = output_dir / "context_enriched_pulse_groups.csv"
    episode_path = output_dir / "context_enriched_candidate_episodes.csv"

    protected_paths = (EVIDENCE_MANUAL, queue_path, pulse_path, episode_path)
    protected_digests = {path: file_digest(path) for path in protected_paths}
    frontend_digest = tree_digest(ROOT / "src")
    raw_digest = tree_digest(ROOT / "data" / "raw")

    evidence_rows, evidence_fields = read_csv(EVIDENCE_MANUAL)
    queue_rows, queue_fields = read_csv(queue_path)
    if not queue_rows:
        raise ValueError(f"Candidate queue is empty: {queue_path}")
    if "candidate_id" not in queue_fields:
        raise ValueError(f"Candidate queue missing candidate_id: {queue_path}")
    # Load Phase 1G files to verify availability and protect them from mutation.
    read_csv(pulse_path)
    read_csv(episode_path)

    normalized, critical_errors, _ = normalize_evidence(evidence_rows, evidence_fields)
    duplicate_count = sum(
        count > 1
        for value, count in Counter(row["evidence_id"] for row in normalized).items()
        if value
    )
    if critical_errors:
        raise ValueError(
            "Critical evidence validation errors: " + "; ".join(critical_errors)
        )

    matches = build_matches(normalized, queue_rows, config.sensor_mode)

    normalized_path = output_dir / "normalized_evidence_manual.csv"
    match_path = output_dir / "candidate_evidence_matches.csv"
    diagnostics_path = output_dir / "phase1h_evidence_match_diagnostics.json"
    normalized_fields = evidence_fields + [
        field for field in NORMALIZED_EVIDENCE_FIELDS if field not in evidence_fields
    ]
    write_csv_json(normalized_path, normalized, normalized_fields)
    write_csv_json(match_path, matches, MATCH_FIELDS)

    matched_evidence = {row["evidence_id"] for row in matches}
    matched_candidates = {
        (row["candidate_type"], row["candidate_id"]) for row in matches
    }
    candidate_keys = {
        (row["candidate_type"], row["candidate_id"]) for row in queue_rows
    }
    warning_count = sum(
        len(split_pipe(row["evidence_validation_warnings"])) for row in normalized
    )
    blank_source_url_count = sum(not row.get("source_url", "").strip() for row in normalized)
    generated_text = "\n".join(
        str(value).lower()
        for row in matches
        for key, value in row.items()
        if key
        in {
            "match_basis",
            "auto_match_warnings",
            "review_status",
            "explanation_strength",
            "reviewer_notes",
        }
    )
    output_names = {
        normalized_path.name,
        normalized_path.with_suffix(".json").name,
        match_path.name,
        match_path.with_suffix(".json").name,
        diagnostics_path.name,
    }
    sanity_checks = {
        "all_evidence_rows_preserved": len(evidence_rows) == len(normalized),
        "normalized_evidence_ids_unique": len({row["evidence_id"] for row in normalized})
        == len(normalized),
        "no_critical_validation_errors": not critical_errors,
        "candidate_queue_loaded": bool(queue_rows),
        "generated_matches_have_temporal_overlap": all(
            row["temporal_overlap"] == "true" and number(row["temporal_overlap_hours"]) > 0
            for row in matches
        ),
        "review_status_pending_only": {row["review_status"] for row in matches}
        <= {"pending_review"},
        "no_causal_language_generated": not any(
            phrase in generated_text for phrase in CAUSAL_PHRASES
        ),
        "no_ranking_created": not {"review_priority_score", "priority_band"}.intersection(
            MATCH_FIELDS
        ),
        "no_review_priority_score_created": "review_priority_score" not in MATCH_FIELDS,
        "no_top_n_output_created": not any(
            phrase in generated_text or phrase in " ".join(output_names)
            for phrase in TOP_N_PHRASES
        ),
        "no_explanation_ready_outputs_created": not any(
            "explanation_ready" in name for name in output_names
        ),
        "no_manual_evidence_overwritten": protected_digests[EVIDENCE_MANUAL]
        == file_digest(EVIDENCE_MANUAL),
        "phase1g_outputs_not_modified": protected_digests[pulse_path]
        == file_digest(pulse_path)
        and protected_digests[episode_path] == file_digest(episode_path),
        "frontend_not_modified": frontend_digest == tree_digest(ROOT / "src"),
        "raw_data_not_modified": raw_digest == tree_digest(ROOT / "data" / "raw"),
        "high_coverage_all_not_run": config.sensor_mode != "HIGH_COVERAGE_ALL",
    }
    if not all(sanity_checks.values()):
        failures = [name for name, passed in sanity_checks.items() if not passed]
        raise ValueError(f"Phase 1H-D sanity checks failed: {failures}")

    diagnostics = {
        "processing_version": PROCESSING_VERSION,
        "sensor_mode": config.sensor_mode,
        "input_files": [
            str(EVIDENCE_MANUAL.relative_to(ROOT)),
            str(queue_path.relative_to(ROOT)),
            str(pulse_path.relative_to(ROOT)),
            str(episode_path.relative_to(ROOT)),
        ],
        "output_files": [
            str(normalized_path.relative_to(ROOT)),
            str(normalized_path.with_suffix(".json").relative_to(ROOT)),
            str(match_path.relative_to(ROOT)),
            str(match_path.with_suffix(".json").relative_to(ROOT)),
            str(diagnostics_path.relative_to(ROOT)),
        ],
        "evidence_input_row_count": len(evidence_rows),
        "normalized_evidence_row_count": len(normalized),
        "duplicate_evidence_id_count": duplicate_count,
        "critical_error_count": len(critical_errors),
        "warning_count": warning_count,
        "evidence_type_counts": count_values(evidence_rows, "evidence_type"),
        "normalized_evidence_type_counts": count_values(
            normalized, "evidence_type_normalized"
        ),
        "spatial_scope_counts": count_values(evidence_rows, "spatial_scope"),
        "normalized_spatial_scope_counts": count_values(
            normalized, "spatial_scope_normalized"
        ),
        "expected_direction_counts": count_values(evidence_rows, "expected_direction"),
        "normalized_expected_direction_counts": count_values(
            normalized, "expected_direction_normalized"
        ),
        "evidence_confidence_counts": count_values(evidence_rows, "evidence_confidence"),
        "normalized_evidence_confidence_counts": count_values(
            normalized, "evidence_confidence_normalized"
        ),
        "source_category_counts": count_values(normalized, "source_category"),
        "blank_source_url_count": blank_source_url_count,
        "candidate_queue_row_count": len(queue_rows),
        "generated_match_count": len(matches),
        "match_candidate_type_counts": count_values(matches, "candidate_type"),
        "match_evidence_type_counts": count_values(matches, "evidence_type_normalized"),
        "auto_match_confidence_counts": count_values(matches, "auto_match_confidence"),
        "direction_consistency_counts": count_values(matches, "direction_consistency"),
        "spatial_relevance_counts": count_values(matches, "spatial_relevance"),
        "unmatched_evidence_count": len(
            {row["evidence_id"] for row in normalized}.difference(matched_evidence)
        ),
        "unmatched_candidate_count": len(candidate_keys.difference(matched_candidates)),
        "boundary_statements": [
            "Matches record temporal and spatial overlap candidates for manual review.",
            "Automatic confidence is categorical and transparent, not a ranking.",
            "Manual review fields remain pending.",
            "No explanation-ready output or causal interpretation is produced.",
        ],
        "sanity_checks": sanity_checks,
    }
    with diagnostics_path.open("w", encoding="utf-8") as handle:
        json.dump(diagnostics, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(
        f"Wrote {len(normalized)} normalized evidence rows and {len(matches)} "
        f"matches for {config.sensor_mode} to {output_dir.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
