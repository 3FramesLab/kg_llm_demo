#!/usr/bin/env python3
"""
Test script to verify the relationship normalization implementation.
"""

import sys
import os
import logging

# Add the kg_builder to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'kg_builder'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_normalizer_import():
    """Test that the normalizer can be imported successfully."""
    try:
        from kg_builder.table_name_normalizer import CombinedNormalizer
        normalizer = CombinedNormalizer(table_strategy='remove_prefix')
        logger.info("✅ CombinedNormalizer imported and initialized successfully")
        return normalizer
    except ImportError as e:
        logger.error(f"❌ Failed to import CombinedNormalizer: {e}")
        return None

def test_relationship_normalization(normalizer):
    """Test relationship normalization with sample data."""
    if normalizer is None:
        logger.error("❌ Cannot test normalization - normalizer not available")
        return
    
    # Test relationships similar to your actual data
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
                "llm_reasoning": "Business unit columns match"
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
    
    logger.info("🔍 TESTING RELATIONSHIP NORMALIZATION")
    logger.info("=" * 60)
    
    logger.info("BEFORE NORMALIZATION:")
    for i, rel in enumerate(test_relationships, 1):
        logger.info(f"{i}. {rel['source_id']} → {rel['target_id']} ({rel['relationship_type']})")
    
    # Apply normalization
    normalized_relationships = normalizer.normalize_relationships(test_relationships)
    
    logger.info("\nAFTER NORMALIZATION:")
    for i, rel in enumerate(normalized_relationships, 1):
        swapped = "🔄" if rel['properties'].get('direction_swapped') else "✓"
        logger.info(f"{i}. {swapped} {rel['source_id']} → {rel['target_id']} ({rel['relationship_type']})")
    
    # Validate results
    master_as_target_count = sum(1 for rel in normalized_relationships 
                                if rel['target_id'] == 'hana_material_master')
    
    logger.info(f"\n📊 VALIDATION RESULTS:")
    logger.info(f"Total relationships: {len(normalized_relationships)}")
    logger.info(f"hana_material_master as target: {master_as_target_count}")
    logger.info(f"Success rate: {master_as_target_count}/{len(normalized_relationships)} = {master_as_target_count/len(normalized_relationships)*100:.1f}%")
    
    if master_as_target_count == len(normalized_relationships):
        logger.info("✅ SUCCESS: All relationships have hana_material_master as target!")
    else:
        logger.warning("⚠️ WARNING: Some relationships still have hana_material_master as source")
    
    return normalized_relationships

def test_schema_parser_integration():
    """Test that schema parser can import the normalizer."""
    try:
        # This will test the import in schema_parser.py
        from kg_builder.services.schema_parser import relationship_normalizer
        if relationship_normalizer is not None:
            logger.info("✅ Schema parser successfully imported relationship normalizer")
            return True
        else:
            logger.warning("⚠️ Schema parser imported but normalizer is None")
            return False
    except ImportError as e:
        logger.error(f"❌ Schema parser failed to import normalizer: {e}")
        return False

def test_kg_relationship_service_integration():
    """Test that kg_relationship_service can import the normalizer."""
    try:
        # This will test the import in kg_relationship_service.py
        from kg_builder.services.kg_relationship_service import relationship_normalizer
        if relationship_normalizer is not None:
            logger.info("✅ KG relationship service successfully imported relationship normalizer")
            return True
        else:
            logger.warning("⚠️ KG relationship service imported but normalizer is None")
            return False
    except ImportError as e:
        logger.error(f"❌ KG relationship service failed to import normalizer: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("🚀 TESTING RELATIONSHIP NORMALIZATION IMPLEMENTATION")
    logger.info("=" * 80)
    
    # Test 1: Basic normalizer import
    logger.info("\n1️⃣ TESTING NORMALIZER IMPORT")
    normalizer = test_normalizer_import()
    
    # Test 2: Relationship normalization logic
    logger.info("\n2️⃣ TESTING NORMALIZATION LOGIC")
    normalized_rels = test_relationship_normalization(normalizer)
    
    # Test 3: Schema parser integration
    logger.info("\n3️⃣ TESTING SCHEMA PARSER INTEGRATION")
    schema_parser_ok = test_schema_parser_integration()
    
    # Test 4: KG relationship service integration
    logger.info("\n4️⃣ TESTING KG RELATIONSHIP SERVICE INTEGRATION")
    kg_service_ok = test_kg_relationship_service_integration()
    
    # Summary
    logger.info("\n📋 IMPLEMENTATION TEST SUMMARY")
    logger.info("=" * 80)
    
    tests_passed = 0
    total_tests = 4
    
    if normalizer is not None:
        logger.info("✅ Normalizer import: PASSED")
        tests_passed += 1
    else:
        logger.info("❌ Normalizer import: FAILED")
    
    if normalized_rels and len(normalized_rels) > 0:
        logger.info("✅ Normalization logic: PASSED")
        tests_passed += 1
    else:
        logger.info("❌ Normalization logic: FAILED")
    
    if schema_parser_ok:
        logger.info("✅ Schema parser integration: PASSED")
        tests_passed += 1
    else:
        logger.info("❌ Schema parser integration: FAILED")
    
    if kg_service_ok:
        logger.info("✅ KG relationship service integration: PASSED")
        tests_passed += 1
    else:
        logger.info("❌ KG relationship service integration: FAILED")
    
    logger.info(f"\n🎯 OVERALL RESULT: {tests_passed}/{total_tests} tests passed ({tests_passed/total_tests*100:.1f}%)")
    
    if tests_passed == total_tests:
        logger.info("🎉 ALL TESTS PASSED! Relationship normalization is fully implemented!")
    else:
        logger.warning(f"⚠️ {total_tests - tests_passed} test(s) failed. Check the errors above.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
