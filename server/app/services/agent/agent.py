import os
from app.services.agent.mcp_client import list_tools_from_server, call_mcp_tool
from app.services.agent.prompts import DOCTOR_PROMPT, PATIENT_PROMPT
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone, timedelta
from google import genai
from google.genai import types

# Configure Gemini
# Initialize the New SDK Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def mcp_to_gemini_tool(mcp_tool):
    """
    Converts a standard MCP tool definition into a Gemini-compatible 
    Function Declaration.
    """
    return types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name=mcp_tool.name,
                description=mcp_tool.description,
                parameters=mcp_tool.inputSchema
            )
        ]
    )

def transform_history(history: List[Dict[str, str]]):
    """
    Converts standard chat history (role/content) 
    to Gemini's required format (role/parts).
    """
    transformed = []
    for entry in history:
        role = "user" if entry["role"] == "user" else "model"
        transformed.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=entry["content"])]
            )
        )
    return transformed

async def run_agent_chat(
    user_message: str, 
    history: List[Dict[str, str]],
    current_user: Dict[str, str],
    user_info: Optional[Dict[str, Any]]
    ):
    """
    Main entry point for the chat.
    1. Fetches tools from MCP.
    2. Sends message to Gemini.
    3. Handles Gemini's request to call tools.
    """
    
    # 1. Identity Extraction
    user_id = current_user.get("id")
    user_role = current_user.get("role")
    user_name = user_info.get("user_name", "User") if user_info else "User"

    # --- IST Time Calculation ---
    ist_tz = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(ist_tz)
    current_time = now_ist.strftime("%A, %Y-%m-%d %H:%M:%S")

    DOCTOR_TOOLS = ["get_doctor_appointments_by_date_range", "search_appointments_by_symptom_keyword", "send_summary_report_to_slack"]
    PATIENT_TOOLS = ["get_doctors", "find_doctor", "get_available_slots", "book_new_appointment"]

    # 2. Select Role-Based Prompt and Identity Context
    if user_role == "doctor":
        base_prompt = DOCTOR_PROMPT
        identity_context = f"DOCTOR IDENTITY: ID={user_id}, Name={user_name}"
        tools = DOCTOR_TOOLS  
    else:
        base_prompt = PATIENT_PROMPT
        identity_context = f"PATIENT IDENTITY: ID={user_id}, Name={user_name}"
        tools = PATIENT_TOOLS

    full_system_instruction = (
        f"{base_prompt}\n\n"
        f"CURRENT_TIME_CONTEXT: The current time in IST is {current_time}.\n"
        f"{identity_context}"
    )

    print("full_system_instruction", full_system_instruction)

    # 1. Fetch available tools from MCP Server
    mcp_tools_raw = await list_tools_from_server()

    # 2. Map all MCP tools to Gemini format
    gemini_tools = [
        mcp_to_gemini_tool(t) 
        for t in mcp_tools_raw 
        if t.name in tools
    ]

     
    # 3. Initialize Model WITH tools passed in
    config = types.GenerateContentConfig(
        system_instruction=full_system_instruction,
        tools=gemini_tools,
        thinking_config=types.ThinkingConfig(include_thoughts=True, thinking_level="medium"),
        temperature=0.1 # Lower temperature for better tool accuracy
    )

    gemini_history = transform_history(history)

    # In Gemini 3, we create a chat session directly from the client
    chat = client.chats.create(
        model="gemini-3-flash-preview",
        config=config,
        history=gemini_history
    )

    # 5. First call to Gemini with the user message
    response = chat.send_message(user_message)

    # Gemini 3 might call multiple tools in one go (parallel tool use)
    while response.function_calls:
        tool_responses = []
        for call in response.function_calls:
            # Execute MCP Tool
            result = await call_mcp_tool(call.name, call.args)
            
            # Create a response part for this tool
            tool_responses.append(
                types.Part.from_function_response(
                    name=call.name,
                    response={'result': result}
                )
            )
        
        # Feed all tool results back to the model
        response = chat.send_message(tool_responses)

    return {
        "answer": response.text,
        # "history": [h.to_dict() for h in chat.history] 
    }