import numpy as np
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
import joblib

class CivicNLPClassifier:
    """SVM-based classifier for categorizing issue severity from text."""
    def __init__(self):
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(stop_words='english')),
            ('clf', SVC(probability=True, kernel='linear'))
        ])
        self.is_trained = False
        self._train_baseline()

    def _train_baseline(self):
        """Train with a few examples to ensure it works immediately."""
        X = [
            "There is a massive pothole in the middle of the main road, very dangerous.",
            "Small crack on the sidewalk, not a big deal.",
            "Garbage is overflowing and attracting rats, health hazard!",
            "Street light is flickering occasionally.",
            "Broken water pipe flooding the entire street!",
            "Slight faded paint on the crosswalk.",
            "Dead animal on the road causing traffic.",
            "Graffiti on a park bench."
        ]
        # 0: Low, 1: Medium, 2: High
        y = [2, 0, 2, 0, 2, 0, 1, 0]
        
        self.pipeline.fit(X, y)
        self.is_trained = True

    def predict_severity(self, text):
        if not text:
            return "Low"
        
        # 0->Low, 1->Medium, 2->High
        severity_map = {0: "Low", 1: "Medium", 2: "High"}
        pred = self.pipeline.predict([text])[0]
        return severity_map.get(pred, "Low")

class CivicRNNPredictor:
    """RNN-based predictor for sequence data (e.g., resolution time prediction)."""
    def __init__(self):
        self.model_loaded = False
        # In a real scenario, we'd load a Keras/PyTorch model here
        
    def predict_resolution_days(self, issue_type, location_history):
        """
        Predicts how many days it might take to resolve.
        location_history could be a list of past resolution times in that area.
        """
        # Baseline logic until a real RNN is trained
        base_days = {"pothole": 5, "garbage": 2, "traffic": 1, "infrastructure": 10}
        days = base_days.get(issue_type.lower(), 4)
        
        if location_history and len(location_history) > 0:
            avg_past = sum(location_history) / len(location_history)
            return round((days + avg_past) / 2)
        
        return days

# Singleton instances
nlp_classifier = CivicNLPClassifier()
rnn_predictor = CivicRNNPredictor()
