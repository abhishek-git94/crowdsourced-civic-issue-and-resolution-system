import numpy as np
import json

# -----------------------------
# Local Embedding (Dummy version)
# Replace with real model later
# -----------------------------

def get_local_embedding(text: str):
    """Return a simple numeric vector for text (placeholder)."""
    # In production: replace with real sentence-transformer embedding
    return np.random.rand(384).tolist()


# -----------------------------
# OpenAI Embedding (optional)
# -----------------------------
def get_openai_embedding(text: str):
    """Placeholder for external embedding service."""
    # Return random until you connect OpenAI API
    return np.random.rand(384).tolist()


# -----------------------------
# Cosine Similarity
# -----------------------------
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# -----------------------------
# Save embedding as JSON in DB
# -----------------------------
def embed_to_json(vector):
    return json.dumps(vector)


# -----------------------------
# Load embedding from JSON in DB
# -----------------------------
def json_to_embed(json_str):
    if not json_str:
        return None
    return json.loads(json_str)

# utils/duplicate_detector.py  (extend)
import json
import numpy as np

# existing functions assumed:
# - get_local_embedding(text) -> list[float]
# - get_openai_embedding(text) -> list[float]
# - cosine_similarity(a, b) -> float

def find_similar_issues(db, embedding, top_k=5, min_score=0.65):
    """
    Return top_k similar issues as dicts with score >= min_score.
    db: SQLAlchemy session
    embedding: list/np.array
    """
    # If you added pgvector in DB, use vector search (fast)
    try:
        # Example using pgvector cosine similarity (scale to your DB flavor)
        rows = db.execute(
            "SELECT id, issue, location, upvotes, embedding, "
            "1 - (embedding_vector <#> :emb) AS similarity "
            "FROM issues "
            "ORDER BY embedding_vector <#> :emb LIMIT :k",
            {"emb": embedding, "k": top_k}
        ).fetchall()
        results = [
            {"id": r[0], "issue": r[1], "location": r[2], "upvotes": r[3],
             "embedding": r[4], "similarity": float(r[5])}
            for r in rows
            if float(r[5]) >= min_score
        ]
        return results
    except Exception:
        # fallback to in-app cosine comparisons (works for small recents)
        from ..models import Issue
        recent = db.query(Issue).filter(Issue.embedding != None).order_by(Issue.created_at.desc()).limit(200).all()
        scores = []
        for old in recent:
            old_emb = json.loads(old.embedding)
            sim = cosine_similarity(embedding, old_emb)
            scores.append((sim, old))
        scores.sort(reverse=True, key=lambda x:x[0])
        results = []
        for sim, old in scores[:top_k]:
            if sim >= min_score:
                results.append({
                    "id": old.id,
                    "issue": old.issue,
                    "location": old.location,
                    "upvotes": old.upvotes,
                    "similarity": round(sim,3)
                })
        return results
