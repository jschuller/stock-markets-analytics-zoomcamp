#!/usr/bin/env python3
"""
Script to clean a Jupyter notebook by removing all output cells and execution counts
"""
import json
import sys

def clean_notebook(input_path, output_path):
    """Remove outputs and execution counts from a Jupyter notebook"""
    with open(input_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    # Clean each cell
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            cell['outputs'] = []
            cell['execution_count'] = None
    
    # Write cleaned notebook
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Cleaned notebook saved to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <input.ipynb> <output.ipynb>", file=sys.stderr)
        sys.exit(1)

    clean_notebook(sys.argv[1], sys.argv[2])
