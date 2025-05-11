# Data Analysis Agent - Frontend

This is the React frontend for the Data Analysis Agent, which provides a user interface for analyzing and visualizing data using natural language queries.

## Features

- CSV file upload and analysis
- SQL database connection and querying
- Natural language query processing
- Data visualization with Plotly
- Responsive UI with Material-UI

## Project Structure

```
frontend/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── csv/
│   │   │   ├── CSVUpload.tsx
│   │   │   └── CSVPreview.tsx
│   │   ├── db/
│   │   │   └── DBConnection.tsx
│   │   ├── query/
│   │   │   └── QueryInput.tsx
│   │   ├── results/
│   │   │   └── ResultsDisplay.tsx
│   │   ├── visualization/
│   │   │   └── PlotlyVisualization.tsx
│   │   └── DataSourceSelection.tsx
│   ├── contexts/
│   │   └── AppContext.tsx
│   ├── hooks/
│   ├── layouts/
│   │   └── MainLayout.tsx
│   ├── services/
│   │   └── api.ts
│   ├── types/
│   │   └── index.ts
│   ├── utils/
│   ├── App.tsx
│   └── main.tsx
├── .env
├── .gitignore
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Setup Instructions

### Prerequisites

- Node.js 18+
- pnpm

### Installation

1. Install dependencies:
   ```bash
   pnpm install
   ```

2. Create a `.env` file with the following content:
   ```
   VITE_API_URL=http://localhost:8000
   ```

## Running the Application

Start the development server:

```bash
pnpm dev
```

The application will be available at http://localhost:5173.

## Building for Production

Build the application for production:

```bash
pnpm build
```

The built files will be in the `dist` directory.

## Environment Variables

- `VITE_API_URL`: URL of the backend API (default: http://localhost:8000)

## Dependencies

- React
- Material-UI
- Plotly.js
- Axios
- React Router
