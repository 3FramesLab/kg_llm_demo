"""
KPI Executor Service for creating, calculating, and storing KPIs with file-based storage.

This service handles:
1. KPI creation and configuration
2. KPI calculation based on reconciliation results
3. Evidence data collection and storage
4. File-based storage of KPI results
5. Drill-down capability for evidence records
"""

import logging
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from kg_builder.models import (
    KPICreateRequest,
    KPIConfiguration,
    KPIResult,
    KPIEvidenceRecord,
    KPIType,
    KPIThresholds
)
from kg_builder.services.rule_storage import get_rule_storage

logger = logging.getLogger(__name__)

# KPI storage paths
KPI_CONFIG_DIR = Path("kpi_configs")
KPI_RESULTS_DIR = Path("kpi_results")
KPI_EVIDENCE_DIR = Path("kpi_evidence")


class KPIExecutor:
    """Execute KPI creation, calculation, and storage."""

    def __init__(self):
        """Initialize KPI executor."""
        self.storage = get_rule_storage()
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure KPI storage directories exist."""
        for directory in [KPI_CONFIG_DIR, KPI_RESULTS_DIR, KPI_EVIDENCE_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")

    def create_kpi(self, request: KPICreateRequest) -> Tuple[KPIConfiguration, str]:
        """
        Create a new KPI configuration.

        Args:
            request: KPI creation request

        Returns:
            Tuple of (KPIConfiguration, config_file_path)
        """
        try:
            # Generate unique KPI ID
            kpi_id = f"KPI_{uuid.uuid4().hex[:8].upper()}"

            # Create configuration
            config = KPIConfiguration(
                kpi_id=kpi_id,
                kpi_name=request.kpi_name,
                kpi_description=request.kpi_description,
                kpi_type=request.kpi_type,
                ruleset_id=request.ruleset_id,
                thresholds=request.thresholds,
                enabled=request.enabled
            )

            # Save configuration to file
            config_file = KPI_CONFIG_DIR / f"kpi_config_{kpi_id}.json"
            with open(config_file, 'w') as f:
                json.dump(config.model_dump(mode='json'), f, indent=2, default=str)

            logger.info(f"Created KPI configuration: {kpi_id} ({request.kpi_name})")
            return config, str(config_file)

        except Exception as e:
            logger.error(f"Error creating KPI: {e}")
            raise

    def calculate_kpi(
        self,
        kpi_config: KPIConfiguration,
        matched_count: int,
        unmatched_source_count: int,
        unmatched_target_count: int,
        total_source_count: int,
        inactive_count: int = 0,
        execution_time_ms: float = 0.0
    ) -> KPIResult:
        """
        Calculate KPI value based on reconciliation results.

        Args:
            kpi_config: KPI configuration
            matched_count: Number of matched records
            unmatched_source_count: Number of unmatched source records
            unmatched_target_count: Number of unmatched target records
            total_source_count: Total source records
            inactive_count: Number of inactive records
            execution_time_ms: Execution time in milliseconds

        Returns:
            KPIResult with calculated value and status
        """
        try:
            calculated_value = 0.0
            calculation_details = {}

            # Calculate based on KPI type
            if kpi_config.kpi_type == KPIType.MATCH_RATE:
                if total_source_count > 0:
                    calculated_value = (matched_count / total_source_count) * 100
                calculation_details = {
                    "matched_count": matched_count,
                    "total_source_count": total_source_count,
                    "formula": "(matched_count / total_source_count) * 100"
                }

            elif kpi_config.kpi_type == KPIType.MATCH_PERCENTAGE:
                if total_source_count > 0:
                    calculated_value = (matched_count / total_source_count) * 100
                calculation_details = {
                    "matched_count": matched_count,
                    "total_source_count": total_source_count,
                    "formula": "(matched_count / total_source_count) * 100"
                }

            elif kpi_config.kpi_type == KPIType.UNMATCHED_SOURCE_COUNT:
                calculated_value = float(unmatched_source_count)
                calculation_details = {
                    "unmatched_source_count": unmatched_source_count,
                    "formula": "unmatched_source_count"
                }

            elif kpi_config.kpi_type == KPIType.UNMATCHED_TARGET_COUNT:
                calculated_value = float(unmatched_target_count)
                calculation_details = {
                    "unmatched_target_count": unmatched_target_count,
                    "formula": "unmatched_target_count"
                }

            elif kpi_config.kpi_type == KPIType.INACTIVE_RECORD_COUNT:
                calculated_value = float(inactive_count)
                calculation_details = {
                    "inactive_count": inactive_count,
                    "formula": "inactive_count"
                }

            elif kpi_config.kpi_type == KPIType.DATA_QUALITY_SCORE:
                # Data quality score: (matched + (total - unmatched_target)) / total * 100
                if total_source_count > 0:
                    quality_records = matched_count + (total_source_count - unmatched_source_count)
                    calculated_value = (quality_records / total_source_count) * 100
                calculation_details = {
                    "matched_count": matched_count,
                    "unmatched_source_count": unmatched_source_count,
                    "total_source_count": total_source_count,
                    "formula": "((matched + (total - unmatched_source)) / total) * 100"
                }

            # Determine status based on thresholds
            status = self._determine_status(
                calculated_value,
                kpi_config.thresholds
            )

            # Create result
            result = KPIResult(
                kpi_id=kpi_config.kpi_id,
                kpi_name=kpi_config.kpi_name,
                kpi_type=kpi_config.kpi_type,
                ruleset_id=kpi_config.ruleset_id,
                calculated_value=calculated_value,
                thresholds=kpi_config.thresholds,
                status=status,
                calculation_details=calculation_details
            )

            logger.info(
                f"Calculated KPI {kpi_config.kpi_id}: value={calculated_value:.2f}, status={status}"
            )
            return result

        except Exception as e:
            logger.error(f"Error calculating KPI: {e}")
            raise

    def _determine_status(self, value: float, thresholds: KPIThresholds) -> str:
        """
        Determine KPI status based on value and thresholds.

        Args:
            value: Calculated KPI value
            thresholds: Threshold configuration

        Returns:
            Status: "pass", "warning", or "critical"
        """
        operator = thresholds.comparison_operator.lower()

        if operator == "less_than":
            if value < thresholds.critical_threshold:
                return "critical"
            elif value < thresholds.warning_threshold:
                return "warning"
            else:
                return "pass"

        elif operator == "greater_than":
            if value > thresholds.critical_threshold:
                return "critical"
            elif value > thresholds.warning_threshold:
                return "warning"
            else:
                return "pass"

        elif operator == "equal_to":
            if value == thresholds.critical_threshold:
                return "critical"
            elif value == thresholds.warning_threshold:
                return "warning"
            else:
                return "pass"

        return "pass"

    def store_kpi_result(
        self,
        kpi_result: KPIResult,
        evidence_records: Optional[List[KPIEvidenceRecord]] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Store KPI result and evidence data to files.

        Args:
            kpi_result: KPI result to store
            evidence_records: Optional evidence records for drill-down

        Returns:
            Tuple of (result_file_path, evidence_file_path)
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Store KPI result
            result_file = KPI_RESULTS_DIR / f"kpi_result_{kpi_result.kpi_id}_{timestamp}.json"
            result_data = kpi_result.model_dump(mode='json')
            result_data["evidence_count"] = len(evidence_records) if evidence_records else 0

            with open(result_file, 'w') as f:
                json.dump(result_data, f, indent=2, default=str)

            logger.info(f"Stored KPI result: {result_file}")

            # Store evidence data if provided
            evidence_file = None
            if evidence_records:
                evidence_file = KPI_EVIDENCE_DIR / f"kpi_evidence_{kpi_result.kpi_id}_{timestamp}.json"
                evidence_data = {
                    "kpi_id": kpi_result.kpi_id,
                    "kpi_name": kpi_result.kpi_name,
                    "total_records": len(evidence_records),
                    "records": [r.model_dump(mode='json') for r in evidence_records]
                }

                with open(evidence_file, 'w') as f:
                    json.dump(evidence_data, f, indent=2, default=str)

                logger.info(f"Stored KPI evidence: {evidence_file}")

            return str(result_file), str(evidence_file) if evidence_file else None

        except Exception as e:
            logger.error(f"Error storing KPI result: {e}")
            raise

    def load_kpi_config(self, kpi_id: str) -> Optional[KPIConfiguration]:
        """Load KPI configuration from file."""
        try:
            config_file = KPI_CONFIG_DIR / f"kpi_config_{kpi_id}.json"
            if not config_file.exists():
                logger.warning(f"KPI config not found: {kpi_id}")
                return None

            with open(config_file, 'r') as f:
                data = json.load(f)

            return KPIConfiguration(**data)

        except Exception as e:
            logger.error(f"Error loading KPI config: {e}")
            return None

    def list_kpi_configs(self, ruleset_id: Optional[str] = None) -> List[KPIConfiguration]:
        """List all KPI configurations, optionally filtered by ruleset."""
        try:
            configs = []
            for config_file in KPI_CONFIG_DIR.glob("kpi_config_*.json"):
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    config = KPIConfiguration(**data)

                    if ruleset_id is None or config.ruleset_id == ruleset_id:
                        configs.append(config)

            return configs

        except Exception as e:
            logger.error(f"Error listing KPI configs: {e}")
            return []


# Singleton instance
_kpi_executor: Optional[KPIExecutor] = None


def get_kpi_executor() -> KPIExecutor:
    """Get or create KPI executor singleton."""
    global _kpi_executor

    if _kpi_executor is None:
        _kpi_executor = KPIExecutor()

    return _kpi_executor

