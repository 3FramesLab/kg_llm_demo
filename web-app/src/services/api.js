import axios from 'axios';

// Use relative path so requests go through nginx proxy to backend
export const API_BASE_URL = process.env.REACT_APP_API_URL || '/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health & Status
export const checkHealth = () => api.get('/health');
export const checkLLMStatus = () => api.get('/llm/status');

// Schema Management
export const listSchemas = () => api.get('/schemas');
export const getSchemaTable = (schemaName) => api.get(`/schemas/${schemaName}/tables`);
export const parseSchema = (schemaName) => api.post(`/schemas/${schemaName}/parse`);

// Knowledge Graph Operations
export const generateKG = (data) => api.post('/kg/generate', data);
export const listKGs = () => api.get('/kg');
export const getKGEntities = (kgName) => api.get(`/kg/${kgName}/entities`);
export const getKGRelationships = (kgName) => api.get(`/kg/${kgName}/relationships`);
export const getKGMetadata = (kgName) => api.get(`/kg/${kgName}/metadata`);
export const queryKG = (kgName, query) => api.post(`/kg/${kgName}/query`, { query });
export const exportKG = (kgName) => api.get(`/kg/${kgName}/export`);
export const deleteKG = (kgName) => api.delete(`/kg/${kgName}`);

// Table Aliases CRUD operations
export const getAllTableAliases = () => api.get('/table-aliases');
export const getKGTableAliases = (kgName) => api.get(`/kg/${kgName}/table-aliases`);
export const createTableAlias = (kgName, aliasData) => api.post(`/kg/${kgName}/table-aliases`, aliasData);
export const updateTableAlias = (kgName, tableName, aliasData) => api.put(`/kg/${kgName}/table-aliases/${tableName}`, aliasData);
export const deleteTableAlias = (kgName, tableName) => api.delete(`/kg/${kgName}/table-aliases/${tableName}`);

// LLM Features
export const extractEntities = (schemaName) => api.post(`/llm/extract/${schemaName}`);
export const analyzeSchema = (schemaName) => api.post(`/llm/analyze/${schemaName}`);
export const suggestRelationships = (data) => api.post('/llm/suggest-relationships', data);
export const generateTableAliases = (data) => api.post('/llm/generate-aliases', data);

// Reconciliation - Rules
export const generateRules = (data) => api.post('/reconciliation/generate', data);
export const listRulesets = () => api.get('/reconciliation/rulesets');
export const getRuleset = (rulesetId) => api.get(`/reconciliation/rulesets/${rulesetId}`);
export const deleteRuleset = (rulesetId) => api.delete(`/reconciliation/rulesets/${rulesetId}`);
export const exportRulesetSQL = (rulesetId) => api.get(`/reconciliation/rulesets/${rulesetId}/export/sql`);

// Reconciliation - Execution
export const validateRule = (data) => api.post('/reconciliation/validate', data);
export const executeReconciliation = (data) => api.post('/reconciliation/execute', data);

// Natural Language Relationships
export const parseNLRelationships = (data) => api.post('/kg/relationships/natural-language', data);
export const integrateNLRelationships = (data) => api.post('/kg/integrate-nl-relationships', data);
export const getKGStatistics = (data) => api.post('/kg/statistics', data);

// Natural Language Query Execution (NEW)
export const executeNLQueries = (data) => api.post('/kg/nl-queries/execute', data);

// MongoDB Reconciliation Results
export const listMongoDBResults = (params) => api.get('/reconciliation/results', { params });
export const getMongoDBResult = (documentId) => api.get(`/reconciliation/results/${documentId}`);
export const getMongoDBStatistics = (rulesetId) =>
  api.get('/reconciliation/statistics', { params: rulesetId ? { ruleset_id: rulesetId } : {} });
export const deleteMongoDBResult = (documentId) => api.delete(`/reconciliation/results/${documentId}`);

// Landing KPI CRUD Operations (Enhanced Analytics API)
export const createKPI = (data) => api.post('/landing-kpi-mssql/kpis', data);
export const listKPIs = (params) => api.get('/landing-kpi-mssql/kpis', { params });
export const getKPI = (kpiId) => api.get(`/landing-kpi-mssql/kpis/${kpiId}`);
export const updateKPI = (kpiId, data) => api.put(`/landing-kpi-mssql/kpis/${kpiId}`, data);
export const deleteKPI = (kpiId) => api.delete(`/landing-kpi-mssql/kpis/${kpiId}`);

// KPI Cache Management
export const updateKPICacheFlags = (kpiId, data) => api.patch(`/landing-kpi-mssql/kpis/${kpiId}/cache-flags`, data);
export const clearKPICacheFlags = (kpiId) => api.post(`/landing-kpi-mssql/kpis/${kpiId}/clear-cache`, { clear_cache: true });

// Landing KPI Execution (Enhanced Analytics API)
export const executeKPI = (kpiId, data) => api.post(`/landing-kpi-mssql/kpis/${kpiId}/execute`, data);
export const executeCachedKPI = (kpiId, data) => api.post(`/landing-kpi/kpis/${kpiId}/execute-cached`, data);
export const getKPIExecutions = async (kpiId, params) => {
  try {
    const response = await api.get(`/landing-kpi-mssql/kpis/${kpiId}/executions`, { params });

    // Handle different response formats
    if (response.data) {
      // Axios automatically parses JSON, so response.data is the parsed object
      if (response.data.success) {
        return {
          data: {
            success: true,
            executions: response.data.data?.executions || response.data.executions || []
          }
        };
      } else if (Array.isArray(response.data)) {
        return {
          data: {
            success: true,
            executions: response.data
          }
        };
      } else if (response.data.results) {
        return {
          data: {
            success: true,
            executions: [response.data.results]
          }
        };
      }
    }

    return response;
  } catch (error) {
    console.error('Error in getKPIExecutions:', error);
    throw error;
  }
};
export const getKPIExecutionResult = (executionId) => api.get(`/landing-kpi-mssql/executions/${executionId}`);
export const getKPIDrilldownData = (executionId, params) => api.get(`/landing-kpi-mssql/executions/${executionId}/drilldown`, { params });

// Enhanced KPI Analytics Features
export const previewSQL = (data) => api.post('/landing-kpi-mssql/sql-preview', data);
export const checkKPIAnalyticsHealth = () => api.get('/landing-kpi-mssql/health');
export const getKPIAnalytics = (params) => api.get('/landing-kpi-mssql/analytics', { params });
export const getExecutionTrends = (params) => api.get('/landing-kpi-mssql/trends', { params });

// KPI Dashboard (Enhanced Analytics API)
export const getDashboardData = () => api.get('/landing-kpi-mssql/dashboard');
export const getLatestResults = async (kpiId) => {
  try {
    const response = await api.get(`/landing-kpi-mssql/kpis/${kpiId}/latest-results`);
    return response;
  } catch (error) {
    // Enhanced error handling for better user experience
    if (error.response?.status === 404) {
      const errorDetail = error.response?.data?.detail || error.response?.data?.error || 'No execution results found';
      console.log(`ℹ️ No results found for KPI ${kpiId}: ${errorDetail}`);
    } else {
      console.error(`❌ Error fetching latest results for KPI ${kpiId}:`, error);
    }
    throw error;
  }
};

// Column Hints Management
export const getAllHints = () => api.get('/hints/');
export const getHintsStatistics = () => api.get('/hints/statistics');
export const getTableHints = (tableName) => api.get(`/hints/table/${tableName}`);
export const getColumnHints = (tableName, columnName) => api.get(`/hints/column/${tableName}/${columnName}`);
export const updateTableHints = (data) => api.post('/hints/table', data);
export const updateColumnHints = (data) => api.post('/hints/column', data);
export const updateColumnHintField = (tableName, columnName, fieldName, data) =>
  api.patch(`/hints/column/${tableName}/${columnName}/${fieldName}`, data);
export const deleteHints = (data) => api.delete('/hints/hints', { data });
export const searchHints = (data) => api.post('/hints/search', data);
export const createHintsVersion = (data) => api.post('/hints/version', data);
export const generateColumnHints = (data) => api.post('/hints/generate', data);
export const bulkGenerateHints = (data) => api.post('/hints/generate/bulk', data);
export const exportHints = (outputPath) => api.get('/hints/export', { params: { output_path: outputPath } });
export const importHints = (data) => api.post('/hints/import', data);

// Material Master Operations
// export const getUniqueOpsPlanner = () => api.get('/material-master/ops-planners'); // Disabled due to Java serialization issues

// Database Connection Management (for Schema Wizard)
export const testDatabaseConnection = (data) => api.post('/database/test-connection', data);
export const addDatabaseConnection = (data) => api.post('/database/connections', data);
export const listDatabaseConnections = () => api.get('/database/connections');
export const removeDatabaseConnection = (connectionId) => api.delete(`/database/connections/${connectionId}`);
export const listDatabasesFromConnection = (connectionId) => api.get(`/database/connections/${connectionId}/databases`);
export const listTablesFromDatabase = (connectionId, databaseName) => api.get(`/database/connections/${connectionId}/databases/${databaseName}/tables`);
export const getTableColumns = (connectionId, databaseName, tableName) => api.get(`/database/connections/${connectionId}/databases/${databaseName}/tables/${tableName}/columns`);
export const saveSchemaConfiguration = (data) => api.post('/database/schema-configuration', data);
export const getSchemaConfigurations = () => api.get('/database/schema-configuration');

export default api;
