-- Test the recursive CTE syntax that caused the original error
-- This tests the core pattern used in the fixed seed data script

SET NOCOUNT ON;

-- Test recursive CTE with MAXRECURSION (should work)
WITH Numbers AS (
    SELECT 1 as RowNum
    UNION ALL
    SELECT RowNum + 1
    FROM Numbers
    WHERE RowNum < 10  -- Small test with 10 records
),
MaterialData AS (
    SELECT 
        RowNum,
        CASE 
            WHEN RowNum <= 5 THEN 'GPU'
            ELSE 'NBU'
        END as ProductType
    FROM Numbers
)
SELECT 
    -- Material ID
    CASE 
        WHEN ProductType = 'GPU' THEN 'GPU-' + RIGHT('000' + CAST(RowNum AS VARCHAR), 3)
        ELSE 'NBU-' + RIGHT('000' + CAST(RowNum - 5 AS VARCHAR), 3)
    END as MATERIAL,
    
    -- Product Type
    ProductType,
    
    -- Test ROW_NUMBER() in SELECT (should work)
    ROW_NUMBER() OVER (ORDER BY RowNum) as TestRowNum

FROM MaterialData
OPTION (MAXRECURSION 10);

PRINT 'SQL syntax test completed successfully!';

SET NOCOUNT OFF;
