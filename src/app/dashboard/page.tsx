import Link from "next/link";
import { ActivityTrend } from "@/components/ActivityTrend";
import { ContextPanel } from "@/components/ContextPanel";
import { ExplanationCards } from "@/components/ExplanationCards";
import { PulseFieldPanel } from "@/components/PulseFieldPanel";
import { SectionCard } from "@/components/SectionCard";
import { SensorCards } from "@/components/SensorCards";
import { dashboardData } from "@/lib/dashboard-data";

export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-slate-100 text-slate-950">
      <div className="mx-auto w-full max-w-7xl px-6 py-8">
        <header className="rounded-[2rem] bg-slate-950 p-8 text-white shadow-xl shadow-slate-300">
          <div className="flex flex-wrap items-start justify-between gap-6">
            <div className="max-w-3xl">
              <Link
                href="/"
                className="text-sm font-medium text-cyan-200 hover:text-white"
              >
                ← Landing
              </Link>
              <p className="mt-8 text-xs font-semibold uppercase tracking-[0.28em] text-cyan-200">
                Frontend vertical slice
              </p>
              <h1 className="mt-3 text-4xl font-semibold tracking-tight md:text-5xl">
                {dashboardData.metadata.project}
              </h1>
              <p className="mt-4 max-w-2xl text-base leading-7 text-slate-300">
                {dashboardData.metadata.description}
              </p>
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/10 p-5">
              <p className="text-sm text-slate-300">Study period</p>
              <p className="mt-2 text-2xl font-semibold">
                {dashboardData.study_period.display_label}
              </p>
              <p className="mt-2 max-w-xs text-sm leading-6 text-slate-300">
                {dashboardData.study_period.selected_reason}
              </p>
            </div>
          </div>
        </header>

        <div className="mt-6 grid gap-6">
          <SectionCard eyebrow="Metadata" title="Dataset status">
            <div className="grid gap-4 md:grid-cols-4">
              {[
                ["Schema", dashboardData.schema_version],
                ["Timezone", dashboardData.metadata.timezone],
                ["Sensors", dashboardData.sensors.length],
                [
                  "Hourly records",
                  dashboardData.hourly_records.length.toString(),
                ],
              ].map(([label, value]) => (
                <div key={label} className="rounded-2xl bg-slate-50 p-4">
                  <p className="text-sm text-slate-500">{label}</p>
                  <p className="mt-2 text-lg font-semibold text-slate-950">
                    {value}
                  </p>
                </div>
              ))}
            </div>
          </SectionCard>

          <SectionCard eyebrow="Sensors" title="Selected MVP locations">
            <SensorCards sensors={dashboardData.sensors} />
          </SectionCard>

          <div className="grid gap-6 lg:grid-cols-[1.35fr_0.85fr]">
            <SectionCard eyebrow="Activity" title="24-hour mock activity trend">
              <ActivityTrend records={dashboardData.hourly_records} />
            </SectionCard>
            <SectionCard eyebrow="Context" title="Weather and calendar">
              <ContextPanel />
              <div className="mt-4 rounded-2xl bg-cyan-50 p-4 text-sm leading-6 text-slate-700">
                Weather fields come from the mock Open-Meteo-shaped context.
                Calendar flags show New Year&apos;s Day as a public holiday in
                the example slice.
              </div>
            </SectionCard>
          </div>

          <SectionCard eyebrow="Pulse field" title="2.5D visual placeholder">
            <PulseFieldPanel pulseField={dashboardData.pulse_field} />
          </SectionCard>

          <SectionCard eyebrow="Interpretation" title="Explanation cards">
            <ExplanationCards cards={dashboardData.explanation_cards} />
          </SectionCard>

          <SectionCard eyebrow="Provenance" title="Source roles">
            <div className="grid gap-3 md:grid-cols-2">
              {dashboardData.provenance.sources.map((source) => (
                <div key={source.source_id} className="rounded-2xl bg-slate-50 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-semibold text-slate-950">
                      {source.source_id}
                    </p>
                    <span
                      className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                        source.used_in_mvp
                          ? "bg-emerald-100 text-emerald-700"
                          : "bg-slate-200 text-slate-600"
                      }`}
                    >
                      {source.used_in_mvp ? "MVP" : "Auxiliary"}
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-slate-600">
                    {source.field_role}
                  </p>
                </div>
              ))}
            </div>
          </SectionCard>
        </div>
      </div>
    </main>
  );
}
