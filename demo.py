"""
Day 33: Lightweight Semantic Cache (No sentence-transformers needed)
Uses TF-IDF-style vectors via scikit-learn. If sklearn fails too,
uncomment the PureNumpyEmbedder fallback below.
"""
import os
import hashlib
import json
import numpy as np
import redis
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=False
)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GROQ_MODEL = "llama-3.1-8b-instant"
SIMILARITY_THRESHOLD = 0.75

# ------------------------------------------------------------------
# Embedding: Try sentence-transformers, fall back to sklearn TF-IDF
# ------------------------------------------------------------------
try:
    from sentence_transformers import SentenceTransformer
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    def get_embedding(text: str) -> np.ndarray:
        emb = embedder.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return emb.astype(np.float32)
    print("[EMBEDDING] Using sentence-transformers (all-MiniLM-L6-v2)")

except ImportError:
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity as sk_cosine
        vectorizer = TfidfVectorizer(max_features=256)
        # Fit on some generic vocab so it's warm
        vectorizer.fit(["python error handling try except cache redis groq llm"])
        def get_embedding(text: str) -> np.ndarray:
            vec = vectorizer.transform([text]).toarray()[0]
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            return vec.astype(np.float32)
        print("[EMBEDDING] Using sklearn TF-IDF fallback")

    except ImportError:
        # Last resort: pure numpy character n-gram hash
        def get_embedding(text: str) -> np.ndarray:
            text = text.lower()
            vec = np.zeros(256, dtype=np.float32)
            for i in range(len(text) - 2):
                idx = hash(text[i:i+3]) % 256
                vec[idx] += 1
            norm = np.linalg.norm(vec)
            return vec / norm if norm > 0 else vec
        print("[EMBEDDING] Using pure-numpy n-gram fallback")


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


def cache_key(query: str) -> str:
    return f"semcache:{hashlib.md5(query.encode()).hexdigest()}"


def store_in_cache(query: str, response: str, metadata: dict = None):
    embedding = get_embedding(query)
    key = cache_key(query)
    redis_client.set(f"{key}:emb", embedding.tobytes())
    payload = {"response": response, "query": query, "metadata": metadata or {}}
    redis_client.set(f"{key}:resp", json.dumps(payload))
    redis_client.expire(f"{key}:emb", 86400)
    redis_client.expire(f"{key}:resp", 86400)
    redis_client.lpush("cache:recent_queries", query)
    redis_client.ltrim("cache:recent_queries", 0, 99)
    redis_client.incr("cache:misses")
    print(f"  [CACHE STORE] Saved: '{query[:50]}...'")


def lookup_cache(query: str) -> tuple:
    query_emb = get_embedding(query)
    cursor = 0
    best_match = None
    best_score = 0.0

    while True:
        cursor, keys = redis_client.scan(cursor, match="semcache:*:emb", count=100)
        for key in keys:
            stored_bytes = redis_client.get(key)
            if not stored_bytes:
                continue
            stored_emb = np.frombuffer(stored_bytes, dtype=np.float32)
            score = cosine_similarity(query_emb, stored_emb)
            if score > best_score:
                best_score = score
                best_match = key
        if cursor == 0:
            break

    if best_match and best_score >= SIMILARITY_THRESHOLD:
        resp_key = (best_match.decode() if isinstance(best_match, bytes) else best_match).replace(":emb", ":resp")
        data = redis_client.get(resp_key)
        if data:
            payload = json.loads(data.decode() if isinstance(data, bytes) else data)
            redis_client.incr("cache:hits")
            print(f"  [CACHE HIT] Similarity: {best_score:.4f}")
            return True, payload["response"]

    redis_client.incr("cache:misses")
    print(f"  [CACHE MISS] Best similarity: {best_match and f'{best_score:.4f}' or 'N/A'}")
    return False, None


def get_cache_stats() -> dict:
    hits = int(redis_client.get("cache:hits") or 0)
    misses = int(redis_client.get("cache:misses") or 0)
    total = hits + misses
    return {
        "hits": hits,
        "misses": misses,
        "total": total,
        "hit_rate": hits / total if total > 0 else 0.0,
        "saved_calls": hits,
        "est_latency_saved_ms": hits * 300
    }


def clear_cache():
    cursor = 0
    deleted = 0
    while True:
        cursor, keys = redis_client.scan(cursor, match="semcache:*", count=100)
        for key in keys:
            redis_client.delete(key)
            deleted += 1
        if cursor == 0:
            break
    redis_client.delete("cache:hits")
    redis_client.delete("cache:misses")
    redis_client.delete("cache:recent_queries")
    print(f"Cleared {deleted} cache entries.")