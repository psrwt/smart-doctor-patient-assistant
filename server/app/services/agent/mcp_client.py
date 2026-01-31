import sys
from typing import List, Dict, Any
from app.mcp_server.server import mcp


async def list_tools_from_server() -> List[Any]:
    """
    to get tools from a FastMCP instance
    """
    try:
        tools_dict = await mcp._tool_manager.get_tools()
        return list(tools_dict.values())
    except Exception as e:
        sys.stderr.write(f"❌ Tool Listing Error: {e}\n")
        return []


async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]):
    """
    Direct call to FastMCP tool execution.
    """
    try:
        return await mcp._tool_manager.call_tool(tool_name, arguments)
    except Exception as e:
        sys.stderr.write(f"❌ Error calling tool {tool_name}: {e}\n")
        raise


async def init_mcp():
    """Lifecycle hook for FastAPI startup"""
    print("✅ MCP Tools initialized In-Process")


async def shutdown_mcp():
    """Lifecycle hook for FastAPI shutdown"""
    print("🛑 MCP Session Closed")
