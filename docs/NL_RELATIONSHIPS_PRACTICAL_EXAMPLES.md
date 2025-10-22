# Natural Language Relationships - Practical Examples & Use Cases

## 1. REAL-WORLD EXAMPLES

### Example 1: E-Commerce Domain

**Scenario**: Building a unified KG for an e-commerce platform

**Natural Language Definitions**:
```
1. "Customers place Orders"
2. "Orders contain Products with quantity and price"
3. "Products are supplied by Vendors with delivery_date"
4. "Vendors have Locations"
5. "Orders are shipped to Addresses"
6. "Customers have multiple Addresses"
7. "Products belong to Categories"
8. "Categories have Subcategories"
```

**System Processing**:
```
Input 1: "Customers place Orders"
→ Entities: customers, orders
→ Type: PLACES (1:N)
→ Confidence: 0.96
→ Status: VALID

Input 2: "Orders contain Products with quantity and price"
→ Entities: orders, products
→ Type: CONTAINS (N:N)
→ Properties: quantity (int), price (decimal)
→ Confidence: 0.94
→ Status: VALID

Input 3: "Products are supplied by Vendors with delivery_date"
→ Entities: products, vendors
→ Type: SUPPLIES (1:N)
→ Properties: delivery_date (date)
→ Confidence: 0.92
→ Status: VALID
```

**Generated KG**:
```
Customers ──PLACES──> Orders
Orders ──CONTAINS──> Products
Products <──SUPPLIED_BY── Vendors
Vendors ──HAS──> Locations
Orders ──SHIPPED_TO──> Addresses
Customers ──HAS──> Addresses
Products ──BELONGS_TO──> Categories
Categories ──HAS──> Subcategories
```

---

### Example 2: Healthcare Domain

**Scenario**: Integrating patient records, lab results, and billing systems

**Natural Language Definitions**:
```
1. "Patients have Medical Records"
2. "Medical Records contain Lab Results with test_date and result_value"
3. "Lab Results reference Tests"
4. "Patients are treated by Doctors"
5. "Doctors work at Hospitals"
6. "Patients have Insurance"
7. "Insurance covers Procedures"
8. "Procedures generate Bills"
```

**System Processing**:
```
Input 1: "Patients have Medical Records"
→ Entities: patients, medical_records
→ Type: HAS (1:N)
→ Confidence: 0.98
→ Status: VALID

Input 2: "Medical Records contain Lab Results with test_date and result_value"
→ Entities: medical_records, lab_results
→ Type: CONTAINS (1:N)
→ Properties: test_date (date), result_value (string)
→ Confidence: 0.95
→ Status: VALID

Input 7: "Insurance covers Procedures"
→ Entities: insurance, procedures
→ Type: COVERS (1:N)
→ Confidence: 0.93
→ Status: VALID
```

---

### Example 3: Manufacturing Domain

**Scenario**: Supply chain and production tracking

**Natural Language Definitions**:
```
1. "Raw Materials are sourced from Suppliers"
2. "Raw Materials are used in Production Runs"
3. "Production Runs produce Finished Goods"
4. "Finished Goods are stored in Warehouses"
5. "Warehouses are located in Regions"
6. "Finished Goods are shipped to Customers"
7. "Customers place Orders"
8. "Orders reference Finished Goods with quantity and delivery_date"
```

**System Processing**:
```
Input 1: "Raw Materials are sourced from Suppliers"
→ Entities: raw_materials, suppliers
→ Type: SOURCED_FROM (1:N)
→ Confidence: 0.91
→ Status: VALID

Input 2: "Raw Materials are used in Production Runs"
→ Entities: raw_materials, production_runs
→ Type: USED_IN (N:N)
→ Confidence: 0.89
→ Status: VALID

Input 8: "Orders reference Finished Goods with quantity and delivery_date"
→ Entities: orders, finished_goods
→ Type: REFERENCES (N:N)
→ Properties: quantity (int), delivery_date (date)
→ Confidence: 0.94
→ Status: VALID
```

---

## 2. ADVANCED USE CASES

### Use Case 1: Conditional Relationships

**Scenario**: Business logic relationships with conditions

**Natural Language Input**:
```
"When product status is 'active', it should reference the active_vendors table"
"If order status is 'pending', it cannot reference completed_shipments"
"Products with category 'restricted' can only be supplied by certified_vendors"
```

**System Processing**:
```
Input 1: "When product status is 'active', it references active_vendors"
→ Entities: products, active_vendors
→ Type: BUSINESS_LOGIC
→ Condition: product.status = 'active'
→ Confidence: 0.88
→ Status: VALID

Input 3: "Products with category 'restricted' can only be supplied by certified_vendors"
→ Entities: products, certified_vendors
→ Type: BUSINESS_LOGIC
→ Condition: product.category = 'restricted'
→ Confidence: 0.85
→ Status: VALID
```

---

### Use Case 2: Cross-Schema Relationships

**Scenario**: Integrating multiple database schemas

**Natural Language Input**:
```
"In the CRM system, Customers have Contacts
In the ERP system, Parties have Addresses
These should be linked as: CRM.Customers MAPS_TO ERP.Parties"

"The order_id in the billing system corresponds to order_number in the inventory system"
```

**System Processing**:
```
Input 1: "CRM.Customers MAPS_TO ERP.Parties"
→ Source: crm_schema.customers
→ Target: erp_schema.parties
→ Type: CROSS_SCHEMA_REFERENCE
→ Mapping: customer_id ↔ party_id
→ Confidence: 0.92
→ Status: VALID

Input 2: "order_id in billing corresponds to order_number in inventory"
→ Source: billing_schema.orders
→ Target: inventory_schema.orders
→ Type: CROSS_SCHEMA_REFERENCE
→ Mapping: order_id ↔ order_number
→ Confidence: 0.90
→ Status: VALID
```

---

### Use Case 3: Semantic Relationships

**Scenario**: Business meaning relationships beyond technical structure

**Natural Language Input**:
```
"Vendors and Suppliers are essentially the same entity"
"Products and Items are synonymous in this context"
"Orders and Transactions represent the same business concept"
"Customers and Accounts are related but distinct"
```

**System Processing**:
```
Input 1: "Vendors and Suppliers are essentially the same entity"
→ Source: vendors
→ Target: suppliers
→ Type: SEMANTIC_REFERENCE
→ Relationship: EQUIVALENT_TO
→ Confidence: 0.87
→ Status: VALID

Input 4: "Customers and Accounts are related but distinct"
→ Source: customers
→ Target: accounts
→ Type: SEMANTIC_REFERENCE
→ Relationship: RELATED_TO
→ Confidence: 0.85
→ Status: VALID
```

---

## 3. BATCH PROCESSING EXAMPLES

### Example: Markdown-Based Definition

**Input File** (relationships.md):
```markdown
# E-Commerce Knowledge Graph Relationships

## Core Entities

### Customers
- Customers place Orders
- Customers have Addresses
- Customers have Payment Methods

### Orders
- Orders contain Products with quantity and unit_price
- Orders are shipped to Addresses
- Orders have Order Status

### Products
- Products belong to Categories
- Products are supplied by Vendors with delivery_date
- Products have Inventory

### Vendors
- Vendors have Locations
- Vendors have Contact Information
```

**System Processing**:
```
Parsed 8 relationships:
1. Customers → Orders (PLACES) ✓ Confidence: 0.96
2. Customers → Addresses (HAS) ✓ Confidence: 0.95
3. Customers → Payment Methods (HAS) ✓ Confidence: 0.94
4. Orders → Products (CONTAINS) ✓ Confidence: 0.94
5. Orders → Addresses (SHIPPED_TO) ✓ Confidence: 0.92
6. Orders → Order Status (HAS) ✓ Confidence: 0.93
7. Products → Categories (BELONGS_TO) ✓ Confidence: 0.97
8. Products → Vendors (SUPPLIED_BY) ✓ Confidence: 0.92
9. Vendors → Locations (HAS) ✓ Confidence: 0.95
10. Vendors → Contact Information (HAS) ✓ Confidence: 0.94

Total: 10 relationships parsed
Success rate: 100%
Average confidence: 0.942
```

---

## 4. INTERACTIVE CONVERSATION EXAMPLES

### Example: Multi-Turn Clarification

```
Turn 1:
User: "Tell me about the relationship between orders and products"

System: "I found 'orders' and 'products' tables. Let me clarify:
1. Is this a one-to-many (one order has many products)?
2. Should the relationship type be 'CONTAINS' or 'INCLUDES'?
3. Are there any properties like quantity or price?"

Turn 2:
User: "One order has many products, use CONTAINS, add quantity"

System: "Perfect! I've created:
- Source: orders
- Target: products
- Type: CONTAINS
- Properties: quantity
- Cardinality: 1:N
- Confidence: 95%

Would you like to add more relationships?"

Turn 3:
User: "Yes, also add that orders are shipped to addresses"

System: "Great! I found 'addresses' table. Is this:
1. One order shipped to one address?
2. One order shipped to multiple addresses?
3. Should the relationship type be 'SHIPPED_TO' or 'DELIVERED_TO'?"

Turn 4:
User: "One order to one address, use SHIPPED_TO"

System: "Done! Created:
- Source: orders
- Target: addresses
- Type: SHIPPED_TO
- Cardinality: 1:1
- Confidence: 94%

Total relationships created: 2
Ready to generate KG?"
```

---

## 5. ERROR HANDLING EXAMPLES

### Example 1: Ambiguous Entity

```
User Input: "Products are related to Items"

System Response:
{
    "success": false,
    "error": "AmbiguousEntityError",
    "message": "Found multiple possible matches for 'Items'",
    "suggestions": [
        {
            "entity": "inventory_items",
            "confidence": 0.85,
            "table_columns": ["item_id", "item_name", "quantity"]
        },
        {
            "entity": "order_items",
            "confidence": 0.78,
            "table_columns": ["order_item_id", "product_id", "quantity"]
        }
    ],
    "action": "Please clarify which entity you meant"
}
```

### Example 2: Low Confidence

```
User Input: "Foo relates to Bar"

System Response:
{
    "success": false,
    "error": "LowConfidenceError",
    "message": "Confidence score (0.42) below threshold (0.70)",
    "parsed_relationship": {
        "source_entity": "foo_table",
        "target_entity": "bar_table",
        "relationship_type": "UNKNOWN",
        "confidence_score": 0.42
    },
    "alternatives": [
        {
            "relationship_type": "REFERENCES",
            "confidence": 0.55
        },
        {
            "relationship_type": "CONTAINS",
            "confidence": 0.48
        }
    ],
    "action": "Please provide more context or use a template"
}
```

### Example 3: Entity Not Found

```
User Input: "Products are supplied by Vendors"

System Response (if 'Vendors' table doesn't exist):
{
    "success": false,
    "error": "EntityNotFoundError",
    "message": "Entity 'Vendors' not found in schema",
    "found_entities": [
        "vendors",
        "supplier",
        "suppliers",
        "vendor_master"
    ],
    "action": "Did you mean one of these? Or create a new entity?"
}
```

---

## 6. PERFORMANCE EXAMPLES

### Example: Batch Processing Performance

```
Input: 50 relationship descriptions

Processing:
- Entity extraction: 2.3s
- Type inference: 3.1s
- Property extraction: 1.8s
- Validation: 1.2s
- Total: 8.4s

Results:
- Successfully parsed: 48
- Failed: 2
- Average confidence: 0.91
- LLM tokens used: 22,500
- Cost: $0.009
```

---

## 7. INTEGRATION EXAMPLES

### Example: KG Generation with NL Relationships

```
Step 1: Generate base KG from schema
→ Auto-detected 45 relationships

Step 2: User provides NL enhancements
→ "Products are supplied by Vendors"
→ "Orders contain Products with quantity"
→ "Customers have Addresses"

Step 3: Parse NL relationships
→ 3 relationships parsed successfully

Step 4: Merge relationships
→ Total relationships: 48 (45 auto + 3 user-defined)

Step 5: Generate unified KG
→ KG created with 48 relationships
→ User-defined relationships marked with user_defined=true
```

---

## 8. VALIDATION EXAMPLES

### Example: Schema Validation

```
Parsed Relationship:
- Source: products
- Target: vendors
- Type: SUPPLIES
- Properties: delivery_date

Validation Checks:
✓ Source entity exists in schema
✓ Target entity exists in schema
✓ Relationship type is valid
✓ Properties exist in schema
✓ No circular dependencies
✓ Cardinality is valid

Result: VALID (Confidence: 0.92)
```

---

**Document Status**: Practical Examples Complete ✅
**Ready for**: User Testing & Feedback

