import ollama
from ultralytics import YOLO
import chromadb
from datetime import datetime
import os

class CivicAIAnalyzer:
    def __init__(self, text_model="phi", yolo_model="yolov8n.pt"):
        """Initialize with Phi model (CPU mode recommended)"""
        self.text_model = text_model
        self.yolo_model = yolo_model
        print(f"🚀 Civic AI Analyzer initialized with Ollama model: {text_model}")
        
        # Load YOLO
        model_path = os.path.join(os.path.dirname(__file__), "last.pt")
        print("🔥 Loading YOLO model from:", model_path)

        self.yolo = YOLO(model_path)


        
        # Initialize RAG (ChromaDB)
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
        
        # Civic issue mapping
        self.civic_mapping = {
            'pothole': ['crack', 'hole', 'damaged'],
            'garbage': ['bottle', 'trash', 'bag', 'cup'],
            'traffic': ['car', 'truck', 'bus', 'traffic light'],
            'street_furniture': ['bench', 'stop sign'],
            'infrastructure': ['fire hydrant', 'parking meter']
        }

    def analyze_image(self, image_path):
        """Detect objects using YOLO"""
        print(f"🔍 Analyzing image: {image_path}")
        results = self.yolo(image_path, verbose=False)
        detected_objects = []

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = r.names[cls_id]
                confidence = float(box.conf[0])
                
                if confidence > 0.3:  # Only confident detections
                    detected_objects.append({
                        'label': label,
                        'confidence': round(confidence * 100, 1)
                    })

        if not detected_objects:
            detected_objects = [{'label': 'unknown object', 'confidence': 0}]

        print(f"✅ Detected {len(detected_objects)} objects")
        for obj in detected_objects[:3]:
            print(f"   - {obj['label']}: {obj['confidence']}%")
        
        return detected_objects

    def categorize_issue(self, objects):
        """Categorize civic issue from detected objects"""
        object_labels = [obj['label'].lower() for obj in objects]
        
        for category, keywords in self.civic_mapping.items():
            for keyword in keywords:
                if any(keyword in label for label in object_labels):
                    return category
        
        if any(word in label for label in object_labels for word in ['road', 'street']):
            return 'road_damage'
        
        return 'general_infrastructure'

    def search_similar_issues(self, category, location):
        """Search RAG for similar past issues"""
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
        """Generate description using Ollama"""
        
        if not category:
            category = self.categorize_issue(objects)
        
        # Object summary
        object_summary = ", ".join([f"{obj['label']} ({obj['confidence']}%)" 
                                   for obj in objects[:3]])
        
        # Search similar issues
        similar_issues = self.search_similar_issues(category, location)
        
        # Build context
        context = ""
        if similar_issues:
            context = f"\n\nNOTE: This location has {len(similar_issues)} similar past issue(s)."
        
        # Create prompt
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

        print(f"🧠 Asking Ollama ({self.text_model})...")
        
        try:
            response = ollama.chat(
                model=self.text_model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            description = response["message"]["content"].strip()
            
            # Clean formatting
            description = description.replace('**', '').replace('*', '')
            description = description.replace('\n\n', ' ').replace('\n', ' ')
            
            print(f"✅ Description generated ({len(description)} chars)")
            return description
            
        except Exception as e:
            print(f"⚠️ Ollama error: {e}")
            return f"A {category.replace('_', ' ')} issue has been detected at {location}. The image shows {object_summary}. Immediate attention recommended."

    def analyze_civic_issue(self, image_path, location="unknown location"):
        """Complete analysis pipeline"""
        print("\n" + "="*60)
        print("🚀 STARTING CIVIC ISSUE ANALYSIS")
        print("="*60)
        
        # Detect objects
        objects = self.analyze_image(image_path)
        
        # Categorize
        category = self.categorize_issue(objects)
        print(f"📋 Category: {category}")
        
        # Generate description
        description = self.generate_description(objects, location, category)
        
        # Determine severity
        max_confidence = max([obj['confidence'] for obj in objects], default=0)
        if max_confidence > 80:
            severity = 'high'
        elif max_confidence > 50:
            severity = 'medium'
        else:
            severity = 'low'
        
        print("="*60)
        print("✅ ANALYSIS COMPLETE")
        print("="*60 + "\n")
        
        return {
            'description': description,
            'category': category,
            'detected_objects': objects,
            'confidence': max_confidence,
            'severity': severity
        }

    def add_to_knowledge_base(self, issue_id, description, category, location):
        """Add resolved issue to RAG"""
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
            print(f"✅ Issue #{issue_id} added to knowledge base")
        except Exception as e:
            print(f"⚠️ Failed to add to RAG: {e}")


# Test
if __name__ == "__main__":
    analyzer = CivicAIAnalyzer(text_model="phi")
    
    img = "sample.jpg"
    if os.path.exists(img):
        result = analyzer.analyze_civic_issue(img, location="Main Street")
        print(f"\n📝 Description:\n{result['description']}")
    else:
        print("⚠️ sample.jpg not found. Place an image and test.")