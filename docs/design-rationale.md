# Design Rationale

This document records interface and visualisation decisions for Melbourne Urban Pulse.

## Design Principle

The interface should explain an urban condition, not merely display charts. Each view should help answer:

1. What happened?
2. Where did it happen?
3. How unusual is it?
4. What context may explain it?
5. How confident is the system?
6. What does it imply for smart infrastructure?

## Core Experience

The intended experience is an urban signal dashboard centred on a **2.5D Urban Pulse Field**.

The field should show sensor-based pulse spikes, glow, or ripple effects over a simplified city plane. It should be treated as a visual analytics metaphor, not as a precise 3D city model.

## Page Structure

### Landing Page

Purpose:

- Introduce the project concept.
- Establish the visual identity.
- Explain Melbourne as a signal system.
- Lead users into the dashboard.

### Dashboard

Purpose:

- Show the main urban pulse analysis.
- Let users explore time, location, activity, context, and anomalies.

Candidate modules:

- Urban Pulse Index card
- 2.5D Urban Pulse Field
- Sensor selector
- Time slider
- Time-series chart
- Weather and calendar context
- Anomaly explanation card
- Location comparison panel

### Methodology Page

Purpose:

- Make the research logic transparent.
- Explain data sources, metrics, confidence, and limitations.

## Visual Language

Possible direction:

- Dark city-grid base
- Warm pulse accents for high activity
- Cool contextual panels for weather and calendar signals
- Subtle glow/ripple effects for activity intensity
- Clear labels for confidence and uncertainty

## Open Questions

- Should the first version be dark, light, or mixed?
- Which Melbourne photos should be used on the landing page?
- How literal should the city map be?
- Should the 2.5D field be implemented with CSS/SVG first or a canvas/WebGL layer later?
