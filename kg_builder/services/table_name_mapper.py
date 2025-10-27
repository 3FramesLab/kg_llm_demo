"""
Service for mapping business terms to actual table names.

This service helps resolve natural language references to tables
(e.g., "RBP", "OPS Excel") to actual database table names
(e.g., "brz_lnd_RBP_GPU", "brz_lnd_OPS_EXCEL_GPU").
"""
import logging
import re
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class TableNameMapper:
    """Maps business terms to actual table names."""

    def __init__(self, schemas_info: Dict[str, any] = None, learned_aliases: Dict[str, List[str]] = None):
        """
        Initialize the mapper.

        Args:
            schemas_info: Dictionary of schema information with tables
            learned_aliases: LLM-learned business-friendly aliases from KG (optional)
        """
        self.schemas_info = schemas_info or {}
        self.learned_aliases = learned_aliases or {}
        self.table_aliases = self._build_aliases()

    def _build_aliases(self) -> Dict[str, str]:
        """
        Build a mapping of aliases to actual table names.
        Includes both hardcoded aliases and LLM-learned aliases.

        Returns:
            Dictionary mapping aliases to table names
        """
        aliases = {}

        # Extract all table names from schemas
        all_tables = self._get_all_tables()

        for table_name in all_tables:
            # Add exact match
            aliases[table_name.lower()] = table_name

            # Add common abbreviations
            # e.g., "brz_lnd_RBP_GPU" -> "rbp", "rbp_gpu", "gpu"
            parts = table_name.lower().split('_')

            # Add last part (e.g., "gpu")
            if parts:
                aliases[parts[-1]] = table_name

            # Add meaningful parts (skip "brz", "lnd")
            meaningful_parts = [p for p in parts if p not in ['brz', 'lnd']]

            # Add combined meaningful parts
            if meaningful_parts:
                combined = '_'.join(meaningful_parts)
                aliases[combined] = table_name

                # Add first meaningful part (e.g., "rbp")
                aliases[meaningful_parts[0]] = table_name

            # Add special aliases for common business terms
            if 'rbp' in table_name.lower():
                aliases['rbp'] = table_name
                aliases['rbp_gpu'] = table_name

            if 'ops' in table_name.lower() and 'excel' in table_name.lower():
                aliases['ops'] = table_name
                aliases['ops_excel'] = table_name
                aliases['ops excel'] = table_name
                aliases['opsexcel'] = table_name

        # Add LLM-learned aliases (highest priority - override hardcoded ones)
        if self.learned_aliases:
            logger.info(f"Adding {len(self.learned_aliases)} LLM-learned table aliases")
            for table_name, learned_alias_list in self.learned_aliases.items():
                for alias in learned_alias_list:
                    alias_lower = alias.lower().strip()
                    if alias_lower:
                        aliases[alias_lower] = table_name
                        logger.debug(f"Added learned alias: '{alias_lower}' → '{table_name}'")

        logger.debug(f"Built {len(aliases)} table aliases (including {len(self.learned_aliases)} learned)")
        return aliases

    def _get_all_tables(self) -> List[str]:
        """Get all table names from schemas."""
        tables = []
        for schema_name, schema in self.schemas_info.items():
            if hasattr(schema, 'tables') and schema.tables:
                tables.extend(schema.tables.keys())
        return tables

    def resolve_table_name(self, term: str) -> Optional[str]:
        """
        Resolve a business term to an actual table name.

        Args:
            term: Business term (e.g., "RBP", "OPS Excel")

        Returns:
            Actual table name or None if not found
        """
        if not term:
            return None

        term_lower = term.lower().strip()

        # Try exact match first
        if term_lower in self.table_aliases:
            return self.table_aliases[term_lower]

        # Try fuzzy matching
        best_match = self._fuzzy_match(term_lower)
        if best_match:
            return best_match

        # Try pattern matching
        pattern_match = self._pattern_match(term_lower)
        if pattern_match:
            return pattern_match

        return None

    def _fuzzy_match(self, term: str) -> Optional[str]:
        """
        Find best fuzzy match for a term.

        Args:
            term: Search term

        Returns:
            Best matching table name or None
        """
        best_match = None
        best_ratio = 0.6  # Minimum similarity threshold

        for alias, table_name in self.table_aliases.items():
            ratio = SequenceMatcher(None, term, alias).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = table_name

        return best_match

    def _pattern_match(self, term: str) -> Optional[str]:
        """
        Find match using pattern matching.

        Args:
            term: Search term

        Returns:
            Matching table name or None
        """
        # Remove spaces and special characters
        normalized = re.sub(r'[^a-z0-9]', '', term)

        for alias, table_name in self.table_aliases.items():
            alias_normalized = re.sub(r'[^a-z0-9]', '', alias)
            if normalized == alias_normalized:
                return table_name

        return None

    def get_all_aliases(self) -> Dict[str, str]:
        """
        Get all available aliases.

        Returns:
            Dictionary of aliases to table names
        """
        return self.table_aliases.copy()

    def get_table_info(self) -> Dict[str, List[str]]:
        """
        Get information about all tables and their aliases.

        Returns:
            Dictionary mapping table names to their aliases
        """
        table_info = {}
        for alias, table_name in self.table_aliases.items():
            if table_name not in table_info:
                table_info[table_name] = []
            table_info[table_name].append(alias)

        return table_info


def get_table_name_mapper(schemas_info: Dict[str, any] = None, learned_aliases: Dict[str, List[str]] = None) -> TableNameMapper:
    """
    Factory function to get a TableNameMapper instance.

    Args:
        schemas_info: Dictionary of schema information
        learned_aliases: LLM-learned business-friendly aliases from KG (optional)

    Returns:
        TableNameMapper instance
    """
    return TableNameMapper(schemas_info, learned_aliases)

