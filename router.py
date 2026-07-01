#!/usr/bin/env python3
"""
LangGraph Router for AI Cost Optimizer — Day 29 (Fixed)
LLM-based intent classification using Groq + structured output
"""

import os
import sys
from typing import TypedDict, Literal
from enum import Enum

from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

# ============ LLM SETUP ============
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.0,
    groq_api_key=GROQ_API_KEY
)

# ============ ENUM FOR INTENT (Avoids Literal issues) ============
class Intent(str, Enum):
    COST = "cost"
    LOGS = "logs"
    CACHE = "cache"
    UNKNOWN = "unknown"

# ============ STRUCTURED OUTPUT SCHEMA ============
class IntentClassification(BaseModel):
    """
    Pydantic model that forces the LLM to return structured JSON.
    """
    intent: str = Field(
        description="The classified intent: cost, logs, cache, or unknown"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score between 0 and 1"
    )
    reasoning: str = Field(
        description="Brief explanation of why this intent was chosen"
    )

# Bind structured output to LLM
structured_llm = llm.with_structured_output(IntentClassification)

# ============ STATE ============
class RouterState(TypedDict):
    question: str
    intent: str | None
    tool_name: str | None
    tool_args: dict
    result: str | None
    confidence: float | None
    reasoning: str | None

# ============ LLM CLASSIFIER NODE ============
def classify_intent(state: RouterState) -> RouterState:
    """
    Uses Groq LLM to classify intent with structured output.
    """
    question = state["question"]
    
    prompt = f"""You are an intent classifier for an AI Cost Optimizer system.
Your job is to classify user questions into one of these categories:

- "cost": Questions about spending, money, price, cost, expenses, budget, billing
  Examples: "How much did I spend?", "What's my most expensive model?", "Am I over budget?"
  
- "logs": Questions about request history, recent calls, past queries, API usage log
  Examples: "Show my last 10 requests", "What did I ask yesterday?", "Recent API calls"
  
- "cache": Questions about cache efficiency, hit rate, performance, savings from caching
  Examples: "Is my cache working?", "What's my hit rate?", "Am I saving money with cache?"
  
- "unknown": Anything else that doesn't fit the above

User question: "{question}"

Classify the intent, provide confidence (0-1), and explain your reasoning briefly.
"""
    
    try:
        classification = structured_llm.invoke(prompt)
        
        intent = classification.intent
        confidence = classification.confidence
        reasoning = classification.reasoning
        
        # Validate intent is one of our known values
        valid_intents = {"cost", "logs", "cache", "unknown"}
        if intent not in valid_intents:
            intent = "unknown"
            confidence = 0.0
            reasoning = f"LLM returned invalid intent '{intent}', defaulting to unknown"
        
        tool_map = {
            "cost": ("get_cost_stats", {}),
            "logs": ("query_logs", {"limit": 10}),
            "cache": ("get_cache_hit_rate", {}),
            "unknown": (None, {})
        }
        tool_name, tool_args = tool_map[intent]
        
        if intent == "logs":
            words = question.split()
            for word in words:
                if word.isdigit():
                    tool_args = {"limit": min(int(word), 100)}
                    break
        
        return {
            **state,
            "intent": intent,
            "tool_name": tool_name,
            "tool_args": tool_args,
            "confidence": confidence,
            "reasoning": reasoning
        }
        
    except Exception as e:
        return {
            **state,
            "intent": "unknown",
            "tool_name": None,
            "tool_args": {},
            "confidence": 0.0,
            "reasoning": f"LLM classification failed: {str(e)}"
        }

# ============ TOOL EXECUTION NODES ============
def execute_cost_tool(state: RouterState) -> RouterState:
    result = (
        "Total Requests: 47\n"
        "Total Cost: $0.005832\n"
        "\n"
        "Breakdown by Model:\n"
        "  - llama3-8b-8192: $0.005832 (47 requests)"
    )
    return {**state, "result": result}


def execute_logs_tool(state: RouterState) -> RouterState:
    limit = state["tool_args"].get("limit", 10)
    result = f"Recent Request Logs (limit={limit}):\n[Simulated: would query PostgreSQL]"
    return {**state, "result": result}


def execute_cache_tool(state: RouterState) -> RouterState:
    result = (
        "Cache Statistics:\n"
        "  Total Requests: 47\n"
        "  Cached Responses: 12\n"
        "  Cache Hit Rate: 25.53%"
    )
    return {**state, "result": result}


def handle_unknown(state: RouterState) -> RouterState:
    result = (
        f"I'm not sure how to help with that.\n\n"
        f"Detected intent: {state['intent']}\n"
        f"Confidence: {state['confidence']:.2f}\n"
        f"Reasoning: {state['reasoning']}\n\n"
        f"I can help you with:\n"
        f"  • Cost analysis: 'How much did I spend?'\n"
        f"  • Request logs: 'Show my last 10 requests'\n"
        f"  • Cache stats: 'What's my cache hit rate?'"
    )
    return {**state, "result": result}

# ============ CONDITIONAL EDGE ============
def route_by_intent(state: RouterState) -> str:
    return state["intent"]

# ============ BUILD GRAPH ============
def build_router():
    graph = StateGraph(RouterState)
    
    graph.add_node("classify", classify_intent)
    graph.add_node("cost", execute_cost_tool)
    graph.add_node("logs", execute_logs_tool)
    graph.add_node("cache", execute_cache_tool)
    graph.add_node("unknown", handle_unknown)
    
    graph.set_entry_point("classify")
    
    graph.add_conditional_edges(
        "classify",
        route_by_intent,
        {
            "cost": "cost",
            "logs": "logs",
            "cache": "cache",
            "unknown": "unknown"
        }
    )
    
    graph.add_edge("cost", END)
    graph.add_edge("logs", END)
    graph.add_edge("cache", END)
    graph.add_edge("unknown", END)
    
    return graph.compile()

# ============ MAIN ============
if __name__ == "__main__":
    router = build_router()
    
    test_questions = [
        "How much did I spend on AI this month?",
        "Show me my last 5 requests",
        "Is my cache working well?",
        "Where did my money go?",
        "Am I burning cash on LLM calls?",
        "What's the damage to my wallet?",
        "Show me what I asked recently",
        "Are my API calls being reused?",
        "What is the weather like today?",
        "Tell me about quantum physics",
    ]
    
    print("=" * 70)
    print("DAY 29: LLM-BASED INTENT CLASSIFICATION")
    print("=" * 70)
    
    for question in test_questions:
        print(f"\n🧑 User: {question}")
        
        result = router.invoke({
            "question": question,
            "intent": None,
            "tool_name": None,
            "tool_args": {},
            "result": None,
            "confidence": None,
            "reasoning": None
        })
        
        print(f"🤖 Intent: {result['intent']} (confidence: {result['confidence']:.2f})")
        print(f"🧠 Reasoning: {result['reasoning']}")
        print(f"🔧 Tool: {result['tool_name']}")
        print(f"📊 Result:\n{result['result']}")
        print("-" * 70)