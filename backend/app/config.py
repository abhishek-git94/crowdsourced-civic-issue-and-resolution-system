import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    SECRET_KEY = os.getenv("SECRET_KEY", "secret123")
    MONGODB_SETTINGS = {
        'host': os.getenv("MONGODB_URI", "mongodb://localhost:27017/JanSuvidha")
    }
    
    # Upload Settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "frontend", "static", "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
    
    # Duplicate Detection Settings
    EMBED_BACKEND = os.getenv("EMBED_BACKEND", "local")
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.78))
    RECENT_CHECK_COUNT = int(os.getenv("RECENT_CHECK_COUNT", 50))
    
    # AI Models
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
    YOLO_MODEL_PATH = os.path.join(BASE_DIR, "models_ai", "last_jansuvidha.pt")
