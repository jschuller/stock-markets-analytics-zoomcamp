#!/usr/bin/env python3
"""
Jupyter Notebook JSON Validator
Checks if a .ipynb file has valid JSON structure
"""

import json
import sys
import os

def validate_notebook(file_path):
    """Validate a Jupyter notebook JSON structure"""
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    if not file_path.endswith('.ipynb'):
        print(f"⚠️  File doesn't appear to be a notebook: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            notebook_content = json.load(f)
        
        # Check for required notebook structure
        required_keys = ['cells', 'metadata', 'nbformat', 'nbformat_minor']
        
        for key in required_keys:
            if key not in notebook_content:
                print(f"❌ Missing required key: {key}")
                return False
        
        # Check cells structure
        if not isinstance(notebook_content['cells'], list):
            print("❌ 'cells' must be a list")
            return False
        
        # Validate each cell
        for i, cell in enumerate(notebook_content['cells']):
            if not isinstance(cell, dict):
                print(f"❌ Cell {i} is not a dictionary")
                return False
            
            if 'cell_type' not in cell:
                print(f"❌ Cell {i} missing 'cell_type'")
                return False
            
            if 'metadata' not in cell:
                print(f"❌ Cell {i} missing 'metadata'")
                return False
            
            if 'source' not in cell:
                print(f"❌ Cell {i} missing 'source'")
                return False
        
        print(f"✅ Valid notebook: {file_path}")
        print(f"📊 Notebook info:")
        print(f"   - Format: {notebook_content['nbformat']}.{notebook_content['nbformat_minor']}")
        print(f"   - Cells: {len(notebook_content['cells'])}")
        
        # Count cell types
        cell_types = {}
        for cell in notebook_content['cells']:
            cell_type = cell['cell_type']
            cell_types[cell_type] = cell_types.get(cell_type, 0) + 1
        
        print(f"   - Cell types: {dict(cell_types)}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        print(f"   Line {e.lineno}, Column {e.colno}")
        
        # Try to show context around the error
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            start = max(0, e.lineno - 3)
            end = min(len(lines), e.lineno + 2)
            
            print(f"\\n📍 Context around error:")
            for i in range(start, end):
                marker = ">>> " if i == e.lineno - 1 else "    "
                print(f"{marker}{i+1:4d}: {lines[i].rstrip()}")
                
        except Exception:
            pass
            
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_notebook.py <notebook_file.ipynb>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    print(f"🔍 Validating notebook: {file_path}")
    print("=" * 50)
    
    if validate_notebook(file_path):
        print("\\n🎉 Notebook is valid and should open correctly!")
        sys.exit(0)
    else:
        print("\\n💡 Notebook has issues. Consider:")
        print("   • Using the test notebook instead")
        print("   • Re-creating the notebook from scratch")
        print("   • Using Google Colab as an alternative")
        sys.exit(1)

if __name__ == "__main__":
    main()
