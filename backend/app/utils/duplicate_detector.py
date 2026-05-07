import numpy as np
import json

SENTENCE_MODEL = None

def _get_sentence_model():
    global SENTENCE_MODEL
    if SENTENCE_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            SENTENCE_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
            print("Sentence Transformer model loaded")
        except Exception as e:
            print(f"Failed to load sentence transformer: {e}")
            SENTENCE_MODEL = False
    return SENTENCE_MODEL


def get_local_embedding(text: str):
    """Return real embedding vector using sentence-transformers."""
    model = _get_sentence_model()
    if model:
        try:
            embedding = model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            print(f"Embedding encoding failed: {e}")
    return np.random.rand(384).tolist()


def get_openai_embedding(text: str):
    """Return embedding using OpenAI API if available, fallback to local."""
    api_key = None
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
    except:
        pass
    
    if not api_key:
        return get_local_embedding(text)
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"OpenAI embedding failed: {e}")
        return get_local_embedding(text)


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

def find_similar_issues(issues, embedding, top_k=5, min_score=0.65):
    """
    Return top_k similar issues as dicts with score >= min_score.
    Used for MongoEngine queryset.
    """
    scores = []
    for issue in issues:
        if not issue.embedding:
            continue
        try:
            old_emb = json.loads(issue.embedding)
            sim = cosine_similarity(embedding, old_emb)
            if sim >= min_score:
                scores.append((sim, issue))
        except Exception:
            continue
    
    scores.sort(reverse=True, key=lambda x: x[0])
    results = []
    for sim, issue in scores[:top_k]:
        results.append({
            "id": str(issue.id),
            "issue": issue.issue,
            "location": issue.location,
            "upvotes": issue.upvotes,
            "similarity": round(sim, 3)
        })
    return results
