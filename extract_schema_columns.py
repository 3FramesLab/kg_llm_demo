#!/usr/bin/env python3
"""
Extract exact column names from schema JSON for SQL generation.
"""

import json

def extract_table_columns():
    """Extract all table columns from schema."""
    with open('schemas/newdqschemanov.json', 'r') as f:
        schema = json.load(f)
    
    tables = {}
    for table_name, table_info in schema['tables'].items():
        columns = []
        for col in table_info['columns']:
            columns.append(col['name'])
        tables[table_name] = columns
    
    return tables

def main():
    """Print all table structures."""
    tables = extract_table_columns()
    
    print("="*60)
    print("EXACT SCHEMA COLUMNS")
    print("="*60)
    
    for table_name, columns in tables.items():
        print(f"\n{table_name}:")
        print(f"  Columns ({len(columns)}):")
        for col in columns:
            print(f"    - {col}")
    
    print(f"\nTotal tables: {len(tables)}")

if __name__ == "__main__":
    main()
