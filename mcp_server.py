import os
import sys
from pydantic import BaseModel, Field, ValidationError
from mcp.server.fastmcp import FastMCP
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/ai_costs")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import RequestLog

mcp = FastMCP("ai-cost-optimizer")


@mcp.tool()
def hello(name: str) -> str:
    """Say hello to verify MCP connection."""
    return f"Hello, {name}! MCP server is working."


@mcp.tool()
def get_cost_stats() -> str:
    """Returns total requests, total cost, and per-model breakdown."""
    session = Session()
    try:
        total_requests = session.query(func.count(RequestLog.id)).scalar() or 0
        total_cost = session.query(func.sum(RequestLog.cost)).scalar() or 0.0

        cost_per_model = session.query(
            RequestLog.model,
            func.sum(RequestLog.cost).label("total"),
            func.count(RequestLog.id).label("count")
        ).group_by(RequestLog.model).all()

        lines = [
            f"Total Requests: {total_requests}",
            f"Total Cost: ${round(total_cost, 6)}",
            "",
            "Breakdown by Model:"
        ]
        for m, c, cnt in cost_per_model:
            lines.append(f"  - {m}: ${round(c, 6)} ({cnt} requests)")

        return "\n".join(lines)

    except Exception as e:
        raise RuntimeError(f"Database error in get_cost_stats: {str(e)}")
    finally:
        session.close()

class QueryLogsInput(BaseModel):
    limit: int = Field(default=10, ge=1, le=100, description="Entries to return (1-100)")
    user_id: str | None = Field(default=None, description="Filter by user ID")


@mcp.tool()
def query_logs(limit: int = 10, user_id: str | None = None) -> str:
    """
    Returns recent N request log entries from PostgreSQL.
    Validates limit is between 1 and 100.
    """
    try:
        validated = QueryLogsInput(limit=limit, user_id=user_id)
    except ValidationError as e:
        errors = "; ".join(f"{err['loc'][0]}: {err['msg']}" for err in e.errors())
        raise ValueError(f"Invalid input: {errors}")

    session = Session()
    try:
        query = session.query(RequestLog).order_by(RequestLog.timestamp.desc())
        if validated.user_id:
            query = query.filter(RequestLog.user_id == validated.user_id)

        logs = query.limit(validated.limit).all()

        if not logs:
            return "No logs found."

        lines = [f"Recent Request Logs (limit={validated.limit}):"]
        for log in logs:
            lines.append(
                f"[{log.timestamp.strftime('%Y-%m-%d %H:%M')}] "
                f"user={log.user_id} | model={log.model} | "
                f"cost=${log.cost:.4f} | cached={log.cached} | "
                f"latency={log.latency_ms}ms"
            )
        return "\n".join(lines)

    except Exception as e:
        raise RuntimeError(f"Database error in query_logs: {str(e)}")
    finally:
        session.close()


@mcp.tool()
def get_cache_hit_rate() -> str:
    """
    Calculates cache hit rate from request_logs.
    Hit rate = cached_requests / total_requests * 100
    """
    session = Session()
    try:
        total = session.query(func.count(RequestLog.id)).scalar() or 0
        if total == 0:
            return "No requests logged yet. Cache hit rate: N/A"

        cached = session.query(func.count(RequestLog.id)).filter(
            RequestLog.cached == True
        ).scalar() or 0

        hit_rate = (cached / total) * 100

        return (
            f"Cache Statistics:\n"
            f"  Total Requests: {total}\n"
            f"  Cached Responses: {cached}\n"
            f"  Cache Hit Rate: {hit_rate:.2f}%"
        )

    except Exception as e:
        raise RuntimeError(f"Database error in get_cache_hit_rate: {str(e)}")
    finally:
        session.close()


if __name__ == "__main__":
    mcp.run(transport="stdio")