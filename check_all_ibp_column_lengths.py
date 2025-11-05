#!/usr/bin/env python3
"""
Check ALL column lengths for brz_lnd_IBP_Product_Master to prevent truncation errors.
"""

import json
import re

def extract_column_info():
    """Extract all column names and their max lengths."""
    with open('schemas/newdqschemanov.json', 'r') as f:
        schema = json.load(f)
    
    table_info = schema['tables']['brz_lnd_IBP_Product_Master']
    columns = []
    
    for col in table_info['columns']:
        name = col['name']
        type_str = col['type']
        
        # Extract length from type like "NVARCHAR(40)" or "VARCHAR(255)"
        length_match = re.search(r'\((\d+)\)', type_str)
        if length_match:
            max_length = int(length_match.group(1))
        else:
            max_length = None
        
        columns.append({
            'name': name,
            'type': type_str,
            'max_length': max_length
        })
    
    return columns

def check_problematic_columns():
    """Identify columns that might cause truncation issues."""
    columns = extract_column_info()
    
    print("="*80)
    print("IBP PRODUCT MASTER - COLUMN LENGTH ANALYSIS")
    print("="*80)
    
    # Focus on columns with small lengths that might cause issues
    problematic = []
    
    for col in columns:
        if col['max_length'] and col['max_length'] <= 20:
            problematic.append(col)
    
    print(f"\nCOLUMNS WITH LENGTH <= 20 (High Risk for Truncation):")
    print("-" * 60)
    
    for col in problematic:
        print(f"{col['name']:<25} {col['type']:<35} Max: {col['max_length']}")
    
    print(f"\nTOTAL RISKY COLUMNS: {len(problematic)}")
    
    # Show all columns for reference
    print(f"\n\nALL COLUMNS ({len(columns)} total):")
    print("-" * 80)
    
    for col in columns:
        length_str = str(col['max_length']) if col['max_length'] else 'N/A'
        print(f"{col['name']:<30} {col['type']:<40} Max: {length_str}")
    
    return problematic

def generate_safe_values():
    """Generate safe value patterns for problematic columns."""
    problematic = check_problematic_columns()
    
    print(f"\n\nSAFE VALUE RECOMMENDATIONS:")
    print("="*80)
    
    recommendations = {
        'ZBOM3': "RIGHT(MATERIAL, 2)  -- 'BOM3_01' = 7 chars max",
        'ZFAB': "CASE (ROW_NUMBER() % 4) WHEN 0 THEN N'FAB1' ... END  -- 4 chars max",
        'ZFABTECH': "CASE ... WHEN 0 THEN N'5NM' ... END  -- 3-4 chars max",
        'ZDIEBIN': "RIGHT(MATERIAL, 3)  -- 'BIN001' = 6 chars max",
        'ZOPSPCB': "RIGHT(MATERIAL, 3)  -- 'PCB001' = 6 chars max",
        'ZMAKEBUY': "Single char: N'M', N'B', N'C'  -- 1 char max",
        'ZMATTYPE': "N'FERT' or N'HALB'  -- 4 chars max",
        'ZITEMTECH': "N'GPU_TECH'  -- 8 chars max",
        'PRODTYPE': "[Product Type]  -- 3-5 chars max",
        'ZMOQ2': "CAST(number AS NVARCHAR)  -- numeric string",
        'ZMOQ1': "CAST(number AS NVARCHAR)  -- numeric string",
        'ZTKLEADTIME': "CAST(days AS NVARCHAR)  -- numeric string",
        'ZTKUNITCOST': "CAST(cost AS NVARCHAR) + N'.00'  -- price string",
        'ZVIRTUALKIT': "N'VIRTUAL' or N'PHYSICAL'  -- 8-9 chars max"
    }
    
    for col in problematic:
        name = col['name']
        max_len = col['max_length']
        
        if name in recommendations:
            print(f"{name:<20} (Max {max_len:>2}): {recommendations[name]}")
        else:
            print(f"{name:<20} (Max {max_len:>2}): ** NEEDS MANUAL REVIEW **")

if __name__ == "__main__":
    generate_safe_values()
