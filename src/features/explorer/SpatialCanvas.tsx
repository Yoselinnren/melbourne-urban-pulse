import type { PulseIndexItem, SensorIndexItem } from "@/lib/types/ui-data";
import { projectCoordinates } from "@/lib/visualisation/spatial-projection";

type Point = { x: number; y: number };

const visualOffsets: Record<string, Point> = {
  "3": { x: -14, y: 10 },
  "66": { x: 14, y: -10 },
};

const displayLabels: Record<string, string> = {
  "133": "Southern Cross · Lonsdale South",
};

export default function SpatialCanvas({
  sensors,
  pulses,
  selectedPulse,
  selectedSensor,
  hoveredSensor,
  onHover,
  onSelect,
}: {
  sensors: SensorIndexItem[];
  pulses: PulseIndexItem[];
  selectedPulse: PulseIndexItem | null;
  selectedSensor: string | null;
  hoveredSensor: string | null;
  onHover: (id: string | null) => void;
  onSelect: (id: string) => void;
}) {
  const positions = projectCoordinates(sensors.map((sensor) => sensor.coordinates));
  const counts = new Map(
    sensors.map((sensor) => [
      sensor.sensorId,
      pulses.filter((pulse) => pulse.memberSensorIds.includes(sensor.sensorId)).length,
    ]),
  );
  const max = Math.max(1, ...counts.values());

  return (
    <section className="spatial" aria-labelledby="spatial-title">
      <div className="spatial-head">
        <div>
          <span className="eyebrow">Geographic sensor positions</span>
          <h1 id="spatial-title">12 central-Melbourne research sensors</h1>
        </div>
        <div className="spatial-legend">
          <span><i className="dot member" />Selected Pulse member</span>
          <span><i className="ring" />Selected sensor</span>
          <span>Ring size = participation in Pulses currently in view, not pedestrian volume</span>
        </div>
      </div>
      <svg viewBox="0 0 760 470" role="img" aria-labelledby="spatial-svg-title spatial-svg-desc">
        <title id="spatial-svg-title">Central-Melbourne research sensor locations</title>
        <desc id="spatial-svg-desc">
          A longitude–latitude projection of 12 purposively selected sensor locations. Two near-coincident sensors are offset and connected to their geographic anchors. The display does not interpolate a continuous surface or show street boundaries.
        </desc>
        <g className="reference-grid" aria-hidden="true">
          <path d="M54 100H706M54 235H706M54 370H706M180 54V416M380 54V416M580 54V416" />
          <text x="60" y="70">N ↑</text>
          <text x="680" y="445">E →</text>
        </g>
        {sensors.map((sensor, index) => {
          const base = positions[index];
          const offset = visualOffsets[sensor.sensorId] ?? { x: 0, y: 0 };
          const position = { x: base.x + offset.x, y: base.y + offset.y };
          const isOffset = offset.x !== 0 || offset.y !== 0;
          const member = selectedPulse?.memberSensorIds.includes(sensor.sensorId) ?? false;
          const selected = selectedSensor === sensor.sensorId;
          const dim = !!selectedPulse && !member;
          const count = counts.get(sensor.sensorId) ?? 0;
          const radius = 7 + Math.sqrt(count / max) * 10;
          const displayLabel = displayLabels[sensor.sensorId] ?? sensor.shortLabel;

          return (
            <g key={sensor.sensorId}>
              {isOffset && <>
                <line className="sensor-offset-line" x1={base.x} y1={base.y} x2={position.x} y2={position.y} />
                <circle className="sensor-anchor" cx={base.x} cy={base.y} r="2" />
              </>}
              <g
                data-sensor-id={sensor.sensorId}
                className={`sensor-node ${member ? "member" : ""} ${selected ? "selected" : ""} ${dim ? "dim" : ""} ${hoveredSensor === sensor.sensorId ? "hovered" : ""}`}
                transform={`translate(${position.x} ${position.y})`}
              >
                <circle className="participation" r={radius} />
                <circle className="sensor-core" r="6" />
                <foreignObject x="-18" y="-18" width="36" height="36">
                  <button
                    className="sensor-hit"
                    onMouseEnter={() => onHover(sensor.sensorId)}
                    onMouseLeave={() => onHover(null)}
                    onFocus={() => onHover(sensor.sensorId)}
                    onBlur={() => onHover(null)}
                    onClick={() => onSelect(sensor.sensorId)}
                    aria-label={`${sensor.locationName}, sensor ${sensor.sensorId}, ${(sensor.coverageRate * 100).toFixed(2)} percent 2025 coverage, member of ${count} Pulses currently in view`}
                  />
                </foreignObject>
                <text className="sensor-label" x="12" y="-10">{displayLabel}</text>
                <text className="sensor-id" x="12" y="6">ID {sensor.sensorId} · {count}</text>
              </g>
            </g>
          );
        })}
      </svg>
    </section>
  );
}
