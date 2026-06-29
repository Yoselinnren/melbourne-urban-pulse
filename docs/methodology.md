# Methodology

This document explains how Melbourne Urban Pulse transforms public urban data into interpretable visual analytics.

## Methodological Position

The project is a research-oriented prototype. Its metrics are designed for interpretability and communication. They should be documented as prototype design choices unless later validated through formal urban science or transport research methods.

## Data Pipeline

Planned pipeline:

1. Collect raw public datasets.
2. Validate schema and file integrity.
3. Profile missingness, date ranges, and sensor coverage.
4. Normalise timestamps and locations.
5. Join pedestrian activity with sensor metadata.
6. Join contextual weather and calendar features.
7. Compute baseline and anomaly metrics.
8. Export a small dashboard-ready JSON file.
9. Document limitations and uncertainty.

## Baseline Method

Recommended MVP baseline:

- Group pedestrian activity by `sensor_id`, weekday, and hour.
- Use median count as the normal baseline.
- Use IQR or standard deviation to describe normal variation.

This keeps the method understandable and defensible for a portfolio/research prototype.

## Anomaly Method

Candidate MVP approaches:

- z-score
- IQR outlier rule
- rolling median deviation
- period-over-period comparison

The first version should use one simple method and explain it clearly.

## Weather Comfort Score

The weather comfort score may consider:

- apparent temperature
- rain or precipitation
- wind speed
- humidity

The score should be described as a heuristic design feature, not a validated comfort model.

## Urban Pulse Index

The Urban Pulse Index may combine:

- activity intensity
- baseline deviation
- anomaly score
- weather comfort
- calendar context

Any weights must be documented as prototype choices.

## Confidence and Limitations

Confidence should account for:

- sensor status
- missing data
- whether a signal is observed, derived, interpolated, or simulated
- whether event explanations are manually verified
- distance from observed sensors if interpolation is used

## Future Work

- More robust anomaly detection
- Event annotation workflow
- Spatial interpolation with explicit uncertainty
- Vehicle and cycling signal integration
- Edge-signal simulation layer
