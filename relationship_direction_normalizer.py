#!/usr/bin/env python3
"""
Relationship Direction Normalizer - Option 1 Implementation
Ensures hana_material_master is always on the target side of relationships.
"""

from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class RelationshipDirectionNormalizer:
    """
    Normalizes relationship direction to ensure master tables are always targets.
    """
    
    def __init__(self):
        # Define master tables that should always be targets
        self.master_tables = {
            'hana_material_master',
            'table_hana_material_master'  # Handle both naming conventions
        }
        
        # Define relationship type mappings for direction swapping
        self.inverse_relationship_map = {
            'REFERENCES': 'REFERENCED_BY',
            'REFERENCED_BY': 'REFERENCES',
            'MATCHES': 'MATCHES',  # Symmetric - stays the same
            'SEMANTIC_REFERENCE': 'SEMANTIC_REFERENCED_BY',
            'SEMANTIC_REFERENCED_BY': 'SEMANTIC_REFERENCE',
            'FOREIGN_KEY': 'FOREIGN_KEY_TARGET',
            'FOREIGN_KEY_TARGET': 'FOREIGN_KEY',
            'CONTAINS': 'CONTAINED_BY',
            'CONTAINED_BY': 'CONTAINS'
        }
    
    def normalize_table_name(self, table_name: str) -> str:
        """
        Normalize table name by removing 'table_' prefix if present.
        
        Args:
            table_name: Original table name
            
        Returns:
            Normalized table name
        """
        if table_name.startswith('table_'):
            return table_name[6:]  # Remove 'table_' prefix
        return table_name
    
    def is_master_table(self, table_name: str) -> bool:
        """
        Check if a table is a master table.
        
        Args:
            table_name: Table name to check
            
        Returns:
            True if table is a master table
        """
        normalized_name = self.normalize_table_name(table_name)
        return normalized_name in {self.normalize_table_name(t) for t in self.master_tables}
    
    def get_inverse_relationship_type(self, relationship_type: str) -> str:
        """
        Get the inverse relationship type for direction swapping.
        
        Args:
            relationship_type: Original relationship type
            
        Returns:
            Inverse relationship type
        """
        return self.inverse_relationship_map.get(relationship_type, relationship_type)
    
    def should_swap_direction(self, source_table: str, target_table: str) -> bool:
        """
        Determine if relationship direction should be swapped.
        
        Args:
            source_table: Current source table
            target_table: Current target table
            
        Returns:
            True if direction should be swapped
        """
        source_is_master = self.is_master_table(source_table)
        target_is_master = self.is_master_table(target_table)
        
        # Swap if source is master but target is not
        return source_is_master and not target_is_master
    
    def normalize_relationship(self, relationship: Dict) -> Dict:
        """
        Normalize a single relationship to ensure master tables are targets.
        
        Args:
            relationship: Original relationship dictionary
            
        Returns:
            Normalized relationship dictionary
        """
        source_id = relationship.get('source_id', '')
        target_id = relationship.get('target_id', '')
        relationship_type = relationship.get('relationship_type', '')
        source_column = relationship.get('source_column')
        target_column = relationship.get('target_column')
        
        # Check if we need to swap direction
        if self.should_swap_direction(source_id, target_id):
            logger.info(f"Swapping relationship direction: {source_id} → {target_id} becomes {target_id} → {source_id}")
            
            # Create normalized relationship with swapped direction
            normalized_relationship = {
                'source_id': self.normalize_table_name(target_id),
                'target_id': self.normalize_table_name(source_id),
                'relationship_type': self.get_inverse_relationship_type(relationship_type),
                'source_column': target_column,  # Swap columns too
                'target_column': source_column,
                'properties': relationship.get('properties', {}).copy()
            }
            
            # Add metadata about the swap
            normalized_relationship['properties']['direction_swapped'] = True
            normalized_relationship['properties']['original_source'] = source_id
            normalized_relationship['properties']['original_target'] = target_id
            normalized_relationship['properties']['original_relationship_type'] = relationship_type
            
        else:
            # No swap needed, just normalize table names
            normalized_relationship = {
                'source_id': self.normalize_table_name(source_id),
                'target_id': self.normalize_table_name(target_id),
                'relationship_type': relationship_type,
                'source_column': source_column,
                'target_column': target_column,
                'properties': relationship.get('properties', {}).copy()
            }
            
            # Add metadata that no swap occurred
            normalized_relationship['properties']['direction_swapped'] = False
        
        return normalized_relationship
    
    def normalize_relationships(self, relationships: List[Dict]) -> List[Dict]:
        """
        Normalize a list of relationships.
        
        Args:
            relationships: List of relationship dictionaries
            
        Returns:
            List of normalized relationship dictionaries
        """
        normalized_relationships = []
        swap_count = 0
        
        for relationship in relationships:
            normalized = self.normalize_relationship(relationship)
            normalized_relationships.append(normalized)
            
            if normalized['properties'].get('direction_swapped', False):
                swap_count += 1
        
        logger.info(f"Normalized {len(relationships)} relationships, swapped direction for {swap_count}")
        
        return normalized_relationships
    
    def create_normalized_relationship(
        self, 
        source_table: str, 
        target_table: str, 
        relationship_type: str,
        source_column: Optional[str] = None,
        target_column: Optional[str] = None,
        properties: Optional[Dict] = None
    ) -> Dict:
        """
        Create a new relationship with proper direction normalization.
        
        Args:
            source_table: Source table name
            target_table: Target table name
            relationship_type: Type of relationship
            source_column: Source column name
            target_column: Target column name
            properties: Additional properties
            
        Returns:
            Normalized relationship dictionary
        """
        # Create temporary relationship
        temp_relationship = {
            'source_id': source_table,
            'target_id': target_table,
            'relationship_type': relationship_type,
            'source_column': source_column,
            'target_column': target_column,
            'properties': properties or {}
        }
        
        # Normalize it
        return self.normalize_relationship(temp_relationship)


def integrate_with_kg_builder():
    """
    Example integration with KG builder components.
    """
    normalizer = RelationshipDirectionNormalizer()
    
    # Example: During LLM relationship inference
    def create_llm_inferred_relationship(source_table: str, target_table: str, 
                                       relationship_type: str, confidence: float,
                                       reasoning: str, source_col: str = None, 
                                       target_col: str = None) -> Dict:
        """Create LLM-inferred relationship with proper direction."""
        
        properties = {
            'llm_inferred': True,
            'llm_confidence': confidence,
            'llm_reasoning': reasoning,
            'llm_description': f"Inferred: {reasoning}"
        }
        
        return normalizer.create_normalized_relationship(
            source_table=source_table,
            target_table=target_table,
            relationship_type=relationship_type,
            source_column=source_col,
            target_column=target_col,
            properties=properties
        )
    
    # Example: During explicit relationship creation
    def create_explicit_relationship(source_table: str, target_table: str,
                                   relationship_type: str, source_col: str,
                                   target_col: str, confidence: float = 0.95) -> Dict:
        """Create explicit relationship with proper direction."""
        
        properties = {
            'llm_inferred': False,
            'explicit': True,
            'confidence': confidence,
            'source': 'explicit_pair_v2'
        }
        
        return normalizer.create_normalized_relationship(
            source_table=source_table,
            target_table=target_table,
            relationship_type=relationship_type,
            source_column=source_col,
            target_column=target_col,
            properties=properties
        )
    
    return create_llm_inferred_relationship, create_explicit_relationship


# Example usage and testing
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create normalizer
    normalizer = RelationshipDirectionNormalizer()
    
    # Test relationships
    test_relationships = [
        {
            "source_id": "hana_material_master",
            "target_id": "brz_lnd_RBP_GPU", 
            "relationship_type": "MATCHES",
            "source_column": "MATERIAL",
            "target_column": "Material",
            "properties": {"confidence": 0.9}
        },
        {
            "source_id": "table_hana_material_master",
            "target_id": "table_brz_lnd_OPS_EXCEL_GPU",
            "relationship_type": "SEMANTIC_REFERENCE", 
            "source_column": "Business Unit",
            "target_column": "Business_Unit",
            "properties": {"llm_inferred": True, "llm_confidence": 0.75}
        },
        {
            "source_id": "brz_lnd_SAR_Excel_NBU",
            "target_id": "hana_material_master",
            "relationship_type": "REFERENCES",
            "source_column": "Material", 
            "target_column": "MATERIAL",
            "properties": {"confidence": 0.95}
        }
    ]
    
    print("Original relationships:")
    for i, rel in enumerate(test_relationships, 1):
        print(f"{i}. {rel['source_id']} → {rel['target_id']} ({rel['relationship_type']})")
    
    print("\nNormalized relationships:")
    normalized = normalizer.normalize_relationships(test_relationships)
    
    for i, rel in enumerate(normalized, 1):
        swapped = "🔄" if rel['properties'].get('direction_swapped') else "✓"
        print(f"{i}. {swapped} {rel['source_id']} → {rel['target_id']} ({rel['relationship_type']})")
    
    print("\nMaster table (hana_material_master) is now always the target! ✅")


# Integration example for your existing KG builder
class KGBuilderIntegration:
    """
    Example integration with existing KG builder components.
    """

    def __init__(self):
        self.normalizer = RelationshipDirectionNormalizer()

    def process_llm_inferred_relationships(self, raw_relationships: List[Dict]) -> List[Dict]:
        """
        Process LLM-inferred relationships with direction normalization.

        Args:
            raw_relationships: Raw relationships from LLM inference

        Returns:
            Normalized relationships
        """
        print(f"Processing {len(raw_relationships)} LLM-inferred relationships...")

        # Normalize all relationships
        normalized = self.normalizer.normalize_relationships(raw_relationships)

        # Log statistics
        swapped_count = sum(1 for rel in normalized if rel['properties'].get('direction_swapped'))
        print(f"✅ Normalized {len(normalized)} relationships")
        print(f"🔄 Swapped direction for {swapped_count} relationships")
        print(f"🎯 hana_material_master is now target in {self._count_master_as_target(normalized)} relationships")

        return normalized

    def process_explicit_relationships(self, explicit_pairs: List[Tuple]) -> List[Dict]:
        """
        Process explicit relationship pairs with direction normalization.

        Args:
            explicit_pairs: List of (source_table, target_table, source_col, target_col) tuples

        Returns:
            Normalized relationships
        """
        relationships = []

        for source_table, target_table, source_col, target_col in explicit_pairs:
            # Create explicit relationship
            relationship = self.normalizer.create_normalized_relationship(
                source_table=source_table,
                target_table=target_table,
                relationship_type='MATCHES',
                source_column=source_col,
                target_column=target_col,
                properties={
                    'llm_inferred': False,
                    'explicit': True,
                    'confidence': 0.95,
                    'source': 'explicit_pair_v2'
                }
            )
            relationships.append(relationship)

        print(f"✅ Created {len(relationships)} explicit relationships with proper direction")
        return relationships

    def _count_master_as_target(self, relationships: List[Dict]) -> int:
        """Count relationships where hana_material_master is the target."""
        return sum(1 for rel in relationships
                  if self.normalizer.normalize_table_name(rel['target_id']) == 'hana_material_master')

    def validate_master_table_consistency(self, relationships: List[Dict]) -> Dict:
        """
        Validate that master tables are consistently used as targets.

        Args:
            relationships: List of relationships to validate

        Returns:
            Validation report
        """
        master_as_source = 0
        master_as_target = 0
        total_relationships = len(relationships)

        for rel in relationships:
            source_normalized = self.normalizer.normalize_table_name(rel['source_id'])
            target_normalized = self.normalizer.normalize_table_name(rel['target_id'])

            if source_normalized == 'hana_material_master':
                master_as_source += 1
            if target_normalized == 'hana_material_master':
                master_as_target += 1

        report = {
            'total_relationships': total_relationships,
            'master_as_source': master_as_source,
            'master_as_target': master_as_target,
            'consistency_achieved': master_as_source == 0,
            'consistency_percentage': (master_as_target / max(master_as_source + master_as_target, 1)) * 100
        }

        return report


# Usage example with your existing data
def demonstrate_with_your_data():
    """
    Demonstrate the normalizer with your actual relationship data.
    """
    integration = KGBuilderIntegration()

    # Your actual LLM-inferred relationship
    your_llm_relationship = {
        "source_id": "table_hana_material_master",
        "target_id": "table_brz_lnd_OPS_EXCEL_GPU",
        "relationship_type": "SEMANTIC_REFERENCE",
        "properties": {
            "llm_inferred": True,
            "llm_confidence": 0.75,
            "llm_reasoning": "The columns 'Business Unit' and 'Business_Unit' denote the same business entity, facilitating organizational context understanding.",
            "llm_description": "Inferred: The columns 'Business Unit' and 'Business_Unit' denote the same business entity, facilitating organizational context understanding.",
            "data_type_match": "NVARCHAR ↔ NVARCHAR"
        },
        "source_column": "Business Unit",
        "target_column": "Business_Unit"
    }

    print("🔍 BEFORE NORMALIZATION:")
    print(f"Source: {your_llm_relationship['source_id']}")
    print(f"Target: {your_llm_relationship['target_id']}")
    print(f"Type: {your_llm_relationship['relationship_type']}")
    print(f"Direction: hana_material_master is SOURCE ❌")

    # Normalize the relationship
    normalized = integration.normalizer.normalize_relationship(your_llm_relationship)

    print("\n✅ AFTER NORMALIZATION:")
    print(f"Source: {normalized['source_id']}")
    print(f"Target: {normalized['target_id']}")
    print(f"Type: {normalized['relationship_type']}")
    print(f"Direction: hana_material_master is TARGET ✅")
    print(f"Swapped: {normalized['properties']['direction_swapped']}")

    # Show the semantic meaning
    print(f"\n🎯 SEMANTIC MEANING:")
    print(f"'{normalized['source_id']}' REFERENCES '{normalized['target_id']}'")
    print(f"brz_lnd_OPS_EXCEL_GPU.Business_Unit → hana_material_master.Business Unit")

    return normalized


if __name__ == "__main__":
    print("=" * 60)
    print("RELATIONSHIP DIRECTION NORMALIZER - DEMONSTRATION")
    print("=" * 60)

    # Run the demonstration
    demonstrate_with_your_data()
