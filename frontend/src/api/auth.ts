import type { AxiosInstance } from 'axios';
import { apiClient } from './index.js'; // Import the named export apiClient
import type { LoginCredentials, LoginResponse } from './types.js'; // Assuming types are moved or defined here

export const login = async (credentials: LoginCredentials): Promise<LoginResponse> => {
  // apiClient.post for '/user/login' will return a string (the token)
  // due to the modified interceptor in api/index.ts
  const tokenString = await apiClient.post<string>('/user/login', credentials, {
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (typeof tokenString === 'string') {
    // Construct the LoginResponse object as expected by the store
    return {
      access_token: tokenString,
      token_type: 'bearer' // Assuming bearer token type as standard
    };
  } else {
    // This case should ideally not be reached if the backend and interceptor work correctly
    console.error('Login failed: Expected a token string, received:', tokenString);
    throw new Error('Login failed: Did not receive a valid token from server');
  }
};

// Add other auth-related API calls here, e.g., register, refreshToken