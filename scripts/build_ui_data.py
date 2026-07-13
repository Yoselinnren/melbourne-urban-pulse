#!/usr/bin/env python3
"""Build deterministic, public UI data from REPRESENTATIVE_12 outputs."""
from __future__ import annotations
import argparse,csv,hashlib,json,os,shutil,tempfile
from collections import defaultdict
from datetime import datetime,timedelta
from pathlib import Path
from statistics import median
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

SCHEMA="1.0.0"; MODE="REPRESENTATIVE_12"; PAD=6; TZ=ZoneInfo("Australia/Melbourne")
ROOT=Path(__file__).resolve().parents[1]; PROC=ROOT/"data/processed/representative_12"
FILES={"sensor_selection":ROOT/"data/metadata/analysis_sensor_selection.csv","sensor_locations":ROOT/"data/raw/sensors/pedestrian_sensor_locations.csv","baselines":PROC/"regular_baselines.csv","hour_panel":PROC/"deviation_interpretation_panel.csv","episodes":PROC/"explanation_ready_candidate_episodes.csv","pulses":PROC/"explanation_ready_pulse_groups.csv","evidence_facts":PROC/"normalized_evidence_manual.csv","evidence_matches":PROC/"candidate_evidence_matches.csv","human_reviews":ROOT/"data/manual/evidence_match_reviews.csv"}
DIRECTION={"above_baseline":"above","below_baseline":"below"}; SERIES_DIR={**DIRECTION,"near_baseline":"near","not_applicable":"not_applicable"}; SCOPE={"localized_pulse":"localized","broad_pulse":"broad","network_wide_pulse":"network_wide"}
STRENGTH={x:x for x in ("strong","extreme","mixed_strong_extreme")}; BASECONF={x:x for x in ("high","medium","low","insufficient")}; READINESS={x:x for x in ("auto_matched_pending_review","not_in_manual_review_scope","partially_reviewed","reviewed_verified_overlap","reviewed_plausible_association","reviewed_insufficient_evidence","reviewed_unexplained","reviewed_data_quality_issue","mixed_review_status")}
REVIEW={x:x for x in ("pending_review","verified_overlap","plausible_association","insufficient_evidence","unexplained","data_quality_issue","rejected")}; EVCONF={"high":"high","medium":"moderate","moderate":"moderate","low":"low"}
EVTYPE={x:x for x in "business_closure crowd_observation dst_transition festival_event major_event melbourne_event night_market nightlife_event public_holiday public_transport road_closure school_holiday sports_event unknown_context weather".split()}; EVSCOPE={x:x for x in "city_wide network_wide precinct sensor_specific site_specific state_wide".split()}; EXDIR={x:x for x in ("above","below","unknown")}; SOURCECAT={x:x for x in "commercial_or_industry media official_event_or_venue official_government official_transport official_weather other project_derived social_or_event_platform".split()}; SPATIAL={x:x for x in "broad_context direct_site_match network_context precinct_context sensor_specific_match".split()}; CONSIST={x:x for x in "consistent inconsistent indeterminate".split()}
WEEK={"Monday":0,"Tuesday":1,"Wednesday":2,"Thursday":3,"Friday":4,"Saturday":5,"Sunday":6}

def die(s): raise ValueError(s)
def mapped(m,v,n):
    if v not in m: die(f"Unknown {n}: {v!r}")
    return m[v]
def b(v):
    if v.lower() in ("true","1"): return True
    if v.lower() in ("false","0"): return False
    die(f"Invalid boolean {v!r}")
def num(v): return None if v in (None,"") else float(v)
def integer(v): return int(float(v))
def parts(v): return [] if not v else sorted({x.strip() for x in v.split("|") if x.strip()})
def rows(p):
    with p.open(encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for x in iter(lambda:f.read(1024*1024),b""): h.update(x)
    return h.hexdigest()
def dump(p,o):
    p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
def iso(v): return datetime.fromisoformat(v).replace(tzinfo=TZ) if datetime.fromisoformat(v).tzinfo is None else datetime.fromisoformat(v).astimezone(TZ)
def isostr(d): return d.isoformat(timespec="seconds")
def key(d): return d.strftime("%Y-%m-%dT%H:00")
def safe_url(url,cat):
    if not url:
        if cat=="project_derived": return None,"project_derived_without_url"
        die("Non-project evidence has blank URL")
    if urlparse(url).scheme not in ("http","https"): die(f"Unsafe evidence URL {url!r}")
    return url,"complete"
def percentile(a,q):
    a=sorted(a); return a[min(len(a)-1,int((len(a)-1)*q+0.999999))]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--sensor-mode",required=True); ap.add_argument("--output-dir",required=True); a=ap.parse_args()
    if a.sensor_mode!=MODE: die(f"Only {MODE} is supported")
    diagnostics=sorted(PROC.glob("*diagnostics.json")); inputs={**FILES,**{f"diagnostic_{p.stem}":p for p in diagnostics}}
    for p in inputs.values():
        if not p.is_file(): die(f"Missing input {p.relative_to(ROOT)}")
    ids=[]
    for name,p in sorted(inputs.items()): ids.append((name,p.relative_to(ROOT).as_posix(),digest(p)))
    seed="\n".join([SCHEMA,MODE]+[f"{rel}:{sha}" for _,rel,sha in ids]); version=hashlib.sha256(seed.encode()).hexdigest()[:24]
    diags={p.name:json.loads(p.read_text(encoding="utf-8")) for p in diagnostics}
    d1a=diags["phase1a_diagnostics.json"]; d1b=diags["phase1b_diagnostics.json"]; d1c=diags["phase1c_diagnostics.json"]; d1d=diags["phase1d_diagnostics.json"]; d1e=diags["phase1e_diagnostics.json"]; d1f=diags["phase1f_diagnostics.json"]; d1g=diags["phase1g_context_diagnostics.json"]; d1hm=diags["phase1h_evidence_match_diagnostics.json"]; d1he=diags["phase1h_explanation_ready_diagnostics.json"]
    versions={"contextPanel":d1a["processing_version"],"baselines":d1b["processing_version"],"scoring":d1c["processing_version"],"interpretation":d1d["processing_version"],"episodes":d1e["processing_version"],"pulses":d1f["processing_version"],"contextEnrichment":d1g["processing_version"],"evidenceMatching":d1hm["processing_version"],"explanationReady":d1he["processing_version"]}
    selected={r["sensor_id"]:r for r in rows(FILES["sensor_selection"]) if r["selection_mode"]==MODE and b(r["enabled"])}
    if len(selected)!=12: die(f"Expected 12 selected sensors, got {len(selected)}")
    raw={r["Location_ID"]:r for r in rows(FILES["sensor_locations"])}
    baselines=defaultdict(list)
    for r in rows(FILES["baselines"]):
        sid=r["sensor_id"]
        if sid not in selected: die(f"Unexpected baseline sensor {sid}")
        cell={"weekdayIndex":mapped(WEEK,r["weekday"],"weekday"),"hour":integer(r["hour"]),"median":float(r["median"]),"p25":float(r["p25"]),"p75":float(r["p75"]),"p05":float(r["p05"]),"p95":float(r["p95"]),"sampleSize":integer(r["sample_size"]),"baselineConfidence":mapped(BASECONF,r["baseline_confidence"],"baseline confidence")}; baselines[sid].append(cell)
    for sid in selected:
        baselines[sid].sort(key=lambda x:(x["weekdayIndex"],x["hour"]))
        if len(baselines[sid])!=168: die(f"Sensor {sid} does not have 168 baseline cells")
    episode_rows=rows(FILES["episodes"]); episodes={r["episode_id"]:r for r in episode_rows}
    if len(episodes)!=len(episode_rows): die("Duplicate episode ID")
    pulse_rows=rows(FILES["pulses"]); pulse_rows.sort(key=lambda r:(r["start_timestamp"],r["pulse_group_id"])); pulse_by_id={r["pulse_group_id"]:r for r in pulse_rows}
    facts={r["evidence_id"]:r for r in rows(FILES["evidence_facts"])}; matches=rows(FILES["evidence_matches"]); reviews={(r["candidate_type"],r["candidate_id"],r["evidence_id"]):r for r in rows(FILES["human_reviews"])}
    pulse_matches=defaultdict(list)
    for m in matches:
        if m["candidate_type"]=="pulse_group": pulse_matches[m["candidate_id"]].append(m)
        elif m["candidate_type"]!="episode": die(f"Unknown candidate type {m['candidate_type']}")
    study_start=iso(d1a["study_period"]["start"]); study_end=iso(d1a["study_period"]["end"])
    windows={}; window_pulses=defaultdict(list); intervals=defaultdict(lambda:defaultdict(list)); index=[]
    for p in pulse_rows:
        pid=p["pulse_group_id"]; start=iso(p["start_timestamp"]); end=iso(p["end_timestamp"]); req0=start-timedelta(hours=PAD); req1=end+timedelta(hours=PAD); act0=max(req0,study_start); act1=min(req1,study_end)
        windows[pid]={"requestedStart":isostr(req0),"requestedEnd":isostr(req1),"actualStart":isostr(act0),"actualEnd":isostr(act1),"paddingHours":PAD,"wasClamped":req0<study_start or req1>study_end}
        t=act0
        while t<=act1: window_pulses[key(t)].append(pid); t+=timedelta(hours=1)
        eids=parts(p["episode_ids"]); sids=parts(p["sensor_ids"])
        for eid in eids:
            if eid not in episodes: die(f"Pulse {pid} references missing episode {eid}")
            e=episodes[eid]
            intervals[pid][e["sensor_id"]].append((datetime.fromisoformat(e["start_local_timestamp_key"]),datetime.fromisoformat(e["end_local_timestamp_key"])))
        item={"pulseId":pid,"start":p["start_timestamp"],"end":p["end_timestamp"],"month":start.month,"direction":mapped(DIRECTION,p["pulse_direction"],"pulse direction"),"scope":mapped(SCOPE,p["pulse_scope"],"pulse scope"),"durationHours":integer(p["duration_hours"]),"maxActiveSensorCount":integer(p["max_active_sensor_count"]),"memberSensorCount":integer(p["sensor_count"]),"memberSensorIds":sorted(sids,key=int),"episodeCount":integer(p["episode_count"]),"strengthBand":mapped(STRENGTH,p["dominant_strength_band"],"strength"),"evidenceMatchCount":integer(p["evidence_match_count"]),"evidenceReadiness":mapped(READINESS,p["explanation_readiness"],"evidence readiness"),"requiresHumanReview":b(p["explanation_requires_human_review"]),"storyCategory":None}
        if b(p["causal_claim_allowed"]) or p["generated_explanation_text"].strip(): die(f"Unsafe causal fields on {pid}")
        index.append(item)
    index_by_id={x["pulseId"]:x for x in index}; series=defaultdict(list); sensor_meta={}
    panel_count=missing_count=0
    with FILES["hour_panel"].open(encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f):
            panel_count+=1; sid=r["sensor_id"]
            if sid not in selected: die(f"Unexpected panel sensor {sid}")
            sensor_meta.setdefault(sid,r); missing=b(r["is_missing"]); missing_count+=int(missing)
            observed=num(r["observed_count"])
            if missing and observed is not None: die("Missing observation has numeric value")
            if not missing and observed is None: die("Observed row has null value")
            for pid in window_pulses.get(r["local_timestamp_key"],[]):
                local=datetime.fromisoformat(r["local_timestamp_key"]); member=any(a0<=local<=a1 for a0,a1 in intervals[pid][sid])
                point={"timestamp":r["timestamp"],"sensorId":sid,"observedCount":observed,"isMissing":missing,"missingReason":r["missing_reason"] or None,"expected":{"median":num(r["baseline_median"]),"p25":num(r["baseline_p25"]),"p75":num(r["baseline_p75"]),"p05":num(r["baseline_p05"]),"p95":num(r["baseline_p95"]),"sampleSize":None if not r["baseline_sample_size"] else integer(r["baseline_sample_size"]),"baselineConfidence":None if not r["baseline_confidence"] else mapped(BASECONF,r["baseline_confidence"],"baseline confidence")},"robustZScore":num(r["robust_z_score"]),"anomalyStrength":num(r["anomaly_strength"]),"scoringConfidence":num(r["scoring_confidence"]),"direction":mapped(SERIES_DIR,r["deviation_direction"],"series direction"),"isPulseMemberAtTimestamp":member}; series[pid].append(point)
    if panel_count!=105120 or missing_count!=16: die(f"Unexpected panel counts {panel_count}/{missing_count}")
    sensor_order=sorted(selected,key=int)
    for pid in series: series[pid].sort(key=lambda x:(x["timestamp"],int(x["sensorId"])))
    def evidence_item(m):
        if m["evidence_id"] not in facts: die(f"Dangling evidence {m['evidence_id']}")
        e=facts[m["evidence_id"]]; cat=mapped(SOURCECAT,e["source_category"],"source category"); url,complete=safe_url(e["source_url"],cat); rev=reviews.get((m["candidate_type"],m["candidate_id"],m["evidence_id"])); status=mapped(REVIEW,(rev or m)["review_status"],"review status")
        coords=None if not e["latitude"] else {"latitude":float(e["latitude"]),"longitude":float(e["longitude"])}
        return {"evidenceId":e["evidence_id"],"matchId":m["match_id"],"name":e["evidence_name"],"type":mapped(EVTYPE,e["evidence_type_normalized"],"evidence type"),"source":{"name":e["source_name"],"category":cat,"url":url,"accessedDate":e["source_accessed_date"] or None,"completeness":complete},"interval":{"start":e["start_timestamp_normalized"],"end":e["end_timestamp_normalized"]},"location":{"name":e["location_name"] or None,"precinct":e["precinct"] or None,"coordinates":coords,"spatialScope":mapped(EVSCOPE,e["spatial_scope_normalized"],"evidence scope")},"expectedDirection":mapped(EXDIR,e["expected_direction_normalized"],"expected direction"),"evidenceConfidence":mapped(EVCONF,e["evidence_confidence_normalized"],"evidence confidence"),"temporalOverlap":{"overlaps":b(m["temporal_overlap"]),"hours":float(m["temporal_overlap_hours"]),"candidateRatio":float(m["temporal_overlap_ratio_candidate"]),"evidenceRatio":float(m["temporal_overlap_ratio_evidence"])},"spatialRelevance":mapped(SPATIAL,m["spatial_relevance"],"spatial relevance"),"directionConsistency":mapped(CONSIST,m["direction_consistency"],"direction consistency"),"automaticMatchConfidence":mapped(EVCONF,m["auto_match_confidence"],"automatic match confidence"),"reviewStatus":status,"reviewedAt":(rev or {}).get("reviewed_at") or None,"notes":e["notes"] or None,"warnings":parts(e["evidence_validation_warnings"])+parts(m["auto_match_warnings"]),"causalClaimAllowed":False}
    out=Path(a.output_dir); out=out if out.is_absolute() else ROOT/out; out.parent.mkdir(parents=True,exist_ok=True); staged=Path(tempfile.mkdtemp(prefix=f".{out.name}.tmp-",dir=out.parent))
    try:
        dump(staged/"pulses/index.json",{"schemaVersion":SCHEMA,"dataVersion":version,"sensorMode":MODE,"items":index})
        participation=defaultdict(list)
        for p in pulse_rows:
            pid=p["pulse_group_id"]; item=index_by_id[pid]; es=[]
            for eid in parts(p["episode_ids"]):
                e=episodes[eid]; es.append({"episodeId":eid,"sensorId":e["sensor_id"],"sensorLabel":e["sensor_short_label"],"start":e["start_timestamp"],"end":e["end_timestamp"],"durationHours":integer(e["duration_hours"]),"direction":mapped(DIRECTION,e["episode_direction"],"episode direction"),"peakAbsScore":float(e["peak_abs_score"]),"meanAbsScore":float(e["mean_abs_score"]),"strengthBand":mapped(STRENGTH,e["episode_strength_band"],"episode strength"),"baselineConfidence":mapped(BASECONF,e["baseline_confidence_band"],"episode baseline confidence"),"interpretationWarnings":parts(e["interpretation_warning_summary"])})
            es.sort(key=lambda x:(x["start"],int(x["sensorId"]),x["episodeId"]))
            for sid in item["memberSensorIds"]: participation[sid].append({"pulseId":pid,"episodeIds":[e["episodeId"] for e in es if e["sensorId"]==sid]})
            frames=[]
            for ts in sorted({x["timestamp"] for x in series[pid]}):
                pts=[x for x in series[pid] if x["timestamp"]==ts]; frames.append({"timestamp":ts,"activeSensorCount":sum(x["isPulseMemberAtTimestamp"] for x in pts),"availableSensorCount":sum(not x["isMissing"] for x in pts),"points":[{"sensorId":x["sensorId"],"observedCount":x["observedCount"],"isMissing":x["isMissing"],"direction":x["direction"],"anomalyStrength":x["anomalyStrength"],"isPulseMemberAtTimestamp":x["isPulseMemberAtTimestamp"]} for x in pts]})
            ev=[evidence_item(m) for m in sorted(pulse_matches[pid],key=lambda x:(x["evidence_id"],x["match_id"]))]; source_complete="project_derived_without_url" if any(x["source"]["completeness"]=="project_derived_without_url" for x in ev) else ("complete" if ev else "not_researched")
            context={"publicHoliday":{"availability":"available","overlaps":b(p["public_holiday_overlap"]),"labels":parts(p["public_holiday_labels"])},"schoolHoliday":{"availability":"available","overlaps":b(p["school_holiday_overlap"]),"labels":parts(p["school_holiday_labels"])},"daylightSaving":{"availability":"available","overlaps":b(p["dst_transition_overlap"]),"labels":parts(p["dst_transition_labels"])},"weather":{"availability":"available","overlaps":b(p["provisional_weather_disruption_overlap"]),"rainyHourCount":integer(p["rainy_hour_count"]),"rainTotal":num(p["rain_total"]),"temperatureMean":num(p["temperature_mean"]),"windSpeedMax":num(p["wind_speed_max"])},"plannedWorks":{"availability":"deferred","overlaps":None}}
            detail={"schemaVersion":SCHEMA,"dataVersion":version,"pulse":{**item,"activeHourCount":integer(p["active_hour_count"]),"strength":{"maxPeakAbsScore":float(p["max_peak_abs_score"]),"meanPeakAbsScore":float(p["mean_peak_abs_score"]),"maxMeanAbsScore":float(p["max_mean_abs_score"])}},"displayWindow":windows[pid],"episodes":es,"series":series[pid],"spatialFrames":frames,"context":context,"evidence":{"readiness":item["evidenceReadiness"],"matchCount":len(ev),"reviewedMatchCount":sum(x["reviewStatus"]!="pending_review" for x in ev),"items":ev,"causalClaimAllowed":False},"quality":{"weatherMissingHourCount":integer(p["weather_missing_hour_count"]),"baselineConfidence":mapped(BASECONF,p["member_baseline_confidence_min"],"pulse baseline confidence"),"sourceCompleteness":source_complete},"provenance":{"processingVersions":versions,"baselineMethod":"eligible regular observations grouped by sensor_id + weekday + hour","primaryScoreSource":"robust_z_score"}}
            dump(staged/f"pulses/{pid}.json",detail)
        sensor_index=[]
        for sid in sensor_order:
            s=selected[sid]; meta=sensor_meta[sid]; rawrow=raw.get(sid,{})
            si={"sensorId":sid,"locationName":s["location_label"],"shortLabel":meta["sensor_short_label"],"sensorName":s["sensor_name"],"coordinates":{"latitude":float(s["latitude"]),"longitude":float(s["longitude"])},"coverageRate":float(s["coverage_rate"]),"availableHours":integer(s["available_2025_hours"]),"missingHours":integer(s["missing_2025_hours"]),"locationType":meta["sensor_location_type"],"selectionTier":s["selection_tier"]}; sensor_index.append(si)
            sd={"schemaVersion":SCHEMA,"dataVersion":version,"sensorId":sid,"sensorName":s["sensor_name"],"locationName":s["location_label"],"shortLabel":meta["sensor_short_label"],"precinct":meta["precinct"] or None,"status":rawrow.get("Status") or s["status"],"locationType":rawrow.get("Location_Type") or meta["sensor_location_type"],"installationDate":rawrow.get("Installation_Date") or None,"coordinates":si["coordinates"],"coverage":{"rate":si["coverageRate"],"availableHours":si["availableHours"],"missingHours":si["missingHours"]},"selection":{"tier":s["selection_tier"],"inclusionReason":s["inclusion_reason"]},"regularRhythm":baselines[sid],"pulseParticipation":sorted(participation[sid],key=lambda x:x["pulseId"]),"mediaIds":[],"limitations":["Coverage describes the 2025 analytical period.","No media mapping is available in UI-0."]}; dump(staged/f"sensors/{sid}.json",sd)
        dump(staged/"sensors/index.json",{"schemaVersion":SCHEMA,"dataVersion":version,"sensorMode":MODE,"items":sensor_index})
        monthly=[]
        for month in range(1,13):
            xs=[x for x in index if x["month"]==month]; monthly.append({"month":month,"total":len(xs),"above":sum(x["direction"]=="above" for x in xs),"below":sum(x["direction"]=="below" for x in xs),"localized":sum(x["scope"]=="localized" for x in xs),"broad":sum(x["scope"]=="broad" for x in xs),"networkWide":sum(x["scope"]=="network_wide" for x in xs),"autoMatchedPendingReview":sum(x["evidenceReadiness"]=="auto_matched_pending_review" for x in xs),"outsideManualReviewScope":sum(x["evidenceReadiness"]=="not_in_manual_review_scope" for x in xs)})
        annual={"schemaVersion":SCHEMA,"dataVersion":version,"sensorMode":MODE,"studyPeriod":{"start":isostr(study_start),"end":isostr(study_end),"timezone":"Australia/Melbourne"},"summary":{"sensorCount":12,"nominalHourlyKeys":d1a["hourly_timestamp_count"],"sensorHourRows":panel_count,"observedRows":panel_count-missing_count,"missingRows":missing_count,"baselineGroupCount":d1b["baseline_group_count"],"episodeCount":len(episode_rows),"pulseCount":len(index),"pulseDirectionCounts":{"above":sum(x["direction"]=="above" for x in index),"below":sum(x["direction"]=="below" for x in index)},"pulseScopeCounts":{"localized":sum(x["scope"]=="localized" for x in index),"broad":sum(x["scope"]=="broad" for x in index),"network_wide":sum(x["scope"]=="network_wide" for x in index)},"evidenceFactCount":len(facts),"evidenceMatchCount":len(matches),"reviewedMatchCount":len(reviews)},"monthly":monthly,"processingVersions":versions,"limitations":["The twelve sensors are a representative central-Melbourne subset.","Context and evidence describe overlap and review state, not causal attribution.","Automatic evidence matches remain pending human review.","Observations use a nominal 8,760-hour local-year convention."]}; dump(staged/"annual-overview.json",annual)
        payloads=list(staged.rglob("*.json")); entries=sorted(((p.relative_to(staged).as_posix(),digest(p),p.stat().st_size) for p in payloads),key=lambda x:x[0]); sizes=[n for path,_,n in entries if path.startswith("pulses/") and path!="pulses/index.json"]
        counts={"sensorCount":len(sensor_index),"pulseCount":len(index),"sourceCandidateEpisodeCount":len(episode_rows),"pulseMemberEpisodeCount":len({e for p in pulse_rows for e in parts(p["episode_ids"])}),"evidenceFactCount":len(facts),"evidenceMatchCount":len(matches),"humanReviewCount":len(reviews),"autoMatchedPendingReviewPulses":sum(x["evidenceReadiness"]=="auto_matched_pending_review" for x in index),"outsideManualReviewScopePulses":sum(x["evidenceReadiness"]=="not_in_manual_review_scope" for x in index)}
        stats={"pulseDetailTotalBytes":sum(sizes),"pulseDetailMinimumBytes":min(sizes),"pulseDetailMedianBytes":int(median(sizes)),"pulseDetailP95Bytes":percentile(sizes,.95),"pulseDetailMaximumBytes":max(sizes),"pulseDetailFilesAbove150KB":sum(x>150*1024 for x in sizes)}
        tree=lambda xs:hashlib.sha256("\n".join(f"{p}:{h}" for p,h,_ in xs).encode()).hexdigest()
        manifest={"schemaVersion":SCHEMA,"dataVersion":version,"sensorMode":MODE,"inputDigests":[{"logicalName":n,"sha256":sha} for n,_,sha in ids],"processingVersions":versions,"recordCounts":counts,"outputFileCounts":{"payloadFiles":len(payloads),"pulseDetailFiles":len(index),"sensorDetailFiles":len(sensor_index),"totalIncludingManifest":len(payloads)+1},"outputDigests":{"payloadTreeSha256":tree(entries),"pulseDetailTreeSha256":tree([x for x in entries if x[0].startswith("pulses/") and x[0]!="pulses/index.json"]),"sensorDetailTreeSha256":tree([x for x in entries if x[0].startswith("sensors/") and x[0]!="sensors/index.json"])},"displayWindowPolicy":{"paddingHours":PAD,"clampToStudyPeriod":True},"payloadStatistics":stats}; dump(staged/"manifest.json",manifest)
        backup=out.with_name(out.name+".backup")
        if backup.exists(): shutil.rmtree(backup)
        if out.exists(): os.replace(out,backup)
        try: os.replace(staged,out)
        except Exception:
            if backup.exists(): os.replace(backup,out)
            raise
        if backup.exists(): shutil.rmtree(backup)
        total=sum(p.stat().st_size for p in out.rglob("*.json")); print(f"Built {len(list(out.rglob('*.json')))} files, {total} bytes, dataVersion={version}")
    finally:
        if staged.exists(): shutil.rmtree(staged)
if __name__=="__main__": main()
