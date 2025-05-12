"""
Agent endpoints for the Learning Coach Agent.
"""

from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.agent_service import AgentService


router = APIRouter()
agent_service = AgentService()


class AgentRequest(BaseModel):
    """Agent request schema."""
    
    user_input: str
    user_id: Optional[int] = None
    context: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    """Agent response schema."""
    
    response: str
    context: Dict[str, Any]


@router.post("/chat", response_model=AgentResponse)
async def chat_with_agent(request: AgentRequest) -> Dict[str, Any]:
    """Chat with the Learning Coach Agent."""
    try:
        response = await agent_service.process_user_input(
            request.user_input, request.user_id, request.context
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}",
        )
