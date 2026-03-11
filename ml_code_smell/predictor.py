import joblib  # type: ignore
import pandas as pd  # type: ignore
import numpy as np  # type: ignore
import shap  # type: ignore
from .feature_extractor import ComprehensiveFeatureExtractor  # type: ignore

def predict_code_smell(code_snippet):
    """
    Predicts the code smell for a given snippet and provides SHAP explanations.
    """
    try:
        # Load best model and label encoder
        model = joblib.load('code_smell_model.pkl')
        le = joblib.load('label_encoder.pkl')
        extractor = ComprehensiveFeatureExtractor()
        
        # Extract features
        features = extractor.extract_features(code_snippet)
        feature_vector = np.array(features).reshape(1, -1)
        
        # Predict
        prediction_idx = model.predict(feature_vector)[0]
        prediction_probs = model.predict_proba(feature_vector)[0]
        
        smell = le.classes_[prediction_idx]
        confidence = prediction_probs[prediction_idx]
        
        # SHAP Explanation
        try:
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(feature_vector)
            
            class_idx = prediction_idx
            if isinstance(shap_values, list):
                sv = shap_values[class_idx]
            else:
                sv = shap_values
                
            feature_names = [
                'lines_of_code', 'number_of_functions', 'number_of_classes', 'cyclomatic_complexity',
                'number_of_parameters', 'number_of_if_statements', 'number_of_loops', 'number_of_imports',
                'number_of_assignments', 'number_of_literals', 'depth_of_ast_tree', 'number_of_sql_strings',
                'number_of_eval_calls', 'number_of_file_operations', 'number_of_user_inputs', 'number_of_try_except',
                'number_of_constants', 'method_length', 'class_size', 'duplicate_lines_ratio', 'dead_code_indicators'
            ]
            
            top_features_indices = np.argsort(np.abs(sv[0]))[::-1][:5]
            top_features = []
            for idx in top_features_indices:
                top_features.append({
                    "feature": feature_names[idx],
                    "weight": float(sv[0][idx])
                })
        except Exception as e:
            # Fallback to model's feature importance if SHAP fails
            feature_names = [
                'lines_of_code', 'number_of_functions', 'number_of_classes', 'cyclomatic_complexity',
                'number_of_parameters', 'number_of_if_statements', 'number_of_loops', 'number_of_imports',
                'number_of_assignments', 'number_of_literals', 'depth_of_ast_tree', 'number_of_sql_strings',
                'number_of_eval_calls', 'number_of_file_operations', 'number_of_user_inputs', 'number_of_try_except',
                'number_of_constants', 'method_length', 'class_size', 'duplicate_lines_ratio', 'dead_code_indicators'
            ]
            
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                top_indices = np.argsort(importances)[::-1][:5]
                top_features = [{"feature": feature_names[idx], "weight": float(importances[idx])} for idx in top_indices]
            else:
                top_features = [{"feature": "N/A", "weight": 0.0}]

        return {
            "smell": smell,
            "confidence": float(confidence),
            "top_features": top_features
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    test_code = "query = 'SELECT * FROM users WHERE name=' + username"
    # Note: Running this directly will fail due to relative import
    # print(predict_code_smell(test_code))
