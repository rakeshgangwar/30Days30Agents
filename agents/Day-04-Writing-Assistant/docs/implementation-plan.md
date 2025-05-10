# Writing Assistant - Implementation Plan

**Overall Goal:** Develop a Writing Assistant with a Python/FastAPI backend, OpenRouter for LLM flexibility, and initial connectors for VS Code and Obsidian, leveraging a shared TypeScript/JavaScript library for common connector logic. Incorporate user preferences.

**Phases:** Aligned with `architecture-plan.md` but with more tech-specific tasks.

---

### **Phase 1: Core Service MVP & Initial Connector (Proof of Concept)**

**(Estimated Duration: TBD - depends on team size/velocity)**

**Goal 1.1: Develop Core Writing Assistant Service (Backend MVP)**

*   **Task 1.1.1: Setup Backend Project Structure**
    *   Initialize Python project using `uv`.
    *   Set up FastAPI application.
    *   Integrate basic logging and configuration management.
    *   **Tech:** Python, FastAPI, `uv`.
*   **Task 1.1.2: Define Core API Endpoints (MVP)**
    *   Design OpenAPI/Swagger schema for initial endpoints:
        *   `/draft` (text input, returns drafted text)
        *   `/analyze_grammar_style` (text input, returns analysis)
        *   `/summarize` (text input, returns summary)
        *   `/adjust_tone` (text input, target tone, returns adjusted text)
    *   Implement basic request/response models (Pydantic).
    *   **Tech:** FastAPI, Pydantic.
*   **Task 1.1.3: LLM Integration via OpenRouter**
    *   Develop an OpenRouter client module in Python.
    *   Integrate LangChain for prompt templating and LLM interaction.
    *   Connect initial API endpoints to LangChain/OpenRouter for basic functionality (using a default LLM initially).
    *   **Tech:** Python, LangChain, OpenRouter API.
*   **Task 1.1.4: Basic User Preferences Service (MVP)**
    *   Design database schema for user preferences (e.g., preferred LLM, default tone).
    *   Implement API endpoints: `/preferences (GET, PUT)`.
    *   Use SQLite for MVP database.
    *   Integrate preference loading into core AI logic (e.g., use preferred LLM if set).
    *   **Tech:** Python, FastAPI, SQLAlchemy (optional), SQLite.
*   **Task 1.1.5: Basic Authentication (Optional for MVP, placeholder)**
    *   If needed for user preferences, implement simple API key auth or placeholder for JWT.
    *   **Tech:** FastAPI security utilities.
*   **Task 1.1.6: Unit & Integration Tests (Backend)**
    *   Write tests for API endpoints and core logic.
    *   **Tech:** `pytest`.
*   **Task 1.1.7: Dockerize Backend Service (Optional for MVP)**
    *   Create a `Dockerfile` for the backend.
    *   **Tech:** Docker.

**Goal 1.2: Develop Shared Connector Logic Library (MVP)**

*   **Task 1.2.1: Setup TypeScript Library Project**
    *   Initialize npm package.
    *   Setup TypeScript, ESLint, Prettier.
    *   **Tech:** TypeScript, npm/yarn.
*   **Task 1.2.2: Implement `ApiService` Module (MVP)**
    *   Methods to call the MVP backend endpoints (`/draft`, `/analyze_grammar_style`, etc.).
    *   Basic error handling.
    *   **Tech:** TypeScript, `axios` or `fetch` API.
*   **Task 1.2.3: Implement `DataModel` Module (MVP)**
    *   TypeScript interfaces for API request/response payloads.
    *   **Tech:** TypeScript.
*   **Task 1.2.4: Unit Tests for Shared Library**
    *   **Tech:** Jest or Vitest.

**Goal 1.3: Develop Initial Connector (e.g., VS Code Extension - PoC)**

*   **Task 1.3.1: Setup VS Code Extension Project**
    *   Use `yo code` generator.
    *   Integrate TypeScript.
    *   **Tech:** TypeScript, VS Code Extension API.
*   **Task 1.3.2: Integrate Shared Connector Library**
    *   Add the shared library as a dependency.
*   **Task 1.3.3: Implement Basic UI & Editor Interaction**
    *   Commands to trigger actions (e.g., "Draft with AI").
    *   Get selected text or current document.
    *   Display results (e.g., in a new editor, notification, or webview).
    *   **Tech:** VS Code API.
*   **Task 1.3.4: Connect UI to `ApiService` from Shared Library**
    *   Call shared library functions to interact with the backend.
*   **Task 1.3.5: Basic User Preference Interaction (PoC)**
    *   Allow setting a preferred LLM via VS Code settings, pass to backend.
*   **Task 1.3.6: Manual Testing & Debugging**

---

### **Phase 2: Expand Connector Ecosystem & Enhance Core Service**

**(Estimated Duration: TBD)**

**Goal 2.1: Develop Second Connector (e.g., Obsidian Plugin)**

*   **Task 2.1.1: Setup Obsidian Plugin Project**
    *   Use Obsidian sample plugin as a template.
    *   Integrate TypeScript.
    *   **Tech:** TypeScript, Obsidian API.
*   **Task 2.1.2: Integrate Shared Connector Library**
*   **Task 2.1.3: Implement UI & Editor Interaction (Obsidian-specific)**
*   **Task 2.1.4: Connect UI to `ApiService`**
*   **Task 2.1.5: User Preference Interaction (Obsidian-specific)**
*   **Task 2.1.6: Testing & Debugging**

**Goal 2.2: Enhance Core Service Features**

*   **Task 2.2.1: Advanced Prompt Engineering**
    *   Develop more sophisticated prompt chains in LangChain.
    *   Allow user-defined custom prompts (stored via User Preferences Service).
*   **Task 2.2.2: Refine User Preferences Service**
    *   Add more preference options (e.g., style profiles, output formats).
    *   Improve UI/UX for managing preferences in connectors.
*   **Task 2.2.3: Robust Authentication & Authorization (if not fully done in MVP)**
    *   Implement JWT-based authentication if user accounts are desired.
*   **Task 2.2.4: Scalable Database (if moving from SQLite)**
    *   Migrate to PostgreSQL/MySQL if needed.
*   **Task 2.2.5: API Versioning Strategy**
    *   Implement a strategy (e.g., URL path versioning `/v1/...`).
*   **Task 2.2.6: Improved Error Handling & Logging**

**Goal 2.3: Enhance Shared Connector Library**

*   **Task 2.3.1: Implement `StateManager` Module**
    *   For caching, managing request statuses, etc.
*   **Task 2.3.2: Refine `ApiService`**
    *   Support for API versioning.
    *   More robust error handling and retry mechanisms.

---

### **Phase 3: Feature Enhancement & Service Maturity**

**(Estimated Duration: TBD)**

*   **Task 3.1: Advanced Core Service Features**
    *   Handling longer documents (chunking, context management).
    *   Deeper integration with external tools (grammar checkers, thesaurus APIs).
    *   User-specific style profiles (more complex than simple preferences).
*   **Task 3.2: Connector-Specific Feature Enhancements**
    *   More seamless UI integrations within each host application.
    *   Context-aware suggestions.
*   **Task 3.3: Performance Optimization**
    *   Backend and connector performance tuning.
*   **Task 3.4: Comprehensive Documentation**
    *   User guides for connectors.
    *   API documentation for developers.
*   **Task 3.5: CI/CD Pipeline Setup**
    *   Automate testing and deployment.
*   **Task 3.6: Develop Connectors for Other Prioritized Tools**
    *   (e.g., LibreOffice, Browser Extension)

---