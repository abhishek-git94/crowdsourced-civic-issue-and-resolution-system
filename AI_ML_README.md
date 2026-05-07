# AI/ML Features Documentation

This document explains all AI and Machine Learning components in the JanSuvidha system.

---

## Table of Contents
1. [System Overview](#system-overview)
2. [YOLO Object Detection](#1-yolo-object-detection)
3. [SVM Severity Classification](#2-svm-severity-classification)
4. [LSTM Resolution Prediction](#3-lstm-resolution-prediction)
5. [RAG System (ChromaDB + Ollama)](#4-rag-system-chromadb--ollama)
6. [Duplicate Detection](#5-duplicate-detection)
7. [Image Enhancement](#6-image-enhancement)
8. [Complete Pipeline Flow](#complete-pipeline-flow)
9. [Model Files](#model-files)
10. [Configuration](#configuration)

---

## System Overview

The AI/ML system handles civic issue detection, classification, and management through multiple components:

| Component | Purpose | Technology |
|-----------|---------|------------|
| Object Detection | Identify issues in images | YOLOv8 |
| Severity Classification | Categorize issue severity (Low/Medium/High) | SVM + TF-IDF |
| Resolution Prediction | Estimate fix time | LSTM (TensorFlow) |
| Semantic Search | Find similar past issues | ChromaDB |
| Description Generation | Auto-generate issue reports | Ollama (LLM) |
| Duplicate Detection | Find duplicate issues | Embeddings + Cosine Similarity |

---

## 1. YOLO Object Detection

### Purpose
Automatically detect civic infrastructure issues from user-uploaded images.

### How It Works
1. Load pre-trained YOLO model (`last_jansuvidha.pt`)
2. Run inference on the uploaded image
3. Filter detections with confidence > 30%
4. Map detected objects to civic categories

### Category Mapping
```
pothole        → ['crack', 'hole', 'damaged']
garbage        → ['bottle', 'trash', 'bag', 'cup']
traffic        → ['car', 'truck', 'bus', 'traffic light']
street_furniture → ['bench', 'stop sign']
infrastructure → ['fire hydrant', 'parking meter']
road_damage    → ['road', 'street']
```

### Code Location
`backend/app/services/ai_service.py` - `analyze_image()` method

### Example Output
```python
[
    {'label': 'pothole', 'confidence': 85.5},
    {'label': 'crack', 'confidence': 72.3}
]
```

---

## 2. SVM Severity Classification

### Purpose
Classify civic issues into severity levels based on text description.

### How It Works
1. Convert text description using TF-IDF vectorizer
2. Pass through trained SVM classifier
3. Output severity level: Low (0), Medium (1), or High (2)

### Training Data
The model is trained on synthetic data covering various scenarios:

| Severity | Examples |
|----------|----------|
| High (2) | "massive pothole", "broken water pipe", "exposed live wires", "open manhole" |
| Medium (1) | "dead animal", "garbage overflow", "street light out", "traffic light stuck" |
| Low (0) | "small crack", "flickering light", "faded paint", "graffiti" |

### Code Location
`backend/app/services/ml_service.py` - `CivicNLPClassifier` class

### Usage
```python
from backend.app.services.ml_service import nlp_classifier

severity = nlp_classifier.predict_severity("Huge pothole on main road")
# Returns: "High"
```

---

## 3. LSTM Resolution Prediction

### Purpose
Predict how many days an issue will take to resolve based on historical data.

### How It Works
1. Take sequence of past resolution times for similar issues
2. Normalize values (0-1 scale, max 30 days)
3. Pass through LSTM neural network
4. Denormalize output to get predicted days

### Base Estimates (Fallback)
```python
{
    "pothole": 5,
    "garbage": 2,
    "traffic": 1,
    "infrastructure": 10
}
```

### Code Location
`backend/app/services/ml_service.py` - `CivicRNNPredictor` class

### Usage
```python
from backend.app.services.ml_service import rnn_predictor

days = rnn_predictor.predict_resolution_days("pothole", [4, 6, 5])
# Returns: estimated days (e.g., 5)
```

---

## 4. RAG System (ChromaDB + Ollama)

### Purpose
- Store historical issues as embeddings
- Search for similar past issues
- Generate professional descriptions using LLM

### Components

#### ChromaDB Vector Store
- Collection name: `civic_issues`
- Stores: document text, metadata (issue_id, category, location, timestamp)
- Used for semantic similarity search

#### Ollama LLM
- Model: Configurable (default: `llama3`)
- Generates: Issue descriptions for municipal reports

### Description Generation Prompt
```
You are writing a civic infrastructure issue report for municipal authorities.

LOCATION: {location}
DETECTED IN IMAGE: {object_summary}
ISSUE CATEGORY: {category}

Write a professional 2-3 sentence description:
1. State what the problem is
2. Mention location type
3. Explain why it needs attention
```

### Code Location
- RAG: `backend/app/services/ai_service.py` - `CivicAIAnalyzer` class
- Search: `search_similar_issues()` method
- Generation: `generate_description()` method

---

## 5. Duplicate Detection

### Purpose
Find if a new issue is a duplicate of an existing one.

### How It Works
1. Generate embedding for new issue text
2. Compare with recent issues (configurable count, default: 50)
3. Calculate cosine similarity
4. Flag as duplicate if similarity > threshold (default: 0.78)

### Embedding Methods
- **Local**: Random 384-dim vector (placeholder, needs sentence-transformer)
- **OpenAI**: Placeholder for OpenAI embedding API

### Code Location
`backend/app/utils/duplicate_detector.py`

### Configuration
```python
SIMILARITY_THRESHOLD = 0.78  # Minimum score to be considered duplicate
RECENT_CHECK_COUNT = 50      # How many recent issues to check
```

---

## 6. Image Enhancement

### Purpose
Improve image quality before YOLO inference using CLAHE (Contrast Limited Adaptive Histogram Equalization).

### Process
1. Convert image to LAB color space
2. Apply CLAHE to L-channel (preserves colors)
3. Merge channels back
4. Return enhanced image

### Benefits
- Better detection in low-light conditions
- Improved contrast for dark/bright areas

### Code Location
`backend/app/services/ai_service.py` - `enhance_image()` function

---

## Complete Pipeline Flow

```
User uploads image
       ↓
[Image Enhancement] ← CLAHE preprocessing
       ↓
[YOLO Detection] ← Detect objects in image
       ↓
[Category Mapping] ← Map objects to civic categories
       ↓
[Ollama Description] ← Generate issue description
       ↓
[SVM Severity] ← Classify severity from description
       ↓
[ChromaDB Search] ← Find similar past issues
       ↓
[Duplicate Check] ← Compare with recent issues
       ↓
[Save to Knowledge Base] ← Store for future reference
       ↓
Final Issue Object
{
    "description": "...",
    "category": "pothole",
    "detected_objects": [...],
    "confidence": 85.5,
    "severity": "High"
}
```

---

## Model Files

| File | Type | Purpose |
|------|------|---------|
| `last_jansuvidha.pt` | YOLOv8 | Main object detection model |
| `yolov8n.pt` | YOLOv8 | Nano variant (lighter) |
| `yolov8s.pt` | YOLOv8 | Small variant |
| `yolo11n.pt` | YOLO11 | Newer YOLO version |
| `svm_severity_model.pkl` | Scikit-learn | SVM severity classifier |
| `lstm_resolution_model.keras` | TensorFlow | LSTM resolution predictor |

**Location**: `models_ai/`

---

## Configuration

All AI/ML settings are in `backend/app/config.py`:

```python
# Database
MONGODB_SETTINGS = {'host': 'mongodb://localhost:27017/JanSuvidha'}

# Duplicate Detection
EMBED_BACKEND = "local"
SIMILARITY_THRESHOLD = 0.78
RECENT_CHECK_COUNT = 50

# AI Models
OLLAMA_MODEL = "llama3"
YOLO_MODEL_PATH = "models_ai/last_jansuvidha.pt"
```

### Environment Variables (.env)
```
SECRET_KEY=your_secret_key
MONGODB_URI=mongodb://localhost:27017/JanSuvidha
EMBED_BACKEND=local
OLLAMA_MODEL=llama3
SIMILARITY_THRESHOLD=0.78
```

---

## Dependencies

```
# Core ML
flask
mongoengine
ultralytics           # YOLOv8
tensorflow            # LSTM (optional)
scikit-learn          # SVM

# NLP & Vector DB
langchain
langchain-ollama
chromadb

# Utilities
numpy
pandas
opencv-python        # Image enhancement
```

---

## Future Improvements

1. **Replace placeholder embeddings** with sentence-transformers (e.g., `all-MiniLM-L6-v2`)
2. **Add OpenAI embedding integration** for better semantic matching
3. **Train custom YOLO model** on domain-specific civic issue dataset
4. **Expand LSTM training data** with real historical resolution times
5. **Add image quality assessment** before processing

---

## Quick Reference

| Task | Command/Code |
|------|--------------|
| Run YOLO detection | `analyzer.analyze_image(image_path)` |
| Classify severity | `nlp_classifier.predict_severity(text)` |
| Predict resolution | `rnn_predictor.predict_resolution_days(category, history)` |
| Search similar issues | `analyzer.search_similar_issues(category, location)` |
| Generate description | `analyzer.generate_description(objects, location)` |
| Full analysis | `analyzer.analyze_civic_issue(image_path, location)` |

---

*Generated for JanSuvidha - AI-Driven Civic Issue Management System*