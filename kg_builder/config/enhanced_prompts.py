"""
Enhanced LLM prompts configuration for comprehensive relationship detection.
"""

from typing import Dict, List, Any

class EnhancedPromptConfig:
    """Configuration for enhanced LLM prompts."""
    
    # Additional relationship types to detect
    ENHANCED_RELATIONSHIP_TYPES = [
        "REFERENCES",
        "HAS", 
        "BELONGS_TO",
        "CONTAINS",
        "ASSOCIATES_WITH",
        "INHERITS_FROM",
        "TRACKS",
        "SEMANTIC_REFERENCE",
        "BUSINESS_LOGIC",
        "HIERARCHICAL",
        "TEMPORAL",
        "LOOKUP"
    ]
    
    # Business domain patterns to look for
    BUSINESS_DOMAIN_PATTERNS = {
        "material_management": [
            "material", "product", "item", "sku", "part", "component",
            "material_master", "product_master", "item_master"
        ],
        "organizational": [
            "company", "division", "department", "business_unit", "plant",
            "organization", "org_unit", "cost_center"
        ],
        "geographic": [
            "country", "region", "state", "city", "location", "address",
            "postal_code", "zip_code", "territory"
        ],
        "temporal": [
            "created", "modified", "updated", "deleted", "effective", "expiry",
            "start_date", "end_date", "valid_from", "valid_to"
        ],
        "financial": [
            "currency", "amount", "price", "cost", "value", "rate",
            "budget", "forecast", "actual"
        ]
    }
    
    # Naming convention patterns
    NAMING_PATTERNS = {
        "identifiers": ["_id", "_uid", "_key", "_code", "_number", "_ref", "_pk"],
        "foreign_keys": ["_fk", "_foreign_key", "_reference", "_ref_id"],
        "audit_fields": ["created_by", "modified_by", "updated_by", "deleted_by"],
        "timestamps": ["created_at", "modified_at", "updated_at", "deleted_at", 
                      "created_date", "modified_date", "updated_date"],
        "status_fields": ["status", "state", "flag", "indicator", "active", "enabled"]
    }
    
    # Data type compatibility rules
    DATA_TYPE_COMPATIBILITY = {
        "string_types": ["VARCHAR", "NVARCHAR", "CHAR", "NCHAR", "TEXT", "NTEXT"],
        "integer_types": ["INT", "INTEGER", "BIGINT", "SMALLINT", "TINYINT"],
        "decimal_types": ["DECIMAL", "NUMERIC", "FLOAT", "REAL", "MONEY"],
        "date_types": ["DATE", "DATETIME", "DATETIME2", "TIMESTAMP", "TIME"],
        "binary_types": ["BINARY", "VARBINARY", "IMAGE", "BLOB"]
    }

def get_enhanced_relationship_detection_prompt() -> str:
    """Get enhanced prompt for comprehensive relationship detection."""
    return """
=== COMPREHENSIVE RELATIONSHIP DETECTION STRATEGY ===

**PRIORITY ORDER:**
1. Explicit structural relationships (FK constraints)
2. Implicit structural relationships (naming patterns)
3. Business logic relationships (domain knowledge)
4. Semantic relationships (meaning similarity)
5. Temporal relationships (time-based connections)

**DETECTION TECHNIQUES:**

**A. Pattern-Based Detection:**
- ID patterns: _id, _uid, _key, _code, _number, _ref
- FK patterns: table_name + _id (e.g., customer_id → customers)
- Audit patterns: created_by, modified_by, created_date, modified_date
- Status patterns: status, state, flag, active, enabled

**B. Business Domain Analysis:**
- Master data patterns: *_master, *_reference, *_lookup
- Transactional patterns: *_transaction, *_detail, *_line
- Hierarchical patterns: parent_*, child_*, *_hierarchy
- Categorical patterns: *_type, *_category, *_group, *_class

**C. Semantic Analysis:**
- Business synonyms: Material = Product = Item = SKU
- Functional equivalence: ID = UID = Key = Code (for identifiers)
- Contextual similarity: Customer = Client = Account
- Domain-specific terms: analyze within business context

**D. Cross-Schema Integration:**
- ETL patterns: source → staging → warehouse → mart
- System boundaries: ERP ↔ CRM ↔ Analytics
- Data flow: raw → processed → aggregated → reported
- Master data: local → global → standardized

**E. Temporal Analysis:**
- Lifecycle tracking: created → modified → deleted
- Event sequences: order → shipment → delivery → invoice
- Version control: version_number, effective_date, expiry_date
- Audit trails: who, what, when, where

**CONFIDENCE SCORING:**
- 0.95+: Exact name match + compatible types
- 0.85-0.94: Strong semantic match + compatible types
- 0.75-0.84: Business logic match + compatible types
- 0.70-0.74: Pattern match + compatible types
- <0.70: Insufficient evidence (exclude)
"""

def get_business_context_examples() -> Dict[str, List[str]]:
    """Get business context examples for different domains."""
    return {
        "manufacturing": [
            "Material Master contains product specifications",
            "BOM (Bill of Materials) references Material Master",
            "Production Orders consume Materials",
            "Quality Control tracks Material batches"
        ],
        "supply_chain": [
            "Vendors supply Materials",
            "Purchase Orders reference Materials and Vendors", 
            "Inventory tracks Material quantities",
            "Shipments contain Materials"
        ],
        "sales": [
            "Customers place Orders",
            "Orders contain Order Items",
            "Order Items reference Products/Materials",
            "Invoices are generated from Orders"
        ],
        "finance": [
            "Cost Centers track expenses",
            "GL Accounts categorize transactions",
            "Budgets are allocated to Cost Centers",
            "Actuals are compared to Budgets"
        ]
    }

def get_enhanced_prompt_instructions() -> str:
    """Get instructions for using enhanced prompts."""
    return """
=== ENHANCED RELATIONSHIP DETECTION INSTRUCTIONS ===

**STEP 1: Structural Analysis**
- Scan for explicit foreign key constraints
- Identify naming pattern relationships (_id, _uid, _key)
- Map table names to column names (customer_id → customers)

**STEP 2: Business Domain Analysis** 
- Analyze table purposes (master data vs transactional)
- Identify business process flows
- Look for hierarchical structures

**STEP 3: Semantic Analysis**
- Match business concepts across naming variations
- Identify synonyms within business context
- Consider domain-specific terminology

**STEP 4: Cross-Schema Integration**
- Look for ETL and data flow patterns
- Identify system integration points
- Consider data lineage relationships

**STEP 5: Validation**
- Verify data type compatibility
- Check field length compatibility
- Ensure business logic makes sense
- Assign appropriate confidence scores

**OUTPUT REQUIREMENTS:**
- Include ALL relationship types found
- Provide clear business reasoning
- Assign confidence scores based on evidence strength
- Include data type compatibility information
"""
