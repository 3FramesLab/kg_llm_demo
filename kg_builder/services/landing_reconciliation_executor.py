"""
Landing Reconciliation Executor.

Main service for executing reconciliation using landing database approach.
Orchestrates extraction, reconciliation, and KPI calculation.
"""
import logging
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from kg_builder.models import (
    DatabaseConnectionInfo,
    ReconciliationRuleSet,
    LandingExecutionRequest,
    LandingExecutionResponse,
    StagingTableInfo
)
from kg_builder.services.landing_db_connector import LandingDBConnector, get_landing_connector
from kg_builder.services.staging_manager import StagingManager, get_staging_manager
from kg_builder.services.data_extractor import DataExtractor, get_data_extractor
from kg_builder.services.landing_query_builder import LandingQueryBuilder, get_query_builder
from kg_builder.services.rule_storage import ReconciliationRuleStorage, get_rule_storage
from kg_builder import config

logger = logging.getLogger(__name__)


class LandingReconciliationExecutor:
    """Executes reconciliation using landing database approach."""

    def __init__(
        self,
        landing_connector: Optional[LandingDBConnector] = None,
        staging_manager: Optional[StagingManager] = None,
        data_extractor: Optional[DataExtractor] = None,
        query_builder: Optional[LandingQueryBuilder] = None
    ):
        """
        Initialize landing reconciliation executor.

        Args:
            landing_connector: Landing database connector
            staging_manager: Staging table manager
            data_extractor: Data extractor
            query_builder: Query builder
        """
        self.landing_connector = landing_connector or get_landing_connector()
        if self.landing_connector is None:
            raise ValueError("Landing database is not configured. Set LANDING_DB_ENABLED=true in config.")

        self.staging_manager = staging_manager or get_staging_manager(self.landing_connector)
        self.data_extractor = data_extractor or get_data_extractor(self.landing_connector, self.staging_manager)
        self.query_builder = query_builder or get_query_builder(config.LANDING_DB_TYPE)
        self.rule_storage = get_rule_storage()

        logger.info("Initialized LandingReconciliationExecutor")

    def execute(self, request: LandingExecutionRequest) -> LandingExecutionResponse:
        """
        Execute reconciliation with landing database.

        Args:
            request: Landing execution request

        Returns:
            Landing execution response with KPIs
        """
        total_start_time = time.time()
        execution_id = f"EXEC_{uuid.uuid4().hex[:8]}"

        logger.info(f"Starting landing-based reconciliation execution: {execution_id}")

        try:
            # Load ruleset
            ruleset = self.rule_storage.load_ruleset(request.ruleset_id)
            if not ruleset:
                raise ValueError(f"Ruleset not found: {request.ruleset_id}")

            logger.info(f"Loaded ruleset '{ruleset.ruleset_id}' with {len(ruleset.rules)} rules")

            # Phase 1: Extract source data to landing
            logger.info("=" * 60)
            logger.info("PHASE 1: Extracting source data to landing database")
            logger.info("=" * 60)

            extraction_start = time.time()

            source_staging_table, source_row_count, source_extract_time = \
                self.data_extractor.extract_to_landing(
                    source_db_config=request.source_db_config,
                    rules=ruleset.rules,
                    execution_id=execution_id,
                    ruleset_id=request.ruleset_id,
                    source_or_target='source',
                    limit=request.limit
                )

            logger.info(f"Source extraction: {source_row_count} rows in {source_extract_time:.2f}ms")

            # Phase 2: Extract target data to landing
            logger.info("=" * 60)
            logger.info("PHASE 2: Extracting target data to landing database")
            logger.info("=" * 60)

            target_staging_table, target_row_count, target_extract_time = \
                self.data_extractor.extract_to_landing(
                    source_db_config=request.target_db_config,
                    rules=ruleset.rules,
                    execution_id=execution_id,
                    ruleset_id=request.ruleset_id,
                    source_or_target='target',
                    limit=request.limit
                )

            logger.info(f"Target extraction: {target_row_count} rows in {target_extract_time:.2f}ms")

            total_extraction_time = (time.time() - extraction_start) * 1000

            # Phase 3: Reconcile in landing DB and calculate KPIs
            logger.info("=" * 60)
            logger.info("PHASE 3: Reconciling in landing database and calculating KPIs")
            logger.info("=" * 60)

            recon_start = time.time()

            kpi_results = self._execute_reconciliation_with_kpis(
                source_staging_table=source_staging_table,
                target_staging_table=target_staging_table,
                ruleset=ruleset
            )

            reconciliation_time = (time.time() - recon_start) * 1000

            logger.info(f"Reconciliation complete in {reconciliation_time:.2f}ms")
            logger.info(f"  - Matched: {kpi_results['matched_count']}")
            logger.info(f"  - Unmatched Source: {kpi_results['unmatched_source_count']}")
            logger.info(f"  - Unmatched Target: {kpi_results['unmatched_target_count']}")
            logger.info(f"  - RCR: {kpi_results['rcr']}% ({kpi_results['rcr_status']})")
            logger.info(f"  - DQCS: {kpi_results['dqcs']} ({kpi_results['dqcs_status']})")
            logger.info(f"  - REI: {kpi_results['rei']}")

            # Phase 4: Store results in MongoDB (if requested)
            mongodb_doc_id = None
            if request.store_in_mongodb:
                logger.info("=" * 60)
                logger.info("PHASE 4: Storing results in MongoDB")
                logger.info("=" * 60)

                mongodb_doc_id = self._store_results_in_mongodb(
                    execution_id=execution_id,
                    ruleset_id=request.ruleset_id,
                    kpi_results=kpi_results
                )

                logger.info(f"Stored in MongoDB: {mongodb_doc_id}")

            # Phase 5: Cleanup or retain staging tables
            if not request.keep_staging:
                logger.info("=" * 60)
                logger.info("PHASE 5: Cleaning up staging tables")
                logger.info("=" * 60)

                self.staging_manager.drop_staging_table(source_staging_table)
                self.staging_manager.drop_staging_table(target_staging_table)
                logger.info("Staging tables dropped")
            else:
                logger.info(f"Staging tables retained (TTL: {config.LANDING_STAGING_TTL_HOURS}h)")

            # Get staging table info
            source_staging_info = self.staging_manager.get_staging_table_info(source_staging_table)
            target_staging_info = self.staging_manager.get_staging_table_info(target_staging_table)

            # Provide defaults if info retrieval failed
            if source_staging_info is None:
                source_staging_info = StagingTableInfo(
                    table_name=source_staging_table,
                    row_count=source_row_count,
                    created_at=datetime.utcnow(),
                    size_mb=0.0,
                    indexes=[]
                )
            if target_staging_info is None:
                target_staging_info = StagingTableInfo(
                    table_name=target_staging_table,
                    row_count=target_row_count,
                    created_at=datetime.utcnow(),
                    size_mb=0.0,
                    indexes=[]
                )

            total_time = (time.time() - total_start_time) * 1000

            logger.info("=" * 60)
            logger.info(f"EXECUTION COMPLETE: {execution_id}")
            logger.info(f"Total time: {total_time:.2f}ms")
            logger.info("=" * 60)

            # Build response
            response = LandingExecutionResponse(
                success=True,
                execution_id=execution_id,
                matched_count=kpi_results['matched_count'],
                unmatched_source_count=kpi_results['unmatched_source_count'],
                unmatched_target_count=kpi_results['unmatched_target_count'],
                total_source_count=kpi_results['total_source_count'],
                total_target_count=kpi_results['total_target_count'],
                rcr=kpi_results['rcr'],
                rcr_status=kpi_results['rcr_status'],
                dqcs=kpi_results['dqcs'],
                dqcs_status=kpi_results['dqcs_status'],
                rei=kpi_results['rei'],
                source_staging=source_staging_info,
                target_staging=target_staging_info,
                extraction_time_ms=total_extraction_time,
                reconciliation_time_ms=reconciliation_time,
                total_time_ms=total_time,
                mongodb_document_id=mongodb_doc_id,
                staging_retained=request.keep_staging,
                staging_ttl_hours=config.LANDING_STAGING_TTL_HOURS
            )

            return response

        except Exception as e:
            logger.error(f"Landing reconciliation execution failed: {e}", exc_info=True)
            raise

    def _execute_reconciliation_with_kpis(
        self,
        source_staging_table: str,
        target_staging_table: str,
        ruleset: ReconciliationRuleSet
    ) -> Dict[str, Any]:
        """
        Execute reconciliation and calculate KPIs in single query.

        Args:
            source_staging_table: Source staging table name
            target_staging_table: Target staging table name
            ruleset: Reconciliation ruleset

        Returns:
            Dictionary with counts and KPIs
        """
        try:
            # Build comprehensive query
            query = self.query_builder.build_reconciliation_with_kpis_query(
                source_staging_table=source_staging_table,
                target_staging_table=target_staging_table,
                ruleset=ruleset
            )

            logger.debug(f"Executing reconciliation query...")

            # Execute query
            result = self.landing_connector.execute_one(query)

            if not result:
                raise ValueError("Reconciliation query returned no results")

            # Parse results
            kpi_results = {
                'matched_count': result.get('matched_count', 0),
                'unmatched_source_count': result.get('unmatched_source_count', 0),
                'unmatched_target_count': result.get('unmatched_target_count', 0),
                'total_source_count': result.get('total_source_count', 0),
                'total_target_count': result.get('total_target_count', 0),
                'rcr': float(result.get('rcr', 0)),
                'rcr_status': result.get('rcr_status', 'UNKNOWN'),
                'dqcs': float(result.get('dqcs', 0)),
                'dqcs_status': result.get('dqcs_status', 'UNKNOWN'),
                'high_confidence_count': result.get('high_confidence_count', 0),
                'medium_confidence_count': result.get('medium_confidence_count', 0),
                'low_confidence_count': result.get('low_confidence_count', 0),
                'rei': float(result.get('rei', 0))
            }

            return kpi_results

        except Exception as e:
            logger.error(f"Failed to execute reconciliation: {e}")
            raise

    def _store_results_in_mongodb(
        self,
        execution_id: str,
        ruleset_id: str,
        kpi_results: Dict[str, Any]
    ) -> Optional[str]:
        """Store reconciliation results and KPIs in MongoDB."""
        try:
            from kg_builder.services.mongodb_storage import get_mongodb_storage

            mongo_storage = get_mongodb_storage()

            # Prepare document
            document = {
                'execution_id': execution_id,
                'ruleset_id': ruleset_id,
                'execution_type': 'landing_database',
                'timestamp': datetime.utcnow(),
                'kpis': kpi_results,
                'matched_count': kpi_results['matched_count'],
                'total_source_count': kpi_results['total_source_count']
            }

            # Store in MongoDB
            doc_id = mongo_storage.store_reconciliation_result(
                ruleset_id=ruleset_id,
                matched_records=[],  # Don't store all records, just KPIs
                unmatched_source=[],
                unmatched_target=[],
                execution_metadata=document
            )

            return doc_id

        except Exception as e:
            logger.warning(f"Failed to store results in MongoDB: {e}")
            return None

    def cleanup_expired_staging_tables(self) -> int:
        """
        Cleanup expired staging tables.

        Returns:
            Number of tables cleaned up
        """
        return self.staging_manager.cleanup_expired_tables()


# Singleton instance
_landing_executor: Optional[LandingReconciliationExecutor] = None


def get_landing_reconciliation_executor() -> Optional[LandingReconciliationExecutor]:
    """
    Get or create landing reconciliation executor singleton.

    Returns:
        LandingReconciliationExecutor or None if not configured
    """
    global _landing_executor

    if _landing_executor is None:
        try:
            _landing_executor = LandingReconciliationExecutor()
        except ValueError as e:
            logger.warning(f"Landing reconciliation executor not available: {e}")
            return None

    return _landing_executor


def reset_landing_executor():
    """Reset singleton instance (for testing)."""
    global _landing_executor
    _landing_executor = None
