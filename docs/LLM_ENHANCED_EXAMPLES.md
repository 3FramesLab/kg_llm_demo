# LLM-Enhanced Multi-Schema KG - Practical Examples

## Example 1: E-Commerce Data Integration

### Scenario
Integrate CRM and Inventory systems to create a unified customer-product view.

### Schemas
```
CRM System:
  - customers (customer_id, name, email)
  - orders (order_id, customer_id, order_date)
  - order_items (item_id, order_id, product_id)

Inventory System:
  - products (product_id, name, sku, price)
  - stock (stock_id, product_id, quantity)
  - suppliers (supplier_id, name, contact)
```

### Request
```bash
curl -X POST http://localhost:8000/api/v1/kg/generate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_names": ["crm_system", "inventory_system"],
    "kg_name": "ecommerce_unified",
    "backends": ["graphiti"],
    "use_llm_enhancement": true
  }'
```

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/kg/generate",
    json={
        "schema_names": ["crm_system", "inventory_system"],
        "kg_name": "ecommerce_unified",
        "backends": ["graphiti"],
        "use_llm_enhancement": True
    }
)

result = response.json()
print(f"✅ Generated unified KG")
print(f"   Nodes: {result['nodes_count']}")
print(f"   Relationships: {result['relationships_count']}")
```

### LLM Enhancements
```json
{
  "inferred_relationships": [
    {
      "source_table": "order_items",
      "target_table": "stock",
      "relationship_type": "SEMANTIC_REFERENCE",
      "reasoning": "Order items reference products which have stock levels",
      "confidence": 0.92
    },
    {
      "source_table": "products",
      "target_table": "suppliers",
      "relationship_type": "BUSINESS_LOGIC",
      "reasoning": "Products are supplied by suppliers",
      "confidence": 0.88
    }
  ],
  "enhanced_descriptions": [
    {
      "source_table": "orders",
      "target_table": "order_items",
      "description": "Each order contains multiple line items, with each item representing a product purchase"
    },
    {
      "source_table": "order_items",
      "target_table": "products",
      "description": "Order items reference specific products from the inventory system"
    }
  ],
  "confidence_scores": [
    {
      "source_table": "customers",
      "target_table": "orders",
      "confidence": 0.99,
      "validation_status": "VALID",
      "reasoning": "Direct foreign key relationship with clear naming"
    }
  ]
}
```

---

## Example 2: Data Lineage Tracking

### Scenario
Track data flow from source systems through ETL to data warehouse.

### Schemas
```
Source System:
  - raw_customers (id, name, email)
  - raw_orders (id, customer_id, amount)

ETL Layer:
  - stg_customers (customer_id, name, email, load_date)
  - stg_orders (order_id, customer_id, amount, load_date)

Data Warehouse:
  - dim_customers (customer_key, customer_id, name, email)
  - fact_orders (order_key, customer_key, amount, order_date)
```

### Request
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/kg/generate",
    json={
        "schema_names": ["source_system", "etl_layer", "data_warehouse"],
        "kg_name": "data_lineage",
        "backends": ["graphiti"],
        "use_llm_enhancement": True
    }
)

result = response.json()
print(f"Data Lineage KG Generated")
print(f"Nodes: {result['nodes_count']}")
print(f"Relationships: {result['relationships_count']}")
```

### LLM Analysis
```json
{
  "inferred_relationships": [
    {
      "source_table": "raw_customers",
      "target_table": "stg_customers",
      "relationship_type": "DATA_LINEAGE",
      "reasoning": "Raw customer data flows to staging layer",
      "confidence": 0.98
    },
    {
      "source_table": "stg_customers",
      "target_table": "dim_customers",
      "relationship_type": "DATA_LINEAGE",
      "reasoning": "Staged customer data is transformed to dimension",
      "confidence": 0.97
    }
  ],
  "enhanced_descriptions": [
    {
      "source_table": "raw_customers",
      "target_table": "stg_customers",
      "description": "Raw customer records are extracted and loaded into the staging layer for validation and transformation"
    },
    {
      "source_table": "stg_customers",
      "target_table": "dim_customers",
      "description": "Staged customer data is transformed and loaded into the customer dimension with surrogate keys"
    }
  ]
}
```

---

## Example 3: Master Data Management

### Scenario
Identify common entities across CRM, ERP, and Inventory systems.

### Schemas
```
CRM:
  - customers (customer_id, name, email)
  - contacts (contact_id, customer_id, phone)

ERP:
  - vendors (vendor_id, name, contact_email)
  - accounts (account_id, vendor_id, balance)

Inventory:
  - suppliers (supplier_id, name, contact_info)
  - shipments (shipment_id, supplier_id, date)
```

### Request
```python
response = requests.post(
    "http://localhost:8000/api/v1/kg/generate",
    json={
        "schema_names": ["crm", "erp", "inventory"],
        "kg_name": "master_data_mdm",
        "backends": ["graphiti"],
        "use_llm_enhancement": True
    }
)

result = response.json()
print(f"Master Data KG Generated")
print(f"Nodes: {result['nodes_count']}")
print(f"Relationships: {result['relationships_count']}")
```

### LLM Insights
```json
{
  "inferred_relationships": [
    {
      "source_table": "vendors",
      "target_table": "suppliers",
      "relationship_type": "MASTER_DATA_LINK",
      "reasoning": "Vendors in ERP and suppliers in Inventory likely represent the same entities",
      "confidence": 0.85
    }
  ],
  "enhanced_descriptions": [
    {
      "source_table": "vendors",
      "target_table": "suppliers",
      "description": "Vendors from the ERP system and suppliers from the Inventory system represent the same external organizations"
    }
  ],
  "confidence_scores": [
    {
      "source_table": "vendors",
      "target_table": "suppliers",
      "confidence": 0.85,
      "validation_status": "LIKELY",
      "reasoning": "Similar naming patterns and business context suggest these are master data duplicates"
    }
  ]
}
```

---

## Example 4: Healthcare System Integration

### Scenario
Integrate patient records, lab results, and billing systems.

### Schemas
```
Patient System:
  - patients (patient_id, name, dob, ssn)
  - visits (visit_id, patient_id, visit_date)

Lab System:
  - lab_tests (test_id, patient_id, test_type, result)
  - test_results (result_id, test_id, value, unit)

Billing System:
  - charges (charge_id, visit_id, amount)
  - invoices (invoice_id, patient_id, total)
```

### Request
```python
response = requests.post(
    "http://localhost:8000/api/v1/kg/generate",
    json={
        "schema_names": ["patient_system", "lab_system", "billing_system"],
        "kg_name": "healthcare_integrated",
        "backends": ["graphiti"],
        "use_llm_enhancement": True
    }
)

result = response.json()
print(f"Healthcare KG Generated")
print(f"Nodes: {result['nodes_count']}")
print(f"Relationships: {result['relationships_count']}")
```

### LLM Analysis
```json
{
  "inferred_relationships": [
    {
      "source_table": "visits",
      "target_table": "lab_tests",
      "relationship_type": "CLINICAL_REFERENCE",
      "reasoning": "Lab tests are typically ordered during patient visits",
      "confidence": 0.93
    },
    {
      "source_table": "lab_tests",
      "target_table": "charges",
      "relationship_type": "BILLING_REFERENCE",
      "reasoning": "Lab tests generate charges that appear in billing",
      "confidence": 0.90
    }
  ],
  "enhanced_descriptions": [
    {
      "source_table": "visits",
      "target_table": "lab_tests",
      "description": "Lab tests are ordered during patient visits and results are recorded in the lab system"
    },
    {
      "source_table": "lab_tests",
      "target_table": "charges",
      "description": "Each lab test generates a charge that is billed to the patient"
    }
  ]
}
```

---

## Example 5: Comparing With and Without LLM

### Without LLM Enhancement
```bash
curl -X POST http://localhost:8000/api/v1/kg/generate \
  -d '{
    "schema_names": ["schema1", "schema2"],
    "kg_name": "kg_no_llm",
    "use_llm_enhancement": false
  }'
```

**Result:**
```json
{
  "nodes_count": 79,
  "relationships_count": 77,
  "generation_time_ms": 15.08
}
```

### With LLM Enhancement
```bash
curl -X POST http://localhost:8000/api/v1/kg/generate \
  -d '{
    "schema_names": ["schema1", "schema2"],
    "kg_name": "kg_with_llm",
    "use_llm_enhancement": true
  }'
```

**Result:**
```json
{
  "nodes_count": 79,
  "relationships_count": 77,
  "generation_time_ms": 16.85
}
```

**Difference:**
- Same nodes and relationships
- LLM adds metadata to relationships:
  - Confidence scores
  - Business descriptions
  - Validation status
  - Reasoning
- Minimal overhead: 1.77ms

---

## Best Practices

### 1. Use LLM for Complex Integrations
```python
# ✅ Good: Multiple schemas with complex relationships
response = requests.post(f"{BASE_URL}/kg/generate", json={
    "schema_names": ["crm", "erp", "inventory", "warehouse"],
    "kg_name": "complex_integration",
    "use_llm_enhancement": True
})
```

### 2. Disable LLM for Simple Cases
```python
# ✅ Good: Single schema or simple relationships
response = requests.post(f"{BASE_URL}/kg/generate", json={
    "schema_names": ["single_schema"],
    "kg_name": "simple_kg",
    "use_llm_enhancement": False
})
```

### 3. Filter by Confidence Score
```python
# ✅ Good: Only use high-confidence relationships
relationships = [
    rel for rel in kg.relationships
    if rel.properties.get('llm_confidence', 1.0) >= 0.85
]
```

### 4. Use Descriptions for Documentation
```python
# ✅ Good: Generate documentation from descriptions
for rel in kg.relationships:
    if 'llm_description' in rel.properties:
        print(f"{rel.source_id} -> {rel.target_id}")
        print(f"  {rel.properties['llm_description']}")
```

---

## Performance Tips

1. **Batch Processing**: Generate multiple KGs in parallel
2. **Caching**: Cache schema information for repeated use
3. **Selective LLM**: Use LLM only for critical relationships
4. **Monitoring**: Track generation times and adjust accordingly

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| LLM not enhancing | Check `OPENAI_API_KEY` is set |
| Slow generation | Disable LLM or reduce schema size |
| Low confidence scores | Review schema naming conventions |
| Missing relationships | Check schema structure and relationships |

---

**Ready to use LLM-enhanced multi-schema KGs!** 🚀

