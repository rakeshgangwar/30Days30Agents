# Detailed Implementation Plan for Digi-Persona

## Project Overview

This project aims to build a virtual human with a social media presence managed by an AI agent. The system will support multiple personas, each with their own identity, content strategy, platform connections, and interaction patterns.

## Technology Stack Selection

1. **Programming Language**: Python (for its extensive libraries for AI, web requests, and automation)
2. **Package Manager**: uv (for faster, more reliable Python package management)
3. **Core AI Model**: OpenAI API (GPT-4) for content generation and interaction
4. **LLM Agent Framework**: LangChain for agent-based AI orchestration
5. **Social Media Platform Integration**:
   - Twitter API
   - LinkedIn API
   - Bluesky API (AT Protocol)
6. **Database**: PostgreSQL (for storing persona details, content history, interaction logs)
7. **Hosting**: Docker containers for easy deployment and scaling
8. **Framework**: FastAPI for API endpoints and web interface
9. **Scheduling**: Celery with Redis for task scheduling and orchestration
10. **Monitoring**: Prometheus and Grafana for system monitoring
11. **Human-in-the-Loop**: Web interface for content review and approval

## Project Structure

Here's the proposed project structure with multi-persona support:

```
digi-persona/
├── app/                      # Main application code
│   ├── api/                  # API endpoints
│   │   ├── endpoints/
│   │   │   ├── personas.py   # Plural to indicate multiple personas
│   │   │   ├── content.py
│   │   │   ├── platforms.py
│   │   │   └── interactions.py
│   ├── core/                 # Core functionality
│   │   ├── ai/               # Basic AI integration (OpenAI API)
│   │   ├── agent/            # LLM agent framework
│   │   │   ├── memory.py     # Agent memory management
│   │   │   ├── tools.py      # Agent tools
│   │   │   ├── prompts.py    # Prompt templates
│   │   │   ├── reasoning.py  # Decision-making
│   │   │   └── manager.py    # Agent lifecycle management
│   │   ├── personas/         # Plural to indicate multiple personas
│   │   │   ├── manager.py    # Manages multiple personas
│   │   │   ├── context.py    # Persona context management
│   │   │   └── models.py     # Persona data models
│   │   ├── content/          # Content generation and management
│   │   └── platforms/        # Social media platform integrations
│   ├── db/                   # Database models and connections
│   │   ├── models/
│   │   │   ├── persona.py    # Updated for multi-persona support
│   │   │   ├── content.py    # Links to persona
│   │   │   ├── platform.py   # Links to persona
│   │   │   └── interaction.py # Links to persona
│   ├── scheduler/            # Task scheduling
│   └── web/                  # Web interface
│       ├── dashboard.py      # Multi-persona dashboard
│       ├── persona_manager.py # Interface for managing personas
├── config/                   # Configuration files
├── docs/                     # Documentation
├── scripts/                  # Utility scripts
├── tests/                    # Test suite
├── .env.example              # Example environment variables
├── docker-compose.yml        # Docker configuration
├── Dockerfile                # Docker build file
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Python project configuration
└── README.md                 # Project documentation
```

## Multi-Persona Architecture

### Database Schema

1. **Persona Model**:
   - Each persona will have a unique identifier
   - Stores persona attributes (name, background, interests, values, tone, etc.)
   - All content, interactions, and platform connections will be linked to a specific persona

2. **Platform Connections**:
   - Each persona can have its own set of platform connections
   - Authentication tokens and API keys will be associated with specific personas

3. **Content and Interactions**:
   - All content and interactions will be linked to a specific persona
   - Content generation prompts will be persona-specific

### Persona Context Management

1. **Context Manager**:
   - Manages the current active persona context
   - All operations require a persona context
   - Middleware sets persona context for API requests

2. **Persona-Specific Configuration**:
   - Each persona has its own configuration settings
   - Content strategies, posting schedules, and interaction rules are persona-specific

### User Interface

1. **Persona Selection**:
   - Dashboard includes persona selection
   - Users can switch between personas

2. **Persona Management**:
   - Interfaces for adding, editing, and deleting personas
   - Persona cloning functionality for quick setup

3. **Persona-Specific Views**:
   - All dashboard views are filtered by the current persona
   - Comparative analytics across personas

## Key Implementation Components

### Persona Context Management

```python
# app/core/personas/context.py
class PersonaContext:
    """Manages the current active persona context."""

    def __init__(self):
        self.current_persona_id = None

    def set_persona(self, persona_id):
        self.current_persona_id = persona_id

    def get_persona(self):
        return self.current_persona_id

    def require_persona(self):
        """Ensures a persona is set in the context."""
        if not self.current_persona_id:
            raise ValueError("No active persona in context")
        return self.current_persona_id

# Global persona context
persona_context = PersonaContext()
```

### Database Models with Persona Relationships

```python
# app/db/models/persona.py
class Persona(Base):
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    background = Column(Text)
    interests = Column(ARRAY(String))
    values = Column(ARRAY(String))
    tone = Column(String)
    expertise = Column(ARRAY(String))
    purpose = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    content = relationship("Content", back_populates="persona")
    platform_connections = relationship("PlatformConnection", back_populates="persona")
    interactions = relationship("Interaction", back_populates="persona")

# app/db/models/content.py
class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=False)
    content_type = Column(String)
    text = Column(Text)
    platform = Column(String)
    status = Column(String)  # draft, pending_review, approved, published
    scheduled_time = Column(DateTime, nullable=True)
    published_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to persona
    persona = relationship("Persona", back_populates="content")
```

### API Middleware for Persona Context

```python
# app/api/middleware.py
from fastapi import Request, HTTPException
from app.core.personas.context import persona_context

async def persona_middleware(request: Request, call_next):
    """Middleware to set persona context from request."""
    persona_id = request.headers.get("X-Persona-ID")
    if persona_id:
        persona_context.set_persona(persona_id)
    response = await call_next(request)
    return response
```

### Content Generation with Persona Context

```python
# app/core/content/generator.py
from app.core.personas.context import persona_context
from app.db.models.persona import Persona
from app.db.session import get_db

async def generate_content(content_type, topic):
    """Generate content for the current persona."""
    persona_id = persona_context.require_persona()

    # Get persona details
    db = next(get_db())
    persona = db.query(Persona).filter(Persona.id == persona_id).first()

    # Generate content using persona attributes
    prompt = f"Generate a {content_type} about {topic} in the voice of {persona.name}. "
    prompt += f"Tone: {persona.tone}. Background: {persona.background}."

    # Call LLM with persona-specific prompt
    # ...
```

### Scheduler with Persona-Specific Tasks

```python
# app/scheduler/tasks.py
from celery import Celery
from app.core.personas.context import persona_context

app = Celery('tasks')

@app.task
def generate_scheduled_content(persona_id, content_type, topic):
    """Generate content for a specific persona."""
    persona_context.set_persona(persona_id)
    # Generate and schedule content
    # ...

@app.task
def schedule_all_personas():
    """Schedule tasks for all active personas."""
    # Get all active personas
    # For each persona, schedule persona-specific tasks
    # ...
```

## Additional Features for Multi-Persona Support

1. **Persona Templates**:
   - Predefined persona templates for quick setup
   - Import/export persona configurations

2. **Persona Groups**:
   - Group related personas together
   - Apply bulk operations to persona groups

3. **Cross-Persona Analytics**:
   - Compare performance metrics across personas
   - Identify successful strategies to apply to other personas

4. **Persona Permissions**:
   - User roles and permissions per persona
   - Different team members can manage different personas

## Detailed Implementation Steps

### Phase 1: Project Setup and Foundation

1. **Project Initialization**
   - Set up the project structure
   - Initialize Git repository
   - Create a virtual environment
   - Set up Docker configuration

2. **Database Setup**
   - Define database schema with multi-persona support
   - Create models for personas, content, platforms, and interactions
   - Implement database migrations

3. **Core Persona Module**
   - Implement persona context management
   - Create persona manager for CRUD operations
   - Develop persona data models and validation

### Phase 2: AI Integration and Content Generation

4. **AI Integration**
   - Set up OpenAI API integration
   - Implement prompt engineering for persona-consistent content
   - Create content generation pipeline with persona context
   - Develop content review and approval workflow

5. **Content Management**
   - Implement content storage and retrieval with persona filtering
   - Create persona-specific content scheduling
   - Develop content analytics per persona

### Phase 2.5: LLM Agent Framework Implementation

6. **Agent Core Setup**
   - Implement LangChain integration
   - Create agent initialization with persona context
   - Develop agent state management
   - Implement prompt template system

7. **Agent Memory and Tools**
   - Create conversation history storage
   - Implement context window management
   - Develop platform-specific tools
   - Create information retrieval tools

8. **Agent Reasoning and Integration**
   - Implement decision-making based on persona attributes
   - Create content strategy adherence
   - Develop ethical guidelines enforcement
   - Integrate with content generation and interaction systems

### Phase 3: Platform Integration

9. **Social Media Platform Integration**
   - Implement Twitter API integration with persona-specific authentication
   - Implement LinkedIn API integration with persona-specific authentication
   - Implement Bluesky API integration with persona-specific authentication

10. **Interaction Management**
   - Develop system for monitoring mentions and replies per persona
   - Implement interaction filtering and prioritization
   - Create AI-assisted response generation with persona context
   - Build human review interface for interactions

### Phase 4: Scheduling and Orchestration

11. **Task Scheduling**
   - Set up Celery with Redis
   - Implement scheduled content generation for multiple personas
   - Create persona-specific posting schedules
   - Develop periodic interaction monitoring for all personas

12. **Workflow Orchestration**
   - Implement content generation → review → posting workflow with persona context
   - Create interaction monitoring → response generation → review → reply workflow
   - Develop error handling and retry mechanisms

### Phase 5: Web Interface and Human-in-the-Loop

13. **Web Interface Development**
    - Create dashboard with persona selection
    - Implement persona management interface
    - Develop content review and approval interface with persona filtering
    - Build interaction management interface with persona context

14. **Authentication and Authorization**
    - Implement user authentication
    - Create role-based access control with persona-specific permissions
    - Secure API endpoints

### Phase 6: Monitoring, Analytics, and Compliance

15. **Monitoring and Logging**
    - Set up system monitoring with Prometheus and Grafana
    - Implement comprehensive logging with persona context
    - Create alerting for critical issues

16. **Analytics**
    - Develop engagement metrics tracking per persona
    - Create comparative performance dashboards
    - Implement A/B testing for content strategies across personas

17. **Compliance and Ethics**
    - Implement transparency features (AI disclosure) for each persona
    - Create content filtering for ethical considerations
    - Develop platform ToS compliance checks

### Phase 7: Testing, Deployment, and Documentation

18. **Testing**
    - Write unit tests for core functionality
    - Implement integration tests for platform interactions
    - Create end-to-end tests for workflows with multiple personas

19. **Deployment**
    - Set up CI/CD pipeline
    - Create deployment scripts
    - Implement backup and recovery procedures

20. **Documentation**
    - Write comprehensive API documentation
    - Create user guides for the web interface
    - Develop operational runbooks

## Implementation Timeline

1. **Week 1: Project Setup and Multi-Persona Foundation**
   - Project initialization with uv package manager
   - Database setup with multi-persona support
   - Persona context management implementation

2. **Week 2: AI Integration and Content Generation**
   - AI integration with persona context
   - Content management with persona filtering

3. **Week 2.5: LLM Agent Framework Implementation**
   - Agent core setup with LangChain
   - Agent memory and tools implementation
   - Agent reasoning and integration

4. **Week 3: Platform Integration**
   - Platform integrations with persona-specific authentication
   - Interaction management with persona context

5. **Week 4: Scheduling and Orchestration**
   - Task scheduling for multiple personas
   - Workflow orchestration with persona context

6. **Week 5: Web Interface and Human-in-the-Loop**
   - Web interface with persona selection
   - Authentication and authorization with persona permissions

7. **Week 6: Monitoring, Analytics, and Compliance**
   - Monitoring and logging with persona context
   - Analytics with cross-persona comparison
   - Compliance and ethics for multiple personas

8. **Week 7: Testing, Deployment, and Documentation**
   - Testing with multiple personas
   - Deployment
   - Documentation

## Docker Setup for Development and Production

We will use Docker for containerization, which provides a consistent environment for development, testing, and production. The Docker setup includes:

1. **FastAPI Application**: The main API service
2. **Celery Worker**: For background task processing
3. **Celery Beat**: For scheduled tasks
4. **PostgreSQL**: For database storage
5. **Redis**: For caching and Celery message broker
6. **Prometheus**: For metrics collection
7. **Grafana**: For metrics visualization

We have created two scripts to run the application in different modes:

- **Development Mode**: `./scripts/dev-docker.sh`
  - Hot reloading enabled (`--reload` flag for Uvicorn)
  - Debug mode enabled
  - Environment set to "development"
  - Volume mounts for live code changes

- **Production Mode**: `./scripts/prod-docker.sh`
  - Hot reloading disabled
  - Debug mode disabled
  - Environment set to "production"
  - Optimized for performance and stability

This setup allows us to develop and test the application in an environment that closely resembles production, while still having the convenience of automatic reloading during development.

## Package Management with uv

We will use uv instead of pip for Python package management, which offers several advantages:

1. **Speed**: uv is significantly faster than pip for installing packages
2. **Reliability**: Better dependency resolution and fewer conflicts
3. **Reproducibility**: More consistent environments across development and production
4. **Caching**: Efficient caching of packages for faster subsequent installations

Instead of using `pip install -r requirements.txt`, we will use:

```bash
uv pip install -r requirements.txt
```

We will also create a `pyproject.toml` file for modern Python packaging configuration.
