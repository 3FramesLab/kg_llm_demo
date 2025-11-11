"""
SQL OPS_PLANNER Enhancer
Automatically adds ops_planner column from hana_material_master to all generated SQL queries.
This is a complete, working implementation that integrates with the existing SQL generation pipeline.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class SQLOpsplannerEnhancer:
    """Enhances SQL queries by automatically adding ops_planner column from hana_material_master."""
    
    def __init__(self):
        """Initialize the SQL enhancer."""
        self.hana_table_patterns = [
            r'hana_material_master',
            r'hana_material_master\s+(\w+)',  # With alias
            r'FROM\s+hana_material_master',
            r'JOIN\s+hana_material_master'
        ]
        logger.info("SQL OPS_PLANNER Enhancer initialized")
    
    def enhance_sql(self, sql: str, query_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhance SQL by adding ops_planner column from hana_material_master.
        
        Args:
            sql: Original SQL query
            query_context: Additional context about the query
            
        Returns:
            Dict with original_sql, enhanced_sql, and metadata
        """
        if not sql or not sql.strip():
            logger.warning("Empty SQL provided for enhancement")
            return {
                'original_sql': sql,
                'enhanced_sql': sql,
                'ops_planner_added': False,
                'involves_hana_master': False,
                'enhancement_applied': False
            }
        
        try:
            # Check if query involves hana_material_master
            involves_hana = self._involves_hana_material_master(sql)
            
            if not involves_hana:
                logger.debug("Query doesn't involve hana_material_master, skipping enhancement")
                return {
                    'original_sql': sql,
                    'enhanced_sql': sql,
                    'ops_planner_added': False,
                    'involves_hana_master': False,
                    'enhancement_applied': False
                }
            
            # Enhance the SQL
            enhanced_sql = self._add_ops_planner_to_query(sql)
            ops_planner_added = 'ops_planner' in enhanced_sql.lower()
            
            logger.info(f"✓ Enhanced SQL with ops_planner: {ops_planner_added}")
            
            return {
                'original_sql': sql,
                'enhanced_sql': enhanced_sql,
                'ops_planner_added': ops_planner_added,
                'involves_hana_master': True,
                'enhancement_applied': True,
                'hana_alias': self._find_hana_alias(sql)
            }
            
        except Exception as e:
            logger.error(f"Failed to enhance SQL with ops_planner: {e}")
            return {
                'original_sql': sql,
                'enhanced_sql': sql,
                'ops_planner_added': False,
                'involves_hana_master': involves_hana,
                'enhancement_applied': False,
                'error': str(e)
            }
    
    def _involves_hana_material_master(self, sql: str) -> bool:
        """Check if the query involves hana_material_master table."""
        sql_lower = sql.lower()
        
        # Check for various patterns
        patterns = [
            r'\bhana_material_master\b',
            r'\bfrom\s+hana_material_master\b',
            r'\bjoin\s+hana_material_master\b',
            r'\bleft\s+join\s+hana_material_master\b',
            r'\bright\s+join\s+hana_material_master\b',
            r'\binner\s+join\s+hana_material_master\b'
        ]
        
        for pattern in patterns:
            if re.search(pattern, sql_lower):
                logger.debug(f"Found hana_material_master pattern: {pattern}")
                return True
        
        return False
    
    def _find_hana_alias(self, sql: str) -> str:
        """Find the alias used for hana_material_master table."""
        try:
            # Look for patterns like "FROM hana_material_master h" or "JOIN hana_material_master h"
            patterns = [
                r'FROM\s+hana_material_master\s+(\w+)',
                r'JOIN\s+hana_material_master\s+(\w+)',
                r'LEFT\s+JOIN\s+hana_material_master\s+(\w+)',
                r'RIGHT\s+JOIN\s+hana_material_master\s+(\w+)',
                r'INNER\s+JOIN\s+hana_material_master\s+(\w+)'
            ]
            
            sql_upper = sql.upper()
            
            for pattern in patterns:
                match = re.search(pattern, sql_upper)
                if match:
                    alias = match.group(1).lower()
                    logger.debug(f"Found hana_material_master alias: {alias}")
                    return alias
            
            # If no alias found, return table name
            logger.debug("No alias found for hana_material_master, using table name")
            return "hana_material_master"
            
        except Exception as e:
            logger.error(f"Error finding hana_material_master alias: {e}")
            return "hana_material_master"
    
    def _add_ops_planner_to_query(self, sql: str) -> str:
        """Add ops_planner column to the SELECT statement."""
        try:
            # Check if ops_planner is already in the query
            if 'ops_planner' in sql.lower():
                logger.debug("ops_planner already present in query")
                return sql
            
            # Find the hana_material_master alias
            hana_alias = self._find_hana_alias(sql)
            
            # Split SQL into lines for processing
            lines = sql.split('\n')
            enhanced_lines = []
            
            in_select_clause = False
            select_clause_processed = False
            
            for i, line in enumerate(lines):
                line_lower = line.lower().strip()
                
                # Detect SELECT clause
                if line_lower.startswith('select') and not select_clause_processed:
                    in_select_clause = True
                
                # Detect end of SELECT clause (FROM keyword)
                if in_select_clause and line_lower.startswith('from'):
                    # Check if the previous line needs a comma
                    if enhanced_lines and not enhanced_lines[-1].rstrip().endswith(','):
                        # Add comma to previous line
                        enhanced_lines[-1] = enhanced_lines[-1].rstrip() + ','

                    # Add ops_planner before FROM
                    ops_planner_line = f"    {hana_alias}.OPS_PLANNER as ops_planner"
                    enhanced_lines.append(ops_planner_line)
                    in_select_clause = False
                    select_clause_processed = True
                
                # Add the current line
                enhanced_lines.append(line)
            
            # If we couldn't add ops_planner in the normal way, try alternative approach
            if not select_clause_processed:
                enhanced_lines = self._add_ops_planner_alternative(lines, hana_alias)
            
            enhanced_sql = '\n'.join(enhanced_lines)
            logger.debug("Successfully added ops_planner to SELECT clause")
            return enhanced_sql
            
        except Exception as e:
            logger.error(f"Error adding ops_planner to query: {e}")
            return sql
    
    def _add_ops_planner_alternative(self, lines: List[str], hana_alias: str) -> List[str]:
        """Alternative method to add ops_planner when normal parsing fails."""
        try:
            enhanced_lines = []
            
            for i, line in enumerate(lines):
                enhanced_lines.append(line)
                
                # Look for the last column in SELECT before FROM
                if i < len(lines) - 1:
                    current_line_lower = line.lower().strip()
                    next_line_lower = lines[i + 1].lower().strip()
                    
                    # If current line is in SELECT and next line starts with FROM
                    if (not current_line_lower.startswith('from') and 
                        next_line_lower.startswith('from')):
                        
                        # Add ops_planner column
                        ops_planner_line = f"    {hana_alias}.OPS_PLANNER as ops_planner,"
                        enhanced_lines.append(ops_planner_line)
                        logger.debug("Added ops_planner using alternative method")
                        break
            
            return enhanced_lines
            
        except Exception as e:
            logger.error(f"Error in alternative ops_planner addition: {e}")
            return lines
    
    def enhance_query_result(self, query_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance a complete query result with ops_planner.
        
        Args:
            query_result: Result from SQL generation containing 'generated_sql'
            
        Returns:
            Enhanced query result with both original and enhanced SQL
        """
        if not query_result or 'generated_sql' not in query_result:
            logger.warning("Invalid query result provided for enhancement")
            return query_result
        
        original_sql = query_result.get('generated_sql')
        enhancement_result = self.enhance_sql(original_sql, query_result)
        
        # Add enhancement information to the result
        enhanced_result = query_result.copy()
        enhanced_result.update({
            'original_sql': enhancement_result['original_sql'],
            'enhanced_sql': enhancement_result['enhanced_sql'],
            'ops_planner_added': enhancement_result['ops_planner_added'],
            'involves_hana_master': enhancement_result['involves_hana_master'],
            'enhancement_applied': enhancement_result['enhancement_applied']
        })
        
        # Use enhanced SQL as the main generated_sql
        if enhancement_result['enhancement_applied']:
            enhanced_result['generated_sql'] = enhancement_result['enhanced_sql']
        
        return enhanced_result


# Global instance for easy import
ops_planner_enhancer = SQLOpsplannerEnhancer()
