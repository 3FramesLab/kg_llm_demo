-- KPI Migration Script
-- Generated from SQLite to MS SQL Server
-- Generated on: 2025-11-06 12:45:29.654287
-- Database: KPI_Analytics

USE [KPI_Analytics];
GO

-- Disable identity insert temporarily
SET IDENTITY_INSERT kpi_definitions ON;
GO

-- KPI 1: Test KPI
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    1,
    N'Test KPI',
    N'TKPI',
    N'Data Quality',
    N'Test',
    N'Show me all products',
    N'2025-10-27 17:54:04',
    N'2025-10-28 08:55:24',
    NULL,
    0
);

-- KPI 2: Test 123
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    2,
    N'Test 123',
    N'RBU GPU Inactive',
    N'Reconciliation',
    N'this gives us inactive records from the OPS Excel',
    N'Show me all the products in RBP GPU which are inactive OPS Excel',
    N'2025-10-27 18:34:16',
    N'2025-10-28 16:26:30',
    NULL,
    0
);

-- KPI 3: RBP missing in Ops Excel
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    3,
    N'RBP missing in Ops Excel',
    N'RBP Missing in OPS Excel',
    N'GPU Product Master vs RBP123',
    N'',
    N'Show me all the products in RBP GPU which are missing in OPS Excel, also show ops planner from hana master',
    N'2025-10-28 09:05:28',
    N'2025-11-06 08:18:42',
    NULL,
    0
);

-- KPI 4: RBP missing in SKU
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    4,
    N'RBP missing in SKU',
    N'RBP missing in SKU',
    N'GPU Product Master vs RBP123',
    N'',
    N'Show me all the products in RBP GPU which are missing in SKULIFNR',
    N'2025-10-28 15:40:30',
    N'2025-11-06 08:18:46',
    NULL,
    0
);

-- KPI 5: RBP GPU Inactive in OPS Excel
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    5,
    N'RBP GPU Inactive in OPS Excel',
    N'RBP GPU Inactive in OPS Excel',
    N'GPU Product Master vs RBP',
    N'',
    N'Show me all the products in RBP GPU which are inactive OPS Excel',
    N'2025-10-28 21:02:29',
    N'2025-10-28 21:09:16',
    NULL,
    0
);

-- KPI 6: Test 1234
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    6,
    N'Test 1234',
    N'',
    N'',
    N'',
    N'Show me all the products in RBP GPU which are missing in OPS Excel, also show ops planner from hana master',
    N'2025-10-30 15:24:30',
    N'2025-10-30 18:06:53',
    NULL,
    0
);

-- KPI 7: RBP missing in SKU, Hana Status, Planner
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    7,
    N'RBP missing in SKU, Hana Status, Planner',
    N'',
    N'',
    N'',
    N'Show me all the products in RBP GPU which are missing in SKULIFNR, also show ops status and ops planner from hana master',
    N'2025-10-30 17:10:19',
    N'2025-11-06 08:18:50',
    NULL,
    0
);

-- KPI 8: GPU Inactive in OPS
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    8,
    N'GPU Inactive in OPS',
    N'GPU Inactive in OPS',
    N'GPU Product Master vs RBP',
    N'',
    N'Show me all the products in RBP GPU which are inactive in OPS Excel',
    N'2025-10-30 18:24:50',
    N'2025-10-31 13:30:54',
    NULL,
    0
);

-- KPI 9: Test098
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    9,
    N'Test098',
    N'',
    N'',
    N'',
    N'show me all hana material master, ibp product master that matches with product type GPU',
    N'2025-11-04 12:07:49',
    N'2025-11-06 08:19:12',
    NULL,
    0
);

-- KPI 10: NONMatch
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    10,
    N'NONMatch',
    N'IBP non match Hana',
    N'',
    N'',
    N'show me all hana material master, ibp product master that not matches with product type GPU	',
    N'2025-11-04 16:32:36',
    N'2025-11-06 08:19:41',
    NULL,
    0
);

-- KPI 11: NONMatch123
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    11,
    N'NONMatch123',
    N'IBP non match Hana',
    N'',
    N'',
    N'show us all hana material master and ibp product master that do not match on product type',
    N'2025-11-04 16:37:15',
    N'2025-11-06 08:19:38',
    NULL,
    0
);

-- KPI 12: GPU Planner Missing
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    12,
    N'GPU Planner Missing',
    N'GPU Planner Missing',
    N'',
    N'GPU Planner Missing',
    N'show matching product type of GPU from hana material master and ibp product master who have no ops planner',
    N'2025-11-04 16:57:32',
    N'2025-11-06 08:19:34',
    NULL,
    0
);

-- KPI 13: GPU Missing Planner
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    13,
    N'GPU Missing Planner',
    N'GPU Missing Planner',
    N'',
    N'',
    N'get hana material master and ibp product master with product type as GPU and having ops planner as null',
    N'2025-11-04 17:41:19',
    N'2025-11-06 08:19:31',
    NULL,
    0
);

-- KPI 14: GPU Missing Status
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    14,
    N'GPU Missing Status',
    N'GPU Missing Status',
    N'',
    N'',
    N'get hana material master and ibp product master with product type as GPU and having ops status as null	
',
    N'2025-11-04 17:42:40',
    N'2025-11-06 08:19:29',
    NULL,
    0
);

-- KPI 15: NBU Missing Status
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    15,
    N'NBU Missing Status',
    N'NBU Missing Status',
    N'',
    N'',
    N'get hana material master and ibp product master with product type as NBU and having ops planner as null',
    N'2025-11-04 17:44:00',
    N'2025-11-06 08:19:27',
    NULL,
    0
);

-- KPI 16: SKU Missing GPU
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    16,
    N'SKU Missing GPU',
    N'SKU Missing GPU',
    N'',
    N'',
    N'get matching SKU LIFNR, ibp product master with product type as GPU',
    N'2025-11-04 17:53:23',
    N'2025-11-06 08:19:25',
    NULL,
    0
);

-- KPI 17: Try123
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    17,
    N'Try123',
    N'Try123',
    N'',
    N'',
    N'get hana material master and ibp product master with product type as NBU and having ops planner as null',
    N'2025-11-05 08:48:16',
    N'2025-11-06 08:19:22',
    NULL,
    0
);

-- KPI 18: Top Level Missing
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    18,
    N'Top Level Missing',
    N'top level missing',
    N'',
    N'',
    N'get hana material master and ibp product master with product type as NBU and top level missing',
    N'2025-11-05 10:15:29',
    N'2025-11-06 08:19:19',
    NULL,
    0
);

-- KPI 19: RBP SKU Missing in Master Product List
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    19,
    N'RBP SKU Missing in Master Product List',
    N'RBP SKU Missing in Master Product List',
    N'GPU Product Master vs RBP',
    N'RBP SKU Missing in Master Product List',
    N'Show me all the products in RBP GPU which are missing in OPS Excel',
    N'2025-11-05 12:33:59',
    N'2025-11-06 08:14:01',
    NULL,
    1
);

-- KPI 20: RBP SKU Missing in SKULIFNR
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    20,
    N'RBP SKU Missing in SKULIFNR',
    N'RBP SKU Missing in SKULIFNR',
    N'GPU Product Master vs RBP',
    N'RBP SKU Missing in SKULIFNR',
    N'Show me all the products in RBP GPU which are missing in SKULIFNR',
    N'2025-11-05 12:34:49',
    N'2025-11-06 05:44:04',
    NULL,
    1
);

-- KPI 21: RBP SKU Obsolete in Master Product List
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    21,
    N'RBP SKU Obsolete in Master Product List',
    N'RBP SKU Obsolete in Master Product List',
    N'GPU Product Master vs RBP',
    N'RBP SKU Obsolete in Master Product List',
    N'Show me all the products in RBP GPU which are inactive OPS Excel',
    N'2025-11-05 12:35:53',
    N'2025-11-06 07:46:58',
    NULL,
    1
);

-- KPI 22: NBU RBP SKU Obsolete in Master Product List
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    22,
    N'NBU RBP SKU Obsolete in Master Product List',
    N'RBP SKU Obsolete in Master Product List',
    N'NBU Product Master vs RBP',
    N'RBP SKU Obsolete in Master Product List',
    N'Show me all the products in RBP NBU which are missing in OPS Data',
    N'2025-11-05 12:36:38',
    N'2025-11-06 07:54:23',
    NULL,
    1
);

-- KPI 23: NBU RBP SKU Missing in Master Product List
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    23,
    N'NBU RBP SKU Missing in Master Product List',
    N'NBU RBP SKU Missing in Master Product List',
    N'NBU Product Master vs RBP',
    N'NBU RBP SKU Missing in Master Product List',
    N'Show me all the products in RBP NBU which are inactive OPS Excel',
    N'2025-11-05 12:37:19',
    N'2025-11-06 08:13:51',
    NULL,
    1
);

-- KPI 24: NBU RBP SKU Missing in SKULIFNR
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    24,
    N'NBU RBP SKU Missing in SKULIFNR',
    N'RBP SKU Missing in SKULIFNR',
    N'NBU Product Master vs RBP',
    N'RBP SKU Missing in SKULIFNR',
    N'Show me all the products in RBP NBU which are missing in SKULIFNR',
    N'2025-11-05 12:39:02',
    N'2025-11-06 08:13:35',
    NULL,
    1
);

-- KPI 25: GPU Master Product List with Planner Missing
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    25,
    N'GPU Master Product List with Planner Missing',
    N'GPU Master Product List with Planner Missing',
    N'GPU Master Product List Quality',
    N'GPU Master Product List with Planner Missing',
    N'show me all GPU Product type records from product master and hana master where ops planner are missing',
    N'2025-11-05 12:40:40',
    N'2025-11-06 09:24:02',
    NULL,
    1
);

-- KPI 26: GPU Master Product List with Status Missing
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    26,
    N'GPU Master Product List with Status Missing',
    N'Master Product List with Status Missing',
    N'GPU Master Product List Quality',
    N'GPU Master Product List with Status Missing',
    N'show me missing ops status from product master and hana master of GPU product type',
    N'2025-11-05 12:44:27',
    N'2025-11-06 09:12:17',
    NULL,
    1
);

-- KPI 27: GPU Master Product List with Top Level Missing
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    27,
    N'GPU Master Product List with Top Level Missing',
    N'Master Product List with Top-Level Missing',
    N'GPU Master Product List Quality',
    N'GPU Master Product List with Top Level Missing',
    N'NA',
    N'2025-11-05 12:45:18',
    N'2025-11-05 12:45:18',
    NULL,
    1
);

-- KPI 28: GPU Master Product List with Marketing Code Missing
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    28,
    N'GPU Master Product List with Marketing Code Missing',
    N'Master Product List with Marketing Code Missing',
    N'GPU Master Product List Quality',
    N'GPU Master Product List with Marketing Code Missing',
    N'NA',
    N'2025-11-05 12:46:23',
    N'2025-11-05 12:46:23',
    NULL,
    1
);

-- KPI 29: GPU Master Product List with PLC Code Missing
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    29,
    N'GPU Master Product List with PLC Code Missing',
    N'Master Product List with PLC Code Missing',
    N'GPU Master Product List Quality',
    N'GPU Master Product List with PLC Code Missing',
    N'NA',
    N'2025-11-05 12:47:04',
    N'2025-11-05 12:47:04',
    NULL,
    1
);

-- KPI 30: NBU Master Product List with Planner Missing
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    30,
    N'NBU Master Product List with Planner Missing',
    N'Master Product List with Planner Missing',
    N'NBU Master Product List Quality',
    N'NBU Master Product List with Planner Missing',
    N'NA',
    N'2025-11-05 12:48:40',
    N'2025-11-05 12:48:40',
    NULL,
    1
);

-- KPI 31: NBU Master Product List with Status Missing
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    31,
    N'NBU Master Product List with Status Missing',
    N'Master Product List with Status Missing',
    N'NBU Master Product List Quality',
    N'NBU Master Product List with Status Missing',
    N'NA',
    N'2025-11-05 12:52:30',
    N'2025-11-05 12:52:30',
    NULL,
    1
);

-- KPI 32: NBU Master Product List with Top-Level Name Missing
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    32,
    N'NBU Master Product List with Top-Level Name Missing',
    N'Master Product List with Top Level Name Missing',
    N'NBU Master Product List Quality',
    N'NBU Master Product List with Top-Level Name Missing',
    N'NA',
    N'2025-11-05 12:53:21',
    N'2025-11-05 12:53:21',
    NULL,
    1
);

-- KPI 33: NBU Master Product List with Item Group Missing
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    33,
    N'NBU Master Product List with Item Group Missing',
    N'Master Product List with Item Group Missing',
    N'NBU Master Product List Quality',
    N'NBU Master Product List with Item Group Missing',
    N'NA',
    N'2025-11-05 12:54:38',
    N'2025-11-05 12:54:38',
    NULL,
    1
);

-- KPI 34: Duplicates in NBU Master Product List
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    34,
    N'Duplicates in NBU Master Product List',
    N'Duplicates in NBU Master Product List',
    N'NBU Master Product List Quality',
    N'Duplicates in NBU Master Product List',
    N'NA',
    N'2025-11-05 12:55:11',
    N'2025-11-05 12:55:11',
    NULL,
    1
);

-- KPI 35: GPU SKULIFNR SKU Missing in Master Product List present in SAR
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    35,
    N'GPU SKULIFNR SKU Missing in Master Product List present in SAR',
    N'SKULIFNR SKU Missing in Master Product List present in SAR',
    N'GPU Master Product List vs SKULIFNR',
    N'SKULIFNR SKU Missing in Master Product List present in SAR',
    N'NA',
    N'2025-11-05 12:58:13',
    N'2025-11-05 12:58:13',
    NULL,
    1
);

-- KPI 36: GPU Active/Inactive/Idle Master Product List SKU missing from SKULIFNR
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    36,
    N'GPU Active/Inactive/Idle Master Product List SKU missing from SKULIFNR',
    N'Active/Inactive/Idle Master Product List SKU missing from SKULIFNR',
    N'GPU Master Product List vs SKULIFNR',
    N'GPU Active/Inactive/Idle Master Product List SKU missing from SKULIFNR',
    N'NA',
    N'2025-11-05 12:59:21',
    N'2025-11-05 12:59:21',
    NULL,
    1
);

-- KPI 37: GPU SKUs in SKULIFNR obsolete in Master Product List
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    37,
    N'GPU SKUs in SKULIFNR obsolete in Master Product List',
    N'SKUs in SKULIFNR obsolete in Master Product List',
    N'GPU Master Product List vs SKULIFNR',
    N'GPU SKUs in SKULIFNR obsolete in Master Product List',
    N'NA',
    N'2025-11-05 13:00:12',
    N'2025-11-05 13:00:12',
    NULL,
    1
);

-- KPI 38: NBU SKULIFNR SKU Missing in Master Product List present in SAR
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    38,
    N'NBU SKULIFNR SKU Missing in Master Product List present in SAR',
    N'SKULIFNR SKU Missing in Master Product List present in SAR',
    N'NBU Master Product List vs SKULIFNR',
    N'NBU SKULIFNR SKU Missing in Master Product List present in SAR',
    N'NA',
    N'2025-11-05 13:01:14',
    N'2025-11-05 13:01:14',
    NULL,
    1
);

-- KPI 39: NBU Active/Inactive/Idle Master Product List SKU missing from SKULIFNR
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    39,
    N'NBU Active/Inactive/Idle Master Product List SKU missing from SKULIFNR',
    N'Active/Inactive/Idle Master Product List SKU missing from SKULIFNR',
    N'NBU Master Product List vs SKULIFNR',
    N'Active/Inactive/Idle Master Product List SKU missing from SKULIFNR',
    N'NA',
    N'2025-11-05 13:01:59',
    N'2025-11-05 13:01:59',
    NULL,
    1
);

-- KPI 40: NBU SKUs in SKULIFNR obsolete in Master Product List
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    40,
    N'NBU SKUs in SKULIFNR obsolete in Master Product List',
    N'SKUs in SKULIFNR obsolete in Master Product List',
    N'NBU Master Product List vs SKULIFNR',
    N'NBU SKUs in SKULIFNR obsolete in Master Product List',
    N'NA',
    N'2025-11-05 13:02:42',
    N'2025-11-05 13:02:42',
    NULL,
    1
);

-- KPI 41: GPU SAR(Non Zero) missing from Master Product List
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    41,
    N'GPU SAR(Non Zero) missing from Master Product List',
    N'SAR(Non Zero) missing from Master Product List',
    N'GPU Master Product List vs SAR > 0 (Total Incoming Supply)',
    N'SAR(Non Zero) missing from Master Product List',
    N'NA',
    N'2025-11-05 13:06:05',
    N'2025-11-05 13:06:05',
    NULL,
    1
);

-- KPI 42: NBU SAR(Non Zero) missing from Master Product List
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    42,
    N'NBU SAR(Non Zero) missing from Master Product List',
    N'SAR(Non Zero) missing from Master Product List',
    N'NBU Master Product List vs SAR > 0 (Total Incoming Supply)',
    N'NBU SAR(Non Zero) missing from Master Product List',
    N'NA',
    N'2025-11-05 13:11:37',
    N'2025-11-05 13:23:07',
    NULL,
    1
);

-- KPI 43: GPU SAR SKU Missing in SKULIFNR
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    43,
    N'GPU SAR SKU Missing in SKULIFNR',
    N'GPU SAR SKU Missing in SKULIFNR',
    N'GPU Master Product List vs SAR > 0 (Total Incoming Supply)',
    N'GPU SAR SKU Missing in SKULIFNR',
    N'NA',
    N'2025-11-05 13:15:00',
    N'2025-11-05 13:22:53',
    NULL,
    1
);

-- KPI 44: GPU SAR(Non Zero) obsolete from Master Product List
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    44,
    N'GPU SAR(Non Zero) obsolete from Master Product List',
    N'SAR(Non Zero) obsolete from Master Product List',
    N'GPU Master Product List vs SAR > 0 (Total Incoming Supply)',
    N'GPU SAR(Non Zero) obsolete from Master Product List',
    N'NA',
    N'2025-11-05 13:20:31',
    N'2025-11-05 13:20:31',
    NULL,
    1
);

-- KPI 45: NBU SAR(Non Zero) obsolete from Master Product List
INSERT INTO kpi_definitions (
    id, name, alias_name, group_name, description, nl_definition,
    created_at, updated_at, created_by, is_active
) VALUES (
    45,
    N'NBU SAR(Non Zero) obsolete from Master Product List',
    N'SAR(Non Zero) obsolete from Master Product List',
    N'NBU Master Product List vs SAR > 0 (Total Incoming Supply)',
    N'NBU SAR(Non Zero) obsolete from Master Product List',
    N'NA',
    N'2025-11-05 13:21:46',
    N'2025-11-05 13:23:14',
    NULL,
    1
);

-- Execution Results
SET IDENTITY_INSERT kpi_execution_results ON;
GO

-- Execution 1
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    11,
    2,
    N'KG_250',
    N'newdqschema',
    N'SELECT DISTINCT s.*
FROM [brz_lnd_RBP_GPU] s
INNER JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
WHERE t.[Active_Inactive] = ''Inactive''',
    56,
    N'success',
    N'2025-10-28 15:38:32',
    4962.633848190308,
    0.95,
    NULL
);

-- Execution 2
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    8,
    2,
    N'KG_102',
    N'newdqschema',
    N'SELECT DISTINCT s.*
FROM [brz_lnd_RBP_GPU] s
INNER JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
WHERE t.[Active_Inactive] = ''Inactive''',
    56,
    N'success',
    N'2025-10-28 09:04:05',
    6026.84473991394,
    0.95,
    NULL
);

-- Execution 3
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    7,
    2,
    N'KG_102',
    N'newdqschema',
    N'SELECT DISTINCT s.*
FROM [brz_lnd_RBP_GPU] s
INNER JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
WHERE t.[Active_Inactive] = ''Inactive''',
    56,
    N'success',
    N'2025-10-28 08:49:20',
    7983.593940734863,
    0.95,
    NULL
);

-- Execution 4
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    6,
    2,
    N'KG_102',
    N'newdqschema',
    N'',
    0,
    N'failed',
    N'2025-10-28 08:20:54',
    3345.5371856689453,
    0.85,
    N'Error executing query: Filter query requires source table'
);

-- Execution 5
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    5,
    2,
    N'KG_102',
    N'newdqschema',
    N'',
    0,
    N'failed',
    N'2025-10-27 19:37:02',
    5705.620527267456,
    0.3,
    N'Error executing query: Comparison query requires join columns to compare ''rbp'' and ''gpu'', but none were found. 

To fix this issue:
1. Ensure your Knowledge Graph has relationships between these tables
2. Use the ''Execute Queries'' tab and add explicit relationship pairs:
   Example: {
     "source_table": "rbp",
     "source_column": "<matching_column>",
     "target_table": "gpu",
     "target_column": "<matching_column>",
     "relationship_type": "MATCHES"
   }
3. Or add matching columns to your schema that can be auto-detected'
);

-- Execution 6
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    4,
    2,
    N'KG_102',
    N'newdqschema',
    NULL,
    0,
    N'failed',
    N'2025-10-27 19:30:30',
    7585.08563041687,
    0,
    N'Could not establish database connection'
);

-- Execution 7
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    3,
    2,
    N'KG_102',
    N'newdqschema',
    NULL,
    0,
    N'failed',
    N'2025-10-27 19:20:28',
    4662.034273147583,
    0,
    N'Could not establish database connection'
);

-- Execution 8
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    2,
    2,
    N'KG_102',
    N'newdqschema',
    NULL,
    0,
    N'failed',
    N'2025-10-27 19:13:55',
    5.043983459472656,
    0,
    N'get_nl_query_parser() got an unexpected keyword argument ''kg_name'''
);

-- Execution 9
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    1,
    2,
    N'KG_102',
    N'newdqschema',
    NULL,
    0,
    N'failed',
    N'2025-10-27 18:55:58',
    4.997014999389648,
    0,
    N'get_nl_query_parser() got an unexpected keyword argument ''kg_name'''
);

-- Execution 10
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    111,
    3,
    N'Nov5_2025_KG_100',
    N'newdqschemanov',
    N'SELECT DISTINCT s.*, h.[OPS_PLANNER] AS [OPS_PLANNER]
FROM [brz_lnd_RBP_GPU] s
LEFT JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
LEFT JOIN [hana_material_master] h ON s.[Material] = h.[MATERIAL]
WHERE t.[PLANNING_SKU] IS NULL',
    0,
    N'success',
    N'2025-11-05 10:12:27',
    13906.428813934326,
    0.95,
    NULL
);

-- Execution 11
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    110,
    3,
    N'Nov5_2025_KG_100',
    N'newdqschemanov',
    N'SELECT DISTINCT s.*, h.[OPS_PLANNER] AS [OPS_PLANNER]
FROM [brz_lnd_RBP_GPU] s
LEFT JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
LEFT JOIN [hana_material_master] h ON s.[Material] = h.[MATERIAL]
WHERE t.[PLANNING_SKU] IS NULL AND h.[OPS_PLANNER] = ''hana master''',
    0,
    N'success',
    N'2025-11-05 10:02:23',
    11851.152658462524,
    0.95,
    NULL
);

-- Execution 12
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    74,
    3,
    N'KG_1000',
    N'newdqschema',
    N'SELECT DISTINCT s.*, h.[OPS_PLANNER] AS [OPS_PLANNER]
FROM [brz_lnd_RBP_GPU] s
LEFT JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
LEFT JOIN [hana_material_master] h ON s.[Material] = h.[MATERIAL]
WHERE t.[PLANNING_SKU] IS NULL',
    35,
    N'success',
    N'2025-10-31 08:25:24',
    11384.366035461426,
    0.95,
    NULL
);

-- Execution 13
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    72,
    3,
    N'KG_1000',
    N'newdqschema',
    N'',
    0,
    N'failed',
    N'2025-10-31 08:21:25',
    4953.686475753784,
    0.3,
    N'Error executing query: Comparison query requires join columns to compare ''brz_lnd_RBP_GPU'' and ''brz_lnd_RBP_GPU'', but none were found. 

To fix this issue:
1. Ensure your Knowledge Graph has relationships between these tables
2. Use the ''Execute Queries'' tab and add explicit relationship pairs:
   Example: {
     "source_table": "brz_lnd_RBP_GPU",
     "source_column": "<matching_column>",
     "target_table": "brz_lnd_RBP_GPU",
     "target_column": "<matching_column>",
     "relationship_type": "MATCHES"
   }
3. Or add matching columns to your schema that can be auto-detected'
);

-- Execution 14
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    42,
    3,
    N'KG_098',
    N'newdqschema',
    N'-- Generated SQL for RBP missing in Ops Excel
SELECT * FROM source_table WHERE condition LIMIT 33',
    33,
    N'success',
    N'2025-10-30 18:39:10',
    2567.6129954677576,
    0.8069164136042717,
    NULL
);

-- Execution 15
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    43,
    3,
    N'KG_098',
    N'newdqschema',
    N'-- Generated SQL for RBP missing in Ops Excel
SELECT * FROM source_table WHERE condition LIMIT 35',
    35,
    N'success',
    N'2025-10-29 18:39:10',
    1767.2480798370502,
    0.8389617025775299,
    NULL
);

-- Execution 16
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    44,
    3,
    N'KG_098',
    N'newdqschema',
    N'-- Generated SQL for RBP missing in Ops Excel
SELECT * FROM source_table WHERE condition LIMIT 36',
    36,
    N'success',
    N'2025-10-28 18:39:10',
    568.2503741388671,
    0.9269411678266926,
    NULL
);

-- Execution 17
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    10,
    3,
    N'KG_102',
    N'newdqschema',
    N'SELECT DISTINCT s.*
FROM [brz_lnd_RBP_GPU] s
LEFT JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
WHERE t.[PLANNING_SKU] IS NULL',
    35,
    N'success',
    N'2025-10-28 10:19:37',
    10903.078079223633,
    0.95,
    NULL
);

-- Execution 18
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    9,
    3,
    N'KG_102',
    N'newdqschema',
    N'SELECT DISTINCT s.*
FROM [brz_lnd_RBP_GPU] s
LEFT JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
WHERE t.[PLANNING_SKU] IS NULL',
    35,
    N'success',
    N'2025-10-28 09:06:27',
    4986.218690872192,
    0.95,
    NULL
);

-- Execution 19
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    45,
    3,
    N'KG_098',
    N'newdqschema',
    N'-- Generated SQL for RBP missing in Ops Excel
SELECT * FROM source_table WHERE condition LIMIT 33',
    33,
    N'success',
    N'2025-10-27 18:39:10',
    2871.4332939492106,
    0.9075311069063923,
    NULL
);

-- Execution 20
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    46,
    3,
    N'KG_098',
    N'newdqschema',
    N'-- Generated SQL for RBP missing in Ops Excel
SELECT * FROM source_table WHERE condition LIMIT 34',
    34,
    N'success',
    N'2025-10-26 18:39:10',
    2570.5117154643535,
    0.9146241566165747,
    NULL
);

-- Execution 21
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    47,
    3,
    N'KG_098',
    N'newdqschema',
    N'-- Generated SQL for RBP missing in Ops Excel
SELECT * FROM source_table WHERE condition LIMIT 34',
    34,
    N'success',
    N'2025-10-25 18:39:10',
    1149.5681322381192,
    0.9210590015434325,
    NULL
);

-- Execution 22
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    48,
    3,
    N'KG_098',
    N'newdqschema',
    N'-- Generated SQL for RBP missing in Ops Excel
SELECT * FROM source_table WHERE condition LIMIT 33',
    33,
    N'success',
    N'2025-10-24 18:39:10',
    2791.215905181076,
    0.8308044914032463,
    NULL
);

-- Execution 23
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    115,
    4,
    N'Nov5_2025_KG_100',
    N'newdqschemanov',
    N'SELECT DISTINCT s.*
FROM [brz_lnd_RBP_GPU] s
LEFT JOIN [brz_lnd_SKU_LIFNR_Excel] t ON s.[Material] = t.[Material]
WHERE t.[Material] IS NULL',
    0,
    N'success',
    N'2025-11-05 10:29:48',
    11505.446672439575,
    0.95,
    NULL
);

-- Execution 24
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    112,
    4,
    N'Nov5_2025_KG_100',
    N'newdqschemanov',
    N'SELECT DISTINCT s.* FROM [brz_lnd_RBP_GPU] s LEFT JOIN [brz_lnd_SKU_LIFNR_Excel] t ON s.[Material] = t.[Material] WHERE t.[Material] IS NULL',
    0,
    N'success',
    N'2025-11-05 10:13:39',
    7715.845346450806,
    0.95,
    NULL
);

-- Execution 25
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    49,
    4,
    N'KG_098',
    N'newdqschema',
    N'-- Generated SQL for RBP missing in SKU
SELECT * FROM source_table WHERE condition LIMIT 41',
    41,
    N'success',
    N'2025-10-30 18:39:10',
    876.5245634805298,
    0.8041091098700901,
    NULL
);

-- Execution 26
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    35,
    4,
    N'KG_098',
    N'newdqschema',
    N'SELECT * FROM rbp_gpu WHERE product_id NOT IN (SELECT product_id FROM skulifnr) LIMIT 46',
    46,
    N'success',
    N'2025-10-30 18:38:33',
    1896.4073905307578,
    0.9362959480337878,
    NULL
);

-- Execution 27
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    31,
    4,
    N'New_KG_123',
    N'newdqschema',
    N'SELECT DISTINCT s.*
FROM [brz_lnd_RBP_GPU] s
LEFT JOIN [brz_lnd_SKU_LIFNR_Excel] t ON s.[Material] = t.[Material]
WHERE t.[Material] IS NULL',
    50,
    N'success',
    N'2025-10-30 17:51:09',
    6865.552663803101,
    0.95,
    NULL
);

-- Execution 28
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    28,
    4,
    N'KG_450',
    N'newdqschema',
    N'SELECT DISTINCT s.*
FROM [brz_lnd_RBP_GPU] s
LEFT JOIN [brz_lnd_SKU_LIFNR_Excel] t ON s.[Material] = t.[Material]
WHERE t.[Material] IS NULL',
    50,
    N'success',
    N'2025-10-30 17:12:49',
    24153.658866882324,
    0.95,
    NULL
);

-- Execution 29
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    50,
    4,
    N'KG_098',
    N'newdqschema',
    N'-- Generated SQL for RBP missing in SKU
SELECT * FROM source_table WHERE condition LIMIT 44',
    44,
    N'success',
    N'2025-10-29 18:39:10',
    888.5960424697621,
    0.8734540031279237,
    NULL
);

-- Execution 30
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    36,
    4,
    N'KG_098',
    N'newdqschema',
    N'SELECT * FROM rbp_gpu WHERE product_id NOT IN (SELECT product_id FROM skulifnr) LIMIT 45',
    45,
    N'success',
    N'2025-10-29 18:38:33',
    680.412265342294,
    0.8855051420097475,
    NULL
);

-- Execution 31
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    51,
    4,
    N'KG_098',
    N'newdqschema',
    N'-- Generated SQL for RBP missing in SKU
SELECT * FROM source_table WHERE condition LIMIT 45',
    45,
    N'success',
    N'2025-10-28 18:39:10',
    1132.290464275209,
    0.8941285168698595,
    NULL
);

-- Execution 32
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    37,
    4,
    N'KG_098',
    N'newdqschema',
    N'SELECT * FROM rbp_gpu WHERE product_id NOT IN (SELECT product_id FROM skulifnr) LIMIT 54',
    54,
    N'success',
    N'2025-10-28 18:38:33',
    633.0247983816415,
    0.8978140152790021,
    NULL
);

-- Execution 33
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    14,
    4,
    N'KG_450',
    N'newdqschema',
    N'SELECT DISTINCT s.*
FROM [brz_lnd_RBP_GPU] s
LEFT JOIN [brz_lnd_SKU_LIFNR_Excel] t ON s.[Material] = t.[Material]
WHERE t.[Material] IS NULL',
    50,
    N'success',
    N'2025-10-28 17:24:29',
    7663.282871246338,
    0.95,
    NULL
);

-- Execution 34
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    13,
    4,
    N'KG_102',
    N'newdqschema',
    N'SELECT DISTINCT s.*
FROM [brz_lnd_RBP_GPU] s
LEFT JOIN [brz_lnd_SKU_LIFNR_Excel] t ON s.[Material] = t.[Material]
WHERE t.[Material] IS NULL',
    50,
    N'success',
    N'2025-10-28 16:20:48',
    7249.915838241577,
    0.95,
    NULL
);

-- Execution 35
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    12,
    4,
    N'KG_250',
    N'newdqschema',
    N'SELECT DISTINCT s.*
FROM [brz_lnd_RBP_GPU] s
LEFT JOIN [brz_lnd_SKU_LIFNR_Excel] t ON s.[Material] = t.[Material]
WHERE t.[Material] IS NULL',
    50,
    N'success',
    N'2025-10-28 15:40:58',
    6554.874658584595,
    0.95,
    NULL
);

-- Execution 36
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    52,
    4,
    N'KG_098',
    N'newdqschema',
    N'-- Generated SQL for RBP missing in SKU
SELECT * FROM source_table WHERE condition LIMIT 42',
    42,
    N'success',
    N'2025-10-27 18:39:10',
    2358.2569035107877,
    0.8220483082544199,
    NULL
);

-- Execution 37
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    38,
    4,
    N'KG_098',
    N'newdqschema',
    N'SELECT * FROM rbp_gpu WHERE product_id NOT IN (SELECT product_id FROM skulifnr) LIMIT 46',
    46,
    N'success',
    N'2025-10-27 18:38:33',
    527.5788332738699,
    0.8913791756463986,
    NULL
);

-- Execution 38
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    53,
    4,
    N'KG_098',
    N'newdqschema',
    N'-- Generated SQL for RBP missing in SKU
SELECT * FROM source_table WHERE condition LIMIT 49',
    49,
    N'success',
    N'2025-10-26 18:39:10',
    1833.555833672255,
    0.8137260628161465,
    NULL
);

-- Execution 39
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    39,
    4,
    N'KG_098',
    N'newdqschema',
    N'SELECT * FROM rbp_gpu WHERE product_id NOT IN (SELECT product_id FROM skulifnr) LIMIT 52',
    52,
    N'success',
    N'2025-10-26 18:38:33',
    1844.6652337063438,
    0.9023780333318802,
    NULL
);

-- Execution 40
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    54,
    4,
    N'KG_098',
    N'newdqschema',
    N'-- Generated SQL for RBP missing in SKU
SELECT * FROM source_table WHERE condition LIMIT 42',
    42,
    N'success',
    N'2025-10-25 18:39:10',
    1538.5162479746818,
    0.8561871185351567,
    NULL
);

-- Execution 41
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    40,
    4,
    N'KG_098',
    N'newdqschema',
    N'SELECT * FROM rbp_gpu WHERE product_id NOT IN (SELECT product_id FROM skulifnr) LIMIT 51',
    51,
    N'success',
    N'2025-10-25 18:38:33',
    1038.9435290661318,
    0.949109809444277,
    NULL
);

-- Execution 42
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    55,
    4,
    N'KG_098',
    N'newdqschema',
    N'-- Generated SQL for RBP missing in SKU
SELECT * FROM source_table WHERE condition LIMIT 43',
    43,
    N'success',
    N'2025-10-24 18:39:10',
    1621.7613207633667,
    0.9056970977213119,
    NULL
);

-- Execution 43
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    41,
    4,
    N'KG_098',
    N'newdqschema',
    N'SELECT * FROM rbp_gpu WHERE product_id NOT IN (SELECT product_id FROM skulifnr) LIMIT 49',
    49,
    N'success',
    N'2025-10-24 18:38:33',
    570.5232853135302,
    0.8731271433923011,
    NULL
);

-- Execution 44
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    16,
    5,
    N'KG_250',
    N'newdqschema',
    N'',
    0,
    N'failed',
    N'2025-10-28 21:07:34',
    5030.904769897461,
    0.3,
    N'Error executing query: Comparison query requires join columns to compare ''brz_lnd_RBP_GPU'' and ''brz_lnd_RBP_GPU'', but none were found. 

To fix this issue:
1. Ensure your Knowledge Graph has relationships between these tables
2. Use the ''Execute Queries'' tab and add explicit relationship pairs:
   Example: {
     "source_table": "brz_lnd_RBP_GPU",
     "source_column": "<matching_column>",
     "target_table": "brz_lnd_RBP_GPU",
     "target_column": "<matching_column>",
     "relationship_type": "MATCHES"
   }
3. Or add matching columns to your schema that can be auto-detected'
);

-- Execution 45
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    15,
    5,
    N'KG_450',
    N'newdqschema',
    N'',
    0,
    N'failed',
    N'2025-10-28 21:03:14',
    5679.183721542358,
    0.3,
    N'Error executing query: Comparison query requires join columns to compare ''brz_lnd_RBP_GPU'' and ''brz_lnd_RBP_GPU'', but none were found. 

To fix this issue:
1. Ensure your Knowledge Graph has relationships between these tables
2. Use the ''Execute Queries'' tab and add explicit relationship pairs:
   Example: {
     "source_table": "brz_lnd_RBP_GPU",
     "source_column": "<matching_column>",
     "target_table": "brz_lnd_RBP_GPU",
     "target_column": "<matching_column>",
     "relationship_type": "MATCHES"
   }
3. Or add matching columns to your schema that can be auto-detected'
);

-- Execution 46
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    25,
    6,
    N'KG_450',
    N'newdqschema',
    N'SELECT DISTINCT s.*, h.[OPS_PLANNER] AS [OPS_PLANNER]
FROM [brz_lnd_RBP_GPU] s
LEFT JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
LEFT JOIN [hana_material_master] h ON s.[Material] = h.[MATERIAL]
WHERE t.[PLANNING_SKU] IS NULL',
    35,
    N'success',
    N'2025-10-30 17:07:43',
    14844.302654266357,
    0.95,
    NULL
);

-- Execution 47
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    24,
    6,
    N'KG_450',
    N'newdqschema',
    N'',
    0,
    N'failed',
    N'2025-10-30 16:59:39',
    43363.19613456726,
    0.5,
    N'Error executing query: Comparison query requires both source and target tables'
);

-- Execution 48
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    23,
    6,
    N'KG_450',
    N'newdqschema',
    N'',
    0,
    N'failed',
    N'2025-10-30 16:55:23',
    17056.418418884277,
    0.5,
    N'Error executing query: Comparison query requires both source and target tables'
);

-- Execution 49
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    22,
    6,
    N'KG_450',
    N'newdqschema',
    N'SELECT DISTINCT s.* FROM [brz_lnd_RBP_GPU] s LEFT JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU] WHERE t.[PLANNING_SKU] IS NULL',
    35,
    N'success',
    N'2025-10-30 16:17:05',
    8414.825916290283,
    0.95,
    NULL
);

-- Execution 50
INSERT INTO kpi_execution_results (
    id, kpi_id, kg_name, select_schema, generated_sql,
    number_of_records, execution_status, execution_timestamp,
    execution_time_ms, confidence_score, error_message
) VALUES (
    21,
    6,
    N'KG_450',
    N'newdqschema',
    N'SELECT DISTINCT s.*
FROM [brz_lnd_RBP_GPU] s
LEFT JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
WHERE t.[PLANNING_SKU] IS NULL',
    35,
    N'success',
    N'2025-10-30 16:14:19',
    12860.9778881073,
    0.95,
    NULL
);

SET IDENTITY_INSERT kpi_execution_results OFF;
GO

-- Re-enable identity insert
SET IDENTITY_INSERT kpi_definitions OFF;
GO

-- Verify migration
SELECT COUNT(*) as 'Total KPIs' FROM kpi_definitions;
SELECT COUNT(*) as 'Total Executions' FROM kpi_execution_results;
GO

PRINT 'KPI Migration completed successfully!';