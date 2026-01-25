# Smart Doctor-Patient Assistant with MCP
=======================================

A comprehensive web application designed to facilitate seamless interaction between doctors and patients using intelligent AI agents. This project leverages a modern tech stack with **FastAPI** for the backend and **React (Vite)** for the frontend, utilizing the **Model Context Protocol (MCP)** for advanced, agentic capabilities.

## 🚀 Key Features
The purpose of this application is to bridge the gap in healthcare communication through intelligent orchestration.

-   **Model Context Protocol (MCP)**: Implements an internal MCP server (`app/mcp/server.py`) using the `mcp` Python library. This standardizes tool exposure and discovery.
-   **Agentic AI**: The AI Agent dynamically discovers tools via MCP and orchestrates complex workflows (e.g., checking availability -> booking -> notifying).
-   **Patient Assistant**: Helps patients find doctors, check availability, and book appointments (syncs with Google Calendar).
-   **Doctor Assistant**: Assists doctors in getting schedule summaries (from DB), analyzing patient data, and receiving notifications.

## 🛠 Tech Stack

### Server (Backend)
-   **Framework**: FastAPI
-   **Agent Architecture**: Model Context Protocol (MCP) using `mcp` library (FastMCP)
-   **LLM Integration**: LangChain + Groq (Llama 3.3)
-   **Database**: PostgreSQL (SQLAlchemy ORM)
-   **Tools**: Google Calendar API, Email Service

### Client (Frontend)
-   **Framework**: React 19 + Vite
-   **Styling**: TailwindCSS
-   **Chat UI**: Interactive chat interface for Agent communication.

## 📂 MCP Architecture

The project follows the MCP Client-Server model strictly:

-   **MCP Server (`app/mcp/server.py`)**:
    -   Host: Internal In-Process FastMCP Server.
    -   Tools Exposed: `list_doctors`, `check_doctor_availability`, `book_appointment_tool`, `book_google_calendar_tool`, `get_doctor_all_appointments_stats`, `send_notification_tool`.
    
-   **MCP Client (`app/services/agent_service.py`)**:
    -   The `MedicalAgent` acts as an MCP Client.
    -   It uses `mcp_server.list_tools()` to dynamically discover available capabilities.
    -   It uses `mcp_server.call_tool()` to execute actions, ensuring decoupling between the agent cognitive logic and the tool implementation.

## ⚙️ Setup & Installation

### Prerequisites
-   Node.js (v18+)
-   Python (v3.10+)
-   PostgreSQL Database running locally or cloud.

### 1. Backend Setup (`server`)
1.  Navigate to `server`:
    ```bash
    cd server
    ```
2.  Create virtual environment:
    ```bash
    python -m venv venv
    venv\Scripts\activate  # Windows
    # source venv/bin/activate # Mac/Linux
    ```
3.  Install dependencies (including `mcp`):
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure `.env` file in `server/`:
    ```env
    DATABASE_URL=postgresql://user:pass@localhost/dbname
    SECRET_KEY=your_secret_key
    GROQ_API_KEY=gsk_...
    GOOGLE_SERVICE_ACCOUNT_FILE=path/to/service_account.json
    GOOGLE_CALENDAR_ID=your_calendar_id
    EMAIL_USER=your_email
    EMAIL_PASSWORD=your_app_password
    ```
5.  Run the server:
    ```bash
    uvicorn app.main:app --reload
    ```

### 2. Frontend Setup (`client`)
1.  Navigate to `client`:
    ```bash
    cd client
    npm install
    npm run dev
    ```

## 🧩 Usage & Prompts

### Patient Flow
Login as a patient and try:
-   "I want to book an appointment with Dr. Ahuja tomorrow morning."
-   "Is Dr. Smith available on Friday?" -> "Book the 3 PM slot."

### Doctor Flow
Login as a doctor and try:
-   "How many patients do I have today?"
-   "Generate a summary report for tomorrow."

## 📦 Deliverables Checklist
- [x] MCP-compliant tool definitions (FastMCP).
- [x] LLM-triggered tool invocation via MCP.
- [x] Multi-turn conversation handling.
- [x] Full-stack interop (FastAPI <-> React).
