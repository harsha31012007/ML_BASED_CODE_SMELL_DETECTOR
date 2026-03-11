import os
import pandas as pd  # type: ignore
import numpy as np  # type: ignore
import joblib  # type: ignore
from ml_code_smell.feature_extractor import ComprehensiveFeatureExtractor  # type: ignore
from sklearn.model_selection import train_test_split  # type: ignore
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier  # type: ignore
from sklearn.svm import SVC  # type: ignore
from sklearn.linear_model import LogisticRegression  # type: ignore
from sklearn.neural_network import MLPClassifier  # type: ignore
from sklearn.preprocessing import LabelEncoder  # type: ignore

def train_all_models(X, y):
    models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
        "SVM": SVC(probability=True, random_state=42),
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Neural Network": MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42)
    }
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    trained_models = {}
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        trained_models[name] = model
        
    return trained_models, X_test, y_test

def main():
    dataset_path = "code_smell_dataset.csv"
    if not os.path.exists(dataset_path):
        print("Dataset not found. Please run generate_dataset.py first.")
        return

    print("Loading dataset and extracting features...")
    df = pd.read_csv(dataset_path)
    extractor = ComprehensiveFeatureExtractor()
    
    X = []
    for code in df['code_snippet']:
        X.append(extractor.extract_features(code))
    
    X = np.array(X)
    
    # Encode labels
    le = LabelEncoder()
    y = le.fit_transform(df['smell_label'])
    joblib.dump(le, 'label_encoder.pkl')
    
    trained_models, X_test, y_test = train_all_models(X, y)
    
    # Save all models for evaluation
    joblib.dump(trained_models, 'all_models.pkl')
    joblib.dump((X_test, y_test), 'test_data.pkl')
    print("Training complete. Models and test data saved.")

if __name__ == "__main__":
    main()
