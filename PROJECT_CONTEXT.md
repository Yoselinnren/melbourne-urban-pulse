# Melbourne Urban Pulse - Project Context

> Current direction: an English-only research portfolio project for research-degree applications. A future personal portfolio and custom domain may contain this project, but are outside the first release.

## Project Overview

**Melbourne Urban Pulse** is a research-oriented urban data storytelling and visual analytics prototype. It aims to explain Melbourne's urban rhythm through public sensor data, contextual signals, anomaly patterns, and human-centred interface design.

The project should not be treated as a simple pedestrian-count dashboard. Pedestrian activity is the first implemented signal because it is public, structured, spatially located, and suitable for building a complete data pipeline. The broader ambition is to create an extensible urban signal interpretation system that can later support vehicle flow, cycling, public transport activity, weather, events, disruption records, and future edge-generated sensing outputs.

Core research question:

> How does Melbourne's urban activity change across time, location, weather, calendar context, and events — and how can these signals be translated into an interpretable smart infrastructure interface?

## Research Positioning

The project sits at the intersection of:

- Smart infrastructure
- Urban computing
- Human-computer interaction for complex systems
- Data visualisation and visual analytics
- Lightweight urban data engineering
- Edge-AI-ready urban sensing interfaces

The current project does **not** claim to perform real edge AI inference. A more accurate framing is:

> Melbourne Urban Pulse builds the interpretation and visualisation layer for future distributed urban sensing systems.

This means the data model and interface should be designed so future edge-generated signals can be added without changing the core research story.

## Technical Stack

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Package manager: pnpm
- Data environment: Python virtual environment with pandas, NumPy, requests, matplotlib, scikit-learn, and JupyterLab
- Data storage: local raw and processed files under `data/`
- Documentation: Markdown files under the project root and `docs/`

## Data Scope

Current raw data sources include:

- City of Melbourne hourly pedestrian counts
- City of Melbourne pedestrian sensor locations
- Open-Meteo historical hourly weather for Melbourne
- Victorian Government important dates
- City activities and planned works data
- Melbourne events calendar PDF
- Traffic signal volume data for later vehicle-flow extension
- Bicycle volume and speed data for later cycling extension

The MVP should focus on pedestrian activity, sensor metadata, weather, calendar context, and selected manually curated event or disruption notes.

## Core Concept

The system should be designed as an **Urban Signal Interpretation System** with five layers:

1. **Mobility Pulse** — observed movement, starting with pedestrian flow.
2. **Environmental Context** — weather and environmental comfort.
3. **Calendar Rhythm** — weekday/weekend, holidays, terms, seasons, and institutional rhythms.
4. **Event and Disruption Layer** — events, planned works, road closures, and manually reviewed anomalies.
5. **Infrastructure Pressure Interpretation** — baseline deviation, anomaly strength, confidence, and explanatory cards.

## Key Metrics

The first version should prefer interpretable methods over black-box modelling.

- Activity Intensity
- Baseline Deviation
- Anomaly Score
- Weather Comfort Score
- Calendar Context Flags
- Confidence Score

The current project does not implement or claim a validated Urban Pulse Index.

## Visual Direction

The key visual module is the **2.5D Urban Pulse Field**:

- x/y: sensor location on a city plane
- height/glow/ripple: activity intensity, pulse score, or anomaly strength
- time: controlled by a time slider
- context: explained through nearby interpretation panels

The first version should use sensor-based 2.5D spikes and ripple effects. If a continuous surface is added later, it must be described as an interpolated field, not a directly observed city state.

## Current Project State

Completed:

- reproducible analytical phases from source profiling through explanation-ready aggregation;
- a 12-sensor representative mode with 4,647 episodes and 425 Pulses;
- deterministic public UI data and independent validation;
- an annual Explorer with spatial, temporal, filtering, Pulse, and sensor states;
- evidence schemas, a review queue, 64 evidence facts, and 64 automatic matches.

Not yet completed:

- human review of the automatic matches;
- an approved visual identity and responsive Explorer;
- the narrative homepage and public methodology presentation;
- browser, accessibility, and public-release acceptance.

## Development Rules

- Keep raw data out of Git.
- Keep processed/generated data out of Git unless intentionally exporting a small public demo file.
- Do not overclaim edge AI capability unless it is implemented and evaluated.
- Prioritise a clear research story over adding many unrelated charts.
- Use interpretable baseline and anomaly methods first.
- Maintain transparent limitations and confidence labels.
- Build a small vertical slice before expanding the number of data sources.

## Next Steps

See [docs/roadmap.md](docs/roadmap.md) for the ordered milestones, ownership, and acceptance gates.
