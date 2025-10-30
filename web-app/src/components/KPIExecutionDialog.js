import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Alert,
  CircularProgress,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
} from '@mui/material';
import { executeKPI, listKGs, listSchemas } from '../services/api';
import KPIExecutionStatusModal from './KPIExecutionStatusModal';

const KPIExecutionDialog = ({ open, kpi, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    kg_name: '',
    schemas: [],
    definitions: [],
    use_llm: true,
    min_confidence: 0.7,
    limit: 1000,
    db_type: 'sqlserver',
  });
  const [kgs, setKgs] = useState([]);
  const [schemas, setSchemas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState(null);

  // Status modal state
  const [statusModalOpen, setStatusModalOpen] = useState(false);
  const [executionId, setExecutionId] = useState(null);

  useEffect(() => {
    if (open) {
      fetchKGs();
      fetchSchemas();
      // Initialize with KPI's definition if available
      const initialDefinitions = kpi?.nl_definition ? [kpi.nl_definition] : [];
      setFormData({
        kg_name: '',
        schemas: [],
        definitions: initialDefinitions,
        use_llm: true,
        min_confidence: 0.7,
        limit: 1000,
        db_type: 'sqlserver',
      });
      setError(null);
    }
  }, [open, kpi]);

  const fetchKGs = async () => {
    try {
      const response = await listKGs();
      // Handle both array of objects and array of strings
      const kgList = response.data.graphs || [];
      const kgNames = kgList.map((kg) => (typeof kg === 'string' ? kg : kg.name));
      setKgs(kgNames);
    } catch (err) {
      setError('Failed to fetch Knowledge Graphs');
      console.error('Error fetching KGs:', err);
    }
  };

  const fetchSchemas = async () => {
    try {
      const response = await listSchemas();
      setSchemas(response.data.schemas || []);
    } catch (err) {
      setError('Failed to fetch Schemas');
      console.error('Error fetching schemas:', err);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSchemaChange = (e) => {
    const { value } = e.target;
    setFormData((prev) => ({
      ...prev,
      schemas: [value], // Single schema selection
    }));
  };

  const handleExecute = async () => {
    // Validation
    if (!formData.kg_name.trim()) {
      setError('Knowledge Graph name is required');
      return;
    }
    if (!formData.schemas || formData.schemas.length === 0) {
      setError('Schema is required');
      return;
    }
    if (!formData.definitions || formData.definitions.length === 0) {
      setError('At least one definition is required');
      return;
    }

    setExecuting(true);
    setError(null);

    try {
      const response = await executeKPI(kpi.id, formData);

      // Get execution ID from response
      const execId = response.data.execution_id;
      setExecutionId(execId);

      // Close this dialog and show status modal
      onClose();
      setStatusModalOpen(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to execute KPI');
      console.error('Error executing KPI:', err);
    } finally {
      setExecuting(false);
    }
  };

  const handleExecutionComplete = (execution) => {
    setStatusModalOpen(false);
    setExecutionId(null);
    onSuccess(); // Refresh the KPI list
  };

  const handleExecutionError = (errorMessage) => {
    setStatusModalOpen(false);
    setExecutionId(null);
    setError(errorMessage);
  };

  return (
    <>
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Execute KPI - {kpi?.name}</DialogTitle>
      <DialogContent sx={{ pt: 2 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* Knowledge Graph Dropdown */}
          <FormControl fullWidth disabled={executing || loading}>
            <InputLabel>Knowledge Graph</InputLabel>
            <Select
              name="kg_name"
              value={formData.kg_name}
              onChange={handleChange}
              label="Knowledge Graph"
            >
              <MenuItem value="">
                <em>Select a Knowledge Graph</em>
              </MenuItem>
              {kgs.map((kg) => (
                <MenuItem key={kg} value={kg}>
                  {kg}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Schema Dropdown */}
          <FormControl fullWidth disabled={executing}>
            <InputLabel>Schema</InputLabel>
            <Select
              name="schemas"
              value={formData.schemas[0] || ''}
              onChange={handleSchemaChange}
              label="Schema"
            >
              <MenuItem value="">
                <em>Select a Schema</em>
              </MenuItem>
              {schemas.map((schema) => (
                <MenuItem key={schema} value={schema}>
                  {schema}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* NL Definition (Read-only) */}
          <TextField
            label="NL Definition"
            name="definitions"
            value={formData.definitions[0] || ''}
            fullWidth
            disabled
            multiline
            rows={3}
            helperText="Definition from KPI"
          />

          {/* Min Confidence */}
          <TextField
            label="Min Confidence"
            name="min_confidence"
            type="number"
            value={formData.min_confidence}
            onChange={handleChange}
            fullWidth
            disabled={executing}
            inputProps={{ min: 0, max: 1, step: 0.1 }}
            helperText="Minimum confidence threshold (0.0 - 1.0)"
          />

          {/* Limit Records */}
          <TextField
            label="Limit Records"
            name="limit"
            type="number"
            value={formData.limit}
            onChange={handleChange}
            fullWidth
            disabled={executing}
            inputProps={{ min: 1, max: 100000 }}
            helperText="Maximum number of records to return"
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={executing}>
          Cancel
        </Button>
        <Button
          onClick={handleExecute}
          variant="contained"
          disabled={executing}
          startIcon={executing ? <CircularProgress size={20} /> : null}
        >
          {executing ? 'Executing...' : 'Execute'}
        </Button>
      </DialogActions>
    </Dialog>

    {/* Status Modal - Shows real-time execution progress */}
    <KPIExecutionStatusModal
      open={statusModalOpen}
      executionId={executionId}
      kpiName={kpi?.name}
      onComplete={handleExecutionComplete}
      onError={handleExecutionError}
    />
  </>
  );
};

export default KPIExecutionDialog;

