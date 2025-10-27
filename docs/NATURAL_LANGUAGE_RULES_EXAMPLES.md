# Natural Language Rules Creation API - Examples

The Natural Language Rules Creation API allows you to define relationships between tables using plain English or semi-structured formats. The system automatically generates reconciliation rules from these definitions.

## API Endpoint

```
POST /v1/kg/relationships/natural-language
```

## Request Format

```json
{
  "kg_name": "your_kg_name",
  "schemas": ["schema1", "schema2"],
  "definitions": [
    "Your natural language definitions here"
  ],
  "use_llm": true,
  "min_confidence": 0.7
}
```

### Parameters

- **kg_name** (string, required): Name of your knowledge graph
- **schemas** (array, required): List of schema names involved (e.g., `["orderMgmt-catalog", "vendorDB-suppliers"]`)
- **definitions** (array, required): List of natural language relationship definitions
- **use_llm** (boolean, optional): Use LLM for enhanced parsing (default: `true`)
- **min_confidence** (float, optional): Minimum confidence threshold for relationships (default: `0.7`)

---

## Supported Input Formats

The API supports **4 different input formats**:

1. **Natural Language** - Plain English descriptions
2. **Semi-Structured** - Arrow notation with relationship types
3. **Pseudo-SQL** - SQL-like JOIN syntax
4. **Business Rules** - Conditional logic with IF-THEN

---

## Format 1: Natural Language

Use plain English to describe relationships between entities.

### Example 1: Simple Relationship

```bash
curl -X POST http://localhost:8000/v1/kg/relationships/natural-language \
  -H "Content-Type: application/json" \
  -d '{
    "kg_name": "ecommerce_kg",
    "schemas": ["orderMgmt-catalog", "vendorDB-suppliers"],
    "definitions": [
      "Products are supplied by Vendors",
      "Orders contain Products",
      "Customers place Orders"
    ],
    "use_llm": true,
    "min_confidence": 0.8
  }'
```

**What it does:**
- Parses natural language relationships
- Identifies tables: `Products`, `Vendors`, `Orders`, `Customers`
- Infers join columns based on naming conventions
- Creates relationship definitions with confidence scores

### Example 2: Multiple Relationships

```json
{
  "kg_name": "retail_system",
  "schemas": ["sales-schema", "inventory-schema"],
  "definitions": [
    "Products belong to Categories",
    "Orders are placed by Customers",
    "OrderItems reference Products with quantity",
    "Warehouses manage Inventory",
    "Suppliers provide Products"
  ],
  "use_llm": true,
  "min_confidence": 0.7
}
```

### Example 3: With Attributes

```json
{
  "kg_name": "manufacturing_kg",
  "schemas": ["production-schema", "materials-schema"],
  "definitions": [
    "Products are manufactured from RawMaterials",
    "ProductionOrders have Batches with batch number",
    "QualityChecks are performed on Batches",
    "Suppliers supply RawMaterials with unit price"
  ],
  "use_llm": true,
  "min_confidence": 0.75
}
```

---

## Format 2: Semi-Structured (Arrow Notation)

Use arrow notation to specify exact columns and relationship types.

### Example 4: Direct Column Mapping

```bash
curl -X POST http://localhost:8000/v1/kg/relationships/natural-language \
  -H "Content-Type: application/json" \
  -d '{
    "kg_name": "supply_chain_kg",
    "schemas": ["orderMgmt-catalog", "vendorDB-suppliers"],
    "definitions": [
      "catalog.product_id → vendor.vendor_product_id (SUPPLIED_BY)",
      "orders.customer_id → customers.customer_id (PLACED_BY)",
      "order_items.product_id → products.product_id (CONTAINS)"
    ],
    "use_llm": false,
    "min_confidence": 0.9
  }'
```

**Format:** `schema.table.column → schema.table.column (RELATIONSHIP_TYPE)`

### Example 5: Complex Mappings

```json
{
  "kg_name": "financial_kg",
  "schemas": ["accounts-schema", "transactions-schema"],
  "definitions": [
    "accounts.account_number → transactions.source_account (DEBITS)",
    "accounts.account_number → transactions.target_account (CREDITS)",
    "customers.customer_id → accounts.account_holder_id (OWNS)",
    "transactions.transaction_id → audit_logs.ref_transaction_id (AUDITED_BY)"
  ],
  "use_llm": false,
  "min_confidence": 1.0
}
```

---

## Format 3: Pseudo-SQL

Use SQL-like JOIN syntax to define relationships.

### Example 6: SQL JOIN Style

```bash
curl -X POST http://localhost:8000/v1/kg/relationships/natural-language \
  -H "Content-Type: application/json" \
  -d '{
    "kg_name": "inventory_kg",
    "schemas": ["products-schema", "stock-schema"],
    "definitions": [
      "SELECT * FROM products JOIN suppliers ON products.supplier_id = suppliers.supplier_id",
      "SELECT * FROM orders JOIN customers ON orders.customer_id = customers.customer_id",
      "SELECT * FROM order_items JOIN products ON order_items.product_id = products.product_id"
    ],
    "use_llm": false,
    "min_confidence": 0.8
  }'
```

### Example 7: With WHERE Conditions

```json
{
  "kg_name": "active_products_kg",
  "schemas": ["catalog-schema", "inventory-schema"],
  "definitions": [
    "SELECT * FROM products p JOIN inventory i ON p.product_id = i.product_id WHERE p.status = 'Active'",
    "SELECT * FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE o.order_status != 'Cancelled'"
  ],
  "use_llm": false,
  "min_confidence": 0.85
}
```

---

## Format 4: Business Rules

Use conditional logic with IF-THEN statements.

### Example 8: Conditional Relationships

```bash
curl -X POST http://localhost:8000/v1/kg/relationships/natural-language \
  -H "Content-Type: application/json" \
  -d '{
    "kg_name": "conditional_kg",
    "schemas": ["sales-schema", "products-schema"],
    "definitions": [
      "IF product.status = '\''active'\'' THEN match with inventory.product_id",
      "IF order.order_type = '\''online'\'' THEN link to digital_receipts.order_id",
      "IF customer.account_type = '\''premium'\'' THEN associate with vip_services.customer_id"
    ],
    "use_llm": true,
    "min_confidence": 0.7
  }'
```

---

## Complete Working Example

Here's a complete example using Python:

```python
import requests
import json

# API Configuration
BASE_URL = "http://localhost:8000/v1"
ENDPOINT = f"{BASE_URL}/kg/relationships/natural-language"

# Request payload
payload = {
    "kg_name": "ecommerce_reconciliation",
    "schemas": ["orderMgmt-catalog", "vendorDB-suppliers"],
    "definitions": [
        # Natural Language
        "Products are supplied by Vendors",
        "Orders contain Products with quantity",

        # Semi-Structured
        "catalog.product_id → vendor.vendor_product_id (SUPPLIED_BY)",

        # Pseudo-SQL
        "SELECT * FROM orders JOIN customers ON orders.customer_id = customers.customer_id",

        # Business Rules
        "IF product.Active_Inactive = 'Active' THEN match with vendor.product_status = 'Available'"
    ],
    "use_llm": True,
    "min_confidence": 0.75
}

# Make the request
response = requests.post(ENDPOINT, json=payload)

# Process the response
if response.status_code == 200:
    result = response.json()

    print(f"✅ Success: {result['success']}")
    print(f"📊 Parsed Relationships: {result['parsed_count']}")
    print(f"❌ Failed: {result['failed_count']}")
    print(f"⏱️  Processing Time: {result['processing_time_ms']:.2f}ms")

    # Display parsed relationships
    for rel in result['relationships']:
        print(f"\n🔗 Relationship: {rel['relationship_type']}")
        print(f"   From: {rel['source_entity']}.{rel['source_column']}")
        print(f"   To: {rel['target_entity']}.{rel['target_column']}")
        print(f"   Confidence: {rel['confidence']:.2%}")

    # Display errors (if any)
    if result['errors']:
        print("\n⚠️  Errors:")
        for error in result['errors']:
            print(f"   - {error}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
```

---

## Response Format

```json
{
  "success": true,
  "relationships": [
    {
      "source_entity": "Products",
      "source_column": "product_id",
      "target_entity": "Vendors",
      "target_column": "vendor_product_id",
      "relationship_type": "SUPPLIED_BY",
      "confidence": 0.95,
      "input_format": "NATURAL_LANGUAGE",
      "validation_status": "VALID",
      "validation_errors": []
    }
  ],
  "parsed_count": 5,
  "failed_count": 0,
  "errors": [],
  "processing_time_ms": 1250.5
}
```

---

## Use Cases

### 1. E-Commerce System

```json
{
  "kg_name": "ecommerce_kg",
  "schemas": ["orders", "products", "customers"],
  "definitions": [
    "Customers place Orders",
    "Orders contain Products with quantity and price",
    "Products belong to Categories",
    "Orders are shipped to Addresses",
    "Payments are linked to Orders"
  ]
}
```

### 2. Manufacturing System

```json
{
  "kg_name": "manufacturing_kg",
  "schemas": ["production", "materials", "quality"],
  "definitions": [
    "ProductionOrders use RawMaterials with quantity",
    "Batches are created from ProductionOrders",
    "QualityChecks are performed on Batches",
    "RawMaterials are supplied by Suppliers with unit cost"
  ]
}
```

### 3. Financial System

```json
{
  "kg_name": "financial_kg",
  "schemas": ["accounts", "transactions", "customers"],
  "definitions": [
    "accounts.account_number → transactions.source_account (DEBITS)",
    "accounts.account_number → transactions.target_account (CREDITS)",
    "Customers own Accounts",
    "Transactions are audited by AuditLogs"
  ]
}
```

---

## Tips for Best Results

1. **Use Natural Language for Discovery**
   - Start with plain English to explore relationships
   - Good for brainstorming and initial setup

2. **Use Semi-Structured for Precision**
   - When you know exact columns to match
   - Provides highest confidence scores
   - Best for production systems

3. **Use Pseudo-SQL for Complex Logic**
   - When you need WHERE conditions
   - For filtering specific records
   - Multiple join conditions

4. **Use Business Rules for Conditional Logic**
   - Status-based matching (active/inactive)
   - Type-based relationships
   - Dynamic matching criteria

5. **Combine Multiple Formats**
   - Mix and match formats in the same request
   - Use what's most appropriate for each relationship

6. **Adjust Confidence Threshold**
   - Lower (0.6-0.7): More relationships, less certain
   - Medium (0.7-0.85): Balanced
   - High (0.85-1.0): Only high-confidence matches

---

## Next Steps

After creating natural language relationships:

1. **Generate Reconciliation Rules**
   ```
   POST /v1/reconciliation/generate
   ```

2. **View Generated SQL**
   ```
   GET /v1/reconciliation/rulesets/{ruleset_id}/export/sql
   ```

3. **Execute Reconciliation**
   ```
   POST /v1/reconciliation/execute
   ```

4. **View Results**
   ```
   GET /v1/reconciliation/results
   ```

---

## Error Handling

Common errors and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| `Schema not found` | Schema file doesn't exist | Check schema name, ensure JSON file exists |
| `Below confidence threshold` | Relationship confidence too low | Lower `min_confidence` or refine definition |
| `Invalid column` | Column doesn't exist in schema | Check column names in schema JSON |
| `Ambiguous relationship` | Multiple possible interpretations | Use semi-structured format for precision |

---

## Testing

Test with curl:

```bash
# Test 1: Natural Language
curl -X POST http://localhost:8000/v1/kg/relationships/natural-language \
  -H "Content-Type: application/json" \
  -d '{"kg_name":"test_kg","schemas":["schema1"],"definitions":["Products have Categories"]}'

# Test 2: Semi-Structured
curl -X POST http://localhost:8000/v1/kg/relationships/natural-language \
  -H "Content-Type: application/json" \
  -d '{"kg_name":"test_kg","schemas":["schema1"],"definitions":["products.product_id → categories.category_id (HAS)"]}'
```

---

For more information, see:
- [Reconciliation Guide](RECONCILIATION_EXECUTION_GUIDE.md)
- [KPI Guide](KPI_FEATURE_COMPLETE_GUIDE.md)
- [Quick Start](QUICK_START.md)
