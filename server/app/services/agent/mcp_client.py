import sys
from typing import List, Dict, Any
from app.mcp_server.server import mcp


async def list_tools_from_server() -> List[Any]:
    """
    Correct way to get tools from a FastMCP instance.
    """
    try:
        if hasattr(mcp, "_tool_manager"):
            tm = mcp._tool_manager
            if hasattr(tm, "get_tools"):
                tools_dict = await tm.get_tools()
                if isinstance(tools_dict, dict):
                    return list(tools_dict.values())
            if hasattr(tm, "_tools"):
                return list(tm._tools.values())

            if hasattr(tm, "tools"):
                obj = tm.tools
                return list(obj.values()) if isinstance(obj, dict) else obj
        if hasattr(mcp, "_tools"):
            return list(mcp._tools.values())

        if hasattr(mcp, "list_tools"):
            # Check if it's async
            import inspect

            if inspect.iscoroutinefunction(mcp.list_tools):
                return await mcp.list_tools()
            return mcp.list_tools()

        return []
    except Exception as e:
        sys.stderr.write(f"❌ Critical Tool Listing Error: {e}\n")
        return []


async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]):
    """
    Direct call to FastMCP tool execution.
    """
    try:
        # FastMCP 2.x stores tools and their execution logic in _tool_manager
        if hasattr(mcp, "_tool_manager"):
            tm = mcp._tool_manager
            if hasattr(tm, "call_tool"):
                return await tm.call_tool(tool_name, arguments)

        # Fallback for other versions
        if hasattr(mcp, "call_tool"):
            return await mcp.call_tool(tool_name, arguments)

        if hasattr(mcp, "_call_tool"):
            return await mcp._call_tool(tool_name, arguments)

        raise AttributeError(f"MCP instance has no method to call tool '{tool_name}'")
    except Exception as e:
        sys.stderr.write(f"❌ Error calling tool {tool_name}: {e}\n")
        raise


async def init_mcp():
    """Lifecycle hook for FastAPI startup"""
    print("✅ MCP Tools initialized In-Process")


async def shutdown_mcp():
    """Lifecycle hook for FastAPI shutdown"""
    print("🛑 MCP Session Closed")
