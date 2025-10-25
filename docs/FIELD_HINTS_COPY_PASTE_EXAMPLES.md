# Field Hints Copy-Paste Examples

Ready-to-use field hints JSON for common scenarios. Copy and paste directly into the web UI.

## Example 1: HANA Material Master ↔ OPS Excel GPU

**Use Case**: Match SAP HANA product data with data lake GPU specifications

**Copy this JSON:**
```json
[
  {
    "table_name": "hana_material_master",
    "field_hints": {
      "MATERIAL": "PLANNING_SKU"
    },
    "priority_fields": ["MATERIAL", "MATERIAL_DESC"],
    "exclude_fields": ["INTERNAL_NOTES", "TEMP_FIELD"]
  },
  {
    "table_name": "brz_lnd_OPS_EXCEL_GPU",
    "field_hints": {
      "PLANNING_SKU": "MATERIAL",
      "GPU_MODEL": "PRODUCT_TYPE"
    },
    "priority_fields": ["PLANNING_SKU", "GPU_MODEL"],
    "exclude_fields": ["STAGING_FLAG"]
  }
]
```

**What it does:**
- Maps MATERIAL (HANA) ↔ PLANNING_SKU (OPS Excel)
- Maps GPU_MODEL (OPS Excel) ↔ PRODUCT_TYPE (HANA)
- Prioritizes key identifiers
- Excludes internal/staging fields

---

## Example 2: Simple Single Table (Minimal)

**Use Case**: Basic field mapping with no exclusions

**Copy this JSON:**
```json
[
  {
    "table_name": "orders",
    "field_hints": {
      "order_id": "order_number",
      "customer_id": "cust_id"
    },
    "priority_fields": ["order_id", "customer_id"],
    "exclude_fields": []
  }
]
```

---

## Example 3: Multi-Table with Exclusions

**Use Case**: Multiple tables with sensitive data to exclude

**Copy this JSON:**
```json
[
  {
    "table_name": "customer_master",
    "field_hints": {
      "customer_id": "cust_num",
      "email": "email_address"
    },
    "priority_fields": ["customer_id", "email"],
    "exclude_fields": ["ssn", "credit_card", "password", "internal_notes"]
  },
  {
    "table_name": "customer_staging",
    "field_hints": {
      "cust_num": "customer_id",
      "email_address": "email"
    },
    "priority_fields": ["cust_num", "email_address"],
    "exclude_fields": ["temp_flag", "debug_info", "staging_date"]
  }
]
```

---

## Example 4: Product Catalog Reconciliation

**Use Case**: Match products across different systems

**Copy this JSON:**
```json
[
  {
    "table_name": "erp_products",
    "field_hints": {
      "product_code": "sku",
      "product_name": "description",
      "category_id": "category_code"
    },
    "priority_fields": ["product_code", "product_name", "category_id"],
    "exclude_fields": ["internal_notes", "temp_category", "staging_status"]
  },
  {
    "table_name": "ecommerce_catalog",
    "field_hints": {
      "sku": "product_code",
      "description": "product_name",
      "category_code": "category_id"
    },
    "priority_fields": ["sku", "description", "category_code"],
    "exclude_fields": ["draft_flag", "temp_price", "internal_id"]
  }
]
```

---

## Example 5: Inventory Management

**Use Case**: Match inventory across warehouse systems

**Copy this JSON:**
```json
[
  {
    "table_name": "warehouse_a_inventory",
    "field_hints": {
      "item_id": "item_code",
      "warehouse_location": "bin_location",
      "quantity_on_hand": "qty_available"
    },
    "priority_fields": ["item_id", "warehouse_location", "quantity_on_hand"],
    "exclude_fields": ["last_counted_by", "count_notes", "temp_adjustment"]
  },
  {
    "table_name": "warehouse_b_inventory",
    "field_hints": {
      "item_code": "item_id",
      "bin_location": "warehouse_location",
      "qty_available": "quantity_on_hand"
    },
    "priority_fields": ["item_code", "bin_location", "qty_available"],
    "exclude_fields": ["counted_by", "adjustment_notes", "staging_qty"]
  }
]
```

---

## Example 6: Financial Data Reconciliation

**Use Case**: Match GL accounts and transactions

**Copy this JSON:**
```json
[
  {
    "table_name": "sap_gl_master",
    "field_hints": {
      "gl_account": "account_number",
      "account_name": "account_description",
      "cost_center": "cost_center_code"
    },
    "priority_fields": ["gl_account", "account_name", "cost_center"],
    "exclude_fields": ["internal_comments", "temp_status", "audit_notes"]
  },
  {
    "table_name": "oracle_gl_master",
    "field_hints": {
      "account_number": "gl_account",
      "account_description": "account_name",
      "cost_center_code": "cost_center"
    },
    "priority_fields": ["account_number", "account_description", "cost_center_code"],
    "exclude_fields": ["internal_flag", "temp_account", "staging_notes"]
  }
]
```

---

## Example 7: Customer Data (Sensitive)

**Use Case**: Match customer records while excluding PII

**Copy this JSON:**
```json
[
  {
    "table_name": "crm_customers",
    "field_hints": {
      "customer_id": "cust_id",
      "company_name": "organization",
      "phone": "contact_phone"
    },
    "priority_fields": ["customer_id", "company_name"],
    "exclude_fields": ["ssn", "credit_card", "bank_account", "password", "internal_notes", "personal_email"]
  },
  {
    "table_name": "data_lake_customers",
    "field_hints": {
      "cust_id": "customer_id",
      "organization": "company_name",
      "contact_phone": "phone"
    },
    "priority_fields": ["cust_id", "organization"],
    "exclude_fields": ["pii_flag", "temp_ssn", "staging_data", "debug_info"]
  }
]
```

---

## Example 8: Minimal (Just Hints, No Priorities/Exclusions)

**Use Case**: Quick setup with only field hints

**Copy this JSON:**
```json
[
  {
    "table_name": "source_table",
    "field_hints": {
      "id": "identifier",
      "code": "product_code"
    },
    "priority_fields": [],
    "exclude_fields": []
  },
  {
    "table_name": "target_table",
    "field_hints": {
      "identifier": "id",
      "product_code": "code"
    },
    "priority_fields": [],
    "exclude_fields": []
  }
]
```

---

## How to Use These Examples

1. **Copy** the JSON from the example that matches your use case
2. **Navigate** to the web UI:
   - Knowledge Graph page → Generate KG tab → Field Preferences accordion
   - OR Reconciliation page → Generate Rules tab → Field Preferences accordion
3. **Paste** the JSON into the text field
4. **Customize** table names and field names to match your actual schema
5. **Generate** the KG or Rules

---

## Customization Checklist

Before using an example:

- [ ] Replace `table_name` with your actual table names
- [ ] Replace field names in `field_hints` with your actual column names
- [ ] Update `priority_fields` to match your key identifiers
- [ ] Update `exclude_fields` to match your internal/staging fields
- [ ] Verify JSON syntax (no trailing commas, all strings quoted)
- [ ] Test with a small dataset first

---

## Validation Tips

**Check JSON syntax:**
- Use an online JSON validator: https://jsonlint.com/
- Ensure all strings are double-quoted
- No trailing commas after last item
- Proper nesting of brackets and braces

**Verify field names:**
- Table names must match exactly (case-sensitive)
- Field names must exist in the actual tables
- Check for typos in column names

**Test incrementally:**
- Start with just field_hints
- Add priority_fields next
- Add exclude_fields last
- Verify results at each step


