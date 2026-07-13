#!/usr/bin/env python3
"""
LangGraph Router for AI Cost Optimizer — Day 30 (Fixed)
OpenRouter with working free models
"""

import os
from typing import TypedDict
from enum import Enum

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# ============ OPENROUTER SETUP ============
# Replace OpenRouter with Groq
from langchain_groq import ChatGroq

cheap_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

expensive_llm = ChatGroq(
    model="mixtral-8x7b-32768",
    temperature=0.0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# ============ SCHEMAS ============
class IntentClassification(BaseModel):
    intent: str = Field(description="cost, logs, cache, or unknown")
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(description="Why this intent")

class ComplexityClassification(BaseModel):
    complexity: str = Field(description="simple or complex")
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(description="Why this complexity")

intent_llm = cheap_llm.with_structured_output(IntentClassification)
complexity_llm = cheap_llm.with_structured_output(ComplexityClassification)

# ============ STATE ============
class RouterState(TypedDict):
    question: str
    intent: str | None
    complexity: str | None
    model_used: str | None
    tool_name: str | None
    tool_args: dict
    result: str | None
    confidence: float | None
    reasoning: str | None
    cost_estimate: float | None

# ============ CLASSIFIERS ============
def classify_intent(state: RouterState) -> RouterState:
    question = state["question"]
    
    prompt = f"""Classify this question into: cost, logs, cache, or unknown.

Examples:
- "How much did I spend?" → cost
- "Show my last 10 requests" → logs
- "Is my cache working?" → cache
- "What is the weather?" → unknown

Question: "{question}"
"""
    try:
        classification = intent_llm.invoke(prompt)
        intent = classification.intent
        if intent not in {"cost", "logs", "cache", "unknown"}:
            intent = "unknown"
        confidence = classification.confidence
        reasoning = classification.reasoning
    except Exception as e:
        print(f"Intent classification failed: {e}")
        intent = "unknown"
        confidence = 0.0
        reasoning = f"Error: {str(e)}"
    
    # FIX: Use square brackets [] not parentheses ()
    tool_map = {
        "cost": ("get_cost_stats", {}),
        "logs": ("query_logs", {"limit": 10}),
        "cache": ("get_cache_hit_rate", {}),
        "unknown": (None, {})
    }
    tool_name, tool_args = tool_map[intent]  # <-- FIXED: was tool_map("intent")
    
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

def classify_complexity(state: RouterState) -> RouterState:
    question = state["question"]
    
    prompt = f"""Determine if this question is SIMPLE or COMPLEX.

SIMPLE: Single fact, number, or straightforward lookup.
Examples: "How much did I spend?", "Show my last 5 requests"

COMPLEX: Analysis, comparison, prediction, multi-step reasoning.
Examples: "Analyze spending trends over last month", "Compare Groq vs OpenAI costs"

Question: "{question}"
"""
    try:
        classification = complexity_llm.invoke(prompt)
        complexity = classification.complexity.lower()
        if complexity not in {"simple", "complex"}:
            complexity = "simple"
    except Exception as e:
        print(f"Complexity classification failed: {e}")
        complexity = "simple"
    
    model_map = {
        "simple": ("llama-3.3-70b-versatile", 0.0),
        "complex": ("mixtral-8x7b-32768", 0.0)
    }
    model_used, cost = model_map.get(complexity, ("llama-3.3-70b-versatile", 0.0))
    
    return {
        **state,
        "complexity": complexity,
        "model_used": model_used,
        "cost_estimate": cost
    }

# ============ TOOL EXECUTION ============
def execute_tool(state: RouterState) -> RouterState:
    intent = state["intent"]
    model = state["model_used"]
    complexity = state["complexity"]
    
    if intent == "cost":
        result = (
            f"[Using {model} ({complexity}) — FREE]\n\n"
            f"Total Requests: 47\n"
            f"Total Cost: $0.005832\n"
            f"Breakdown by Model:\n"
            f"  - llama-3.3-70b-versatile: $0.005832 (47 requests)"
        )
    elif intent == "logs":
        limit = state["tool_args"].get("limit", 10)
        result = (
            f"[Using {model} ({complexity}) — FREE]\n\n"
            f"Recent Request Logs (limit={limit}):\n"
            f"[Simulated: would query PostgreSQL]"
        )
    elif intent == "cache":
        result = (
            f"[Using {model} ({complexity}) — FREE]\n\n"
            f"Cache Statistics:\n"
            f"  Total Requests: 47\n"
            f"  Cached Responses: 12\n"
            f"  Cache Hit Rate: 25.53%"
        )
    else:
        result = (
            f"[Using {model} ({complexity}) — FREE]\n\n"
            f"I'm not sure how to help with that.\n\n"
            f"I can help you with:\n"
            f"  • Cost analysis\n"
            f"  • Request logs\n"
            f"  • Cache stats"
        )
    
    return {**state, "result": result}

# ============ BUILD GRAPH ============
def build_router():
    graph = StateGraph(RouterState)
    
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("classify_complexity", classify_complexity)
    graph.add_node("execute_tool", execute_tool)
    
    graph.set_entry_point("classify_intent")
    graph.add_edge("classify_intent", "classify_complexity")
    graph.add_edge("classify_complexity", "execute_tool")
    graph.add_edge("execute_tool", END)
    
    return graph.compile()

# ============ MAIN ============
if __name__ == "__main__":
    router = build_router()
    
    test_questions = [
        "How much did I spend?",
        "Show my last 5 requests",
        "Analyze my spending trends over the last month",
        "Compare my Groq vs OpenAI costs",
        "What's my cache hit rate?",
        "Predict next month's spending",
    ]
    
    print("=" * 70)
    print("DAY 30: MODEL SELECTION WITH OPENROUTER FREE MODELS")
    print("=" * 70)
    
    for question in test_questions:
        print(f"\n🧑 User: {question}")
        
        result = router.invoke({
            "question": question,
            "intent": None,
            "complexity": None,
            "model_used": None,
            "tool_name": None,
            "tool_args": {},
            "result": None,
            "confidence": None,
            "reasoning": None,
            "cost_estimate": None
        })
        
        print(f"🤖 Intent: {result['intent']}")
        print(f"📊 Complexity: {result['complexity']}")
        print(f"🧠 Model: {result['model_used']}")
        print(f"💰 Cost: ${result['cost_estimate']:.6f} (FREE)")
        print(f"📊 Result:\n{result['result']}")
        print("-" * 70)