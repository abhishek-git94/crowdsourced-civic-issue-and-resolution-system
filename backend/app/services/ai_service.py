import ollama
from ultralytics import YOLO
import chromadb
from datetime import datetime
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
        
        print(f"🚀 Civic AI Analyzer initialized with Ollama model: {self.text_model}")
        print(f"🔥 Loading YOLO model from: {self.yolo_model}")

        self.yolo = YOLO(self.yolo_model)
        
        try:
            self.chroma_client = chromadb.Client()
            self.collection = self.chroma_client.get_or_create_collection(
                name="civic_issues",
                metadata={"description": "Historical civic issues"}
            )
            print("✅ RAG system initialized")
        except Exception as e:
            print(f"⚠️ RAG initialization failed: {e}")
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
                
                if confidence > 0.3:
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
            print(f"⚠️ RAG search failed: {e}")
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
            print(f"⚠️ Ollama error: {e}")
            return f"A {category.replace('_', ' ')} issue has been detected at {location}. The image shows {object_summary}. Immediate attention recommended."

    def analyze_civic_issue(self, image_path, location="unknown location"):
        objects = self.analyze_image(image_path)
        category = self.categorize_issue(objects)
        description = self.generate_description(objects, location, category)
        
        # Use SVM NLP Classifier for severity if description is available
        if description:
            severity = nlp_classifier.predict_severity(description)
        else:
            max_confidence = max([obj['confidence'] for obj in objects], default=0)
            if max_confidence > 80:
                severity = 'High'
            elif max_confidence > 50:
                severity = 'Medium'
            else:
                severity = 'Low'
        
        # RNN component (future scope integration)
        # prediction = rnn_predictor.predict_resolution_days(category, [])
        
        return {
            'description': description,
            'category': category,
            'detected_objects': objects,
            'confidence': max_confidence,
            'severity': severity
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
            print(f"⚠️ Failed to add to RAG: {e}")
