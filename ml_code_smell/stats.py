# pyre-ignore-all-errors
import os
import sys
import json
from collections import Counter

from .analyzer import CodeSmellAnalyzer  # type: ignore
from .features import FeatureExtractor  # type: ignore

def generate_project_stats(directory):
    """
    Crawls a directory to perform project-wide analysis of all Python files.
    Aggregates code smell counts and calculates average code metrics.
    """
    analyzer = CodeSmellAnalyzer(log_file="project_stats.log")
    extractor = FeatureExtractor()
    
    all_smells = []
    all_features = []
    file_count = 0
    
    print(f"Analyzing directory: {directory}...")
    
    # Recursively walk through the project directory
    for root, dirs, files in os.walk(directory):
        # Skip common directories that don't contain source code we care about
        if any(excluded in root for excluded in ['.venv', '__pycache__', '.git', '.gemini']):
            continue
            
        for file in files:
            # Only analyze Python files, skipping temp files generated during execution
            if file.endswith('.py') and not file.startswith('temp_'):
                file_path = os.path.join(root, file)
                file_count += 1
                
                # Perform code smell analysis on the file
                smells = analyzer.analyze_file(file_path)
                all_smells.extend(smells)
                
                # Extract numerical features (complexity, length, etc.)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        features = extractor.extract_features(f.read())
                        all_features.append(features)
                except Exception as e:
                    print(f"Skipping {file}: {e}")

    # Aggregate findings using Counter for easy distribution mapping
    smell_counts = Counter([s['type'] for s in all_smells])
    severity_counts = Counter([s['severity'] for s in all_smells])
    
    # Calculate averages from the extracted feature lists
    # Feature indices based on FeatureExtractor.features dictionary order:
    # 0: num_lines, 12: cyclomatic_complexity
    avg_complexity = sum([float(f[12]) for f in all_features]) / len(all_features) if all_features else 0.0
    avg_lines = sum([float(f[0]) for f in all_features]) / len(all_features) if all_features else 0.0

    # Format output for a clean report
    final_complexity = float("{:.2f}".format(avg_complexity))
    final_lines = float("{:.2f}".format(avg_lines))

    # Compile the final report object
    stats = {
        "total_files_analyzed": file_count,
        "total_smells_found": len(all_smells),
        "smell_distribution": dict(smell_counts),
        "severity_distribution": dict(severity_counts),
        "averages": {
            "complexity": final_complexity,
            "lines_per_file": final_lines
        }
    }
    
    return stats

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    results = generate_project_stats(project_root)
    print("\n" + "="*40)
    print("PROJECT-WIDE STATIC ANALYSIS REPORT")
    print("="*40)
    print(json.dumps(results, indent=2))
