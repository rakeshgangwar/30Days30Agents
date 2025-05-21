import { create } from "zustand";
import { persist } from "zustand/middleware";

interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  resetPassword: (email: string) => Promise<void>;
  clearError: () => void;
}



export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email, password) => {
        set({ isLoading: true, error: null });

        try {
          // Call the real API endpoint
          const response = await fetch('http://localhost:8000/api/v1/auth/login', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
            },
            credentials: 'include',
            body: new URLSearchParams({
              username: email,
              password: password,
            }),
          });

          const data = await response.json();

          if (response.ok) {
            // Fetch user profile with the token
            const userResponse = await fetch('http://localhost:8000/api/v1/auth/me', {
              headers: {
                'Authorization': `Bearer ${data.access_token}`,
              },
              credentials: 'include',
            });

            if (userResponse.ok) {
              const userData = await userResponse.json();

              // Store token in localStorage for API client
              localStorage.setItem("auth_token", data.access_token);

              set({
                user: {
                  id: userData.id.toString(),
                  name: userData.full_name || email.split('@')[0],
                  email: userData.email,
                  avatar: userData.avatar || '/avatars/default.png',
                },
                token: data.access_token,
                isAuthenticated: true,
                isLoading: false,
              });
            } else {
              // Fallback if user profile fetch fails
              // Store token in localStorage for API client
              localStorage.setItem("auth_token", data.access_token);

              set({
                user: {
                  id: '1',
                  name: email.split('@')[0],
                  email: email,
                  avatar: '/avatars/default.png',
                },
                token: data.access_token,
                isAuthenticated: true,
                isLoading: false,
              });
            }
          } else {
            set({
              error: data.detail || "Invalid email or password",
              isLoading: false,
            });
          }
        } catch (error) {
          console.error('Login error:', error);
          set({
            error: "An error occurred during login. Please try again.",
            isLoading: false,
          });
        }
      },

      register: async (name, email, password) => {
        set({ isLoading: true, error: null });

        try {
          // Call the real API endpoint
          const response = await fetch('http://localhost:8000/api/v1/auth/register', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
              full_name: name,
              email: email,
              password: password,
            }),
          });

          const data = await response.json();

          if (response.ok) {
            // After successful registration, log in the user
            await fetch('http://localhost:8000/api/v1/auth/login', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
              },
              credentials: 'include',
              body: new URLSearchParams({
                username: email,
                password: password,
              }),
            })
            .then(response => response.json())
            .then(loginData => {
              // Store token in localStorage for API client
              localStorage.setItem("auth_token", loginData.access_token);

              set({
                user: {
                  id: data.id.toString(),
                  name: data.full_name || name,
                  email: data.email,
                  avatar: data.avatar || '/avatars/default.png',
                },
                token: loginData.access_token,
                isAuthenticated: true,
                isLoading: false,
              });
            });
          } else {
            set({
              error: data.detail || "Registration failed. Please try again.",
              isLoading: false,
            });
          }
        } catch (error) {
          console.error('Registration error:', error);
          set({
            error: "An error occurred during registration. Please try again.",
            isLoading: false,
          });
        }
      },

      logout: () => {
        // Remove token from localStorage
        localStorage.removeItem("auth_token");

        set({
          user: null,
          token: null,
          isAuthenticated: false
        });
      },

      resetPassword: async (email) => {
        set({ isLoading: true, error: null });

        try {
          // In a real app, this would call an API endpoint to send a password reset email
          // For now, we'll just simulate a successful response
          await new Promise(resolve => setTimeout(resolve, 1000));

          set({
            isLoading: false
          });
        } catch (error) {
          set({
            error: "An error occurred while processing your request",
            isLoading: false
          });
        }
      },

      clearError: () => {
        set({ error: null });
      }
    }),
    {
      name: "auth-storage", // name of the item in localStorage
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
);
