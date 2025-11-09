from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from backend.adk_agent.adk_service import adk_service


router = APIRouter(prefix="/adk", tags=["ADK Agent"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@router.post("/chat")
async def chat_with_agent(request: ChatRequest):
    """
    Chat with the ADK agent for mission planning.
    Returns agent response and, if generated, a mission playbook.
    """
    try:
        # Prepare session and runner
        session, runner = await adk_service.setup_session_and_runner(
            user_id=request.user_id,
            session_id=request.session_id
        )

        # Ask the agent
        result = await adk_service.call_agent(
            query=request.message,
            runner=runner,
            user_id=request.user_id or adk_service.default_user_id,
            session_id=session.id
        )

        return {
            "session_id": session.id,
            "agent_response": result.get("agent_response"),
            "playbook": result.get("playbook"),
            "ready_to_execute": bool(result.get("playbook")),
            "geojson": result.get("geojson"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


