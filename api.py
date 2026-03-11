# pyre-ignore-all-errors
from flask import Flask, jsonify, request, send_from_directory  # type: ignore
from flask_cors import CORS  # type: ignore
import subprocess
import os
import json
import pandas as pd  # type: ignore
import random

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from ml_code_smell.analyzer import CodeSmellAnalyzer  # type: ignore

@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    """
    Endpoint to perform static analysis on provided code content.
    Returns a list of detected code smells and vulnerabilities.
    """
    res_data = request.json
    code_content = res_data.get('code', '')
    
    # If no custom code is provided, fall back to sample files
    if not code_content:
        code_type = res_data.get('type', 'vulnerable')
        if code_type == 'vulnerable':
             file_path = os.path.join(BASE_DIR, 'vulnerable_code.py')
        elif code_type == 'clean':
             file_path = os.path.join(BASE_DIR, 'clean_code.py')
        else:
             return jsonify({'error': 'Invalid code type'}), 400
        
        with open(file_path, 'r', encoding='utf-8') as f:
            code_content = f.read()

    # Create a temporary file to run the AST analyzer against
    analyzer = CodeSmellAnalyzer()
    temp_path = os.path.join(BASE_DIR, 'temp_analysis.py')
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(code_content)
    
    # Run the core analysis logic
    smells = analyzer.analyze_file(temp_path)
    
    # Cleanup temp file after analysis
    if os.path.exists(temp_path):
        os.remove(temp_path)

    return jsonify({
        'success': True,
        'smells': smells
    })

@app.route('/api/execute', methods=['POST'])
def execute_code():
    """
    Endpoint to execute the provided Python code and return stdout/stderr.
    Uses a subprocess with a timeout for basic safety.
    """
    temp_file = None
    try:
        data = request.json
        code_content = data.get('code', '')
        
        # Determine the source of code to execute
        if code_content:
            # Custom code from the web editor
            temp_file = os.path.join(BASE_DIR, 'temp_exec.py')
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code_content)
            file_path = temp_file
        else:
            # Predefined sample files
            code_type = data.get('type', 'vulnerable')
            if code_type == 'vulnerable':
                file_path = os.path.join(BASE_DIR, 'vulnerable_code.py')
            elif code_type == 'clean':
                file_path = os.path.join(BASE_DIR, 'clean_code.py')
            else:
                return jsonify({'error': 'Invalid code type'}), 400
        
        # Run the code in a separate process
        result = subprocess.run(
            ['python', file_path],
            capture_output=True,
            text=True,
            timeout=10 # Stop execution if it takes too long (e.g., infinite loops)
        )
        
        return jsonify({
            'success': True,
            'output': result.stdout,
            'error': result.stderr,
            'exit_code': result.returncode
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Execution timeout'}), 408
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Final cleanup of any temporary execution files
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)

@app.route('/api/get-code', methods=['POST'])
def get_code():
    """Fetches the content of a sample file to load into the web editor."""
    try:
        data = request.json
        code_type = data.get('type', 'vulnerable')
        
        if code_type == 'vulnerable':
            file_path = os.path.join(BASE_DIR, 'vulnerable_code.py')
        elif code_type == 'clean':
            file_path = os.path.join(BASE_DIR, 'clean_code.py')
        else:
            return jsonify({'error': 'Invalid code type'}), 400
        
        with open(file_path, 'r', encoding='utf-8') as f:
            code_content = f.read()
        
        return jsonify({
            'success': True,
            'code': code_content
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/random-sample', methods=['GET'])
def get_random_sample():
    """Fetches a random sample from the generated dataset."""
    try:
        dataset_path = os.path.join(BASE_DIR, 'code_smell_dataset.csv')
        if not os.path.exists(dataset_path):
            return jsonify({'error': 'Dataset not found. Please run generate_dataset.py first.'}), 404
        
        df = pd.read_csv(dataset_path)
        random_row = df.sample(n=1).iloc[0]
        
        return jsonify({
            'success': True,
            'code': random_row['code_snippet'],
            'label': random_row['smell_label']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Simple status check for the API."""
    return jsonify({'status': 'healthy'})

# Routes for serving static frontend files
@app.route('/')
def serve_index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/style.css')
def serve_css():
    return send_from_directory(BASE_DIR, 'style.css')

@app.route('/app.js')
def serve_js():
    return send_from_directory(BASE_DIR, 'app.js')

if __name__ == '__main__':
    # Initialize the Flask development server
    print("Starting API server on http://localhost:5000")
    print("Frontend: Open index.html in your browser")
    app.run(debug=True, port=5000)
