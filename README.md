# Smart Doctor-Patient Assistant

A comprehensive web application designed to facilitate seamless interaction between doctors and patients using intelligent AI agents. This project leverages a modern tech stack with **FastAPI** for the backend and **React (Vite)** for the frontend, featuring **Model Context Protocol (MCP)** for advanced agentic capabilities.

## 🚀 About the Project

The purpose of this application is to bridge the gap in healthcare communication. It features dedicated intelligent assistants for both doctors and patients:

-   **Patient Assistant**: Helps patients book appointments, manage schedules, and get basic information.
-   **Doctor Assistant**: Assists doctors in managing their appointments, summarizing schedules, and accessing patient data.

Key integrations include **Google Calendar** for scheduling and **Email Services** for notifications.

## 🛠 Tech Stack

### Client (Frontend)
-   **Framework**: React 19
-   **Build Tool**: Vite
-   **Styling**: TailwindCSS 4
-   **Routing**: React Router DOM 7
-   **HTTP Client**: Axios

### Server (Backend)
-   **Framework**: FastAPI
-   **Database**: PostgreSQL (SQLAlchemy ORM)
-   **AI/Agents**: Model Context Protocol (MCP) dependencies
-   **Authentication**: JWT-based auth

## 📂 Modular Structure

The project is divided into two main directories: `client` and `server`.

### Server (`/server`)
The backend is structured for scalability and separation of concerns:

-   **`app/routes/`**: Defines the API endpoints (e.g., `auth`, `chat`).
-   **`app/services/`**: Contains core business logic and external integrations:
    -   `agent_service.py`: Orchestrates AI agent interactions.
    -   `google_calendar_service.py`: Handles calendar events.
    -   `email_service.py`: Manages email notifications.
    -   `auth_service.py`: Handles user authentication.
-   **`app/mcp/`**: Implements the Model Context Protocol for AI agents:
    -   `tools/`: specific tools for `patient_tools.py` and `doctor_tools.py`.
    -   `registry.py`: Registers tools for the agents.
-   **`app/db/`**: Database configuration and SQLAlchemy models.

### Client (`/client`)
The frontend follows a modern React structure:

-   **`src/pages/`**: Application views/routes.
-   **`src/components/`**: Reusable UI components.
-   **`src/context/`**: Global state management.
-   **`src/assets/`**: Static assets like images.

## ⚙️ Setup & Installation

### Prerequisites
-   Node.js (v18+ recommended)
-   Python (v3.10+)
-   PostgreSQL Database

### 1. Database Setup
Ensure you have a PostgreSQL database running. You will need the credentials (User, Password, Host, DB Name) for the backend configuration.

### 2. Backend Setup (`server`)

1.  Navigate to the server directory:
    ```bash
    cd server
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure Environment Variables:
    -   Create a `.env` file in the `server` root.
    -   Add necessary variables (e.g., `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_NAME`, `SECRET_KEY`, Google API credentials, etc.).
5.  Run the server:
    ```bash
    uvicorn app.main:app --reload
    ```
    The API will be available at `http://localhost:8000`.

### 3. Frontend Setup (`client`)

1.  Navigate to the client directory:
    ```bash
    cd client
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```
    The application will be accessible at `http://localhost:5173`.


