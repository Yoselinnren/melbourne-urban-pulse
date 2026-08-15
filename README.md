# Melbourne Urban Pulse

Melbourne Urban Pulse is an interpretable urban data study and interactive research project built from 2025 public pedestrian sensor observations in central Melbourne.

The workflow compares hourly counts with sensor-specific weekday–hour baselines, groups strong consecutive departures into Episodes, and identifies same-direction co-occurrence across at least three research sensors as Pulses. Under the v1 definitions, it produced 425 Pulses and a purposive set of 16 manually reviewed cases.

The released website is available at [www.yoreny.com](https://www.yoreny.com). The [release review](docs/milestone-8-review.md) records the acceptance evidence, and the [roadmap](docs/roadmap.md) records the completed delivery and final critical review.

## Research Question

How can hourly pedestrian sensor counts be transformed into a transparent, reproducible and manually reviewable framework for departures from usual local urban rhythm?

The study asks:

- when an observation departs strongly from the usual distribution for the same sensor, weekday and hour;
- how long that departure persists;
- whether the same direction appears across several research locations;
- how sensor participation changes hour by hour;
- which documented circumstances overlap with a signal and which signals remain unresolved.

## What the v1 Workflow Does

```text
hourly observations
→ sensor × weekday × hour baselines
→ signed deviation / raw MAD
→ consecutive same-direction Episodes
→ cross-location Pulses with at least three active sensors per hour
→ manual evidence review
→ narrative case study + annual Explorer
```

The workflow is deterministic and rule-based. It is not a machine-learning prediction model, a causal model or an automatic event-explanation system.

## Published Results

- 12 purposively selected central-Melbourne research sensors with near-complete 2025 coverage;
- 105,120 sensor-hours, including 105,104 observations and 16 explicit missing values;
- 2,016 sensor–weekday–hour baseline groups;
- 4,647 rule-defined candidate Episodes;
- 425 Pulses under the published v1 scope, baseline and threshold definitions;
- 256 above-baseline and 169 below-baseline Pulses;
- 16 purposively selected cases and 64 manually reviewed evidence records;
- 15 reviewed Pulses plus one reviewed isolated Episode.

The number 425 is a reproducible result of the v1 definitions, not a count of verified city events. Reviewed context records overlap with a signal; they do not establish its cause.

## Sensor and Interpretation Scope

The 12 sensors form a compact central-city research network selected for coverage and inspectability. They are not a statistically representative sample of metropolitan Melbourne.

Pulse scope uses peak simultaneous sensor participation:

- `localized`: peak of 3–4 sensors;
- `broad`: peak of 5–7 sensors;
- `network_wide`: peak of 8–12 sensors.

The grouping detects temporal co-occurrence across geolocated sensors. It does not currently use distance, precinct adjacency, road topology or spatial clustering.

## Data Sources

Current local raw data includes:

- City of Melbourne hourly pedestrian counts
- City of Melbourne pedestrian sensor locations
- Open-Meteo historical hourly weather
- Victorian Government important dates
- City activities and planned works data
- Melbourne events calendar PDF

Raw data is intentionally excluded from Git.

## Processing Pipeline

The versioned Python stages cover:

1. source profiling and sensor selection;
2. hourly panel construction and context classification;
3. local baseline construction and observation scoring;
4. deviation interpretation and Episode construction;
5. cross-location Pulse grouping and context enrichment;
6. evidence matching, manual review and explanation-ready outputs;
7. browser-safe UI data generation and validation.

Detailed stage records are linked from [the roadmap](docs/roadmap.md) and [the analytical framework](docs/analytical-framework.md).

## Website Routes

- `/projects/melbourne-urban-pulse` — research question, selected cases, current scope and project process;
- `/projects/melbourne-urban-pulse/methodology` — plain-language long-form methodology, formulas, sensitivity and worked example;
- `/explore` — complete 2025 Pulse set, sensor locations, filters, context and reviewed evidence.

## Research Process and AI Assistance

I defined the research topic, designed the project and interaction architecture, directed each stage of development, and reviewed outputs against my intended research and visual direction.

AI tools assisted with analytical implementation, code, source discovery, documentation and testing. The published results come from deterministic scripts and explicit rules rather than an AI prediction model. AI supported the research process; it did not independently determine causal explanations.

## Current Scope and Further Study

The v1 framework is complete for its defined research question. Later studies could add resolution through:

- season- and event-aware baselines;
- distance-, precinct- or topology-aware grouping;
- threshold calibration with annotated or held-out data;
- larger or differently sampled sensor networks;
- timezone-aware handling of repeated daylight-saving hours;
- independent causal study designs.

## Tech Stack

- Next.js
- React
- TypeScript
- pnpm
- Python
- pandas / NumPy

## Project Structure

```text
data/
  raw/          local raw datasets, ignored by Git
  processed/    generated processed datasets, ignored by Git by default
  manual/       manually curated annotations
  metadata/     source catalog and provenance notes
docs/
  data-model.md
  methodology.md
  project-audit.zh-CN.md
  project-positioning.zh-CN.md
  design-rationale.md
pulse obsidian/
  original project planning notes
src/
  app/          Next.js app router source
```

## Development

Install frontend dependencies:

```bash
pnpm install
```

Run the development server:

```bash
pnpm dev
```

Run linting:

```bash
pnpm lint
```

Build the frontend:

```bash
pnpm build
```

Use the project Python environment for data work:

```powershell
.\.venv\Scripts\python.exe
```

On this workstation, bare `python` may resolve to MSYS2. Create or repair `.venv` with the explicit standard CPython executable first.

Validate the published UI data:

```powershell
.\.venv\Scripts\python.exe scripts/validate_ui_data.py --input-dir public/data/ui/v1
```

## Documentation

- [Project context](PROJECT_CONTEXT.md)
- [Active roadmap](docs/roadmap.md)
- [Result framing](docs/result-framing.md)
- [Full-site design and motion audit](docs/milestone-6-audit.md)
- [Data model](docs/data-model.md)
- [Methodology](docs/methodology.md)
- [Chinese project audit](docs/project-audit.zh-CN.md)
- [Approved Chinese positioning](docs/project-positioning.zh-CN.md)
- [Approved bilingual content architecture](docs/content-architecture.zh-CN.md)
- [Design rationale](docs/design-rationale.md)
