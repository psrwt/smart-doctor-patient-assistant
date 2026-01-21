import os
from datetime import datetime
from typing import List, Dict

from langchain_groq import ChatGroq
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage, AIMessage

from app.mcp.registry import MCPToolRegistry

def get_patient_instructions():
    now = datetime.now()
    c_date = now.strftime("%Y-%m-%d")
    c_day = now.strftime("%A")
    c_time = now.strftime("%H:%M")

    return f"""
You are a Smart Medical Assistant.

IMPORTANT CONTEXT: Today is {c_day}, {c_date}. Current time is {c_time}.

GOAL: Help patients book appointments smoothly, including adding them to Google Calendar. Do NOT ask the user for technical formats.

BOOKING LOGIC:
1. If a user says 'today', 'tomorrow', or 'next Friday', convert this to a proper YYYY-MM-DD date yourself.
2. If a user says '11 AM', convert this to '11:00' in 24-hour format.
3. NEVER ask the user to provide a date or time in a specific format. This is your responsibility.
4. If you have the doctor name, date, and time, you MUST first confirm these details with the patient and then you MUST:
   a) Call the `book_appointment` tool to save the appointment in the database.
   b) Call the `book_google_calendar` tool to create the event in Google Calendar.

CONVERSATION EXAMPLES:
- User: "Book appointment with Dr. Ahuja tomorrow at 3 PM"
- Assistant: (Internally calculates date & time) -> Calls `book_appointment` and `book_google_calendar` -> Responds:
    "✅ Appointment booked with Dr. Ahuja on 2026-01-22 at 15:00."

RULES:
- If the user says "yes" or "book it" for a suggested slot, use the details from the previous conversation to call both tools.
- Always respond in **friendly, plain language**.
- NEVER show raw dates/times to the user; always format nicely (e.g., "3 PM on 22 Jan 2026").
- If either tool fails, explain the error clearly to the user and suggest alternatives.
"""


class MedicalAgent:
    def __init__(self, db, current_user):
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.3-70b-versatile",
            temperature=0.2,
        )

        self.registry = MCPToolRegistry(db)
        self.tools: List[BaseTool] = self.registry.get_tools(current_user)

        # 1. Get the string with the date already inserted
        if current_user["role"].lower() == "patient":
            system_string = get_patient_instructions()
        else:
            system_string = "You are a professional assistant for doctors. Summarize their schedule clearly."

        # 2. Build the prompt. 
        # Since we used an f-string above, system_string is now just a plain string 
        # with no '{current_date}' variables left inside it.
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_string),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt,
        )

        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
        )

    async def run(self, user_input: str, history: List[Dict[str, str]] = []) -> str:
        chat_history = []
        for msg in history:
            if msg["role"] == "user":
                chat_history.append(HumanMessage(content=msg["content"]))
            else:
                chat_history.append(AIMessage(content=msg["content"]))

        try:
            # Now we only pass 'input' and 'chat_history'. 
            # 'agent_scratchpad' is handled automatically by the agent.
            result = await self.executor.ainvoke({
                "input": user_input,
                "chat_history": chat_history
            })
            return result["output"]
        except Exception as e:
            return f"Error: {str(e)}"