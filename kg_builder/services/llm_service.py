"""
LLM Service for intelligent entity and relationship extraction using OpenAI.
"""
import json
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI, APIError

from kg_builder.config import (
    OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, 
    OPENAI_MAX_TOKENS, ENABLE_LLM_EXTRACTION
)

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM-based intelligent extraction."""
    
    def __init__(self):
        """Initialize LLM service with OpenAI client."""
        self.enabled = ENABLE_LLM_EXTRACTION and bool(OPENAI_API_KEY)
        self.client = None
        self.model = OPENAI_MODEL
        self.temperature = OPENAI_TEMPERATURE
        self.max_tokens = OPENAI_MAX_TOKENS
        self._use_max_completion_tokens = None  # Auto-detect on first use

        if self.enabled:
            try:
                self.client = OpenAI(api_key=OPENAI_API_KEY)
                logger.info(f"LLM Service initialized with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.enabled = False
        else:
            logger.warning("LLM Service disabled: OPENAI_API_KEY not set or LLM extraction disabled")

    def is_enabled(self) -> bool:
        """Check if LLM service is enabled and available."""
        return self.enabled

    def create_chat_completion(self, messages: List[Dict], max_tokens: Optional[int] = None, **kwargs):
        """
        Create a chat completion with automatic parameter adaptation for different OpenAI model versions.

        Args:
            messages: Chat messages
            max_tokens: Maximum tokens (optional, uses default if not provided)
            **kwargs: Additional parameters for the API call

        Returns:
            OpenAI chat completion response
        """
        if max_tokens is None:
            max_tokens = self.max_tokens

        # Auto-detect which parameter to use on first call
        if self._use_max_completion_tokens is None:
            try:
                # Try with max_completion_tokens (newer models)
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_completion_tokens=max_tokens,
                    messages=messages,
                    **kwargs
                )
                self._use_max_completion_tokens = True
                logger.debug("Using max_completion_tokens parameter for OpenAI API")
                return response
            except Exception as e:
                if "max_completion_tokens" in str(e) or "unsupported_parameter" in str(e):
                    # Fall back to max_tokens (older models)
                    self._use_max_completion_tokens = False
                    logger.debug("Falling back to max_tokens parameter for OpenAI API")
                else:
                    raise

        # Use the detected parameter
        if self._use_max_completion_tokens:
            return self.client.chat.completions.create(
                model=self.model,
                max_completion_tokens=max_tokens,
                messages=messages,
                **kwargs
            )
        else:
            return self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=messages,
                **kwargs
            )
    
    def extract_entities(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to intelligently extract entities from schema.
        
        Args:
            schema: Database schema dictionary
            
        Returns:
            Dictionary with extracted entities and their descriptions
        """
        if not self.enabled:
            logger.warning("LLM extraction disabled, returning empty result")
            return {"entities": [], "descriptions": {}}
        
        try:
            schema_str = json.dumps(schema, indent=2)
            
            prompt = f"""You are a database schema analyst extracting business entities from technical database schemas.

=== OBJECTIVE ===
Analyze the database schema and identify key business entities (tables) with their purposes and characteristics.

=== SCHEMA ===
{schema_str}

=== ENTITY CLASSIFICATION ===

**Master Data**: Core business entities that are relatively static
- Examples: Customers, Products, Vendors, Employees, Locations
- Characteristics: Low change frequency, referenced by many tables

**Transaction Data**: Records of business events/activities
- Examples: Orders, Invoices, Payments, Shipments
- Characteristics: High volume, time-stamped, immutable after creation

**Reference Data**: Lookup tables, codes, classifications
- Examples: Status codes, Categories, Types, Countries
- Characteristics: Small, stable, used for validation/classification

**Audit/Log Data**: System tracking and history
- Examples: Audit logs, Change history, User activity
- Characteristics: Append-only, timestamps, user tracking

**Junction/Bridge Data**: Many-to-many relationship tables
- Examples: Order_Items, User_Roles, Product_Categories
- Characteristics: Composite keys, links two entities

=== ANALYSIS GUIDELINES ===
- Identify the business purpose of each table
- Classify entity type based on characteristics above
- List key attributes (primary keys, foreign keys, unique identifiers, important business fields)
- Note any data quality concerns (nullable important fields, missing constraints)
- Consider relationships to other entities

=== OUTPUT FORMAT (JSON) ===
{{{{
    "entities": [
        {{{{
            "name": "catalog",
            "purpose": "Stores product catalog information including pricing, vendor details, and product specifications",
            "type": "Master Data",
            "key_attributes": ["id", "uuid", "code", "vendor_uid", "tenant_uid", "price"],
            "description": "Central product catalog table. Contains 142 columns covering product details, pricing, vendor relationships, and inventory. Tenant-scoped with soft delete support.",
            "primary_keys": ["id"],
            "unique_identifiers": ["uuid", "code"],
            "foreign_key_references": ["vendor_uid", "tenant_uid", "sub_cat_uid"],
            "data_quality_notes": "Large table with many nullable fields. Consider data completeness validation."
        }}}}
    ]
}}}}

Return ONLY valid JSON, no additional text.
"""

            logger.debug(f"Entity Extraction Prompt:\\n{prompt}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a database schema analyst. Extract entities and their business purposes from database schemas. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            result_text = response.choices[0].message.content
            logger.debug(f"LLM Entity Extraction Response:\n{result_text}")

            result = json.loads(result_text)

            logger.info(f"LLM extracted {len(result.get('entities', []))} entities")
            return result
            
        except APIError as e:
            logger.error(f"OpenAI API error during entity extraction: {e}")
            return {"entities": [], "descriptions": {}, "error": str(e)}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return {"entities": [], "descriptions": {}, "error": "Invalid JSON response"}
        except Exception as e:
            logger.error(f"Error during LLM entity extraction: {e}")
            return {"entities": [], "descriptions": {}, "error": str(e)}
    
    def extract_relationships(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to intelligently extract relationships from schema.
        
        Args:
            schema: Database schema dictionary
            
        Returns:
            Dictionary with extracted relationships
        """
        if not self.enabled:
            logger.warning("LLM extraction disabled, returning empty result")
            return {"relationships": []}
        
        try:
            schema_str = json.dumps(schema, indent=2)
            
            prompt = f"""You are a database schema analyst extracting relationships between entities in a database schema.

=== OBJECTIVE ===
Identify all relationships between tables, including explicit foreign keys and implicit semantic relationships.

=== SCHEMA ===
{schema_str}

=== RELATIONSHIP TYPES ===

**REFERENCES**: Foreign key relationship (explicit or implicit)
- Example: orders.customer_id references customers.id
- Pattern: Column with _id, _uid, _key suffix

**HAS**: Ownership/containment (one-to-many)
- Example: Customer HAS Orders
- Pattern: Parent entity contains child entities

**BELONGS_TO**: Inverse of HAS (many-to-one)
- Example: Order BELONGS_TO Customer
- Pattern: Child entity belongs to parent

**CONTAINS**: Composition relationship
- Example: Order CONTAINS Order_Items
- Pattern: Strong ownership, child can't exist without parent

**ASSOCIATES_WITH**: Many-to-many relationship
- Example: Products ASSOCIATES_WITH Categories (via junction table)
- Pattern: Junction/bridge table with two foreign keys

**INHERITS_FROM**: Hierarchical relationship
- Example: Sub_Category INHERITS_FROM Category
- Pattern: Self-referencing or parent-child hierarchy

**TRACKS**: Audit/history relationship
- Example: Audit_Log TRACKS Entity_Changes
- Pattern: Temporal tracking, timestamps

=== CARDINALITY NOTATION ===
- **1:1** (One-to-One): Each record in A relates to exactly one record in B
- **1:N** (One-to-Many): Each record in A relates to multiple records in B
- **N:1** (Many-to-One): Multiple records in A relate to one record in B
- **N:N** (Many-to-Many): Multiple records in A relate to multiple records in B (requires junction table)

=== DETECTION GUIDELINES ===
- Look for explicit foreign key constraints
- Identify columns with naming patterns: _id, _uid, _key, _code
- Match column names to table names (e.g., customer_id references customers table)
- Consider data types (foreign keys usually match primary key types)
- Identify junction tables (tables with multiple foreign keys, composite primary keys)
- Note self-referencing relationships (parent_id in same table)

=== OUTPUT FORMAT (JSON) ===
{{{{
    "relationships": [
        {{{{
            "source": "catalog",
            "target": "vendors",
            "type": "REFERENCES",
            "cardinality": "N:1",
            "description": "Each catalog item is supplied by one vendor. Enables vendor performance tracking and supply chain management.",
            "foreign_key": "vendor_uid",
            "confidence": 0.95,
            "detection_method": "foreign_key_pattern"
        }}}},
        {{{{
            "source": "orders",
            "target": "customers",
            "type": "BELONGS_TO",
            "cardinality": "N:1",
            "description": "Each order belongs to one customer. Supports customer order history and analytics.",
            "foreign_key": "customer_id",
            "confidence": 0.98,
            "detection_method": "explicit_foreign_key"
        }}}}
    ]
}}}}

Return ONLY valid JSON, no additional text.
"""

            logger.debug(f"Relationship Extraction Prompt:\\n{prompt}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a database schema analyst. Extract relationships between entities from database schemas. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            result_text = response.choices[0].message.content
            logger.debug(f"LLM Relationship Extraction Response:\n{result_text}")

            result = json.loads(result_text)

            logger.info(f"LLM extracted {len(result.get('relationships', []))} relationships")
            return result
            
        except APIError as e:
            logger.error(f"OpenAI API error during relationship extraction: {e}")
            return {"relationships": [], "error": str(e)}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return {"relationships": [], "error": "Invalid JSON response"}
        except Exception as e:
            logger.error(f"Error during LLM relationship extraction: {e}")
            return {"relationships": [], "error": str(e)}
    
    def analyze_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to provide comprehensive schema analysis.
        
        Args:
            schema: Database schema dictionary
            
        Returns:
            Dictionary with schema analysis
        """
        if not self.enabled:
            logger.warning("LLM analysis disabled, returning empty result")
            return {"analysis": {}}
        
        try:
            schema_str = json.dumps(schema, indent=2)
            
            prompt = f"""Provide a comprehensive analysis of this database schema.

Schema:
{schema_str}

Analyze:
1. Overall purpose and domain
2. Data model patterns
3. Key entities and their roles
4. Data relationships and dependencies
5. Potential business logic
6. Data quality considerations

Return as JSON with this structure:
{{
    "domain": "business domain",
    "purpose": "overall purpose",
    "patterns": ["pattern1", "pattern2"],
    "key_entities": ["entity1", "entity2"],
    "data_flow": "description of data flow",
    "business_logic": "inferred business logic",
    "quality_notes": "data quality considerations"
}}"""

            logger.debug(f"Schema Analysis Prompt:\n{prompt}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a database architect. Analyze database schemas and provide insights about their structure, purpose, and business logic. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            result_text = response.choices[0].message.content
            logger.debug(f"LLM Schema Analysis Response:\n{result_text}")

            result = json.loads(result_text)

            logger.info("LLM schema analysis completed")
            return result
            
        except APIError as e:
            logger.error(f"OpenAI API error during schema analysis: {e}")
            return {"analysis": {}, "error": str(e)}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return {"analysis": {}, "error": "Invalid JSON response"}
        except Exception as e:
            logger.error(f"Error during LLM schema analysis: {e}")
            return {"analysis": {}, "error": str(e)}

    def extract_table_aliases(self, table_name: str, table_description: str, columns: List[str]) -> Dict[str, Any]:
        """
        Extract business-friendly names/aliases for a database table using LLM.

        Args:
            table_name: Actual database table name (e.g., 'brz_lnd_RBP_GPU')
            table_description: Description of what the table contains
            columns: List of column names in the table

        Returns:
            Dictionary with table_name and suggested aliases
        """
        if not self.enabled:
            logger.warning("LLM service disabled, cannot extract table aliases")
            return {"table_name": table_name, "aliases": [], "error": "LLM service disabled"}

        try:
            # Prepare the prompt
            columns_str = ", ".join(columns[:10])  # Show first 10 columns
            if len(columns) > 10:
                columns_str += f", ... ({len(columns) - 10} more)"

            prompt = f"""Analyze this database table and suggest 2-4 short, business-friendly names/aliases that users might use to refer to this table.

Table Name: {table_name}
Description: {table_description}
Columns: {columns_str}

Suggest short business names (1-3 words each) that capture the essence of this table. For example:
- If table is 'brz_lnd_RBP_GPU', suggest: ['RBP', 'RBP GPU', 'GPU']
- If table is 'brz_lnd_OPS_EXCEL_GPU', suggest: ['OPS', 'OPS Excel', 'Excel GPU']

Return ONLY valid JSON with this structure (no other text):
{{
    "table_name": "{table_name}",
    "aliases": ["alias1", "alias2", "alias3"],
    "reasoning": "Brief explanation of why these aliases make sense"
}}"""

            logger.info(f"Extracting aliases for table: {table_name}")

            response = self.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a database expert. Suggest business-friendly names for database tables. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=200
            )

            result_text = response.choices[0].message.content
            logger.info(f"📝 LLM Raw Response for table '{table_name}':\n{result_text}")

            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if not json_match:
                logger.warning(f"❌ No JSON found in LLM response for table {table_name}")
                logger.warning(f"Response was: {result_text[:200]}")
                return {"table_name": table_name, "aliases": [], "error": "No JSON in response"}

            result = json.loads(json_match.group())
            logger.info(f"✅ Successfully extracted aliases for {table_name}: {result.get('aliases', [])}")
            logger.info(f"   Reasoning: {result.get('reasoning', 'N/A')}")
            return result

        except APIError as e:
            logger.error(f"OpenAI API error during alias extraction: {e}")
            return {"table_name": table_name, "aliases": [], "error": str(e)}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return {"table_name": table_name, "aliases": [], "error": "Invalid JSON response"}
        except Exception as e:
            logger.error(f"Error during table alias extraction: {e}")
            return {"table_name": table_name, "aliases": [], "error": str(e)}

    def suggest_related_tables(self, source_table: str, source_columns: List[str], available_tables: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Suggest which tables might be related to a source table based on schema analysis.

        Args:
            source_table: The source table name
            source_columns: List of column names in the source table
            available_tables: Dictionary mapping table names to their column lists

        Returns:
            Dictionary with suggested relationships including target tables and likely columns
        """
        if not self.enabled:
            logger.warning("LLM service disabled, cannot suggest related tables")
            return {"source_table": source_table, "suggestions": [], "error": "LLM service disabled"}

        try:
            # Prepare the prompt with available tables
            source_cols_str = ", ".join(source_columns[:15])
            if len(source_columns) > 15:
                source_cols_str += f", ... ({len(source_columns) - 15} more)"

            # Format available tables
            tables_info = []
            for table_name, columns in available_tables.items():
                if table_name != source_table:  # Exclude the source table itself
                    cols_preview = ", ".join(columns[:10])
                    if len(columns) > 10:
                        cols_preview += f", ... ({len(columns) - 10} more)"
                    tables_info.append(f"- {table_name}: [{cols_preview}]")

            tables_str = "\n".join(tables_info[:20])  # Limit to 20 tables
            if len(tables_info) > 20:
                tables_str += f"\n... and {len(tables_info) - 20} more tables"

            prompt = f"""Analyze the source table and suggest which of the available tables are likely to have relationships with it.

Source Table: {source_table}
Source Columns: [{source_cols_str}]

Available Tables:
{tables_str}

Based on the column names, suggest up to 5 tables that are most likely related to the source table. For each suggestion, identify:
1. The target table name
2. The most likely source column for the relationship
3. The most likely target column for the relationship
4. The relationship type (e.g., "MATCHES", "REFERENCES", "LINKS_TO")
5. Confidence score (0.0 to 1.0)

Return ONLY valid JSON with this structure (no other text):
{{
    "source_table": "{source_table}",
    "suggestions": [
        {{
            "target_table": "table_name",
            "source_column": "column_name",
            "target_column": "column_name",
            "relationship_type": "MATCHES",
            "confidence": 0.95,
            "reasoning": "Brief explanation"
        }}
    ]
}}

Focus on columns that look like foreign keys, IDs, or matching fields (e.g., Material, SKU, Product_ID, etc.)."""

            logger.info(f"Suggesting related tables for: {source_table}")

            response = self.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a database relationship expert. Analyze table schemas and suggest likely relationships based on column names and patterns. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000
            )

            result_text = response.choices[0].message.content
            logger.info(f"📝 LLM Raw Response for table suggestions:\n{result_text}")

            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if not json_match:
                logger.warning(f"❌ No JSON found in LLM response")
                return {"source_table": source_table, "suggestions": [], "error": "No JSON in response"}

            result = json.loads(json_match.group())
            logger.info(f"✅ Successfully suggested {len(result.get('suggestions', []))} related tables for {source_table}")
            return result

        except APIError as e:
            logger.error(f"OpenAI API error during relationship suggestion: {e}")
            return {"source_table": source_table, "suggestions": [], "error": str(e)}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return {"source_table": source_table, "suggestions": [], "error": "Invalid JSON response"}
        except Exception as e:
            logger.error(f"Error during relationship suggestion: {e}")
            return {"source_table": source_table, "suggestions": [], "error": str(e)}


# Global LLM service instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

