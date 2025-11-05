#!/usr/bin/env python3
"""
Validate that the seed data SQL script uses only columns that exist in the schema.
"""

import json
import re

def load_schema_columns():
    """Load schema columns from JSON."""
    with open('schemas/newdqschemanov.json', 'r') as f:
        schema = json.load(f)
    
    tables = {}
    for table_name, table_info in schema['tables'].items():
        columns = set()
        for col in table_info['columns']:
            columns.add(col['name'])
        tables[table_name] = columns
    
    return tables

def extract_sql_columns():
    """Extract columns used in SQL INSERT statements."""
    with open('seed_data_500_items_gpu_nbu_fixed.sql', 'r') as f:
        sql_content = f.read()
    
    # Find INSERT statements
    insert_pattern = r'INSERT INTO (\w+)\s*\(\s*([^)]+)\)'
    matches = re.findall(insert_pattern, sql_content, re.IGNORECASE | re.MULTILINE)
    
    sql_tables = {}
    for table_name, columns_str in matches:
        # Clean up column names
        columns = []
        for col in columns_str.split(','):
            col = col.strip()
            # Remove brackets and quotes
            col = col.replace('[', '').replace(']', '').replace('"', '').replace("'", '')
            if col:
                columns.append(col)
        sql_tables[table_name] = set(columns)
    
    return sql_tables

def validate_columns():
    """Validate SQL columns against schema."""
    print("="*60)
    print("VALIDATING SEED DATA COLUMNS AGAINST SCHEMA")
    print("="*60)
    
    schema_tables = load_schema_columns()
    sql_tables = extract_sql_columns()
    
    all_valid = True
    
    for table_name, sql_columns in sql_tables.items():
        print(f"\n📋 Table: {table_name}")
        
        if table_name not in schema_tables:
            print(f"   ❌ ERROR: Table {table_name} not found in schema!")
            all_valid = False
            continue
        
        schema_columns = schema_tables[table_name]
        
        # Check for invalid columns
        invalid_columns = sql_columns - schema_columns
        valid_columns = sql_columns & schema_columns
        
        print(f"   SQL Columns: {len(sql_columns)}")
        print(f"   Schema Columns: {len(schema_columns)}")
        print(f"   Valid Columns: {len(valid_columns)}")
        
        if invalid_columns:
            print(f"   ❌ INVALID COLUMNS ({len(invalid_columns)}):")
            for col in sorted(invalid_columns):
                print(f"      - {col}")
            all_valid = False
        else:
            print(f"   ✅ All columns are valid!")
        
        # Show missing columns (optional)
        missing_columns = schema_columns - sql_columns
        if missing_columns:
            print(f"   ℹ️  Unused Schema Columns ({len(missing_columns)}):")
            for col in sorted(list(missing_columns)[:5]):  # Show first 5
                print(f"      - {col}")
            if len(missing_columns) > 5:
                print(f"      ... and {len(missing_columns) - 5} more")
    
    print(f"\n{'='*60}")
    if all_valid:
        print("✅ VALIDATION PASSED: All SQL columns exist in schema!")
    else:
        print("❌ VALIDATION FAILED: Some SQL columns don't exist in schema!")
    print(f"{'='*60}")
    
    return all_valid

def main():
    """Main validation function."""
    try:
        is_valid = validate_columns()
        return 0 if is_valid else 1
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
