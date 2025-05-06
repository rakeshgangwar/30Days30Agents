# Agent Communication Standardization Plan

## Overview

This document outlines the strategy for standardizing communication between agents built as part of the 30 Days 30 Agents challenge. The goal is to ensure all agents, regardless of their implementation framework or language, can effectively communicate using either REST API with OpenAPI schema or Google's A2A protocol.

## Implementation Timeline

### Phase 1: Core Schema Design (Days 1-3)

**Goals:**
- Define minimal but extensible message schema
- Create capability advertisement format
- Document core REST endpoints for all agents

**Deliverables:**
1. `message_schema.json` - Standard message format
2. `capability_schema.json` - Capability advertisement format
3. `api_endpoints.md` - Core REST endpoints specification

### Phase 2: Individual Agent Development (Days 4-20)

**Goals:**
- Build diverse agents with core functionality
- Implement simplified standard interfaces
- Document adaptation challenges
- Tag components for future standardization

**Deliverables:**
1. Working agents with basic communication capability
2. `adaptation_notes.md` - Framework-specific challenges
3. Tagged codebase for future standardization work

### Phase 3: Standardization Refinement (Days 21-30)

**Goals:**
- Refine communication standards based on experience
- Create adapters for key agents
- Develop integration tests
- Build lightweight agent registry

**Deliverables:**
1. Updated schemas and specifications
2. Framework adapters for major agent types
3. Integration test suite
4. Central agent registry prototype

## Message Schema (v0.1)

```json
{
  "message_id": "uuid-string",
  "sender": {
    "agent_id": "string",
    "agent_type": "string",
    "framework": "string"
  },
  "receiver": {
    "agent_id": "string"
  },
  "content": {
    "type": "text|json|binary",
    "data": {},
    "format_version": "string"
  },
  "metadata": {
    "timestamp": "ISO-datetime",
    "conversation_id": "uuid-string",
    "capabilities_used": ["capability-name"],
    "context": {}
  }
}
```

## Capability Advertisement Format (v0.1)

```json
{
  "agent_id": "string",
  "name": "string",
  "description": "string",
  "version": "string",
  "capabilities": [
    {
      "name": "string",
      "description": "string",
      "parameters": [
        {
          "name": "string",
          "type": "string",
          "description": "string",
          "required": boolean
        }
      ],
      "return_schema": {}
    }
  ],
  "protocols_supported": ["rest", "a2a", "websocket"]
}
```

## Core REST API Endpoints

Each agent should implement these minimum endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| /health | GET | Basic health check |
| /capabilities | GET | List agent capabilities |
| /message | POST | Send message to agent |
| /conversations/{id} | GET | Get conversation history |
| /schema | GET | Get OpenAPI schema |

## Framework-Specific Adapters

### Python (LangChain/LlamaIndex)

```python
# Example adapter snippet
class StandardCommunicationMixin:
    def get_capabilities(self):
        """Return agent capabilities in standard format"""
        pass

    def process_standard_message(self, message):
        """Process message in standard format"""
        pass
```

### Node.js

```javascript
// Example adapter snippet
class StandardCommunication {
  getCapabilities() {
    // Return agent capabilities in standard format
  }

  processStandardMessage(message) {
    // Process message in standard format
  }
}
```

## Testing Strategy

- Unit Tests: Validate individual components
- Schema Validation: Ensure messages conform to schema
- Integration Tests: Test pairs of agents communicating
- A2A Compatibility: Verify A2A protocol support

## Future Considerations

- Federation between agent registries
- Security and access control
- Performance optimization
- Scaling to large agent ecosystems

This plan provides a structured approach to standardizing communication while still allowing you to focus on building diverse, functional agents throughout your 30-day challenge.