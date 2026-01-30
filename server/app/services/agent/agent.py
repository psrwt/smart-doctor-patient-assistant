import os
import json
from groq import Groq
from app.services.agent.mcp_client import list_tools_from_server, call_mcp_tool
from app.services.agent.prompts import DOCTOR_PROMPT, PATIENT_PROMPT
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone, timedelta

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def map_mcp_to_groq_tool(mcp_tool: Any) -> Dict[str, Any]:
    """
    Converts a FastMCP tool object into the Groq/OpenAI function calling format.
    """
    name = getattr(mcp_tool, "name", "unknown")
    description = getattr(mcp_tool, "description", "")
    # FastMCP uses '.parameters' for the JSON schema
    parameters = getattr(mcp_tool, "parameters", {"type": "object", "properties": {}})

    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters,
        },
    }


async def run_agent_chat(
    user_message: str,
    history: List[Dict[str, str]],
    current_user: Dict[str, Any],
    user_info: Optional[Dict[str, Any]],
):
    # 1. Identity & Time Extraction
    user_id = current_user.get("id")
    user_role = current_user.get("role")
    user_name = user_info.get("user_name", "User") if user_info else "User"

    ist_tz = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(ist_tz)
    current_time = now_ist.strftime("%A, %Y-%m-%d %H:%M:%S")

    DOCTOR_TOOLS = [
        "get_doctor_appointments_by_date_range",
        "search_appointments_by_symptom_keyword",
        "send_summary_report_to_slack",
    ]
    PATIENT_TOOLS = [
        "get_doctors",
        "find_doctor",
        "get_available_slots",
        "book_new_appointment",
    ]

    tools_filter = DOCTOR_TOOLS if user_role == "doctor" else PATIENT_TOOLS
    base_prompt = DOCTOR_PROMPT if user_role == "doctor" else PATIENT_PROMPT
    identity_context = f"{user_role.upper()} IDENTITY: ID={user_id}, Name={user_name}"

    full_system_instruction = (
        f"{base_prompt}\n\n"
        f"CURRENT_TIME_CONTEXT: The current time in IST is {current_time}.\n"
        f"{identity_context}\n"
    )

    # 2. Fetch and Map Tools
    mcp_tools_raw = await list_tools_from_server()
    available_tools = [
        map_mcp_to_groq_tool(tool)
        for tool in mcp_tools_raw
        if tool.name in tools_filter
    ]

    # 3. Prepare Conversation History
    messages = [{"role": "system", "content": full_system_instruction}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    # 4. LLM Interaction Loop
    max_iterations = 5
    response_text = ""

    for i in range(max_iterations):
        tool_params = (
            {"tools": available_tools, "tool_choice": "auto"} if available_tools else {}
        )

        response = client.chat.completions.create(
            model=MODEL, messages=messages, temperature=0.1, **tool_params
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if response_message.content:
            response_text = response_message.content

        if not tool_calls:
            break

        # Assistant message must be added to history before tool results
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            args_str = tool_call.function.arguments or "{}"
            function_args = json.loads(args_str)
            if not isinstance(function_args, dict):
                function_args = {}

            try:
                print(f"🛠️ Tool calling: {function_name}")
                mcp_result = await call_mcp_tool(function_name, function_args)

                # Extract text from FastMCP result content list
                if hasattr(mcp_result, "content"):
                    readable_result = "".join(
                        [
                            c.text if hasattr(c, "text") else str(c)
                            for c in mcp_result.content
                        ]
                    )
                else:
                    readable_result = json.dumps(mcp_result)

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": readable_result,
                    }
                )
            except Exception as e:
                print(f"❌ Tool Error: {e}")
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": f"Error: {str(e)}",
                    }
                )

    return {"answer": response_text}
