# pyre-ignore-all-errors
import ast
import re
import os
import datetime
from .ir_analysis import DataFlowAnalyzer  # type: ignore
from .feature_extractor import ComprehensiveFeatureExtractor
from . import predictor  # type: ignore

class CodeSmellAnalyzer(ast.NodeVisitor):
    """
    AST-based analyzer for detecting common Python code smells and security vulnerabilities.
    Uses the Visitor pattern to traverse the Abstract Syntax Tree and ML for complex smells.
    """
    def __init__(self, log_file="analysis.log"):
        self.smells = []  # List of detected smells
        self.current_file = ""
        self.source_code = ""
        self.log_file = log_file
        self.depth_limit = 4  # Maximum allowed nesting depth
        self.current_nesting_depth = 0
        self.feature_extractor = ComprehensiveFeatureExtractor()

    def _log(self, message):
        """Append a timestamped message to the analysis log file."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a", encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")

    def analyze_file(self, file_path):
        """
        Performs a full analysis on a Python file.
        Includes AST traversal, regex checks, and data flow analysis.
        """
        self.current_file = file_path
        self.smells = []
        self.current_nesting_depth = 0
        self._log(f"Starting analysis of {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.source_code = f.read()
                # Build the Abstract Syntax Tree
                tree = ast.parse(self.source_code)
                
                self._log("AST parsing complete. Starting traversal...")
                # Start the recursive AST visitation
                self.visit(tree)
                
                self._log("AST traversal complete. Checking regex-based smells...")
                # Check for things that are easier to find with patterns than AST
                self._check_regex_smells()
                
                self._log("Running Data Flow and Taint Analysis...")
                # Perform advanced analysis for security vulnerabilities
                df_analyzer = DataFlowAnalyzer()
                df_smells = df_analyzer.analyze(tree, file_path)
                self.smells.extend(df_smells)
                
                self._log("Running ML-based Prediction Pipeline...")
                # Combine AST features with ML predictions
                prediction_result = predictor.predict_code_smell(self.source_code)
                if prediction_result and "error" not in prediction_result:
                    smell_type = prediction_result['smell']
                    if smell_type != "clean_code":
                        confidence_val = prediction_result['confidence'] * 100
                        if confidence_val > 40:
                            explanation = ", ".join([f"{f['feature']}" for f in prediction_result['top_features']])
                            self._add_smell(
                                f"ML: {smell_type}",
                                f"ML model detected {smell_type} with {confidence_val:.2f}% confidence. Key indicators: {explanation}",
                                1,
                                "High" if confidence_val > 85 else "Medium"
                            )
                
                self._log(f"Analysis complete for {file_path}. Found {len(self.smells)} smells.")
        except Exception as e:
            self._log(f"Error analyzing {file_path}: {e}")
            print(f"Error analyzing {file_path}: {e}")
        return self.smells

    def _add_smell(self, smell_type, description, line, severity="High"):
        self.smells.append({
            "type": smell_type,
            "description": description,
            "file": os.path.basename(self.current_file),
            "line": line,
            "severity": severity
        })

    def visit_ClassDef(self, node):
        """Detect Large Class smell by counting methods and lines."""
        method_count = len([n for n in node.body if isinstance(n, ast.FunctionDef)])
        line_count = node.end_lineno - node.lineno
        if method_count > 15 or line_count > 200:
            self._add_smell(
                "Large Class",
                f"Class '{node.name}' is too large ({method_count} methods, {line_count} lines).",
                node.lineno,
                "Medium"
            )
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Detect Long Method and Long Parameter List smells."""
        # Check method length
        line_count = node.end_lineno - node.lineno
        if line_count > 60: 
            self._add_smell(
                "Long Method",
                f"Method '{node.name}' is too long ({line_count} lines). Consider refactoring.",
                node.lineno,
                "Medium"
            )
        
        # Check parameter count
        param_count = len(node.args.args)
        if param_count > 5:
            self._add_smell(
                "Long Parameter List",
                f"Method '{node.name}' has too many parameters ({param_count}).",
                node.lineno,
                "Medium"
            )
        
        self.generic_visit(node)

    def visit_If(self, node):
        self._enter_nesting(node)
        self.generic_visit(node)
        self._exit_nesting()

    def visit_For(self, node):
        self._enter_nesting(node)
        self.generic_visit(node)
        self._exit_nesting()

    def visit_While(self, node):
        self._enter_nesting(node)
        self.generic_visit(node)
        self._exit_nesting()

    def _enter_nesting(self, node):
        self.current_nesting_depth += 1
        if self.current_nesting_depth > self.depth_limit:
            self._add_smell(
                "Deeply Nested Code",
                f"Code is nested too deeply ({self.current_nesting_depth} levels). Consider extracting methods.",
                node.lineno,
                "Medium"
            )

    def _exit_nesting(self):
        self.current_nesting_depth -= 1

    def visit_Call(self, node):
        """Detect potential security risks in function calls."""
        if isinstance(node.func, ast.Name):
            # Checking for use of input() as a simple example
            if node.func.id == 'input':
                 self._add_smell(
                    "Unsafe API Usage",
                    f"Usage of potentially unsafe function '{node.func.id}' detected. Use secure alternatives.",
                    node.lineno,
                    "High"
                )
        
        self.generic_visit(node)

    def _check_regex_smells(self):
        """Find patterns that are hard to detect via AST but easy with strings."""
        lines = self.source_code.split('\n')
        for i, line in enumerate(lines):
            # Look for common variable names used for secrets paired with assignment
            if re.search(r'(api_key|password|secret|token)\s*=\s*[\'"][^\'"]+[\'"]', line, re.IGNORECASE):
                self._add_smell(
                    "Hard-coded Credential",
                    "Possible hard-coded credential detected.",
                    i + 1,
                    "Critical"
                )
            
            # Look for hard-coded internal IP addresses
            if re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', line):
                 self._add_smell(
                    "Magic String/Number",
                    "Hard-coded IP address detected.",
                    i + 1,
                    "Low"
                )

if __name__ == "__main__":
    code = """
import os
import sqlite3

def vulnerable_func(username):
    # Hard-coded credential
    password = "admin_password123"
    
    # SQL injection
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    
    # Deeply nested code
    for i in range(10):
        for j in range(10):
            for k in range(10):
                if i > 5:
                    if j > 5:
                        if k > 5:
                            print(i, j, k)
    """
    
    # Save code to a temp file for analysis
    temp_path = "temp_analyzer_test.py"
    with open(temp_path, "w", encoding='utf-8') as f:
        f.write(code)
        
    print("="*40)
    print("STATIC CODE SMELL ANALYSIS")
    print("="*40)
    
    analyzer = CodeSmellAnalyzer()
    smells = analyzer.analyze_file(temp_path)
    
    if not smells:
        print("  No code smells detected.")
    else:
        for smell in smells:
            severity_str = f"[{smell['severity']}]"
            print(f"  {severity_str:10} {smell['type']:25} (Line {smell['line']})")
            print(f"             {smell['description']}")
            print("-" * 20)
            
    print("="*40)
    
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)

