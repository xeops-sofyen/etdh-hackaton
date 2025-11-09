"""
Simplified ADK Service for Drone Mission Planning
Based on ADK Runner pattern - no manual event appending needed
"""
import logging
import os
from typing import Optional, Tuple, List, Dict, Any
from pathlib import Path

from google.adk.agents import Agent
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService, Session
from google.adk.sessions.base_session_service import ListSessionsResponse
from google.genai import types

from .agent_factory import get_drone_agent
from .config import ADK_CONFIG
from .geojson_converter import playbook_to_geojson

logger = logging.getLogger(__name__)


class ADKService:
    """Simplified ADK service for drone mission planning"""

    def __init__(self) -> None:
        self.setup_environment()

        # Initialize database session service
        db_path = Path("./backend/data/adk_sessions.db")
        db_path.parent.mkdir(parents=True, exist_ok=True)

        db_url = f"sqlite:///{db_path}"
        self.session_service = DatabaseSessionService(db_url=db_url)

        # App configuration
        self.app_name = "heimdall_drone_planner"
        self.default_user_id = "default_user"

        logger.info(f"ADK Service initialized with database: {db_path}")

    def setup_environment(self) -> None:
        """Set up environment variables for Google AI"""
        os.environ["GOOGLE_API_KEY"] = ADK_CONFIG['api_key']
        # Add other env vars if needed (Vertex AI, etc.)

    async def setup_session_and_runner(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Tuple[Session, Runner]:
        """
        Create or get existing session and runner.

        The Runner automatically handles conversation persistence via session_service.
        No manual event appending needed!

        Args:
            user_id: User identifier (optional, defaults to default_user)
            session_id: Session ID (optional, creates new if not provided)

        Returns:
            Tuple of (Session, Runner)
        """
        user = user_id or self.default_user_id

        # Try to get existing session
        session: Optional[Session] = None
        if session_id:
            session = await self.session_service.get_session(
                app_name=self.app_name,
                user_id=user,
                session_id=session_id
            )

        # Create new session if needed
        if not session:
            # Initialize session state for drone missions
            initial_state = {
                'latest_playbook': None,
                'latest_geojson': None,
                'mission_count': 0
            }

            session = await self.session_service.create_session(
                app_name=self.app_name,
                user_id=user,
                session_id=session_id,  # Will auto-generate if None
                state=initial_state
            )
            logger.info(f"Session created: '{session.id}' for user: '{user}'")
        else:
            logger.info(f"Session reused: '{session.id}' for user: '{user}'")

        # Get agent
        agent: Agent = get_drone_agent()

        # Create runner - it automatically persists conversation!
        runner: Runner = Runner(
            agent=agent,
            app_name=self.app_name,
            session_service=self.session_service
        )

        logger.info(f"Runner created for agent '{agent.name}'")
        return session, runner

    async def call_agent(
        self,
        query: str,
        runner: Runner,
        user_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Send a query to the agent and return the final response.

        The Runner handles all conversation persistence automatically.

        Args:
            query: User message
            runner: Runner instance
            user_id: User ID
            session_id: Session ID

        Returns:
            Dict with agent_response, playbook, geojson, etc.
        """
        logger.info(f">>> User Query: {query}")

        # Prepare user message in ADK format
        content: types.Content = types.Content(
            role="user",
            parts=[types.Part(text=query)]
        )

        # Initialize response tracking
        final_text = ""
        playbook = None
        geojson = None

        # Execute agent
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            # # Track tool calls for playbook creation
            # if hasattr(event, 'content') and event.content and event.content.parts:
            #     for part in event.content.parts:
            #         # Check for function responses (completed tool calls)
            #         if hasattr(part, 'function_response') and part.function_response:
            #             func_name = part.function_response.name
            #             func_result = part.function_response.response

            #             # If playbook was created, extract it and generate geojson
            #             if func_name == 'create_mission_playbook' and func_result:
            #                 result_data = func_result.get('result')
            #                 if result_data:
            #                     playbook = result_data
            #                     # Generate GeoJSON from playbook
            #                     try:
            #                         from .geojson_converter import playbook_to_geojson
            #                         geojson = playbook_to_geojson(playbook)
            #                     except Exception as e:
            #                         logger.error(f"GeoJSON conversion error: {e}")

            # Process final response
            if event.is_final_response():
                if event.content and event.content.parts:
                    # Extract text response
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            final_text = part.text
                session = await self.session_service.get_session(
                    app_name=self.app_name,
                    user_id=user_id,
                    session_id=session_id
                )
                if session:
                    playbook = session.state.get('playbook')
                    geojson = playbook_to_geojson(playbook)
                break

        # # Update session state with playbook/geojson if created
        # if playbook or geojson:
        #     session = await self.session_service.get_session(
        #         app_name=self.app_name,
        #         user_id=user_id,
        #         session_id=session_id
        #     )

        #     if session:
        #         # Ensure state exists
        #         if session.state is None:
        #             session.state = {}

        #         # Update state with new playbook/geojson
        #         if playbook:
        #             session.state['latest_playbook'] = playbook
        #             current_count = session.state.get('mission_count', 0)
        #             session.state['mission_count'] = current_count + 1
        #         if geojson:
        #             session.state['latest_geojson'] = geojson

        #         # ADK's Session object will auto-persist state changes
        #         logger.info(f"Updated session state: playbook={playbook is not None}, geojson={geojson is not None}")

        logger.info(f"<<< Agent Response: {final_text[:100] if final_text else 'No text response'}...")

        return {
            'agent_response': final_text or "I've processed your request.",
            'playbook': playbook,
            'geojson': geojson,
            'ready_to_execute': playbook is not None
        }

    async def get_session_state(
        self,
        user_id: str,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get session state"""
        session = await self.session_service.get_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id
        )

        if not session:
            return None

        return session.state

    async def get_session_events(
        self,
        user_id: str,
        session_id: str
    ) -> List[Event]:
        """Get all events (conversation history) for a session"""
        try:
            session = await self.session_service.get_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id
            )

            if not session:
                logger.debug("Session not found")
                return []

            # Access events directly from session
            events: List[Event] = session.events if hasattr(session, "events") else []
            return events

        except Exception as e:
            logger.error(f"Error getting events for session {session_id}: {e}")
            return []

    async def list_user_sessions(
        self,
        user_id: Optional[str] = None
    ) -> List[Session]:
        """List all sessions for a user"""
        try:
            user = user_id or self.default_user_id

            response: ListSessionsResponse = await self.session_service.list_sessions(
                app_name=self.app_name,
                user_id=user
            )

            sessions: List[Session] = response.sessions
            return sessions if isinstance(sessions, list) else []

        except Exception as e:
            logger.error(f"Error listing sessions for user {user_id}: {e}")
            return []

    async def delete_session(
        self,
        user_id: str,
        session_id: str
    ) -> bool:
        """Delete a session"""
        try:
            await self.session_service.delete_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id
            )
            logger.info(f"Deleted session: {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return False

    async def export_session(
        self,
        user_id: str,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """Export complete session data"""
        session = await self.session_service.get_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id
        )

        if not session:
            return None

        # Convert events to serializable format
        messages = []
        if session.events:
            for event in session.events:
                if isinstance(event, types.Content):
                    msg = {
                        'role': event.role,
                        'parts': []
                    }
                    if event.parts:
                        for part in event.parts:
                            if hasattr(part, 'text'):
                                msg['parts'].append({'text': part.text})
                    messages.append(msg)

        state = session.state or {}

        return {
            'id': session.id,
            'user_id': session.user_id,
            'app_name': session.app_name,
            'messages': messages,
            'latest_playbook': state.get('latest_playbook'),
            'latest_geojson': state.get('latest_geojson'),
            'mission_count': state.get('mission_count', 0),
        }


# Global ADK service instance
adk_service = ADKService()
