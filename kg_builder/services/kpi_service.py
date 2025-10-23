"""
KPI Service for Data Quality and Reconciliation Monitoring.

This service calculates and stores three key performance indicators:
1. Reconciliation Coverage Rate (RCR) - % of matched records
2. Data Quality Confidence Score (DQCS) - weighted confidence average
3. Reconciliation Efficiency Index (REI) - efficiency score
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from statistics import mean

try:
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

from kg_builder.config import (
    get_mongodb_connection_string,
    MONGODB_DATABASE
)

logger = logging.getLogger(__name__)


class KPIService:
    """Service for calculating and storing KPIs."""

    def __init__(self):
        """Initialize KPI service with MongoDB connection."""
        if not PYMONGO_AVAILABLE:
            raise RuntimeError("pymongo is not installed")

        self.client: Optional[MongoClient] = None
        self.db = None
        self._connect()

    def _connect(self):
        """Establish connection to MongoDB."""
        try:
            connection_string = get_mongodb_connection_string()
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[MONGODB_DATABASE]
            logger.info("KPI Service connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def _ensure_indexes(self):
        """Create indexes for KPI collections."""
        try:
            # RCR Collection
            rcr_col = self.db['kpi_reconciliation_coverage']
            rcr_col.create_index([('ruleset_id', 1), ('timestamp', -1)])
            rcr_col.create_index([('metrics.coverage_rate', 1)])

            # DQCS Collection
            dqcs_col = self.db['kpi_data_quality_confidence']
            dqcs_col.create_index([('ruleset_id', 1), ('timestamp', -1)])
            dqcs_col.create_index([('metrics.overall_confidence_score', 1)])

            # REI Collection
            rei_col = self.db['kpi_reconciliation_efficiency']
            rei_col.create_index([('ruleset_id', 1), ('timestamp', -1)])
            rei_col.create_index([('metrics.efficiency_index', 1)])

            # KG Metadata Collection
            kg_col = self.db['kpi_knowledge_graph_metadata']
            kg_col.create_index([('kg_name', 1)])
            kg_col.create_index([('created_at', -1)])

            # Ruleset Relationships Collection
            rel_col = self.db['kpi_ruleset_relationships']
            rel_col.create_index([('ruleset_id', 1)])
            rel_col.create_index([('source_kg', 1)])

            logger.info("KPI indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")

    def calculate_rcr(
        self,
        matched_count: int,
        total_source_count: int,
        ruleset_id: str,
        ruleset_name: str,
        execution_id: str,
        source_kg: str,
        source_schemas: List[str],
        breakdown_by_rule: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Calculate Reconciliation Coverage Rate (RCR).

        RCR = (Matched Records / Total Source Records) × 100
        """
        if total_source_count == 0:
            coverage_rate = 0.0
        else:
            coverage_rate = (matched_count / total_source_count) * 100

        # Determine status
        if coverage_rate >= 90:
            status = "HEALTHY"
        elif coverage_rate >= 80:
            status = "WARNING"
        else:
            status = "CRITICAL"

        kpi_doc = {
            "kpi_type": "RECONCILIATION_COVERAGE_RATE",
            "ruleset_id": ruleset_id,
            "ruleset_name": ruleset_name,
            "execution_id": execution_id,
            "timestamp": datetime.utcnow(),
            "period": "execution",
            "metrics": {
                "matched_records": matched_count,
                "unmatched_source": total_source_count - matched_count,
                "total_source_records": total_source_count,
                "coverage_rate": round(coverage_rate, 2),
                "coverage_percentage": round(coverage_rate, 2)
            },
            "breakdown_by_rule": breakdown_by_rule or [],
            "thresholds": {
                "warning_level": 90,
                "critical_level": 80,
                "status": status
            },
            "data_lineage": {
                "source_kg": source_kg,
                "source_schemas": source_schemas,
                "generated_from_kg": source_kg
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        return kpi_doc

    def calculate_dqcs(
        self,
        matched_records: List[Dict[str, Any]],
        ruleset_id: str,
        ruleset_name: str,
        execution_id: str,
        source_kg: str,
        rule_quality_breakdown: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Calculate Data Quality Confidence Score (DQCS).

        DQCS = Σ(matched_count × confidence_score) / Σ matched_count
        """
        if not matched_records:
            overall_score = 0.0
            high_confidence = 0
            medium_confidence = 0
            low_confidence = 0
        else:
            # Extract confidence scores
            confidence_scores = [
                record.get('match_confidence', 0.0)
                for record in matched_records
            ]

            overall_score = mean(confidence_scores) if confidence_scores else 0.0

            # Count by confidence level
            high_confidence = sum(1 for s in confidence_scores if s >= 0.9)
            medium_confidence = sum(1 for s in confidence_scores if 0.8 <= s < 0.9)
            low_confidence = sum(1 for s in confidence_scores if s < 0.8)

        # Determine status
        if overall_score >= 0.8:
            status = "GOOD"
        elif overall_score >= 0.7:
            status = "ACCEPTABLE"
        else:
            status = "POOR"

        kpi_doc = {
            "kpi_type": "DATA_QUALITY_CONFIDENCE_SCORE",
            "ruleset_id": ruleset_id,
            "ruleset_name": ruleset_name,
            "execution_id": execution_id,
            "timestamp": datetime.utcnow(),
            "period": "execution",
            "metrics": {
                "overall_confidence_score": round(overall_score, 3),
                "confidence_percentage": round(overall_score * 100, 2),
                "total_matched_records": len(matched_records),
                "high_confidence_matches": high_confidence,
                "medium_confidence_matches": medium_confidence,
                "low_confidence_matches": low_confidence
            },
            "confidence_distribution": {
                "0.9_to_1.0": high_confidence,
                "0.8_to_0.9": medium_confidence,
                "below_0.8": low_confidence
            },
            "rule_quality_breakdown": rule_quality_breakdown or [],
            "thresholds": {
                "excellent": 0.9,
                "good": 0.8,
                "acceptable": 0.7,
                "current_status": status
            },
            "data_lineage": {
                "source_kg": source_kg,
                "relationships_used": len(rule_quality_breakdown or [])
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        return kpi_doc

    def calculate_rei(
        self,
        matched_count: int,
        total_source_count: int,
        active_rules: int,
        total_rules: int,
        execution_time_ms: float,
        ruleset_id: str,
        ruleset_name: str,
        execution_id: str,
        source_kg: str,
        resource_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate Reconciliation Efficiency Index (REI).

        REI = (Match Success Rate × Rule Utilization × Speed Factor) / 100
        """
        # Calculate components
        match_success_rate = (matched_count / total_source_count * 100) if total_source_count > 0 else 0
        rule_utilization = (active_rules / total_rules * 100) if total_rules > 0 else 0

        # Speed factor: target is 1000ms per 1000 records
        target_time_ms = (total_source_count / 1000) * 1000
        speed_factor = (target_time_ms / execution_time_ms * 100) if execution_time_ms > 0 else 0

        # Calculate REI
        efficiency_index = (match_success_rate * rule_utilization * speed_factor) / 10000

        # Determine status
        if efficiency_index >= 50:
            status = "EXCELLENT"
        elif efficiency_index >= 40:
            status = "GOOD"
        elif efficiency_index >= 30:
            status = "ACCEPTABLE"
        elif efficiency_index >= 20:
            status = "WARNING"
        else:
            status = "CRITICAL"

        records_per_second = (total_source_count / execution_time_ms * 1000) if execution_time_ms > 0 else 0

        kpi_doc = {
            "kpi_type": "RECONCILIATION_EFFICIENCY_INDEX",
            "ruleset_id": ruleset_id,
            "ruleset_name": ruleset_name,
            "execution_id": execution_id,
            "timestamp": datetime.utcnow(),
            "period": "execution",
            "metrics": {
                "efficiency_index": round(efficiency_index, 2),
                "match_success_rate": round(match_success_rate, 2),
                "rule_utilization": round(rule_utilization, 2),
                "speed_factor": round(speed_factor, 2)
            },
            "performance_details": {
                "total_records_processed": total_source_count,
                "execution_time_ms": execution_time_ms,
                "records_per_second": round(records_per_second, 2),
                "target_time_ms": target_time_ms,
                "actual_time_ms": execution_time_ms,
                "time_efficiency": round(speed_factor, 2)
            },
            "rule_efficiency": {
                "total_rules": total_rules,
                "active_rules": active_rules,
                "rules_with_matches": active_rules
            },
            "resource_utilization": resource_metrics or {},
            "efficiency_assessment": {
                "status": status,
                "bottleneck": "database_queries" if speed_factor < 50 else "none",
                "optimization_potential": "HIGH" if efficiency_index < 40 else "MEDIUM"
            },
            "thresholds": {
                "excellent": 50,
                "good": 40,
                "acceptable": 30,
                "poor": 20,
                "current_status": status
            },
            "data_lineage": {
                "source_kg": source_kg,
                "ruleset_version": 1,
                "schema_count": 2
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        return kpi_doc

    def store_kpi(self, kpi_type: str, kpi_doc: Dict[str, Any]) -> Optional[str]:
        """Store KPI document in MongoDB."""
        try:
            collection_name = self._get_collection_name(kpi_type)
            collection = self.db[collection_name]
            result = collection.insert_one(kpi_doc)
            logger.info(f"Stored {kpi_type} with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error storing KPI: {e}")
            return None

    def _get_collection_name(self, kpi_type: str) -> str:
        """Get MongoDB collection name for KPI type."""
        mapping = {
            "RECONCILIATION_COVERAGE_RATE": "kpi_reconciliation_coverage",
            "DATA_QUALITY_CONFIDENCE_SCORE": "kpi_data_quality_confidence",
            "RECONCILIATION_EFFICIENCY_INDEX": "kpi_reconciliation_efficiency"
        }
        return mapping.get(kpi_type, "kpi_metrics")

    def get_latest_kpi(self, kpi_type: str, ruleset_id: str) -> Optional[Dict[str, Any]]:
        """Get latest KPI for a ruleset."""
        try:
            collection_name = self._get_collection_name(kpi_type)
            collection = self.db[collection_name]
            result = collection.find_one(
                {"kpi_type": kpi_type, "ruleset_id": ruleset_id},
                sort=[("timestamp", -1)]
            )
            return result
        except Exception as e:
            logger.error(f"Error retrieving KPI: {e}")
            return None

    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("KPI Service connection closed")

