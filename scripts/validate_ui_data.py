#!/usr/bin/env python3
"""Independent on-disk validator for public UI data v1."""
import argparse,hashlib,json,re,statistics
from collections import defaultdict
from pathlib import Path

SCHEMA="1.0.0"; MODE="REPRESENTATIVE_12"; LIMITS={"manifest.json":25*1024,"annual-overview.json":50*1024,"sensors/index.json":10*1024,"pulses/index.json":200*1024}; FORBIDDEN=("data/raw/","data/processed/","photos/raw/",".venv/","urban pulse index","priority score","reviewer identity","generated causal")
def fail(s): raise ValueError(s)
def load(p):
    try:return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e: fail(f"Invalid JSON {p}: {e}")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def need(o,keys,where):
    if not isinstance(o,dict): fail(f"Expected object at {where}")
    missing=[k for k in keys if k not in o]
    if missing: fail(f"Missing {missing} at {where}")
def walk(v,path="$"):
    if isinstance(v,dict):
        for k,x in v.items():
            if k.lower() in ("reviewedby","reviewer_notes","reviewernotes","generatedexplanationtext"): fail(f"Private/unsafe key {path}.{k}")
            if k=="causalClaimAllowed" and x is not False: fail(f"Causal flag not false at {path}")
            walk(x,f"{path}.{k}")
    elif isinstance(v,list):
        for i,x in enumerate(v): walk(x,f"{path}[{i}]")
    elif isinstance(v,str):
        low=v.replace("\\","/").lower()
        if re.match(r"^[a-z]:/",low) or (low.startswith("/") and not low.startswith("//")): fail(f"Absolute path at {path}")
        for token in FORBIDDEN:
            if token in low: fail(f"Forbidden public text {token!r} at {path}")
def pct(a,q): a=sorted(a);return a[min(len(a)-1,int((len(a)-1)*q+.999999))]
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input-dir",required=True);a=ap.parse_args();root=Path(a.input_dir)
    if not root.is_dir(): fail(f"Missing input directory {root}")
    files=sorted(root.rglob("*.json")); docs={p.relative_to(root).as_posix():load(p) for p in files}
    for path,o in docs.items(): walk(o,path)
    m=docs.get("manifest.json"); need(m,["schemaVersion","dataVersion","sensorMode","inputDigests","processingVersions","recordCounts","outputFileCounts","outputDigests","displayWindowPolicy","payloadStatistics"],"manifest")
    if m["schemaVersion"]!=SCHEMA or m["sensorMode"]!=MODE: fail("Manifest schema/mode mismatch")
    version=m["dataVersion"]; payload_paths=sorted(set(docs)-{"manifest.json"})
    if len(payload_paths)!=m["outputFileCounts"]["payloadFiles"]: fail("Payload file count mismatch")
    tree=lambda xs:hashlib.sha256("\n".join(f"{p}:{sha(root/p)}" for p in xs).encode()).hexdigest()
    if tree(payload_paths)!=m["outputDigests"]["payloadTreeSha256"]: fail("Payload tree digest mismatch")
    if tree([p for p in payload_paths if p.startswith("pulses/") and p!="pulses/index.json"])!=m["outputDigests"]["pulseDetailTreeSha256"]: fail("Pulse tree digest mismatch")
    if tree([p for p in payload_paths if p.startswith("sensors/") and p!="sensors/index.json"])!=m["outputDigests"]["sensorDetailTreeSha256"]: fail("Sensor tree digest mismatch")
    c=m["recordCounts"]
    exact={"sensorCount":12,"pulseCount":425,"sourceCandidateEpisodeCount":4647,"evidenceFactCount":64,"evidenceMatchCount":64,"humanReviewCount":64,"autoMatchedPendingReviewPulses":0,"outsideManualReviewScopePulses":410}
    for k,v in exact.items():
        if c.get(k)!=v: fail(f"Expected {k}={v}, got {c.get(k)}")
    annual=docs["annual-overview.json"]; need(annual,["schemaVersion","dataVersion","sensorMode","studyPeriod","summary","monthly","processingVersions","limitations"],"annual")
    if annual["dataVersion"]!=version or annual["summary"]["missingRows"]!=16 or annual["summary"]["observedRows"]!=105104: fail("Annual version/missingness counts mismatch")
    if len(annual["monthly"])!=12 or sum(x["total"] for x in annual["monthly"])!=425: fail("Monthly totals mismatch")
    pindex=docs["pulses/index.json"]; sindex=docs["sensors/index.json"]
    if pindex["dataVersion"]!=version or len(pindex["items"])!=425: fail("Pulse index mismatch")
    if sindex["dataVersion"]!=version or len(sindex["items"])!=12: fail("Sensor index mismatch")
    pulse_ids=[x["pulseId"] for x in pindex["items"]]; sensor_ids=[x["sensorId"] for x in sindex["items"]]
    if len(set(pulse_ids))!=425 or len(set(sensor_ids))!=12: fail("Duplicate index ID")
    pmap={x["pulseId"]:x for x in pindex["items"]}; all_episode_ids=set(); expected_part=defaultdict(dict); pending=outside=reviewed=0
    pulse_sizes=[]; max_pair=(0,"")
    for pid in pulse_ids:
        path=f"pulses/{pid}.json"; d=docs.get(path); need(d,["schemaVersion","dataVersion","pulse","displayWindow","episodes","series","spatialFrames","context","evidence","quality","provenance"],path)
        if d["schemaVersion"]!=SCHEMA or d["dataVersion"]!=version: fail(f"Version mismatch {pid}")
        for k,v in pmap[pid].items():
            if d["pulse"].get(k)!=v: fail(f"Pulse index/detail mismatch {pid}.{k}")
        if not set(d["pulse"]["memberSensorIds"])<=set(sensor_ids): fail(f"Dangling sensor in {pid}")
        eids=[]
        for e in d["episodes"]:
            if e["sensorId"] not in sensor_ids or e["episodeId"] in eids: fail(f"Bad/duplicate member episode {e['episodeId']}")
            all_episode_ids.add(e["episodeId"]);eids.append(e["episodeId"]);expected_part[e["sensorId"]].setdefault(pid,[]).append(e["episodeId"])
        if len(eids)!=d["pulse"]["episodeCount"]: fail(f"Episode count mismatch {pid}")
        byts=defaultdict(dict)
        for x in d["series"]:
            if x["sensorId"] not in sensor_ids: fail(f"Dangling series sensor {pid}")
            if x["isMissing"] and x["observedCount"] is not None: fail(f"Missing value not null {pid}")
            if not x["isMissing"] and x["observedCount"] is None: fail(f"Observed value null {pid}")
            if x["sensorId"] in byts[x["timestamp"]]: fail(f"Duplicate series point {pid}")
            byts[x["timestamp"]][x["sensorId"]]=x
        if set(byts)!={x["timestamp"] for x in d["spatialFrames"]}: fail(f"Frame timestamp mismatch {pid}")
        for f in d["spatialFrames"]:
            if len(f["points"])!=12 or set(x["sensorId"] for x in f["points"])!=set(sensor_ids): fail(f"Frame sensor set mismatch {pid}")
            if f["activeSensorCount"]!=sum(x["isPulseMemberAtTimestamp"] for x in f["points"]) or f["availableSensorCount"]!=sum(not x["isMissing"] for x in f["points"]): fail(f"Frame count mismatch {pid}")
            for x in f["points"]:
                s=byts[f["timestamp"]][x["sensorId"]]
                for k in ("observedCount","isMissing","direction","anomalyStrength","isPulseMemberAtTimestamp"):
                    if x[k]!=s[k]: fail(f"Series/frame mismatch {pid}/{f['timestamp']}/{x['sensorId']}/{k}")
        if d["context"]["plannedWorks"]!={"availability":"deferred","overlaps":None}: fail(f"Planned works semantics {pid}")
        if d["evidence"]["causalClaimAllowed"] is not False: fail(f"Causal flag {pid}")
        if len(d["evidence"]["items"])!=d["evidence"]["matchCount"] or d["evidence"]["matchCount"]!=d["pulse"]["evidenceMatchCount"]: fail(f"Evidence count {pid}")
        for e in d["evidence"]["items"]:
            if e["reviewStatus"]=="pending_review": pending+=1
            else: reviewed+=1
            u=e["source"]["url"]; comp=e["source"]["completeness"]
            if u is None and comp!="project_derived_without_url": fail(f"Null URL completeness {pid}")
            if u is not None and not (u.startswith("http://") or u.startswith("https://")): fail(f"Invalid URL {pid}")
        outside+=d["evidence"]["readiness"]=="not_in_manual_review_scope"
        size=(root/path).stat().st_size;pulse_sizes.append(size);max_pair=max(max_pair,(size,pid))
    if pending!=0 or reviewed!=63 or outside!=410: fail("Evidence review/readiness totals mismatch")
    if len(all_episode_ids)!=c["pulseMemberEpisodeCount"] or len(all_episode_ids)>=4647: fail("Pulse member episode semantics mismatch")
    for sid in sensor_ids:
        d=docs.get(f"sensors/{sid}.json");need(d,["schemaVersion","dataVersion","sensorId","regularRhythm","pulseParticipation","mediaIds"],f"sensor {sid}")
        if d["sensorId"]!=sid or d["dataVersion"]!=version or len(d["regularRhythm"])!=168 or d["mediaIds"]!=[]: fail(f"Sensor detail mismatch {sid}")
        cells={(x["weekdayIndex"],x["hour"]) for x in d["regularRhythm"]}
        if cells!={(w,h) for w in range(7) for h in range(24)}: fail(f"Rhythm grid mismatch {sid}")
        got={x["pulseId"]:sorted(x["episodeIds"]) for x in d["pulseParticipation"]}; exp={pid:sorted(eids) for pid,eids in expected_part[sid].items()}
        if got!=exp: fail(f"Sensor participation mismatch {sid}")
    for path,limit in LIMITS.items():
        if (root/path).stat().st_size>limit: fail(f"Hard payload limit exceeded: {path}")
    for sid in sensor_ids:
        if (root/f"sensors/{sid}.json").stat().st_size>75*1024: fail(f"Sensor detail hard limit {sid}")
    hard=sum(x>250*1024 for x in pulse_sizes)
    if hard: fail(f"{hard} Pulse details exceed 250 KB")
    total=sum(p.stat().st_size for p in files);warn=sum(x>150*1024 for x in pulse_sizes)
    print("UI data validation passed")
    print(f"Pulse detail file count: {len(pulse_sizes)}")
    print(f"Pulse detail total raw bytes: {sum(pulse_sizes)}")
    print(f"Pulse detail minimum/median/p95/maximum: {min(pulse_sizes)}/{int(statistics.median(pulse_sizes))}/{pct(pulse_sizes,.95)}/{max(pulse_sizes)}")
    print(f"Maximum-size Pulse ID: {max_pair[1]}")
    print(f"Files above 150 KB / 250 KB: {warn}/{hard}")
    print(f"UI data total files / raw bytes: {len(files)}/{total}")
if __name__=="__main__": main()
