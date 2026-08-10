import type { CSSProperties } from "react";
import type { Metadata } from "next";
import Link from "next/link";
import HeroPulseField from "@/features/narrative/HeroPulseField";
import Reveal from "@/features/narrative/Reveal";
import "./project.css";

export const metadata: Metadata = {
  title: "Melbourne Urban Pulse | Yoreny",
  description: "An inspectable research argument about the spatial-temporal form of departures from Melbourne's regular pedestrian rhythm.",
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
  return <div className="explorer-preview" aria-hidden="true"><div className="explorer-preview__head"><b>MUP</b><span>Explore</span><span>425 Pulses</span></div><div className="explorer-preview__body"><div className="explorer-preview__plane">{[18, 31, 44, 53, 66, 75, 82, 39, 59, 70, 27, 88].map((left, index) => <i key={index} style={{ left: `${left}%`, top: `${18 + ((index * 29) % 64)}%` }} />)}</div><div className="explorer-preview__aside"><b>2025 research window</b><span>12 sensors</span><span>425 Pulses</span><span>16 reviewed cases</span></div></div><div className="explorer-preview__timeline">{Array.from({ length: 30 }, (_, index) => <i key={index} style={{ left: `${2 + index * 3.25}%`, top: `${16 + ((index * 17) % 60)}%` }} />)}</div></div>;
}

export default function MelbourneUrbanPulseProject() {
  return <main className="mup-project" id="project">
    <header className="project-nav">
      <Link className="project-brand" href="/"><span>MUP</span><strong>Melbourne Urban Pulse</strong></Link>
      <nav aria-label="Project"><a href="#question">Project</a><a href="#method">Methodology</a><Link className="button button--compact" href="/explore">Open Explorer</Link></nav>
    </header>

    <section className="project-hero" aria-labelledby="project-title">
      <div className="hero-copy">
        <p className="eyebrow">RESEARCH CASE STUDY · MELBOURNE · 2025</p>
        <h1 id="project-title">The city keeps a rhythm.<br />We study where it departs.</h1>
        <p className="hero-summary">Hourly pedestrian observations are compared with each place&apos;s regular rhythm. The result is not a list of predictable holidays or events, but a set of spatial-temporal signatures—some broad, some brief, and some still unresolved.</p>
        <p className="claim-boundary">Context coincided with each Pulse; it is not presented as the cause.</p>
        <div className="hero-actions"><Link className="button" href={`/explore?pulse=${newYearPulse}`}>Explore 425 Pulses</Link><a className="text-link" href="#method">Read methodology →</a></div>
      </div>
      <HeroPulseField />
      <dl className="study-metrics"><div><dt>Representative sensors</dt><dd>12</dd></div><div><dt>Pulses in 2025</dt><dd>425</dd></div><div><dt>Reviewed cases</dt><dd>16</dd></div></dl>
      <div className="scroll-cue"><span>SCROLL TO READ THE SIGNAL</span><span>Reviewed overlap, not causal attribution</span></div>
    </section>

    <section className="chapter chapter--question" id="question">
      <Reveal><ChapterIntro label="01 · RESEARCH QUESTION" title="What changes when the expected rhythm breaks?">The useful result is not that holidays, rain, or events matter. Those conditions are foreseeable. The research asks what observable form appears: when it begins, how long it lasts, and how far it reaches across the sensor network.</ChapterIntro></Reveal>
      <Reveal className="rhythm-card"><p className="case-label">EXPECTED RHYTHM → OBSERVED DEPARTURE</p><div className="rhythm-plot"><i className="rhythm-regular" /><i className="rhythm-observed" /><span className="pulse-window">PULSE WINDOW</span></div><p>A Pulse is the bounded spatial-temporal signature—not the name of its coinciding context.</p></Reveal>
    </section>

    <section className="chapter chapter--method" id="method">
      <Reveal><ChapterIntro label="02 · METHOD IN BRIEF" title="From hourly observations to reviewed Pulses.">The pipeline separates measurement, expectation, detection, spatial grouping, and human evidence review. Each stage narrows what can be claimed.</ChapterIntro></Reveal>
      <Reveal className="method-grid">
        {[ ["01 · OBSERVE", "Hourly counts", "PLACE · TIME · COUNT"], ["02 · EXPECT", "Regular baseline", "PLACE × HOUR × DAY TYPE"], ["03 · DETECT", "Episode windows", "DIRECTION · DURATION · STRENGTH"], ["04 · GROUP + REVIEW", "Spatial Pulse", "REACH · EVIDENCE · UNCERTAINTY"] ].map(([step, title, detail], index) => <article key={step}><p>{step}</p><h3>{title}</h3><div className={`method-symbol method-symbol--${index + 1}`} aria-hidden="true" /><small>{detail}</small></article>)}
      </Reveal>
      <Reveal className="method-boundary"><strong>Reviewed evidence confirms temporal overlap. It does not isolate a cause.</strong><span>PUBLIC DATA → REPRODUCIBLE PIPELINE → MANUAL REVIEW</span></Reveal>
    </section>

    <section className="chapter chapter--case">
      <Reveal><ChapterIntro label="03 · CASE 01 / NEW YEAR" title="One date, two city rhythms.">The reviewed sequence moves from a six-hour network-wide above-baseline Pulse to a five-hour network-wide below-baseline Pulse. The result is the phase reversal—not merely that New Year is unusual.</ChapterIntro></Reveal>
      <Reveal className="case-grid"><CasePanel label="PHASE 01 · ABOVE BASELINE" title="00:00–05:00" facts="6 HOURS · 12/12 SENSORS · NETWORK-WIDE" note="Event dispersal · crowds · special transport · closures" values={[46,65,38,82,53,100,61,91,44,70,56,86]} href={`/explore?pulse=${newYearPulse}`} /><CasePanel label="PHASE 02 · BELOW BASELINE" title="06:00–10:00" facts="5 HOURS · 12/12 SENSORS · NETWORK-WIDE" note="Public holiday morning · business closure · transport transition" values={[48,66,36,84,54,98,62,92,43,72,57,87]} direction="below" href="/explore?pulse=P1F_REPRESENTATIVE_12_below_baseline_202501010600" /></Reveal>
      <Reveal className="evidence-boundary"><strong>The available context shifts across the sequence; neither phase is assigned a single cause.</strong><span>REVIEWED OVERLAP · NON-CAUSAL</span></Reveal>
    </section>

    <section className="chapter chapter--case chapter--weather">
      <Reveal><ChapterIntro label="04 · CASE 02 / WEATHER" title="Rain does not have one temporal footprint.">Both reviewed cases are wet and below baseline, yet their reach and duration differ. A weather label alone is therefore not a sufficient result.</ChapterIntro></Reveal>
      <Reveal className="case-grid"><CasePanel label="06 JAN · SHORT WET MORNING" title="07:00–09:00" facts="3 HOURS · 9 SENSORS · BELOW BASELINE" note="Rain · Australian Open qualifying · school holiday" values={[62,78,44,86,55,91,67,49,74]} direction="below" href={`/explore?pulse=${janRainPulse}`} /><CasePanel label="02 JUL · SUSTAINED WET + COLD" title="12:00–20:00" facts="9 HOURS · 11 SENSORS · BELOW BASELINE" note="Sustained wet and cold · weak later transport context" values={[60,76,43,88,54,95,68,47,79,58,84]} direction="below" href={`/explore?pulse=${julyRainPulse}`} /></Reveal>
      <Reveal className="evidence-boundary"><strong>Reviewed wet-weather cases appeared with different network reach and duration.</strong><span>TWO PURPOSELY SELECTED CASES · NO RAINFALL-RESPONSE CURVE</span></Reveal>
    </section>

    <section className="chapter chapter--case chapter--event">
      <Reveal><ChapterIntro label="05 · CASE 03 / EVENT FORM" title="Known events leave different observable forms.">Both reviewed Pulses are broad and above baseline. One is a compact early-morning signal; the other is a layered evening window. Event evidence does not make their temporal form interchangeable.</ChapterIntro></Reveal>
      <Reveal className="case-grid"><CasePanel label="MELBOURNE MARATHON · 06:00" title="Compact event Pulse" facts="1 HOUR · 9 SENSORS · ABOVE BASELINE" note="Marathon · early access · road closures · public transport" values={[96,67,82,52,88,63,75,46,72]} href={`/explore?pulse=${marathonPulse}`} /><CasePanel label="17 DEC · 18:00–01:00" title="Layered evening Pulse" facts="8 HOURS · 8 SENSORS · ABOVE BASELINE" note="RMIT graduation · two Christmas activities · partial intervals" values={[48,82,39,70,31,77,46,62]} href={`/explore?pulse=${decemberPulse}`} /></Reveal>
      <Reveal className="evidence-boundary"><strong>Event-linked reviewed Pulses can differ substantially in temporal form.</strong><span>NO ATTENDANCE-NORMALISED EFFECT · NO CAUSAL COUNTERFACTUAL</span></Reveal>
    </section>

    <section className="chapter chapter--case chapter--unresolved">
      <Reveal><ChapterIntro label="06 · CASE 04 / UNRESOLVED" title="The system must preserve what it cannot explain.">At QVM–Therry Street South, an eight-hour above-baseline episode remained local to one sensor. Manual review found no matching night event. The absence of a match is retained as uncertainty, not converted into an explanation.</ChapterIntro></Reveal>
      <Reveal className="unresolved-grid"><div className="isolated-plot"><div className="isolated-node"><i /><span>QVM–Therry St (South)</span><small>20:00–03:00 · 8 HOURS · ONE SENSOR</small></div><p>LOCALIZED ABOVE-BASELINE EPISODE</p></div><div className="evidence-review"><p className="case-label">EVIDENCE REVIEW</p><h3>No matching night event found</h3><dl><div><dt>Regular market hours</dt><dd>NO MATCH</dd></div><div><dt>Night-event search</dt><dd>NO MATCH</dd></div><div><dt>Expected direction</dt><dd>INDETERMINATE</dd></div></dl><p className="negative-search">LOW-CONFIDENCE NEGATIVE SEARCH<br /><span>Useful boundary evidence, not proof of no local cause.</span></p><Link className="text-link" href="/explore?sensor=49">Inspect the sensor →</Link></div></Reveal>
      <Reveal className="evidence-boundary"><strong>Unresolved local signals are retained instead of being forced into a city-event or weather explanation.</strong><span>UNRESOLVED · KEPT VISIBLE</span></Reveal>
    </section>

    <section className="chapter chapter--limits">
      <Reveal><ChapterIntro label="07 · LIMITATIONS + PROVENANCE" title="What this study can—and cannot—say.">Transparent boundaries are part of the result. The project describes observed signatures and reviewed overlap; it does not turn observational evidence into causal certainty.</ChapterIntro></Reveal>
      <Reveal className="limits-grid"><article><p className="case-label">SUPPORTED</p><h3>What we can describe</h3><ul><li>Direction against a regular baseline</li><li>Duration and network reach</li><li>Reviewed temporal context overlap</li><li>Signals that remain unresolved</li></ul></article><article className="not-supported"><p className="case-label">NOT SUPPORTED</p><h3>What we do not claim</h3><ul><li>A condition caused the Pulse</li><li>Annual prevalence from 16 cases</li><li>Event size or effectiveness</li><li>A generated causal explanation</li></ul></article><article><p className="case-label">PROVENANCE</p><h3>Inspect the research trail</h3><ul><li>City of Melbourne pedestrian sensors</li><li>Weather, calendar, transport and event sources</li><li>Versioned processing scripts and data contracts</li></ul><strong className="provenance-count">16 CASES · 64 REVIEWED LINKS<small>PURPOSIVE CASE SET · NOT REPRESENTATIVE</small></strong></article></Reveal>
      <a className="text-link" href="#method">Open the methodology and reproducibility notes →</a>
    </section>

    <section className="chapter chapter--explorer">
      <Reveal className="explorer-copy"><p className="eyebrow">08 · EXPLORE THE YEAR</p><h2>The cases are an argument.<br />The Explorer is the audit trail.</h2><p>Inspect all 425 Pulses across 12 representative sensors. Filters, selected Pulses, sensor participation, evidence status, and unresolved observations remain visible.</p><Link className="button" href={`/explore?pulse=${newYearPulse}`}>Open selected case</Link><small>SELECTED CASE HANDOFF → /explore?pulse=…</small></Reveal>
      <Reveal><ExplorerPreview /><p className="preview-caption">LIVE ANALYTICAL EXPERIENCE · 2025 ANNUAL VIEW</p></Reveal>
    </section>

    <section className="chapter chapter--role">
      <Reveal><p className="eyebrow">09 · RESEARCHER ROLE</p><h2>Built as an inspectable<br />research argument.</h2><p>The work combines data engineering, analytical framing, manual evidence review, information design, and an interactive Explorer for research-degree applications.</p></Reveal>
      <Reveal className="role-grid">{[["01", "Data pipeline", "Public observations → reproducible outputs"], ["02", "Analytical framing", "Baselines → episodes → spatial Pulses"], ["03", "Evidence review", "Context overlap → uncertainty retained"], ["04", "Interactive communication", "Narrative argument → annual Explorer"]].map(([number, title, detail]) => <article key={number}><span>{number}</span><h3>{title}</h3><p>{detail}</p></article>)}</Reveal>
      <footer className="portfolio-route">YORENY.COM · PERSONAL PORTFOLIO → PROJECT ENTRY → HERO + NARRATIVE → EXPLORER</footer>
    </section>
  </main>;
}
