/**
 * KPI Analytics API Service - Separate Database Version
 * API client for the new KPI Analytics database with enhanced features
 */

import api from './api';

// Base URL for KPI Analytics endpoints (separate database)
// Note: Don't include /v1 here as it's already in the API base URL
const KPI_ANALYTICS_BASE = '/landing-kpi-mssql';

// ==================== KPI CRUD Operations ====================

/**
 * Create a new KPI definition
 * @param {Object} kpiData - KPI definition data
 * @param {string} kpiData.name - KPI name
 * @param {string} kpiData.alias_name - KPI alias
 * @param {string} kpiData.group_name - KPI group
 * @param {string} kpiData.description - KPI description
 * @param {string} kpiData.nl_definition - Natural language definition
 * @param {string} kpiData.business_priority - Priority (high, medium, low)
 * @param {number} kpiData.target_sla_seconds - Target SLA in seconds
 * @returns {Promise} API response
 */
export const createKPI = (kpiData) =>
  api.post(`${KPI_ANALYTICS_BASE}/kpis`, kpiData);

/**
 * Get all KPIs with latest execution status
 * @param {Object} params - Query parameters
 * @param {boolean} params.include_inactive - Include inactive KPIs
 * @returns {Promise} API response with KPIs array
 */
export const listKPIs = (params = {}) =>
  api.get(`${KPI_ANALYTICS_BASE}/kpis`, { params });

/**
 * Get KPI by ID
 * @param {number} kpiId - KPI ID
 * @returns {Promise} API response with KPI data
 */
export const getKPI = (kpiId) =>
  api.get(`${KPI_ANALYTICS_BASE}/kpis/${kpiId}`);

/**
 * Update KPI definition
 * @param {number} kpiId - KPI ID
 * @param {Object} kpiData - Updated KPI data
 * @returns {Promise} API response
 */
export const updateKPI = (kpiId, kpiData) =>
  api.put(`${KPI_ANALYTICS_BASE}/kpis/${kpiId}`, kpiData);

/**
 * Delete (deactivate) KPI
 * @param {number} kpiId - KPI ID
 * @returns {Promise} API response
 */
export const deleteKPI = (kpiId) =>
  api.delete(`${KPI_ANALYTICS_BASE}/kpis/${kpiId}`);

// ==================== KPI Execution Operations ====================

/**
 * Execute a KPI and store results in Analytics database
 * @param {number} kpiId - KPI ID
 * @param {Object} executionParams - Execution parameters
 * @param {string} executionParams.kg_name - Knowledge graph name
 * @param {string} executionParams.select_schema - Schema name
 * @param {string} executionParams.db_type - Database type
 * @param {number} executionParams.limit_records - Record limit
 * @param {boolean} executionParams.use_llm - Use LLM for SQL generation
 * @returns {Promise} API response with execution results
 */
export const executeKPI = (kpiId, executionParams) =>
  api.post(`${KPI_ANALYTICS_BASE}/kpis/${kpiId}/execute`, executionParams);

/**
 * Get execution history for a KPI
 * @param {number} kpiId - KPI ID
 * @param {Object} params - Query parameters
 * @param {number} params.limit - Number of executions to return
 * @returns {Promise} API response with execution history
 */
export const getKPIExecutions = (kpiId, params = {}) =>
  api.get(`${KPI_ANALYTICS_BASE}/kpis/${kpiId}/executions`, { params });

/**
 * Get detailed execution result by ID
 * @param {number} executionId - Execution ID
 * @returns {Promise} API response with detailed execution data
 */
export const getExecutionResult = (executionId) =>
  api.get(`${KPI_ANALYTICS_BASE}/executions/${executionId}`);

// ==================== Enhanced Features ====================

/**
 * Preview generated SQL for a query without executing it
 * @param {Object} previewData - Preview parameters
 * @param {string} previewData.query - Natural language query
 * @param {string} previewData.kg_name - Knowledge graph name
 * @param {string} previewData.select_schema - Schema name
 * @returns {Promise} API response with generated SQL
 */
export const previewSQL = (previewData) =>
  api.post(`${KPI_ANALYTICS_BASE}/sql-preview`, previewData);

/**
 * Health check for KPI Analytics service
 * @returns {Promise} API response with health status
 */
export const checkKPIAnalyticsHealth = () =>
  api.get(`${KPI_ANALYTICS_BASE}/health`);

// ==================== Analytics & Reporting ====================

/**
 * Get KPI performance analytics
 * @param {Object} params - Analytics parameters
 * @param {string} params.date_from - Start date (YYYY-MM-DD)
 * @param {string} params.date_to - End date (YYYY-MM-DD)
 * @param {string} params.group_name - Filter by group
 * @returns {Promise} API response with analytics data
 */
export const getKPIAnalytics = (params = {}) =>
  api.get(`${KPI_ANALYTICS_BASE}/analytics`, { params });

/**
 * Get execution trends for dashboard
 * @param {Object} params - Trend parameters
 * @param {number} params.days - Number of days to include
 * @returns {Promise} API response with trend data
 */
export const getExecutionTrends = (params = {}) =>
  api.get(`${KPI_ANALYTICS_BASE}/trends`, { params });

// ==================== Utility Functions ====================

/**
 * Check if ops_planner enhancement is available
 * @param {string} sql - SQL query to check
 * @returns {boolean} True if ops_planner is included
 */
export const hasOpsPlanner = (sql) => {
  return sql && sql.toLowerCase().includes('ops_planner');
};

/**
 * Check if query involves hana_material_master
 * @param {string} sql - SQL query to check
 * @returns {boolean} True if hana_material_master is involved
 */
export const involvesHanaMaster = (sql) => {
  return sql && sql.toLowerCase().includes('hana_material_master');
};

/**
 * Check if query involves material tables that should be enhanced
 * @param {string} sql - SQL query to check
 * @returns {boolean} True if material tables are involved
 */
export const involvesMaterialTables = (sql) => {
  if (!sql) return false;

  const materialTables = [
    'brz_lnd_rbp_gpu',
    'brz_lnd_ops_excel_gpu',
    'brz_lnd_sku_lifnr_excel',
    'brz_lnd_ibp_product_master',
    'brz_lnd_sar_excel_gpu',
    'brz_lnd_gpu_sku_in_skulifnr',
    'brz_lnd_sar_excel_nbu'
  ];

  const sqlLower = sql.toLowerCase();
  return materialTables.some(table => sqlLower.includes(table));
};

/**
 * Get enhancement status for a SQL query
 * @param {string} originalSql - Original SQL
 * @param {string} enhancedSql - Enhanced SQL
 * @returns {Object} Enhancement status information
 */
export const getEnhancementStatus = (originalSql, enhancedSql) => {
  const hasMaterialTables = involvesMaterialTables(originalSql);
  const hasMaterialMaster = involvesHanaMaster(enhancedSql);
  const hasOpsCol = hasOpsPlanner(enhancedSql);
  const wasEnhanced = originalSql !== enhancedSql;

  return {
    involvesMaterialTables: hasMaterialTables,
    hasMaterialMaster: hasMaterialMaster,
    hasOpsPlanner: hasOpsCol,
    wasEnhanced: wasEnhanced,
    shouldBeEnhanced: hasMaterialTables,
    enhancementWorking: hasMaterialTables ? (hasMaterialMaster && hasOpsCol) : true
  };
};

/**
 * Format execution time for display
 * @param {number} timeMs - Time in milliseconds
 * @returns {string} Formatted time string
 */
export const formatExecutionTime = (timeMs) => {
  if (!timeMs) return 'N/A';
  
  if (timeMs < 1000) {
    return `${Math.round(timeMs)}ms`;
  } else if (timeMs < 60000) {
    return `${(timeMs / 1000).toFixed(1)}s`;
  } else {
    const minutes = Math.floor(timeMs / 60000);
    const seconds = Math.floor((timeMs % 60000) / 1000);
    return `${minutes}m ${seconds}s`;
  }
};

/**
 * Get status color for execution status
 * @param {string} status - Execution status
 * @returns {string} Material-UI color name
 */
export const getStatusColor = (status) => {
  switch (status?.toLowerCase()) {
    case 'success':
      return 'success';
    case 'error':
    case 'failed':
      return 'error';
    case 'pending':
    case 'running':
      return 'warning';
    default:
      return 'default';
  }
};

/**
 * Get priority color for business priority
 * @param {string} priority - Business priority
 * @returns {string} Material-UI color name
 */
export const getPriorityColor = (priority) => {
  switch (priority?.toLowerCase()) {
    case 'high':
      return 'error';
    case 'medium':
      return 'warning';
    case 'low':
      return 'info';
    default:
      return 'default';
  }
};

export default {
  createKPI,
  listKPIs,
  getKPI,
  updateKPI,
  deleteKPI,
  executeKPI,
  getKPIExecutions,
  getExecutionResult,
  previewSQL,
  checkKPIAnalyticsHealth,
  getKPIAnalytics,
  getExecutionTrends,
  hasOpsPlanner,
  involvesHanaMaster,
  formatExecutionTime,
  getStatusColor,
  getPriorityColor
};
