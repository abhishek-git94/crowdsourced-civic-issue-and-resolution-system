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
