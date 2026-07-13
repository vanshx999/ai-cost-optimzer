"""
Day 34: Dashboard Stats Endpoint
Aggregates PostgreSQL cost logs + Redis cache stats.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import redis
from pydantic import BaseModel
from typing import List

# ------------------------------------------------------------------
# PostgreSQL setup (from Day 22)
# ------------------------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://costuser:costpass@localhost:5432/costoptimizer"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# ------------------------------------------------------------------
# Redis setup (from Day 33)
# ------------------------------------------------------------------
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

# ------------------------------------------------------------------
# FastAPI app
# ------------------------------------------------------------------
app = FastAPI(title="Cost Optimizer Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------
# Pydantic models
# ------------------------------------------------------------------
class ModelStat(BaseModel):
    model: str
    count: int
    total_cost: float
    total_tokens: int


class DashboardStats(BaseModel):
    total_cost: float
    total_tokens: int
    total_requests: int
    cache_hits: int
    cache_misses: int
    cache_hit_rate: float
    saved_calls: int
    by_model: List[ModelStat]


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------
@app.get("/dashboard-stats", response_model=DashboardStats)
def get_dashboard_stats():
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT
                COALESCE(SUM(cost), 0) as total_cost,
                COALESCE(SUM(tokens), 0) as total_tokens,
                COUNT(*) as total_requests
            FROM requests
        """)).fetchone()

        total_cost = float(result.total_cost) if result else 0.0
        total_tokens = int(result.total_tokens) if result else 0
        total_requests = int(result.total_requests) if result else 0

        model_rows = db.execute(text("""
            SELECT
                model,
                COUNT(*) as request_count,
                COALESCE(SUM(cost), 0) as total_cost,
                COALESCE(SUM(tokens), 0) as total_tokens
            FROM requests
            GROUP BY model
            ORDER BY total_cost DESC
        """)).fetchall()

        by_model = [
            ModelStat(
                model=row.model,
                count=int(row.request_count),
                total_cost=float(row.total_cost),
                total_tokens=int(row.total_tokens)
            )
            for row in model_rows
        ]

    except Exception:
        total_cost = 0.0
        total_tokens = 0
        total_requests = 0
        by_model = []
    finally:
        db.close()

    hits = int(redis_client.get("cache:hits") or 0)
    misses = int(redis_client.get("cache:misses") or 0)
    total_cache = hits + misses
    hit_rate = hits / total_cache if total_cache > 0 else 0.0

    return DashboardStats(
        total_cost=round(total_cost, 4),
        total_tokens=total_tokens,
        total_requests=total_requests,
        cache_hits=hits,
        cache_misses=misses,
        cache_hit_rate=round(hit_rate, 4),
        saved_calls=hits,
        by_model=by_model
    )


@app.get("/health")
def health():
    return {"status": "ok"}


# ------------------------------------------------------------------
# Run
# ------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)