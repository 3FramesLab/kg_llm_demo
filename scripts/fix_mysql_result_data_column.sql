-- Fix MySQL result_data column size issue
-- The result_data column is currently TEXT (64KB limit) but needs to be LONGTEXT (4GB limit)
-- to handle large result sets from cached SQL execution

-- Check current column type
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'KPI_Analytics' 
  AND TABLE_NAME = 'kpi_execution_results' 
  AND COLUMN_NAME IN ('result_data', 'evidence_data', 'generated_sql', 'error_message');

-- Fix result_data column to handle large datasets
ALTER TABLE kpi_execution_results 
MODIFY COLUMN result_data LONGTEXT;

-- Also fix evidence_data column for consistency
ALTER TABLE kpi_execution_results 
MODIFY COLUMN evidence_data LONGTEXT;

-- Fix generated_sql column to handle very long SQL queries
ALTER TABLE kpi_execution_results 
MODIFY COLUMN generated_sql LONGTEXT;

-- Fix error_message column to handle detailed error messages
ALTER TABLE kpi_execution_results 
MODIFY COLUMN error_message LONGTEXT;

-- Verify the changes
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'KPI_Analytics' 
  AND TABLE_NAME = 'kpi_execution_results' 
  AND COLUMN_NAME IN ('result_data', 'evidence_data', 'generated_sql', 'error_message');

-- Show success message
SELECT 'MySQL column types updated successfully!' as status;
