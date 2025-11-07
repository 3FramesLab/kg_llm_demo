"""
Material Master Enhancer
Automatically includes hana_material_master and ops_planner in material-related queries.
This ensures ops_planner is always available for material analysis.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class MaterialMasterEnhancer:
    """Enhances SQL queries by automatically including hana_material_master and ops_planner."""
    
    def __init__(self):
        """Initialize the Material Master enhancer."""
        # Tables that contain material information and should be enhanced
        self.material_tables = [
            'brz_lnd_rbp_gpu',
            'brz_lnd_ops_excel_gpu',
            'brz_lnd_sku_lifnr_excel',
            'brz_lnd_ibp_product_master',
            'brz_lnd_sar_excel_gpu',
            'brz_lnd_gpu_sku_in_skulifnr',
            'brz_lnd_sar_excel_nbu'
        ]
        
        # Material column mappings (table -> material column name)
        self.material_columns = {
            'brz_lnd_rbp_gpu': 'Material',
            'brz_lnd_ops_excel_gpu': 'PLANNING_SKU',
            'brz_lnd_sku_lifnr_excel': 'SKU',
            'brz_lnd_ibp_product_master': 'Material',
            'brz_lnd_sar_excel_gpu': 'Material',
            'brz_lnd_gpu_sku_in_skulifnr': 'SKU',
            'brz_lnd_sar_excel_nbu': 'Material'
        }
        
        logger.info("Material Master Enhancer initialized")
    
    def enhance_sql_with_material_master(self, sql: str, query_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhance SQL by automatically including hana_material_master and ops_planner.
        
        Args:
            sql: Original SQL query
            query_context: Additional context about the query
            
        Returns:
            Dict with original_sql, enhanced_sql, and metadata
        """
        if not sql or not sql.strip():
            logger.warning("Empty SQL provided for material master enhancement")
            return {
                'original_sql': sql,
                'enhanced_sql': sql,
                'material_master_added': False,
                'ops_planner_added': False,
                'enhancement_applied': False
            }
        
        try:
            # Check if query involves material tables
            involves_material_tables = self._involves_material_tables(sql)
            
            if not involves_material_tables:
                logger.debug("Query doesn't involve material tables, skipping enhancement")
                return {
                    'original_sql': sql,
                    'enhanced_sql': sql,
                    'material_master_added': False,
                    'ops_planner_added': False,
                    'enhancement_applied': False,
                    'reason': 'no_material_tables'
                }
            
            # Check if hana_material_master is already included
            if 'hana_material_master' in sql.lower():
                logger.debug("hana_material_master already in query, applying ops_planner enhancement only")
                from kg_builder.services.sql_ops_planner_enhancer import ops_planner_enhancer
                ops_result = ops_planner_enhancer.enhance_sql(sql)
                return {
                    'original_sql': sql,
                    'enhanced_sql': ops_result['enhanced_sql'],
                    'material_master_added': False,
                    'ops_planner_added': ops_result['ops_planner_added'],
                    'enhancement_applied': ops_result['enhancement_applied'],
                    'reason': 'ops_planner_only'
                }
            
            # Enhance the SQL by adding hana_material_master
            logger.info(f"🔧 Adding material master to SQL: {sql[:100]}...")
            enhanced_sql = self._add_material_master_to_query(sql)

            # Check if material master was actually added
            material_master_actually_added = 'hana_material_master' in enhanced_sql.lower()
            logger.info(f"🔍 Material master actually added: {material_master_actually_added}")

            if not material_master_actually_added:
                logger.warning(f"⚠️ Material master enhancement failed - SQL unchanged")
                logger.info(f"🔍 Enhanced SQL: {enhanced_sql[:200]}...")

            # Now add ops_planner to the enhanced SQL
            from kg_builder.services.sql_ops_planner_enhancer import ops_planner_enhancer
            ops_result = ops_planner_enhancer.enhance_sql(enhanced_sql)

            final_sql = ops_result['enhanced_sql']

            # Check if ops_planner was actually added
            ops_planner_actually_added = 'ops_planner' in final_sql.lower()
            logger.info(f"🔍 OPS_PLANNER actually added: {ops_planner_actually_added}")

            if material_master_actually_added or ops_planner_actually_added:
                logger.info(f"✓ Enhanced SQL with material master and ops_planner")
            else:
                logger.warning(f"⚠️ Enhancement claimed success but SQL unchanged!")

            return {
                'original_sql': sql,
                'enhanced_sql': final_sql,
                'material_master_added': material_master_actually_added,
                'ops_planner_added': ops_planner_actually_added,
                'enhancement_applied': material_master_actually_added or ops_planner_actually_added,
                'material_tables_detected': involves_material_tables
            }
            
        except Exception as e:
            logger.error(f"Failed to enhance SQL with material master: {e}")
            return {
                'original_sql': sql,
                'enhanced_sql': sql,
                'material_master_added': False,
                'ops_planner_added': False,
                'enhancement_applied': False,
                'error': str(e)
            }
    
    def _involves_material_tables(self, sql: str) -> List[str]:
        """Check if the query involves material-related tables."""
        sql_lower = sql.lower()
        involved_tables = []
        
        for table in self.material_tables:
            # Check for various patterns
            patterns = [
                rf'\b{table.lower()}\b',
                rf'\bfrom\s+{table.lower()}\b',
                rf'\bjoin\s+{table.lower()}\b',
                rf'\bleft\s+join\s+{table.lower()}\b',
                rf'\bright\s+join\s+{table.lower()}\b',
                rf'\binner\s+join\s+{table.lower()}\b'
            ]
            
            for pattern in patterns:
                if re.search(pattern, sql_lower):
                    involved_tables.append(table)
                    logger.debug(f"Found material table: {table}")
                    break
        
        return involved_tables
    
    def _add_material_master_to_query(self, sql: str) -> str:
        """Add hana_material_master join to the query."""
        try:
            logger.info(f"🔍 Finding main material table in SQL...")
            # Find the main table and its material column
            main_table, material_column = self._find_main_material_table(sql)

            if not main_table or not material_column:
                logger.warning(f"❌ Could not identify main material table for enhancement. Found table: {main_table}, column: {material_column}")
                logger.info(f"🔍 SQL being analyzed: {sql[:200]}...")
                return sql

            logger.info(f"✅ Found main material table: {main_table}, column: {material_column}")

            # Add hana_material_master join
            logger.info(f"🔧 Injecting material master join...")
            enhanced_sql = self._inject_material_master_join(sql, main_table, material_column)

            if enhanced_sql != sql:
                logger.info(f"✅ Added hana_material_master join for table: {main_table}")
            else:
                logger.warning(f"⚠️ JOIN injection failed - SQL unchanged")

            return enhanced_sql

        except Exception as e:
            logger.error(f"❌ Error adding material master to query: {e}")
            return sql
    
    def _find_main_material_table(self, sql: str) -> Tuple[Optional[str], Optional[str]]:
        """Find the main material table in the query."""
        sql_lower = sql.lower()

        # Look for FROM clause first - handle bracketed table names
        from_patterns = [
            r'from\s+\[([^\]]+)\]',  # FROM [table_name]
            r'from\s+(\w+)'          # FROM table_name
        ]

        for pattern in from_patterns:
            from_match = re.search(pattern, sql_lower)
            if from_match:
                table_name = from_match.group(1)
                logger.debug(f"Found FROM table: {table_name}")
                for material_table in self.material_tables:
                    if material_table.lower() == table_name.lower():
                        logger.debug(f"Matched material table: {material_table}")
                        return material_table, self.material_columns.get(material_table)

        # Look for any material table in the query
        for material_table in self.material_tables:
            if material_table.lower() in sql_lower:
                logger.debug(f"Found material table in query: {material_table}")
                return material_table, self.material_columns.get(material_table)

        logger.debug("No material table found in query")
        return None, None
    
    def _inject_material_master_join(self, sql: str, main_table: str, material_column: str) -> str:
        """Inject hana_material_master join into the SQL."""
        try:
            # Find the main table alias
            main_alias = self._find_table_alias(sql, main_table)
            
            # Create the join clause
            join_clause = f"\nLEFT JOIN hana_material_master hm ON {main_alias}.{material_column} = hm.MATERIAL"
            
            # Find where to insert the join (after the main FROM clause)
            lines = sql.split('\n')
            enhanced_lines = []
            
            for line in lines:
                enhanced_lines.append(line)
                
                # Insert join after FROM line
                if line.lower().strip().startswith('from') and main_table.lower() in line.lower():
                    enhanced_lines.append(join_clause)
            
            return '\n'.join(enhanced_lines)
            
        except Exception as e:
            logger.error(f"Error injecting material master join: {e}")
            return sql
    
    def _find_table_alias(self, sql: str, table_name: str) -> str:
        """Find the alias used for a table."""
        try:
            # Look for patterns like "FROM [table_name] alias" or "FROM table_name alias"
            patterns = [
                rf'FROM\s+\[{re.escape(table_name)}\]\s+(\w+)',  # [table_name] alias
                rf'FROM\s+{re.escape(table_name)}\s+(\w+)',      # table_name alias
                rf'FROM\s+\[{re.escape(table_name.lower())}\]\s+(\w+)',  # [table_name_lower] alias
                rf'FROM\s+{re.escape(table_name.lower())}\s+(\w+)'       # table_name_lower alias
            ]

            for pattern in patterns:
                match = re.search(pattern, sql, re.IGNORECASE)
                if match:
                    alias = match.group(1)
                    logger.debug(f"Found table alias '{alias}' for table '{table_name}'")
                    return alias

            # If no alias found, return table name
            logger.debug(f"No alias found for table '{table_name}', using table name")
            return table_name

        except Exception as e:
            logger.error(f"Error finding table alias: {e}")
            return table_name


# Global instance for easy import
material_master_enhancer = MaterialMasterEnhancer()
