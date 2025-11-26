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
  useMediaQuery,
  useTheme,
} from '@mui/material';
import { executeKPI, listKGs, listSchemas } from '../../services/api';
import KPIExecutionStatusModal from './KPIExecutionStatusModal';

const KPIExecutionDialog = ({ open, kpi, onClose, onSuccess, fullScreen }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [formData, setFormData] = useState({
    kg_name: '',
    schemas: [],
    select_schema: '', // Add explicit select_schema field
    definitions: [],
    use_llm: true,
    min_confidence: 0.8, // Hardcoded value
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
        min_confidence: 0.8, // Hardcoded value
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
      const kgList = response.data.data || []; // Fixed: changed from 'graphs' to 'data'
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
      schemas: [value], // Keep for backward compatibility
      select_schema: value, // Add explicit select_schema
    }));
  };

  const handleExecute = async () => {
    // Validation
    if (!formData.kg_name.trim()) {
      setError('Knowledge Graph name is required');
      return;
    }
    if (formData.kg_name.toLowerCase() === 'default') {
      setError('Please select a valid Knowledge Graph (not "default")');
      return;
    }
    if (!formData.select_schema || formData.select_schema.trim() === '') {
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
    console.log('KPI execution completed:', execution);
    console.log('Calling onSuccess handler');
    setStatusModalOpen(false);
    setExecutionId(null);
    onSuccess(); // This will trigger handleExecutionSuccess in LandingKPIManagement
  };

  const handleExecutionError = (errorMessage) => {
    setStatusModalOpen(false);
    setExecutionId(null);
    setError(errorMessage);
  };

  const handleStatusModalClose = () => {
    setStatusModalOpen(false);
    setExecutionId(null);
  };

  return (
    <>
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      fullScreen={fullScreen || isMobile}
    >
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
            rows={isMobile ? 2 : 3}
            helperText="Definition from KPI"
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
      <DialogActions sx={{ px: isMobile ? 2 : 3, pb: isMobile ? 2 : 1 }}>
        <Button
          onClick={onClose}
          disabled={executing}
          fullWidth={isMobile}
          size="small"
        >
          Cancel
        </Button>
        <Button
          onClick={handleExecute}
          variant="contained"
          disabled={
            executing ||
            !formData.kg_name ||
            formData.kg_name.trim() === '' ||
            formData.kg_name.toLowerCase() === 'default' ||
            !formData.select_schema ||
            formData.select_schema.trim() === ''
          }
          startIcon={executing ? <CircularProgress size={20} /> : null}
          fullWidth={isMobile}
          size="small"
          sx={{ ml: isMobile ? 0 : 1, mt: isMobile ? 1 : 0 }}
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
      onClose={handleStatusModalClose}
    />
  </>
  );
};

export default KPIExecutionDialog;

