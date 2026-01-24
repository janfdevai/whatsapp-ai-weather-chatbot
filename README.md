# 🤖 WhatsApp AI Chatbot

A production-ready, AI-powered WhatsApp chatbot built with **FastAPI**, **LangGraph**, and **LangChain**. This project demonstrates a robust integration of LLMs with the WhatsApp Business API, utilizing background tasks to ensure high performance and reliability.

---

## 🚀 Key Features

- **Asynchronous Architecture**: Leverages FastAPI's `BackgroundTasks` to handle incoming webhooks instantly, avoiding Meta's strict 3-second timeout.
- **Stateful AI Agent**: Uses **LangGraph** to manage conversation state, including user profiles (name, phone number) and message history.
- **Meta Webhook Integration**: Full support for WhatsApp Cloud API webhooks, including automated verification and message status updates (marking as read).
- **LangSmith Tracing**: Integrated observability for debugging and monitoring agent performance.
- **Easy Deployment**: Uses `uv` for lightning-fast dependency management and environment setup.

## 🛠️ Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)
- **Orchestration**: [LangGraph](https://langchain-ai.github.io/langgraph/)
- **LLM Framework**: [LangChain](https://www.langchain.com/)
- **Database (Memory)**: In-memory Checkpointer (Easily swappable to Postgres/Redis)
- **API Communication**: `httpx` for asynchronous HTTP requests
- **Dependency Management**: [uv](https://docs.astral.sh/uv/)

## 📂 Project Structure

```text
whatsapp-ai-chatbot/
├── app/
│   ├── agents/              # AI Agent logic and graph definitions
│   │   ├── chatbot_agent/   # Modular chatbot implementation
│   │   │   ├── graph.py     # LangGraph workflow definition
│   │   │   ├── nodes.py     # Graph nodes (LLM calls, tools)
│   │   │   ├── state.py     # State schemas (Messages, UserProfile)
│   │   │   ├── tools.py     # Custom tools for the agent
│   │   │   └── utils.py     # Helper functions
│   │   └── team.py          # Agent compilation and memory setup
│   ├── chanels/             # Communication channels (e.g., WhatsApp)
│   │   └── whatsapp.py      # Meta API integration and webhook logic
│   └── main.py              # FastAPI application entry point
├── .env                     # Environment variables
├── pyproject.toml           # Project dependencies
└── README.md                # You are here!
```

---

## 🏁 Getting Started

### 1. Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) installed.
- A Meta Developer account with a WhatsApp App configured.
- [ngrok](https://ngrok.com/) for local tunneling.

### 2. Installation

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd whatsapp-ai-chatbot
uv sync
```

### 3. Configuration

Create a `.env` file in the root directory and fill in your credentials:

```env
# Meta / WhatsApp Configuration
VERIFY_TOKEN=your_secure_verify_token
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
PHONE_NUMBER_ID=your_phone_number_id
GRAPH_API_VERSION=v22.0

# AI Configuration
OPENAI_API_KEY=your_openai_api_key

# Optional: LangSmith Tracing
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=whatsapp-ai-chatbot
```

### 4. Run the Application

Start the development server:

```bash
uv run fastapi dev app/main.py
```

The server will be available at `http://127.0.0.1:8000`.

---

## 🔗 Connecting to Meta

1. **Tunnel your local server**:
   Use [ngrok](https://dashboard.ngrok.com/get-started/setup) to expose your local FastAPI server to the internet.
   ```bash
   ngrok http 8000
   ```

2. **Configure the Webhook in Meta Dashboard**:
   Follow the official guides to set up your webhook:
   - 📖 [Meta Webhook Configuration Guide](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started#configure-webhooks)
   - 📺 [Meta Webhook Configuration (Video Tutorial)](https://www.youtube.com/watch?v=8hKEbOHWyQk)

   **Settings**:
   - **Callback URL**: `https://<your-ngrok-id>.ngrok-free.app/webhook`
   - **Verify Token**: The `VERIFY_TOKEN` you defined in your `.env`.
   - **Webhook Fields**: Ensure you are subscribed to `messages`.

3. **Message your Bot**: 
   Send a message to the test WhatsApp number associated with your app. The bot should reply using the **LangGraph** chat agent!

---

## 🛡️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.