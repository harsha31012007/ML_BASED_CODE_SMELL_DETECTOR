# ML-Driven Code Smell Detector Compiler

An advanced static analysis tool designed to detect common Python code smells and security vulnerabilities using AST traversal, data flow analysis, and machine learning techniques.

## 🚀 Features

-   **AST-Based Static Analysis**: Traverses the Abstract Syntax Tree (AST) to identify structural patterns like Large Classes, Long Methods, and Deeply Nested Code.
-   **Intermediate Representation (IR)**: Generates a simplified Control Flow Graph (CFG) for targeted analysis.
-   **Security Vulnerability Detection**: Uses Data Flow and Taint Analysis to track untrusted data from sources (like `input()`) to critical sinks (like `eval()` or `os.system()`).
-   **Regex-Driven Checks**: Identifies hard-coded credentials, secret keys, and magic strings.
-   **Web UI & API Interface**: Includes a modern web interface for manual code submission and analysis.
-   **Command-Line Interface (CLI)**: Enables fast terminal-based analysis of local files.
-   **ML-Driven Classification**: Extensible architecture for machine learning model-based smell detection.

## 📁 Project Structure

```text
├── ml_code_smell/          # Core package
│   ├── analyzer.py         # Main AST visitation logic
│   ├── ir_analysis.py      # CFG and Taint Analysis logic
│   ├── cli.py              # CLI entry point
│   ├── model.py            # ML model handling
│   └── ...                 # Other utility modules
├── api.py                  # Flask REST API server
├── app.js / index.html     # Web interface frontend
├── train_model.py          # Script for training the smell detection model
├── vulnerable_code.py      # Example file with detected smells
├── clean_code.py           # Example file with no smells
└── requirements.txt        # Project dependencies
```

## 🛠️ Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/ml-based-code-smell-detector.git
    cd ml-based-code-smell-detector
    ```

2.  **Set up a virtual environment (recommended)**:
    ```bash
    python -m venv .venv
    # On Windows:
    .venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 💻 Usage

### Running the Web Interface

Start the Flask API server and open the web UI:

```bash
python api.py
```
Then, open `index.html` in your web browser. You can paste code or load sample files to see real-time analysis results.

### Using the Command Line Interface (CLI)

Run the analyzer on any Python file directly from your terminal:

```bash
python -m ml_code_smell some_file.py
```
For JSON output:
```bash
python -m ml_code_smell some_file.py --format json
```

### Training the ML Model

If you have a dataset for code smells, you can train or update the detection model:

```bash
python train_model.py
```

## 🔍 Detected Smells

-   **Structural**: Large Class, Long Method, Long Parameter List, Deeply Nested Code.
-   **Security**: SQL Injection, Command Injection (Tainted Data Flow), Unsafe API Usage.
-   **Pattern-based**: Hard-coded Credentials, Magic Strings/IPs.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
