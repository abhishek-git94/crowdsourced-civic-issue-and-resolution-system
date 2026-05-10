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
# NOTE: _keyword_detect is now a thin wrapper around the unified classify_issue_type
# engine from civic_ai.py so both paths stay consistent.

CATEGORY_DEFAULT_OBJECTS = {
    'roads':          [{'label': 'pothole',              'confidence': 78}],
    'sanitation':     [{'label': 'garbage_heap',         'confidence': 82}],
    'water':          [{'label': 'water_leak',           'confidence': 80}],
    'electricity':    [{'label': 'broken_street_light',  'confidence': 75}],
    'traffic':        [{'label': 'traffic_signal_broken','confidence': 77}],
    'parks':          [{'label': 'broken_bench',         'confidence': 70}],
    'infrastructure': [{'label': 'building_damage',      'confidence': 65}],
}


def _keyword_detect(text: str):
    """Return (category, confidence, detected_objects) using the unified engine."""
    try:
        from .civic_ai import classify_issue_type
        cat, sub, conf = classify_issue_type(text or '', [])
    except Exception:
        cat, sub, conf = 'infrastructure', 'building_damage', 50.0

    # Build detected_objects list with the matched subclass
    obj_label = sub if sub else cat
    objects   = [{'label': obj_label, 'confidence': round(conf, 1)}]
    return cat, round(conf, 1), objects


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
        self.yolo_classes = None
        if YOLO_AVAILABLE:
            try:
                # Try custom model first, fallback to default
                if os.path.exists(self.yolo_model_path):
                    self.yolo = YOLO(self.yolo_model_path)
                    # Get custom model classes
                    self.yolo_classes = self.yolo.names
                    print(f"[AI] Custom YOLO model loaded: {len(self.yolo_classes)} classes")
                    print(f"[AI] Classes: {list(self.yolo_classes.values())}")
                else:
                    # Download default model
                    self.yolo = YOLO('yolov8n.pt')
                    self.yolo_classes = self.yolo.names
                    print(f"[AI] Using default YOLO model (yolov8n.pt)")
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
        """Detect objects in image using YOLO only - NO FALLBACK"""
        
        # Map custom model classes to system categories
        CLASS_TO_CATEGORY_MAP = {
            'Pothole Issues': ('roads', 'pothole'),
            'Damaged Road issues': ('roads', 'road_damage'),
            'Illegal Parking Issues': ('traffic', 'illegal_parking'),
            'Broken Road Sign Issues': ('roads', 'sign_damage'),
            'Fallen trees': ('parks', 'fallen_tree'),
            'Littering/Garbage on Public Places': ('sanitation', 'garbage'),
            'Vandalism Issues': ('infrastructure', 'vandalism'),
            'Dead Animal Pollution': ('sanitation', 'dead_animal'),
            'Damaged concrete structures': ('infrastructure', 'structure_damage'),
            'Damaged Electric wires and poles': ('electricity', 'wire_damage'),
        }
        
        print(f"[AI] Starting YOLO detection on: {image_path}")
        
        if self.yolo is not None and CV2_AVAILABLE:
            try:
                image = cv2.imread(image_path)
                if image is not None:
                    # Resize to 320 for FASTER YOLO
                    h, w = image.shape[:2]
                    print(f"[AI] Original Image size: {w}x{h}")
                    
                    target_size = 320
                    if max(h, w) > target_size:
                        scale = target_size / max(h, w)
                        image = cv2.resize(image, (int(w*scale), int(h*scale)),
                                           interpolation=cv2.INTER_AREA)
                        print(f"[AI] Resized to: {int(w*scale)}x{int(h*scale)} (faster)")
                    
                    # Use smaller imgsz for faster inference
                    results = self.yolo(image, verbose=False, imgsz=target_size, conf=0.05)
                    
                    detected = []
                    raw_detections = []
                    
                    for r in results:
                        if r.boxes is None:
                            print("[AI] No boxes detected")
                            continue
                        
                        print(f"[AI] Found {len(r.boxes)} boxes")
                        
                        for box in r.boxes:
                            cls_id = int(box.cls[0])
                            label = self.yolo_classes[cls_id] if self.yolo_classes else r.names[cls_id]
                            conf = float(box.conf[0]) * 100
                            
                            raw_detections.append({
                                'label': label,
                                'confidence': round(conf, 1),
                                'class_id': cls_id
                            })
                            
                            # Map to category
                            category, subclass = CLASS_TO_CATEGORY_MAP.get(label, ('infrastructure', label.lower()))
                            
                            if conf > 5:
                                detected.append({
                                    'label': label,
                                    'confidence': round(conf, 1),
                                    'category': category,
                                    'subclass': subclass
                                })
                    
                    print(f"[AI] Raw detections: {raw_detections}")
                    print(f"[AI] Filtered detections (>5%): {detected}")
                    
                    if detected:
                        print(f"[AI] YOLO SUCCESS: {detected}")
                        return detected
                    else:
                        print("[AI] YOLO: No objects detected above 5% threshold")
                        return []
                else:
                    print(f"[AI] ERROR: Could not read image file: {image_path}")
                    return []
            except Exception as e:
                print(f"[AI] YOLO detection ERROR: {e}")
                import traceback
                traceback.print_exc()
                return []
        else:
            print("[AI] YOLO not available - returning empty")
            return []

    # ── Civic categorisation ──────────────────────────────────────────────────

    def categorize_issue(self, objects, user_description=""):
        from .civic_ai import classify_issue_type
        best_type, best_subclass, confidence = classify_issue_type(user_description, objects)
        return best_type, best_subclass, confidence

    def categorize_issue_from_description(self, description):
        """Categorize based on user description text only - NO FALLBACK"""
        if not description:
            return 'general', 'unknown', 30
        
        desc_lower = description.lower()
        
        # Direct keyword matching for your 10 classes
        category_mapping = {
            # Roads
            'roads': ['road', 'road damage', 'road broken', 'road crack', 'asphalt', 'pavement'],
            'pothole': ['pothole', 'potholes', 'hole in road', 'hole on road', 'road hole'],
            'road_damage': ['road damage', 'road broken', 'road crack', 'road sink'],
            'sign_damage': ['road sign', 'sign broken', 'sign damaged', 'traffic sign'],
            # Traffic
            'illegal_parking': ['illegal parking', 'wrong parking', 'parking violation', 'parked illegally'],
            # Parks
            'fallen_tree': ['fallen tree', 'tree fallen', 'tree down', 'tree fallen'],
            # Sanitation
            'garbage': ['garbage', 'litter', 'waste', 'trash', 'dirty', 'filth', 'waste dump'],
            'dead_animal': ['dead animal', 'animal dead', 'dead dog', 'dead animal'],
            # Infrastructure
            'vandalism': ['vandalism', 'vandalized', 'graffiti', 'damaged deliberately'],
            'structure_damage': ['concrete', 'structure damage', 'broken wall', 'damaged structure'],
            # Electricity
            'wire_damage': ['electric wire', 'wire broken', 'electrical wire', 'pole wire', 'hanging wire'],
        }
        
        # Map to system categories
        system_category_map = {
            'roads': 'roads',
            'pothole': 'roads',
            'road_damage': 'roads',
            'sign_damage': 'roads',
            'illegal_parking': 'traffic',
            'fallen_tree': 'parks',
            'garbage': 'sanitation',
            'dead_animal': 'sanitation',
            'vandalism': 'infrastructure',
            'structure_damage': 'infrastructure',
            'wire_damage': 'electricity',
        }
        
        # Find matching sub-category
        best_match = None
        best_score = 0
        
        for sub_cat, keywords in category_mapping.items():
            score = sum(1 for kw in keywords if kw in desc_lower)
            if score > best_score:
                best_score = score
                best_match = sub_cat
        
        if best_match:
            category = system_category_map.get(best_match, 'general')
            confidence = min(90, 50 + best_score * 10)
            print(f"[AI] Description match: {best_match} (score: {best_score})")
            return category, best_match, confidence
        
        return 'general', 'unknown', 30

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

    def generate_description(self, objects, location="unknown location", category=None, sub_category=None, user_description=""):
        if not category or not sub_category:
            category, sub_category, _ = self.categorize_issue(objects, user_description)

        obj_summary = ", ".join([f"{o['label']} ({o['confidence']}%)" for o in objects[:3]])
        context = ""
        similar = self.search_similar_issues(category, location)
        if similar:
            context = f"\n\nNOTE: This location has {len(similar)} similar past issue(s)."

        user_context = f"\nUSER PROVIDED DESCRIPTION: {user_description}\n" if user_description else ""

        # Try Ollama
        if OLLAMA_AVAILABLE:
            prompt = (
                f"You are writing a civic infrastructure issue report for municipal authorities.\n\n"
                f"LOCATION: {location}\n"
                f"DETECTED IN IMAGE: {obj_summary}\n"
                f"ISSUE CATEGORY: {category} ({sub_category})\n"
                f"{user_context}"
                f"{context}\n\n"
                f"Write a professional 2-3 sentence description. Be factual, no markdown. Incorporate the user's description if provided.\n"
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

        # Deterministic fallback description - much better now
        if user_description and len(user_description.strip()) > 10:
            return user_description

        cat_display = category.replace('_', ' ').title()
        sub_display = sub_category.replace('_', ' ').title() if sub_category else 'Unknown'
        
        # Custom descriptions for trained model classes
        descriptions = {
            'pothole': f"A pothole has been detected on the road at {location}, creating a safety hazard for vehicles. {obj_summary}",
            'road_damage': f"Road surface damage has been identified at {location}. {obj_summary}",
            'illegal_parking': f"Illegal parking violation detected at {location}, causing traffic obstruction. {obj_summary}",
            'sign_damage': f"A damaged road sign has been found at {location}, affecting road safety. {obj_summary}",
            'fallen_tree': f"A fallen tree has been reported at {location}, blocking the road and creating hazard. {obj_summary}",
            'garbage': f"Littering and garbage accumulation detected at {location}, affecting sanitation. {obj_summary}",
            'vandalism': f"Vandalism has been reported at {location}, damaging public property. {obj_summary}",
            'dead_animal': f"Dead animal pollution detected at {location}, creating health hazard. {obj_summary}",
            'structure_damage': f"Damaged concrete structure at {location}, posing safety risk. {obj_summary}",
            'wire_damage': f"Damaged electrical wires/poles at {location}, creating electrical safety hazard. {obj_summary}",
        }
        
        if sub_category in descriptions:
            return descriptions[sub_category]
        
        if sub_category == 'pothole':
            return f"A pothole has been detected on the road at {location}, causing potential hazard to vehicles. {obj_summary}."
        if sub_category == 'broken_street_light':
            return f"A broken or non-functional street light has been identified at {location}, leading to poor visibility and safety concerns. {obj_summary}."
        if sub_category == 'garbage_heap':
            return f"A significant accumulation of garbage has been reported at {location}, requiring immediate clearance for sanitation. {obj_summary}."

        return (
            f"A {sub_display} issue (Category: {cat_display}) has been detected at {location}. "
            f"Image analysis confirmed: {obj_summary}. "
            f"This requires prompt attention from the concerned department to ensure public safety and maintain civic standards."
        )

    # ── Full analysis ─────────────────────────────────────────────────────────

    def analyze_civic_issue(self, image_path, location="unknown location",
                            existing_issues=None, department=None, user_description=""):
        import time
        import json
        t_start = time.time()

        print(f"[AI] ====== Starting analysis ======")
        
        objects  = self.analyze_image(image_path)
        
        print(f"[AI] YOLO returned {len(objects)} objects")
        
        # Use YOLO's category if available
        detected_category = None
        detected_subcategory = None
        for obj in objects:
            if 'category' in obj:
                detected_category = obj['category']
                detected_subcategory = obj.get('subclass', '')
                break
        
        # If YOLO detected category, use it
        if detected_category:
            category = detected_category
            sub_category = detected_subcategory
            cat_confidence = max((obj['confidence'] for obj in objects), default=85)
            print(f"[AI] SUCCESS - Using YOLO category: {category} / {sub_category}")
        else:
            # NO FALLBACK - Use user description to determine category
            print(f"[AI] YOLO no detection - Using description: '{user_description[:50]}...'")
            category, sub_category, cat_confidence = self.categorize_issue_from_description(user_description)
            print(f"[AI] Category from description: {category} / {sub_category}")
        
        description = self.generate_description(objects, location, category, sub_category, user_description=user_description)

        max_confidence = max((obj['confidence'] for obj in objects), default=cat_confidence)

        # Skip slow duplicate detection - removed for speed (was taking 15+ seconds)
        similar_issues = []
        is_duplicate = False
        duplicate_id = None

        # Fast severity calculation without embedding
        severity = max_confidence / 10
        if severity >= 8:
            severity_level = 'Critical'
        elif severity >= 6:
            severity_level = 'High'
        elif severity >= 4:
            severity_level = 'Medium'
        else:
            severity_level = 'Low'
            
        priority = calculate_priority(severity_level, category, department, location)

        sentiment_result = analyze_sentiment(description)
        assigned_dept, dept_confidence = smart_assign_department(category, description, objects)
        predicted_days = predict_resolution_days(category, severity_level)

        if sentiment_result['urgency_score'] > 0.6 and severity_level == 'Low':
            severity_level = 'Medium'
            priority = calculate_priority(severity_level, category, assigned_dept, location)

        elapsed_total = round(time.time() - t_start, 2)
        print(f"[AI] analyze_civic_issue completed in {elapsed_total}s")

        analysis_report = {
            'timestamp': datetime.now().isoformat(),
            'model_info': {'text': self.text_model, 'vision': 'YOLOv8n'},
            'detections': objects,
            'reasoning': f"Classified as {sub_category} under {category} with {cat_confidence}% confidence based on keyword and visual analysis.",
            'environmental_factors': {
                'location_context': 'High priority area' if 'hospital' in location.lower() or 'school' in location.lower() else 'Normal',
                'sentiment_urgency': round(sentiment_result['urgency_score'], 2)
            }
        }

        return {
            'description':              description,
            'category':                 category,
            'sub_category':             sub_category,
            'detected_objects':         objects,
            'confidence':               max_confidence,
            'severity':                 severity_level,
            'severity_score':           severity,
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
            'analysis_report':          json.dumps(analysis_report)
        }

def calculate_dynamic_severity_advanced(confidence, similar_issues, description, category):
    """Enhanced severity calculation"""
    from .civic_ai import assess_damage_severity
    score, level = assess_damage_severity(category, description, [])
    
    # Adjust based on confidence and duplicates
    if similar_issues and len(similar_issues) > 2:
        score += 1.0
        
    if confidence > 90:
        score += 0.5
        
    score = min(10.0, max(1.0, score))
    
    if score >= 8: level = 'Critical'
    elif score >= 6: level = 'High'
    elif score >= 4: level = 'Medium'
    else: level = 'Low'
    
    return round(score, 1), level

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