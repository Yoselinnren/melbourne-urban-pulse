import type { PulseIndexItem } from "@/lib/types/ui-data";

const lanes = [["network_wide", "Network-wide at peak"], ["broad", "Broad at peak"], ["localized", "Localized at peak"]] as const;
const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const yearStart = Date.parse("2025-01-01T00:00:00+11:00");
const yearMs = 365 * 24 * 3600e3;

export default function TemporalRibbon({ pulses, selected, hovered, onHover, onSelect }: { pulses: PulseIndexItem[]; selected: string | null; hovered: string | null; onHover: (id: string | null) => void; onSelect: (id: string) => void }) {
  return <section className="timeline" aria-labelledby="timeline-title">
    <div className="timeline-heading">
      <div><span className="eyebrow">Annual navigation</span><h2 id="timeline-title">2025 Pulse timeline</h2></div>
      <div className="timeline-legend"><span className="above-key">▲ Above baseline</span><span className="below-key">▼ Below baseline</span><span className="pending-key">• Manually reviewed</span></div>
    </div>
    {pulses.length === 0 ? <div className="timeline-empty" role="status">No Pulses match the current filters. Change or reset the filters to restore the annual view.</div> : <div className="timeline-chart">
      <div className="month-axis">{months.map((month) => <span key={month}>{month}</span>)}</div>
      {lanes.map(([scope, laneLabel]) => {
        const matches = pulses.filter((pulse) => pulse.scope === scope);
        return <div className="timeline-lane" key={scope}><span className="lane-label">{laneLabel}</span><div className="lane-track">{matches.map((pulse, index) => {
          const left = Math.max(0, Math.min(99.5, (Date.parse(pulse.start) - yearStart) / yearMs * 100));
          const width = Math.max(.45, pulse.durationHours / 8760 * 100);
          const reviewed = pulse.evidenceReadiness !== "not_in_manual_review_scope";
          return <button
            key={pulse.pulseId}
            className={`pulse-mark ${pulse.direction} ${selected === pulse.pulseId ? "selected" : ""} ${hovered === pulse.pulseId ? "hovered" : ""} ${reviewed ? "pending" : ""}`}
            style={{ left: `${left}%`, width: `${width}%`, top: `${5 + (index % 3) * 14}px` }}
            onMouseEnter={() => onHover(pulse.pulseId)}
            onMouseLeave={() => onHover(null)}
            onFocus={() => onHover(pulse.pulseId)}
            onBlur={() => onHover(null)}
            onClick={() => onSelect(pulse.pulseId)}
            aria-label={`${pulse.start} to ${pulse.end}; ${pulse.direction} baseline; ${laneLabel}; ${pulse.durationHours} hours; peak ${pulse.maxActiveSensorCount} simultaneous sensors; ${pulse.evidenceReadiness.replaceAll("_", " ")}`}
          />;
        })}</div></div>;
      })}
    </div>}
  </section>;
}
