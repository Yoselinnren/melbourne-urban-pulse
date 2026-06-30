import exampleDashboardData from "../../public/dashboard-data/example_dashboard_data.json";
import type { DashboardData, HourlyRecord, Sensor } from "./types";

export const dashboardData = exampleDashboardData as DashboardData;

export function getSensorById(sensorId: string): Sensor | undefined {
  return dashboardData.sensors.find((sensor) => sensor.sensor_id === sensorId);
}

export function formatHour(timestamp: string): string {
  return new Intl.DateTimeFormat("en-AU", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
    timeZone: dashboardData.metadata.timezone,
  }).format(new Date(timestamp));
}

export function getTotalActivity(record: HourlyRecord): number {
  return record.sensor_readings.reduce(
    (total, reading) => total + (reading.observed_count ?? 0),
    0,
  );
}

export function getLatestRecord(): HourlyRecord {
  return dashboardData.hourly_records[dashboardData.hourly_records.length - 1];
}

export function getPeakRecord(): HourlyRecord {
  return dashboardData.hourly_records.reduce((peak, record) =>
    getTotalActivity(record) > getTotalActivity(peak) ? record : peak,
  );
}
