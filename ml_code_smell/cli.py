# pyre-ignore-all-errors
import argparse
import sys
import os
import json

from .analyzer import CodeSmellAnalyzer  # type: ignore

def main():
    """
    Main entry point for the command-line interface.
    Handles argument parsing and triggers the analysis for a single file.
    """
    # Configure argument parser for the CLI
    parser = argparse.ArgumentParser(description="ML-Driven Code Smell Detector Compiler")
    parser.add_argument("file", help="Path to the Python file to analyze")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")
    
    # Parse inputs from the terminal
    args = parser.parse_args()
    
    # Validation: Ensure the target file exists
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)
        
    # Initialize the core analyzer component
    analyzer = CodeSmellAnalyzer()
    try:
        # Run the full static analysis stack
        smells = analyzer.analyze_file(args.file)
        
        # Display results based on requested format
        if args.format == "json":
            print(json.dumps(smells, indent=2))
        else:
            print(f"Analysis Results for '{args.file}':")
            if not smells:
                print("No code smells detected.")
            else:
                for smell in smells:
                    # Print each finding with its severity level
                    print(f"[{smell['severity']}] {smell['type']} (Line {smell['line']}): {smell['description']}")
                    
    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
