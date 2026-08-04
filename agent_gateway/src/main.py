import sys
import os

#path resolution
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from typing import Dict, Any, Optional
from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field

from auth import auth_router
from auth.router import get_current_user
from agents.supervisor import run_supervisor_agent

app = FastAPI(
    title="Agent Gateway API",
    description="REST API Gateway hosting LangGraph AI Banking Agent with JWT authentication.",
    version="1.0.0"
)

# Mount authentication router
app.include_router(auth_router)

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message/query for the banking agent")
    thread_id: Optional[str] = Field(None, description="Optional conversation session/thread ID")

class ChatResponse(BaseModel):
    response: str
    user_id: str
    thread_id: str

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "agent_gateway"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Protected chat endpoint: Executes the LangGraph banking supervisor agent
    using user_id extracted from the validated JWT token and optional thread_id.
    """
    user_id = current_user["user_id"]
    thread_id = request.thread_id or f"thread_{user_id}"
    
    agent_output = await run_supervisor_agent(
        user_query=request.message,
        user_id=user_id,
        thread_id=thread_id
    )
    
    return ChatResponse(
        response=agent_output,
        user_id=user_id,
        thread_id=thread_id
    )
