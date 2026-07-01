# AI Cost Optimizer

Monitor, analyze, and optimize your LLM API spending. A full-stack application with a **FastAPI** backend and **React + Tailwind CSS** dashboard.

## Architecture

```
ai-cost-optimizer/
├── main.py              # FastAPI server (REST endpoints)
├── router.py            # LangGraph-based intent classification
├── mcp_server.py        # MCP server for AI agent integration
├── a2a_server.py        # A2A agent protocol server
├── model.py             # SQLAlchemy models
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container build
├── docker-compose.yml   # Local dev with PostgreSQL
├── frontend/            # React dashboard (Vite + Tailwind)
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── api.js              # Axios client
│   │   │   ├── StatsCards.jsx
│   │   │   ├── CostChart.jsx       # Recharts bar chart
│   │   │   ├── RecentRequestsTable.jsx
│   │   │   └── StatusIndicator.jsx
│   │   └── ...
│   └── ...
└── ...
```

## Features

- **LLM Question Answering** — Ask questions via `/ask` endpoint, powered by Groq
- **Cost Tracking** — Per-request cost calculation based on token usage
- **Caching** — In-memory cache with TTL to reduce duplicate LLM calls
- **Analytics Dashboard** — Real-time metrics: total requests, cost breakdown, cache hit rate
- **Intent Classification** — LangGraph router that classifies questions into cost/logs/cache intents
- **MCP & A2A Support** — Agent interoperability protocols for AI tool integration

## Quick Start (Local)

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (or Docker for containerized DB)

### Backend

```bash
# Clone and enter the backend directory
cd ai-cost-optimizer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY=gsk_your_key_here
export DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_costs

# Start the server
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

### Docker (Alternative)

```bash
GROQ_API_KEY=gsk_your_key_here docker compose up --build
```

## API Endpoints

| Method | Path         | Auth Required | Description                     |
|--------|--------------|---------------|---------------------------------|
| GET    | `/health`    | No            | Health check                    |
| POST   | `/ask`       | Yes           | Ask a question to the LLM       |
| GET    | `/stats`     | Yes           | Get cost and usage statistics   |

**Headers for auth-protected endpoints:**
```
x-api-key: sk-vansh-abc123
```

### Example: Ask a question

```bash
curl -X POST http://localhost:8000/ask \
  -H "x-api-key: sk-vansh-abc123" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the capital of France?"}'
```

### Example: Get stats

```bash
curl http://localhost:8000/stats \
  -H "x-api-key: sk-vansh-abc123"
```

## Deployment

### Backend → Render

1. Push the repo to GitHub
2. On Render, create a **Web Service**
3. Connect your GitHub repo
4. Set:
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `GROQ_API_KEY`
   - `DATABASE_URL`
6. Deploy

### Frontend → Vercel

1. Push the repo to GitHub
2. On Vercel, **Add New Project**
3. Import the repo, set **Root Directory** to `frontend`
4. Vercel auto-detects Vite — no config needed
5. Add environment variable:
   - `VITE_API_URL` = your Render backend URL
6. Deploy

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | Python, FastAPI, SQLAlchemy         |
| LLM        | Groq (llama-3.3-70b-versatile)      |
| Routing    | LangGraph                           |
| Frontend   | React, Vite, Tailwind CSS           |
| Charts     | Recharts                            |
| HTTP       | Axios                               |
| Database   | PostgreSQL                          |
| Containers | Docker, Docker Compose              |
