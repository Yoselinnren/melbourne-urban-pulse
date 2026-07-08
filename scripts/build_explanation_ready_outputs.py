"""Build Phase 1H-E explanation-ready evidence metadata outputs.

Explanation-ready means structured evidence metadata is attached to every
candidate. It does not mean an explanation has been reviewed or proven.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from analysis_config import ROOT, resolve_output_dir


PROCESSING_VERSION = "phase1h-e-0.1.0"
SUPPORTED_MODES = {"MVP_3", "REPRESENTATIVE_12"}

EVIDENCE_MANUAL = ROOT / "data" / "manual" / "evidence_manual.csv"
EVIDENCE_REVIEWS = ROOT / "data" / "manual" / "evidence_match_reviews.csv"

FORBIDDEN_CAUSAL_PHRASES = (
    "caused",
    "due to",
    "because of",
    "explained by",
    "attributed to",
)

ADDED_FIELDS = [
    "evidence_match_count",
    "reviewed_evidence_match_count",
    "pending_review_match_count",
    "verified_overlap_count",
    "plausible_association_count",
    "insufficient_evidence_count",
    "rejected_match_count",
    "data_quality_issue_count",
    "unexplained_review_count",
    "evidence_ids",
    "evidence_names",
    "evidence_types",
    "evidence_source_names",
    "evidence_source_urls",
    "evidence_confidence_values",
    "evidence_auto_match_confidence_values",
    "evidence_direction_consistency_values",
    "evidence_spatial_relevance_values",
    "evidence_temporal_overlap_hours_total",
    "evidence_temporal_overlap_hours_max",
    "strongest_auto_match_confidence",
    "strongest_evidence_confidence",
    "dominant_evidence_type",
    "dominant_spatial_relevance",
    "dominant_direction_consistency",
    "strongest_reviewed_explanation_strength",
    "manual_review_queue_member",
    "manual_evidence_search_scope",
    "evidence_review_status_summary",
    "explanation_readiness",
    "explanation_ready_for_ui",
    "explanation_requires_human_review",
    "explanation_has_verified_overlap",
    "explanation_has_plausible_association",
    "explanation_has_only_auto_matches",
    "explanation_has_no_evidence",
    "explanation_has_data_quality_issue",
    "explanation_is_unexplained",
    "causal_claim_allowed",
    "generated_explanation_text",
    "language_guardrail_status",
    "evidence_provenance_summary",
]

CONFIDENCE_ORDER = {
    "pending_manual_review": 0,
    "low": 1,
    "moderate": 2,
    "high": 3,
}
EVIDENCE_CONFIDENCE_ORDER = {"low": 1, "moderate": 2, "high": 3}
EXPLANATION_STRENGTH_ORDER = {"none": 1, "weak": 2, "moderate": 3, "strong": 4}
DOMINANT_TIE_ORDER = {
    "consistent": 3,
    "indeterminate": 2,
    "inconsistent": 1,
    "network_context": 5,
    "direct_site_match": 4,
    "sensor_specific_match": 4,
    "precinct_context": 3,
    "broad_context": 2,
    "pending_manual_review": 1,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Phase 1H-E explanation-ready evidence metadata outputs."
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


def optional_digest(path: Path) -> str | None:
    return file_digest(path) if path.exists() else None


def tree_digest(path: Path) -> str:
    digest = hashlib.sha256()
    if not path.exists():
        return digest.hexdigest()
    for file_path in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(str(file_path.relative_to(path)).encode("utf-8"))
        digest.update(file_digest(file_path).encode("ascii"))
    return digest.hexdigest()


def number(value: str | None) -> float:
    if value in (None, ""):
        return 0.0
    parsed = float(value)
    return parsed if parsed == parsed else 0.0


def fmt_number(value: float) -> str:
    return f"{round(value, 3):.3f}".rstrip("0").rstrip(".") or "0"


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def pipe(values: list[str]) -> str:
    return "|".join(value for value in values if value)


def unique_pipe(values: list[str]) -> str:
    seen: set[str] = set()
    kept: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            kept.append(value)
    return "|".join(kept)


def count_values(values: list[str]) -> dict[str, int]:
    return dict(sorted(Counter(value or "blank" for value in values).items()))


def strongest(values: list[str], order: dict[str, int]) -> str:
    filtered = [value for value in values if value]
    if not filtered:
        return ""
    return max(filtered, key=lambda value: order.get(value, 0))


def dominant(values: list[str], tie_order: dict[str, int] | None = None) -> str:
    filtered = [value for value in values if value]
    if not filtered:
        return ""
    counts = Counter(filtered)
    return max(
        counts,
        key=lambda value: (
            counts[value],
            (tie_order or {}).get(value, 0),
            -filtered.index(value),
        ),
    )


def review_lookup(rows: list[dict[str, str]]) -> dict[tuple[str, str, str], dict[str, str]]:
    lookup: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in rows:
        key = (
            row.get("candidate_type", "").strip(),
            row.get("candidate_id", "").strip(),
            row.get("evidence_id", "").strip(),
        )
        if all(key):
            lookup[key] = row
    return lookup


def joined_matches(
    matches: list[dict[str, str]],
    evidence_rows: list[dict[str, str]],
    review_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    evidence_by_id = {row["evidence_id"]: row for row in evidence_rows}
    reviews = review_lookup(review_rows)
    joined: list[dict[str, str]] = []
    for match in matches:
        evidence = evidence_by_id.get(match["evidence_id"])
        if not evidence:
            continue
        review = reviews.get(
            (match["candidate_type"], match["candidate_id"], match["evidence_id"]),
            {},
        )
        final_status = (
            review.get("review_status", "").strip()
            or match.get("review_status", "").strip()
            or "pending_review"
        )
        final_strength = review.get("explanation_strength", "").strip() or match.get(
            "explanation_strength", ""
        ).strip()
        joined.append(
            {
                **match,
                "_final_review_status": final_status,
                "_final_explanation_strength": final_strength,
                "_manual_review_present": bool_text(bool(review)),
                "_evidence_name": evidence.get("evidence_name", ""),
                "_evidence_source_name": evidence.get("source_name", ""),
                "_evidence_source_url": evidence.get("source_url", ""),
                "_evidence_confidence": evidence.get(
                    "evidence_confidence_normalized", ""
                ),
                "_source_category": evidence.get("source_category", ""),
            }
        )
    return joined


def readiness(statuses: list[str], manual_review_queue_member: bool) -> str:
    if not statuses:
        return (
            "review_queue_no_evidence_linked"
            if manual_review_queue_member
            else "not_in_manual_review_scope"
        )
    status_set = set(statuses)
    reviewed = status_set.difference({"pending_review"})
    if status_set == {"pending_review"}:
        return "auto_matched_pending_review"
    if "data_quality_issue" in reviewed:
        return "reviewed_data_quality_issue"
    if "plausible_association" in reviewed:
        return "reviewed_plausible_association"
    if "verified_overlap" in reviewed:
        return "reviewed_verified_overlap"
    if reviewed and reviewed.issubset({"insufficient_evidence", "rejected"}):
        return "reviewed_insufficient_evidence"
    if reviewed == {"unexplained"}:
        return "reviewed_unexplained"
    if "pending_review" in status_set and reviewed:
        return "partially_reviewed"
    return "mixed_review_status"


def aggregate(
    matches: list[dict[str, str]], manual_review_queue_member: bool
) -> dict[str, str]:
    statuses = [row["_final_review_status"] for row in matches]
    strengths = [row["_final_explanation_strength"] for row in matches]
    evidence_confidences = [row["_evidence_confidence"] for row in matches]
    auto_confidences = [row.get("auto_match_confidence", "") for row in matches]
    directions = [row.get("direction_consistency", "") for row in matches]
    spatial = [row.get("spatial_relevance", "") for row in matches]
    types = [row.get("evidence_type_normalized", "") for row in matches]
    hours = [number(row.get("temporal_overlap_hours")) for row in matches]
    status_counts = Counter(statuses)
    ready = readiness(statuses, manual_review_queue_member)
    has_matches = bool(matches)
    has_pending = bool(status_counts.get("pending_review"))
    has_no_evidence = not has_matches and manual_review_queue_member

    source_names = [row["_evidence_source_name"] for row in matches]
    source_categories = [row["_source_category"] for row in matches]
    provenance = ""
    if has_matches:
        provenance = (
            f"source_count={len(set(source_names))};"
            f"source_names={unique_pipe(source_names)};"
            f"source_categories={unique_pipe(source_categories)}"
        )

    return {
        "evidence_match_count": str(len(matches)),
        "reviewed_evidence_match_count": str(len(statuses) - status_counts["pending_review"]),
        "pending_review_match_count": str(status_counts["pending_review"]),
        "verified_overlap_count": str(status_counts["verified_overlap"]),
        "plausible_association_count": str(status_counts["plausible_association"]),
        "insufficient_evidence_count": str(status_counts["insufficient_evidence"]),
        "rejected_match_count": str(status_counts["rejected"]),
        "data_quality_issue_count": str(status_counts["data_quality_issue"]),
        "unexplained_review_count": str(status_counts["unexplained"]),
        "evidence_ids": pipe([row.get("evidence_id", "") for row in matches]),
        "evidence_names": pipe([row["_evidence_name"] for row in matches]),
        "evidence_types": pipe(types),
        "evidence_source_names": pipe(source_names),
        "evidence_source_urls": pipe([row["_evidence_source_url"] for row in matches]),
        "evidence_confidence_values": pipe(evidence_confidences),
        "evidence_auto_match_confidence_values": pipe(auto_confidences),
        "evidence_direction_consistency_values": pipe(directions),
        "evidence_spatial_relevance_values": pipe(spatial),
        "evidence_temporal_overlap_hours_total": fmt_number(sum(hours)),
        "evidence_temporal_overlap_hours_max": fmt_number(max(hours) if hours else 0.0),
        "strongest_auto_match_confidence": strongest(auto_confidences, CONFIDENCE_ORDER),
        "strongest_evidence_confidence": strongest(
            evidence_confidences, EVIDENCE_CONFIDENCE_ORDER
        ),
        "dominant_evidence_type": dominant(types),
        "dominant_spatial_relevance": dominant(spatial, DOMINANT_TIE_ORDER),
        "dominant_direction_consistency": dominant(directions, DOMINANT_TIE_ORDER),
        "strongest_reviewed_explanation_strength": strongest(
            [
                strength
                for strength, status in zip(strengths, statuses)
                if status != "pending_review"
            ],
            EXPLANATION_STRENGTH_ORDER,
        ),
        "manual_review_queue_member": bool_text(manual_review_queue_member),
        "manual_evidence_search_scope": (
            "in_review_queue"
            if manual_review_queue_member
            else "not_in_review_queue"
        ),
        "evidence_review_status_summary": unique_pipe(statuses) if statuses else "none",
        "explanation_readiness": ready,
        "explanation_ready_for_ui": bool_text(has_matches),
        "explanation_requires_human_review": bool_text(not has_matches or has_pending),
        "explanation_has_verified_overlap": bool_text(bool(status_counts["verified_overlap"])),
        "explanation_has_plausible_association": bool_text(
            bool(status_counts["plausible_association"])
        ),
        "explanation_has_only_auto_matches": bool_text(
            has_matches and set(statuses) == {"pending_review"}
        ),
        "explanation_has_no_evidence": bool_text(has_no_evidence),
        "explanation_has_data_quality_issue": bool_text(
            bool(status_counts["data_quality_issue"])
        ),
        "explanation_is_unexplained": bool_text(bool(status_counts["unexplained"])),
        "causal_claim_allowed": "false",
        "generated_explanation_text": "",
        "language_guardrail_status": "non_causal_metadata_only",
        "evidence_provenance_summary": provenance,
    }


def enrich_candidates(
    rows: list[dict[str, str]],
    id_field: str,
    candidate_type: str,
    matches_by_candidate: dict[tuple[str, str], list[dict[str, str]]],
    review_queue_keys: set[tuple[str, str]],
) -> list[dict[str, str]]:
    return [
        {
            **row,
            **aggregate(
                matches_by_candidate.get((candidate_type, row[id_field]), []),
                (candidate_type, row[id_field]) in review_queue_keys,
            ),
        }
        for row in rows
    ]


def scan_forbidden(rows: list[dict[str, Any]]) -> dict[str, Any]:
    text = "\n".join(str(value).lower() for row in rows for value in row.values())
    hits = {
        phrase: text.count(phrase)
        for phrase in FORBIDDEN_CAUSAL_PHRASES
        if phrase in text
    }
    return {
        "forbidden_phrase_count": len(FORBIDDEN_CAUSAL_PHRASES),
        "hit_count_total": sum(hits.values()),
        "passed": not hits,
    }


def ids(rows: list[dict[str, str]], field: str) -> list[str]:
    return [row[field] for row in rows]


def main() -> None:
    config = parse_args()
    if config.sensor_mode not in SUPPORTED_MODES:
        raise ValueError("HIGH_COVERAGE_ALL is not supported by Phase 1H-E.")

    output_dir = resolve_output_dir(config.output_dir, config.sensor_mode)
    episode_path = output_dir / "context_enriched_candidate_episodes.csv"
    pulse_path = output_dir / "context_enriched_pulse_groups.csv"
    match_path = output_dir / "candidate_evidence_matches.csv"
    evidence_path = output_dir / "normalized_evidence_manual.csv"
    phase1h_d_diag_path = output_dir / "phase1h_evidence_match_diagnostics.json"
    review_queue_path = output_dir / "phase1h_review_queue.csv"

    protected_files = [
        EVIDENCE_MANUAL,
        EVIDENCE_REVIEWS,
        episode_path,
        pulse_path,
        match_path,
        evidence_path,
        phase1h_d_diag_path,
        review_queue_path,
    ]
    file_digests = {path: optional_digest(path) for path in protected_files}
    frontend_digest = tree_digest(ROOT / "src")
    raw_digest = tree_digest(ROOT / "data" / "raw")

    episodes, episode_fields = read_csv(episode_path)
    pulses, pulse_fields = read_csv(pulse_path)
    matches, _ = read_csv(match_path)
    evidence_rows, _ = read_csv(evidence_path)
    review_queue_rows, _ = read_csv(review_queue_path)
    if not phase1h_d_diag_path.exists():
        raise FileNotFoundError(f"Required input not found: {phase1h_d_diag_path}")
    with phase1h_d_diag_path.open("r", encoding="utf-8") as handle:
        phase1h_d_diagnostics = json.load(handle)
    if phase1h_d_diagnostics.get("sensor_mode") != config.sensor_mode:
        raise ValueError("Phase 1H-D diagnostics sensor mode does not match.")

    review_rows: list[dict[str, str]] = []
    manual_review_file_found = EVIDENCE_REVIEWS.exists()
    if manual_review_file_found:
        review_rows, _ = read_csv(EVIDENCE_REVIEWS)

    episode_ids = set(ids(episodes, "episode_id"))
    pulse_ids = set(ids(pulses, "pulse_group_id"))
    evidence_ids = {row["evidence_id"] for row in evidence_rows}

    linked_matches = joined_matches(matches, evidence_rows, review_rows)
    by_candidate: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in linked_matches:
        by_candidate[(row["candidate_type"], row["candidate_id"])].append(row)
    review_queue_keys = {
        (row.get("candidate_type", ""), row.get("candidate_id", ""))
        for row in review_queue_rows
        if row.get("candidate_type") and row.get("candidate_id")
    }

    episode_outputs = enrich_candidates(
        episodes, "episode_id", "episode", by_candidate, review_queue_keys
    )
    pulse_outputs = enrich_candidates(
        pulses, "pulse_group_id", "pulse_group", by_candidate, review_queue_keys
    )

    episode_output_path = output_dir / "explanation_ready_candidate_episodes.csv"
    pulse_output_path = output_dir / "explanation_ready_pulse_groups.csv"
    diagnostics_path = output_dir / "phase1h_explanation_ready_diagnostics.json"
    write_csv_json(episode_output_path, episode_outputs, episode_fields + ADDED_FIELDS)
    write_csv_json(pulse_output_path, pulse_outputs, pulse_fields + ADDED_FIELDS)

    all_outputs = episode_outputs + pulse_outputs
    language_scan = scan_forbidden(all_outputs)
    output_names = {
        episode_output_path.name,
        episode_output_path.with_suffix(".json").name,
        pulse_output_path.name,
        pulse_output_path.with_suffix(".json").name,
        diagnostics_path.name,
    }
    all_output_fields = set(episode_fields + pulse_fields + ADDED_FIELDS)
    match_candidate_ok = all(
        (row["candidate_type"] == "episode" and row["candidate_id"] in episode_ids)
        or (row["candidate_type"] == "pulse_group" and row["candidate_id"] in pulse_ids)
        for row in matches
    )
    all_match_evidence_ok = all(row["evidence_id"] in evidence_ids for row in matches)
    matched_episode_count = len(
        {
            row["candidate_id"]
            for row in linked_matches
            if row["candidate_type"] == "episode"
        }
    )
    matched_pulse_count = len(
        {
            row["candidate_id"]
            for row in linked_matches
            if row["candidate_type"] == "pulse_group"
        }
    )
    review_statuses = [row["_final_review_status"] for row in linked_matches]
    no_manual_review_fabricated = all(
        row["_manual_review_present"] == "true"
        or row["_final_review_status"] == row.get("review_status", "")
        for row in linked_matches
    )
    outside_review_scope = [
        row
        for row in all_outputs
        if row["manual_review_queue_member"] == "false"
    ]

    sanity_checks = {
        "episode_output_rows_equal_input_rows": len(episode_outputs) == len(episodes),
        "pulse_output_rows_equal_input_rows": len(pulse_outputs) == len(pulses),
        "episode_ids_unique_and_unchanged": ids(episode_outputs, "episode_id")
        == ids(episodes, "episode_id")
        and len(episode_ids) == len(episodes),
        "pulse_group_ids_unique_and_unchanged": ids(pulse_outputs, "pulse_group_id")
        == ids(pulses, "pulse_group_id")
        and len(pulse_ids) == len(pulses),
        "all_matches_reference_existing_candidates": match_candidate_ok,
        "all_matches_reference_existing_evidence": all_match_evidence_ok,
        "manual_review_rows_not_required": True,
        "no_manual_review_fabricated": no_manual_review_fabricated,
        "no_candidates_outside_review_queue_marked_no_evidence_found_or_unexplained": all(
            row["explanation_readiness"] != "no_evidence_found"
            and row["explanation_is_unexplained"] == "false"
            for row in outside_review_scope
        ),
        "causal_claim_allowed_false_for_all_rows": all(
            row["causal_claim_allowed"] == "false" for row in all_outputs
        ),
        "no_forbidden_causal_language": language_scan["passed"],
        "no_ranking_created": "ranking" not in all_output_fields
        and not any("ranking" in name for name in output_names),
        "no_review_priority_score_created": "review_priority_score"
        not in all_output_fields,
        "no_priority_band_created": "priority_band" not in all_output_fields,
        "no_top_n_output_created": not any("top" in name.lower() for name in output_names),
        "no_urban_pulse_index_created": "urban_pulse_index" not in all_output_fields,
        "no_infrastructure_pressure_conclusion_created": "infrastructure_pressure_conclusion"
        not in all_output_fields,
        "no_frontend_files_modified": frontend_digest == tree_digest(ROOT / "src"),
        "no_raw_files_modified": raw_digest == tree_digest(ROOT / "data" / "raw"),
        "evidence_manual_not_modified": file_digests[EVIDENCE_MANUAL]
        == optional_digest(EVIDENCE_MANUAL),
        "evidence_match_reviews_not_modified": file_digests[EVIDENCE_REVIEWS]
        == optional_digest(EVIDENCE_REVIEWS),
        "phase1g_outputs_not_modified": file_digests[episode_path]
        == optional_digest(episode_path)
        and file_digests[pulse_path] == optional_digest(pulse_path),
        "high_coverage_all_not_run": config.sensor_mode != "HIGH_COVERAGE_ALL",
    }
    if not all(sanity_checks.values()):
        failures = [name for name, passed in sanity_checks.items() if not passed]
        raise ValueError(f"Phase 1H-E sanity checks failed: {failures}")

    diagnostics = {
        "processing_version": PROCESSING_VERSION,
        "sensor_mode": config.sensor_mode,
        "input_files": [
            str(episode_path.relative_to(ROOT)),
            str(pulse_path.relative_to(ROOT)),
            str(match_path.relative_to(ROOT)),
            str(evidence_path.relative_to(ROOT)),
            str(phase1h_d_diag_path.relative_to(ROOT)),
            str(review_queue_path.relative_to(ROOT)),
            str(EVIDENCE_REVIEWS.relative_to(ROOT)),
        ],
        "output_files": [
            str(episode_output_path.relative_to(ROOT)),
            str(episode_output_path.with_suffix(".json").relative_to(ROOT)),
            str(pulse_output_path.relative_to(ROOT)),
            str(pulse_output_path.with_suffix(".json").relative_to(ROOT)),
            str(diagnostics_path.relative_to(ROOT)),
        ],
        "episode_input_row_count": len(episodes),
        "episode_output_row_count": len(episode_outputs),
        "pulse_input_row_count": len(pulses),
        "pulse_output_row_count": len(pulse_outputs),
        "evidence_match_input_row_count": len(matches),
        "normalized_evidence_input_row_count": len(evidence_rows),
        "manual_review_file_found": manual_review_file_found,
        "manual_review_row_count": len(review_rows),
        "manual_review_queue_row_count": len(review_queue_rows),
        "matched_episode_count": matched_episode_count,
        "matched_pulse_count": matched_pulse_count,
        "unmatched_episode_count": len(episodes) - matched_episode_count,
        "unmatched_pulse_count": len(pulses) - matched_pulse_count,
        "total_evidence_links_to_episodes": sum(
            row["candidate_type"] == "episode" for row in linked_matches
        ),
        "total_evidence_links_to_pulses": sum(
            row["candidate_type"] == "pulse_group" for row in linked_matches
        ),
        "explanation_readiness_counts_episodes": count_values(
            [row["explanation_readiness"] for row in episode_outputs]
        ),
        "explanation_readiness_counts_pulses": count_values(
            [row["explanation_readiness"] for row in pulse_outputs]
        ),
        "manual_review_queue_member_count_episodes": sum(
            row["manual_review_queue_member"] == "true" for row in episode_outputs
        ),
        "manual_review_queue_member_count_pulses": sum(
            row["manual_review_queue_member"] == "true" for row in pulse_outputs
        ),
        "not_in_manual_review_scope_count_episodes": sum(
            row["explanation_readiness"] == "not_in_manual_review_scope"
            for row in episode_outputs
        ),
        "not_in_manual_review_scope_count_pulses": sum(
            row["explanation_readiness"] == "not_in_manual_review_scope"
            for row in pulse_outputs
        ),
        "evidence_type_counts": count_values(
            [row["evidence_type_normalized"] for row in linked_matches]
        ),
        "evidence_confidence_counts": count_values(
            [row["_evidence_confidence"] for row in linked_matches]
        ),
        "auto_match_confidence_counts": count_values(
            [row["auto_match_confidence"] for row in linked_matches]
        ),
        "direction_consistency_counts": count_values(
            [row["direction_consistency"] for row in linked_matches]
        ),
        "spatial_relevance_counts": count_values(
            [row["spatial_relevance"] for row in linked_matches]
        ),
        "review_status_counts": count_values(review_statuses),
        "explanation_strength_counts": count_values(
            [row["_final_explanation_strength"] for row in linked_matches]
        ),
        "language_guardrail_scan": language_scan,
        "boundary_statements": [
            "Explanation-ready outputs contain structured evidence metadata, not final explanation prose.",
            "Automatic matches remain pending review unless human review rows are supplied.",
            "causal_claim_allowed is false for every output row.",
            "No ranking, priority score, Urban Pulse Index, or infrastructure-pressure conclusion is produced.",
        ],
        "sanity_checks": sanity_checks,
    }
    with diagnostics_path.open("w", encoding="utf-8") as handle:
        json.dump(diagnostics, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(
        f"Wrote {len(episode_outputs)} episode rows and {len(pulse_outputs)} "
        f"pulse rows for {config.sensor_mode} to {output_dir.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
