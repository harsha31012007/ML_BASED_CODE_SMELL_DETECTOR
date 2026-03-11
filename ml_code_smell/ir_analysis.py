import ast
from collections import defaultdict

class CFGNode:
    """
    Represents a Basic Block in the Control Flow Graph.
    Contains a set of AST nodes that execute sequentially without branching.
    """
    def __init__(self, node_id, ast_nodes):
        self.node_id = node_id
        self.ast_nodes = ast_nodes  # List of AST nodes in this basic block
        self.successors = []        # Outgoing edges in the graph
        self.predecessors = []      # Incoming edges in the graph

    def add_successor(self, node):
        """Creates a directed edge between this node and another CFG node."""
        if node not in self.successors:
            self.successors.append(node)
        if self not in node.predecessors:
            node.predecessors.append(self)

class DataFlowAnalyzer(ast.NodeVisitor):
    """
    Advanced analyzer that tracks the flow of untrusted data (taint) 
    from 'sources' (e.g., input) to 'sinks' (e.g., eval).
    """
    def __init__(self):
        self.tainted_vars = set()  # Track which variables are 'contaminated'
        self.smells = []           # List of security findings
        self.current_function = None
        self.file_path = "<unknown>"

    def analyze(self, tree, file_path="<unknown>"):
        """Entry point for performing taint analysis on an AST."""
        self.file_path = file_path
        self.visit(tree)
        return self.smells

    def _add_smell(self, smell_type, description, line, severity="Critical"):
        """Records a security smell found during data flow analysis."""
        self.smells.append({
            "type": smell_type,
            "description": description,
            "file": self.file_path,
            "line": line,
            "severity": severity
        })

    def visit_FunctionDef(self, node):
        """Tracks taint introduced by function parameters."""
        self.current_function = node.name
        # Function parameters are considered potential taint sources (untrusted input)
        for arg in node.args.args:
            self.tainted_vars.add(arg.arg)
        
        self.generic_visit(node)
        
        # Cleanup state after finishing function analysis (intra-procedural)
        self.current_function = None
        self.tainted_vars.clear() 

    def visit_Assign(self, node):
        """Tracks the propagation of taint through variable assignments."""
        # Check if any part of the right-hand side is tainted
        is_tainted = self._is_tainted(node.value)
        
        # Propagation: if RHS is tainted, LHS variables also become tainted
        for target in node.targets:
            if isinstance(target, ast.Name):
                if is_tainted:
                    self.tainted_vars.add(target.id)
                elif target.id in self.tainted_vars:
                    # If assignment is to a safe value, remove taint (sanitization)
                    self.tainted_vars.remove(target.id)
        
        self.generic_visit(node)

    def _is_tainted(self, node):
        """Recursively checks if an AST node contains or is derived from tainted data."""
        if isinstance(node, ast.Name):
            return node.id in self.tainted_vars
        elif isinstance(node, ast.BinOp):
            # Taint propagates through operations (e.g., 'a + b' is tainted if 'a' is)
            return self._is_tainted(node.left) or self._is_tainted(node.right)
        elif isinstance(node, ast.JoinedStr): # f-strings
            # f-strings are tainted if any embedded expression is tainted
            for val in node.values:
                if self._is_tainted(val):
                    return True
        elif isinstance(node, ast.Call):
            # Check for direct sources (input()) or transitive taint through arguments
            if isinstance(node.func, ast.Name) and getattr(node.func, 'id', '') == 'input':
                return True 
            for arg in node.args:
                if self._is_tainted(arg):
                    return True
        return False

    def visit_Call(self, node):
        """Checks if tainted data is used in dangerous 'sink' functions."""
        is_sink = False
        sink_name = ""
        
        # Hard-coded list of dangerous sinks for demonstration
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'execute':
                is_sink = True
                sink_name = "SQL Execution (execute)"
            elif isinstance(node.func.value, ast.Name) and node.func.value.id == 'os' and node.func.attr == 'system':
                is_sink = True
                sink_name = "OS Command (os.system)"
                
        elif isinstance(node.func, ast.Name):
            if node.func.id in ['eval', 'exec']:
                is_sink = True
                sink_name = f"Code Execution ({node.func.id})"

        if is_sink:
            # If a sink is reached, check if the data being passed is untrusted
            for arg in node.args:
                if self._is_tainted(arg):
                    self._add_smell(
                        "Tainted Data Flow",
                        f"Potentially untrusted data flows into a critical sink: {sink_name}",
                        node.lineno,
                        "Critical"
                    )
                    break
                    
        self.generic_visit(node)

def build_cfg(tree):
    """
    Constructs a basic Control Flow Graph (CFG) from the AST.
    Divides code into Basic Blocks based on control flow changes (if, for, while).
    """
    nodes = []
    current_block = []
    
    for node in ast.walk(tree):
        # Identify nodes that cause the start of a new basic block
        if isinstance(node, (ast.If, ast.For, ast.While, ast.FunctionDef)):
            if current_block:
                cfg_node = CFGNode(len(nodes), current_block)
                nodes.append(cfg_node)
                current_block = []
        current_block.append(node)
        
    if current_block:
        nodes.append(CFGNode(len(nodes), current_block))
        
    # Link blocks sequentially for simple visual representation in this demo
    for i in range(len(nodes) - 1):
        nodes[i].add_successor(nodes[i+1])
        
    return nodes

if __name__ == "__main__":
    code = """
def vulnerable_func(user_input):
    cmd = "echo " + user_input
    eval(cmd)  # Critical Taint Sink
    
def safe_func():
    x = 10
    print(x)
    """
    
    tree = ast.parse(code)
    print("="*40)
    print("INTERMEDIATE REPRESENTATION & DATA FLOW ANALYSIS")
    print("="*40)
    
    print("\n1. Building Control Flow Graph (CFG) blocks:")
    cfg = build_cfg(tree)
    for node in cfg:
        print(f"  Block {node.node_id}: {len(node.ast_nodes)} AST nodes")
        
    print("\n2. Running Taint Analysis:")
    analyzer = DataFlowAnalyzer()
    smells = analyzer.analyze(tree, "example_taint.py")
    
    if not smells:
        print("  No tainted data flows detected.")
    else:
        for smell in smells:
            print(f"  [!] {smell['type']} (Line {smell['line']}): {smell['description']}")
    print("="*40)
