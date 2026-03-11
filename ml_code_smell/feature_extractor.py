import ast
import os
from radon.complexity import cc_visit  # type: ignore
from radon.metrics import h_visit  # type: ignore

class ComprehensiveFeatureExtractor(ast.NodeVisitor):
    """
    Extracts 21+ features from Python code using AST and Radon.
    """
    def __init__(self):
        self.features = {
            'lines_of_code': 0,
            'number_of_functions': 0,
            'number_of_classes': 0,
            'cyclomatic_complexity': 0,
            'number_of_parameters': 0,
            'number_of_if_statements': 0,
            'number_of_loops': 0,
            'number_of_imports': 0,
            'number_of_assignments': 0,
            'number_of_literals': 0,
            'depth_of_ast_tree': 0,
            'number_of_sql_strings': 0,
            'number_of_eval_calls': 0,
            'number_of_file_operations': 0,
            'number_of_user_inputs': 0,
            'number_of_try_except': 0,
            'number_of_constants': 0,
            'method_length': 0,
            'class_size': 0,
            'duplicate_lines_ratio': 0.0,
            'dead_code_indicators': 0
        }
        self.sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'FROM', 'WHERE']
        self.file_ops = ['open', 'read', 'write', 'close']
        self.current_depth = 0
        self.max_depth = 0
        self.function_lines = []
        self.class_lines = []

    def extract_features(self, source_code):
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return [0] * 21

        self.features['lines_of_code'] = len(source_code.splitlines())
        
        # Radon features
        try:
            complexity = cc_visit(source_code)
            self.features['cyclomatic_complexity'] = sum(c.complexity for c in complexity) if complexity else 1
        except:
            self.features['cyclomatic_complexity'] = 1

        self.visit(tree)
        
        # Aggregated features
        if self.function_lines:
            self.features['method_length'] = sum(self.function_lines) / len(self.function_lines)
        if self.class_lines:
            self.features['class_size'] = sum(self.class_lines) / len(self.class_lines)
            
        self.features['depth_of_ast_tree'] = self.max_depth
        
        # Simple duplication check (placeholder for ratio)
        lines = source_code.splitlines()
        unique_lines = set(lines)
        if len(lines) > 0:
            self.features['duplicate_lines_ratio'] = 1.0 - (len(unique_lines) / len(lines))

        return list(self.features.values())

    def visit(self, node):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        super().visit(node)
        self.current_depth -= 1

    def visit_FunctionDef(self, node):
        self.features['number_of_functions'] += 1
        self.features['number_of_parameters'] += len(node.args.args)
        self.function_lines.append(node.end_lineno - node.lineno)
        
        # Dead code check: code after return
        for i, stmt in enumerate(node.body):
            if isinstance(stmt, ast.Return) and i < len(node.body) - 1:
                self.features['dead_code_indicators'] += 1
        
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.features['number_of_classes'] += 1
        self.class_lines.append(node.end_lineno - node.lineno)
        self.generic_visit(node)

    def visit_If(self, node):
        self.features['number_of_if_statements'] += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.features['number_of_loops'] += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.features['number_of_loops'] += 1
        self.generic_visit(node)

    def visit_Import(self, node):
        self.features['number_of_imports'] += 1
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self.features['number_of_imports'] += 1
        self.generic_visit(node)

    def visit_Assign(self, node):
        self.features['number_of_assignments'] += 1
        self.generic_visit(node)

    def visit_Constant(self, node):
        self.features['number_of_literals'] += 1
        if isinstance(node.value, str):
            if any(kw in node.value.upper() for kw in self.sql_keywords):
                self.features['number_of_sql_strings'] += 1
            if len(node.value) > 20: # Arbitrary constant heuristic
                self.features['number_of_constants'] += 1
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in ['eval', 'exec']:
                self.features['number_of_eval_calls'] += 1
            if node.func.id == 'input':
                self.features['number_of_user_inputs'] += 1
            if node.func.id in self.file_ops:
                self.features['number_of_file_operations'] += 1
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in self.file_ops:
                self.features['number_of_file_operations'] += 1
            if node.func.attr == 'system' and isinstance(node.func.value, ast.Name) and node.func.value.id == 'os':
                self.features['number_of_eval_calls'] += 1
        self.generic_visit(node)

    def visit_Try(self, node):
        self.features['number_of_try_except'] += 1
        # Improper error handling check: empty except or broad exception
        for handler in node.handlers:
            if handler.type is None or (isinstance(handler.type, ast.Name) and handler.type.id == 'Exception'):
                 if len(handler.body) <= 1 and isinstance(handler.body[0], (ast.Pass, ast.Continue)):
                     self.features['dead_code_indicators'] += 1 # Using as general indicator of bad practice
        self.generic_visit(node)
