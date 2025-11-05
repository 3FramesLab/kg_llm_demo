#!/usr/bin/env python3
"""
Extract exact column names for brz_lnd_IBP_Product_Master table from schema.
"""

import json

def extract_ibp_columns():
    """Extract all column names for IBP Product Master table."""
    with open('schemas/newdqschemanov.json', 'r') as f:
        schema = json.load(f)
    
    table_info = schema['tables']['brz_lnd_IBP_Product_Master']
    columns = []
    
    for col in table_info['columns']:
        columns.append(col['name'])
    
    print("brz_lnd_IBP_Product_Master columns:")
    print(f"Total columns: {len(columns)}")
    print()
    
    # Print columns for SQL INSERT
    print("Column names for INSERT statement:")
    for i, col in enumerate(columns):
        if i == len(columns) - 1:
            print(f"    {col}")
        else:
            print(f"    {col},")
    
    print()
    print("Column names as comma-separated list:")
    print(", ".join(columns))

if __name__ == "__main__":
    extract_ibp_columns()
