#!/usr/bin/env python3
"""
Test script to analyze if PRDID can match with Material fields
from the newdqschemanov.json schema using various matching algorithms.
"""

import json
from difflib import SequenceMatcher
import re
from typing import List, Dict, Tuple

def load_schema(file_path: str) -> Dict:
    """Load schema from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def extract_material_fields(schema: Dict) -> List[Tuple[str, str, str]]:
    """Extract all fields that could be material-related."""
    material_fields = []
    
    for table_name, table_info in schema['tables'].items():
        for column in table_info['columns']:
            col_name = column['name']
            col_type = column['type']
            
            # Look for material-related fields
            if any(keyword in col_name.lower() for keyword in ['material', 'prd', 'product', 'sku', 'item']):
                material_fields.append((table_name, col_name, col_type))
    
    return material_fields

def fuzzy_match_score(str1: str, str2: str) -> float:
    """Calculate fuzzy match score between two strings."""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def semantic_similarity(field1: str, field2: str) -> Dict[str, float]:
    """Analyze semantic similarity between field names."""
    scores = {}
    
    # Direct name similarity
    scores['name_similarity'] = fuzzy_match_score(field1, field2)
    
    # Semantic keywords
    material_keywords = ['material', 'product', 'item', 'sku', 'part', 'component']
    id_keywords = ['id', 'uid', 'key', 'code', 'number']
    
    field1_lower = field1.lower()
    field2_lower = field2.lower()
    
    # Check if both are material-related
    field1_is_material = any(kw in field1_lower for kw in material_keywords)
    field2_is_material = any(kw in field2_lower for kw in material_keywords)
    
    # Check if both are ID-related
    field1_is_id = any(kw in field1_lower for kw in id_keywords)
    field2_is_id = any(kw in field2_lower for kw in id_keywords)
    
    scores['both_material_related'] = 1.0 if (field1_is_material and field2_is_material) else 0.0
    scores['both_id_related'] = 1.0 if (field1_is_id and field2_is_id) else 0.0
    
    # Pattern matching
    # PRDID could be "Product ID"
    if 'prd' in field1_lower and 'id' in field1_lower and 'material' in field2_lower:
        scores['pattern_match'] = 0.85
    elif 'material' in field1_lower and 'prd' in field2_lower and 'id' in field2_lower:
        scores['pattern_match'] = 0.85
    else:
        scores['pattern_match'] = 0.0
    
    return scores

def analyze_prdid_material_matches(schema: Dict) -> List[Dict]:
    """Analyze potential matches between PRDID and Material fields."""
    material_fields = extract_material_fields(schema)
    
    # Find PRDID field
    prdid_field = None
    for table_name, col_name, col_type in material_fields:
        if col_name.upper() == 'PRDID':
            prdid_field = (table_name, col_name, col_type)
            break
    
    if not prdid_field:
        return [{"error": "PRDID field not found in schema"}]
    
    # Find Material fields
    material_matches = []
    for table_name, col_name, col_type in material_fields:
        if col_name.upper() != 'PRDID' and 'material' in col_name.lower():
            
            # Calculate similarity scores
            similarity_scores = semantic_similarity('PRDID', col_name)
            
            # Calculate overall confidence
            confidence = (
                similarity_scores['name_similarity'] * 0.2 +
                similarity_scores['both_material_related'] * 0.4 +
                similarity_scores['both_id_related'] * 0.2 +
                similarity_scores['pattern_match'] * 0.2
            )
            
            match_info = {
                'source_table': prdid_field[0],
                'source_column': prdid_field[1],
                'source_type': prdid_field[2],
                'target_table': table_name,
                'target_column': col_name,
                'target_type': col_type,
                'confidence': round(confidence, 3),
                'similarity_scores': similarity_scores,
                'relationship_type': 'MATCHES' if confidence > 0.7 else 'POTENTIAL_MATCH',
                'reasoning': f"PRDID (Product ID) semantically matches {col_name} as both represent product/material identifiers"
            }
            
            material_matches.append(match_info)
    
    # Sort by confidence
    material_matches.sort(key=lambda x: x['confidence'], reverse=True)
    
    return material_matches

def main():
    """Main function to test PRDID-Material matching."""
    schema_file = 'schemas/newdqschemanov.json'
    
    try:
        # Load schema
        schema = load_schema(schema_file)
        print(f"Loaded schema with {schema['total_tables']} tables")
        
        # Extract all material-related fields
        material_fields = extract_material_fields(schema)
        print(f"\nFound {len(material_fields)} material-related fields:")
        for table, col, col_type in material_fields:
            print(f"  {table}.{col} ({col_type})")
        
        # Analyze PRDID-Material matches
        print(f"\n{'='*60}")
        print("PRDID-MATERIAL MATCHING ANALYSIS")
        print(f"{'='*60}")
        
        matches = analyze_prdid_material_matches(schema)
        
        if matches and 'error' not in matches[0]:
            print(f"\nFound {len(matches)} potential matches:")
            
            for i, match in enumerate(matches, 1):
                print(f"\n{i}. {match['source_table']}.{match['source_column']} → {match['target_table']}.{match['target_column']}")
                print(f"   Confidence: {match['confidence']}")
                print(f"   Relationship: {match['relationship_type']}")
                print(f"   Reasoning: {match['reasoning']}")
                print(f"   Similarity Scores:")
                for score_name, score_value in match['similarity_scores'].items():
                    print(f"     - {score_name}: {score_value}")
        else:
            print("No matches found or error occurred:")
            print(matches)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
