import os
import sys
from typing import List, Dict, Any, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack

_exit_stack = AsyncExitStack()
_session: Optional[ClientSession] = None

async def get_mcp_session() -> ClientSession:
    global _session
    if _session is not None:
        return _session

    # Ensure the sub-process knows where to find the 'app' package
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() 

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp_server.server"],
        env=env # Pass the modified env
    )
    
    try:
        read, write = await _exit_stack.enter_async_context(stdio_client(server_params))
        _session = await _exit_stack.enter_async_context(ClientSession(read, write))
        await _session.initialize()
        return _session
    except Exception as e:
        # Log this to stderr so it doesn't interfere with stdio if called elsewhere
        sys.stderr.write(f"MCP Initialization Error: {e}\n")
        raise

async def list_tools_from_server() -> List[Any]:
    session = await get_mcp_session()
    response = await session.list_tools()
    return response.tools

async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]):
    session = await get_mcp_session()
    result = await session.call_tool(tool_name, arguments)
    return result.content

# This replaces your old shutdown and ensures cleanup
async def init_mcp():
    await get_mcp_session()

async def shutdown_mcp():
    global _session
    await _exit_stack.aclose()
    _session = None
    print("🛑 MCP Session Closed")