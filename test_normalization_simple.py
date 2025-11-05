#!/usr/bin/env python3
"""
Simple test to verify the relationship normalization implementation works.
"""

import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_standalone_normalization():
    """Test the normalization logic standalone."""
    try:
        from table_name_normalizer import CombinedNormalizer
        
        # Initialize normalizer
        normalizer = CombinedNormalizer(table_strategy='remove_prefix')
        logger.info("✅ CombinedNormalizer imported and initialized successfully")
        
        # Test relationships with your actual data patterns
        test_relationships = [
            {
                "source_id": "table_hana_material_master",
                "target_id": "table_brz_lnd_OPS_EXCEL_GPU",
                "relationship_type": "SEMANTIC_REFERENCE",
                "source_column": "Business Unit",
                "target_column": "Business_Unit",
                "properties": {
                    "llm_inferred": True,
                    "llm_confidence": 0.75,
                    "llm_reasoning": "The columns 'Business Unit' and 'Business_Unit' denote the same business entity, facilitating organizational context understanding.",
                    "data_type_match": "NVARCHAR ↔ NVARCHAR"
                }
            },
            {
                "source_id": "hana_material_master",
                "target_id": "brz_lnd_RBP_GPU",
                "relationship_type": "MATCHES",
                "source_column": "MATERIAL",
                "target_column": "Material",
                "properties": {
                    "explicit": True,
                    "confidence": 0.95
                }
            },
            {
                "source_id": "brz_lnd_SAR_Excel_NBU",
                "target_id": "table_hana_material_master",
                "relationship_type": "REFERENCES",
                "source_column": "Material",
                "target_column": "MATERIAL",
                "properties": {
                    "explicit": True,
                    "confidence": 0.90
                }
            }
        ]
        
        logger.info("🔍 TESTING YOUR ACTUAL RELATIONSHIP PATTERNS")
        logger.info("=" * 70)
        
        logger.info("BEFORE NORMALIZATION:")
        for i, rel in enumerate(test_relationships, 1):
            logger.info(f"{i}. {rel['source_id']} → {rel['target_id']} ({rel['relationship_type']})")
        
        # Apply normalization
        normalized_relationships = normalizer.normalize_relationships(test_relationships)
        
        logger.info("\nAFTER NORMALIZATION:")
        for i, rel in enumerate(normalized_relationships, 1):
            swapped = "🔄" if rel['properties'].get('direction_swapped') else "✓"
            logger.info(f"{i}. {swapped} {rel['source_id']} → {rel['target_id']} ({rel['relationship_type']})")
        
        # Detailed analysis
        logger.info("\n📊 DETAILED ANALYSIS:")
        logger.info("-" * 50)
        
        for i, (original, normalized) in enumerate(zip(test_relationships, normalized_relationships), 1):
            logger.info(f"\nRelationship {i}:")
            logger.info(f"  Original: {original['source_id']} → {original['target_id']}")
            logger.info(f"  Normalized: {normalized['source_id']} → {normalized['target_id']}")
            logger.info(f"  Direction swapped: {normalized['properties'].get('direction_swapped', False)}")
            logger.info(f"  Table names normalized: {normalized['properties'].get('table_names_normalized', False)}")
            
            # Check if hana_material_master is now target
            if normalized['target_id'] == 'hana_material_master':
                logger.info(f"  ✅ hana_material_master is TARGET")
            else:
                logger.info(f"  ❌ hana_material_master is NOT target")
        
        # Final validation
        master_as_target_count = sum(1 for rel in normalized_relationships 
                                    if rel['target_id'] == 'hana_material_master')
        
        logger.info(f"\n🎯 FINAL VALIDATION:")
        logger.info(f"Total relationships: {len(normalized_relationships)}")
        logger.info(f"hana_material_master as target: {master_as_target_count}")
        logger.info(f"Success rate: {master_as_target_count}/{len(normalized_relationships)} = {master_as_target_count/len(normalized_relationships)*100:.1f}%")
        
        # Check for consistent naming
        all_table_names = set()
        for rel in normalized_relationships:
            all_table_names.add(rel['source_id'])
            all_table_names.add(rel['target_id'])
        
        prefixed_names = [name for name in all_table_names if name.startswith('table_')]
        
        logger.info(f"\n🏷️ NAMING CONSISTENCY:")
        logger.info(f"All table names: {sorted(all_table_names)}")
        logger.info(f"Names with 'table_' prefix: {len(prefixed_names)}")
        
        if len(prefixed_names) == 0:
            logger.info("✅ SUCCESS: All table names are clean (no 'table_' prefixes)")
        else:
            logger.warning(f"⚠️ WARNING: {len(prefixed_names)} names still have 'table_' prefix")
        
        # Overall success check
        success = (master_as_target_count == len(normalized_relationships) and len(prefixed_names) == 0)
        
        if success:
            logger.info("\n🎉 IMPLEMENTATION SUCCESS!")
            logger.info("✅ All relationships have hana_material_master as target")
            logger.info("✅ All table names are consistently clean")
            logger.info("✅ Direction and naming normalization working perfectly!")
        else:
            logger.warning("\n⚠️ IMPLEMENTATION ISSUES DETECTED")
            if master_as_target_count != len(normalized_relationships):
                logger.warning("❌ Not all relationships have hana_material_master as target")
            if len(prefixed_names) > 0:
                logger.warning("❌ Some table names still have 'table_' prefix")
        
        return success
        
    except ImportError as e:
        logger.error(f"❌ Failed to import normalizer: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run the standalone test."""
    logger.info("🚀 TESTING RELATIONSHIP NORMALIZATION (STANDALONE)")
    logger.info("=" * 80)
    
    success = test_standalone_normalization()
    
    if success:
        logger.info("\n🎯 CONCLUSION: IMPLEMENTATION IS WORKING PERFECTLY!")
        logger.info("The normalization will be applied automatically when:")
        logger.info("1. LLM infers relationships in schema_parser.py")
        logger.info("2. Explicit relationships are created in kg_relationship_service.py")
        logger.info("3. Foreign key relationships are processed")
        logger.info("4. Natural language relationships are added")
    else:
        logger.error("\n❌ CONCLUSION: IMPLEMENTATION HAS ISSUES")
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
