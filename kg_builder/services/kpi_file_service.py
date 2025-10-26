"""
File-based KPI Service for Data Quality and Reconciliation Monitoring.

This service manages KPI definitions and results using JSON files instead of MongoDB.
Provides CRUD operations for KPIs, execution logic, and evidence drill-down.
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import uuid
from filelock import FileLock

from kg_builder.config import get_database_connection

logger = logging.getLogger(__name__)


class KPIFileService:
    """Service for managing KPIs with file-based storage."""

    def __init__(self, data_dir: str = "./data/kpi"):
        """Initialize KPI file service."""
        self.data_dir = Path(data_dir)
        self.definitions_dir = self.data_dir / "definitions"
        self.results_dir = self.data_dir / "results"
        self.evidence_dir = self.data_dir / "evidence"

        # File paths
        self.kpis_file = self.definitions_dir / "kpis.json"
        self.index_file = self.results_dir / "index.json"

        # Ensure directories exist
        self._init_directories()

        logger.info(f"KPI File Service initialized with data_dir: {data_dir}")

    def _init_directories(self):
        """Create necessary directories if they don't exist."""
        self.definitions_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

        # Initialize kpis.json if not exists
        if not self.kpis_file.exists():
            self._write_json_file(self.kpis_file, {
                "kpis": [],
                "metadata": {
                    "version": "1.0",
                    "last_updated": datetime.utcnow().isoformat(),
                    "total_kpis": 0
                }
            })

        # Initialize index.json if not exists
        if not self.index_file.exists():
            self._write_json_file(self.index_file, {
                "results": [],
                "metadata": {
                    "total_results": 0,
                    "last_updated": datetime.utcnow().isoformat()
                }
            })

    def _read_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Read and parse JSON file."""
        try:
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                return {}

            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from {file_path}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return {}

    def _write_json_file(self, file_path: Path, data: Dict[str, Any]) -> bool:
        """Write dict as formatted JSON to file."""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Use file locking for concurrent write safety
            lock_file = file_path.with_suffix('.lock')
            lock = FileLock(str(lock_file), timeout=10)

            with lock:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)

            return True
        except Exception as e:
            logger.error(f"Error writing to {file_path}: {e}")
            return False

    # ========================================================================
    # KPI Definition Management
    # ========================================================================

    def create_kpi_definition(self, kpi_dict: Dict[str, Any]) -> str:
        """Create a new KPI definition."""
        try:
            # Generate KPI ID
            kpi_id = str(uuid.uuid4())

            # Add metadata
            now = datetime.utcnow().isoformat()
            kpi_dict['kpi_id'] = kpi_id
            kpi_dict['created_at'] = now
            kpi_dict['updated_at'] = now

            # Read existing KPIs
            data = self._read_json_file(self.kpis_file)

            # Append new KPI
            data['kpis'].append(kpi_dict)
            data['metadata']['total_kpis'] = len(data['kpis'])
            data['metadata']['last_updated'] = now

            # Write back
            success = self._write_json_file(self.kpis_file, data)

            if success:
                logger.info(f"Created KPI: {kpi_id} - {kpi_dict.get('kpi_name')}")
                return kpi_id
            else:
                raise Exception("Failed to write KPI file")

        except Exception as e:
            logger.error(f"Error creating KPI: {e}")
            raise

    def list_kpi_definitions(self, ruleset_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all KPI definitions, optionally filtered by ruleset."""
        try:
            data = self._read_json_file(self.kpis_file)
            kpis = data.get('kpis', [])

            # Filter by ruleset if provided
            if ruleset_id:
                kpis = [kpi for kpi in kpis if kpi.get('ruleset_id') == ruleset_id]

            logger.info(f"Listed {len(kpis)} KPIs")
            return kpis

        except Exception as e:
            logger.error(f"Error listing KPIs: {e}")
            return []

    def get_kpi_definition(self, kpi_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific KPI definition by ID."""
        try:
            data = self._read_json_file(self.kpis_file)
            kpis = data.get('kpis', [])

            for kpi in kpis:
                if kpi.get('kpi_id') == kpi_id:
                    return kpi

            logger.warning(f"KPI not found: {kpi_id}")
            return None

        except Exception as e:
            logger.error(f"Error getting KPI {kpi_id}: {e}")
            return None

    def update_kpi_definition(self, kpi_id: str, updates: Dict[str, Any]) -> bool:
        """Update a KPI definition."""
        try:
            data = self._read_json_file(self.kpis_file)
            kpis = data.get('kpis', [])

            # Find and update KPI
            found = False
            for i, kpi in enumerate(kpis):
                if kpi.get('kpi_id') == kpi_id:
                    # Update fields
                    kpis[i].update(updates)
                    kpis[i]['updated_at'] = datetime.utcnow().isoformat()
                    found = True
                    break

            if not found:
                logger.warning(f"KPI not found for update: {kpi_id}")
                return False

            # Update metadata
            data['metadata']['last_updated'] = datetime.utcnow().isoformat()

            # Write back
            success = self._write_json_file(self.kpis_file, data)

            if success:
                logger.info(f"Updated KPI: {kpi_id}")

            return success

        except Exception as e:
            logger.error(f"Error updating KPI {kpi_id}: {e}")
            return False

    def delete_kpi_definition(self, kpi_id: str) -> bool:
        """Delete a KPI definition."""
        try:
            data = self._read_json_file(self.kpis_file)
            kpis = data.get('kpis', [])

            # Remove KPI
            original_count = len(kpis)
            kpis = [kpi for kpi in kpis if kpi.get('kpi_id') != kpi_id]

            if len(kpis) == original_count:
                logger.warning(f"KPI not found for deletion: {kpi_id}")
                return False

            # Update data
            data['kpis'] = kpis
            data['metadata']['total_kpis'] = len(kpis)
            data['metadata']['last_updated'] = datetime.utcnow().isoformat()

            # Write back
            success = self._write_json_file(self.kpis_file, data)

            if success:
                logger.info(f"Deleted KPI: {kpi_id}")

            return success

        except Exception as e:
            logger.error(f"Error deleting KPI {kpi_id}: {e}")
            return False

    # ========================================================================
    # KPI Execution & Results
    # ========================================================================

    def execute_kpi(self, kpi_id: str, ruleset_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute a KPI and save the result."""
        try:
            # Get KPI definition
            kpi = self.get_kpi_definition(kpi_id)
            if not kpi:
                raise Exception(f"KPI not found: {kpi_id}")

            # Use provided ruleset_id or default from KPI
            target_ruleset_id = ruleset_id or kpi.get('ruleset_id')

            # Execute query based on KPI type
            kpi_type = kpi.get('kpi_type')
            query_result = self._execute_kpi_query(kpi_type, target_ruleset_id)

            # Calculate value
            calculated_value = self._calculate_kpi_value(kpi_type, query_result)

            # Determine status
            thresholds = kpi.get('thresholds', {})
            status = self._determine_status(calculated_value, thresholds)

            # Create result document
            result = {
                "result_id": str(uuid.uuid4()),
                "kpi_id": kpi_id,
                "kpi_name": kpi.get('kpi_name'),
                "kpi_type": kpi_type,
                "ruleset_id": target_ruleset_id,
                "execution_timestamp": datetime.utcnow().isoformat(),
                "calculated_value": calculated_value,
                "status": status,
                "metrics": query_result,
                "thresholds": thresholds,
                "execution_details": {
                    "kpi_type": kpi_type,
                    "data_source": "reconciliation_results"
                }
            }

            # Save result
            result_id = self.save_kpi_result(result)
            result['result_id'] = result_id

            logger.info(f"Executed KPI {kpi_id}: value={calculated_value}, status={status}")

            return result

        except Exception as e:
            logger.error(f"Error executing KPI {kpi_id}: {e}")
            raise

    def save_kpi_result(self, result_dict: Dict[str, Any]) -> str:
        """Save a KPI result to file and update index."""
        try:
            result_id = result_dict.get('result_id') or str(uuid.uuid4())
            kpi_id = result_dict.get('kpi_id')
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

            # Create filename
            filename = f"{kpi_id}_{timestamp}.json"
            result_file = self.results_dir / filename

            # Write result file
            self._write_json_file(result_file, result_dict)

            # Update index
            index_data = self._read_json_file(self.index_file)

            # Add to index
            index_entry = {
                "result_id": result_id,
                "kpi_id": kpi_id,
                "kpi_name": result_dict.get('kpi_name'),
                "execution_timestamp": result_dict.get('execution_timestamp'),
                "calculated_value": result_dict.get('calculated_value'),
                "status": result_dict.get('status'),
                "file_path": filename
            }

            index_data['results'].insert(0, index_entry)  # Insert at beginning (newest first)
            index_data['metadata']['total_results'] = len(index_data['results'])
            index_data['metadata']['last_updated'] = datetime.utcnow().isoformat()

            self._write_json_file(self.index_file, index_data)

            logger.info(f"Saved KPI result: {result_id}")

            return result_id

        except Exception as e:
            logger.error(f"Error saving KPI result: {e}")
            raise

    def list_kpi_results(self, kpi_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List KPI results, optionally filtered by KPI ID."""
        try:
            index_data = self._read_json_file(self.index_file)
            results = index_data.get('results', [])

            # Filter by KPI ID if provided
            if kpi_id:
                results = [r for r in results if r.get('kpi_id') == kpi_id]

            # Apply limit
            results = results[:limit]

            logger.info(f"Listed {len(results)} KPI results")

            return results

        except Exception as e:
            logger.error(f"Error listing KPI results: {e}")
            return []

    def get_kpi_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific KPI result by ID."""
        try:
            # Find in index
            index_data = self._read_json_file(self.index_file)
            results = index_data.get('results', [])

            file_path = None
            for result in results:
                if result.get('result_id') == result_id:
                    file_path = result.get('file_path')
                    break

            if not file_path:
                logger.warning(f"Result not found in index: {result_id}")
                return None

            # Read full result file
            result_file = self.results_dir / file_path
            full_result = self._read_json_file(result_file)

            return full_result

        except Exception as e:
            logger.error(f"Error getting KPI result {result_id}: {e}")
            return None

    def delete_kpi_result(self, result_id: str) -> bool:
        """Delete a KPI result."""
        try:
            # Find in index
            index_data = self._read_json_file(self.index_file)
            results = index_data.get('results', [])

            file_path = None
            for result in results:
                if result.get('result_id') == result_id:
                    file_path = result.get('file_path')
                    break

            if not file_path:
                logger.warning(f"Result not found for deletion: {result_id}")
                return False

            # Delete result file
            result_file = self.results_dir / file_path
            if result_file.exists():
                result_file.unlink()

            # Remove from index
            results = [r for r in results if r.get('result_id') != result_id]
            index_data['results'] = results
            index_data['metadata']['total_results'] = len(results)
            index_data['metadata']['last_updated'] = datetime.utcnow().isoformat()

            self._write_json_file(self.index_file, index_data)

            logger.info(f"Deleted KPI result: {result_id}")

            return True

        except Exception as e:
            logger.error(f"Error deleting KPI result {result_id}: {e}")
            return False

    # ========================================================================
    # Evidence/Drill-Down
    # ========================================================================

    def get_evidence_data(
        self,
        kpi_id: str,
        match_status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get evidence data for KPI drill-down."""
        try:
            # Get KPI definition
            kpi = self.get_kpi_definition(kpi_id)
            if not kpi:
                raise Exception(f"KPI not found: {kpi_id}")

            ruleset_id = kpi.get('ruleset_id')
            kpi_type = kpi.get('kpi_type')

            # Build query based on KPI type
            evidence_records = self._query_evidence_data(
                kpi_type,
                ruleset_id,
                match_status,
                limit,
                offset
            )

            total_count = len(evidence_records)

            logger.info(f"Retrieved {total_count} evidence records for KPI {kpi_id}")

            return {
                "success": True,
                "evidence_records": evidence_records,
                "total_count": total_count,
                "limit": limit,
                "offset": offset
            }

        except Exception as e:
            logger.error(f"Error getting evidence data for KPI {kpi_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "evidence_records": [],
                "total_count": 0
            }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _execute_kpi_query(self, kpi_type: str, ruleset_id: str) -> Dict[str, Any]:
        """Execute KPI calculation query based on type."""
        try:
            conn = get_database_connection()
            cursor = conn.cursor()

            if kpi_type == "match_rate" or kpi_type == "match_percentage":
                query = """
                    SELECT
                        COUNT(CASE WHEN match_status = 'matched' THEN 1 END) as matched_count,
                        COUNT(*) as total_count
                    FROM reconciliation_results
                    WHERE ruleset_id = ?
                """
                cursor.execute(query, (ruleset_id,))
                row = cursor.fetchone()

                return {
                    "matched_count": row[0] if row else 0,
                    "total_count": row[1] if row else 0
                }

            elif kpi_type == "unmatched_source_count":
                query = """
                    SELECT COUNT(*) as unmatched_count
                    FROM reconciliation_results
                    WHERE ruleset_id = ? AND match_status = 'unmatched_source'
                """
                cursor.execute(query, (ruleset_id,))
                row = cursor.fetchone()

                return {"unmatched_count": row[0] if row else 0}

            elif kpi_type == "unmatched_target_count":
                query = """
                    SELECT COUNT(*) as unmatched_count
                    FROM reconciliation_results
                    WHERE ruleset_id = ? AND match_status = 'unmatched_target'
                """
                cursor.execute(query, (ruleset_id,))
                row = cursor.fetchone()

                return {"unmatched_count": row[0] if row else 0}

            elif kpi_type == "inactive_record_count":
                query = """
                    SELECT COUNT(*) as inactive_count
                    FROM reconciliation_results
                    WHERE ruleset_id = ? AND match_status = 'inactive'
                """
                cursor.execute(query, (ruleset_id,))
                row = cursor.fetchone()

                return {"inactive_count": row[0] if row else 0}

            elif kpi_type == "data_quality_score":
                query = """
                    SELECT
                        AVG(CAST(match_confidence AS REAL)) as avg_confidence,
                        COUNT(*) as total_records
                    FROM reconciliation_results
                    WHERE ruleset_id = ? AND match_status = 'matched'
                """
                cursor.execute(query, (ruleset_id,))
                row = cursor.fetchone()

                return {
                    "avg_confidence": row[0] if row and row[0] else 0.0,
                    "total_records": row[1] if row else 0
                }

            else:
                logger.warning(f"Unknown KPI type: {kpi_type}")
                return {}

        except Exception as e:
            logger.error(f"Error executing KPI query: {e}")
            return {}
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def _calculate_kpi_value(self, kpi_type: str, query_result: Dict[str, Any]) -> float:
        """Calculate KPI value from query results."""
        if kpi_type == "match_rate" or kpi_type == "match_percentage":
            matched = query_result.get('matched_count', 0)
            total = query_result.get('total_count', 0)
            return round((matched / total * 100) if total > 0 else 0.0, 2)

        elif kpi_type == "unmatched_source_count":
            return float(query_result.get('unmatched_count', 0))

        elif kpi_type == "unmatched_target_count":
            return float(query_result.get('unmatched_count', 0))

        elif kpi_type == "inactive_record_count":
            return float(query_result.get('inactive_count', 0))

        elif kpi_type == "data_quality_score":
            return round(query_result.get('avg_confidence', 0.0) * 100, 2)

        else:
            return 0.0

    def _determine_status(self, value: float, thresholds: Dict[str, Any]) -> str:
        """Determine KPI status based on thresholds."""
        warning = thresholds.get('warning_threshold', 80)
        critical = thresholds.get('critical_threshold', 70)
        operator = thresholds.get('comparison_operator', 'less_than')

        if operator == "less_than":
            if value < critical:
                return "critical"
            elif value < warning:
                return "warning"
            else:
                return "pass"

        elif operator == "greater_than":
            if value > critical:
                return "critical"
            elif value > warning:
                return "warning"
            else:
                return "pass"

        else:  # equal_to
            if value == critical:
                return "critical"
            elif value == warning:
                return "warning"
            else:
                return "pass"

    def _query_evidence_data(
        self,
        kpi_type: str,
        ruleset_id: str,
        match_status: Optional[str],
        limit: int,
        offset: int
    ) -> List[Dict[str, Any]]:
        """Query evidence data for drill-down."""
        try:
            conn = get_database_connection()
            cursor = conn.cursor()

            # Build base query
            query = """
                SELECT
                    id as record_id,
                    match_status,
                    rule_name,
                    source_data,
                    target_data,
                    match_confidence
                FROM reconciliation_results
                WHERE ruleset_id = ?
            """
            params = [ruleset_id]

            # Filter by KPI type - only show relevant records
            if kpi_type == "match_rate" or kpi_type == "match_percentage":
                # Show all records for match rate
                pass
            elif kpi_type == "unmatched_source_count":
                query += " AND match_status = 'unmatched_source'"
            elif kpi_type == "unmatched_target_count":
                query += " AND match_status = 'unmatched_target'"
            elif kpi_type == "inactive_record_count":
                query += " AND match_status = 'inactive'"
            elif kpi_type == "data_quality_score":
                query += " AND match_status = 'matched'"

            # Add match_status filter if provided (overrides KPI type filter)
            if match_status:
                query += " AND match_status = ?"
                params.append(match_status)

            # Add pagination
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            logger.info(f"Executing evidence query for KPI type {kpi_type}, ruleset {ruleset_id}")
            logger.debug(f"Evidence query: {query}, params: {params}")

            cursor.execute(query, params)
            rows = cursor.fetchall()

            logger.info(f"Retrieved {len(rows)} evidence records")

            # Convert to list of dicts
            evidence_records = []
            for row in rows:
                evidence_records.append({
                    "record_id": row[0],
                    "match_status": row[1],
                    "rule_name": row[2],
                    "record_data": {
                        "source_data": row[3],
                        "target_data": row[4],
                        "match_confidence": row[5]
                    }
                })

            return evidence_records

        except Exception as e:
            logger.error(f"Error querying evidence data: {e}", exc_info=True)
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
