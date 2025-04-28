import os
import asyncio
import json
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Import your async agent creation function
import sys
sys.path.append("..")
from agents import get_agent_async

app = FastAPI()
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int):
    await websocket.accept()
    print(f"Client #{session_id} connected")

    # Create agent and session
    root_agent, exit_stack = await get_agent_async()

    # Set up ADK runner/session as in your async_main
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
    from google.genai import types

    session_service = InMemorySessionService()
    artifacts_service = InMemoryArtifactService()
    session = session_service.create_session(
        state={}, app_name='mcp_maps_app', user_id=f'user_{session_id}'
    )
    runner = Runner(
        app_name='mcp_maps_app',
        agent=root_agent,
        artifact_service=artifacts_service,
        session_service=session_service,
    )

    try:
        while True:
            text = await websocket.receive_text()
            content = types.Content(role='user', parts=[types.Part(text=text)])
            events_async = runner.run_async(
                session_id=session.id, user_id=session.user_id, new_message=content
            )
            async for event in events_async:
                # Send only the text part to the client
                if hasattr(event, "content") and event.content and event.content.parts:
                    msg = event.content.parts[0].text
                    await websocket.send_text(json.dumps({"message": msg}))
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await exit_stack.aclose()
        print(f"Client #{session_id} disconnected")