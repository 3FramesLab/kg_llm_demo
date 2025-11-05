"""
Initialize Column Hints from Existing Schema
This script generates initial hints for all tables and columns in a schema file.
"""

import json
import sys
import logging
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from kg_builder.services.hint_manager import get_hint_manager
from kg_builder.services.llm_service import get_llm_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def infer_semantic_type(column_name: str, data_type: str) -> str:
    """
    Infer semantic type from column name and data type.

    Args:
        column_name: Name of the column
        data_type: SQL data type

    Returns:
        Semantic type (identifier, measure, dimension, date, flag, description)
    """
    column_lower = column_name.lower()

    # Identifiers
    if any(term in column_lower for term in ['_id', '_uid', '_key', '_code', '_number', 'material']):
        return "identifier"

    # Dates
    if any(term in column_lower for term in ['_date', '_time', 'created', 'modified', 'updated']):
        return "date"

    # Flags/Booleans
    if any(term in column_lower for term in ['_flag', 'is_', 'has_', 'active', 'deleted']):
        return "flag"

    # Measures (numeric)
    if 'INTEGER' in data_type or 'BIGINT' in data_type or 'DECIMAL' in data_type:
        if any(term in column_lower for term in ['count', 'qty', 'quantity', 'amount', 'price', 'cost']):
            return "measure"

    # Descriptions
    if any(term in column_lower for term in ['_desc', '_name', '_text', 'description', 'comment']):
        return "description"

    # Default to dimension
    return "dimension"


def infer_role(column_name: str, primary_key: bool) -> str:
    """
    Infer column role.

    Args:
        column_name: Name of the column
        primary_key: Whether this is a primary key

    Returns:
        Role (primary_key, foreign_key, attribute)
    """
    if primary_key:
        return "primary_key"

    column_lower = column_name.lower()

    # Foreign keys
    if any(term in column_lower for term in ['_id', '_uid', '_key', '_ref']) and not column_lower.endswith('s'):
        return "foreign_key"

    return "attribute"


def generate_aliases(column_name: str) -> list:
    """
    Generate common aliases for a column name.

    Args:
        column_name: Name of the column

    Returns:
        List of aliases
    """
    aliases = []
    column_lower = column_name.lower()

    # Remove underscores and create variations
    no_underscore = column_lower.replace('_', ' ')
    if no_underscore != column_lower:
        aliases.append(no_underscore)

    # Add common variations
    if 'material' in column_lower:
        aliases.extend(['product', 'item', 'sku', 'part'])
    elif 'status' in column_lower:
        aliases.extend(['state', 'condition'])
    elif 'type' in column_lower:
        aliases.extend(['category', 'classification'])
    elif 'code' in column_lower:
        aliases.extend(['id', 'identifier'])
    elif 'name' in column_lower:
        aliases.extend(['title', 'label'])

    # Remove duplicates and limit
    return list(set(aliases))[:5]


def generate_common_terms(column_name: str, semantic_type: str) -> list:
    """
    Generate common natural language terms.

    Args:
        column_name: Name of the column
        semantic_type: Semantic type

    Returns:
        List of common terms
    """
    terms = []
    column_words = column_name.lower().replace('_', ' ').split()

    # Basic terms
    terms.extend([
        column_name.lower().replace('_', ' '),
        f"what {column_words[0]}" if column_words else "",
        f"which {column_words[0]}" if column_words else ""
    ])

    # Type-specific terms
    if semantic_type == "identifier":
        terms.extend([f"{column_words[0]} number", f"{column_words[0]} id"])
    elif semantic_type == "flag":
        terms.extend(["is active", "is deleted", "status"])

    # Remove empty strings and duplicates
    return list(filter(None, set(terms)))[:5]


def create_basic_hints(table_name: str, column_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create basic hints without LLM.

    Args:
        table_name: Name of the table
        column_info: Column information from schema

    Returns:
        Basic hints dictionary
    """
    column_name = column_info['name']
    data_type = column_info.get('type', 'UNKNOWN')
    primary_key = column_info.get('primary_key', False)

    semantic_type = infer_semantic_type(column_name, data_type)
    role = infer_role(column_name, primary_key)

    return {
        "business_name": column_name.replace('_', ' ').title(),
        "aliases": generate_aliases(column_name),
        "description": f"Column {column_name} in {table_name}",
        "semantic_type": semantic_type,
        "data_type": data_type,
        "role": role,
        "common_terms": generate_common_terms(column_name, semantic_type),
        "examples": [],
        "searchable": True,
        "filterable": True,
        "aggregatable": semantic_type in ["measure"],
        "priority": "high" if primary_key or semantic_type == "identifier" else "medium",
        "business_rules": [],
        "user_notes": "",
        "auto_generated": True,
        "manual_verified": False
    }


def create_table_hints(table_name: str) -> Dict[str, Any]:
    """
    Create basic table-level hints.

    Args:
        table_name: Name of the table

    Returns:
        Table hints dictionary
    """
    # Generate business name
    business_name = table_name.replace('_', ' ').title()

    # Extract potential aliases from table name
    aliases = []
    if 'brz_lnd_' in table_name:
        # Bronze landing table
        clean_name = table_name.replace('brz_lnd_', '')
        aliases.append(clean_name)

    parts = table_name.split('_')
    if len(parts) > 1:
        aliases.append(' '.join(parts))

    return {
        "business_name": business_name,
        "aliases": list(set(aliases))[:5],
        "description": f"Data table: {table_name}",
        "category": "unknown",
        "user_notes": "Auto-generated, needs review"
    }


def initialize_hints(
    schema_path: str,
    use_llm: bool = False,
    overwrite_existing: bool = False
):
    """
    Initialize hints from schema file.

    Args:
        schema_path: Path to schema JSON file
        use_llm: Whether to use LLM for generation
        overwrite_existing: Whether to overwrite existing hints
    """
    logger.info(f"Loading schema from: {schema_path}")

    # Load schema
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)

    hint_manager = get_hint_manager()
    llm_service = get_llm_service() if use_llm else None

    if use_llm and not llm_service.is_enabled():
        logger.warning("LLM service not available, falling back to basic hints")
        use_llm = False

    tables = schema.get('tables', {})
    total_tables = len(tables)
    total_columns = sum(len(table.get('columns', [])) for table in tables.values())

    logger.info(f"Found {total_tables} tables with {total_columns} columns")

    processed_tables = 0
    processed_columns = 0
    skipped_columns = 0

    for table_name, table_info in tables.items():
        logger.info(f"Processing table: {table_name}")

        # Add table hints
        table_hints = create_table_hints(table_name)
        hint_manager.add_table_hints(
            table_name=table_name,
            table_hints=table_hints,
            user="initialization_script"
        )
        processed_tables += 1

        # Process columns
        columns = table_info.get('columns', [])
        for column_info in columns:
            column_name = column_info['name']

            # Skip if exists and overwrite is False
            if not overwrite_existing:
                existing = hint_manager.get_column_hints(table_name, column_name)
                if existing:
                    logger.debug(f"Skipping existing: {table_name}.{column_name}")
                    skipped_columns += 1
                    continue

            # Generate hints
            if use_llm:
                try:
                    logger.info(f"  Generating LLM hints for: {column_name}")
                    result = llm_service.extract_column_hints(
                        table_name=table_name,
                        column_name=column_name,
                        column_type=column_info.get('type', 'UNKNOWN')
                    )

                    column_hints = result.get('hints', {})
                    column_hints['auto_generated'] = True
                    column_hints['data_type'] = column_info.get('type')

                except Exception as e:
                    logger.error(f"  LLM error for {column_name}: {e}, falling back to basic hints")
                    column_hints = create_basic_hints(table_name, column_info)
            else:
                logger.debug(f"  Creating basic hints for: {column_name}")
                column_hints = create_basic_hints(table_name, column_info)

            # Save hints
            hint_manager.add_column_hints(
                table_name=table_name,
                column_name=column_name,
                column_hints=column_hints,
                user="initialization_script"
            )
            processed_columns += 1

    # Create initial version
    logger.info("Creating initial version snapshot")
    hint_manager.create_version_snapshot(
        version_name="v1.0_initial",
        user="initialization_script",
        comment=f"Initial hints generated from schema. LLM: {use_llm}, Overwrite: {overwrite_existing}"
    )

    # Report statistics
    stats = hint_manager.get_statistics()
    logger.info("\n" + "=" * 60)
    logger.info("Initialization Complete")
    logger.info("=" * 60)
    logger.info(f"Tables processed: {processed_tables}/{total_tables}")
    logger.info(f"Columns processed: {processed_columns}")
    logger.info(f"Columns skipped: {skipped_columns}")
    logger.info(f"Total columns in hints: {stats['total_columns']}")
    logger.info(f"Auto-generated: {stats['auto_generated']}")
    logger.info(f"Manual verified: {stats['manual_verified']}")
    logger.info("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initialize column hints from schema")
    parser.add_argument(
        "--schema",
        default="schemas/newdqschemanov.json",
        help="Path to schema JSON file"
    )
    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="Use LLM for hint generation (requires OPENAI_API_KEY)"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing hints"
    )

    args = parser.parse_args()

    initialize_hints(
        schema_path=args.schema,
        use_llm=args.use_llm,
        overwrite_existing=args.overwrite
    )
