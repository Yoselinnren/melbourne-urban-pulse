import type { AnnualOverviewData, PulseDetailData, PulseIndexItem, SensorDetailData, SensorIndexItem } from "@/lib/types/ui-data";
import type { ExplorerState } from "./explorer-state";
import ExplorerStatus from "./ExplorerStatus";

const dt = (value: string) => new Intl.DateTimeFormat("en-AU", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
const label = (value: string) => value.replaceAll("_", " ");
const stateLabel = (value: string) => value === "reviewed_verified_overlap" ? "manually reviewed" : value === "not_in_manual_review_scope" ? "outside manual review set" : label(value);
type Props = { annual: AnnualOverviewData; filtered: PulseIndexItem[]; filters: ExplorerState; pulse: PulseIndexItem | null; sensor: SensorIndexItem | null; pulseDetail: PulseDetailData | null; sensorDetail: SensorDetailData | null; pulseStatus: string; sensorStatus: string; pulseError: string | null; sensorError: string | null; onCloseSensor: () => void; onRetryPulse: () => void; onRetrySensor: () => void };

export default function ContextInspector(props: Props) {
  if (props.sensor) return <SensorInspector {...props} sensor={props.sensor} />;
  if (props.pulse) return <PulseInspector {...props} pulse={props.pulse} />;
  const above = props.filtered.filter((pulse) => pulse.direction === "above").length;
  const counts = {
    localized: props.filtered.filter((pulse) => pulse.scope === "localized").length,
    broad: props.filtered.filter((pulse) => pulse.scope === "broad").length,
    network: props.filtered.filter((pulse) => pulse.scope === "network_wide").length,
  };
  const reviewed = props.filtered.filter((pulse) => pulse.evidenceReadiness !== "not_in_manual_review_scope").length;
  const active = [
    props.filters.month && `month ${props.filters.month}`,
    props.filters.direction && `${props.filters.direction} baseline`,
    ...props.filters.scopes.map((scope) => `${label(scope)} at peak`),
    ...props.filters.evidenceReadiness.map(stateLabel),
  ].filter(Boolean);
  return <aside className="inspector" aria-labelledby="inspector-title">
    <InspectorHead kicker="Annual overview" title="2025 study network" />
    <dl className="facts">
      <Fact k="Study period" v={`${props.annual.studyPeriod.start.slice(0, 10)} — ${props.annual.studyPeriod.end.slice(0, 10)}`} />
      <Fact k="Research sensors" v={props.annual.summary.sensorCount} />
      <Fact k="Pulses under v1 rules" v={props.annual.summary.pulseCount} />
      <Fact k="Pulses in view" v={props.filtered.length} />
      <Fact k="Above / below baseline" v={`${above} / ${props.filtered.length - above}`} />
      <Fact k="Localized / broad / network-wide at peak" v={`${counts.localized} / ${counts.broad} / ${counts.network}`} />
      <Fact k="Missing sensor-hours" v={props.annual.summary.missingRows} />
      <Fact k="Pulses in manual review set" v={reviewed} />
    </dl>
    <Section title="Current filters">
      <p>{active.length ? active.join(" · ") : "All 2025 Pulses are visible."}</p>
      <p>{props.filtered.length} of {props.annual.summary.pulseCount} Pulses are visible.</p>
    </Section>
    <p className="boundary">Pulse counts describe rule-defined departures from local baselines, not total pedestrian volume or a count of verified city events.</p>
  </aside>;
}

function SensorInspector(props: Props & { sensor: SensorIndexItem }) {
  const detail = props.sensorDetail;
  const member = props.pulse?.memberSensorIds.includes(props.sensor.sensorId);
  return <aside className="inspector" aria-labelledby="inspector-title">
    <div className="inspector-title-row">
      <InspectorHead kicker="Sensor details" title={props.sensor.locationName} />
      <button className="close-context" onClick={props.onCloseSensor}>Close sensor</button>
    </div>
    <dl className="facts">
      <Fact k="Sensor ID" v={props.sensor.sensorId} />
      <Fact k="Coordinates" v={`${props.sensor.coordinates.latitude.toFixed(5)}, ${props.sensor.coordinates.longitude.toFixed(5)}`} />
      <Fact k="2025 coverage" v={`${(props.sensor.coverageRate * 100).toFixed(2)}%`} />
      <Fact k="Available / missing hours" v={`${props.sensor.availableHours.toLocaleString()} / ${props.sensor.missingHours}`} />
      <Fact k="Location type" v={props.sensor.locationType} />
    </dl>
    {props.pulse && <p className={`membership ${member ? "yes" : "no"}`}>{member ? "This sensor participates in the selected Pulse." : "This sensor does not participate in the selected Pulse."}</p>}
    <DetailState status={props.sensorStatus} error={props.sensorError} retry={props.onRetrySensor}>{detail && <>
      <Section title="Selection">
        <p>Installed {detail.installationDate ?? "date unavailable"}.</p>
        <p>Selected for the central-Melbourne study network because: {detail.selection.inclusionReason}</p>
      </Section>
      <Section title="Local baseline">
        <p><b>{detail.regularRhythm.length}</b> weekday–hour baseline cells.</p>
        <p>Eligible sample size per cell: {Math.min(...detail.regularRhythm.map((cell) => cell.sampleSize))}–{Math.max(...detail.regularRhythm.map((cell) => cell.sampleSize))}; sample-sufficiency labels: {[...new Set(detail.regularRhythm.map((cell) => cell.baselineConfidence))].join(", ")}.</p>
      </Section>
      <Section title="Pulse participation"><p>Member of <b>{detail.pulseParticipation.length}</b> Pulses across the 2025 result set.</p></Section>
      {detail.limitations.map((limitation) => <p className="boundary" key={limitation}>{limitation}</p>)}
    </>}</DetailState>
  </aside>;
}

function PulseInspector(props: Props & { pulse: PulseIndexItem }) {
  const detail = props.pulseDetail;
  return <aside className="inspector" aria-labelledby="inspector-title">
    <InspectorHead kicker="Selected Pulse" title={dt(props.pulse.start)} />
    <dl className="facts">
      <Fact k="Direction" v={`${props.pulse.direction} baseline`} />
      <Fact k="Peak scope" v={`${label(props.pulse.scope)} at peak`} />
      <Fact k="Duration" v={`${props.pulse.durationHours} hours`} />
      <Fact k="Peak simultaneous sensors" v={props.pulse.maxActiveSensorCount} />
      <Fact k="Sensors involved during period" v={props.pulse.memberSensorCount} />
      <Fact k="Sensor Episodes" v={props.pulse.episodeCount} />
      <Fact k="Strength band" v={label(props.pulse.strengthBand)} />
      <Fact k="Evidence-review state" v={stateLabel(props.pulse.evidenceReadiness)} />
    </dl>
    <p className="boundary">Scope is classified from peak simultaneous participation; the number of active sensors can change each hour.</p>
    <DetailState status={props.pulseStatus} error={props.pulseError} retry={props.onRetryPulse}>{detail && <>
      <Section title="Context">
        <ContextRow name="Public holiday" value={context(detail.context.publicHoliday)} />
        <ContextRow name="School holiday" value={context(detail.context.schoolHoliday)} />
        <ContextRow name="Daylight-saving transition" value={context(detail.context.daylightSaving)} />
        <ContextRow name="Weather in Pulse window" value={detail.context.weather.overlaps ? `${detail.context.weather.rainyHourCount} rainy hours; max wind ${detail.context.weather.windSpeedMax ?? "—"}` : "No weather disruption overlap recorded"} />
        <ContextRow name="Planned works" value="Not assessed in v1" />
      </Section>
      <Section title={`Reviewed evidence · ${detail.evidence.matchCount} sources`}>
        {detail.evidence.items.length === 0 ? <p>No evidence item is linked because this Pulse is outside the purposive manual-review set.</p> : detail.evidence.items.map((evidence) => <article className="evidence-item" key={evidence.matchId}>
          <h4>{evidence.name}</h4>
          <p>{evidence.source.name}</p>
          <ul>
            <li>{evidence.temporalOverlap.hours} hour temporal overlap</li>
            <li>{label(evidence.spatialRelevance)}</li>
            <li>{label(evidence.directionConsistency)}</li>
            <li>Review status: {label(evidence.reviewStatus)}</li>
          </ul>
          {evidence.notes && <p>{evidence.notes}</p>}
          {evidence.warnings.length > 0 && <p>Notes: {evidence.warnings.map(label).join(", ")}.</p>}
          {evidence.source.url && <a href={evidence.source.url} target="_blank" rel="noreferrer">Open source ↗</a>}
        </article>)}
      </Section>
      <p className="boundary">Reviewed overlap describes documented context; it does not establish causation.</p>
      <Section title="Quality + provenance">
        <p>Baseline sample sufficiency: {detail.quality.baselineConfidence}. Weather data missing in {detail.quality.weatherMissingHourCount} Pulse hours.</p>
        <p className="mono">Processing version: {detail.provenance.processingVersions.explanationReady}</p>
      </Section>
    </>}</DetailState>
  </aside>;
}

function InspectorHead({ kicker, title }: { kicker: string; title: string }) { return <header className="inspector-head"><span className="eyebrow">{kicker}</span><h2 id="inspector-title">{title}</h2></header>; }
function Fact({ k, v }: { k: string; v: React.ReactNode }) { return <div><dt>{k}</dt><dd>{v}</dd></div>; }
function Section({ title, children }: { title: string; children: React.ReactNode }) { return <section className="inspector-section"><h3>{title}</h3>{children}</section>; }
function ContextRow({ name, value }: { name: string; value: string }) { return <p className="context-row"><b>{name}</b><span>{value}</span></p>; }
function context(value: { availability: string; overlaps: boolean | null; labels: string[] }) { return value.availability === "deferred" ? "Not assessed in v1" : value.overlaps ? (value.labels.join(", ") || "Overlap recorded") : "No overlap recorded"; }
function DetailState({ status, error, retry, children }: { status: string; error: string | null; retry: () => void; children: React.ReactNode }) { if (status === "loading") return <ExplorerStatus>Loading details…</ExplorerStatus>; if (status === "error") return <ExplorerStatus kind="error" onRetry={retry}>{error ?? "Detail payload could not be loaded."}</ExplorerStatus>; return <>{children}</>; }
