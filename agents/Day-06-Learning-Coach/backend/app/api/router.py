"""
API router for the Learning Coach Agent.
"""

from fastapi import APIRouter

from app.core.config import settings

api_router = APIRouter(prefix=settings.API_V1_STR)

# Import and include routers
from app.api.endpoints import users, agent, learning_paths, quizzes, resources
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
api_router.include_router(learning_paths.router, prefix="/paths", tags=["learning_paths"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["quizzes"])
api_router.include_router(resources.router, prefix="/resources", tags=["resources"])
