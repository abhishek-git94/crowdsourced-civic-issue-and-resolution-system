"""
Civic AI Analyzer – safe imports with keyword-based fallback.
If YOLO / Ollama / OpenCV are not installed the module still loads
and falls back to deterministic keyword + description analysis.
"""

# ── Optional heavy deps ────────────────────────────────────────────────────────
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# ── Standard deps ─────────────────────────────────────────────────────────────
from datetime import datetime
import os

from ..config import Config
from .advanced_ai import (
    analyze_sentiment,
    smart_assign_department,
    predict_resolution_days,
    cluster_issues,
    detect_anomalies,
    natural_language_query
)

# ── Keyword-based civic detection (no heavy deps) ─────────────────────────────
CIVIC_KEYWORD_MAP = {
    'pothole':          ('roads',          85),
    'road':             ('roads',          70),
    'crack':            ('roads',          72),
    'broken road':      ('roads',          90),
    'damage':           ('infrastructure', 68),
    'garbage':          ('sanitation',     88),
    'trash':            ('sanitation',     85),
    'waste':            ('sanitation',     82),
    'litter':           ('sanitation',     78),
    'water':            ('water',          80),
    'leak':             ('water',          85),
    'drain':            ('water',          80),
    'flood':            ('water',          90),
    'overflow':         ('water',          85),
    'sewage':           ('water',          88),
    'light':            ('electricity',    78),
    'electric':         ('electricity',    85),
    'wire':             ('electricity',    88),
    'power':            ('electricity',    80),
    'dark':             ('electricity',    70),
    'pole':             ('electricity',    75),
    'traffic':          ('traffic',        80),
    'signal':           ('traffic',        85),
    'sign':             ('traffic',        72),
    'park':             ('parks',          75),
    'tree':             ('parks',          70),
    'bench':            ('parks',          68),
}

CATEGORY_OBJECTS = {
    'roads':         [{'label': 'pothole',          'confidence': 78}],
    'sanitation':    [{'label': 'garbage_heap',     'confidence': 82}],
    'water':         [{'label': 'water_leak',       'confidence': 80}],
    'electricity':   [{'label': 'broken_streetlight','confidence': 75}],
    'traffic':       [{'label': 'traffic_signal',   'confidence': 77}],
    'parks':         [{'label': 'broken_bench',     'confidence': 70}],
    'infrastructure':[{'label': 'infrastructure_issue','confidence': 72}],
}


def _keyword_detect(text: str):
    """Return (category, confidence, detected_objects) from plain text."""
    text_lower = (text or '').lower()
    best_cat = 'infrastructure'
    best_conf = 60

    for kw, (cat, conf) in CIVIC_KEYWORD_MAP.items():
        if kw in text_lower and conf > best_conf:
            best_cat = cat
            best_conf = conf

    objects = CATEGORY_OBJECTS.get(best_cat, [{'label': 'civic_issue', 'confidence': best_conf}])
    return best_cat, best_conf, objects


# ── Scoring helpers ───────────────────────────────────────────────────────────

def calculate_dynamic_severity(confidence, similar_issues):
    if not similar_issues:
        if confidence >= 80:
            return 'High'
        elif confidence >= 50:
            return 'Medium'
        return 'Low'

    num_similar = len(similar_issues)
    now = datetime.now()
    recency_score = 0
    for sim_issue in similar_issues:
        if hasattr(sim_issue, 'created_at') and sim_issue.created_at:
            days_old = (now - sim_issue.created_at).days
            if days_old <= 7:
                recency_score += 3
            elif days_old <= 30:
                recency_score += 2
            elif days_old <= 90:
                recency_score += 1

    report_score = min(num_similar * 15, 60)
    total_score = (confidence * 0.30) + (report_score * 0.40) + (recency_score * 10 * 0.30)

    if total_score >= 60:
        return 'High'
    elif total_score >= 35:
        return 'Medium'
    return 'Low'


def calculate_priority(severity, category, department, location=""):
    severity_scores = {'Low': 1, 'Medium': 2, 'High': 3}
    base_score = severity_scores.get(severity, 1)

    category_priority = {
        'infrastructure': 3, 'roads': 3, 'water': 3, 'electricity': 3,
        'sanitation': 2, 'garbage': 2, 'parks': 1, 'other': 1
    }
    cat_score = category_priority.get((category or 'other').lower(), 1)

    location_boost = 1
    if location:
        critical_kw = ['hospital', 'school', 'highway', 'main road', 'airport',
                       'station', 'junction', 'square', 'market', 'rajwada', 'vijay nagar']
        if any(kw in location.lower() for kw in critical_kw):
            location_boost = 3
        elif any(kw in location.lower() for kw in ['street', 'lane', 'colony', 'park']):
            location_boost = 1.5

    total_priority = (base_score * 0.4) + (cat_score * 0.3) + (location_boost * 0.2) + (2 * 0.1)

    if total_priority >= 2.5:
        return 'Urgent'
    elif total_priority >= 2.0:
        return 'High'
    elif total_priority >= 1.5:
        return 'Medium'
    return 'Low'


def check_duplicate_threshold(similar_issues, min_similarity=0.75):
    if not similar_issues:
        return False, None
    for sim in similar_issues:
        if isinstance(sim, dict):
            similarity = sim.get('similarity', 0)
            issue_id = sim.get('id')
        else:
            similarity = getattr(sim, 'similarity', 0)
            issue_id = str(sim.id) if hasattr(sim, 'id') else None
        if similarity >= min_similarity:
            return True, issue_id
    return False, None


def enhance_image(img):
    if not CV2_AVAILABLE:
        return img
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    merged = cv2.merge((cl, a, b))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)


# ── Main AI Analyzer class ────────────────────────────────────────────────────

class CivicAIAnalyzer:
    def __init__(self, text_model=None, yolo_model=None):
        self.text_model = text_model or getattr(Config, 'OLLAMA_MODEL', 'llama3')
        self.yolo_model_path = yolo_model or getattr(Config, 'YOLO_MODEL_PATH', 'yolov8n.pt')
        self.conf_threshold = getattr(Config, 'YOLO_CONF_THRESHOLD', 0.25)

        print(f"[AI] Ollama available: {OLLAMA_AVAILABLE}")
        print(f"[AI] YOLO  available: {YOLO_AVAILABLE}")
        print(f"[AI] OpenCV available: {CV2_AVAILABLE}")
        print(f"[AI] ChromaDB available: {CHROMA_AVAILABLE}")

        # YOLO – optional
        self.yolo = None
        if YOLO_AVAILABLE:
            try:
                self.yolo = YOLO(self.yolo_model_path)
                print(f"[AI] YOLO model loaded from {self.yolo_model_path}")
            except Exception as e:
                print(f"[AI] YOLO load failed: {e} – using keyword fallback")

        # ChromaDB – optional
        self.collection = None
        if CHROMA_AVAILABLE:
            try:
                self.chroma_client = chromadb.Client()
                self.collection = self.chroma_client.get_or_create_collection(
                    name="civic_issues",
                    metadata={"description": "Historical civic issues"}
                )
                print("[AI] RAG system initialized")
            except Exception as e:
                print(f"[AI] RAG initialization failed: {e}")

        self.civic_mapping = {
            'pothole':          ['crack', 'hole', 'damaged'],
            'garbage':          ['bottle', 'trash', 'bag', 'cup'],
            'traffic':          ['car', 'truck', 'bus', 'traffic light'],
            'street_furniture': ['bench', 'stop sign'],
            'infrastructure':   ['fire hydrant', 'parking meter'],
        }

    # ── Image analysis ────────────────────────────────────────────────────────

    def analyze_image(self, image_path):
        """Detect objects in image. Falls back to filename/path clues."""
        # Try YOLO first
        if self.yolo is not None and CV2_AVAILABLE:
            try:
                image = cv2.imread(image_path)
                if image is not None:
                    # ── Speed fix: resize to 640 (YOLO native res) before inference ──
                    h, w = image.shape[:2]
                    if max(h, w) > 640:
                        scale = 640 / max(h, w)
                        image = cv2.resize(image, (int(w * scale), int(h * scale)),
                                           interpolation=cv2.INTER_AREA)
                    image = enhance_image(image)
                    results = self.yolo(image, verbose=False, imgsz=640, conf=0.20)
                    detected = []
                    for r in results:
                        if r.boxes is None:
                            continue
                        for box in r.boxes:
                            cls_id = int(box.cls[0])
                            label  = r.names[cls_id]
                            conf   = float(box.conf[0])
                            if conf > 0.15:
                                detected.append({'label': label, 'confidence': round(conf * 100, 1)})
                    if detected:
                        return detected
            except Exception as e:
                print(f"[AI] YOLO detection error: {e}")

        # Keyword fallback from filename
        fname = os.path.basename(image_path).lower()
        _, conf, objects = _keyword_detect(fname)
        return objects

    # ── Civic categorisation ──────────────────────────────────────────────────

    def categorize_issue(self, objects):
        labels = [obj['label'].lower() for obj in objects]
        for category, keywords in self.civic_mapping.items():
            for kw in keywords:
                if any(kw in lbl for lbl in labels):
                    return category
        if any('road' in lbl or 'street' in lbl for lbl in labels):
            return 'road_damage'
        return 'general_infrastructure'

    # ── RAG search ────────────────────────────────────────────────────────────

    def search_similar_issues(self, category, location):
        if not self.collection:
            return []
        try:
            results = self.collection.query(
                query_texts=[f"Category: {category}, Location: {location}"],
                n_results=2
            )
            similar = []
            if results['documents'] and results['documents'][0]:
                for doc in results['documents'][0]:
                    similar.append({'description': doc})
            return similar
        except Exception as e:
            print(f"[AI] RAG search failed: {e}")
            return []

    # ── Description generation ────────────────────────────────────────────────

    def generate_description(self, objects, location="unknown location", category=None):
        if not category:
            category = self.categorize_issue(objects)

        obj_summary = ", ".join([f"{o['label']} ({o['confidence']}%)" for o in objects[:3]])
        context = ""
        similar = self.search_similar_issues(category, location)
        if similar:
            context = f"\n\nNOTE: This location has {len(similar)} similar past issue(s)."

        # Try Ollama
        if OLLAMA_AVAILABLE:
            prompt = (
                f"You are writing a civic infrastructure issue report for municipal authorities.\n\n"
                f"LOCATION: {location}\n"
                f"DETECTED IN IMAGE: {obj_summary}\n"
                f"ISSUE CATEGORY: {category}\n"
                f"{context}\n\n"
                f"Write a professional 2-3 sentence description. Be factual, no markdown.\n"
                f"Write the description now:"
            )
            try:
                response = ollama.chat(
                    model=self.text_model,
                    messages=[{"role": "user", "content": prompt}]
                )
                desc = response["message"]["content"].strip()
                desc = desc.replace('**', '').replace('*', '').replace('\n\n', ' ').replace('\n', ' ')
                return desc
            except Exception as e:
                print(f"[AI] Ollama error: {e}")

        # Deterministic fallback description
        cat_display = category.replace('_', ' ').title()
        return (
            f"A {cat_display} issue has been detected at {location}. "
            f"The image analysis identified: {obj_summary}. "
            f"This requires prompt attention from the concerned department to ensure public safety."
        )

    # ── Full analysis ─────────────────────────────────────────────────────────

    def analyze_civic_issue(self, image_path, location="unknown location",
                            existing_issues=None, department=None):
        import time
        t_start = time.time()

        objects  = self.analyze_image(image_path)
        category = self.categorize_issue(objects)
        description = self.generate_description(objects, location, category)

        max_confidence = max((obj['confidence'] for obj in objects), default=60)

        # Duplicate detection – skip if image analysis already took > 5s to stay responsive
        similar_issues = []
        elapsed = time.time() - t_start
        if elapsed < 5 and existing_issues:
            try:
                from ..utils.duplicate_detector import get_local_embedding, find_similar_issues
                embedding = get_local_embedding(description)
                similar_issues = find_similar_issues(existing_issues, embedding, top_k=10, min_score=0.5)
            except Exception as e:
                print(f"[AI] Duplicate detection failed: {e}")

        severity = calculate_dynamic_severity(max_confidence, similar_issues)
        priority = calculate_priority(severity, category, department, location)
        is_duplicate, duplicate_id = check_duplicate_threshold(similar_issues, min_similarity=0.75)

        sentiment_result = analyze_sentiment(description)
        assigned_dept, dept_confidence = smart_assign_department(category, description, objects)
        predicted_days = predict_resolution_days(category, severity)

        if sentiment_result['urgency_score'] > 0.6 and severity == 'Low':
            severity = 'Medium'
            priority = calculate_priority(severity, category, assigned_dept, location)

        elapsed_total = round(time.time() - t_start, 2)
        print(f"[AI] analyze_civic_issue completed in {elapsed_total}s")

        return {
            'description':              description,
            'category':                 category,
            'detected_objects':         objects,
            'confidence':               max_confidence,
            'severity':                 severity,
            'priority':                 priority,
            'similar_issues_count':     len(similar_issues),
            'duplicate_detected':       is_duplicate,
            'duplicate_of':             duplicate_id,
            'similar_issues':           similar_issues[:3] if similar_issues else [],
            'sentiment':                sentiment_result['sentiment'],
            'urgency_score':            round(sentiment_result['urgency_score'], 2),
            'assigned_department':      assigned_dept,
            'department_confidence':    round(dept_confidence, 2),
            'predicted_resolution_days': predicted_days,
            'analysis_time_seconds':    elapsed_total,
        }

    # ── Knowledge base ────────────────────────────────────────────────────────

    def add_to_knowledge_base(self, issue_id, description, category, location):
        if not self.collection:
            return
        try:
            self.collection.add(
                documents=[f"Category: {category}\nLocation: {location}\nDescription: {description}"],
                ids=[f"issue_{issue_id}"],
                metadatas=[{
                    'issue_id': issue_id,
                    'category': category,
                    'location': location,
                    'timestamp': datetime.now().isoformat()
                }]
            )
        except Exception as e:
            print(f"[AI] Failed to add to RAG: {e}")


# ── Module-level singleton (lazy, safe) ───────────────────────────────────────
_analyzer_instance = None


def get_analyzer():
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = CivicAIAnalyzer()
    return _analyzer_instance
