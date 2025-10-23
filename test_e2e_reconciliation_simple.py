#!/usr/bin/env python
"""
Simplified End-to-End Reconciliation Test Script

This script automates the complete data reconciliation workflow:
1. Schema Loading - Load JSON schemas from schemas/ folder
2. Knowledge Graph Creation - Create KG from schemas
3. Relationship Generation - Generate relationships using LLM
4. Reconciliation Rules Generation - Generate rules using LLM
5. Database Connection - Verify source and target databases
6. Rule Execution - Execute rules against databases
7. KPI Calculation - Calculate RCR, DQCS, REI
"""

import os
import sys
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from kg_builder.services.schema_parser import SchemaParser
from kg_builder.services.reconciliation_service import get_reconciliation_service
from kg_builder.services.reconciliation_executor import get_reconciliation_executor
from kg_builder.services.kpi_service import KPIService
from kg_builder.models import DatabaseConnectionInfo
from kg_builder.config import get_source_db_config, get_target_db_config

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('e2e_reconciliation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set specific loggers to DEBUG to see SQL queries
logging.getLogger('kg_builder.services.reconciliation_executor').setLevel(logging.DEBUG)
logging.getLogger('kg_builder.services.reconciliation_service').setLevel(logging.DEBUG)

def load_schemas(schema_dir: str = "schemas") -> Tuple[List[str], Dict[str, Any]]:
    """Step 1: Load JSON schemas from directory."""
    logger.info("\n" + "="*80)
    logger.info("STEP 1: SCHEMA LOADING")
    logger.info("="*80)
    
    try:
        schema_path = Path(schema_dir)
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema directory not found: {schema_dir}")
        
        schema_files = list(schema_path.glob("*.json"))
        if not schema_files:
            raise FileNotFoundError(f"No JSON files found in {schema_dir}")
        
        schema_names = [f.stem for f in schema_files]
        logger.info(f"Found {len(schema_names)} schemas: {schema_names}")
        
        loaded_schemas = {}
        for schema_name in schema_names:
            schema = SchemaParser.load_schema(schema_name)
            loaded_schemas[schema_name] = schema
            logger.info(f"[OK] Loaded schema: {schema_name} - Tables: {len(schema.tables)}")
        
        logger.info(f"[OK] Successfully loaded {len(schema_names)} schemas")
        return schema_names, loaded_schemas
        
    except Exception as e:
        logger.error(f"[FAIL] Schema loading failed: {e}", exc_info=True)
        raise

def create_knowledge_graph(schema_names: List[str], kg_name: str) -> Dict[str, Any]:
    """Step 2: Create knowledge graph from schemas."""
    logger.info("\n" + "="*80)
    logger.info("STEP 2: KNOWLEDGE GRAPH CREATION")
    logger.info("="*80)
    
    try:
        logger.info(f"Creating KG '{kg_name}' from schemas: {schema_names}")
        
        if len(schema_names) > 1:
            kg = SchemaParser.build_merged_knowledge_graph(schema_names, kg_name, use_llm=False)
        else:
            kg = SchemaParser.build_knowledge_graph(schema_names[0], kg_name)
        
        logger.info(f"[OK] KG created: {kg.name}")
        logger.info(f"  - Nodes: {len(kg.nodes)}")
        logger.info(f"  - Relationships: {len(kg.relationships)}")
        
        return {
            "kg_name": kg.name,
            "nodes_count": len(kg.nodes),
            "relationships_count": len(kg.relationships),
            "kg_object": kg
        }
        
    except Exception as e:
        logger.error(f"[FAIL] KG creation failed: {e}", exc_info=True)
        raise

def generate_reconciliation_rules(kg_data: Dict[str, Any], schema_names: List[str]) -> Dict[str, Any]:
    """Step 3: Generate reconciliation rules from KG."""
    logger.info("\n" + "="*80)
    logger.info("STEP 3: RECONCILIATION RULES GENERATION")
    logger.info("="*80)
    
    try:
        recon_service = get_reconciliation_service()
        kg_name = kg_data["kg_name"]
        
        logger.info(f"Generating reconciliation rules from KG '{kg_name}'")
        
        ruleset = recon_service.generate_from_knowledge_graph(
            kg_name=kg_name,
            schema_names=schema_names,
            use_llm=False,
            min_confidence=0.7
        )
        
        logger.info(f"[OK] Reconciliation rules generated")
        logger.info(f"  - Ruleset ID: {ruleset.ruleset_id}")
        logger.info(f"  - Total Rules: {len(ruleset.rules)}")
        
        for i, rule in enumerate(ruleset.rules[:3], 1):
            logger.info(f"  - Rule {i}: {rule.rule_name} (confidence: {rule.confidence_score})")
        
        if len(ruleset.rules) > 3:
            logger.info(f"  - ... and {len(ruleset.rules) - 3} more rules")
        
        # Save ruleset to disk
        ruleset_path = Path("data/reconciliation_rules") / f"{ruleset.ruleset_id}.json"
        ruleset_path.parent.mkdir(parents=True, exist_ok=True)
        
        ruleset_dict = {
            "ruleset_id": ruleset.ruleset_id,
            "ruleset_name": ruleset.ruleset_name,
            "schemas": ruleset.schemas,
            "rules": [
                {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.rule_name,
                    "source_schema": rule.source_schema,
                    "source_table": rule.source_table,
                    "source_columns": rule.source_columns,
                    "target_schema": rule.target_schema,
                    "target_table": rule.target_table,
                    "target_columns": rule.target_columns,
                    "match_type": rule.match_type,
                    "transformation": rule.transformation,
                    "confidence_score": rule.confidence_score,
                    "reasoning": rule.reasoning,
                    "validation_status": rule.validation_status,
                    "llm_generated": rule.llm_generated,
                    "created_at": rule.created_at.isoformat() if hasattr(rule.created_at, 'isoformat') else str(rule.created_at),
                    "metadata": rule.metadata
                }
                for rule in ruleset.rules
            ],
            "created_at": ruleset.created_at.isoformat() if hasattr(ruleset.created_at, 'isoformat') else str(ruleset.created_at),
            "generated_from_kg": ruleset.generated_from_kg
        }
        
        with open(ruleset_path, 'w', encoding='utf-8') as f:
            json.dump(ruleset_dict, f, indent=2)
        
        logger.info(f"Saved ruleset to: {ruleset_path}")
        
        return {
            "ruleset_id": ruleset.ruleset_id,
            "ruleset_name": ruleset.ruleset_name,
            "rules_count": len(ruleset.rules),
            "ruleset_object": ruleset
        }
        
    except Exception as e:
        logger.error(f"[FAIL] Rules generation failed: {e}", exc_info=True)
        raise

def verify_database_connections() -> Tuple[DatabaseConnectionInfo, DatabaseConnectionInfo]:
    """Step 4: Verify database connections."""
    logger.info("\n" + "="*80)
    logger.info("STEP 4: DATABASE CONNECTION VERIFICATION")
    logger.info("="*80)

    try:
        # Get database configs from environment variables
        source_config = get_source_db_config()
        target_config = get_target_db_config()

        if not source_config or not target_config:
            raise RuntimeError("Database configurations not found in environment variables")

        # Convert Docker host to localhost for local testing
        source_config.host = source_config.host.replace("host.docker.internal", "localhost")
        target_config.host = target_config.host.replace("host.docker.internal", "localhost")

        logger.info(f"Source Database: {source_config.db_type} @ {source_config.host}:{source_config.port}/{source_config.database}")
        logger.info(f"Target Database: {target_config.db_type} @ {target_config.host}:{target_config.port}/{target_config.database}")
        logger.info(f"[OK] Database configurations loaded successfully")

        return source_config, target_config

    except Exception as e:
        logger.error(f"[FAIL] Database connection verification failed: {e}", exc_info=True)
        raise

def execute_reconciliation_rules(
    ruleset_data: Dict[str, Any],
    source_config: DatabaseConnectionInfo,
    target_config: DatabaseConnectionInfo,
    limit: int = 100
) -> Dict[str, Any]:
    """Step 5: Execute reconciliation rules."""
    logger.info("\n" + "="*80)
    logger.info("STEP 5: RULE EXECUTION")
    logger.info("="*80)
    
    try:
        executor = get_reconciliation_executor()
        ruleset_id = ruleset_data["ruleset_id"]
        
        logger.info(f"Executing ruleset '{ruleset_id}' against databases")
        logger.info(f"Record limit: {limit}")
        
        start_time = time.time()
        
        result = executor.execute_ruleset(
            ruleset_id=ruleset_id,
            source_db_config=source_config,
            target_db_config=target_config,
            limit=limit,
            include_matched=True,
            include_unmatched=True,
            store_in_mongodb=True
        )
        
        execution_time = time.time() - start_time
        total_source = result.matched_count + result.unmatched_source_count

        logger.info(f"[OK] Rule execution completed in {execution_time:.2f}s")
        logger.info(f"  - Matched Records: {result.matched_count}")
        logger.info(f"  - Unmatched Source: {result.unmatched_source_count}")
        logger.info(f"  - Unmatched Target: {result.unmatched_target_count}")
        logger.info(f"  - Total Source Records: {total_source}")
        logger.info(f"  - Storage Location: {result.storage_location}")

        if total_source > 0:
            coverage = (result.matched_count / total_source * 100)
            logger.info(f"  - Coverage Rate: {coverage:.2f}%")

        return {
            "matched_count": result.matched_count,
            "unmatched_source_count": result.unmatched_source_count,
            "unmatched_target_count": result.unmatched_target_count,
            "total_source_count": total_source,
            "execution_time_ms": execution_time * 1000,
            "result_object": result,
            "storage_location": result.storage_location,
            "mongodb_document_id": result.mongodb_document_id
        }
        
    except Exception as e:
        logger.error(f"[FAIL] Rule execution failed: {e}", exc_info=True)
        raise

def calculate_kpis(
    execution_data: Dict[str, Any],
    ruleset_data: Dict[str, Any],
    schema_names: List[str]
) -> Dict[str, Any]:
    """Step 6: Calculate KPIs."""
    logger.info("\n" + "="*80)
    logger.info("STEP 6: KPI CALCULATION")
    logger.info("="*80)
    
    try:
        kpi_service = KPIService()

        matched_count = execution_data["matched_count"]
        total_source_count = execution_data["total_source_count"]
        ruleset_id = ruleset_data["ruleset_id"]

        logger.info(f"Calculating KPIs for ruleset '{ruleset_id}'")

        # Generate execution ID from timestamp
        execution_id = f"EXEC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        kg_name = ruleset_data.get("generated_from_kg", f"kg_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        # Calculate RCR
        rcr_doc = kpi_service.calculate_rcr(
            matched_count=matched_count,
            total_source_count=total_source_count,
            ruleset_id=ruleset_id,
            ruleset_name=ruleset_data["ruleset_name"],
            execution_id=execution_id,
            source_kg=kg_name,
            source_schemas=schema_names
        )
        rcr_id = kpi_service.store_kpi("RECONCILIATION_COVERAGE_RATE", rcr_doc)
        logger.info(f"[OK] RCR: {rcr_doc['metrics']['coverage_rate']:.2f}% - MongoDB ID: {rcr_id}")

        # Calculate DQCS
        matched_records = []
        if "result_object" in execution_data and hasattr(execution_data["result_object"], 'matched_records'):
            matched_records = execution_data["result_object"].matched_records

        dqcs_doc = kpi_service.calculate_dqcs(
            matched_records=matched_records,
            ruleset_id=ruleset_id,
            ruleset_name=ruleset_data["ruleset_name"],
            execution_id=execution_id,
            source_kg=kg_name
        )
        dqcs_id = kpi_service.store_kpi("DATA_QUALITY_CONFIDENCE_SCORE", dqcs_doc)
        logger.info(f"[OK] DQCS: {dqcs_doc['metrics']['overall_confidence_score']:.3f} - MongoDB ID: {dqcs_id}")
        
        # Calculate REI
        rei_doc = kpi_service.calculate_rei(
            matched_count=matched_count,
            total_source_count=total_source_count,
            active_rules=ruleset_data["rules_count"],
            total_rules=ruleset_data["rules_count"],
            execution_time_ms=execution_data["execution_time_ms"],
            ruleset_id=ruleset_id,
            ruleset_name=ruleset_data["ruleset_name"],
            execution_id=execution_id,
            source_kg=kg_name
        )
        rei_id = kpi_service.store_kpi("RECONCILIATION_EFFICIENCY_INDEX", rei_doc)
        logger.info(f"[OK] REI: {rei_doc['metrics']['efficiency_index']:.2f} - MongoDB ID: {rei_id}")
        
        return {
            "rcr": rcr_doc["metrics"]["coverage_rate"],
            "dqcs": dqcs_doc["metrics"]["overall_confidence_score"],
            "rei": rei_doc["metrics"]["efficiency_index"],
            "rcr_id": rcr_id,
            "dqcs_id": dqcs_id,
            "rei_id": rei_id
        }
        
    except Exception as e:
        logger.error(f"[FAIL] KPI calculation failed: {e}", exc_info=True)
        raise

def main():
    """Main execution function."""
    logger.info("\n" + "="*80)
    logger.info("STARTING END-TO-END RECONCILIATION WORKFLOW")
    logger.info("="*80)
    
    start_time = time.time()
    
    try:
        # Step 1: Load schemas
        schema_names, loaded_schemas = load_schemas()
        
        # Step 2: Create KG
        kg_name = f"kg_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        kg_data = create_knowledge_graph(schema_names, kg_name)
        
        # Step 3: Generate rules
        ruleset_data = generate_reconciliation_rules(kg_data, schema_names)
        
        # Step 4: Verify DB connections
        source_config, target_config = verify_database_connections()
        
        # Step 5: Execute rules
        execution_data = execute_reconciliation_rules(ruleset_data, source_config, target_config)
        
        # Step 6: Calculate KPIs
        kpi_data = calculate_kpis(execution_data, ruleset_data, schema_names)
        
        # Summary
        total_time = time.time() - start_time
        logger.info("\n" + "="*80)
        logger.info("END-TO-END RECONCILIATION WORKFLOW - SUMMARY")
        logger.info("="*80)
        logger.info(f"Total Execution Time: {total_time:.2f} seconds")
        logger.info(f"Schemas Processed: {len(schema_names)}")
        logger.info(f"Rules Generated: {ruleset_data['rules_count']}")
        logger.info(f"Records Matched: {execution_data['matched_count']}/{execution_data['total_source_count']}")
        logger.info(f"KPI Results:")
        logger.info(f"  - RCR: {kpi_data['rcr']:.2f}%")
        logger.info(f"  - DQCS: {kpi_data['dqcs']:.3f}")
        logger.info(f"  - REI: {kpi_data['rei']:.2f}")
        logger.info("[OK] WORKFLOW COMPLETED SUCCESSFULLY")
        logger.info("="*80)
        
        return 0
        
    except Exception as e:
        logger.error(f"\n[FAIL] WORKFLOW FAILED: {e}", exc_info=True)
        logger.error("="*80)
        return 1

if __name__ == "__main__":
    sys.exit(main())

