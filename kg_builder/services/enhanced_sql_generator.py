"""
Enhanced SQL Generator with OPS_PLANNER inclusion
Automatically includes ops_planner column from hana_material_master in all generated queries.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class EnhancedSQLGenerator:
    """Enhanced SQL Generator that automatically includes ops_planner column."""
    
    def __init__(self, original_generator):
        """Initialize with the original SQL generator."""
        self.original_generator = original_generator
        logger.info("Enhanced SQL Generator initialized with ops_planner inclusion")
    
    def enhance_sql_with_ops_planner(self, sql: str, query_intent: Dict[str, Any]) -> str:
        """
        Enhance generated SQL to include ops_planner column from hana_material_master.
        
        Args:
            sql: Original generated SQL
            query_intent: Query intent with table information
            
        Returns:
            Enhanced SQL with ops_planner column included
        """
        try:
            # Skip enhancement if SQL is None or empty
            if not sql or not sql.strip():
                logger.warning("Empty SQL provided, skipping ops_planner enhancement")
                return sql
            
            # Check if hana_material_master is involved in the query
            if not self._involves_hana_material_master(sql):
                logger.info("Query doesn't involve hana_material_master, skipping ops_planner enhancement")
                return sql
            
            # Enhance the SQL
            enhanced_sql = self._add_ops_planner_to_select(sql)
            
            logger.info("✓ Enhanced SQL with ops_planner column")
            return enhanced_sql
            
        except Exception as e:
            logger.error(f"Failed to enhance SQL with ops_planner: {e}")
            # Return original SQL if enhancement fails
            return sql
    
    def _involves_hana_material_master(self, sql: str) -> bool:
        """Check if the query involves hana_material_master table."""
        sql_lower = sql.lower()
        return 'hana_material_master' in sql_lower
    
    def _add_ops_planner_to_select(self, sql: str) -> str:
        """Add ops_planner column to SELECT statement."""
        try:
            # Parse the SQL to identify the main SELECT statement
            sql_lines = sql.strip().split('\n')
            enhanced_lines = []
            
            in_select_clause = False
            select_clause_ended = False
            ops_planner_added = False
            
            for line in sql_lines:
                line_lower = line.lower().strip()
                
                # Detect start of SELECT clause
                if line_lower.startswith('select'):
                    in_select_clause = True
                    select_clause_ended = False
                
                # Detect end of SELECT clause (FROM keyword)
                if in_select_clause and line_lower.startswith('from'):
                    in_select_clause = False
                    select_clause_ended = True
                    
                    # Add ops_planner before FROM if not already added
                    if not ops_planner_added:
                        # Find the hana_material_master alias
                        hana_alias = self._find_hana_material_master_alias(sql)
                        ops_planner_line = f"    {hana_alias}.OPS_PLANNER as ops_planner,"
                        enhanced_lines.append(ops_planner_line)
                        ops_planner_added = True
                        logger.debug(f"Added ops_planner column with alias: {hana_alias}")
                
                # Add the current line
                enhanced_lines.append(line)
                
                # Check if ops_planner is already in this line
                if 'ops_planner' in line_lower:
                    ops_planner_added = True
            
            # If we couldn't add ops_planner in the normal way, try alternative approach
            if not ops_planner_added:
                enhanced_lines = self._add_ops_planner_alternative(sql_lines)
                ops_planner_added = True
            
            enhanced_sql = '\n'.join(enhanced_lines)
            
            if ops_planner_added:
                logger.debug("Successfully added ops_planner to SELECT clause")
            else:
                logger.warning("Could not add ops_planner to SELECT clause")
            
            return enhanced_sql
            
        except Exception as e:
            logger.error(f"Error adding ops_planner to SELECT: {e}")
            return sql
    
    def _find_hana_material_master_alias(self, sql: str) -> str:
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
            
            # If no alias found, assume table name is used directly
            logger.debug("No alias found for hana_material_master, using table name")
            return "hana_material_master"
            
        except Exception as e:
            logger.error(f"Error finding hana_material_master alias: {e}")
            return "hana_material_master"
    
    def _add_ops_planner_alternative(self, sql_lines: List[str]) -> List[str]:
        """Alternative method to add ops_planner when normal parsing fails."""
        try:
            enhanced_lines = []
            
            for i, line in enumerate(sql_lines):
                enhanced_lines.append(line)
                
                # Look for the last column in SELECT before FROM
                if i < len(sql_lines) - 1:
                    current_line_lower = line.lower().strip()
                    next_line_lower = sql_lines[i + 1].lower().strip()
                    
                    # If current line is in SELECT and next line starts with FROM
                    if (not current_line_lower.startswith('from') and 
                        next_line_lower.startswith('from') and
                        'select' in '\n'.join(sql_lines[:i+1]).lower()):
                        
                        # Add ops_planner column
                        hana_alias = self._find_hana_material_master_alias('\n'.join(sql_lines))
                        ops_planner_line = f"    {hana_alias}.OPS_PLANNER as ops_planner,"
                        enhanced_lines.append(ops_planner_line)
                        logger.debug("Added ops_planner using alternative method")
                        break
            
            return enhanced_lines
            
        except Exception as e:
            logger.error(f"Error in alternative ops_planner addition: {e}")
            return sql_lines
    
    def generate_sql(self, query_intent: Dict[str, Any], kg_data: Dict[str, Any], **kwargs) -> str:
        """
        Generate SQL using original generator and enhance with ops_planner.
        
        This method wraps the original generator and adds ops_planner enhancement.
        """
        try:
            # Generate SQL using original generator
            original_sql = self.original_generator.generate_sql(query_intent, kg_data, **kwargs)
            
            # Enhance with ops_planner
            enhanced_sql = self.enhance_sql_with_ops_planner(original_sql, query_intent)
            
            return enhanced_sql
            
        except Exception as e:
            logger.error(f"Error in enhanced SQL generation: {e}")
            # Return original result if enhancement fails
            try:
                return self.original_generator.generate_sql(query_intent, kg_data, **kwargs)
            except:
                return None
