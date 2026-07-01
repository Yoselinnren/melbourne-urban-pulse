import { getLatestRecord, getPeakRecord } from "@/lib/dashboard-data";

export function ContextPanel() {
  const latest = getLatestRecord();
  const peak = getPeakRecord();

  const items = [
    {
      label: "Peak observed hour",
      value: `${String(peak.hour).padStart(2, "0")}:00`,
      detail: peak.city_summary.dominant_context.replaceAll("_", " "),
    },
    {
      label: "Latest-hour weather",
      value: `${latest.weather.temperature_2m}°C`,
      detail: latest.weather.weather_disruption_flag
        ? "weather disruption flag on"
        : "no weather disruption flag",
    },
    {
      label: "Latest-hour calendar",
      value: latest.calendar.is_public_holiday ? "Public holiday" : "Regular day",
      detail: `${latest.calendar.season} / ${
        latest.calendar.is_weekend ? "weekend" : "weekday"
      }`,
    },
  ];

  return (
    <div className="grid gap-3 md:grid-cols-3">
      {items.map((item) => (
        <div key={item.label} className="rounded-2xl bg-slate-50 p-4">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            {item.label}
          </p>
          <p className="mt-2 text-2xl font-semibold text-slate-950">
            {item.value}
          </p>
          <p className="mt-1 text-sm capitalize text-slate-600">
            {item.detail}
          </p>
        </div>
      ))}
    </div>
  );
}
