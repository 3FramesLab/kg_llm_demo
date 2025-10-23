"""
Test script for KPI Service implementation.

Tests the three KPIs:
1. Reconciliation Coverage Rate (RCR)
2. Data Quality Confidence Score (DQCS)
3. Reconciliation Efficiency Index (REI)
"""

import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_kpi_calculations():
    """Test KPI calculations with sample data."""
    try:
        from kg_builder.services.kpi_service import KPIService
        
        logger.info("=" * 80)
        logger.info("KPI SERVICE TEST")
        logger.info("=" * 80)
        
        # Initialize KPI service
        logger.info("\n1. Initializing KPI Service...")
        kpi_service = KPIService()
        kpi_service._ensure_indexes()
        logger.info("✓ KPI Service initialized successfully")
        
        # Sample data from RECON_23B2B063
        ruleset_id = "RECON_23B2B063"
        ruleset_name = "Reconciliation_Test_New_321"
        execution_id = "EXEC_20251023_143022"
        source_kg = "Test_New_321"
        source_schemas = ["orderMgmt-catalog", "qinspect-designcode"]
        
        # Test data
        matched_count = 1247
        total_source_count = 1300
        active_rules = 18
        total_rules = 22
        execution_time_ms = 2500
        
        # Sample matched records with confidence scores
        matched_records = [
            {"match_confidence": 0.95, "rule_used": "RULE_57DFE374"},
            {"match_confidence": 0.85, "rule_used": "RULE_538D152A"},
            {"match_confidence": 0.75, "rule_used": "RULE_4A051192"},
        ] * 415  # Repeat to get ~1245 records
        
        # =====================================================================
        # Test 1: Calculate RCR
        # =====================================================================
        logger.info("\n2. Testing Reconciliation Coverage Rate (RCR)...")
        rcr_doc = kpi_service.calculate_rcr(
            matched_count=matched_count,
            total_source_count=total_source_count,
            ruleset_id=ruleset_id,
            ruleset_name=ruleset_name,
            execution_id=execution_id,
            source_kg=source_kg,
            source_schemas=source_schemas
        )
        
        logger.info(f"   RCR Calculation:")
        logger.info(f"   - Matched Records: {rcr_doc['metrics']['matched_records']}")
        logger.info(f"   - Total Source: {rcr_doc['metrics']['total_source_records']}")
        logger.info(f"   - Coverage Rate: {rcr_doc['metrics']['coverage_rate']}%")
        logger.info(f"   - Status: {rcr_doc['thresholds']['status']}")
        
        # Store RCR
        rcr_id = kpi_service.store_kpi("RECONCILIATION_COVERAGE_RATE", rcr_doc)
        logger.info(f"   ✓ RCR stored with ID: {rcr_id}")
        
        # =====================================================================
        # Test 2: Calculate DQCS
        # =====================================================================
        logger.info("\n3. Testing Data Quality Confidence Score (DQCS)...")
        dqcs_doc = kpi_service.calculate_dqcs(
            matched_records=matched_records,
            ruleset_id=ruleset_id,
            ruleset_name=ruleset_name,
            execution_id=execution_id,
            source_kg=source_kg
        )
        
        logger.info(f"   DQCS Calculation:")
        logger.info(f"   - Overall Confidence: {dqcs_doc['metrics']['overall_confidence_score']}")
        logger.info(f"   - Total Matched: {dqcs_doc['metrics']['total_matched_records']}")
        logger.info(f"   - High Confidence (0.9-1.0): {dqcs_doc['metrics']['high_confidence_matches']}")
        logger.info(f"   - Medium Confidence (0.8-0.9): {dqcs_doc['metrics']['medium_confidence_matches']}")
        logger.info(f"   - Low Confidence (<0.8): {dqcs_doc['metrics']['low_confidence_matches']}")
        logger.info(f"   - Status: {dqcs_doc['thresholds']['current_status']}")
        
        # Store DQCS
        dqcs_id = kpi_service.store_kpi("DATA_QUALITY_CONFIDENCE_SCORE", dqcs_doc)
        logger.info(f"   ✓ DQCS stored with ID: {dqcs_id}")
        
        # =====================================================================
        # Test 3: Calculate REI
        # =====================================================================
        logger.info("\n4. Testing Reconciliation Efficiency Index (REI)...")
        rei_doc = kpi_service.calculate_rei(
            matched_count=matched_count,
            total_source_count=total_source_count,
            active_rules=active_rules,
            total_rules=total_rules,
            execution_time_ms=execution_time_ms,
            ruleset_id=ruleset_id,
            ruleset_name=ruleset_name,
            execution_id=execution_id,
            source_kg=source_kg
        )
        
        logger.info(f"   REI Calculation:")
        logger.info(f"   - Efficiency Index: {rei_doc['metrics']['efficiency_index']}")
        logger.info(f"   - Match Success Rate: {rei_doc['metrics']['match_success_rate']}%")
        logger.info(f"   - Rule Utilization: {rei_doc['metrics']['rule_utilization']}%")
        logger.info(f"   - Speed Factor: {rei_doc['metrics']['speed_factor']}%")
        logger.info(f"   - Records/Second: {rei_doc['performance_details']['records_per_second']}")
        logger.info(f"   - Status: {rei_doc['efficiency_assessment']['status']}")
        
        # Store REI
        rei_id = kpi_service.store_kpi("RECONCILIATION_EFFICIENCY_INDEX", rei_doc)
        logger.info(f"   ✓ REI stored with ID: {rei_id}")
        
        # =====================================================================
        # Test 4: Retrieve KPIs
        # =====================================================================
        logger.info("\n5. Testing KPI Retrieval...")
        
        retrieved_rcr = kpi_service.get_latest_kpi("RECONCILIATION_COVERAGE_RATE", ruleset_id)
        if retrieved_rcr:
            logger.info(f"   ✓ Retrieved RCR: {retrieved_rcr['metrics']['coverage_rate']}%")
        
        retrieved_dqcs = kpi_service.get_latest_kpi("DATA_QUALITY_CONFIDENCE_SCORE", ruleset_id)
        if retrieved_dqcs:
            logger.info(f"   ✓ Retrieved DQCS: {retrieved_dqcs['metrics']['overall_confidence_score']}")
        
        retrieved_rei = kpi_service.get_latest_kpi("RECONCILIATION_EFFICIENCY_INDEX", ruleset_id)
        if retrieved_rei:
            logger.info(f"   ✓ Retrieved REI: {retrieved_rei['metrics']['efficiency_index']}")
        
        # =====================================================================
        # Summary
        # =====================================================================
        logger.info("\n" + "=" * 80)
        logger.info("KPI TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"✓ RCR (Coverage Rate): {rcr_doc['metrics']['coverage_rate']}% - {rcr_doc['thresholds']['status']}")
        logger.info(f"✓ DQCS (Confidence): {dqcs_doc['metrics']['overall_confidence_score']} - {dqcs_doc['thresholds']['current_status']}")
        logger.info(f"✓ REI (Efficiency): {rei_doc['metrics']['efficiency_index']} - {rei_doc['efficiency_assessment']['status']}")
        logger.info("\n✓ All KPI tests passed successfully!")
        logger.info("=" * 80)
        
        kpi_service.close()
        return True
        
    except Exception as e:
        logger.error(f"✗ KPI test failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = test_kpi_calculations()
    sys.exit(0 if success else 1)

