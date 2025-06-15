export interface BackendResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

export interface User {
  id: number;
  username: string;
  email?: string;
  is_active?: boolean;
  is_superuser?: boolean;
  // Add any other user-related fields your backend provides
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  username?: string; // Optional: if your backend returns username upon login
  // Add other fields your backend returns upon login if necessary
}