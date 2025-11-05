"""
Hint Manager Service for persistent column hints storage and management.
Provides CRUD operations, versioning, and LLM integration for column hints.
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)


class HintManager:
    """Manages persistent column hints with versioning and user edits."""

    def __init__(self, hints_dir: str = "schemas/hints"):
        """
        Initialize the hint manager.

        Args:
            hints_dir: Directory to store hints files
        """
        self.hints_dir = Path(hints_dir)
        self.hints_file = self.hints_dir / "column_hints.json"
        self.backup_file = self.hints_dir / "column_hints_backup.json"
        self.versions_dir = self.hints_dir / "versions"
        self.metadata_file = self.versions_dir / "metadata.json"

        # Create directories if they don't exist
        self.hints_dir.mkdir(parents=True, exist_ok=True)
        self.versions_dir.mkdir(parents=True, exist_ok=True)

        # Initialize hints structure if file doesn't exist
        if not self.hints_file.exists():
            self._initialize_hints_file()

        logger.info(f"HintManager initialized with hints directory: {self.hints_dir}")

    def _initialize_hints_file(self):
        """Initialize a new hints file with default structure."""
        default_structure = {
            "metadata": {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "updated_by": "system",
                "schema_name": "",
                "total_tables": 0,
                "total_columns": 0,
                "auto_generated": False,
                "manual_edits": 0
            },
            "tables": {},
            "global_hints": {
                "common_patterns": {
                    "_uid": "Unique identifier",
                    "_id": "Record ID",
                    "_code": "Classification code",
                    "_date": "Date field",
                    "_time": "Timestamp field"
                },
                "semantic_type_definitions": {
                    "identifier": "Unique keys, IDs, codes",
                    "measure": "Numeric values for analysis",
                    "dimension": "Categorical attributes",
                    "date": "Temporal fields",
                    "flag": "Boolean/status indicators",
                    "description": "Text descriptions"
                }
            }
        }

        self._save_hints(default_structure)
        logger.info("Initialized new hints file")

    def load_hints(self) -> Dict[str, Any]:
        """Load hints from file."""
        try:
            with open(self.hints_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading hints: {e}")
            return self._get_empty_hints_structure()

    def _save_hints(self, hints: Dict[str, Any], create_backup: bool = True):
        """
        Save hints to file with optional backup.

        Args:
            hints: Hints dictionary to save
            create_backup: Whether to create a backup before saving
        """
        try:
            # Create backup if requested and file exists
            if create_backup and self.hints_file.exists():
                shutil.copy2(self.hints_file, self.backup_file)
                logger.debug("Created backup of hints file")

            # Update metadata
            hints['metadata']['last_updated'] = datetime.now().isoformat()

            # Save to file
            with open(self.hints_file, 'w', encoding='utf-8') as f:
                json.dump(hints, f, indent=2, ensure_ascii=False)

            logger.info("Hints saved successfully")

        except Exception as e:
            logger.error(f"Error saving hints: {e}")
            raise

    def create_version_snapshot(self, version_name: str, user: str, comment: str = ""):
        """
        Create a versioned snapshot of current hints.

        Args:
            version_name: Name/identifier for this version
            user: User creating the version
            comment: Optional comment about changes
        """
        try:
            hints = self.load_hints()
            version_file = self.versions_dir / f"column_hints_{version_name}.json"

            # Save version
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(hints, f, indent=2, ensure_ascii=False)

            # Update version metadata
            self._update_version_metadata(version_name, user, comment)

            logger.info(f"Created version snapshot: {version_name}")

        except Exception as e:
            logger.error(f"Error creating version snapshot: {e}")
            raise

    def _update_version_metadata(self, version_name: str, user: str, comment: str):
        """Update version tracking metadata."""
        metadata = {}
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

        if 'versions' not in metadata:
            metadata['versions'] = []

        metadata['versions'].append({
            "version_name": version_name,
            "created_at": datetime.now().isoformat(),
            "created_by": user,
            "comment": comment
        })

        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def get_table_hints(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get hints for a specific table."""
        hints = self.load_hints()
        return hints.get('tables', {}).get(table_name)

    def get_column_hints(self, table_name: str, column_name: str) -> Optional[Dict[str, Any]]:
        """Get hints for a specific column."""
        table_hints = self.get_table_hints(table_name)
        if table_hints:
            return table_hints.get('columns', {}).get(column_name)
        return None

    def add_table_hints(self, table_name: str, table_hints: Dict[str, Any], user: str = "system"):
        """
        Add or update hints for a table.

        Args:
            table_name: Name of the table
            table_hints: Table-level hints dictionary
            user: User making the change
        """
        hints = self.load_hints()

        if 'tables' not in hints:
            hints['tables'] = {}

        # Add audit info
        table_hints['last_edited_by'] = user
        table_hints['last_edited_at'] = datetime.now().isoformat()

        hints['tables'][table_name] = {
            'table_hints': table_hints,
            'columns': hints['tables'].get(table_name, {}).get('columns', {})
        }

        hints['metadata']['updated_by'] = user
        hints['metadata']['total_tables'] = len(hints['tables'])

        self._save_hints(hints)
        logger.info(f"Added/updated table hints for: {table_name}")

    def add_column_hints(
        self,
        table_name: str,
        column_name: str,
        column_hints: Dict[str, Any],
        user: str = "system"
    ):
        """
        Add or update hints for a column.

        Args:
            table_name: Name of the table
            column_name: Name of the column
            column_hints: Column hints dictionary
            user: User making the change
        """
        hints = self.load_hints()

        # Ensure table structure exists
        if 'tables' not in hints:
            hints['tables'] = {}
        if table_name not in hints['tables']:
            hints['tables'][table_name] = {'table_hints': {}, 'columns': {}}
        if 'columns' not in hints['tables'][table_name]:
            hints['tables'][table_name]['columns'] = {}

        # Add audit info
        column_hints['last_edited_by'] = user
        column_hints['last_edited_at'] = datetime.now().isoformat()

        hints['tables'][table_name]['columns'][column_name] = column_hints

        # Update metadata
        hints['metadata']['updated_by'] = user
        total_columns = sum(
            len(table.get('columns', {}))
            for table in hints['tables'].values()
        )
        hints['metadata']['total_columns'] = total_columns

        # Track manual edits
        if not column_hints.get('auto_generated', False):
            hints['metadata']['manual_edits'] = hints['metadata'].get('manual_edits', 0) + 1

        self._save_hints(hints)
        logger.info(f"Added/updated column hints for: {table_name}.{column_name}")

    def update_column_hint_field(
        self,
        table_name: str,
        column_name: str,
        field_name: str,
        field_value: Any,
        user: str = "system"
    ):
        """
        Update a specific field in column hints.

        Args:
            table_name: Name of the table
            column_name: Name of the column
            field_name: Field to update (e.g., 'business_name', 'aliases')
            field_value: New value for the field
            user: User making the change
        """
        column_hints = self.get_column_hints(table_name, column_name)

        if column_hints is None:
            logger.warning(f"Column {table_name}.{column_name} not found, creating new hints")
            column_hints = {}

        column_hints[field_name] = field_value
        column_hints['manual_verified'] = True

        self.add_column_hints(table_name, column_name, column_hints, user)
        logger.info(f"Updated {field_name} for {table_name}.{column_name}")

    def delete_column_hints(self, table_name: str, column_name: str, user: str = "system"):
        """Delete hints for a specific column."""
        hints = self.load_hints()

        if table_name in hints.get('tables', {}):
            if column_name in hints['tables'][table_name].get('columns', {}):
                del hints['tables'][table_name]['columns'][column_name]
                hints['metadata']['updated_by'] = user
                self._save_hints(hints)
                logger.info(f"Deleted column hints for: {table_name}.{column_name}")
                return True

        logger.warning(f"Column hints not found: {table_name}.{column_name}")
        return False

    def delete_table_hints(self, table_name: str, user: str = "system"):
        """Delete hints for an entire table."""
        hints = self.load_hints()

        if table_name in hints.get('tables', {}):
            del hints['tables'][table_name]
            hints['metadata']['updated_by'] = user
            hints['metadata']['total_tables'] = len(hints['tables'])
            self._save_hints(hints)
            logger.info(f"Deleted table hints for: {table_name}")
            return True

        logger.warning(f"Table hints not found: {table_name}")
        return False

    def search_hints(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for columns by business name, aliases, or common terms.

        Args:
            search_term: Term to search for

        Returns:
            List of matching columns with their hints
        """
        hints = self.load_hints()
        results = []
        search_lower = search_term.lower()

        for table_name, table_data in hints.get('tables', {}).items():
            for column_name, column_hints in table_data.get('columns', {}).items():
                # Search in business name
                if search_lower in column_hints.get('business_name', '').lower():
                    results.append({
                        'table_name': table_name,
                        'column_name': column_name,
                        'hints': column_hints,
                        'match_type': 'business_name'
                    })
                    continue

                # Search in aliases
                aliases = column_hints.get('aliases', [])
                if any(search_lower in alias.lower() for alias in aliases):
                    results.append({
                        'table_name': table_name,
                        'column_name': column_name,
                        'hints': column_hints,
                        'match_type': 'alias'
                    })
                    continue

                # Search in common terms
                common_terms = column_hints.get('common_terms', [])
                if any(search_lower in term.lower() for term in common_terms):
                    results.append({
                        'table_name': table_name,
                        'column_name': column_name,
                        'hints': column_hints,
                        'match_type': 'common_term'
                    })

        return results

    def export_hints(self, output_path: str):
        """Export hints to a different file."""
        hints = self.load_hints()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(hints, f, indent=2, ensure_ascii=False)
        logger.info(f"Exported hints to: {output_path}")

    def import_hints(self, input_path: str, merge: bool = False, user: str = "system"):
        """
        Import hints from a file.

        Args:
            input_path: Path to hints file to import
            merge: If True, merge with existing hints; if False, replace
            user: User performing the import
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            imported_hints = json.load(f)

        if merge:
            existing_hints = self.load_hints()
            # Merge tables
            for table_name, table_data in imported_hints.get('tables', {}).items():
                if table_name not in existing_hints['tables']:
                    existing_hints['tables'][table_name] = table_data
                else:
                    # Merge columns
                    existing_hints['tables'][table_name]['columns'].update(
                        table_data.get('columns', {})
                    )

            existing_hints['metadata']['updated_by'] = user
            self._save_hints(existing_hints)
            logger.info(f"Merged hints from: {input_path}")
        else:
            imported_hints['metadata']['updated_by'] = user
            self._save_hints(imported_hints)
            logger.info(f"Replaced hints from: {input_path}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the hints dictionary."""
        hints = self.load_hints()

        total_columns = 0
        auto_generated_count = 0
        manual_verified_count = 0
        priority_high_count = 0

        for table_data in hints.get('tables', {}).values():
            for column_hints in table_data.get('columns', {}).values():
                total_columns += 1
                if column_hints.get('auto_generated', False):
                    auto_generated_count += 1
                if column_hints.get('manual_verified', False):
                    manual_verified_count += 1
                if column_hints.get('priority') == 'high':
                    priority_high_count += 1

        return {
            'total_tables': len(hints.get('tables', {})),
            'total_columns': total_columns,
            'auto_generated': auto_generated_count,
            'manual_verified': manual_verified_count,
            'priority_high': priority_high_count,
            'last_updated': hints['metadata'].get('last_updated'),
            'updated_by': hints['metadata'].get('updated_by'),
            'manual_edits': hints['metadata'].get('manual_edits', 0)
        }

    def _get_empty_hints_structure(self) -> Dict[str, Any]:
        """Return empty hints structure."""
        return {
            "metadata": {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "updated_by": "system",
                "total_tables": 0,
                "total_columns": 0
            },
            "tables": {},
            "global_hints": {}
        }


# Global instance
_hint_manager: Optional[HintManager] = None


def get_hint_manager(hints_dir: str = "schemas/hints") -> HintManager:
    """Get or create hint manager instance."""
    global _hint_manager
    if _hint_manager is None:
        _hint_manager = HintManager(hints_dir)
    return _hint_manager
