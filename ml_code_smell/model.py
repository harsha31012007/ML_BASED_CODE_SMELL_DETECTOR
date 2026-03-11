import joblib  # type: ignore
import numpy as np  # type: ignore
from sklearn.ensemble import RandomForestClassifier  # type: ignore
import os

class SmellDetectorModel:
    def __init__(self, model_path='model.pkl'):
        self.model_path = model_path
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False

    def train(self, X, y):
        """Trains the Random Forest model."""
        self.model.fit(X, y)
        self.is_trained = True
        print("Model trained successfully.")

    def predict(self, features):
        """Predicts if code has smells based on features."""
        if not self.is_trained:
            self.load()
        
        if len(np.array(features).shape) == 1:
            features = np.array(features).reshape(1, -1)
            
        prediction = self.model.predict(features)
        probability = self.model.predict_proba(features)
        return prediction[0], probability[0]

    def save(self):
        """Saves the trained model to disk."""
        if self.is_trained:
            joblib.dump(self.model, self.model_path)
            print(f"Model saved to {self.model_path}")
        else:
            print("Model is not trained. Cannot save.")

    def load(self):
        """Loads the trained model from disk."""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            self.is_trained = True
            print(f"Model loaded from {self.model_path}")
        else:
            print("Model file not found. Please train the model first.")
