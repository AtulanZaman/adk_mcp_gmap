# agent.py (modify get_tools_async and other parts as needed)
import asyncio
from dotenv import load_dotenv
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService # Optional
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams, StdioServerParameters
import os

load_dotenv()
google_maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")

async def get_tools_async():
  """ Step 1: Gets tools from the Google Maps MCP Server."""
  # Read the API key from environment variable

  if not google_maps_api_key or "YOUR_API_KEY" in google_maps_api_key:
      raise ValueError("Please set 'GOOGLE_MAPS_API_KEY' in your .env file.")

  print("Attempting to connect to MCP Google Maps server...")
  tools, exit_stack = await MCPToolset.from_server(
      connection_params=StdioServerParameters(
          command='npx',
          args=["-y",
                "@modelcontextprotocol/server-google-maps",
          ],
          # Pass the API key as an environment variable to the npx process
          env={
              "GOOGLE_MAPS_API_KEY": google_maps_api_key,
          }
      )
  )
  print("MCP Toolset created successfully.")
  return tools, exit_stack

# --- Step 2: Agent Definition ---
async def get_agent_async():
  """Creates an ADK Agent equipped with tools from the MCP Server."""
  tools, exit_stack = await get_tools_async()
  print(f"Fetched {len(tools)} tools from MCP server.")
  root_agent = LlmAgent(
      model='gemini-2.0-flash', # Adjust if needed
      name='maps_assistant',
      instruction='Help user with mapping and directions using available tools.',
      tools=tools
  )
  return root_agent, exit_stack

# --- Step 3: Main Execution Logic (modify query) ---
async def async_main():
  session_service = InMemorySessionService()
  artifacts_service = InMemoryArtifactService() # Optional

  session = session_service.create_session(
      state={}, app_name='mcp_maps_app', user_id='user_maps'
  )

  # TODO: Use specific addresses for reliable results with this server
  query = "What is the route from 1600 Amphitheatre Pkwy to 1165 Borregas Ave"
  print(f"User Query: '{query}'")
  content = types.Content(role='user', parts=[types.Part(text=query)])

  root_agent, exit_stack = await get_agent_async()

  runner = Runner(
      app_name='mcp_maps_app',
      agent=root_agent,
      artifact_service=artifacts_service, # Optional
      session_service=session_service,
  )

  print("Running agent...")
  events_async = runner.run_async(
      session_id=session.id, user_id=session.user_id, new_message=content
  )

  async for event in events_async:
    print(f"Event received: {event}")

  print("Closing MCP server connection...")
  await exit_stack.aclose()
  print("Cleanup complete.")

if __name__ == '__main__':
  try:
    asyncio.run(async_main())
  except Exception as e:
    print(f"An error occurred: {e}")
