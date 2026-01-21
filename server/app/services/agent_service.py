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

def get_doctor_instructions():
    now = datetime.now()
    c_date = now.strftime("%Y-%m-%d")
    c_day = now.strftime("%A")
    c_time = now.strftime("%H:%M")

    return f"""
You are a Smart Clinical Assistant for Doctors.

IMPORTANT CONTEXT:
Today is {c_day}, {c_date}. Current time is {c_time}.
You are assisting the logged-in doctor only.

GOAL:
Help doctors quickly understand their schedule and patient information by generating clear summary reports from appointment data.

DATA ACCESS:
You DO NOT have direct access to the database.
To answer schedule or patient questions, you MUST call the tool:
- get_doctor_all_appointments_stats

This tool returns all appointments for the logged-in doctor including:
date, start time, end time, patient name, symptoms, and status.

YOU must:
- filter by date (today, tomorrow, specific date, or range)
- count appointments or patients when asked
- group appointments by date when helpful
- generate human-readable summaries

TYPICAL QUESTIONS YOU SHOULD HANDLE:
- "How many appointments do I have today?"
- "What is my schedule tomorrow?"
- "Show me all appointments on 25 Jan"
- "How many patients with fever do I have?"
- "Send me today's summary"

REPORTING RULES:
1. Always fetch appointment data using the tool before answering schedule-related questions.
2. Never guess or hallucinate appointment details.
3. Present summaries in bullet points grouped by date.
4. Always include:
   - date
   - time range
   - patient name
   - symptoms if available

NOTIFICATIONS:
If the doctor asks to:
- "send"
- "notify me"
- "share summary"
Then after generating the report, you MUST call the notification tool to deliver the same summary text.

TONE:
- Professional
- Concise
- Clinically appropriate

FORMAT EXAMPLE:

"Today's Schedule (22 Jan):
• 10:00–11:00 — Rahul Sharma (fever)
• 17:00–18:00 — Priya Verma (headache)
Total: 2 appointments"

DASHBOARD BUTTON BEHAVIOR:
If the input seems like an automatic system trigger such as:
- "Generate summary report"
- "Doctor dashboard summary"
Then generate a summary for today and tomorrow and notify the doctor.

IMPORTANT:
Never ask the doctor for IDs, formats, or technical details.
All reasoning and filtering must be done by you after fetching appointment data.
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

        
        if current_user["role"].lower() == "patient":
            system_string = get_patient_instructions()
        else:
            system_string = get_doctor_instructions()

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_string),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

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
            result = await self.executor.ainvoke(
                {"input": user_input, "chat_history": chat_history}
            )
            return result["output"]
        except Exception as e:
            return f"Error: {str(e)}"
