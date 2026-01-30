import sys
from typing import List, Dict, Any
# We import the actual MCP server instance directly to call its tools
from app.mcp_server.server import mcp 

async def list_tools_from_server() -> List[Any]:
    """
    Returns tools directly from the FastMCP instance registry.
    This bypasses the need for a background subprocess on Vercel.
    """
    try:
        # FastMCP keeps tools in its internal manager
        tools = []
        for tool_name, tool_obj in mcp._tool_manager.list_tools():
            tools.append(tool_obj)
        return tools
    except Exception as e:
        sys.stderr.write(f"Error listing tools: {e}\n")
        return []

async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]):
    """
    Calls the tool function directly using the FastMCP call_tool method.
    """
    try:
        # This executes the function mapped to the tool name directly
        result = await mcp.call_tool(tool_name, arguments)
        return result
    except Exception as e:
        sys.stderr.write(f"Error calling tool {tool_name}: {e}\n")
        raise

async def init_mcp():
    """No subprocess to start, just a confirmation log."""
    print("✅ MCP Tools initialized In-Process")

async def shutdown_mcp():
    """No subprocess to kill."""
    print("🛑 MCP Session Closed")