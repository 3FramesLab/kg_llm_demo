"""
Storage service for reconciliation rules and rulesets.

Provides persistence layer for saving and retrieving reconciliation rules.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from kg_builder.models import ReconciliationRuleSet, ReconciliationRule
from kg_builder.config import DATA_DIR

logger = logging.getLogger(__name__)


class ReconciliationRuleStorage:
    """Store and retrieve reconciliation rulesets."""

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize the storage service.

        Args:
            storage_path: Optional custom path for storing rules.
                         Defaults to data/reconciliation_rules
        """
        if storage_path is None:
            self.storage_path = DATA_DIR / "reconciliation_rules"
        else:
            self.storage_path = storage_path

        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"ReconciliationRuleStorage initialized at: {self.storage_path}")

    def save_ruleset(self, ruleset: ReconciliationRuleSet) -> bool:
        """
        Save a ruleset to JSON file.

        Args:
            ruleset: The ruleset to save

        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = self.storage_path / f"{ruleset.ruleset_id}.json"

            # Convert to dict
            ruleset_dict = ruleset.dict()

            # Convert datetime objects to ISO format strings
            ruleset_dict = self._serialize_datetimes(ruleset_dict)

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(ruleset_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved ruleset '{ruleset.ruleset_id}' to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error saving ruleset {ruleset.ruleset_id}: {e}")
            return False

    def load_ruleset(self, ruleset_id: str) -> Optional[ReconciliationRuleSet]:
        """
        Load a ruleset from storage.

        Args:
            ruleset_id: ID of the ruleset to load

        Returns:
            ReconciliationRuleSet if found, None otherwise
        """
        try:
            filepath = self.storage_path / f"{ruleset_id}.json"

            if not filepath.exists():
                logger.warning(f"Ruleset file not found: {filepath}")
                return None

            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Convert ISO strings back to datetime
            data = self._deserialize_datetimes(data)

            ruleset = ReconciliationRuleSet(**data)
            logger.info(f"Loaded ruleset '{ruleset_id}' with {len(ruleset.rules)} rules")
            return ruleset

        except Exception as e:
            logger.error(f"Error loading ruleset {ruleset_id}: {e}")
            return None

    def list_rulesets(self) -> List[Dict[str, Any]]:
        """
        List all saved rulesets with metadata.

        Returns:
            List of dictionaries containing ruleset metadata
        """
        rulesets = []

        try:
            for filepath in self.storage_path.glob("*.json"):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Extract metadata
                    metadata = {
                        'ruleset_id': data.get('ruleset_id'),
                        'ruleset_name': data.get('ruleset_name'),
                        'schemas': data.get('schemas', []),
                        'rules_count': len(data.get('rules', [])),
                        'created_at': data.get('created_at'),
                        'generated_from_kg': data.get('generated_from_kg')
                    }
                    rulesets.append(metadata)

                except Exception as e:
                    logger.error(f"Error reading ruleset file {filepath}: {e}")
                    continue

            logger.info(f"Found {len(rulesets)} rulesets")
            return rulesets

        except Exception as e:
            logger.error(f"Error listing rulesets: {e}")
            return []

    def delete_ruleset(self, ruleset_id: str) -> bool:
        """
        Delete a ruleset from storage.

        Args:
            ruleset_id: ID of the ruleset to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = self.storage_path / f"{ruleset_id}.json"

            if not filepath.exists():
                logger.warning(f"Ruleset file not found: {filepath}")
                return False

            filepath.unlink()
            logger.info(f"Deleted ruleset '{ruleset_id}'")
            return True

        except Exception as e:
            logger.error(f"Error deleting ruleset {ruleset_id}: {e}")
            return False

    def search_rulesets(
        self,
        schema_name: Optional[str] = None,
        kg_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for rulesets matching criteria.

        Args:
            schema_name: Filter by schema name
            kg_name: Filter by source knowledge graph name

        Returns:
            List of matching ruleset metadata
        """
        all_rulesets = self.list_rulesets()
        filtered = []

        for ruleset in all_rulesets:
            # Check schema filter
            if schema_name:
                schemas = ruleset.get('schemas', [])
                if schema_name not in schemas:
                    continue

            # Check KG filter
            if kg_name:
                if ruleset.get('generated_from_kg') != kg_name:
                    continue

            filtered.append(ruleset)

        logger.info(f"Found {len(filtered)} rulesets matching filters")
        return filtered

    def export_ruleset_to_sql(self, ruleset_id: str) -> Optional[str]:
        """
        Export a ruleset as SQL JOIN statements.

        Args:
            ruleset_id: ID of the ruleset to export

        Returns:
            SQL string or None if ruleset not found
        """
        ruleset = self.load_ruleset(ruleset_id)

        if not ruleset:
            return None

        sql_statements = []
        sql_statements.append(f"-- Reconciliation Rules: {ruleset.ruleset_name}")
        sql_statements.append(f"-- Generated from KG: {ruleset.generated_from_kg}")
        sql_statements.append(f"-- Schemas: {', '.join(ruleset.schemas)}")
        sql_statements.append(f"-- Total Rules: {len(ruleset.rules)}")
        sql_statements.append("")

        for i, rule in enumerate(ruleset.rules, 1):
            sql_statements.append(f"-- Rule {i}: {rule.rule_name}")
            sql_statements.append(f"-- Match Type: {rule.match_type}")
            sql_statements.append(f"-- Confidence: {rule.confidence_score:.2f}")
            sql_statements.append(f"-- Reasoning: {rule.reasoning}")

            # Generate JOIN condition
            source_cols = ', '.join([f"s.{col}" for col in rule.source_columns])
            target_cols = ', '.join([f"t.{col}" for col in rule.target_columns])

            join_conditions = []
            for src_col, tgt_col in zip(rule.source_columns, rule.target_columns):
                if rule.transformation:
                    join_conditions.append(f"{rule.transformation} = t.{tgt_col}")
                else:
                    join_conditions.append(f"s.{src_col} = t.{tgt_col}")

            join_condition = " AND ".join(join_conditions)

            sql_statements.append(f"""
SELECT {source_cols}, {target_cols}
FROM {rule.source_schema}.{rule.source_table} s
JOIN {rule.target_schema}.{rule.target_table} t
    ON {join_condition};
""")
            sql_statements.append("")

        return "\n".join(sql_statements)

    def _serialize_datetimes(self, obj: Any) -> Any:
        """Recursively convert datetime objects to ISO format strings."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {key: self._serialize_datetimes(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_datetimes(item) for item in obj]
        else:
            return obj

    def _deserialize_datetimes(self, obj: Any) -> Any:
        """Recursively convert ISO format strings to datetime objects."""
        if isinstance(obj, dict):
            # Check for datetime fields
            result = {}
            for key, value in obj.items():
                if key in ['created_at'] and isinstance(value, str):
                    try:
                        result[key] = datetime.fromisoformat(value)
                    except (ValueError, TypeError):
                        result[key] = value
                else:
                    result[key] = self._deserialize_datetimes(value)
            return result
        elif isinstance(obj, list):
            return [self._deserialize_datetimes(item) for item in obj]
        else:
            return obj


# Singleton instance
_rule_storage: Optional[ReconciliationRuleStorage] = None


def get_rule_storage() -> ReconciliationRuleStorage:
    """Get or create the singleton rule storage instance."""
    global _rule_storage
    if _rule_storage is None:
        _rule_storage = ReconciliationRuleStorage()
    return _rule_storage
