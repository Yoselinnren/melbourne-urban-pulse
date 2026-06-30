import Link from "next/link";
import { dashboardData } from "@/lib/dashboard-data";

export default function Home() {
  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,#dff7ff,transparent_35%),linear-gradient(135deg,#f8fafc,#eef6ff_48%,#f8fafc)] text-slate-950">
      <section className="mx-auto flex min-h-screen w-full max-w-6xl flex-col justify-center px-6 py-16">
        <div className="max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-700">
            Smart infrastructure · urban signals · visual analytics
          </p>
          <h1 className="mt-6 text-5xl font-semibold tracking-tight text-slate-950 md:text-7xl">
            Melbourne Urban Pulse
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-700">
            A research-oriented data storytelling prototype that translates
            pedestrian activity, weather, calendar rhythm, and event context
            into an interpretable view of Melbourne&apos;s urban activity.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/dashboard"
              className="rounded-full bg-slate-950 px-6 py-3 text-sm font-semibold text-white transition hover:bg-cyan-800"
            >
              Open dashboard slice
            </Link>
            <a
              href="https://data.melbourne.vic.gov.au/"
              target="_blank"
              rel="noreferrer"
              className="rounded-full border border-slate-300 bg-white/70 px-6 py-3 text-sm font-semibold text-slate-800 transition hover:border-cyan-500"
            >
              Source context
            </a>
          </div>
        </div>

        <div className="mt-16 grid gap-4 md:grid-cols-3">
          {[
            ["Study period", dashboardData.study_period.display_label],
            ["MVP sensors", `${dashboardData.sensors.length} locations`],
            [
              "Current data",
              dashboardData.metadata.is_mock ? "Mock vertical slice" : "Processed data",
            ],
          ].map(([label, value]) => (
            <div
              key={label}
              className="rounded-3xl border border-white/80 bg-white/70 p-6 shadow-sm shadow-cyan-100"
            >
              <p className="text-sm font-medium text-slate-500">{label}</p>
              <p className="mt-2 text-2xl font-semibold text-slate-950">
                {value}
              </p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
