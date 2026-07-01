import os
import time
import hashlib
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, func
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

app = FastAPI(title="AI Cost Optimizer")

# ============ CORS ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ DATABASE (PostgreSQL) ============
DATABASE_URL = "postgresql://localhost:5432/ai_costs"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class RequestLog(Base):
    __tablename__ = "request_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    model = Column(String, nullable=False, index=True)
    tokens_in = Column(Integer, default=0)
    tokens_out = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    cached = Column(Boolean, default=False)
    latency_ms = Column(Integer, nullable=True)

# ============ AUTH ============
API_KEYS = {
    "sk-vansh-abc123": {"user_id": "vansh", "tier": "free"},
    "sk-friend-def456": {"user_id": "friend", "tier": "paid"},
}

def get_user_from_key(api_key: str):
    return API_KEYS.get(api_key)

# ============ LLM SETUP ============
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_llm():
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.0,
        groq_api_key=GROQ_API_KEY
    )

# ============ PRICING ============
MODEL_PRICING = {
    "llama-3.3-70b-versatile": {"input": 0.0001, "output": 0.0002},  # per 1K tokens
    "gpt-4": {"input": 0.03, "output": 0.06},
}

def calculate_cost(model: str, tokens_in: int, tokens_out: int):
    pricing = MODEL_PRICING.get(model, {"input": 0, "output": 0})
    cost = (tokens_in / 1000 * pricing["input"]) + (tokens_out / 1000 * pricing["output"])
    return round(cost, 6)

# ============ CACHE ============
response_cache = {}
CACHE_TTL = 3600

def get_cache_key(question: str, model: str, user_id: str):
    return hashlib.sha256(f"{user_id}:{question}:{model}".encode()).hexdigest()

def get_cached_answer(cache_key: str):
    if cache_key not in response_cache:
        return None
    entry = response_cache[cache_key]
    if time.time() - entry["timestamp"] > CACHE_TTL:
        del response_cache[cache_key]
        return None
    return entry["answer"]

def set_cached_answer(cache_key: str, answer: str):
    response_cache[cache_key] = {"answer": answer, "timestamp": time.time()}

# ============ API MODELS ============
class Question(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str
    cost: float
    cached: bool
    latency_ms: int

# ============ LOGGING FUNCTION ============
def log_request(user_id: str, model: str, tokens_in: int, tokens_out: int, 
                cost: float, cached: bool, latency_ms: int):
    """Write one row to PostgreSQL."""
    session = Session()
    log = RequestLog(
        user_id=user_id,
        model=model,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost=cost,
        cached=cached,
        latency_ms=latency_ms
    )
    session.add(log)
    session.commit()
    session.close()

# ============ ENDPOINT ============
@app.post("/ask", response_model=Answer)
def ask(q: Question, x_api_key: str = Header(...)):
    start_time = time.time()
    
    # Auth
    user = get_user_from_key(x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Cache check
    model = "llama3-8b-8192"
    cache_key = get_cache_key(q.question, model, user["user_id"])
    cached = get_cached_answer(cache_key)
    
    if cached:
        latency_ms = int((time.time() - start_time) * 1000)
        log_request(user["user_id"], model, 0, 0, 0.0, True, latency_ms)
        return Answer(answer=cached, cost=0.0, cached=True, latency_ms=latency_ms)
    
    # LLM Call (real Groq call)
    prompt = ChatPromptTemplate.from_template("Answer briefly: {question}")
    chain = prompt | get_llm() | StrOutputParser()
    answer = chain.invoke({"question": q.question})
    
    # Simulate token counts (Groq returns usage in response)
    tokens_in = len(q.question.split()) * 2  # Rough estimate
    tokens_out = len(answer.split()) * 2      # Rough estimate
    
    # Calculate cost
    cost = calculate_cost(model, tokens_in, tokens_out)
    
    # Cache it
    set_cached_answer(cache_key, answer)
    
    # Log it
    latency_ms = int((time.time() - start_time) * 1000)
    log_request(user["user_id"], model, tokens_in, tokens_out, cost, False, latency_ms)
    
    return Answer(answer=answer, cost=cost, cached=False, latency_ms=latency_ms)

@app.get("/stats")
def stats(x_api_key: str = Header(...)):
    user = get_user_from_key(x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    session = Session()
    
    total_requests = session.query(func.count(RequestLog.id)).scalar()
    total_cost = session.query(func.sum(RequestLog.cost)).scalar() or 0.0
    
    cost_per_model = session.query(
        RequestLog.model,
        func.sum(RequestLog.cost).label("total")
    ).group_by(RequestLog.model).all()
    
    session.close()
    
    return {
        "total_requests": total_requests,
        "total_cost": round(total_cost, 6),
        "cost_per_model": {m: round(c, 6) for m, c in cost_per_model}
    }

@app.get("/health")
def health():
    return {"status": "ok"}