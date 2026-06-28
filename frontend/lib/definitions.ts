export interface User {
  id: number;
  email: string;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export type DeviceType = "machine" | "environmental" | "fleet" | "storage";
export type DeviceStatus = "active" | "inactive" | "decommissioned";

export interface Device {
  id: string;
  name: string;
  type: DeviceType;
  status: DeviceStatus;
  location: string | null;
  description: string | null;
  hardware_id: string | null;
  claimed: boolean;
  claimed_at: string | null;
  last_seen_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface StandardResponse<T = any> {
  status: boolean;
  code: number;
  message: string;
  data: T | null;
}

export interface ApiError {
  status: false;
  code: number;
  message: string;
  data: any;
}
