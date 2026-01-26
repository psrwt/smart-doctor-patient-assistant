# Smart Doctor-Patient Assistant (MCP Architecture) 🏥🤖

A state-of-the-art, AI-powered healthcare orchestration system built on the **Model Context Protocol (MCP)**. This application facilitates seamless communication between patients and doctors, leveraging intelligent agents to manage appointments, clinical reports, and notifications.

---

## 🏗️ Modern MCP Architecture

### 1. MCP Server (`server/app/mcp_server`)
Built with **FastMCP**, the server acts as the source of truth for all "capabilities" (tools). It runs as a background process communicating over `stdio` transport.
*   **Dynamic Tool Exposure:** All medical logic is encapsulated as MCP tools.
*   **Database Isolation:** Only the MCP server interacts directly with the database for tool execution.

### 2. MCP Client & Medical Agent (`server/app/services/agent`)
The FastAPI backend hosts the **MCP Client** which:
*   **Connects on Startup:** Establishes a session with the internal MCP server.
*   **Dynamic Discovery:** The LLM (Llama 3.3 via Groq) retrieves tool definitions at runtime via MCP protocol.
*   **Secure Execution:** The Agent never touches the DB directly; it requests tool execution from the MCP Server.

---

## 🚀 Key Features

### 🩺 For Patients
-   **Intelligent Doctor Search:** Find doctors by name or specialty.
-   **Smart Appointment Booking:** Real-time checking of available slots and instant booking.
-   **Calendar Integration:** Automatic synchronization with Google Calendar.

### 🧑‍⚕️ For Doctors
-   **Schedule Summarization:** Get daily or weekly appointment breakdowns powered by AI.
-   **Clinical Symptom Search:** Search through patient history using keyword matching (e.g., "how many patients had fever?").
-   **Slack Notifications:** Instantly push schedule summaries or patient reports to Slack.

---

## 🛠️ Tech Stack

### Backend (Python/FastAPI)
-   **Core:** FastAPI (High-performance web framework).
-   **Intelligence:** Groq (Llama-3.3-70b-Versatile).
-   **Protocol:** [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) via `mcp` & `fastmcp`.
-   **Database:** PostgreSQL with SQLAlchemy ORM.

### Frontend (React/Vite)
-   **UI/UX:** React 19 + TailwindCSS.
-   **Communication:** Real-time AI chat interface.

### Integrations
-   **Google Calendar API:** For automated appointment scheduling.
-   **Slack API:** For doctor-side notifications.

---

## 📂 Project Structure

```text
smart-doctor-patient-assistant/
├── client/                     # React Frontend (Vite)
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   │   ├── ChatBox.jsx     # Main AI chat interface
│   │   │   ├── LoginForm.jsx   # Authentication components
│   │   │   └── ...
│   │   ├── pages/              # Main application views
│   │   │   ├── Auth.jsx        # Unified Login/Signup page
│   │   │   ├── DoctorDashboard.jsx
│   │   │   └── PatientDashboard.jsx
│   │   ├── context/            # Global state (AuthContext)
│   │   └── App.jsx             # Root component & Routing
├── server/                     # FastAPI Backend
│   ├── app/
│   │   ├── mcp_server/         # 🚀 MCP Server Implementation
│   │   │   ├── tools/          # Modular Tool definitions
│   │   │   │   ├── book_appointment.py
│   │   │   │   ├── notify_on_slack.py
│   │   │   │   └── ... (7+ Specialized Tools)
│   │   │   └── server.py       # FastMCP server entry point (Stdio Transport)
│   │   ├── services/           # Backend business logic
│   │   │   ├── agent/          # MCP Client & LLM Orchestration
│   │   │   │   ├── agent.py    # LangChain/Groq Agent logic
│   │   │   │   └── mcp_client.py # MCP Protocol lifecycle
│   │   │   ├── auth_service.py # Security & JWT management
│   │   │   └── ...             # Calendar & Email integrations
│   │   ├── routes/             # FastAPI HTTP endpoints (Chat, Auth)
│   │   ├── db/                 # PostgreSQL Models & Session
│   │   └── main.py             # FastAPI App & Lifecycle hooks
└── ...
```

---

## ⚙️ Setup & Installation

### 1. Server Setup
1.  Navigate to `server/` and create a virtual environment.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Configure your `.env` with:
    -   `DATABASE_URL`
    -   `GROQ_API_KEY`
    -   `GOOGLE_APPLICATION_CREDENTIALS` (JSON path)
    -   `SLACK_BOT_TOKEN` & `SLACK_CHANNEL_ID`

4.  Start the FastAPI server:
    ```bash
    uvicorn app.main:app --reload
    ```
    *(Note: The MCP Server is automatically managed/started by the FastAPI lifecycle)*

### 2. Client Setup
1.  Navigate to `client/`.
2.  Install & Run:
    ```bash
    npm install
    npm run dev
    ```

---

## 🛡️ Usage Scenarios

### Patient Prompt Example:
> *"Find Dr. Ahuja and check if he has any slots open tomorrow afternoon. If yes, book a 2 PM slot for me for my persistent cough."*

### Doctor Prompt Example:
> *"Give me a summary of all appointments for today and push it to my Slack."*
> *"How many patients mentioned 'fever' in their symptoms this month?"*

