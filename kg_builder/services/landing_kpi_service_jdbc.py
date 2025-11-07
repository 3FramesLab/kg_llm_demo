"""
Landing KPI Service using JDBC (Working Alternative to pyodbc)
Uses the existing JDBC infrastructure that's already working in the system.
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import glob
import os

try:
    import jaydebeapi
    JAYDEBEAPI_AVAILABLE = True
except ImportError:
    JAYDEBEAPI_AVAILABLE = False
    logging.warning("JayDeBeApi not installed. Database execution will not be available.")

from kg_builder.config import (
    KPI_DB_HOST, KPI_DB_PORT, KPI_DB_DATABASE,
    KPI_DB_USERNAME, KPI_DB_PASSWORD, KPI_DB_TYPE,
    JDBC_DRIVERS_PATH
)

logger = logging.getLogger(__name__)


class LandingKPIServiceJDBC:
    """Landing KPI Service using JDBC connections (like the rest of the system)."""
    
    def __init__(self, database: str = None):
        """Initialize with JDBC connection to KPI database."""
        self.host = KPI_DB_HOST
        self.port = KPI_DB_PORT
        self.database = database or KPI_DB_DATABASE  # Use KPI-specific database
        self.username = KPI_DB_USERNAME
        self.password = KPI_DB_PASSWORD
        self.db_type = KPI_DB_TYPE

        logger.info(f"KPI Service initialized for {self.db_type} at {self.host}:{self.port}/{self.database}")
    
    def _get_connection(self):
        """Get JDBC database connection (same as other services use)."""
        if not JAYDEBEAPI_AVAILABLE:
            raise Exception("jaydebeapi is not available - cannot connect to database")

        try:
            # Build JDBC URL
            if self.db_type.lower() in ['sqlserver', 'mssql']:
                jdbc_url = f"jdbc:sqlserver://{self.host}:{self.port};databaseName={self.database};encrypt=true;trustServerCertificate=true"
                driver_class = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
                jar_pattern = "mssql-jdbc*.jar"
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            # Find JDBC driver
            jdbc_dir = JDBC_DRIVERS_PATH
            pattern = os.path.join(jdbc_dir, jar_pattern)
            jars = glob.glob(pattern)
            
            if not jars:
                raise Exception(f"No JDBC driver found for {self.db_type} at {pattern}")
            
            driver_jar = jars[0]
            logger.debug(f"Using JDBC driver: {driver_jar}")
            
            # Connect using jaydebeapi (same as other services)
            conn = jaydebeapi.connect(
                driver_class,
                jdbc_url,
                [self.username, self.password],
                driver_jar
            )
            
            return conn
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def get_all_kpis(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """Get all KPIs using JDBC connection."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            where_clause = "" if include_inactive else "WHERE k.is_active = 1"
            
            query = f"""
                SELECT 
                    k.id, k.name, k.alias_name, k.group_name, k.description, k.nl_definition,
                    k.created_at, k.updated_at, k.created_by, k.is_active,
                    e.id as latest_execution_id,
                    e.execution_timestamp as latest_execution,
                    e.execution_status as latest_status,
                    e.number_of_records as latest_record_count,
                    e.generated_sql as latest_sql,
                    e.error_message as latest_error
                FROM kpi_definitions k
                LEFT JOIN kpi_execution_results e ON k.id = e.kpi_id
                    AND e.execution_timestamp = (
                        SELECT MAX(execution_timestamp) 
                        FROM kpi_execution_results 
                        WHERE kpi_id = k.id
                    )
                {where_clause}
                ORDER BY k.group_name, k.name
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            kpis = []
            for row in rows:
                kpi = {
                    'id': row[0],
                    'name': row[1],
                    'alias_name': row[2],
                    'group_name': row[3],
                    'description': row[4],
                    'nl_definition': row[5],
                    'created_at': str(row[6]) if row[6] else None,
                    'updated_at': str(row[7]) if row[7] else None,
                    'created_by': row[8],
                    'is_active': bool(row[9]),
                    'latest_execution': {
                        'id': row[10],
                        'timestamp': str(row[11]) if row[11] else None,
                        'status': row[12],
                        'record_count': row[13],
                        'generated_sql': row[14],  # Always include SQL
                        'error_message': row[15]
                    } if row[10] else None
                }
                kpis.append(kpi)
            
            logger.info(f"Retrieved {len(kpis)} KPIs via JDBC")
            return kpis
            
        finally:
            cursor.close()
            conn.close()

    def delete_kpi(self, kpi_id: int) -> bool:
        """Delete a KPI by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # First check if KPI exists
            cursor.execute("SELECT id FROM kpi_definitions WHERE id = ?", (kpi_id,))
            if not cursor.fetchone():
                logger.warning(f"KPI with ID {kpi_id} not found for deletion")
                return False

            # Delete execution results first (foreign key constraint)
            cursor.execute("DELETE FROM kpi_execution_results WHERE kpi_id = ?", (kpi_id,))
            deleted_executions = cursor.rowcount

            # Delete the KPI definition
            cursor.execute("DELETE FROM kpi_definitions WHERE id = ?", (kpi_id,))
            deleted_kpi = cursor.rowcount

            # Commit the transaction
            conn.commit()

            logger.info(f"✓ Deleted KPI {kpi_id} and {deleted_executions} execution records")
            return deleted_kpi > 0

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Failed to delete KPI {kpi_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def test_connection(self) -> bool:
        """Test if JDBC connection works."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result[0] == 1
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data grouped by KPI groups."""
        kpis = self.get_all_kpis(include_inactive=False)
        
        # Group KPIs by group_name
        groups = {}
        for kpi in kpis:
            group_name = kpi.get('group_name') or 'Ungrouped'
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(kpi)
        
        # Convert to list format
        groups_list = [
            {
                'group_name': group_name,
                'kpis': kpis_in_group
            }
            for group_name, kpis_in_group in sorted(groups.items())
        ]
        
        return {'groups': groups_list}
    
    def create_kpi(self, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new KPI (placeholder - would need full implementation)."""
        # For now, just return the data with a fake ID
        # In a real implementation, this would insert into the database
        return {
            'id': 999,
            'success': True,
            'message': 'KPI creation not fully implemented yet',
            **kpi_data
        }

    def update_kpi(self, kpi_id: int, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update KPI definition using JDBC connection."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Build dynamic update query
            updates = []
            params = []

            # Handle the fields that can be updated
            for key in ['name', 'alias_name', 'group_name', 'description', 'nl_definition', 'is_active']:
                if key in kpi_data and kpi_data[key] is not None:
                    updates.append(f"{key} = ?")
                    params.append(kpi_data[key])

            if not updates:
                # No updates to make, just return the current KPI
                return self.get_kpi(kpi_id)

            # Add updated_at timestamp (SQL Server syntax)
            updates.append("updated_at = GETDATE()")
            params.append(kpi_id)

            # Execute update query
            query = f"UPDATE kpi_definitions SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)

            if cursor.rowcount == 0:
                raise ValueError(f"KPI with ID {kpi_id} not found")

            conn.commit()
            logger.info(f"✓ Updated KPI ID: {kpi_id}")

            # Return the updated KPI
            return self.get_kpi(kpi_id)

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Failed to update KPI {kpi_id}: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_kpi(self, kpi_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific KPI by ID."""
        kpis = self.get_all_kpis(include_inactive=True)
        for kpi in kpis:
            if kpi['id'] == kpi_id:
                return kpi
        return None
    
    def execute_kpi(self, kpi_id: int, execution_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a KPI and store results in the database."""
        import time
        import json
        from datetime import datetime

        start_time = time.time()

        try:
            # Get the KPI definition
            kpi = self.get_kpi(kpi_id)
            if not kpi:
                raise ValueError(f"KPI with ID {kpi_id} not found")

            # Extract execution parameters
            kg_name = execution_params.get('kg_name', 'default')
            schemas = execution_params.get('schemas', ['newdqschemanov'])
            select_schema = schemas[0] if schemas else 'newdqschemanov'
            use_llm = execution_params.get('use_llm', True)
            limit_records = execution_params.get('limit', 1000)
            db_type = execution_params.get('db_type', 'sqlserver')

            # Load Knowledge Graph for join column inference
            from kg_builder.services.graphiti_backend import get_graphiti_backend
            from kg_builder.models import KnowledgeGraph, GraphNode, GraphRelationship

            logger.info(f"Loading Knowledge Graph: {kg_name}")
            graphiti = get_graphiti_backend()
            entities_data = graphiti.get_entities(kg_name)
            relationships_data = graphiti.get_relationships(kg_name)

            # Convert to KnowledgeGraph object
            nodes = [GraphNode(**entity) for entity in entities_data] if entities_data else []
            relationships = [GraphRelationship(**rel) for rel in relationships_data] if relationships_data else []

            # Load metadata including table_aliases
            table_aliases = {}
            try:
                kg_metadata = graphiti.get_kg_metadata(kg_name)
                if kg_metadata:
                    table_aliases = kg_metadata.get('table_aliases', {})
            except Exception as e:
                logger.warning(f"Could not load KG metadata: {e}")

            kg = KnowledgeGraph(
                name=kg_name,
                nodes=nodes,
                relationships=relationships,
                schema_file=select_schema,
                table_aliases=table_aliases
            )
            logger.info(f"✓ Loaded KG '{kg_name}' with {len(nodes)} nodes and {len(relationships)} relationships")

            # Execute the KPI using the existing NL query system with KG
            from kg_builder.services.nl_query_executor import NLQueryExecutor
            from kg_builder.services.nl_query_parser import get_nl_query_parser

            # Extract schemas_info from KG for LLM prompt
            def _extract_schemas_info_from_kg(kg):
                schemas_info = {}
                for node in kg.nodes:
                    if node.properties.get("type") == "Table":
                        schema_name = node.properties.get("schema", select_schema)
                        if schema_name not in schemas_info:
                            schemas_info[schema_name] = {"tables": {}}

                        table_name = node.label
                        columns = node.properties.get("columns", [])

                        # Extract column names
                        column_names = []
                        for col in columns:
                            if isinstance(col, dict):
                                col_name = col.get("name")
                                if col_name:
                                    column_names.append(col_name)
                            elif hasattr(col, 'name'):
                                column_names.append(col.name)

                        schemas_info[schema_name]["tables"][table_name] = {
                            "columns": column_names
                        }
                return schemas_info

            schemas_info = _extract_schemas_info_from_kg(kg)

            # Parse the natural language definition with KG
            parser = get_nl_query_parser(kg=kg, schemas_info=schemas_info)
            intent = parser.parse(kpi['nl_definition'], use_llm=use_llm)

            # Execute the query with KG
            executor = NLQueryExecutor(
                db_type=db_type.lower(),
                kg=kg,
                use_llm=use_llm
            )

            # Get database connection for execution
            from kg_builder.services.landing_kpi_executor import _get_source_database_connection
            connection = _get_source_database_connection(db_type)

            if not connection:
                raise Exception("Could not establish database connection for KPI execution")

            # Generate SQL (simple, no enhancement)
            sql_to_execute = executor.generator.generate(intent)

            logger.info(f"🔍 Generated SQL: {sql_to_execute[:100]}...")

            # Execute the SQL
            from kg_builder.services.nl_query_executor import QueryResult
            try:
                cursor = connection.cursor()
                cursor.execute(sql_to_execute)

                # Fetch results
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []

                # Convert to list of dictionaries
                records = []
                for row in rows:
                    record = {}
                    for i, value in enumerate(row):
                        if i < len(columns):
                            record[columns[i]] = value
                    records.append(record)

                result = QueryResult(
                    definition=kpi['nl_definition'],
                    query_type='kpi_execution',
                    operation='execute',
                    sql=sql_to_execute,
                    record_count=len(records),
                    records=records,
                    join_columns=None,
                    confidence=0.95,  # High confidence for successful execution
                    execution_time_ms=(time.time() - start_time) * 1000,
                    error=None,
                    source_table=None,
                    target_table=None
                )

                logger.info(f"✅ Enhanced SQL executed successfully: {len(records)} records found")

            except Exception as e:
                logger.error(f"❌ Enhanced SQL execution failed: {e}")
                result = QueryResult(
                    definition=kpi['nl_definition'],
                    query_type='kpi_execution',
                    operation='execute',
                    sql=sql_to_execute,
                    record_count=0,
                    records=[],
                    join_columns=None,
                    confidence=0.0,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    error=str(e),
                    source_table=None,
                    target_table=None
                )
            finally:
                cursor.close()

            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)

            # Prepare execution record
            execution_record = {
                'kpi_id': kpi_id,
                'kg_name': kg_name,
                'select_schema': select_schema,
                'db_type': db_type,
                'limit_records': limit_records,
                'use_llm': use_llm,
                'generated_sql': result.sql,
                'number_of_records': result.record_count,
                'execution_status': 'success' if not result.error else 'error',
                'execution_time_ms': execution_time_ms,
                'confidence_score': result.confidence,
                'error_message': result.error if result.error else None,
                'result_data': json.dumps(result.records) if result.records else None,
                'execution_timestamp': datetime.now().isoformat()
            }

            # Store execution result in database
            execution_id = self.store_execution_result(execution_record)

            # Return comprehensive result
            return {
                'success': True,
                'execution_id': execution_id,
                'kpi_id': kpi_id,
                'kpi_name': kpi['name'],
                'execution_status': execution_record['execution_status'],
                'record_count': execution_record['number_of_records'],
                'execution_time_ms': execution_time_ms,
                'generated_sql': result.sql,
                'enhanced_sql': result.sql,  # Same as generated_sql for now
                'enhancement_applied': False,  # No enhancement for now
                'material_master_added': False,
                'ops_planner_added': False,
                'confidence_score': execution_record['confidence_score'],
                'data': result.records,
                'error_message': execution_record['error_message']
            }

        except Exception as e:
            # Store failed execution
            execution_time_ms = int((time.time() - start_time) * 1000)

            execution_record = {
                'kpi_id': kpi_id,
                'kg_name': execution_params.get('kg_name', 'default'),
                'select_schema': execution_params.get('schemas', ['newdqschemanov'])[0],
                'db_type': execution_params.get('db_type', 'sqlserver'),
                'limit_records': execution_params.get('limit', 1000),
                'use_llm': execution_params.get('use_llm', True),
                'generated_sql': None,
                'number_of_records': 0,
                'execution_status': 'error',
                'execution_time_ms': execution_time_ms,
                'confidence_score': 0.0,
                'error_message': str(e),
                'result_data': None,
                'execution_timestamp': datetime.now().isoformat()
            }

            try:
                execution_id = self.store_execution_result(execution_record)
            except Exception as store_error:
                logger.error(f"Failed to store error execution result: {store_error}")
                execution_id = None

            return {
                'success': False,
                'execution_id': execution_id,
                'kpi_id': kpi_id,
                'execution_status': 'error',
                'error_message': str(e),
                'execution_time_ms': execution_time_ms
            }

    def store_execution_result(self, execution_record: Dict[str, Any]) -> int:
        """Store KPI execution result in the database."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Insert execution result
            cursor.execute("""
                INSERT INTO kpi_execution_results (
                    kpi_id, kg_name, select_schema, db_type, limit_records, use_llm,
                    generated_sql, number_of_records, execution_status, execution_timestamp,
                    execution_time_ms, confidence_score, error_message, result_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution_record['kpi_id'],
                execution_record['kg_name'],
                execution_record['select_schema'],
                execution_record['db_type'],
                execution_record['limit_records'],
                execution_record['use_llm'],
                execution_record['generated_sql'],
                execution_record['number_of_records'],
                execution_record['execution_status'],
                execution_record['execution_timestamp'],
                execution_record['execution_time_ms'],
                execution_record['confidence_score'],
                execution_record['error_message'],
                execution_record['result_data']
            ))

            # Get the inserted ID
            cursor.execute("SELECT @@IDENTITY")
            execution_id = cursor.fetchone()[0]

            # Commit the transaction
            conn.commit()

            logger.info(f"✓ Stored execution result with ID {execution_id}")
            return execution_id

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Failed to store execution result: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_latest_results(self, kpi_id: int) -> Optional[Dict[str, Any]]:
        """Get the latest execution results for a specific KPI."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT TOP 1
                    id, kpi_id, kg_name, select_schema, generated_sql,
                    number_of_records, execution_status, execution_timestamp,
                    execution_time_ms, confidence_score, error_message, result_data
                FROM kpi_execution_results
                WHERE kpi_id = ?
                ORDER BY execution_timestamp DESC
            """, (kpi_id,))

            row = cursor.fetchone()
            if not row:
                return None

            # Parse result data if it exists
            result_data = None
            if row[11]:  # result_data column
                try:
                    import json
                    result_data = json.loads(row[11])
                except:
                    result_data = None

            return {
                'execution_id': row[0],
                'kpi_id': row[1],
                'kg_name': row[2],
                'select_schema': row[3],
                'generated_sql': row[4],
                'number_of_records': row[5],
                'execution_status': row[6],
                'execution_timestamp': str(row[7]) if row[7] else None,
                'execution_time_ms': row[8],
                'confidence_score': row[9],
                'error_message': row[10],
                'result_data': result_data
            }

        finally:
            cursor.close()
            conn.close()
