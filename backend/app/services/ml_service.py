import numpy as np
import os
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
import joblib

# Optional TensorFlow import (if installed)
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Embedding
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

class CivicNLPClassifier:
    """SVM-based classifier for categorizing issue severity from text."""
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'models_ai', 'svm_severity_model.pkl')
        self.pipeline = None
        self.is_trained = False
        self._load_or_train()

    def _load_or_train(self):
        """Load trained model if exists, otherwise train a robust baseline."""
        if os.path.exists(self.model_path):
            try:
                self.pipeline = joblib.load(self.model_path)
                self.is_trained = True
                print("✅ SVM Model loaded successfully.")
                return
            except Exception as e:
                print(f"⚠️ Failed to load SVM model: {e}")
        
        print("⚙️ Training new SVM Model with expanded dataset...")
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(stop_words='english', ngram_range=(1, 2))),
            ('clf', SVC(probability=True, kernel='linear', C=1.0))
        ])
        
        # Expanded synthetic dataset for better training
        X = [
            # High Severity (2)
            "There is a massive pothole in the middle of the main road, very dangerous.",
            "Broken water pipe flooding the entire street!",
            "Exposed live wires hanging from the street light pole.",
            "Huge open manhole in the middle of the sidewalk.",
            "Bridge has a large structural crack and feels unstable.",
            "Severe flooding blocking the main intersection.",
            # Medium Severity (1)
            "Dead animal on the road causing traffic and bad smell.",
            "Large pile of garbage is overflowing and attracting rats, health hazard!",
            "Street light is completely out on my block.",
            "Deep crack on the road edge causing bumpy rides.",
            "Fallen tree branch partially blocking the lane.",
            "Traffic light is stuck on red.",
            # Low Severity (0)
            "Small crack on the sidewalk, not a big deal.",
            "Street light is flickering occasionally.",
            "Slight faded paint on the crosswalk.",
            "Graffiti on a park bench.",
            "A few scattered trash bags near the bin.",
            "Signpost is slightly bent."
        ]
        y = [2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
        
        self.pipeline.fit(X, y)
        self.is_trained = True
        
        # Save model
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.pipeline, self.model_path)
            print("✅ SVM Model trained and saved.")
        except Exception as e:
            print(f"⚠️ Could not save SVM model: {e}")

    def predict_severity(self, text):
        if not text:
            return "Low"
        
        severity_map = {0: "Low", 1: "Medium", 2: "High"}
        pred = self.pipeline.predict([text])[0]
        return severity_map.get(pred, "Low")


class CivicRNNPredictor:
    """RNN-based predictor for sequence data (e.g., resolution time prediction)."""
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'models_ai', 'lstm_resolution_model.keras')
        self.model = None
        self.is_trained = False
        if TF_AVAILABLE:
            self._load_or_train()

    def _load_or_train(self):
        if os.path.exists(self.model_path):
            try:
                self.model = load_model(self.model_path)
                self.is_trained = True
                print("✅ LSTM RNN Model loaded successfully.")
                return
            except Exception as e:
                print(f"⚠️ Failed to load LSTM model: {e}")
        
        print("⚙️ Training new LSTM RNN Model...")
        
        # Create a simple synthetic sequential dataset
        # X: sequence of past resolution times (normalized 0-1)
        # y: next resolution time
        np.random.seed(42)
        X_train = np.random.rand(100, 5, 1) # 100 sequences of length 5
        y_train = np.mean(X_train, axis=1) + (np.random.rand(100, 1) * 0.1) # next is avg + noise
        
        self.model = Sequential([
            LSTM(32, input_shape=(5, 1), return_sequences=False),
            Dense(16, activation='relu'),
            Dense(1, activation='linear')
        ])
        self.model.compile(optimizer='adam', loss='mse')
        self.model.fit(X_train, y_train, epochs=10, verbose=0)
        self.is_trained = True
        
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            self.model.save(self.model_path)
            print("✅ LSTM Model trained and saved.")
        except Exception as e:
            print(f"⚠️ Could not save LSTM model: {e}")

    def predict_resolution_days(self, issue_type, location_history):
        """
        Predicts how many days it might take to resolve using the LSTM model.
        location_history should be a list of past resolution times (in days) in that area.
        """
        base_days = {"pothole": 5, "garbage": 2, "traffic": 1, "infrastructure": 10}
        default_days = base_days.get(issue_type.lower(), 4)
        
        if not TF_AVAILABLE or not self.is_trained:
            # Fallback if no TF
            if location_history and len(location_history) > 0:
                return round((default_days + sum(location_history) / len(location_history)) / 2)
            return default_days

        # Prepare sequence (pad or truncate to length 5)
        seq = location_history[-5:] if location_history else []
        while len(seq) < 5:
            seq.insert(0, default_days) # pad with default
            
        # Normalize (assuming max days = 30)
        max_days = 30.0
        seq_norm = np.array(seq) / max_days
        seq_input = np.reshape(seq_norm, (1, 5, 1))
        
        try:
            pred_norm = self.model.predict(seq_input, verbose=0)[0][0]
            pred_days = pred_norm * max_days
            return max(1, round(pred_days))
        except Exception as e:
            print(f"⚠️ RNN Prediction error: {e}")
            return default_days

# Singleton instances
nlp_classifier = CivicNLPClassifier()
rnn_predictor = CivicRNNPredictor()
