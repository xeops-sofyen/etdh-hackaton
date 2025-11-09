"""
Example Usage of Simplified ADK Service

This script demonstrates how to use the new simplified ADK service
for conversational drone mission planning.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.adk_agent.adk_service import adk_service


async def example_single_turn():
    """Example: Single-turn mission creation"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Single-Turn Mission Creation")
    print("="*60)

    # Setup session and runner (creates new session)
    session, runner = await adk_service.setup_session_and_runner()

    print(f"Created session: {session.id}")

    # Create a mission with a single request
    query = "Create a patrol mission around coordinates 48.8788, 2.3675 at 50m altitude with 8 waypoints in a circular pattern"

    print(f"\nUser: {query}")

    result = await adk_service.call_agent(
        query=query,
        runner=runner,
        user_id=session.user_id,
        session_id=session.id
    )

    print(f"\nAgent: {result['agent_response']}")
    print(f"\nPlaybook created: {result['playbook'] is not None}")
    print(f"GeoJSON created: {result['geojson'] is not None}")
    print(f"Ready to execute: {result['ready_to_execute']}")

    if result['playbook']:
        print(f"\nMission ID: {result['playbook']['mission_id']}")
        print(f"Waypoint count: {len(result['playbook']['waypoints'])}")

    return session.id


async def example_multi_turn(session_id: str):
    """Example: Multi-turn conversation (continuing previous session)"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Multi-Turn Conversation")
    print("="*60)

    # Continue existing session
    session, runner = await adk_service.setup_session_and_runner(
        session_id=session_id
    )

    print(f"Continuing session: {session.id}")

    # Modify the mission
    query = "Increase the altitude to 80 meters"

    print(f"\nUser: {query}")

    result = await adk_service.call_agent(
        query=query,
        runner=runner,
        user_id=session.user_id,
        session_id=session.id
    )

    print(f"\nAgent: {result['agent_response']}")

    # The agent automatically has access to the full conversation history!
    # No manual history management needed.


async def example_session_retrieval(session_id: str):
    """Example: Retrieve session data"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Session Retrieval")
    print("="*60)

    # Export full session data
    session_data = await adk_service.export_session(
        user_id="default_user",
        session_id=session_id
    )

    if session_data:
        print(f"\nSession ID: {session_data['id']}")
        print(f"Message count: {len(session_data['messages'])}")
        print(f"Mission count: {session_data.get('mission_count', 0)}")
        print(f"Has playbook: {session_data['latest_playbook'] is not None}")

        print("\nConversation history:")
        for i, msg in enumerate(session_data['messages'], 1):
            role = msg['role']
            parts = msg.get('parts', [])
            if parts and 'text' in parts[0]:
                text = parts[0]['text'][:100]
                print(f"  {i}. [{role}]: {text}...")
    else:
        print(f"Session {session_id} not found")


async def example_list_sessions():
    """Example: List all sessions"""
    print("\n" + "="*60)
    print("EXAMPLE 4: List All Sessions")
    print("="*60)

    sessions = await adk_service.list_user_sessions()

    print(f"\nFound {len(sessions)} active session(s)")

    for i, session in enumerate(sessions, 1):
        print(f"\n{i}. Session {session.id}")
        print(f"   User: {session.user_id}")
        print(f"   Events: {len(session.events) if session.events else 0}")
        if session.state:
            print(f"   Has playbook: {session.state.get('latest_playbook') is not None}")
            print(f"   Mission count: {session.state.get('mission_count', 0)}")


async def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("SIMPLIFIED ADK SERVICE - USAGE EXAMPLES")
    print("="*60)
    print("\nThese examples demonstrate the new simplified architecture.")
    print("No manual event appending - ADK Runner handles everything!\n")

    try:
        # Example 1: Create a mission
        session_id = await example_single_turn()

        # Example 2: Continue conversation
        await example_multi_turn(session_id)

        # Example 3: Retrieve session
        await example_session_retrieval(session_id)

        # Example 4: List sessions
        await example_list_sessions()

        print("\n" + "="*60)
        print("✓ All examples completed successfully!")
        print("="*60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run examples
    asyncio.run(main())
