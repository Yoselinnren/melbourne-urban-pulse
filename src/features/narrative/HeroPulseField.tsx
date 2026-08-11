"use client";

import type { CSSProperties } from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import type { PulseDetailData } from "@/lib/types/ui-data";

const pulseId = "P1F_REPRESENTATIVE_12_above_baseline_202501010000";
const fallback = [50, 72, 38, 86, 58, 94, 64, 100, 70, 44, 76, 54];

export default function HeroPulseField() {
  const [pulse, setPulse] = useState<PulseDetailData | null>(null);
  const [failed, setFailed] = useState(false);
  const [active, setActive] = useState(true);
  const fieldRef = useRef<HTMLDivElement>(null);
  const intersectingRef = useRef(true);

  useEffect(() => {
    const controller = new AbortController();
    fetch(`/data/ui/v1/pulses/${pulseId}.json`, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error("Pulse data unavailable");
        return response.json() as Promise<PulseDetailData>;
      })
      .then(setPulse)
      .catch((error) => {
        if (error?.name !== "AbortError") setFailed(true);
      });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    const node = fieldRef.current;
    if (!node) return;
    const syncActive = () => setActive(intersectingRef.current && !document.hidden);
    const observer = new IntersectionObserver(([entry]) => {
      intersectingRef.current = entry.isIntersecting;
      syncActive();
    });
    const visibility = () => syncActive();
    observer.observe(node);
    document.addEventListener("visibilitychange", visibility);
    return () => {
      observer.disconnect();
      document.removeEventListener("visibilitychange", visibility);
    };
  }, []);

  const heights = useMemo(() => {
    if (!pulse) return fallback;
    const strongest = new Map<string, number>();
    for (const episode of pulse.episodes) {
      strongest.set(episode.sensorId, Math.max(strongest.get(episode.sensorId) ?? 0, episode.peakAbsScore));
    }
    const values = [...strongest.values()].slice(0, 12);
    const max = Math.max(...values, 1);
    return values.map((value) => Math.round(34 + (value / max) * 66));
  }, [pulse]);

  const state = pulse ? "ready" : failed ? "fallback" : "loading";

  return (
    <div ref={fieldRef} className={`pulse-field pulse-field--${state} ${active ? "is-active" : ""}`} aria-busy={state === "loading"}>
      <div className="pulse-field__head">
        <span>URBAN PULSE FIELD · SELECTED CASE</span>
        <strong>New Year phase 01 · network-wide above baseline</strong>
        <small>01 JAN 2025 · 00:00–05:00 · 12/12 SENSORS · 6 HOURS</small>
      </div>
      <div className="pulse-field__plot" role="img" aria-label="Twelve discrete sensor anomaly traces">
        <div className="pulse-field__grid" aria-hidden="true" />
        <div className="pulse-field__baseline" aria-hidden="true" />
        {state === "loading" ? (
          <div className="pulse-field__skeleton" role="status" aria-label="Loading verified Pulse data">
            {fallback.map((height, index) => (
              <i aria-hidden="true" key={index} style={{ "--trace-height": `${height}%`, "--skeleton-delay": `${index * 45}ms` } as CSSProperties} />
            ))}
            <span>LOADING VERIFIED PULSE DATA</span>
          </div>
        ) : (
          <div className="pulse-field__traces" aria-hidden="true">
            {heights.map((height, index) => (
              <span className={`pulse-trace ${index === 7 ? "is-selected" : ""}`} key={index} style={{ "--trace-height": `${height}%`, "--trace-delay": `${Math.floor(index / 2) * 60}ms` } as CSSProperties}>
                <i />
              </span>
            ))}
          </div>
        )}
      </div>
      <div className="pulse-field__foot">
        <span>Discrete sensor observations · no interpolated city surface</span>
        <span>{failed ? "STATIC FALLBACK · FINAL VALUES" : "▲ ABOVE BASELINE · ● SELECTED PHASE"}</span>
        <strong>06:00–10:00 → network-wide below baseline</strong>
      </div>
    </div>
  );
}
