import axios from "axios";

// Create an axios instance with default config
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

// Add a request interceptor to include auth token and persona ID
apiClient.interceptors.request.use(
  (config) => {
    // Get auth token from localStorage
    const token = localStorage.getItem("auth_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Get active persona ID from localStorage
    const activePersonaId = localStorage.getItem("active_persona_id");
    if (activePersonaId) {
      config.headers["X-Persona-ID"] = activePersonaId;
    } else {
      console.warn("No active persona ID found in localStorage for API request:", config.url);
    }

    // Log API requests in development
    if (import.meta.env.DEV) {
      console.log(`API ${config.method?.toUpperCase()} request to ${config.url}`, {
        headers: config.headers,
        data: config.data,
        params: config.params,
      });
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle common errors
apiClient.interceptors.response.use(
  (response) => {
    // Log successful responses in development
    if (import.meta.env.DEV) {
      console.log(`API Response from ${response.config.url}:`, {
        status: response.status,
        data: response.data
      });
    }
    return response;
  },
  (error) => {
    // Log detailed error information
    const errorDetails = {
      message: error.message,
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      headers: {
        sent: error.config?.headers,
        received: error.response?.headers
      }
    };
    
    console.error("API Request Failed:", errorDetails);
    
    // Handle authentication errors
    if (error.response && error.response.status === 401) {
      // Clear auth token and redirect to login
      localStorage.removeItem("auth_token");
      window.location.href = "/login";
    }

    // Handle other errors
    return Promise.reject(error);
  }
);

export default apiClient;
