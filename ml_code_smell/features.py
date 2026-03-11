import ast
import math
from collections import Counter

class FeatureExtractor(ast.NodeVisitor):
    """
    Extracts numerical features from Python code for use in ML models.
    Calculates metrics like complexity, nesting depth, and parameter counts.
    """
    def __init__(self):
        # A dictionary holding all the metrics we extract
        self.features = {
            'num_lines': 0,
            'num_functions': 0,
            'avg_function_length': 0.0,
            'max_function_length': 0,
            'num_variables': 0,
            'num_loops': 0,
            'num_conditionals': 0,
            'max_nesting_depth': 0,
            'num_string_literals': 0,
            'high_entropy_strings': 0,  # Used to detect potential encoded keys/secrets
            'avg_parameters': 0.0,
            'max_parameters': 0,
            'cyclomatic_complexity': 1, # Base complexity is always 1
            'num_classes': 0,
        }
        self.current_depth = 0
        self.function_lengths = []
        self.parameter_counts = []

    def extract_features(self, source_code):
        """Processes source code and returns a list of numerical feature values."""
        tree = ast.parse(source_code)
        self.features['num_lines'] = len(source_code.splitlines())
        self.visit(tree)
        
        # Calculate derived averages and maximums
        if self.function_lengths:
            self.features['avg_function_length'] = sum(self.function_lengths) / len(self.function_lengths)
            self.features['max_function_length'] = max(self.function_lengths)
        
        if self.parameter_counts:
            self.features['avg_parameters'] = sum(self.parameter_counts) / len(self.parameter_counts)
            self.features['max_parameters'] = max(self.parameter_counts)
            
        return list(self.features.values())

    def visit_ClassDef(self, node):
        """Track number of classes defined in the file."""
        self.features['num_classes'] += 1
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Analyze function definitions for length and complexity."""
        self.features['num_functions'] += 1
        length = node.end_lineno - node.lineno
        self.function_lengths.append(length)
        
        param_count = len(node.args.args)
        self.parameter_counts.append(param_count)
        
        # Track nesting depth for functions
        self.current_depth += 1
        self.features['max_nesting_depth'] = max(self.features['max_nesting_depth'], self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_For(self, node):
        """Analyze For-loops for quantity and complexity."""
        self.features['num_loops'] += 1
        self.features['cyclomatic_complexity'] += 1
        self.current_depth += 1
        self.features['max_nesting_depth'] = max(self.features['max_nesting_depth'], self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_While(self, node):
        """Analyze While-loops for quantity and complexity."""
        self.features['num_loops'] += 1
        self.features['cyclomatic_complexity'] += 1
        self.current_depth += 1
        self.features['max_nesting_depth'] = max(self.features['max_nesting_depth'], self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_If(self, node):
        """Analyze If-statements for quantity and complexity."""
        self.features['num_conditionals'] += 1
        self.features['cyclomatic_complexity'] += 1
        self.current_depth += 1
        self.features['max_nesting_depth'] = max(self.features['max_nesting_depth'], self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1
    
    def visit_ExceptHandler(self, node):
        """Exception handlers contribute to cyclomatic complexity."""
        self.features['cyclomatic_complexity'] += 1
        self.generic_visit(node)

    def visit_Assign(self, node):
        """Track variable assignments."""
        self.features['num_variables'] += len(node.targets)
        self.generic_visit(node)

    def visit_Constant(self, node):
        """Analyze string literals for potential secrets via entropy."""
        if isinstance(node.value, str):
            self.features['num_string_literals'] += 1
            # If a string has high randomness (entropy), it might be an API key or password
            if self._calculate_entropy(node.value) > 3.5: 
                self.features['high_entropy_strings'] += 1
        self.generic_visit(node)

    def _calculate_entropy(self, string):
        """Calculates the Shannon Entropy of a string to measure its randomness."""
        if not string:
            return 0
        entropy = 0
        # Formula for Shannon Entropy: -Sum(p_x * log2(p_x))
        for x in set(string):
            p_x = float(string.count(x)) / len(string)
            entropy += - p_x * math.log(p_x, 2)
        return entropy
