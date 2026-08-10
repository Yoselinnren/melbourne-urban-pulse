# Melbourne Urban Pulse

> Current direction: an English-language research portfolio project for research-degree applications. See the [active roadmap](docs/roadmap.md) for the source-of-truth project state.

Melbourne Urban Pulse is an English-language research case-study website and visual analytics prototype for smart infrastructure research.

The project asks how known urban conditions manifest differently across Melbourne's pedestrian sensor network, where observed activity departs from expected city rhythm, and how those differences can be communicated without turning evidence overlap into causation.

This is not intended to be a simple pedestrian-count dashboard. Pedestrian activity is the first implemented signal because the City of Melbourne provides public, structured, spatially located sensor data. The longer-term goal is to design an extensible urban signal interpretation system that can later support vehicle flow, cycling, public transport activity, environmental context, planned works, events, and future edge-generated sensing outputs.

## Research Positioning

The project sits at the intersection of:

- Smart infrastructure
- Urban computing
- Human-computer interaction for complex systems
- Data visualisation and visual analytics
- Lightweight urban data engineering
- Edge-AI-ready urban sensing interfaces

The current version does not claim to perform real edge AI inference. Instead, it builds the interpretation and visualisation layer that could later receive edge-generated urban sensing signals.

## Core Idea

Melbourne Urban Pulse treats the city as a layered signal system:

1. **Mobility Pulse** — observed movement, starting with pedestrian flow.
2. **Environmental Context** — weather and comfort conditions.
3. **Calendar Rhythm** — weekdays, weekends, holidays, seasons, and institutional rhythms.
4. **Event and Disruption Layer** — events, planned works, road closures, and manually reviewed anomalies.
5. **Evidence and Uncertainty Interpretation** — baseline deviation, anomaly strength, reviewed overlap, confidence, and unresolved context.

The key visual concept is a **2.5D Urban Pulse Field** that begins as a data-driven Hero and resolves into the analytical Explorer. Sensor locations are shown on a simplified city plane, with restrained height, glow, ripple, and transition effects encoding observed signals.

## Current Status

Completed:

- reproducible analytical phases from source profiling through explanation-ready aggregation;
- a 12-sensor representative study with 105,104 observed sensor-hours and 16 explicit missing observations;
- 4,647 candidate episodes and 425 cross-sensor Pulses;
- weather, calendar, DST, evidence, and provenance context;
- 64 evidence facts and 64 automatic matches;
- deterministic browser-safe UI data with independent validation;
- an approved, responsive annual Explorer with spatial, temporal, filtering, Pulse, and sensor views;
- Explorer lint, production-build, UI-data, accessibility-baseline, browser, and physical-display checks;
- 64 reviewed evidence matches covering 15 Pulses and one isolated episode.

Not yet completed:

- research-result framing and selected-case narrative;
- the complete Hero, narrative homepage, methodology, and motion system;
- implementation and acceptance of the full website outside the Explorer;
- site-wide public-release acceptance.

## Data Sources

Current local raw data includes:

- City of Melbourne hourly pedestrian counts
- City of Melbourne pedestrian sensor locations
- Open-Meteo historical hourly weather
- Victorian Government important dates
- City activities and planned works data
- Melbourne events calendar PDF
- Traffic signal volume data for later extension
- Bicycle volume and speed data for later extension

Raw data is intentionally excluded from Git.

## Tech Stack

- Next.js
- React
- TypeScript
- Tailwind CSS
- pnpm
- Python
- pandas / NumPy / scikit-learn / matplotlib
- JupyterLab

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

## Documentation

- [Project context](PROJECT_CONTEXT.md)
- [Active roadmap](docs/roadmap.md)
- [Result framing](docs/result-framing.md)
- [Full-site design and motion audit](docs/milestone-6-audit.md)
- [Data model](docs/data-model.md)
- [Methodology](docs/methodology.md)
- [Design rationale](docs/design-rationale.md)

## Next Steps

1. Frame the research result and approve contrasting selected cases.
2. Audit the Figma-to-code gap and evaluate GitHub dynamic-art skills.
3. Design and approve the complete Hero, narrative flow, methodology, motion, and responsive states.
4. Implement the approved narrative website and connect it to the Explorer.
5. Run site-wide acceptance and prepare the first public research-portfolio release.
