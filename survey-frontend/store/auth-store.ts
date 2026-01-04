'use client';

import { create } from 'zustand';
import axios from 'axios';
import { API_ENDPOINTS, setAuthToken, removeAuthToken, getAuthToken, setUserData, getUserData } from '../lib/api';

interface User {
  id: number;
  email: string;
  firstname: string;
  lastname: string;
  full_name: string;
  is_active: boolean;
  is_staff?: boolean;
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchCurrentUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,  // Start with loading true
  isAuthenticated: false,

  login: async (email: string, password: string) => {
    try {
      set({ isLoading: true });
      const response = await axios.post(API_ENDPOINTS.auth.login, {
        email,
        password,
      });

      const { token, user_id, email: userEmail, firstname, lastname, is_staff } = response.data;
      setAuthToken(token);

      const userData = {
        id: user_id,
        email: userEmail,
        firstname,
        lastname,
        full_name: `${firstname} ${lastname}`.trim() || userEmail,
        is_active: true,
        is_staff,
      };

      // Save user data to localStorage
      setUserData(userData);

      // Set user data in state
      set({
        user: userData,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: async () => {
    try {
      const token = getAuthToken();
      if (token) {
        await axios.post(API_ENDPOINTS.auth.logout, {}, {
          headers: { Authorization: `Bearer ${token}` },
        });
      }
    } catch (_error) {
      console.error('Logout error:', _error);
    } finally {
      removeAuthToken();
      set({
        user: null,
        isAuthenticated: false,
      });
    }
  },

  fetchCurrentUser: async () => {
    const token = getAuthToken();
    if (!token) {
      set({ isAuthenticated: false, user: null, isLoading: false });
      return;
    }

    // Restore user data from localStorage
    const userData = getUserData();
    if (userData) {
      set({ 
        user: userData, 
        isAuthenticated: true, 
        isLoading: false 
      });
    } else {
      // No user data found, clear auth
      removeAuthToken();
      set({ 
        isAuthenticated: false, 
        user: null, 
        isLoading: false 
      });
    }
  },
}));
