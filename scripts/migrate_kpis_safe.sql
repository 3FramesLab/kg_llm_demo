-- SAFE KPI Migration Script
-- Generated from SQLite to MS SQL Server
-- Handles duplicates by checking existing KPIs first
-- Generated on: 2025-11-06 12:49:01.297101
-- Database: KPI_Analytics

USE [KPI_Analytics];
GO

PRINT 'Starting SAFE KPI Migration...';
GO

-- KPI 1: Test KPI
PRINT 'Processing KPI: Test KPI';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'Test KPI')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 2: Test 123
PRINT 'Processing KPI: Test 123';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'Test 123')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 3: RBP missing in Ops Excel
PRINT 'Processing KPI: RBP missing in Ops Excel';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'RBP missing in Ops Excel')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 4: RBP missing in SKU
PRINT 'Processing KPI: RBP missing in SKU';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'RBP missing in SKU')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 5: RBP GPU Inactive in OPS Excel
PRINT 'Processing KPI: RBP GPU Inactive in OPS Excel';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'RBP GPU Inactive in OPS Excel')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 6: Test 1234
PRINT 'Processing KPI: Test 1234';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'Test 1234')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 7: RBP missing in SKU, Hana Status, Planner
PRINT 'Processing KPI: RBP missing in SKU, Hana Status, Planner';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'RBP missing in SKU, Hana Status, Planner')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 8: GPU Inactive in OPS
PRINT 'Processing KPI: GPU Inactive in OPS';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'GPU Inactive in OPS')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 9: Test098
PRINT 'Processing KPI: Test098';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'Test098')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 10: NONMatch
PRINT 'Processing KPI: NONMatch';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'NONMatch')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 11: NONMatch123
PRINT 'Processing KPI: NONMatch123';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'NONMatch123')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 12: GPU Planner Missing
PRINT 'Processing KPI: GPU Planner Missing';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'GPU Planner Missing')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 13: GPU Missing Planner
PRINT 'Processing KPI: GPU Missing Planner';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'GPU Missing Planner')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 14: GPU Missing Status
PRINT 'Processing KPI: GPU Missing Status';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'GPU Missing Status')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 15: NBU Missing Status
PRINT 'Processing KPI: NBU Missing Status';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'NBU Missing Status')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 16: SKU Missing GPU
PRINT 'Processing KPI: SKU Missing GPU';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'SKU Missing GPU')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 17: Try123
PRINT 'Processing KPI: Try123';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'Try123')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 18: Top Level Missing
PRINT 'Processing KPI: Top Level Missing';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'Top Level Missing')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 19: RBP SKU Missing in Master Product List
PRINT 'Processing KPI: RBP SKU Missing in Master Product List';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'RBP SKU Missing in Master Product List')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 20: RBP SKU Missing in SKULIFNR
PRINT 'Processing KPI: RBP SKU Missing in SKULIFNR';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'RBP SKU Missing in SKULIFNR')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 21: RBP SKU Obsolete in Master Product List
PRINT 'Processing KPI: RBP SKU Obsolete in Master Product List';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'RBP SKU Obsolete in Master Product List')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 22: NBU RBP SKU Obsolete in Master Product List
PRINT 'Processing KPI: NBU RBP SKU Obsolete in Master Product List';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'NBU RBP SKU Obsolete in Master Product List')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 23: NBU RBP SKU Missing in Master Product List
PRINT 'Processing KPI: NBU RBP SKU Missing in Master Product List';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'NBU RBP SKU Missing in Master Product List')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 24: NBU RBP SKU Missing in SKULIFNR
PRINT 'Processing KPI: NBU RBP SKU Missing in SKULIFNR';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'NBU RBP SKU Missing in SKULIFNR')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 25: GPU Master Product List with Planner Missing
PRINT 'Processing KPI: GPU Master Product List with Planner Missing';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'GPU Master Product List with Planner Missing')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 26: GPU Master Product List with Status Missing
PRINT 'Processing KPI: GPU Master Product List with Status Missing';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'GPU Master Product List with Status Missing')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 27: GPU Master Product List with Top Level Missing
PRINT 'Processing KPI: GPU Master Product List with Top Level Missing';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'GPU Master Product List with Top Level Missing')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 28: GPU Master Product List with Marketing Code Missing
PRINT 'Processing KPI: GPU Master Product List with Marketing Code Missing';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'GPU Master Product List with Marketing Code Missing')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 29: GPU Master Product List with PLC Code Missing
PRINT 'Processing KPI: GPU Master Product List with PLC Code Missing';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'GPU Master Product List with PLC Code Missing')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 30: NBU Master Product List with Planner Missing
PRINT 'Processing KPI: NBU Master Product List with Planner Missing';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'NBU Master Product List with Planner Missing')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 31: NBU Master Product List with Status Missing
PRINT 'Processing KPI: NBU Master Product List with Status Missing';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'NBU Master Product List with Status Missing')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 32: NBU Master Product List with Top-Level Name Missing
PRINT 'Processing KPI: NBU Master Product List with Top-Level Name Missing';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'NBU Master Product List with Top-Level Name Missing')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 33: NBU Master Product List with Item Group Missing
PRINT 'Processing KPI: NBU Master Product List with Item Group Missing';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'NBU Master Product List with Item Group Missing')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 34: Duplicates in NBU Master Product List
PRINT 'Processing KPI: Duplicates in NBU Master Product List';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'Duplicates in NBU Master Product List')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 35: GPU SKULIFNR SKU Missing in Master Product List present in SAR
PRINT 'Processing KPI: GPU SKULIFNR SKU Missing in Master Product List present in SAR';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'GPU SKULIFNR SKU Missing in Master Product List present in SAR')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 36: GPU Active/Inactive/Idle Master Product List SKU missing from SKULIFNR
PRINT 'Processing KPI: GPU Active/Inactive/Idle Master Product List SKU missing from SKULIFNR';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'GPU Active/Inactive/Idle Master Product List SKU missing from SKULIFNR')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 37: GPU SKUs in SKULIFNR obsolete in Master Product List
PRINT 'Processing KPI: GPU SKUs in SKULIFNR obsolete in Master Product List';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'GPU SKUs in SKULIFNR obsolete in Master Product List')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 38: NBU SKULIFNR SKU Missing in Master Product List present in SAR
PRINT 'Processing KPI: NBU SKULIFNR SKU Missing in Master Product List present in SAR';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'NBU SKULIFNR SKU Missing in Master Product List present in SAR')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 39: NBU Active/Inactive/Idle Master Product List SKU missing from SKULIFNR
PRINT 'Processing KPI: NBU Active/Inactive/Idle Master Product List SKU missing from SKULIFNR';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'NBU Active/Inactive/Idle Master Product List SKU missing from SKULIFNR')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 40: NBU SKUs in SKULIFNR obsolete in Master Product List
PRINT 'Processing KPI: NBU SKUs in SKULIFNR obsolete in Master Product List';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'NBU SKUs in SKULIFNR obsolete in Master Product List')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 41: GPU SAR(Non Zero) missing from Master Product List
PRINT 'Processing KPI: GPU SAR(Non Zero) missing from Master Product List';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'GPU SAR(Non Zero) missing from Master Product List')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 42: NBU SAR(Non Zero) missing from Master Product List
PRINT 'Processing KPI: NBU SAR(Non Zero) missing from Master Product List';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'NBU SAR(Non Zero) missing from Master Product List')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 43: GPU SAR SKU Missing in SKULIFNR
PRINT 'Processing KPI: GPU SAR SKU Missing in SKULIFNR';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'GPU SAR SKU Missing in SKULIFNR')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 44: GPU SAR(Non Zero) obsolete from Master Product List
PRINT 'Processing KPI: GPU SAR(Non Zero) obsolete from Master Product List';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'GPU SAR(Non Zero) obsolete from Master Product List')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- KPI 45: NBU SAR(Non Zero) obsolete from Master Product List
PRINT 'Processing KPI: NBU SAR(Non Zero) obsolete from Master Product List';

IF NOT EXISTS (SELECT 1 FROM kpi_definitions WHERE name = N'NBU SAR(Non Zero) obsolete from Master Product List')
BEGIN
    PRINT '  -> Inserting new KPI';
    INSERT INTO kpi_definitions (
        name, alias_name, group_name, description, nl_definition,
        created_at, updated_at, created_by, is_active
    ) VALUES (
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
END
ELSE
BEGIN
    PRINT '  -> KPI already exists, skipping';
END
GO

-- Sample Execution Results (Recent ones only)
PRINT 'Adding sample execution results...';
GO

-- Latest execution for KPI ID 2
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'Test 123';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
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
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 3
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'RBP missing in Ops Excel';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
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
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 4
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'RBP missing in SKU';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
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
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 5
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'RBP GPU Inactive in OPS Excel';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
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
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 6
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'Test 1234';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
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
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 7
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'RBP missing in SKU, Hana Status, Planner';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
        N'Nov5_2025_KG_100',
        N'newdqschemanov',
        N'SELECT DISTINCT s.*, h.[OPS_STATUS], h.[OPS_PLANNER]
FROM [brz_lnd_RBP_GPU] s
LEFT JOIN [brz_lnd_SKU_LIFNR_Excel] t ON s.[Material] = t.[Material]
LEFT JOIN [hana_material_master] h ON s.[Material] = h.[MATERIAL]
WHERE t.[Material] IS NULL',
        0,
        N'success',
        N'2025-11-05 10:31:16',
        7972.028017044067,
        0.95,
        NULL
    );
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 8
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'GPU Inactive in OPS';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
        N'New_1010',
        N'newdqschema',
        N'SELECT DISTINCT s.* FROM [brz_lnd_RBP_GPU] s INNER JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Product_Line] = t.[Product_Line] AND s.[Business_Unit] = t.[Business_Unit] WHERE t.[Active_Inactive] = ''Inactive''',
        180,
        N'success',
        N'2025-10-30 19:14:22',
        13593.589782714844,
        0.95,
        NULL
    );
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 9
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'Test098';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
        N'Nov_100_KG',
        N'newdqschemanov',
        N'SELECT DISTINCT s.* FROM [hana_material_master] s INNER JOIN [brz_lnd_IBP_Product_Master] t ON s.[MATERIAL] = t.[PRDID] WHERE s.[Product Type] = ''GPU''',
        350,
        N'success',
        N'2025-11-04 16:30:12',
        17090.29483795166,
        0.95,
        NULL
    );
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 10
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'NONMatch';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
        N'Nov5_2025_KG_100',
        N'newdqschemanov',
        N'SELECT DISTINCT s.*
FROM [brz_lnd_IBP_Product_Master] s
LEFT JOIN [hana_material_master] t ON s.[PRDID] = t.[MATERIAL]
WHERE t.[MATERIAL] IS NULL AND s.[PRODTYPE] = ''GPU''',
        150,
        N'success',
        N'2025-11-05 10:35:18',
        10362.892389297485,
        0.95,
        NULL
    );
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 11
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'NONMatch123';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
        N'Nov_100_KG',
        N'newdqschemanov',
        N'SELECT DISTINCT s.* FROM [hana_material_master] s LEFT JOIN [brz_lnd_IBP_Product_Master] t ON s.[MATERIAL] = t.[PRDID] WHERE t.[PRDID] IS NULL',
        300,
        N'success',
        N'2025-11-04 16:41:34',
        12728.789806365967,
        0.95,
        NULL
    );
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 12
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'GPU Planner Missing';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
        N'New_KG_1008',
        N'newdqschemanov',
        N'SELECT DISTINCT s.* FROM [hana_material_master] s INNER JOIN [brz_lnd_IBP_Product_Master] t ON s.[MATERIAL] = t.[PRDID] WHERE s.[OPS_PLANNER] IS NULL',
        200,
        N'success',
        N'2025-11-04 17:39:10',
        6742.026805877686,
        0.95,
        NULL
    );
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 13
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'GPU Missing Planner';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
        N'New_KG_1008',
        N'newdqschemanov',
        N'SELECT DISTINCT s.* FROM [hana_material_master] s INNER JOIN [brz_lnd_IBP_Product_Master] t ON s.[MATERIAL] = t.[PRDID] WHERE s.[Product Type] = ''GPU'' AND s.[OPS_PLANNER] IS NULL',
        100,
        N'success',
        N'2025-11-04 17:41:32',
        9843.206644058228,
        0.95,
        NULL
    );
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 14
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'GPU Missing Status';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
        N'New_KG_1008',
        N'newdqschemanov',
        N'SELECT DISTINCT s.* FROM [hana_material_master] s INNER JOIN [brz_lnd_IBP_Product_Master] t ON s.[MATERIAL] = t.[PRDID] WHERE s.[Product Type] = ''GPU'' AND s.[OPS_STATUS] IS NULL',
        49,
        N'success',
        N'2025-11-04 17:43:11',
        8367.681503295898,
        0.95,
        NULL
    );
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 15
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'NBU Missing Status';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
        N'Nov_5_111',
        N'newdqschemanov',
        N'SELECT DISTINCT s.*, h.[Product Type], h.[OPS_PLANNER]
FROM [brz_lnd_IBP_Product_Master] s
INNER JOIN [hana_material_master] h ON s.[PRDID] = h.[MATERIAL]
WHERE h.[Product Type] = ''NBU'' AND h.[OPS_PLANNER] IS NULL',
        100,
        N'success',
        N'2025-11-05 09:02:50',
        8767.157554626465,
        0.95,
        NULL
    );
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 16
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'SKU Missing GPU';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
        N'Nov5_2025_KG_100',
        N'newdqschemanov',
        N'SELECT DISTINCT s.*
FROM [brz_lnd_GPU_SKU_IN_SKULIFNR] s
INNER JOIN [brz_lnd_IBP_Product_Master] t ON s.[PLANNING_SKU] = t.[PRDID]
WHERE s.[Prd_Type] = ''GPU''',
        350,
        N'success',
        N'2025-11-05 09:58:28',
        14301.267385482788,
        0.95,
        NULL
    );
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 17
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'Try123';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
        N'Nov5_2025_KG_100',
        N'newdqschemanov',
        N'SELECT DISTINCT s.*, h.[Product Type], h.[OPS_PLANNER]
FROM [brz_lnd_IBP_Product_Master] s
INNER JOIN [hana_material_master] h ON s.[PRDID] = h.[MATERIAL]
WHERE h.[Product Type] = ''NBU'' AND h.[OPS_PLANNER] IS NULL',
        100,
        N'success',
        N'2025-11-05 10:01:06',
        15616.727828979492,
        0.95,
        NULL
    );
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 18
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'Top Level Missing';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
        N'Nov5_2025_KG_100',
        N'newdqschemanov',
        N'SELECT DISTINCT s.*
FROM [brz_lnd_IBP_Product_Master] s
LEFT JOIN [hana_material_master] t ON s.[PRDID] = t.[MATERIAL]
WHERE t.[MATERIAL] IS NULL
AND s.[PRODTYPE] = ''NBU''
AND s.[ZTOPLVLNAME] IS NULL',
        0,
        N'success',
        N'2025-11-05 10:36:41',
        7390.438079833984,
        0.95,
        NULL
    );
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 19
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'RBP SKU Missing in Master Product List';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
        N'KG_Nov6_123',
        N'dqschema',
        N'SELECT DISTINCT s.*
FROM [brz_lnd_RBP_GPU] s
LEFT JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU]
WHERE t.[PLANNING_SKU] IS NULL',
        150,
        N'success',
        N'2025-11-06 11:35:53',
        10795.426368713379,
        0.95,
        NULL
    );
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 20
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'RBP SKU Missing in SKULIFNR';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
        N'Nov5_2025_KG_100',
        N'newdqschemanov',
        N'SELECT DISTINCT s.*
FROM [brz_lnd_RBP_GPU] s
LEFT JOIN [brz_lnd_SKU_LIFNR_Excel] t ON s.[Material] = t.[Material]
WHERE t.[Material] IS NULL',
        500,
        N'success',
        N'2025-11-06 07:52:05',
        8945.707559585571,
        0.95,
        NULL
    );
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 21
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'RBP SKU Obsolete in Master Product List';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
        N'Nov5_2025_KG_100',
        N'newdqschemanov',
        N'SELECT DISTINCT s.* FROM [brz_lnd_RBP_GPU] s INNER JOIN [brz_lnd_OPS_EXCEL_GPU] t ON s.[Material] = t.[PLANNING_SKU] WHERE t.[Active_Inactive] = ''Inactive''',
        100,
        N'success',
        N'2025-11-06 07:53:08',
        9238.191366195679,
        0.95,
        NULL
    );
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 22
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'NBU RBP SKU Obsolete in Master Product List';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
        N'KG_Nov6_123',
        N'dqschema',
        N'SELECT DISTINCT s.*
FROM [brz_lnd_RBP_NBU] s
LEFT JOIN [brz_lnd_OPS_EXCEL_NBU] t ON s.[Material] = t.[MATERIAL_PN]
WHERE t.[MATERIAL_PN] IS NULL',
        0,
        N'success',
        N'2025-11-06 08:22:29',
        12194.486618041992,
        0.3,
        NULL
    );
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 25
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'GPU Master Product List with Planner Missing';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
        N'KG_Nov6_123',
        N'dqschema',
        N'SELECT DISTINCT s.*
FROM [brz_lnd_IBP_Product_Master] s
LEFT JOIN [hana_material_master] t ON s.[PRDID] = t.[MATERIAL]
WHERE t.[MATERIAL] IS NULL AND t.[OPS_PLANNER] IS NULL',
        300,
        N'success',
        N'2025-11-06 09:24:11',
        10063.3544921875,
        0.95,
        NULL
    );
    PRINT '  -> Added execution result';
END
GO

-- Latest execution for KPI ID 26
-- Get the new KPI ID after migration
DECLARE @kpi_id INT;
SELECT @kpi_id = id FROM kpi_definitions WHERE name = N'GPU Master Product List with Status Missing';

IF @kpi_id IS NOT NULL
BEGIN
    INSERT INTO kpi_execution_results (
        kpi_id, kg_name, select_schema, generated_sql,
        number_of_records, execution_status, execution_timestamp,
        execution_time_ms, confidence_score, error_message
    ) VALUES (
        @kpi_id,
        N'KG_Nov6_123',
        N'dqschema',
        N'SELECT DISTINCT s.*
FROM [brz_lnd_IBP_Product_Master] s
LEFT JOIN [hana_material_master] t ON s.[PRDID] = t.[MATERIAL]
WHERE t.[MATERIAL] IS NULL AND s.[PRODTYPE] = ''GPU''',
        150,
        N'success',
        N'2025-11-06 09:12:25',
        6859.87401008606,
        0.95,
        NULL
    );
    PRINT '  -> Added execution result';
END
GO

-- Final Verification
PRINT 'Migration completed! Summary:';
SELECT COUNT(*) as 'Total KPIs' FROM kpi_definitions;
SELECT COUNT(*) as 'Total Executions' FROM kpi_execution_results;

-- Show sample of migrated KPIs
PRINT 'Sample migrated KPIs:';
SELECT TOP 10 name, group_name, created_at FROM kpi_definitions ORDER BY created_at DESC;
GO

PRINT 'SAFE KPI Migration completed successfully!';