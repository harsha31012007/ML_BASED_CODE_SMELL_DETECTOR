# pyre-ignore-all-errors
import os
import json
from ml_code_smell.analyzer import CodeSmellAnalyzer  # type: ignore
from ml_code_smell.features import FeatureExtractor  # type: ignore

def generate_data():
    files = ['vulnerable_code.py', 'clean_code.py']
    results = {}

    analyzer = CodeSmellAnalyzer()
    extractor = FeatureExtractor()

    for file_name in files:
        if not os.path.exists(file_name):
            print(f"File {file_name} not found.")
            continue
        
        with open(file_name, 'r', encoding='utf-8') as f:
            code = f.read()

        # Analyze Smells
        smells = analyzer.analyze_file(file_name)

        # Extract Features
        features = extractor.extract_features(code)
        feature_names = [
            'num_lines', 'num_functions', 'avg_function_length', 'max_function_length',
            'num_variables', 'num_loops', 'num_conditionals', 'max_nesting_depth',
            'num_string_literals', 'high_entropy_strings'
        ]
        
        feature_dict = dict(zip(feature_names, features))

        results[file_name] = {
            'smells': smells,
            'features': feature_dict,
            'code_snippet': code[:200] + "..." if len(code) > 200 else code  # type: ignore
        }

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    generate_data()
