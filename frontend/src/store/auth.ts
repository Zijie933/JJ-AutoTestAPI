import { defineStore } from 'pinia';
import { login as apiLogin } from '@/api/auth.js';
import type { LoginResponse } from '@/api/types.js';
import type { LoginCredentials } from '@/api/types.js';
import type { User } from '@/api/types.js'; // Assuming User type is defined in types.ts

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem('authToken') || null,
    user: JSON.parse(localStorage.getItem('authUser') || 'null'),
    isAuthenticated: !!localStorage.getItem('authToken'),
  }),
  getters: {
    // No specific getters needed for now, can add later if required
  },
  actions: {
    async login(credentials: LoginCredentials) {
      try {
        const response: LoginResponse = await apiLogin(credentials);
        console.log(response)
        if (response && response.access_token) { // Adjust based on your actual LoginResponse structure
          this.token = response.access_token;
          // Assuming your LoginResponse also contains user info or you make another call to get it
          // For now, let's mock a user object or assume it's part of the response
          // You might need to fetch user details separately if not included in login response
          const mockUser: User = { id: 1, username: credentials.username, email: '', is_active: true, is_superuser: false }; // Example user
          this.user = mockUser; // 由于 LoginResponse 类型中未定义 user 属性，直接使用 mockUser
          this.isAuthenticated = true;
          localStorage.setItem('authToken', this.token);
          localStorage.setItem('authUser', JSON.stringify(this.user));
          return true;
        } else {
          // Handle cases where login is successful but no token (should not happen with correct backend)
          // Or if response structure is different
          throw new Error('Login failed: No token received');
        }
      } catch (error: any) {
        this.logout(); // Ensure clean state on error
        console.error('Login failed:', error);
        throw error; // Re-throw to be caught by the component
      }
    },
    logout() {
      this.token = null;
      this.user = null;
      this.isAuthenticated = false;
      localStorage.removeItem('authToken');
      localStorage.removeItem('authUser');
    },
    // Action to initialize store from localStorage (e.g., on app load)
    // This is implicitly handled by the initial state definition now.
    // You could add an explicit action if more complex initialization is needed.
    // checkAuth() {
    //   this.token = localStorage.getItem('authToken');
    //   const storedUser = localStorage.getItem('authUser');
    //   this.user = storedUser ? JSON.parse(storedUser) : null;
    //   this.isAuthenticated = !!this.token;
    // }
  },
});