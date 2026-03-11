import joblib  # type: ignore
import pandas as pd  # type: ignore
import numpy as np  # type: ignore
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import seaborn as sns  # type: ignore

def evaluate():
    print("Loading models and test data...")
    try:
        trained_models = joblib.load('all_models.pkl')
        X_test, y_test = joblib.load('test_data.pkl')
        le = joblib.load('label_encoder.pkl')
    except FileNotFoundError:
        print("Required files not found. Run train_model.py first.")
        return

    results = []
    best_f1 = 0
    best_model_name = ""

    for name, model in trained_models.items():
        y_pred = model.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        # Using macro average for multi-class
        prec = precision_score(y_test, y_pred, average='macro', zero_division=0)
        rec = recall_score(y_test, y_pred, average='macro', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='macro', zero_division=0)
        
        results.append({
            "Model": name,
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1-score": f1
        })
        
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name

    # Comparison Table
    comparison_df = pd.DataFrame(results)
    print("\nModel Comparison Table:")
    print(comparison_df.to_string(index=False))
    
    # Save the best model
    print(f"\nBest Model: {best_model_name} (F1: {best_f1:.4f})")
    joblib.dump(trained_models[best_model_name], 'code_smell_model.pkl')
    print(f"Saved {best_model_name} as code_smell_model.pkl")

    # Confusion Matrix for the best model
    best_model = trained_models[best_model_name]
    y_pred_best = best_model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred_best)
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', xticklabels=le.classes_, yticklabels=le.classes_)
    plt.title(f'Confusion Matrix - {best_model_name}')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.savefig('confusion_matrix.png')
    print("Confusion matrix saved as confusion_matrix.png")

if __name__ == "__main__":
    evaluate()
