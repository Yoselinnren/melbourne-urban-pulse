import type { CSSProperties } from "react";
import type { Metadata } from "next";
import Link from "next/link";
import HeroPulseField from "@/features/narrative/HeroPulseField";
import Reveal from "@/features/narrative/Reveal";
import "./project.css";

export const metadata: Metadata = {
  title: "Melbourne Urban Pulse | Yoreny | Siyang",
  description: "An interpretable urban data study that turns 2025 hourly pedestrian counts into local departures, Episodes and cross-location Pulses, with manually reviewed context and explicit uncertainty.",
};

const newYearPulse = "P1F_REPRESENTATIVE_12_above_baseline_202501010000";
const janRainPulse = "P1F_REPRESENTATIVE_12_below_baseline_202501060700";
const julyRainPulse = "P1F_REPRESENTATIVE_12_below_baseline_202507021200";
const marathonPulse = "P1F_REPRESENTATIVE_12_above_baseline_202510120600";
const decemberPulse = "P1F_REPRESENTATIVE_12_above_baseline_202512171800";

function ChapterIntro({ label, title, children }: { label: string; title: string; children: React.ReactNode }) {
  return <header className="chapter-intro"><p className="eyebrow">{label}</p><h2>{title}</h2><p>{children}</p></header>;
}

function SignalBars({ values, direction = "above", selected = -1 }: { values: number[]; direction?: "above" | "below"; selected?: number }) {
  return <div className={`signal-bars signal-bars--${direction}`} aria-hidden="true">{values.map((value, index) => <i className={selected === index ? "selected" : ""} key={index} style={{ "--signal": `${value}%` } as CSSProperties} />)}</div>;
}

function CasePanel({ label, title, facts, note, values, direction = "above", href }: { label: string; title: string; facts: string; note: string; values: number[]; direction?: "above" | "below"; href: string }) {
  return <article className="case-panel"><p className="case-label">{label}</p><h3>{title}</h3><p className="case-facts">{facts}</p><SignalBars values={values} direction={direction} /><p className="case-note">{note}</p><Link className="text-link" href={href}>Inspect this Pulse →</Link></article>;
}

function ExplorerPreview() {
  return <div className="explorer-preview" aria-hidden="true"><div className="explorer-preview__head"><b>MUP</b><span>Explore</span><span>425 Pulses</span></div><div className="explorer-preview__body"><div className="explorer-preview__plane">{[18, 31, 44, 53, 66, 75, 82, 39, 59, 70, 27, 88].map((left, index) => <i key={index} style={{ left: `${left}%`, top: `${18 + ((index * 29) % 64)}%` }} />)}</div><div className="explorer-preview__aside"><b>2025 study network</b><span>12 research sensors</span><span>425 v1 Pulses</span><span>16 reviewed cases</span></div></div><div className="explorer-preview__timeline">{Array.from({ length: 30 }, (_, index) => <i key={index} style={{ left: `${2 + index * 3.25}%`, top: `${16 + ((index * 17) % 60)}%` }} />)}</div></div>;
}

export default function MelbourneUrbanPulseProject() {
  return <main className="mup-project" id="project">
    <header className="project-nav">
      <Link className="project-brand" href="/"><span>MUP</span><strong>Melbourne Urban Pulse</strong></Link>
      <nav aria-label="Project"><a href="#question">Project</a><Link href="/projects/melbourne-urban-pulse/methodology">Method</Link><Link className="button button--compact" href="/explore">Explore data</Link></nav>
    </header>

    <section className="project-hero" aria-labelledby="project-title">
      <div className="hero-copy">
        <p className="eyebrow">INTERPRETABLE URBAN DATA STUDY · CENTRAL MELBOURNE · 2025</p>
        <h1 id="project-title">When does a place depart<br />{" "}from its usual rhythm?</h1>
        <p className="hero-summary">This project compares 2025 hourly pedestrian counts from 12 purposively selected central-Melbourne sensors with each location&apos;s own weekday–hour baseline. Strong consecutive departures become Episodes; same-direction co-occurrence across at least three sensors becomes a Pulse. Under the v1 definitions, the workflow produced 425 Pulses, with 16 cases selected for manual evidence review.</p>
        <p className="claim-boundary">Reviewed context records overlap with a signal; it does not establish its cause.</p>
        <div className="hero-actions"><Link className="button" href={`/explore?pulse=${newYearPulse}`}>Explore the 2025 Pulses</Link><Link className="text-link" href="/projects/melbourne-urban-pulse/methodology">Read the full method →</Link></div>
      </div>
      <HeroPulseField />
      <dl className="study-metrics"><div><dt>Central-city research sensors</dt><dd>12</dd></div><div><dt>Pulses under v1 rules</dt><dd>425</dd></div><div><dt>Manually reviewed cases</dt><dd>16</dd></div></dl>
      <div className="scroll-cue"><span>SCROLL TO FOLLOW THE STUDY</span><span>Detection first · context reviewed afterwards</span></div>
    </section>

    <section className="chapter chapter--question" id="question">
      <Reveal><ChapterIntro label="01 · RESEARCH QUESTION" title="When does a place depart from its own usual rhythm?">A pedestrian count has little meaning without a local reference. The same value may be ordinary at one place and unusual at another, or ordinary on a weekday morning and unusual late at night. This study asks how far an hourly observation departs from the usual distribution for the same sensor, weekday and hour; how long that departure persists; and whether the same direction appears across several research locations.</ChapterIntro></Reveal>
      <Reveal className="rhythm-card"><p className="case-label">LOCAL BASELINE → HOURLY DEPARTURE → EPISODE → PULSE</p><div className="rhythm-plot"><i className="rhythm-regular" /><i className="rhythm-observed" /><span className="pulse-window">PULSE WINDOW</span></div><p>A Pulse is a rule-defined period in which at least three research sensors show strong departures in the same direction during every included hour. It describes temporal co-occurrence across geolocated sensors; the v1 grouping does not use distance or spatial adjacency.</p></Reveal>
    </section>

    <section className="chapter chapter--method" id="method">
      <Reveal><ChapterIntro label="02 · METHOD IN BRIEF" title="From hourly observations to reviewed Pulses.">The workflow keeps measurement, baseline construction, deviation detection, cross-location grouping and evidence review separate. The rules remain visible so that each result can be traced back to the observations and decisions that produced it.</ChapterIntro></Reveal>
      <Reveal className="method-grid">
        {[ ["01 · OBSERVE", "Hourly counts", "SENSOR · LOCAL TIME · COUNT · MISSINGNESS"], ["02 · BASELINE", "Local reference", "SENSOR × WEEKDAY × HOUR · MEDIAN · RAW MAD"], ["03 · DETECT", "Consecutive departures", "HIGH-CONFIDENCE BASELINE · |SCORE| ≥ 3 · SAME DIRECTION"], ["04 · GROUP + REVIEW", "Cross-location Pulse", "≥3 SENSORS PER HOUR · CONTEXT REVIEWED AFTER DETECTION"] ].map(([step, title, detail], index) => <article key={step}><p>{step}</p><h3>{title}</h3><div className={`method-symbol method-symbol--${index + 1}`} aria-hidden="true" /><small>{detail}</small></article>)}
      </Reveal>
      <Reveal className="method-boundary"><strong>The score is the observed count minus the local baseline median, divided by the raw MAD. It is a relative deviation measure, not a probability.</strong><Link className="text-link" href="/projects/melbourne-urban-pulse/methodology">Read the full methodology →</Link></Reveal>
    </section>

    <section className="chapter chapter--case">
      <Reveal><ChapterIntro label="03 · CASE 01 / NEW YEAR" title="One date, two directions.">Across the selected research network, a six-hour above-baseline Pulse from 00:00 to 05:00 was followed by a five-hour below-baseline Pulse from 06:00 to 10:00. The hourly number of participating sensors changed throughout both periods; the result is a direction change with an evolving participation pattern.</ChapterIntro></Reveal>
      <Reveal className="case-grid"><CasePanel label="PHASE 1 · ABOVE BASELINE" title="00:00–05:00" facts="6 HOURS · 9–12 ACTIVE SENSORS PER HOUR · 12 INVOLVED · NETWORK-WIDE AT PEAK" note="Reviewed context: New Year events, early-morning crowds, extended public transport and road closures" values={[46,65,38,82,53,100,61,91,44,70,56,86]} href={`/explore?pulse=${newYearPulse}`} /><CasePanel label="PHASE 2 · BELOW BASELINE" title="06:00–10:00" facts="5 HOURS · 7–12 ACTIVE SENSORS PER HOUR · 12 INVOLVED · NETWORK-WIDE AT PEAK" note="Reviewed context: public-holiday morning, business closures and the end of overnight transport changes" values={[48,66,36,84,54,98,62,92,43,72,57,87]} direction="below" href="/explore?pulse=P1F_REPRESENTATIVE_12_below_baseline_202501010600" /></Reveal>
      <Reveal className="evidence-boundary"><strong>The reviewed sources overlap different parts of the sequence. They help describe its context but do not identify one cause for either phase.</strong></Reveal>
    </section>

    <section className="chapter chapter--case chapter--weather">
      <Reveal><ChapterIntro label="04 · CASE 02 / WET WEATHER" title="Two wet periods, two temporal structures.">Both selected Pulses are below baseline and overlap recorded rain. One lasts three morning hours; the other continues for nine hours from midday. The comparison describes different durations and participation patterns within two purposively selected cases. It does not estimate a general rainfall response.</ChapterIntro></Reveal>
      <Reveal className="case-grid"><CasePanel label="6 JAN · WET MORNING" title="07:00–09:00" facts="3 HOURS · 6–9 ACTIVE SENSORS PER HOUR · 10 INVOLVED" note="3.6 mm rain across 3 hours · school holiday · Australian Open qualifying in the wider context" values={[62,78,44,86,55,91,67,49,74]} direction="below" href={`/explore?pulse=${janRainPulse}`} /><CasePanel label="2 JUL · SUSTAINED WET PERIOD" title="12:00–20:00" facts="9 HOURS · 3–11 ACTIVE SENSORS PER HOUR · 12 INVOLVED" note="10.4 mm rain across 8 rainy hours · cold conditions · limited later transport context" values={[60,76,43,88,54,95,68,47,79,58,84]} direction="below" href={`/explore?pulse=${julyRainPulse}`} /></Reveal>
      <Reveal className="evidence-boundary"><strong>The two reviewed wet-weather cases differ in duration and hourly sensor participation. Because they were selected for comparison and other conditions were not controlled, the study treats this as a descriptive contrast rather than a causal weather effect.</strong></Reveal>
    </section>

    <section className="chapter chapter--case chapter--event">
      <Reveal><ChapterIntro label="05 · CASE 03 / ACTIVITY CONTEXT" title="Event-overlapping signals do not share one form.">The selected Melbourne Marathon Pulse is concentrated in one early-morning hour. The 17 December case extends across eight evening and overnight hours. Both are above baseline and overlap documented activities, but their durations and participation structures differ.</ChapterIntro></Reveal>
      <Reveal className="case-grid"><CasePanel label="MELBOURNE MARATHON · 06:00" title="One-hour Pulse" facts="1 HOUR · 9 ACTIVE SENSORS · 9 INVOLVED · ABOVE BASELINE" note="Reviewed context: marathon access, road closures and public-transport arrangements" values={[96,67,82,52,88,63,75,46,72]} href={`/explore?pulse=${marathonPulse}`} /><CasePanel label="17 DEC · 18:00–01:00" title="Eight-hour evening Pulse" facts="8 HOURS · 3–8 ACTIVE SENSORS PER HOUR · 10 INVOLVED · ABOVE BASELINE" note="Reviewed context: RMIT graduation and two Christmas activities with partial time overlap" values={[48,82,39,70,31,77,46,62]} href={`/explore?pulse=${decemberPulse}`} /></Reveal>
      <Reveal className="evidence-boundary"><strong>Within this purposively selected case pair, documented activity context overlaps two substantially different temporal forms. The comparison does not estimate attendance-normalised effects or event causation.</strong></Reveal>
    </section>

    <section className="chapter chapter--case chapter--unresolved">
      <Reveal><ChapterIntro label="06 · CASE 04 / UNRESOLVED" title="A detected signal can remain unexplained.">An eight-hour above-baseline Episode at QVM–Therry Street South remained confined to one sensor. No matching night event was identified within the reviewed sources. The result is retained as unresolved because source coverage cannot prove that no local circumstance occurred.</ChapterIntro></Reveal>
      <Reveal className="unresolved-grid"><div className="isolated-plot"><div className="isolated-node"><i /><span>QVM–Therry St (South)</span><small>20:00–03:00 · 8 HOURS · ONE SENSOR</small></div><p>ISOLATED ABOVE-BASELINE EPISODE</p></div><div className="evidence-review"><p className="case-label">EVIDENCE REVIEW</p><h3>No matching night event identified in reviewed sources</h3><dl><div><dt>Regular market hours</dt><dd>NO TEMPORAL MATCH</dd></div><div><dt>Night-event search</dt><dd>NO MATCHING SOURCE IDENTIFIED</dd></div><div><dt>Direction assessment</dt><dd>INDETERMINATE</dd></div></dl><p className="negative-search">LIMITED NEGATIVE SEARCH<br />{" "}<span>Not evidence that no local circumstance occurred.</span></p><Link className="text-link" href="/explore?sensor=49">Inspect the sensor →</Link></div></Reveal>
      <Reveal className="evidence-boundary"><strong>Unresolved signals remain visible so that a missing explanation is not replaced by an invented one.</strong></Reveal>
    </section>

    <section className="chapter chapter--limits">
      <Reveal><ChapterIntro label="07 · CURRENT SCOPE + FURTHER STUDY" title="What the v1 framework establishes.">The current study provides a reproducible result for a defined 2025 sensor network and transparent rule set. Its boundaries describe how the findings should be read and where later research could add resolution.</ChapterIntro></Reveal>
      <Reveal className="limits-grid"><article><p className="case-label">ESTABLISHED IN V1</p><h3>What can be inspected</h3><ul><li>Direction relative to each local weekday–hour baseline</li><li>Duration and hourly sensor participation</li><li>Cross-location co-occurrence under explicit thresholds</li><li>Manually reviewed context overlap and unresolved cases</li></ul></article><article className="not-supported"><p className="case-label">INTERPRETATION BOUNDARY</p><h3>How to read the results</h3><ul><li>A central-city study network, not a city-wide statistical sample</li><li>Peak participation categories, not spatial clustering</li><li>Purposefully selected cases, not a representative sample of all Pulses</li><li>Context overlap, not an estimate of causal effect</li></ul></article><article><p className="case-label">FURTHER STUDY</p><h3>Ways to add resolution</h3><ul><li>Season- and event-aware baselines</li><li>Distance-, precinct- or topology-aware grouping</li><li>Threshold calibration with annotated or held-out data</li><li>Larger sensor networks and causal study designs</li></ul><strong className="provenance-count">16 CASES · 64 REVIEWED RECORDS<small>PURPOSIVE CASE SET</small></strong></article></Reveal>
      <Link className="text-link" href="/projects/melbourne-urban-pulse/methodology">Read methods, sources and reproducibility notes →</Link>
    </section>

    <section className="chapter chapter--explorer">
      <Reveal className="explorer-copy"><p className="eyebrow">08 · EXPLORE THE 2025 RESULTS</p><h2>Inspect the complete<br />{" "}Pulse set.</h2><p>The case studies show selected contrasts. The Explorer exposes all 425 v1 Pulses across the 12 research sensors, including filters, direction, scope, hourly participation, evidence status and sensor-level context.</p><Link className="button" href={`/explore?pulse=${newYearPulse}`}>Open the New Year case</Link></Reveal>
      <Reveal><ExplorerPreview /><p className="preview-caption">INTERACTIVE 2025 RESULT EXPLORER</p></Reveal>
    </section>

    <section className="chapter chapter--role">
      <Reveal><p className="eyebrow">09 · RESEARCH PROCESS</p><h2>Human-directed research,<br />{" "}developed with AI assistance.</h2><p>I defined the research topic, designed the project and interaction architecture, directed each stage of development, and reviewed outputs against my intended research and visual direction. AI tools assisted with analytical implementation, code, source discovery, documentation and testing. The published results come from deterministic scripts and explicit rules rather than an AI prediction model.</p></Reveal>
      <Reveal className="role-grid">{[["01", "Research direction + design", "Topic, project architecture, interaction design and final direction · author-led"], ["02", "Analytical + software implementation", "Methods, data processing and interface development · AI-assisted, author-directed"], ["03", "Evidence review", "Public-source review, case interpretation and uncertainty decisions · author-directed"], ["04", "Verification + editorial control", "Automated consistency tests, iterative review and final approval"]].map(([number, title, detail]) => <article key={number}><span>{number}</span><h3>{title}</h3><p>{detail}</p></article>)}</Reveal>
      <p className="evidence-boundary">AI supported the research process; it was not the analytical model and did not independently determine causal explanations.</p>
    </section>
  </main>;
}
