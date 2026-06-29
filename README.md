# Melbourne Urban Pulse

Melbourne Urban Pulse is a research-oriented urban data storytelling and visual analytics prototype for smart infrastructure research.

The project explores how Melbourne's urban activity changes across time, location, weather, calendar context, and events — and how these signals can be translated into an interpretable interface for future smart infrastructure systems.

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
5. **Infrastructure Pressure Interpretation** — baseline deviation, anomaly strength, confidence, and explanatory cards.

The key visual concept is a **2.5D Urban Pulse Field**, where sensor locations are shown on a simplified city plane and activity intensity is represented through height, glow, or ripple effects.

## Current Status

Completed:

- Next.js project scaffold
- TypeScript and Tailwind baseline
- Python virtual environment for data work
- Core raw datasets collected locally
- Initial research and design framing
- Documentation skeletons

Not yet completed:

- Processed dashboard-ready dataset
- Data profiling scripts or notebooks
- Baseline and anomaly calculations
- Manual event annotations
- Custom frontend interface
- Final visual system

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

## Documentation

- [Project context](PROJECT_CONTEXT.md)
- [Data model](docs/data-model.md)
- [Methodology](docs/methodology.md)
- [Design rationale](docs/design-rationale.md)

## Next Steps

1. Profile the raw datasets.
2. Define the first dashboard JSON schema.
3. Generate a small processed MVP dataset.
4. Build the first frontend vertical slice.
5. Add the 2.5D Urban Pulse Field after the data schema is stable.
