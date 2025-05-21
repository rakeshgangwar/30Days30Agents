import path from "path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    proxy: {
      // Proxy API requests to the backend server
      '/api': {
        target: process.env.DOCKER_ENV === 'true' ? 'http://app:8000' : 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        // Preserve the base path in proxied requests
        rewrite: (path) => path,
        // Configure how the proxy handles redirects
        configure: (proxy) => {
          proxy.on('proxyRes', function(proxyRes) {
            // Handle redirects by rewriting the location header
            if (proxyRes.headers['location']) {
              // For Docker environment, replace absolute URLs with paths relative to the frontend
              const location = proxyRes.headers['location'];
              if (location.includes('app:8000') || location.includes('localhost:8000')) {
                // Extract the path from the URL
                const url = new URL(location);
                // Use just the pathname+search for the redirect
                proxyRes.headers['location'] = url.pathname + url.search;
              }
            }
          });
        }
      },
    },
  },
})
