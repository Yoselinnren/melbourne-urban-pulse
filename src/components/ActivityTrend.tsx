import { formatHour, getTotalActivity } from "@/lib/dashboard-data";
import type { HourlyRecord } from "@/lib/types";

type ActivityTrendProps = {
  records: HourlyRecord[];
};

export function ActivityTrend({ records }: ActivityTrendProps) {
  const width = 760;
  const height = 260;
  const padding = 34;
  const values = records.map(getTotalActivity);
  const max = Math.max(...values, 1);
  const points = values.map((value, index) => {
    const x =
      padding +
      (index / Math.max(records.length - 1, 1)) * (width - padding * 2);
    const y = height - padding - (value / max) * (height - padding * 2);
    return { x, y, value, record: records[index] };
  });
  const path = points
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`)
    .join(" ");
  const peak = points.reduce((current, point) =>
    point.value > current.value ? point : current,
  );

  return (
    <div>
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-gradient-to-br from-slate-950 to-slate-800 p-3">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          role="img"
          aria-label="Mock 24-hour activity trend"
          className="h-72 w-full"
        >
          <defs>
            <linearGradient id="trendFill" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.45" />
              <stop offset="100%" stopColor="#22d3ee" stopOpacity="0" />
            </linearGradient>
          </defs>
          {[0.25, 0.5, 0.75, 1].map((tick) => {
            const y = height - padding - tick * (height - padding * 2);
            return (
              <line
                key={tick}
                x1={padding}
                x2={width - padding}
                y1={y}
                y2={y}
                stroke="rgba(226,232,240,0.16)"
              />
            );
          })}
          <path
            d={`${path} L ${width - padding} ${height - padding} L ${padding} ${
              height - padding
            } Z`}
            fill="url(#trendFill)"
          />
          <path
            d={path}
            fill="none"
            stroke="#22d3ee"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="4"
          />
          {points.map((point, index) => (
            <circle
              key={point.record.timestamp}
              cx={point.x}
              cy={point.y}
              r={index % 3 === 0 || point === peak ? 4 : 2.5}
              fill={point === peak ? "#facc15" : "#e0f2fe"}
            />
          ))}
          <text
            x={peak.x}
            y={Math.max(peak.y - 14, 18)}
            textAnchor="middle"
            className="fill-yellow-200 text-[13px] font-semibold"
          >
            peak {peak.value.toLocaleString()}
          </text>
          <text
            x={padding}
            y={height - 8}
            className="fill-slate-300 text-[12px]"
          >
            {formatHour(records[0].timestamp)}
          </text>
          <text
            x={width - padding}
            y={height - 8}
            textAnchor="end"
            className="fill-slate-300 text-[12px]"
          >
            {formatHour(records[records.length - 1].timestamp)}
          </text>
        </svg>
      </div>
      <p className="mt-3 text-sm leading-6 text-slate-600">
        Mock total observed pedestrian activity across the selected MVP sensors.
        Missing sensor observations remain explicit in the per-hour data and
        are not treated as observed zero activity.
      </p>
    </div>
  );
}
