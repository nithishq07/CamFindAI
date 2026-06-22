export interface Camera {
  id: number;
  name: string;
  location: string;
  rtsp_url: string;
  fps: number;
  is_recording: boolean;
  status: "online" | "offline" | "warning";
}

export interface Zone {
  id: number;
  camera_id: number;
  name: string;
  coordinates: [number, number][];  // polygon points
  restricted: boolean;
}

export interface Person {
  global_id: string;
  risk_score: number;
  first_seen: string;   // ISO 8601
  last_seen: string;
  current_camera_id: number | null;
  org_id: number;
}

export interface TrajectoryPoint {
  id: number;
  global_id: string;
  camera_id: number;
  zone_id: number | null;
  location_label: string;
  x: number;
  y: number;
  frame_ts: string;
}

export interface Alert {
  id: number;
  severity: "critical" | "high" | "medium" | "low";
  alert_type: string;
  frame_ts: string;
  camera_id: number;
  zone_id: number | null;
  global_id: string;
  status: "open" | "acknowledged" | "resolved";
  acknowledged_by: number | null;
  acknowledged_at: string | null;
  resolved_at: string | null;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: "admin" | "operator" | "investigator" | "viewer";
  org_id: number;
  sso_provider: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}
