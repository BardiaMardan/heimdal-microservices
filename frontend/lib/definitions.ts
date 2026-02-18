export interface User {
  id: number;
  email: string;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface ApiError {
  detail?: string | { msg: string }[];
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}
