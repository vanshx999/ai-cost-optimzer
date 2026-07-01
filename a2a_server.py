#!/usr/bin/env python3
"""
A2A Server Skeleton for AI Cost Optimizer — Day 28 (Fixed)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime, timezone
import uuid

app = FastAPI(title="AI Cost Optimizer A2A Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory task store (use Redis/DB in production)
tasks = {}

AGENT_CARD = {
    "name": "AI Cost Optimizer Agent",
    "description": "Analyzes AI API spending, cache efficiency, and request patterns from PostgreSQL logs",
    "version": "1.0.0",
    "protocolVersion": "1.0",
    "url": "http://localhost:8080",
    "capabilities": {
        "streaming": False,
        "pushNotifications": False,
        "stateTransitionHistory": True
    },
    "defaultInputModes": ["text/plain"],
    "defaultOutputModes": ["text/plain"],
    "skills": [
        {
            "id": "cost-analysis",
            "name": "AI Cost Analysis",
            "description": "Returns total API costs, per-model breakdown, and spending trends",
            "tags": ["cost", "analytics", "llm", "optimization"],
            "examples": ["How much did I spend on Groq this week?", "Show me my most expensive model"]
        },
        {
            "id": "cache-analysis",
            "name": "Cache Efficiency Analysis",
            "description": "Calculates cache hit rate and recommends improvements",
            "tags": ["cache", "performance", "optimization"],
            "examples": ["Is my caching actually saving money?", "What's my cache hit rate?"]
        },
        {
            "id": "log-query",
            "name": "Request Log Query",
            "description": "Returns recent API request logs with filtering",
            "tags": ["logs", "history", "requests"],
            "examples": ["Show my last 10 requests", "What did I ask yesterday?"]
        }
    ]
}

class SendMessageRequest(BaseModel):
    message: str = Field(description="The user's question or task")
    sessionId: str | None = Field(default=None, description="Optional session ID")

class TaskStatus(BaseModel):
    id: str
    status: Literal["submitted", "working", "completed", "failed", "canceled"]
    message: str | None = None
    result: str | None = None
    createdAt: str
    updatedAt: str

def now_iso():
    """Safe ISO timestamp for Python 3.14"""
    return datetime.now(timezone.utc).isoformat()

@app.get("/.well-known/agent-card.json")
def get_agent_card():
    return AGENT_CARD

@app.post("/message:send", response_model=TaskStatus)
def send_message(request: SendMessageRequest):
    try:
        task_id = str(uuid.uuid4())
        now = now_iso()
        
        # Create task
        task = {
            "id": task_id,
            "status": "submitted",
            "message": request.message,
            "result": None,
            "createdAt": now,
            "updatedAt": now
        }
        tasks[task_id] = task
        
        # Simulate processing
        task["status"] = "working"
        task["updatedAt"] = now_iso()
        
        # Route based on message content
        msg = request.message.lower()
        if any(w in msg for w in ["cost", "spend", "money", "price"]):
            task["result"] = (
                "Total Requests: 47\n"
                "Total Cost: $0.005832\n"
                "Breakdown by Model:\n"
                "  - llama3-8b-8192: $0.005832 (47 requests)"
            )
        elif any(w in msg for w in ["cache", "hit rate", "efficiency"]):
            task["result"] = "Cache Hit Rate: 25.53% (12/47 cached)"
        elif any(w in msg for w in ["log", "request", "recent", "history"]):
            task["result"] = "Recent logs: 10 entries found [simulated]"
        else:
            task["result"] = "I can analyze costs, cache, or logs. What would you like?"
        
        task["status"] = "completed"
        task["updatedAt"] = now_iso()
        
        return TaskStatus(**task)
        
    except Exception as e:
        # Log the real error so we can see it in the server terminal
        print(f"ERROR in /message:send: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStatus(**task)

@app.get("/health")
def health():
    return {"status": "ok", "agent": "ai-cost-optimizer", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)