"""
FastAPI Entry Point for Agent Gateway Microservice
"""

from fastapi import FastAPI
from auth import auth_router

app = FastAPI(
    title="Agent Gateway API",
    description="REST API Gateway hosting LangGraph AI Banking Agent with JWT authentication.",
    version="1.0.0"
)

# Mount authentication router
app.include_router(auth_router)


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "agent_gateway"}
