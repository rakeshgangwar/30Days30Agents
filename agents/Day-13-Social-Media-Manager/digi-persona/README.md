# Digi-Persona

A platform for creating and managing multiple virtual personas with social media presence powered by AI.

## Overview

Digi-Persona is a system that allows you to create, manage, and operate multiple virtual personas across different social media platforms. Each persona has its own identity, content strategy, and interaction patterns, all powered by AI.

## Features

- **Multi-Persona Support**: Create and manage multiple virtual personas
- **AI-Powered Content Generation**: Generate persona-specific content using advanced AI models
- **Multi-Platform Integration**: Post and interact across Twitter, LinkedIn, and Bluesky
- **Scheduled Posting**: Automate content posting with persona-specific schedules
- **Interaction Management**: Monitor and respond to interactions across platforms
- **Human-in-the-Loop**: Review and approve content before posting
- **Analytics**: Track performance metrics for each persona

## Technology Stack

### Backend
- **Framework**: Python, FastAPI
- **Database**: PostgreSQL
- **AI**: OpenAI GPT-4o
- **Task Scheduling**: Celery, Redis
- **Containerization**: Docker
- **Monitoring**: Prometheus, Grafana

### Frontend
- **Framework**: React with TypeScript
- **Build Tool**: Vite
- **UI Components**: shadcn/ui (built on Tailwind CSS)
- **Routing**: React Router
- **State Management**: Zustand
- **API Client**: Axios
- **Data Visualization**: Recharts

## Getting Started

### Prerequisites

- Python 3.10+ (for local development)
- Docker and Docker Compose (for containerized development and production)
- PostgreSQL (for production)
- Redis (for caching and task queue)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/digi-persona.git
   cd digi-persona
   ```

2. Run the setup script:
   ```
   ./scripts/setup.sh
   ```

3. Create a `.env` file with your configuration:
   ```
   # Application Settings
   APP_NAME=Digi-Persona
   APP_ENV=development
   DEBUG=True
   SECRET_KEY=your-secret-key
   API_PREFIX=/api/v1

   # Database Settings
   DATABASE_URL=sqlite:///./digi_persona.db
   DATABASE_TEST_URL=sqlite:///./digi_persona_test.db

   # Redis Settings (optional)
   REDIS_URL=redis://localhost:6379/0

   # OpenAI Settings
   OPENAI_API_KEY=your-openai-api-key

   # JWT Settings
   JWT_SECRET_KEY=your-jwt-secret-key
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

4. Run the application:

   **Local Development (Backend only):**
   ```bash
   ./scripts/run.sh
   ```

   **Local Development (Frontend only):**
   ```bash
   cd frontend
   pnpm install
   pnpm dev
   ```

   **Docker Development Mode (Backend only):**
   ```bash
   ./scripts/dev-docker.sh
   ```

   **Docker Production Mode (Backend only):**
   ```bash
   ./scripts/prod-docker.sh
   ```

   **Full Application with Docker (Frontend and Backend):**
   ```bash
   ./scripts/run-docker-full.sh
   ```

   For more details on Docker setup, see the [Docker Setup](./docs/docker-setup.md) documentation.

### Usage

#### API
1. Access the API documentation at `http://localhost:8000/api/v1/docs`
2. Create a new persona using the API
3. Generate content for the persona
4. Approve and schedule the content

#### Web Interface
1. Access the web interface at `http://localhost:5173`
2. Log in with the following mock credentials:
   - Email: `john@example.com`
   - Password: `password123`
3. Use the dashboard to manage personas, content, and platform connections
4. Generate AI-powered content and schedule it for posting
5. Monitor interactions and analytics
6. Use the content calendar to schedule and manage content
7. Connect social media platforms through the platform connection interface
8. View analytics and generate reports
9. Configure application settings

### Running Tests

```bash
./scripts/test.sh
```

## API Endpoints

### Personas

- `POST /api/v1/personas` - Create a new persona
- `GET /api/v1/personas/{persona_id}` - Get a persona by ID
- `GET /api/v1/personas` - Get a list of personas
- `PUT /api/v1/personas/{persona_id}` - Update a persona
- `DELETE /api/v1/personas/{persona_id}` - Delete a persona

### Content

- `POST /api/v1/content` - Create a new content item
- `GET /api/v1/content/{content_id}` - Get a content item by ID
- `GET /api/v1/content` - Get a list of content items
- `PUT /api/v1/content/{content_id}` - Update a content item
- `DELETE /api/v1/content/{content_id}` - Delete a content item
- `POST /api/v1/content/generate` - Generate content for a persona
- `POST /api/v1/content/{content_id}/approve` - Approve a content item
- `POST /api/v1/content/{content_id}/publish` - Mark a content item as published
- `POST /api/v1/content/{content_id}/schedule` - Schedule a content item for posting
- `GET /api/v1/content/list/due` - Get content that is due for posting
- `GET /api/v1/content/list/upcoming` - Get content that is scheduled for posting in the near future

## Project Structure

```
digi-persona/
├── app/                    # Backend application code
│   ├── api/                # API endpoints
│   ├── core/               # Core business logic
│   │   └── agent/          # LLM agent framework
│   ├── db/                 # Database models and utilities
│   ├── schemas/            # Pydantic schemas for request/response validation
│   └── main.py             # FastAPI application entry point
├── frontend/               # Frontend application code
│   ├── public/             # Static assets
│   ├── src/                # Source code
│   │   ├── components/     # UI components
│   │   ├── pages/          # Page components
│   │   ├── api/            # API client and services
│   │   ├── store/          # State management
│   │   └── routes/         # Route definitions
│   ├── vite.config.ts      # Vite configuration
│   └── package.json        # Frontend dependencies
├── docs/                   # Documentation
├── scripts/                # Utility scripts
│   ├── run.sh              # Script to run the backend locally
│   ├── setup.sh            # Script to set up the environment
│   ├── test.sh             # Script to run tests
│   ├── dev-docker.sh       # Script to run Docker in development mode
│   └── prod-docker.sh      # Script to run Docker in production mode
├── tests/                  # Test code
├── .env                    # Environment variables
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker services configuration
└── README.md               # This file
```

## Documentation

For detailed documentation, see the [docs](./docs) directory:

- [Initial Plan](./docs/initial-plan.md) - Initial project planning
- [Detailed Plan](./docs/detailed-plan.md) - Comprehensive project plan
- [Implementation Plan](./docs/implementation-plan.md) - Step-by-step implementation guide
- [Docker Setup](./docs/docker-setup.md) - Docker configuration and usage
- [Project Checklist](./docs/project-checklist.md) - Progress tracking
- [Next Steps](./docs/next-steps.md) - Upcoming development phases
- [Frontend Implementation](./docs/frontend-implementation.md) - Frontend architecture and features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for providing the GPT models
- FastAPI for the web framework
- All the open-source libraries that made this project possible
