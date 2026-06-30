import type { Sensor } from "@/lib/types";

type SensorCardsProps = {
  sensors: Sensor[];
};

export function SensorCards({ sensors }: SensorCardsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      {sensors.map((sensor) => (
        <article
          key={sensor.sensor_id}
          className="rounded-2xl border border-slate-200 bg-slate-50 p-4"
        >
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">
                Sensor {sensor.sensor_id}
              </p>
              <h3 className="mt-2 text-lg font-semibold text-slate-950">
                {sensor.display.short_label}
              </h3>
            </div>
            <span className="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700">
              {sensor.status === "A" ? "Active" : sensor.status}
            </span>
          </div>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            {sensor.description}
          </p>
          <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
            <div>
              <dt className="text-slate-500">Precinct</dt>
              <dd className="font-medium text-slate-900">
                {sensor.display.precinct}
              </dd>
            </div>
            <div>
              <dt className="text-slate-500">Confidence</dt>
              <dd className="font-medium text-slate-900">
                {Math.round(sensor.confidence.metadata_confidence * 100)}%
              </dd>
            </div>
            <div className="col-span-2">
              <dt className="text-slate-500">Coordinates</dt>
              <dd className="font-mono text-xs text-slate-800">
                {sensor.coordinates.latitude.toFixed(5)},{" "}
                {sensor.coordinates.longitude.toFixed(5)}
              </dd>
            </div>
          </dl>
        </article>
      ))}
    </div>
  );
}
