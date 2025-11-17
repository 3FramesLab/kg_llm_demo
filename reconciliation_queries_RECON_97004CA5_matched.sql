-- ============================================================================
-- Reconciliation Rules: Reconciliation_demo_reconciliation_kg
-- Generated from KG: demo_reconciliation_kg
-- Schemas: orderMgmt-catalog, qinspect-designcode
-- Total Rules: 19
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Rule 1: Name_Match_catalog_id
-- Match Type: ReconciliationMatchType.EXACT
-- Confidence: 0.75
-- Reasoning: Column name similarity suggests matching: id ≈ id
-- ----------------------------------------------------------------------------

-- MATCHED RECORDS: Records that exist in both source and target

SELECT
    'RULE_4C15FFE9' AS rule_id,
    'Name_Match_catalog_id' AS rule_name,
    0.75 AS confidence_score,
    s.*,
    t.*
FROM orderMgmt-catalog.catalog s
INNER JOIN qinspect-designcode.design_code_master t
    ON s.id = t.id;


-- ----------------------------------------------------------------------------
-- Rule 2: Name_Match_catalog_code
-- Match Type: ReconciliationMatchType.EXACT
-- Confidence: 0.75
-- Reasoning: Column name similarity suggests matching: code ≈ code
-- ----------------------------------------------------------------------------

-- MATCHED RECORDS: Records that exist in both source and target

SELECT
    'RULE_FBE542AB' AS rule_id,
    'Name_Match_catalog_code' AS rule_name,
    0.75 AS confidence_score,
    s.*,
    t.*
FROM orderMgmt-catalog.catalog s
INNER JOIN qinspect-designcode.design_code_master t
    ON s.code = t.code;


-- ----------------------------------------------------------------------------
-- Rule 3: Name_Match_catalog_sub_cat_uid
-- Match Type: ReconciliationMatchType.EXACT
-- Confidence: 0.75
-- Reasoning: Column name similarity suggests matching: sub_cat_uid ≈ sub_category_uid
-- ----------------------------------------------------------------------------

-- MATCHED RECORDS: Records that exist in both source and target

SELECT
    'RULE_6A50635D' AS rule_id,
    'Name_Match_catalog_sub_cat_uid' AS rule_name,
    0.75 AS confidence_score,
    s.*,
    t.*
FROM orderMgmt-catalog.catalog s
INNER JOIN qinspect-designcode.design_code_master t
    ON s.sub_cat_uid = t.sub_category_uid;


-- ----------------------------------------------------------------------------
-- Rule 4: Name_Match_catalog_tenant_uid
-- Match Type: ReconciliationMatchType.EXACT
-- Confidence: 0.75
-- Reasoning: Column name similarity suggests matching: tenant_uid ≈ parent_tenant_uid
-- ----------------------------------------------------------------------------

-- MATCHED RECORDS: Records that exist in both source and target

SELECT
    'RULE_0BBE6DE7' AS rule_id,
    'Name_Match_catalog_tenant_uid' AS rule_name,
    0.75 AS confidence_score,
    s.*,
    t.*
FROM orderMgmt-catalog.catalog s
INNER JOIN qinspect-designcode.design_code_master t
    ON s.tenant_uid = t.parent_tenant_uid;


-- ----------------------------------------------------------------------------
-- Rule 5: Name_Match_catalog_tenant_uid
-- Match Type: ReconciliationMatchType.EXACT
-- Confidence: 0.75
-- Reasoning: Column name similarity suggests matching: tenant_uid ≈ tenant_uid
-- ----------------------------------------------------------------------------

-- MATCHED RECORDS: Records that exist in both source and target

SELECT
    'RULE_47EFE9E3' AS rule_id,
    'Name_Match_catalog_tenant_uid' AS rule_name,
    0.75 AS confidence_score,
    s.*,
    t.*
FROM orderMgmt-catalog.catalog s
INNER JOIN qinspect-designcode.design_code_master t
    ON s.tenant_uid = t.tenant_uid;


-- ----------------------------------------------------------------------------
-- Rule 6: Name_Match_catalog_brand_uid
-- Match Type: ReconciliationMatchType.EXACT
-- Confidence: 0.75
-- Reasoning: Column name similarity suggests matching: brand_uid ≈ brand_uid
-- ----------------------------------------------------------------------------

-- MATCHED RECORDS: Records that exist in both source and target

SELECT
    'RULE_0D835B1E' AS rule_id,
    'Name_Match_catalog_brand_uid' AS rule_name,
    0.75 AS confidence_score,
    s.*,
    t.*
FROM orderMgmt-catalog.catalog s
INNER JOIN qinspect-designcode.design_code_master t
    ON s.brand_uid = t.brand_uid;


-- ----------------------------------------------------------------------------
-- Rule 7: Name_Match_catalog_brand_uid
-- Match Type: ReconciliationMatchType.EXACT
-- Confidence: 0.75
-- Reasoning: Column name similarity suggests matching: brand_uid ≈ sub_brand_uid
-- ----------------------------------------------------------------------------

-- MATCHED RECORDS: Records that exist in both source and target

SELECT
    'RULE_9674A01A' AS rule_id,
    'Name_Match_catalog_brand_uid' AS rule_name,
    0.75 AS confidence_score,
    s.*,
    t.*
FROM orderMgmt-catalog.catalog s
INNER JOIN qinspect-designcode.design_code_master t
    ON s.brand_uid = t.sub_brand_uid;


-- ----------------------------------------------------------------------------
-- Rule 8: Name_Match_catalog_subbrand_uid
-- Match Type: ReconciliationMatchType.EXACT
-- Confidence: 0.75
-- Reasoning: Column name similarity suggests matching: subbrand_uid ≈ brand_uid
-- ----------------------------------------------------------------------------

-- MATCHED RECORDS: Records that exist in both source and target

SELECT
    'RULE_BF9AE3C5' AS rule_id,
    'Name_Match_catalog_subbrand_uid' AS rule_name,
    0.75 AS confidence_score,
    s.*,
    t.*
FROM orderMgmt-catalog.catalog s
INNER JOIN qinspect-designcode.design_code_master t
    ON s.subbrand_uid = t.brand_uid;


-- ----------------------------------------------------------------------------
-- Rule 9: Name_Match_catalog_designer_code
-- Match Type: ReconciliationMatchType.EXACT
-- Confidence: 0.75
-- Reasoning: Column name similarity suggests matching: designer_code ≈ design_code
-- ----------------------------------------------------------------------------

-- MATCHED RECORDS: Records that exist in both source and target

SELECT
    'RULE_7D2CFAE0' AS rule_id,
    'Name_Match_catalog_designer_code' AS rule_name,
    0.75 AS confidence_score,
    s.*,
    t.*
FROM orderMgmt-catalog.catalog s
INNER JOIN qinspect-designcode.design_code_master t
    ON s.designer_code = t.design_code;


-- ----------------------------------------------------------------------------
-- Rule 10: Name_Match_catalog_fabric_code
-- Match Type: ReconciliationMatchType.EXACT
-- Confidence: 0.75
-- Reasoning: Column name similarity suggests matching: fabric_code ≈ fabric_code
-- ----------------------------------------------------------------------------

-- MATCHED RECORDS: Records that exist in both source and target

SELECT
    'RULE_992F772F' AS rule_id,
    'Name_Match_catalog_fabric_code' AS rule_name,
    0.75 AS confidence_score,
    s.*,
    t.*
FROM orderMgmt-catalog.catalog s
INNER JOIN qinspect-designcode.design_code_master t
    ON s.fabric_code = t.fabric_code;


-- ----------------------------------------------------------------------------
-- Rule 11: Name_Match_catalog_collection_uid
-- Match Type: ReconciliationMatchType.EXACT
-- Confidence: 0.75
-- Reasoning: Column name similarity suggests matching: collection_uid ≈ collection_uid
-- ----------------------------------------------------------------------------

-- MATCHED RECORDS: Records that exist in both source and target

SELECT
    'RULE_E7A77BB4' AS rule_id,
    'Name_Match_catalog_collection_uid' AS rule_name,
    0.75 AS confidence_score,
    s.*,
    t.*
FROM orderMgmt-catalog.catalog s
INNER JOIN qinspect-designcode.design_code_master t
    ON s.collection_uid = t.collection_uid;


-- ----------------------------------------------------------------------------
-- Rule 12: Name_Match_catalog_brand_id
-- Match Type: ReconciliationMatchType.EXACT
-- Confidence: 0.75
-- Reasoning: Column name similarity suggests matching: brand_id ≈ brand_uid
-- ----------------------------------------------------------------------------

-- MATCHED RECORDS: Records that exist in both source and target

SELECT
    'RULE_AE536465' AS rule_id,
    'Name_Match_catalog_brand_id' AS rule_name,
    0.75 AS confidence_score,
    s.*,
    t.*
FROM orderMgmt-catalog.catalog s
INNER JOIN qinspect-designcode.design_code_master t
    ON s.brand_id = t.brand_uid;


-- ----------------------------------------------------------------------------
-- Rule 13: Name_Match_catalog_brand_id
-- Match Type: ReconciliationMatchType.EXACT
-- Confidence: 0.75
-- Reasoning: Column name similarity suggests matching: brand_id ≈ sub_brand_uid
-- ----------------------------------------------------------------------------

-- MATCHED RECORDS: Records that exist in both source and target

SELECT
    'RULE_1DB95F51' AS rule_id,
    'Name_Match_catalog_brand_id' AS rule_name,
    0.75 AS confidence_score,
    s.*,
    t.*
FROM orderMgmt-catalog.catalog s
INNER JOIN qinspect-designcode.design_code_master t
    ON s.brand_id = t.sub_brand_uid;


-- ----------------------------------------------------------------------------
-- Rule 14: Name_Match_catalog_product_id
-- Match Type: ReconciliationMatchType.EXACT
-- Confidence: 0.75
-- Reasoning: Column name similarity suggests matching: product_id ≈ product_type_uid
-- ----------------------------------------------------------------------------

-- MATCHED RECORDS: Records that exist in both source and target

SELECT
    'RULE_E0FAB26E' AS rule_id,
    'Name_Match_catalog_product_id' AS rule_name,
    0.75 AS confidence_score,
    s.*,
    t.*
FROM orderMgmt-catalog.catalog s
INNER JOIN qinspect-designcode.design_code_master t
    ON s.product_id = t.product_type_uid;


-- ----------------------------------------------------------------------------
-- Rule 15: Name_Match_catalog_product_id
-- Match Type: ReconciliationMatchType.EXACT
-- Confidence: 0.75
-- Reasoning: Column name similarity suggests matching: product_id ≈ product_code
-- ----------------------------------------------------------------------------

-- MATCHED RECORDS: Records that exist in both source and target

SELECT
    'RULE_C2FE9F6F' AS rule_id,
    'Name_Match_catalog_product_id' AS rule_name,
    0.75 AS confidence_score,
    s.*,
    t.*
FROM orderMgmt-catalog.catalog s
INNER JOIN qinspect-designcode.design_code_master t
    ON s.product_id = t.product_code;


-- ----------------------------------------------------------------------------
-- Rule 16: Name_Match_catalog_product_id
-- Match Type: ReconciliationMatchType.EXACT
-- Confidence: 0.75
-- Reasoning: Column name similarity suggests matching: product_id ≈ product_uid
-- ----------------------------------------------------------------------------

-- MATCHED RECORDS: Records that exist in both source and target

SELECT
    'RULE_4B84D5BC' AS rule_id,
    'Name_Match_catalog_product_id' AS rule_name,
    0.75 AS confidence_score,
    s.*,
    t.*
FROM orderMgmt-catalog.catalog s
INNER JOIN qinspect-designcode.design_code_master t
    ON s.product_id = t.product_uid;


-- ----------------------------------------------------------------------------
-- Rule 17: Name_Match_catalog_parent_tenant_uid
-- Match Type: ReconciliationMatchType.EXACT
-- Confidence: 0.75
-- Reasoning: Column name similarity suggests matching: parent_tenant_uid ≈ parent_tenant_uid
-- ----------------------------------------------------------------------------

-- MATCHED RECORDS: Records that exist in both source and target

SELECT
    'RULE_981EE711' AS rule_id,
    'Name_Match_catalog_parent_tenant_uid' AS rule_name,
    0.75 AS confidence_score,
    s.*,
    t.*
FROM orderMgmt-catalog.catalog s
INNER JOIN qinspect-designcode.design_code_master t
    ON s.parent_tenant_uid = t.parent_tenant_uid;


-- ----------------------------------------------------------------------------
-- Rule 18: Name_Match_catalog_parent_tenant_uid
-- Match Type: ReconciliationMatchType.EXACT
-- Confidence: 0.75
-- Reasoning: Column name similarity suggests matching: parent_tenant_uid ≈ tenant_uid
-- ----------------------------------------------------------------------------

-- MATCHED RECORDS: Records that exist in both source and target

SELECT
    'RULE_5DA7A54B' AS rule_id,
    'Name_Match_catalog_parent_tenant_uid' AS rule_name,
    0.75 AS confidence_score,
    s.*,
    t.*
FROM orderMgmt-catalog.catalog s
INNER JOIN qinspect-designcode.design_code_master t
    ON s.parent_tenant_uid = t.tenant_uid;


-- ----------------------------------------------------------------------------
-- Rule 19: Name_Match_catalog_subseason_uid
-- Match Type: ReconciliationMatchType.EXACT
-- Confidence: 0.75
-- Reasoning: Column name similarity suggests matching: subseason_uid ≈ season_uid
-- ----------------------------------------------------------------------------

-- MATCHED RECORDS: Records that exist in both source and target

SELECT
    'RULE_93347C90' AS rule_id,
    'Name_Match_catalog_subseason_uid' AS rule_name,
    0.75 AS confidence_score,
    s.*,
    t.*
FROM orderMgmt-catalog.catalog s
INNER JOIN qinspect-designcode.design_code_master t
    ON s.subseason_uid = t.season_uid;

