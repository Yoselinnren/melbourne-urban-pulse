export type FieldOrigin =
  | "observed"
  | "derived"
  | "manual_annotation"
  | "future_edge_signal_placeholder";

export type DashboardData = {
  schema_version: string;
  metadata: DashboardMetadata;
  provenance: DashboardProvenance;
  study_period: StudyPeriod;
  field_definitions: Record<FieldOrigin, string[]>;
  sensors: Sensor[];
  calendar_context: CalendarContext[];
  hourly_records: HourlyRecord[];
  explanation_cards: ExplanationCard[];
  pulse_field: PulseField;
  quality_notes: string[];
};

export type DashboardMetadata = {
  project: string;
  dataset_name: string;
  created_at: string;
  created_by: string;
  description: string;
  is_mock: boolean;
  timezone: string;
  spatial_reference: string;
};

export type DashboardProvenance = {
  profile_inputs: string[];
  sources: DataSource[];
};

export type DataSource = {
  source_id: string;
  source_type: string;
  local_path: string;
  used_in_mvp: boolean;
  field_role: string;
  notes: string;
};

export type StudyPeriod = {
  start: string;
  end: string;
  display_label: string;
  selected_reason: string;
};

export type Sensor = {
  sensor_id: string;
  sensor_name: string;
  description: string;
  status: string;
  location_type: string;
  coordinates: {
    latitude: number;
    longitude: number;
  };
  display: {
    precinct: string;
    short_label: string;
  };
  selection_reason: string;
  confidence: {
    metadata_confidence: number;
    coverage_note: string;
  };
};

export type CalendarContext = {
  date: string;
  weekday: string;
  is_weekend: boolean;
  is_public_holiday: boolean;
  is_school_term: boolean;
  is_school_holiday: boolean;
  season: string;
  important_dates: Array<{
    name: string;
    type: string;
    source_status: string;
  }>;
  source_quality: {
    origin: string;
    confidence_score: number;
  };
};

export type WeatherContext = {
  temperature_2m: number;
  apparent_temperature: number;
  relative_humidity_2m: number;
  precipitation: number;
  rain: number;
  wind_speed_10m: number;
  weather_code: number;
  weather_comfort_score: number;
  weather_disruption_flag: boolean;
};

export type SensorReading = {
  sensor_id: string;
  observed_count: number | null;
  direction_1_count: number | null;
  direction_2_count: number | null;
  baseline_count: number | null;
  activity_intensity: number | null;
  baseline_deviation: number | null;
  pulse_score: number | null;
  anomaly_score: number | null;
  is_missing: boolean;
  missing_reason?: string;
  quality: {
    observed_data_available: boolean;
    confidence_score: number;
  };
};

export type HourlyRecord = {
  timestamp: string;
  date: string;
  hour: number;
  calendar: {
    is_weekend: boolean;
    is_public_holiday: boolean;
    season: string;
  };
  weather: WeatherContext;
  sensor_readings: SensorReading[];
  city_summary: {
    total_observed_count: number;
    mean_pulse_score: number;
    max_anomaly_score: number;
    dominant_context: string;
  };
  pulse_field_frame: {
    frame_id: string;
    render_mode: string;
    confidence_surface_available: boolean;
  };
  record_quality: {
    complete_sensor_count: number;
    missing_sensor_count: number;
    confidence_score: number;
  };
};

export type ExplanationCard = {
  card_id: string;
  timestamp: string;
  sensor_id: string | null;
  severity: string;
  title: string;
  summary: string;
  evidence: Array<{
    field: string;
    value: string | number | boolean;
    origin: string;
  }>;
  possible_causes: Array<{
    label: string;
    origin: string;
    confidence: number;
  }>;
  annotation_status: string;
  confidence: {
    score: number;
    reason: string;
  };
};

export type PulseField = {
  field_type: string;
  coordinate_mode: string;
  rendering_strategy: string;
  interpolated_surface_enabled: boolean;
  legend: {
    height: string;
    ripple_radius: string;
    color: string;
    opacity: string;
  };
  frames: PulseFrame[];
  uncertainty_model: Record<string, string>;
};

export type PulseFrame = {
  timestamp: string;
  points: PulsePoint[];
};

export type PulsePoint = {
  sensor_id: string;
  height: number | null;
  ripple_radius: number | null;
  color_value: number | null;
  confidence_score: number;
  infrastructure_pressure_proxy: number | null;
  edge_density_estimate: number | null;
  is_missing?: boolean;
};
