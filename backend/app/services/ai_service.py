import ollama
from ultralytics import YOLO
import chromadb
from datetime import datetime, timedelta
import os
import cv2
from ..utils.duplicate_detector import (
    get_local_embedding,
    get_openai_embedding,
    cosine_similarity,
    embed_to_json,
    json_to_embed
)
from ..config import Config
from .ml_service import nlp_classifier, rnn_predictor
from .advanced_ai import (
    analyze_sentiment,
    smart_assign_department,
    predict_resolution_days,
    cluster_issues,
    detect_anomalies,
    natural_language_query
)


def calculate_dynamic_severity(confidence, similar_issues):
    """
    Calculate severity based on:
    1. Confidence level (0-100)
    2. Number of similar reports
    3. Recency of similar reports (recent = higher severity)
    
    Returns: 'Low', 'Medium', 'High'
    """
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
    
    confidence_score = confidence
    report_score = min(num_similar * 15, 60)
    
    total_score = (
        (confidence_score * 0.30) +
        (report_score * 0.40) +
        (recency_score * 10 * 0.30)
    )
    
    if total_score >= 60:
        return 'High'
    elif total_score >= 35:
        return 'Medium'
    return 'Low'


def calculate_priority(severity, category, department):
    """
    Calculate priority based on:
    1. Severity (already computed)
    2. Category type (infrastructure > sanitation > parks > other)
    3. Department workload (fewer pending = higher priority)
    
    Returns: 'Low', 'Medium', 'High', 'Urgent'
    """
    severity_scores = {'Low': 1, 'Medium': 2, 'High': 3}
    base_score = severity_scores.get(severity, 1)
    
    # Category priority
    category_priority = {
        'infrastructure': 3,
        'roads': 3,
        'water': 3,
        'electricity': 3,
        'sanitation': 2,
        'garbage': 2,
        'parks': 1,
        'other': 1
    }
    cat_score = category_priority.get(category.lower() if category else 'other', 1)
    
    # Department factor (simulated - in real app would query dept workload)
    dept_score = 2
    
    total_priority = (base_score * 0.5) + (cat_score * 0.3) + (dept_score * 0.2)
    
    if total_priority >= 2.5:
        return 'Urgent'
    elif total_priority >= 2.0:
        return 'High'
    elif total_priority >= 1.5:
        return 'Medium'
    return 'Low'


def check_duplicate_threshold(similar_issues, min_similarity=0.75):
    """
    Check if any similar issue exceeds the duplicate threshold.
    Returns: (is_duplicate, matching_issue_id or None)
    """
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
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    merged = cv2.merge((cl, a, b))
    enhanced = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
    return enhanced

class CivicAIAnalyzer:
    def __init__(self, text_model=None, yolo_model=None):
        self.text_model = text_model or Config.OLLAMA_MODEL
        self.yolo_model = yolo_model or Config.YOLO_MODEL_PATH
        self.conf_threshold = Config.YOLO_CONF_THRESHOLD
        
        print(f"Civic AI Analyzer initialized with Ollama model: {self.text_model}")
        print(f"Loading YOLO model from: {self.yolo_model}")

        self.yolo = YOLO(self.yolo_model)
        
        try:
            self.chroma_client = chromadb.Client()
            self.collection = self.chroma_client.get_or_create_collection(
                name="civic_issues",
                metadata={"description": "Historical civic issues"}
            )
            print("RAG system initialized")
        except Exception as e:
            print(f"RAG initialization failed: {e}")
            self.collection = None
        
        self.civic_mapping = {
            'pothole': ['crack', 'hole', 'damaged'],
            'garbage': ['bottle', 'trash', 'bag', 'cup'],
            'traffic': ['car', 'truck', 'bus', 'traffic light'],
            'street_furniture': ['bench', 'stop sign'],
            'infrastructure': ['fire hydrant', 'parking meter']
        }

    def analyze_image(self, image_path):
        image = cv2.imread(image_path)
        if image is None:
            return [{'label': 'unknown object', 'confidence': 0}]

        image = enhance_image(image)
        results = self.yolo(image, verbose=False)
        detected_objects = []

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = r.names[cls_id]
                confidence = float(box.conf[0])
                
                if confidence > Config.YOLO_CONF_THRESHOLD:
                    detected_objects.append({
                        'label': label,
                        'confidence': round(confidence * 100, 1)
                    })

        if not detected_objects:
            detected_objects = [{'label': 'unknown object', 'confidence': 0}]
        
        return detected_objects

    def categorize_issue(self, objects):
        object_labels = [obj['label'].lower() for obj in objects]
        for category, keywords in self.civic_mapping.items():
            for keyword in keywords:
                if any(keyword in label for label in object_labels):
                    return category
        
        if any(word in label for label in object_labels for word in ['road', 'street']):
            return 'road_damage'
        return 'general_infrastructure'

    def search_similar_issues(self, category, location):
        if not self.collection:
            return []
        try:
            query_text = f"Category: {category}, Location: {location}"
            results = self.collection.query(
                query_texts=[query_text],
                n_results=2
            )
            similar_issues = []
            if results['documents'] and results['documents'][0]:
                for doc in results['documents'][0]:
                    similar_issues.append({'description': doc})
            return similar_issues
        except Exception as e:
            print(f"RAG search failed: {e}")
            return []

    def generate_description(self, objects, location="unknown location", category=None):
        if not category:
            category = self.categorize_issue(objects)
        
        object_summary = ", ".join([f"{obj['label']} ({obj['confidence']}%)" for obj in objects[:3]])
        similar_issues = self.search_similar_issues(category, location)
        
        context = ""
        if similar_issues:
            context = f"\n\nNOTE: This location has {len(similar_issues)} similar past issue(s)."
        
        prompt = f"""You are writing a civic infrastructure issue report for municipal authorities.

LOCATION: {location}
DETECTED IN IMAGE: {object_summary}
ISSUE CATEGORY: {category}
{context}

Write a professional 2-3 sentence description for this civic issue report.

Requirements:
1. State what the problem is clearly
2. Mention the location type (road/sidewalk/public area)
3. Explain why it needs attention (safety/maintenance)
4. Keep it factual and concise
5. Do NOT use markdown, bullets, or special formatting

Write the description now:"""

        try:
            response = ollama.chat(
                model=self.text_model,
                messages=[{"role": "user", "content": prompt}]
            )
            description = response["message"]["content"].strip()
            description = description.replace('**', '').replace('*', '').replace('\n\n', ' ').replace('\n', ' ')
            return description
        except Exception as e:
            print(f"Ollama error: {e}")
            return f"A {category.replace('_', ' ')} issue has been detected at {location}. The image shows {object_summary}. Immediate attention recommended."

    def analyze_civic_issue(self, image_path, location="unknown location", existing_issues=None, department=None):
        objects = self.analyze_image(image_path)
        category = self.categorize_issue(objects)
        description = self.generate_description(objects, location, category)
        
        max_confidence = max([obj['confidence'] for obj in objects], default=0)

        similar_issues = []
        if existing_issues and description:
            try:
                embedding = get_local_embedding(description)
                from ..utils.duplicate_detector import find_similar_issues
                similar_issues = find_similar_issues(existing_issues, embedding, top_k=10, min_score=0.5)
            except Exception as e:
                print(f"Duplicate detection failed: {e}")

        severity = calculate_dynamic_severity(max_confidence, similar_issues)
        priority = calculate_priority(severity, category, department)
        
        is_duplicate, duplicate_id = check_duplicate_threshold(similar_issues, min_similarity=0.75)
        
        # Sentiment Analysis from user description
        sentiment_result = analyze_sentiment(description)
        
        # Smart Department Assignment
        assigned_dept, dept_confidence = smart_assign_department(category, description, objects)
        
        # Resolution Prediction
        predicted_days = predict_resolution_days(category, severity)
        
        # Upgrade severity/priority based on sentiment urgency
        if sentiment_result['urgency_score'] > 0.6 and severity == 'Low':
            severity = 'Medium'
            priority = calculate_priority(severity, category, assigned_dept)
        
        return {
            'description': description,
            'category': category,
            'detected_objects': objects,
            'confidence': max_confidence,
            'severity': severity,
            'priority': priority,
            'similar_issues_count': len(similar_issues),
            'duplicate_detected': is_duplicate,
            'duplicate_of': duplicate_id,
            'similar_issues': similar_issues[:3] if similar_issues else [],
            # New AI features
            'sentiment': sentiment_result['sentiment'],
            'urgency_score': round(sentiment_result['urgency_score'], 2),
            'assigned_department': assigned_dept,
            'department_confidence': round(dept_confidence, 2),
            'predicted_resolution_days': predicted_days
        }

    def add_to_knowledge_base(self, issue_id, description, category, location):
        if not self.collection:
            return
        try:
            doc_text = f"Category: {category}\nLocation: {location}\nDescription: {description}"
            self.collection.add(
                documents=[doc_text],
                ids=[f"issue_{issue_id}"],
                metadatas=[{
                    'issue_id': issue_id,
                    'category': category,
                    'location': location,
                    'timestamp': datetime.now().isoformat()
                }]
            )
        except Exception as e:
            print(f"Failed to add to RAG: {e}")
