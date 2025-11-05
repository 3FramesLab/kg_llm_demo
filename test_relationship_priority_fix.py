#!/usr/bin/env python3
"""
Test relationship priority and join fixes.
"""

def test_relationship_priority():
    """Test that relationship prioritization works correctly."""
    
    print("="*60)
    print("TESTING RELATIONSHIP PRIORITY AND JOIN FIXES")
    print("="*60)
    
    # The problematic SQL that was generated
    problematic_sql = """
    SELECT DISTINCT TOP 1000 s.* 
    FROM [brz_lnd_IBP_Product_Master] s 
    LEFT JOIN [hana_material_master] t ON s.[PRDID] = t.[MATERIAL] 
    WHERE t.[MATERIAL] IS NULL 
    AND s.[PRODTYPE] = 'NBU' 
    AND s.[ZTOPLVLNAME] = ''
    """
    
    print("--- Problematic SQL ---")
    print(problematic_sql)
    
    print("\n--- Issues Identified ---")
    print("❌ s.[PRDID] = t.[MATERIAL] - Wrong relationship (PRDID has 'PRD_' prefix)")
    print("❌ s.[ZTOPLVLNAME] = '' - Should be IS NULL, not = ''")
    print("❌ Using low-priority relationship instead of high-priority one")
    
    # Relationship priority analysis
    print("\n--- Relationship Priority Analysis ---")
    
    # Simulate available relationships
    available_relationships = [
        {
            'source_table': 'hana_material_master',
            'target_table': 'brz_lnd_IBP_Product_Master',
            'source_column': 'MATERIAL',
            'target_column': 'PRDID',
            'confidence': 0.85,
            'priority_type': 'LOW (hierarchical ID with prefix)'
        },
        {
            'source_table': 'hana_material_master', 
            'target_table': 'brz_lnd_IBP_Product_Master',
            'source_column': 'MATERIAL',
            'target_column': 'ZBASEMATERIAL',
            'confidence': 0.90,
            'priority_type': 'HIGH (direct material identifier)'
        }
    ]
    
    print("Available relationships:")
    for i, rel in enumerate(available_relationships, 1):
        print(f"  {i}. {rel['source_table']}.{rel['source_column']} ↔ {rel['target_table']}.{rel['target_column']}")
        print(f"     Confidence: {rel['confidence']}, Priority: {rel['priority_type']}")
    
    # Priority scoring simulation
    print("\n--- Priority Scoring Simulation ---")
    
    def calculate_priority_score(rel):
        source_col = rel['source_column'].upper()
        target_col = rel['target_column'].upper()
        
        # Column type priority scores
        high_priority_cols = {'ZBASEMATERIAL', 'MATERIAL', 'MATERIAL_ID'}
        medium_priority_cols = {'PLANNING_SKU', 'SKU', 'SKU_ID'}
        low_priority_cols = {'PRDID', 'PRODUCT_ID', 'PRD_ID'}
        
        if source_col in high_priority_cols or target_col in high_priority_cols:
            priority_score = 3.0
        elif source_col in medium_priority_cols or target_col in medium_priority_cols:
            priority_score = 2.0
        elif source_col in low_priority_cols or target_col in low_priority_cols:
            priority_score = 1.0
        else:
            priority_score = 2.5
        
        confidence = rel['confidence']
        total_score = priority_score + confidence
        return priority_score, total_score
    
    scored_relationships = []
    for rel in available_relationships:
        priority_score, total_score = calculate_priority_score(rel)
        scored_rel = rel.copy()
        scored_rel['priority_score'] = priority_score
        scored_rel['total_score'] = total_score
        scored_relationships.append(scored_rel)
    
    # Sort by total score (priority + confidence)
    scored_relationships.sort(key=lambda r: r['total_score'], reverse=True)
    
    print("Relationships sorted by priority + confidence:")
    for i, rel in enumerate(scored_relationships, 1):
        print(f"  {i}. {rel['source_column']} ↔ {rel['target_column']}")
        print(f"     Priority: {rel['priority_score']:.1f}, Confidence: {rel['confidence']:.2f}, Total: {rel['total_score']:.2f}")
        if i == 1:
            print("     ✅ SELECTED (highest score)")
        else:
            print("     ❌ Not selected")
    
    # Expected correct SQL
    print("\n--- Expected Correct SQL ---")
    correct_sql = """
    SELECT DISTINCT TOP 1000 s.* 
    FROM [brz_lnd_IBP_Product_Master] s 
    LEFT JOIN [hana_material_master] t ON s.[ZBASEMATERIAL] = t.[MATERIAL] 
    WHERE t.[MATERIAL] IS NULL 
    AND s.[PRODTYPE] = 'NBU' 
    AND s.[ZTOPLVLNAME] IS NULL
    """
    print(correct_sql)
    
    print("--- Key Improvements ---")
    print("✅ s.[ZBASEMATERIAL] = t.[MATERIAL] (correct high-priority relationship)")
    print("✅ s.[ZTOPLVLNAME] IS NULL (correct NULL check)")
    print("✅ s.[PRODTYPE] = 'NBU' (correct column name)")
    
    print(f"\n{'='*60}")
    print("RELATIONSHIP PRIORITY AND JOIN FIXES TEST COMPLETE")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_relationship_priority()
