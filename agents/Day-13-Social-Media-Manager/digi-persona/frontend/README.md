# Digi-Persona Frontend

This is the frontend web interface for the Digi-Persona application, built with React, Vite, and shadcn/ui.

## Overview

The Digi-Persona frontend provides a user-friendly interface for managing multiple virtual personas, generating and scheduling content, monitoring interactions, and analyzing performance across different social media platforms.

## Features

- **Multi-Persona Management**: Create, edit, and manage multiple virtual personas
- **Content Creation and Scheduling**: Generate content with AI assistance and schedule it for posting
- **Platform Connections**: Connect and manage social media platform integrations
- **Interaction Management**: Monitor and respond to interactions across platforms
- **Analytics Dashboard**: Track performance metrics and gain insights

## Technology Stack

- **Framework**: React with TypeScript
- **Build Tool**: Vite
- **UI Components**: shadcn/ui (built on Tailwind CSS)
- **Routing**: React Router
- **State Management**: Zustand
- **API Client**: Axios
- **Data Fetching**: TanStack Query (React Query)
- **Charts**: Recharts
- **Form Handling**: React Hook Form
- **Date Handling**: date-fns

## Project Structure

```
frontend/
├── public/            # Static assets
├── src/
│   ├── components/    # UI components
│   │   ├── ui/        # shadcn components
│   │   ├── layout/    # Layout components
│   │   ├── personas/  # Persona-related components
│   │   ├── content/   # Content-related components
│   │   ├── platforms/ # Platform-related components
│   │   ├── analytics/ # Analytics components
│   │   └── common/    # Shared components
│   ├── hooks/         # Custom hooks
│   ├── lib/           # Utility functions
│   ├── api/           # API client and services
│   ├── store/         # State management
│   ├── pages/         # Page components
│   ├── routes/        # Route definitions
│   ├── types/         # TypeScript types
│   ├── App.tsx        # Main App component
│   └── main.tsx       # Entry point
├── .eslintrc.js       # ESLint configuration
├── tsconfig.json      # TypeScript configuration
├── vite.config.ts     # Vite configuration
└── package.json       # Dependencies and scripts
```

## Getting Started

### Prerequisites

- Node.js (v18 or later)
- pnpm (v8 or later)

### Installation

1. Clone the repository
2. Navigate to the frontend directory:
   ```bash
   cd digi-persona/frontend
   ```
3. Install dependencies:
   ```bash
   pnpm install
   ```

### Development

Run the development server:

```bash
pnpm run dev
```

The application will be available at http://localhost:5173

### Building for Production

Build the application:

```bash
pnpm run build
```

Preview the production build:

```bash
pnpm run preview
```

## API Integration

The frontend communicates with the Digi-Persona API for all data operations. The API client is configured in `src/api/client.ts` and uses Axios for HTTP requests.

Environment variables:

- `VITE_API_URL`: The base URL for the API (defaults to "http://localhost:8000/api/v1")

## Authentication

The application uses JWT-based authentication. The token is stored in localStorage and included in API requests via an Axios interceptor.

## State Management

Global state is managed using Zustand. The main stores are:

- `personaStore`: Manages personas and active persona selection
- `contentStore`: Manages content items and content generation

## Adding New Features

1. Create new components in the appropriate directory
2. Add new pages in the `pages` directory
3. Update routes in `src/routes/index.tsx`
4. Add new API services in the `api` directory
5. Create or update stores as needed

## Contributing

1. Follow the established project structure
2. Use TypeScript for type safety
3. Follow the component patterns used in the project
4. Test your changes thoroughly

## License

This project is licensed under the MIT License.
