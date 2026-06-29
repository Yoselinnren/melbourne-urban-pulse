
## 1. Project Overview

**Melbourne Urban Pulse** is an interactive urban data storytelling and visual analytics project for smart infrastructure research.

It should not be treated as a simple pedestrian dashboard or a decorative portfolio website. Instead, it should be developed as a research-oriented prototype that explains Melbourne CBD’s urban rhythm through multiple urban signals, contextual factors, anomaly patterns, and human-centred interface design.

The first implemented signal will likely be **pedestrian activity**, because Melbourne’s pedestrian sensor data is public, structured, and suitable for building a complete data pipeline. However, the project should not be limited to pedestrian flow. Pedestrian data should act as the first working signal in a broader urban sensing framework that can later support vehicle flow, public transport activity, cycling, events, weather, environmental stress, and edge-generated sensing outputs.

The central research question is:

**How does Melbourne’s urban activity change across time, location, weather, calendar context, and events — and how can these signals be translated into an interpretable smart infrastructure interface?**

---

## 2. Research Positioning

The project can be framed as:

**A research-oriented visual analytics prototype for smart urban infrastructure, designed to translate public urban data and edge-AI-ready sensing signals into interpretable city activity patterns.**

It sits at the intersection of:

- Smart Infrastructure
    
- Urban Computing
    
- HCI / UX for Complex Systems
    
- Data Visualisation / Visual Analytics
    
- Lightweight Urban Data Engineering
    
- Edge-AI-ready Urban Sensing Interfaces
    

The project should not falsely claim to perform real edge AI inference unless that capability is actually implemented and evaluated.

A more accurate positioning is:

**The current project builds the interpretation and visualisation layer for future distributed urban sensing systems.**

The data model should therefore be designed to support future edge-generated signals, such as pedestrian density estimates, vehicle flow anomalies, environmental comfort readings, or infrastructure pressure indicators from local sensors or resource-constrained devices.

---

## 3. Core Concept: Urban Signal Interpretation System

The project should not begin from the question “What data can we find?” It should begin from the question “What urban condition do we want users to understand?”

The system can be structured into five layers.

### 3.1 Mobility Pulse

This represents observable urban movement.

First version:

- Pedestrian flow
    

Future extensions:

- Vehicle flow
    
- Public transport activity
    
- Cycling activity
    
- Parking occupancy
    
- Crowd density proxy
    

The key is to design a general signal schema so that different forms of urban movement can eventually use the same analytical and visual structure.

### 3.2 Environmental Context

This explains how weather and environmental conditions affect urban activity.

Possible variables:

- Temperature
    
- Apparent temperature
    
- Rainfall
    
- Wind speed
    
- Humidity
    
- Weather condition
    

Derived outputs:

- Weather Comfort Score
    
- Weather Disruption Flag
    

### 3.3 Calendar Rhythm

This captures institutional and social time structures.

Possible variables:

- Weekday / weekend
    
- Public holidays
    
- School terms
    
- University semesters
    
- Daylight saving transitions
    
- Season
    

This layer helps distinguish true anomalies from expected calendar-driven changes.

### 3.4 Event and Disruption Layer

This captures special events and disruptions that may explain unusual urban activity.

Possible variables:

- Festivals
    
- Sports matches
    
- Concerts
    
- Protests
    
- Transport disruptions
    
- Road closures
    
- Extreme weather warnings
    
- Construction works
    

The first version can use manually curated event notes for selected anomalies. Later versions may integrate external event or disruption datasets.

### 3.5 Infrastructure Pressure Interpretation

This is the final interpretive layer.

It answers:

- Is current activity higher than the normal baseline?
    
- Is the pattern routine, unusual, or disruptive?
    
- Can weather, holidays, school terms, or events explain the change?
    
- Does the signal suggest local infrastructure pressure?
    
- How should future edge-generated signals be interpreted in the interface?
    

Outputs may include:

- Urban Pulse Index
    
- Baseline Deviation
    
- Anomaly Score
    
- Infrastructure Pressure Proxy
    
- Confidence Score
    
- Explanation Card
    

---

## 4. Core Visual Concept: 2.5D Urban Pulse Field

A key visual module should be the **2.5D Urban Pulse Field**.

Different sensors have different geographic locations. These locations can be mapped onto a city plane, with height, glow, ripple, or vertical spikes representing activity intensity, anomaly strength, or infrastructure pressure at a selected time.

This should not be presented as a full 3D city model or an exact physical terrain. It is better understood as a **spatial-temporal activity field** derived from distributed urban sensors.

Basic mapping logic:

- x / y: sensor position on the city plane
    
- z / height: activity intensity, baseline deviation, pulse score, or anomaly score
    
- time: controlled by a time slider
    
- context: explained through a nearby interpretation panel
    

For the first version, the safest implementation is:

- Sensor-based 2.5D pulse spikes
    
- Ripple circles
    
- Time slider
    
- Context explanation panel
    

Later versions can extend this into:

- Gaussian influence field
    
- Interpolated pulse surface
    
- Anomaly surface
    
- Edge signal simulation layer
    

If a continuous surface is generated, the methodology must clearly state that it is a derived or interpolated field, not a directly observed continuous city state. Areas farther away from sensors should show lower confidence.

---

## 5. Data Layer Design

### 5.1 Core MVP Data

The first version should focus on:

1. **City of Melbourne pedestrian counts**
    
    - Hourly pedestrian activity
        
    - First implemented mobility signal
        
2. **Pedestrian sensor metadata**
    
    - sensor_id
        
    - sensor name
        
    - latitude / longitude
        
    - status
        
    - direction
        
    - installation context
        
3. **Historical weather**
    
    - temperature
        
    - apparent temperature
        
    - rainfall
        
    - wind speed
        
    - humidity
        
    - weather condition
        
4. **Victorian public holidays and important dates**
    
    - public holidays
        
    - school terms
        
    - daylight saving changes
        
    - potentially university semester markers
        
5. **Manually curated event or disruption notes**
    
    - used only for selected anomalies
        
    - clearly labelled as manually verified or exploratory
        

### 5.2 Later Data Extensions

Potential later additions:

- Vehicle flow
    
- Cycling data
    
- Public transport / GTFS
    
- Parking occupancy
    
- Road closures
    
- Major events
    
- Air quality
    
- Noise or environmental sensing
    
- Edge AI simulated outputs
    
- Real-time urban sensor streams
    

The first version should avoid too many data sources. The goal is to build a clear research and technical structure before expanding the scope.

---

## 6. Metrics and Parameters

The technical depth should come from clear metric design rather than tool stacking.

### 6.1 Activity Intensity

Measures how active a place is at a given time.

Possible basis:

- raw count
    
- normalised count
    
- percentile rank
    

### 6.2 Baseline Deviation

Measures how far current activity deviates from normal patterns.

Recommended baseline:

- group by sensor_id + weekday + hour
    
- use median as the normal baseline
    
- use IQR or standard deviation as variation range
    

### 6.3 Anomaly Score

Detects unusual activity patterns.

Possible methods:

- z-score
    
- IQR outlier detection
    
- rolling median deviation
    
- period-over-period comparison
    

The MVP should prefer interpretable methods rather than black-box models.

### 6.4 Weather Comfort Score

Measures how favourable the weather is for urban activity.

Possible assumptions:

- 18–24°C as a comfortable temperature band
    
- rainfall reduces comfort
    
- strong wind reduces comfort
    
- apparent temperature may be more relevant than raw temperature
    

### 6.5 Calendar Context Score

Represents time-based context.

Possible flags:

- weekday / weekend
    
- public holiday
    
- school term / break
    
- daylight saving transition
    
- season
    

### 6.6 Urban Pulse Index

A composite overview metric for the interface.

It may combine:

- mobility activity
    
- baseline deviation
    
- weather comfort
    
- calendar context
    
- anomaly signal
    

The methodology should clearly state that the weights are prototype design choices, not validated urban science claims.

### 6.7 Confidence Score

Represents uncertainty.

Possible factors:

- sensor status
    
- missing data ratio
    
- distance from sensor
    
- whether an event explanation was manually verified
    
- whether the signal is real, derived, or simulated
    

---

## 7. Interface Logic

The UI should not be a collection of charts. It should present an explanatory chain:

1. What happened?
    
2. Where did it happen?
    
3. How unusual is it?
    
4. What contextual factors might explain it?
    
5. How confident is the system?
    
6. What does it imply for smart infrastructure?
    

### 7.1 Landing Page

Purpose: introduce the concept and visual identity.

Content:

- Melbourne Urban Pulse title
    
- Explanation of the city as a signal system
    
- Original Melbourne photography
    
- Core signal themes: movement, weather, calendar, events
    
- Entry point to the dashboard
    

### 7.2 Dashboard

Purpose: show the main analysis.

Modules:

- Urban Pulse Index
    
- 2.5D Urban Pulse Field
    
- Sensor selector
    
- Time slider
    
- Time-series chart
    
- Weather and calendar context
    
- Anomaly explanation cards
    
- Location comparison panel
    

### 7.3 Methodology Page

Purpose: support research credibility.

Content:

- Data sources
    
- Data pipeline
    
- Data schema
    
- Baseline method
    
- Anomaly method
    
- Urban Pulse Index logic
    
- Edge signal layer
    
- Limitations
    
- Future work
    

---

## 8. Visualisation Design

Charts should be designed around the intended conclusions, not chosen randomly.

### 8.1 Temporal Rhythm

Question: When is the city active?

Possible views:

- hourly line chart
    
- weekday-hour heatmap
    
- daily trend
    
- anomaly timeline
    

### 8.2 Spatial Pulse

Question: Where does activity concentrate?

Possible views:

- sensor map
    
- 2.5D pulse field
    
- location ranking bar chart
    
- precinct comparison
    

### 8.3 Context Explanation

Question: Do weather, holidays, school terms, or events explain the change?

Possible views:

- weather vs activity scatter
    
- holiday vs normal comparison
    
- school term vs break comparison
    
- event annotation timeline
    

### 8.4 Methodology and Data Quality

Question: How reliable is the result?

Possible views:

- data pipeline diagram
    
- missing data summary
    
- confidence labels
    
- source provenance cards
    

---

## 9. Implementation Roadmap

### Phase 0: Baseline Setup

Completed:

- Next.js scaffold
    
- TypeScript / Tailwind
    
- Python `.venv`
    
- Python packages
    
- JupyterLab
    
- lint / build
    
- GitHub baseline
    

### Phase 1: Project Framing

Goals:

- Replace default README
    
- Define research question
    
- Define MVP scope
    
- Define data sources
    
- Define signal schema
    
- Create initial documentation
    

Outputs:

- `docs/data-model.md`
    
- `docs/methodology.md`
    
- `docs/design-rationale.md`
    
- updated README
    

### Phase 2: Mock Vertical Slice

Goal:

Validate frontend structure before using real data.

Outputs:

- `public/dashboard-data/dashboard_data.json`
    
- TypeScript types
    
- Landing page
    
- Basic dashboard layout
    
- One metric card
    
- One time-series view
    
- One sensor/location view
    
- One explanation card
    

### Phase 3: Real Pedestrian Data Pipeline

Goal:

Integrate real pedestrian count and sensor metadata.

Outputs:

- fetch script
    
- validation script
    
- preprocessing script
    
- baseline calculation
    
- anomaly calculation
    
- exported dashboard JSON
    

### Phase 4: Context Data Integration

Goal:

Add weather, public holidays, school terms, daylight saving, and event context.

Outputs:

- weather fetcher
    
- calendar fetcher
    
- event annotation structure
    
- context-aware anomaly explanation
    

### Phase 5: Urban Pulse Field

Goal:

Implement the project’s core visual experience.

First version:

- sensor-based 2.5D spikes
    
- time slider
    
- pulse score rendering
    
- context explanation
    

Later version:

- interpolated pulse surface
    
- anomaly surface
    
- confidence surface
    

### Phase 6: Research and Portfolio Polish

Goal:

Make the project suitable for public portfolio use and RA applications.

Outputs:

- polished README
    
- methodology page
    
- screenshots
    
- Vercel deployment
    
- final visual system
    
- accessibility checks
    
- performance checks
    
- limitations and future work
    

---

## 10. Final Goal

The final project should demonstrate:

1. A working interactive urban visual analytics website
    
2. A clear data processing pipeline
    
3. An interpretable Urban Pulse metric system
    
4. A visually distinctive 2.5D Urban Pulse Field
    
5. An edge-AI-ready sensing data model
    
6. Transparent methodology and limitations
    
7. A research artefact suitable for GitHub portfolio and RA applications
    

The purpose is not simply to show where pedestrian activity is high.

The deeper goal is to show:

**How distributed urban sensor signals, environmental context, calendar rhythm, and event disruptions can be transformed into a human-interpretable view of smart infrastructure conditions.**