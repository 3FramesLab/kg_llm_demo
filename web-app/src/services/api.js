import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/v1';

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
export const parseSchema = (schemaName) => api.post(`/schemas/${schemaName}/parse`);

// Knowledge Graph Operations
export const generateKG = (data) => api.post('/kg/generate', data);
export const listKGs = () => api.get('/kg');
export const getKGEntities = (kgName) => api.get(`/kg/${kgName}/entities`);
export const getKGRelationships = (kgName) => api.get(`/kg/${kgName}/relationships`);
export const queryKG = (kgName, query) => api.post(`/kg/${kgName}/query`, { query });
export const exportKG = (kgName) => api.get(`/kg/${kgName}/export`);
export const deleteKG = (kgName) => api.delete(`/kg/${kgName}`);

// LLM Features
export const extractEntities = (schemaName) => api.post(`/llm/extract/${schemaName}`);
export const analyzeSchema = (schemaName) => api.post(`/llm/analyze/${schemaName}`);

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

// MongoDB Reconciliation Results
export const listMongoDBResults = (params) => api.get('/reconciliation/results', { params });
export const getMongoDBResult = (documentId) => api.get(`/reconciliation/results/${documentId}`);
export const getMongoDBStatistics = (rulesetId) =>
  api.get('/reconciliation/statistics', { params: rulesetId ? { ruleset_id: rulesetId } : {} });
export const deleteMongoDBResult = (documentId) => api.delete(`/reconciliation/results/${documentId}`);

export default api;
