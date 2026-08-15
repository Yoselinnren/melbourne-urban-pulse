import type { Metadata } from "next";
import { readFile } from "node:fs/promises";
import path from "node:path";
import Link from "next/link";
import "../project.css";
import "./methodology.css";

export const dynamic = "force-static";
export const metadata: Metadata = {
  title: "Methodology | Melbourne Urban Pulse",
  description: "A plain-language account of how hourly pedestrian observations become local baselines, Episodes, cross-location Pulses and manually reviewed cases.",
};

type MethodSection = { number: number; title: string; paragraphs: string[] };

function publicCopy(source: string) {
  return source
    .replaceAll("representative sensors", "research sensors")
    .replaceAll("Representative sensors", "Research sensors")
    .replaceAll("spatial Pulse", "cross-location Pulse")
    .replaceAll("spatial Pulses", "cross-location Pulses");
}

function parseSections(source: string): MethodSection[] {
  const text = publicCopy(source).replaceAll("\r\n", "\n");
  const headings = [...text.matchAll(/^(\d+)\. (.+)$/gm)];
  const sections = headings.map((heading, index) => ({
    number: Number(heading[1]),
    title: heading[2].trim(),
    paragraphs: text.slice((heading.index ?? 0) + heading[0].length, headings[index + 1]?.index ?? text.length).trim().split(/\n\s*\n/).map((paragraph) => paragraph.replaceAll("\n", " ").trim()).filter(Boolean),
  }));
  const conclusions = sections.find((section) => section.number === 11);
  if (conclusions) {
    const start = conclusions.paragraphs.findIndex((paragraph) => paragraph.startsWith("Several other extensions follow"));
    const end = conclusions.paragraphs.findIndex((paragraph) => paragraph.startsWith("These are best understood"));
    if (start >= 0 && end >= start) {
      const future = conclusions.paragraphs.splice(start, end - start + 1);
      sections.push({ number: 12, title: "Current Scope and Opportunities for Further Study", paragraphs: future });
    }
  }
  return sections.sort((a, b) => a.number - b.number);
}

function Paragraph({ text }: { text: string }) {
  const formula = text.length < 180 && (text.includes(" = ") || text === "rain > 0" || text.startsWith("wind_speed_10m"));
  return formula ? <pre className="method-formula">{text}</pre> : <p>{text}</p>;
}

export default async function MethodologyPage() {
  const source = await readFile(path.join(process.cwd(), "docs", "review-input", "methodology-notes.zh-CN.txt"), "utf8");
  const sections = parseSections(source);
  const toc = [...sections, { number: 13, title: "Research Process and AI Assistance", paragraphs: [] }, { number: 14, title: "Reproduce and Inspect", paragraphs: [] }];

  return <main className="mup-project methodology-page">
    <header className="project-nav">
      <Link className="project-brand" href="/projects/melbourne-urban-pulse"><span>MUP</span><strong>Melbourne Urban Pulse</strong></Link>
      <nav aria-label="Methodology"><Link href="/projects/melbourne-urban-pulse">Project</Link><span aria-current="page">Method</span><Link className="button button--compact" href="/explore">Explore data</Link></nav>
    </header>

    <section className="method-hero">
      <p className="eyebrow">METHODOLOGY</p>
      <h1>From hourly footfall to<br />{" "}interpretable urban Pulses.</h1>
      <p>A plain-language account of how 2025 pedestrian observations become local baselines, strong departures, sensor Episodes, cross-location Pulses and manually reviewed cases.</p>
      <div className="method-hero__facts"><span>12 research sensors</span><span>105,120 sensor-hours</span><span>425 v1 Pulses</span><span>16 reviewed cases</span></div>
    </section>

    <div className="method-layout">
      <aside className="method-toc" aria-label="Methodology contents">
        <p className="eyebrow">CONTENTS</p>
        <ol>{toc.map((section) => <li key={section.number}><a href={`#method-${section.number}`}><span>{String(section.number).padStart(2, "0")}</span>{section.title}</a></li>)}</ol>
      </aside>

      <article className="method-article">
        <section className="method-reading-guide" aria-labelledby="reading-guide-title">
          <p className="eyebrow">READING GUIDE</p>
          <h2 id="reading-guide-title">Three kinds of information remain separate.</h2>
          <div><p><b>Observed</b>Hourly counts, timestamps, sensor locations and missing values.</p><p><b>Derived</b>Baselines, scores, Episodes and Pulses produced by explicit rules.</p><p><b>Manually reviewed</b>Public context sources, overlap decisions and unresolved evidence.</p></div>
        </section>

        <div className="method-chain" aria-label="Analysis sequence"><span>Hourly observations</span><i>→</i><span>Local baseline</span><i>→</i><span>Departure score</span><i>→</i><span>Episode</span><i>→</i><span>Cross-location Pulse</span><i>→</i><span>Evidence review</span></div>

        {sections.map((section) => <section className="method-section" id={`method-${section.number}`} key={section.number}>
          <header><span>{String(section.number).padStart(2, "0")}</span><h2>{section.title}</h2></header>
          {section.paragraphs.map((paragraph, index) => <Paragraph text={paragraph} key={`${section.number}-${index}`} />)}
          {section.number === 8 && <SensitivityTables />}
        </section>)}

        <section className="method-section" id="method-13">
          <header><span>13</span><h2>Research Process and AI Assistance</h2></header>
          <p>I defined the research topic, designed the project and interaction architecture, directed each stage of development, and reviewed outputs against my intended research and visual direction.</p>
          <p>AI tools assisted me with analytical implementation, code, source discovery, documentation and testing. I directed the public-source review, case interpretation and uncertainty decisions. Automated validators checked whether generated outputs followed the stated rules.</p>
          <p>The published results come from deterministic scripts and explicit thresholds rather than an AI prediction model. AI supported the research process; it did not independently determine causal explanations.</p>
        </section>

        <section className="method-section" id="method-14">
          <header><span>14</span><h2>Reproduce and Inspect</h2></header>
          <p>The repository keeps the processing stages, data contracts, review records and interface separate so that the published result can be traced and rebuilt. Raw source data remains outside Git where licensing, size or local-processing requirements apply.</p>
          <pre className="method-formula">pnpm lint{"\n"}pnpm build{"\n"}.venv\Scripts\python.exe scripts/validate_ui_data.py --input-dir public/data/ui/v1</pre>
          <div className="method-actions"><Link className="button" href="/projects/melbourne-urban-pulse">Return to the project</Link><Link className="button" href="/explore">Inspect the 2025 Pulses</Link><a className="text-link" href="https://github.com/Yoselinnren/melbourne-urban-pulse">View source and reproducibility notes ↗</a></div>
        </section>
      </article>
    </div>
  </main>;
}

function SensitivityTables() {
  return <div className="sensitivity-grid">
    <figure><figcaption>Minimum simultaneous sensors</figcaption><table><thead><tr><th>Minimum</th><th>Qualifying hours</th><th>Groups</th></tr></thead><tbody>{[[2,1625,774],[3,918,425],[4,585,266],[6,280,121],[8,145,61]].map((row) => <tr key={row[0]}>{row.map((value) => <td key={value}>{value.toLocaleString()}</td>)}</tr>)}</tbody></table><p>The published v1 uses a minimum of three sensors.</p></figure>
    <figure><figcaption>Hourly score threshold</figcaption><table><thead><tr><th>Threshold</th><th>Sensor-hours</th><th>Share</th></tr></thead><tbody>{[["|score| ≥ 2","18,246","17.36%"],["|score| ≥ 3","8,089","7.70%"],["|score| ≥ 4","4,273","4.07%"],["|score| ≥ 5","2,633","2.51%"]].map((row) => <tr key={row[0]}>{row.map((value) => <td key={value}>{value}</td>)}</tr>)}</tbody></table><p>The published v1 uses |score| ≥ 3 with high baseline sample sufficiency.</p></figure>
  </div>;
}
