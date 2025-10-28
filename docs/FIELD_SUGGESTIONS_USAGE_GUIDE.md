# Field Suggestions - Usage Guide

## Quick Start

### Basic Usage

```python
from kg_builder.services.reconciliation_service import get_reconciliation_service

# Define field preferences
field_preferences = [
    {
        "table_name": "catalog",
        "priority_fields": ["vendor_uid", "product_id"],
        "exclude_fields": ["internal_notes"],
        "field_hints": {
            "vendor_uid": "supplier_id",
            "product_id": "item_id"
        }
    }
]

# Generate rules with field preferences
recon_service = get_reconciliation_service()
ruleset = recon_service.generate_from_knowledge_graph(
    kg_name="my_kg",
    schema_names=["schema1", "schema2"],
    use_llm=True,
    field_preferences=field_preferences
)
```

## Field Preference Structure

### FieldPreference Model

```python
class FieldPreference(BaseModel):
    table_name: str                    # Table to apply preferences to
    priority_fields: List[str] = []    # Fields to prioritize
    exclude_fields: List[str] = []     # Fields to exclude
    field_hints: Dict[str, str] = {}   # Suggested field mappings
```

## Examples

### Example 1: Prioritize Key Fields

```python
field_preferences = [
    {
        "table_name": "customers",
        "priority_fields": ["customer_id", "email", "phone"],
        "exclude_fields": [],
        "field_hints": {}
    }
]
```

**Effect**: LLM will focus on matching customer_id, email, and phone fields first.

### Example 2: Exclude Sensitive Fields

```python
field_preferences = [
    {
        "table_name": "users",
        "priority_fields": [],
        "exclude_fields": ["password", "ssn", "credit_card"],
        "field_hints": {}
    }
]
```

**Effect**: LLM will skip password, ssn, and credit_card fields.

### Example 3: Provide Field Hints

```python
field_preferences = [
    {
        "table_name": "orders",
        "priority_fields": ["order_id", "customer_id"],
        "exclude_fields": ["internal_notes"],
        "field_hints": {
            "order_id": "order_number",
            "customer_id": "cust_id",
            "order_date": "created_at"
        }
    }
]
```

**Effect**: LLM will use hints to match fields across schemas.

### Example 4: Multiple Tables

```python
field_preferences = [
    {
        "table_name": "catalog",
        "priority_fields": ["product_id", "vendor_id"],
        "exclude_fields": ["temp_field"],
        "field_hints": {"vendor_id": "supplier_id"}
    },
    {
        "table_name": "inventory",
        "priority_fields": ["sku", "warehouse_id"],
        "exclude_fields": ["notes"],
        "field_hints": {"sku": "product_code"}
    }
]
```

**Effect**: Different preferences for different tables.

## How It Works

1. **Priority Fields**: LLM prioritizes these fields when generating rules
2. **Exclude Fields**: LLM skips these fields entirely
3. **Field Hints**: LLM uses these as strong suggestions for field matching

## Benefits

| Feature | Benefit |
|---------|---------|
| **Priority Fields** | Focus on important fields first |
| **Exclude Fields** | Skip sensitive or irrelevant fields |
| **Field Hints** | Guide LLM with known mappings |
| **Multiple Tables** | Different preferences per table |

## API Integration

### REST Endpoint Example

```python
from kg_builder.models import RuleGenerationRequest, FieldPreference

request = RuleGenerationRequest(
    schema_names=["schema1", "schema2"],
    kg_name="my_kg",
    use_llm_enhancement=True,
    field_preferences=[
        FieldPreference(
            table_name="catalog",
            priority_fields=["vendor_uid", "product_id"],
            exclude_fields=["internal_notes"],
            field_hints={"vendor_uid": "supplier_id"}
        )
    ]
)
```

## Best Practices

1. **Start Simple**: Begin with priority_fields only
2. **Test Incrementally**: Add exclude_fields and hints gradually
3. **Use Hints Wisely**: Only provide hints for known mappings
4. **Document Preferences**: Comment why certain fields are prioritized
5. **Monitor Results**: Check generated rules to verify preferences are working

## Troubleshooting

### Issue: Field preferences not affecting rules

**Solution**: Ensure `use_llm=True` is set. Field preferences only work with LLM-based rule generation.

### Issue: Too many rules still generated

**Solution**: Add more fields to `exclude_fields` or reduce `priority_fields` to focus LLM.

### Issue: Wrong field mappings

**Solution**: Review `field_hints` and ensure source/target field names are correct.

## Performance Impact

- **Minimal**: Field preferences add negligible overhead
- **Benefit**: Reduces LLM processing by focusing on relevant fields
- **Result**: Faster rule generation with better quality

## Backward Compatibility

✅ Fully backward compatible - `field_preferences` is optional

