"""
Rule validation service for testing reconciliation rules against actual databases.

Uses JayDeBeApi to connect to databases via JDBC and validate rules with real data.
"""

import logging
import jaydebeapi
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from kg_builder.models import (
    ReconciliationRule,
    ValidationResult,
    ReconciliationMatchType,
    DatabaseConnectionInfo
)
from kg_builder.config import JDBC_DRIVERS_PATH

logger = logging.getLogger(__name__)


class RuleValidator:
    """Validate reconciliation rules against actual database data."""

    def __init__(self):
        """Initialize the rule validator."""
        self.jdbc_drivers_path = Path(JDBC_DRIVERS_PATH) if JDBC_DRIVERS_PATH else None

    def validate_rule_with_data(
        self,
        rule: ReconciliationRule,
        source_db_config: DatabaseConnectionInfo,
        target_db_config: DatabaseConnectionInfo,
        sample_size: int = 100
    ) -> ValidationResult:
        """
        Validate a reconciliation rule against actual database data.

        Args:
            rule: The reconciliation rule to validate
            source_db_config: Source database connection info
            target_db_config: Target database connection info
            sample_size: Number of records to sample for testing

        Returns:
            ValidationResult with validation details
        """
        logger.info(f"Validating rule '{rule.rule_id}' with sample size {sample_size}")

        issues = []
        warnings = []
        exists = True
        types_compatible = True
        sample_match_rate = None
        cardinality = None
        estimated_performance_ms = None

        source_conn = None
        target_conn = None

        try:
            # Step 1: Connect to source database
            logger.debug(f"Connecting to source database: {source_db_config.db_type}")
            source_conn = self._connect_to_database(source_db_config)

            if not source_conn:
                issues.append("Failed to connect to source database")
                exists = False
            else:
                # Step 2: Verify source table and columns exist
                source_exists, source_issues = self._verify_table_columns(
                    source_conn,
                    rule.source_schema,
                    rule.source_table,
                    rule.source_columns,
                    "source"
                )
                if not source_exists:
                    exists = False
                    issues.extend(source_issues)

            # Step 3: Connect to target database
            logger.debug(f"Connecting to target database: {target_db_config.db_type}")
            target_conn = self._connect_to_database(target_db_config)

            if not target_conn:
                issues.append("Failed to connect to target database")
                exists = False
            else:
                # Step 4: Verify target table and columns exist
                target_exists, target_issues = self._verify_table_columns(
                    target_conn,
                    rule.target_schema,
                    rule.target_table,
                    rule.target_columns,
                    "target"
                )
                if not target_exists:
                    exists = False
                    issues.extend(target_issues)

            # If tables/columns exist, proceed with further validation
            if exists and source_conn and target_conn:
                # Step 5: Check data type compatibility
                types_compatible, type_issues = self._check_type_compatibility(
                    source_conn,
                    target_conn,
                    rule
                )
                if not types_compatible:
                    issues.extend(type_issues)

                # Step 6: Test on sample data
                sample_match_rate, match_warnings = self._test_sample_data(
                    source_conn,
                    target_conn,
                    rule,
                    sample_size
                )
                warnings.extend(match_warnings)

                # Step 7: Determine cardinality
                cardinality = self._detect_cardinality(
                    source_conn,
                    target_conn,
                    rule,
                    sample_size
                )

                # Step 8: Estimate performance
                estimated_performance_ms = self._estimate_performance(
                    source_conn,
                    target_conn,
                    rule
                )

        except Exception as e:
            logger.error(f"Error during rule validation: {e}")
            issues.append(f"Validation error: {str(e)}")
            exists = False

        finally:
            # Clean up connections
            if source_conn:
                try:
                    source_conn.close()
                    logger.debug("Source connection closed")
                except Exception as e:
                    logger.error(f"Error closing source connection: {e}")

            if target_conn:
                try:
                    target_conn.close()
                    logger.debug("Target connection closed")
                except Exception as e:
                    logger.error(f"Error closing target connection: {e}")

        # Determine if rule is valid
        valid = exists and types_compatible and len(issues) == 0

        # Add warnings for low match rates
        if sample_match_rate is not None and sample_match_rate < 0.5:
            warnings.append(f"Low match rate detected: {sample_match_rate:.2%}")

        result = ValidationResult(
            rule_id=rule.rule_id,
            valid=valid,
            exists=exists,
            types_compatible=types_compatible,
            sample_match_rate=sample_match_rate,
            cardinality=cardinality,
            estimated_performance_ms=estimated_performance_ms,
            issues=issues,
            warnings=warnings
        )

        logger.info(f"Validation complete for rule '{rule.rule_id}': valid={valid}")
        return result

    def _connect_to_database(
        self,
        db_config: DatabaseConnectionInfo
    ) -> Optional[Any]:
        """
        Connect to a database using JayDeBeApi.

        Args:
            db_config: Database connection configuration

        Returns:
            Database connection or None if failed
        """
        try:
            # Build JDBC URL based on database type
            jdbc_url = self._build_jdbc_url(db_config)

            # Get JDBC driver class
            driver_class = self._get_driver_class(db_config.db_type)

            # Get driver JAR path
            driver_jar = self._get_driver_jar(db_config.db_type)

            # Connect using JayDeBeApi
            logger.debug(f"Connecting to {jdbc_url} with driver {driver_class}")

            conn = jaydebeapi.connect(
                driver_class,
                jdbc_url,
                [db_config.username, db_config.password],
                driver_jar
            )

            logger.debug("Database connection established")
            return conn

        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return None

    def _build_jdbc_url(self, db_config: DatabaseConnectionInfo) -> str:
        """Build JDBC URL based on database type."""
        db_type = db_config.db_type.lower()

        if db_type == "oracle":
            # Oracle: jdbc:oracle:thin:@host:port:sid or @host:port/service
            if db_config.service_name:
                return f"jdbc:oracle:thin:@{db_config.host}:{db_config.port}/{db_config.service_name}"
            else:
                return f"jdbc:oracle:thin:@{db_config.host}:{db_config.port}:{db_config.database}"

        elif db_type == "sqlserver" or db_type == "mssql":
            # SQL Server: jdbc:sqlserver://host:port;databaseName=dbname
            return f"jdbc:sqlserver://{db_config.host}:{db_config.port};databaseName={db_config.database};encrypt=true;trustServerCertificate=true"

        elif db_type == "postgresql" or db_type == "postgres":
            # PostgreSQL: jdbc:postgresql://host:port/database
            return f"jdbc:postgresql://{db_config.host}:{db_config.port}/{db_config.database}"

        elif db_type == "mysql":
            # MySQL: jdbc:mysql://host:port/database
            return f"jdbc:mysql://{db_config.host}:{db_config.port}/{db_config.database}"

        else:
            raise ValueError(f"Unsupported database type: {db_config.db_type}")

    def _get_driver_class(self, db_type: str) -> str:
        """Get JDBC driver class name for database type."""
        db_type = db_type.lower()

        drivers = {
            "oracle": "oracle.jdbc.OracleDriver",
            "sqlserver": "com.microsoft.sqlserver.jdbc.SQLServerDriver",
            "mssql": "com.microsoft.sqlserver.jdbc.SQLServerDriver",
            "postgresql": "org.postgresql.Driver",
            "postgres": "org.postgresql.Driver",
            "mysql": "com.mysql.cj.jdbc.Driver"
        }

        if db_type not in drivers:
            raise ValueError(f"Unknown database type: {db_type}")

        return drivers[db_type]

    def _get_driver_jar(self, db_type: str) -> str:
        """Get path to JDBC driver JAR file."""
        if not self.jdbc_drivers_path or not self.jdbc_drivers_path.exists():
            raise ValueError(f"JDBC drivers path not configured or doesn't exist: {self.jdbc_drivers_path}")

        db_type = db_type.lower()

        # Map database types to JAR file patterns
        jar_patterns = {
            "oracle": "ojdbc*.jar",
            "sqlserver": "mssql-jdbc*.jar",
            "mssql": "mssql-jdbc*.jar",
            "postgresql": "postgresql*.jar",
            "postgres": "postgresql*.jar",
            "mysql": "mysql-connector*.jar"
        }

        if db_type not in jar_patterns:
            raise ValueError(f"Unknown database type: {db_type}")

        # Find the JAR file
        pattern = jar_patterns[db_type]
        jar_files = list(self.jdbc_drivers_path.glob(pattern))

        if not jar_files:
            raise ValueError(f"JDBC driver not found for {db_type}. Expected pattern: {pattern} in {self.jdbc_drivers_path}")

        # Use the first matching JAR
        return str(jar_files[0])

    def _verify_table_columns(
        self,
        conn: Any,
        schema: str,
        table: str,
        columns: List[str],
        label: str
    ) -> Tuple[bool, List[str]]:
        """
        Verify that table and columns exist in the database.

        Args:
            conn: Database connection
            schema: Schema name
            table: Table name
            columns: List of column names
            label: Label for error messages (source/target)

        Returns:
            Tuple of (exists, issues)
        """
        issues = []
        cursor = None

        try:
            cursor = conn.cursor()

            # Build a simple query to check table existence
            # Use LIMIT/ROWNUM to make it fast
            test_query = f"SELECT * FROM {schema}.{table} WHERE 1=0"

            try:
                cursor.execute(test_query)
                logger.debug(f"{label.capitalize()} table exists: {schema}.{table}")
            except Exception as e:
                issues.append(f"{label.capitalize()} table not found: {schema}.{table} - {str(e)}")
                return False, issues

            # Get column metadata
            cursor.execute(f"SELECT * FROM {schema}.{table} WHERE ROWNUM <= 1")
            db_columns = [desc[0].upper() for desc in cursor.description]

            # Check if requested columns exist
            for col in columns:
                if col.upper() not in db_columns:
                    issues.append(f"{label.capitalize()} column not found: {col} in {schema}.{table}")

            if issues:
                return False, issues

            return True, []

        except Exception as e:
            logger.error(f"Error verifying {label} table/columns: {e}")
            issues.append(f"Error checking {label} table: {str(e)}")
            return False, issues

        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass

    def _check_type_compatibility(
        self,
        source_conn: Any,
        target_conn: Any,
        rule: ReconciliationRule
    ) -> Tuple[bool, List[str]]:
        """
        Check if source and target column data types are compatible.

        Args:
            source_conn: Source database connection
            target_conn: Target database connection
            rule: Reconciliation rule

        Returns:
            Tuple of (compatible, issues)
        """
        issues = []

        try:
            # Get source column types
            source_cursor = source_conn.cursor()
            source_cursor.execute(
                f"SELECT * FROM {rule.source_schema}.{rule.source_table} WHERE ROWNUM <= 1"
            )
            source_types = {desc[0].upper(): desc[1] for desc in source_cursor.description}
            source_cursor.close()

            # Get target column types
            target_cursor = target_conn.cursor()
            target_cursor.execute(
                f"SELECT * FROM {rule.target_schema}.{rule.target_table} WHERE ROWNUM <= 1"
            )
            target_types = {desc[0].upper(): desc[1] for desc in target_cursor.description}
            target_cursor.close()

            # Compare types for each column pair
            for src_col, tgt_col in zip(rule.source_columns, rule.target_columns):
                src_type = source_types.get(src_col.upper())
                tgt_type = target_types.get(tgt_col.upper())

                if src_type is None:
                    issues.append(f"Source column type not found: {src_col}")
                elif tgt_type is None:
                    issues.append(f"Target column type not found: {tgt_col}")
                elif not self._are_types_compatible(src_type, tgt_type):
                    issues.append(
                        f"Type mismatch: {src_col} (type {src_type}) vs {tgt_col} (type {tgt_type})"
                    )

            return len(issues) == 0, issues

        except Exception as e:
            logger.error(f"Error checking type compatibility: {e}")
            issues.append(f"Type compatibility check failed: {str(e)}")
            return False, issues

    def _are_types_compatible(self, type1: Any, type2: Any) -> bool:
        """Check if two JDBC types are compatible for matching."""
        # Convert JDBC type codes to type names
        import jaydebeapi
        import java.sql.Types as Types

        # Numeric types are compatible with each other
        numeric_types = {
            Types.INTEGER, Types.BIGINT, Types.SMALLINT, Types.TINYINT,
            Types.DECIMAL, Types.NUMERIC, Types.FLOAT, Types.DOUBLE, Types.REAL
        }

        # String types are compatible with each other
        string_types = {
            Types.CHAR, Types.VARCHAR, Types.LONGVARCHAR,
            Types.NCHAR, Types.NVARCHAR, Types.LONGNVARCHAR
        }

        # Date/time types are compatible with each other
        datetime_types = {
            Types.DATE, Types.TIME, Types.TIMESTAMP
        }

        # Check if both are in the same category
        if type1 in numeric_types and type2 in numeric_types:
            return True
        if type1 in string_types and type2 in string_types:
            return True
        if type1 in datetime_types and type2 in datetime_types:
            return True

        # Exact match
        return type1 == type2

    def _test_sample_data(
        self,
        source_conn: Any,
        target_conn: Any,
        rule: ReconciliationRule,
        sample_size: int
    ) -> Tuple[Optional[float], List[str]]:
        """
        Test the rule on sample data and calculate match rate.

        Args:
            source_conn: Source database connection
            target_conn: Target database connection
            rule: Reconciliation rule
            sample_size: Number of records to sample

        Returns:
            Tuple of (match_rate, warnings)
        """
        warnings = []

        try:
            # Sample source records
            source_cursor = source_conn.cursor()
            source_cols = ', '.join(rule.source_columns)
            source_query = f"""
                SELECT {source_cols}
                FROM {rule.source_schema}.{rule.source_table}
                WHERE ROWNUM <= {sample_size}
            """
            source_cursor.execute(source_query)
            source_records = source_cursor.fetchall()
            source_cursor.close()

            if not source_records:
                warnings.append("No source records found for testing")
                return None, warnings

            # Sample target records
            target_cursor = target_conn.cursor()
            target_cols = ', '.join(rule.target_columns)
            target_query = f"""
                SELECT {target_cols}
                FROM {rule.target_schema}.{rule.target_table}
                WHERE ROWNUM <= {sample_size}
            """
            target_cursor.execute(target_query)
            target_records = target_cursor.fetchall()
            target_cursor.close()

            if not target_records:
                warnings.append("No target records found for testing")
                return None, warnings

            # Count matches based on match type
            matches = 0
            for source_record in source_records:
                if self._record_matches(source_record, target_records, rule):
                    matches += 1

            # Calculate match rate
            match_rate = matches / len(source_records) if source_records else 0.0

            logger.debug(
                f"Sample test: {matches}/{len(source_records)} matches = {match_rate:.2%}"
            )

            return match_rate, warnings

        except Exception as e:
            logger.error(f"Error testing sample data: {e}")
            warnings.append(f"Sample data test failed: {str(e)}")
            return None, warnings

    def _record_matches(
        self,
        source_record: Tuple,
        target_records: List[Tuple],
        rule: ReconciliationRule
    ) -> bool:
        """Check if a source record matches any target record."""
        for target_record in target_records:
            if rule.match_type == ReconciliationMatchType.EXACT:
                # Exact match: all column values must be equal
                if source_record == target_record[:len(source_record)]:
                    return True

            elif rule.match_type == ReconciliationMatchType.FUZZY:
                # Fuzzy match: use string similarity (simplified)
                # In production, use proper fuzzy matching library
                if self._fuzzy_match(source_record, target_record):
                    return True

            elif rule.match_type == ReconciliationMatchType.TRANSFORMATION:
                # Apply transformation before matching
                # This would require executing the transformation
                # For now, treat as exact match
                if source_record == target_record[:len(source_record)]:
                    return True

        return False

    def _fuzzy_match(self, record1: Tuple, record2: Tuple, threshold: float = 0.8) -> bool:
        """Simple fuzzy matching (for strings)."""
        try:
            # Simple implementation: check if strings are similar
            for val1, val2 in zip(record1, record2):
                if isinstance(val1, str) and isinstance(val2, str):
                    # Simple similarity: case-insensitive comparison
                    if val1.lower().strip() != val2.lower().strip():
                        return False
                else:
                    if val1 != val2:
                        return False
            return True
        except:
            return False

    def _detect_cardinality(
        self,
        source_conn: Any,
        target_conn: Any,
        rule: ReconciliationRule,
        sample_size: int
    ) -> Optional[str]:
        """
        Detect the cardinality of the relationship (1:1, 1:N, N:M).

        Args:
            source_conn: Source database connection
            target_conn: Target database connection
            rule: Reconciliation rule
            sample_size: Number of records to analyze

        Returns:
            Cardinality string: "1:1", "1:N", "N:1", or "N:M"
        """
        try:
            # Count distinct values on both sides
            source_cursor = source_conn.cursor()
            source_cols = ', '.join(rule.source_columns)

            source_cursor.execute(f"""
                SELECT COUNT(*) as total, COUNT(DISTINCT {source_cols}) as distinct_count
                FROM (
                    SELECT {source_cols}
                    FROM {rule.source_schema}.{rule.source_table}
                    WHERE ROWNUM <= {sample_size}
                )
            """)
            source_result = source_cursor.fetchone()
            source_total = source_result[0]
            source_distinct = source_result[1]
            source_cursor.close()

            target_cursor = target_conn.cursor()
            target_cols = ', '.join(rule.target_columns)

            target_cursor.execute(f"""
                SELECT COUNT(*) as total, COUNT(DISTINCT {target_cols}) as distinct_count
                FROM (
                    SELECT {target_cols}
                    FROM {rule.target_schema}.{rule.target_table}
                    WHERE ROWNUM <= {sample_size}
                )
            """)
            target_result = target_cursor.fetchone()
            target_total = target_result[0]
            target_distinct = target_result[1]
            target_cursor.close()

            # Determine cardinality based on uniqueness
            source_unique = (source_total == source_distinct)
            target_unique = (target_total == target_distinct)

            if source_unique and target_unique:
                return "1:1"
            elif source_unique and not target_unique:
                return "1:N"
            elif not source_unique and target_unique:
                return "N:1"
            else:
                return "N:M"

        except Exception as e:
            logger.error(f"Error detecting cardinality: {e}")
            return None

    def _estimate_performance(
        self,
        source_conn: Any,
        target_conn: Any,
        rule: ReconciliationRule
    ) -> Optional[float]:
        """
        Estimate the performance of executing this rule.

        Args:
            source_conn: Source database connection
            target_conn: Target database connection
            rule: Reconciliation rule

        Returns:
            Estimated execution time in milliseconds
        """
        try:
            # Simple estimation: time a small query and extrapolate
            start_time = time.time()

            cursor = source_conn.cursor()
            source_cols = ', '.join(rule.source_columns)
            cursor.execute(f"""
                SELECT {source_cols}
                FROM {rule.source_schema}.{rule.source_table}
                WHERE ROWNUM <= 10
            """)
            cursor.fetchall()
            cursor.close()

            elapsed_ms = (time.time() - start_time) * 1000

            # Rough estimate: multiply by expected scale
            estimated_ms = elapsed_ms * 10  # Assuming 100x scale

            return estimated_ms

        except Exception as e:
            logger.error(f"Error estimating performance: {e}")
            return None


# Singleton instance
_rule_validator: Optional[RuleValidator] = None


def get_rule_validator() -> RuleValidator:
    """Get or create the singleton rule validator instance."""
    global _rule_validator
    if _rule_validator is None:
        _rule_validator = RuleValidator()
    return _rule_validator
