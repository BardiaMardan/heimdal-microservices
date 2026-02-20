export interface User {
  id: number;
  email: string;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
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
