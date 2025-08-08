#!/usr/bin/env python3
"""
Script to update the multimodal notebook to remove door/hardware references
and replace them with financial services context.
"""

import json
import re

def update_notebook():
    # Read the notebook file
    with open('MULTIMODAL_DOCUMENT_AI_POC.ipynb', 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    # Define replacements
    replacements = [
        ('Seclock Document Q&A', 'Financial Services Document Q&A'),
        ('Seclock\'s door hardware documents', 'financial industry documents'),
        ('technical questions about Seclock\'s door hardware documents', 'analytical questions about financial industry documents'),
        ('door hardware products', 'financial data and statistics'),
        ('Seclock Multimodal Q\\&A Workflow', 'Financial Services Multimodal Q\\&A Workflow'),
        ('technical door hardware documents', 'financial industry documents'),
        ('by product line or brand', 'by fund type or asset class'),
        ('Ask a question about financial docs...', 'Ask a question about financial data and statistics...'),
        ('## Groundtruth Questions', '## Legacy Questions (Hardware Examples - For Reference Only)'),
    ]
    
    # Process each cell
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') == 'markdown' and 'source' in cell:
            # Handle source as either string or list
            if isinstance(cell['source'], list):
                source_text = ''.join(cell['source'])
            else:
                source_text = cell['source']
            
            # Apply replacements
            for old, new in replacements:
                source_text = source_text.replace(old, new)
            
            # Update the cell source
            if isinstance(cell['source'], list):
                # Split back into lines for list format
                cell['source'] = source_text.splitlines(keepends=True)
            else:
                cell['source'] = source_text
    
    # Write the updated notebook
    with open('MULTIMODAL_DOCUMENT_AI_POC.ipynb', 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)
    
    print("Notebook updated successfully!")
    print("Updated references:")
    for old, new in replacements:
        print(f"  '{old}' -> '{new}'")

if __name__ == '__main__':
    update_notebook() 