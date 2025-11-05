# Enhanced LLM Prompts Guide

## 🎯 Overview

This guide explains how to enhance LLM prompts to detect more comprehensive relationship types beyond just `SEMANTIC_REFERENCE`. The enhanced prompts help the LLM look into multiple aspects of database relationships.

## 🔍 Why Only SEMANTIC_REFERENCE Before?

Your original results showed only `SEMANTIC_REFERENCE` relationships because:

1. **No Explicit Foreign Keys**: Your schema lacks explicit FK constraints
2. **Limited Naming Patterns**: Columns don't follow `_id`, `_uid` conventions
3. **Basic Prompts**: Original prompts focused mainly on semantic similarity
4. **Missing Business Context**: LLM wasn't guided to consider business relationships

## 🚀 Enhanced Prompt Strategy

### **1. Multi-Dimensional Analysis**

The enhanced prompts now instruct the LLM to analyze:

```
**A. Structural Patterns:**
- ID patterns: _id, _uid, _key, _code, _number, _ref
- FK patterns: table_name + _id (e.g., customer_id → customers)
- Audit patterns: created_by, modified_by, created_date, modified_date

**B. Business Domain Analysis:**
- Master data patterns: *_master, *_reference, *_lookup
- Transactional patterns: *_transaction, *_detail, *_line
- Hierarchical patterns: parent_*, child_*, *_hierarchy

**C. Semantic Analysis:**
- Business synonyms: Material = Product = Item = SKU
- Functional equivalence: ID = UID = Key = Code
- Contextual similarity: Customer = Client = Account
```

### **2. Relationship Type Expansion**

Enhanced prompts detect **12 relationship types** instead of just semantic ones:

| Type | Description | Example |
|------|-------------|---------|
| `REFERENCES` | Implicit foreign keys | `material_number` ↔ `materials.number` |
| `HAS` | One-to-many ownership | `Customer HAS Orders` |
| `BELONGS_TO` | Many-to-one membership | `Product BELONGS_TO Category` |
| `CONTAINS` | Composition | `Order CONTAINS Order_Items` |
| `ASSOCIATES_WITH` | Many-to-many | `Products ASSOCIATES_WITH Categories` |
| `INHERITS_FROM` | Hierarchical | `Sub_Category INHERITS_FROM Category` |
| `TRACKS` | Audit/history | `Audit_Log TRACKS Entity_Changes` |
| `SEMANTIC_REFERENCE` | Same concept, different names | `Material` ↔ `Product` |
| `BUSINESS_LOGIC` | Business rules | `order.product_code` ↔ `catalog.code` |
| `HIERARCHICAL` | Parent-child | `category_uid` ↔ `sub_cat_uid` |
| `TEMPORAL` | Time-based | `created_time` ↔ `order_date` |
| `LOOKUP` | Master data | `status_code` ↔ `status_master.code` |

### **3. Business Context Integration**

Enhanced prompts include business context:

```
**Manufacturing/Supply Chain Context:**
- Material Master tables contain product specifications
- BOM (Bill of Materials) references materials and components
- Production orders consume materials and produce finished goods

**Sales/Customer Context:**
- Customer master data drives sales transactions
- Orders contain multiple line items referencing products
- Pricing tables link products to customer-specific prices
```

## 🛠️ How to Use Enhanced Prompts

### **Method 1: API Configuration**

```python
# Enhanced KG generation
payload = {
    "schema_names": ["newdqschemanov"],
    "kg_name": "enhanced_kg",
    "use_llm_enhancement": True,
    "field_preferences": [
        {
            "source_table": "hana_material_master",
            "source_column": "MATERIAL",
            "target_table": "brz_lnd_RBP_GPU",
            "target_column": "Material",
            "priority": "high",
            "relationship_hint": "REFERENCES - Material master data relationship"
        }
    ]
}
```

### **Method 2: Natural Language Relationships**

```python
# Add business context via NL relationships
POST /api/v1/kg/relationships/natural-language
{
    "definitions": [
        "Material Master contains product specifications",
        "RBP GPU references Material Master for product data",
        "IBP Product Master has hierarchical relationship with Material Master",
        "OPS Excel belongs to Material Master category"
    ]
}
```

### **Method 3: Direct Service Configuration**

```python
from kg_builder.services.multi_schema_llm_service import MultiSchemaLLMService

# Initialize with enhanced prompts
llm_service = MultiSchemaLLMService(use_enhanced_prompts=True)
```

## 📊 Expected Results with Enhanced Prompts

### **Before (Basic Prompts):**
```json
{
    "relationships": [
        {
            "relationship_type": "SEMANTIC_REFERENCE",
            "confidence": 0.85
        }
    ]
}
```

### **After (Enhanced Prompts):**
```json
{
    "relationships": [
        {
            "relationship_type": "REFERENCES",
            "confidence": 0.90,
            "reasoning": "Material field references Material Master table"
        },
        {
            "relationship_type": "HAS", 
            "confidence": 0.85,
            "reasoning": "Material Master has multiple product variants"
        },
        {
            "relationship_type": "HIERARCHICAL",
            "confidence": 0.80,
            "reasoning": "Product hierarchy from master to variants"
        },
        {
            "relationship_type": "SEMANTIC_REFERENCE",
            "confidence": 0.85,
            "reasoning": "Same business concept, different naming"
        }
    ]
}
```

## 🎯 Specific Enhancements for Your Schema

### **For Material/Product Relationships:**

```python
field_preferences = [
    {
        "source_table": "hana_material_master",
        "source_column": "MATERIAL", 
        "target_table": "brz_lnd_RBP_GPU",
        "target_column": "Material",
        "relationship_hint": "REFERENCES - Material master lookup"
    },
    {
        "source_table": "brz_lnd_IBP_Product_Master",
        "source_column": "PRDID",
        "target_table": "hana_material_master", 
        "target_column": "MATERIAL",
        "relationship_hint": "HIERARCHICAL - Product to material hierarchy"
    }
]
```

### **Business Context Definitions:**

```python
business_definitions = [
    "Material Master is the authoritative source for product data",
    "All product tables reference Material Master for specifications",
    "PRDID represents product hierarchy above material level",
    "Business Unit and Product Line create categorical relationships",
    "GPU and NBU tables contain operational data linked to materials"
]
```

## 🧪 Testing Enhanced Prompts

Run the test script to see enhanced prompts in action:

```bash
python test_enhanced_prompts.py
```

This will show you:
- ✅ Multiple relationship types detected
- ✅ Business context analysis
- ✅ Enhanced confidence scoring
- ✅ Comprehensive reasoning

## 📈 Benefits of Enhanced Prompts

1. **Comprehensive Detection**: Finds all relationship types, not just semantic
2. **Business Awareness**: Understands domain-specific patterns
3. **Better Confidence**: More accurate confidence scoring
4. **Rich Context**: Provides detailed reasoning for each relationship
5. **Flexible Configuration**: Can be customized per domain/schema

## 🎉 Result

With enhanced prompts, you'll see relationships like:
- `REFERENCES` for master data lookups
- `HAS`/`BELONGS_TO` for hierarchical structures  
- `BUSINESS_LOGIC` for operational dependencies
- `HIERARCHICAL` for organizational structures
- `TEMPORAL` for audit trails
- And more comprehensive `SEMANTIC_REFERENCE` relationships!

The enhanced prompts transform the LLM from a simple semantic matcher into a comprehensive database relationship analyst.
