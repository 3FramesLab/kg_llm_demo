#!/usr/bin/env python3
"""
Table Name Normalizer - Handles inconsistent table_ prefix naming
"""

import re
from typing import Dict, List, Set
import logging

logger = logging.getLogger(__name__)

class TableNameNormalizer:
    """
    Normalizes table names to handle inconsistent 'table_' prefix usage.
    """
    
    def __init__(self, strategy: str = 'remove_prefix'):
        """
        Initialize normalizer with strategy.
        
        Args:
            strategy: 'remove_prefix', 'add_prefix', or 'context_aware'
        """
        self.strategy = strategy
        self.normalization_stats = {
            'total_processed': 0,
            'prefixes_removed': 0,
            'prefixes_added': 0,
            'no_change': 0
        }
    
    def normalize_table_name(self, table_name: str, context: str = 'default') -> str:
        """
        Normalize a single table name.
        
        Args:
            table_name: Original table name
            context: Context for normalization ('sql', 'display', 'schema')
            
        Returns:
            Normalized table name
        """
        if not table_name:
            return table_name
        
        original_name = table_name
        self.normalization_stats['total_processed'] += 1
        
        if self.strategy == 'remove_prefix':
            normalized = self._remove_table_prefix(table_name)
        elif self.strategy == 'add_prefix':
            normalized = self._add_table_prefix(table_name)
        elif self.strategy == 'context_aware':
            normalized = self._context_aware_normalize(table_name, context)
        else:
            normalized = table_name
            
        # Track statistics
        if normalized != original_name:
            if original_name.startswith('table_') and not normalized.startswith('table_'):
                self.normalization_stats['prefixes_removed'] += 1
            elif not original_name.startswith('table_') and normalized.startswith('table_'):
                self.normalization_stats['prefixes_added'] += 1
        else:
            self.normalization_stats['no_change'] += 1
            
        return normalized
    
    def _remove_table_prefix(self, table_name: str) -> str:
        """Remove table_ prefix if present."""
        if table_name.startswith('table_'):
            return table_name[6:]  # Remove 'table_' (6 characters)
        return table_name
    
    def _add_table_prefix(self, table_name: str) -> str:
        """Add table_ prefix if not present."""
        if not table_name.startswith('table_'):
            return f'table_{table_name}'
        return table_name
    
    def _context_aware_normalize(self, table_name: str, context: str) -> str:
        """Normalize based on context."""
        if context in ['sql', 'database', 'query']:
            # For SQL contexts, remove prefix (matches actual table names)
            return self._remove_table_prefix(table_name)
        elif context in ['schema', 'metadata', 'catalog']:
            # For schema contexts, add prefix (for categorization)
            return self._add_table_prefix(table_name)
        else:
            # Default: remove prefix for cleaner names
            return self._remove_table_prefix(table_name)
    
    def normalize_relationship(self, relationship: Dict) -> Dict:
        """
        Normalize table names in a relationship.
        
        Args:
            relationship: Relationship dictionary
            
        Returns:
            Relationship with normalized table names
        """
        normalized_relationship = relationship.copy()
        
        # Normalize source and target table names
        if 'source_id' in relationship:
            normalized_relationship['source_id'] = self.normalize_table_name(
                relationship['source_id'], 'sql'
            )
        
        if 'target_id' in relationship:
            normalized_relationship['target_id'] = self.normalize_table_name(
                relationship['target_id'], 'sql'
            )
        
        # Add normalization metadata
        if 'properties' not in normalized_relationship:
            normalized_relationship['properties'] = {}
        
        normalized_relationship['properties']['table_names_normalized'] = True
        normalized_relationship['properties']['normalization_strategy'] = self.strategy
        
        return normalized_relationship
    
    def normalize_relationships(self, relationships: List[Dict]) -> List[Dict]:
        """
        Normalize table names in a list of relationships.
        
        Args:
            relationships: List of relationship dictionaries
            
        Returns:
            List of relationships with normalized table names
        """
        normalized_relationships = []
        
        for relationship in relationships:
            normalized = self.normalize_relationship(relationship)
            normalized_relationships.append(normalized)
        
        logger.info(f"Normalized table names in {len(relationships)} relationships")
        return normalized_relationships
    
    def get_normalization_stats(self) -> Dict:
        """Get normalization statistics."""
        return self.normalization_stats.copy()
    
    def find_inconsistent_names(self, relationships: List[Dict]) -> Dict:
        """
        Find inconsistent table naming patterns.
        
        Args:
            relationships: List of relationships to analyze
            
        Returns:
            Analysis of naming inconsistencies
        """
        table_names = set()
        prefixed_names = set()
        clean_names = set()
        
        # Collect all table names
        for rel in relationships:
            for field in ['source_id', 'target_id']:
                if field in rel:
                    name = rel[field]
                    table_names.add(name)
                    
                    if name.startswith('table_'):
                        prefixed_names.add(name)
                        clean_names.add(name[6:])  # Add clean version
                    else:
                        clean_names.add(name)
        
        # Find duplicates (same table with and without prefix)
        duplicates = []
        for clean_name in clean_names:
            prefixed_version = f'table_{clean_name}'
            if clean_name in table_names and prefixed_version in table_names:
                duplicates.append({
                    'clean_name': clean_name,
                    'prefixed_name': prefixed_version
                })
        
        return {
            'total_unique_names': len(table_names),
            'prefixed_names': len(prefixed_names),
            'clean_names': len(clean_names),
            'duplicates': duplicates,
            'consistency_issues': len(duplicates) > 0,
            'all_table_names': sorted(list(table_names))
        }


# Integration with relationship direction normalizer
class CombinedNormalizer:
    """
    Combines table name normalization with relationship direction normalization.
    """
    
    def __init__(self, table_strategy: str = 'remove_prefix'):
        from relationship_direction_normalizer import RelationshipDirectionNormalizer
        
        self.table_normalizer = TableNameNormalizer(strategy=table_strategy)
        self.direction_normalizer = RelationshipDirectionNormalizer()
    
    def normalize_relationship(self, relationship: Dict) -> Dict:
        """
        Apply both table name and direction normalization.
        
        Args:
            relationship: Original relationship
            
        Returns:
            Fully normalized relationship
        """
        # Step 1: Normalize table names
        table_normalized = self.table_normalizer.normalize_relationship(relationship)
        
        # Step 2: Normalize direction (this also normalizes table names, but consistently)
        fully_normalized = self.direction_normalizer.normalize_relationship(table_normalized)
        
        return fully_normalized
    
    def normalize_relationships(self, relationships: List[Dict]) -> List[Dict]:
        """Normalize a list of relationships with both normalizers."""
        normalized = []
        
        for relationship in relationships:
            normalized_rel = self.normalize_relationship(relationship)
            normalized.append(normalized_rel)
        
        # Get statistics
        table_stats = self.table_normalizer.get_normalization_stats()
        
        logger.info(f"Applied combined normalization to {len(relationships)} relationships")
        logger.info(f"Table name changes: {table_stats}")
        
        return normalized


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test data with inconsistent naming
    test_relationships = [
        {
            "source_id": "table_hana_material_master",
            "target_id": "table_brz_lnd_OPS_EXCEL_GPU",
            "relationship_type": "SEMANTIC_REFERENCE"
        },
        {
            "source_id": "hana_material_master",
            "target_id": "brz_lnd_RBP_GPU",
            "relationship_type": "MATCHES"
        },
        {
            "source_id": "brz_lnd_SAR_Excel_NBU",
            "target_id": "table_hana_material_master",
            "relationship_type": "REFERENCES"
        }
    ]
    
    print("🔍 INCONSISTENT NAMING ANALYSIS:")
    print("=" * 50)
    
    # Analyze inconsistencies
    normalizer = TableNameNormalizer()
    analysis = normalizer.find_inconsistent_names(test_relationships)
    
    print(f"Total unique names: {analysis['total_unique_names']}")
    print(f"Names with 'table_' prefix: {analysis['prefixed_names']}")
    print(f"Clean names: {analysis['clean_names']}")
    print(f"Consistency issues: {analysis['consistency_issues']}")
    
    if analysis['duplicates']:
        print("\n❌ DUPLICATE NAMING DETECTED:")
        for dup in analysis['duplicates']:
            print(f"  • {dup['clean_name']} AND {dup['prefixed_name']}")
    
    print(f"\nAll table names found:")
    for name in analysis['all_table_names']:
        prefix_status = "📋" if name.startswith('table_') else "🔧"
        print(f"  {prefix_status} {name}")
    
    print("\n✅ AFTER NORMALIZATION (remove_prefix strategy):")
    print("=" * 50)
    
    # Apply normalization
    combined_normalizer = CombinedNormalizer(table_strategy='remove_prefix')
    normalized = combined_normalizer.normalize_relationships(test_relationships)
    
    for i, rel in enumerate(normalized, 1):
        direction_swapped = "🔄" if rel['properties'].get('direction_swapped') else "✓"
        print(f"{i}. {direction_swapped} {rel['source_id']} → {rel['target_id']}")
    
    print(f"\n🎯 RESULT: All table names are now clean and hana_material_master is always the target!")
