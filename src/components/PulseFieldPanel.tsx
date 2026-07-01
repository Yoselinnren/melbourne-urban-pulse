import { getSensorById } from "@/lib/dashboard-data";
import type { PulseField } from "@/lib/types";

type PulseFieldPanelProps = {
  pulseField: PulseField;
};

export function PulseFieldPanel({ pulseField }: PulseFieldPanelProps) {
  const frame = pulseField.frames[1] ?? pulseField.frames[0];

  return (
    <div>
      <div className="relative overflow-hidden rounded-3xl border border-slate-800 bg-slate-950 p-6 text-white">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(34,211,238,0.18),transparent_30%),radial-gradient(circle_at_70%_60%,rgba(250,204,21,0.12),transparent_28%)]" />
        <div className="relative">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-200">
                Placeholder field
              </p>
              <h3 className="mt-2 text-2xl font-semibold">
                2.5D Urban Pulse Field
              </h3>
            </div>
            <span className="rounded-full border border-white/20 px-3 py-1 text-sm text-slate-200">
              {pulseField.rendering_strategy.replaceAll("_", " ")}
            </span>
          </div>

          <div className="mt-8 grid h-80 grid-cols-3 items-end gap-5 border-b border-l border-cyan-100/20 px-6 pb-8">
            {frame.points.map((point) => {
              const sensor = getSensorById(point.sensor_id);
              const height = Math.max((point.height ?? 0.12) * 100, 10);
              const opacity = Math.max(point.confidence_score, 0.18);

              return (
                <div key={point.sensor_id} className="flex h-full flex-col justify-end">
                  <div className="flex flex-1 items-end justify-center">
                    <div className="relative flex items-end justify-center">
                      <span
                        className="absolute bottom-0 rounded-full border border-cyan-200/30"
                        style={{
                          width: `${64 + (point.ripple_radius ?? 0.2) * 80}px`,
                          height: `${24 + (point.ripple_radius ?? 0.2) * 30}px`,
                          opacity,
                        }}
                      />
                      <span
                        className="w-10 rounded-t-full bg-gradient-to-t from-cyan-500 to-yellow-200 shadow-lg shadow-cyan-400/30"
                        style={{ height: `${height}%`, opacity }}
                      />
                    </div>
                  </div>
                  <div className="mt-4 text-center">
                    <p className="text-sm font-semibold">
                      {sensor?.display.short_label ?? point.sensor_id}
                    </p>
                    <p className="text-xs text-slate-300">
                      pulse {point.height ?? "missing"} · conf{" "}
                      {Math.round(point.confidence_score * 100)}%
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
      <p className="mt-3 text-sm leading-6 text-slate-600">
        This is a CSS placeholder using provisional `pulse_field` frames. It
        encodes spike height as pulse score, ripple size as activity, and
        opacity as confidence. No WebGL or spatial interpolation is implemented
        yet.
      </p>
    </div>
  );
}
