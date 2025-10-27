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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { createKPI, updateKPI } from '../services/api';

const KPIForm = ({ open, kpi, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    alias_name: '',
    group_name: '',
    description: '',
    nl_definition: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const groups = ['Data Quality', 'Reconciliation', 'Performance', 'Compliance', 'Other'];

  // Initialize form with KPI data if editing
  useEffect(() => {
    if (kpi) {
      setFormData({
        name: kpi.name || '',
        alias_name: kpi.alias_name || '',
        group_name: kpi.group_name || '',
        description: kpi.description || '',
        nl_definition: kpi.nl_definition || '',
      });
    } else {
      setFormData({
        name: '',
        alias_name: '',
        group_name: '',
        description: '',
        nl_definition: '',
      });
    }
    setError(null);
  }, [kpi, open]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async () => {
    // Validation
    if (!formData.name.trim()) {
      setError('KPI name is required');
      return;
    }
    if (!formData.nl_definition.trim()) {
      setError('Natural language definition is required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      if (kpi) {
        // Update existing KPI
        await updateKPI(kpi.id, formData);
      } else {
        // Create new KPI
        await createKPI(formData);
      }
      onSuccess();
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save KPI');
      console.error('Error saving KPI:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{kpi ? 'Edit KPI' : 'Create New KPI'}</DialogTitle>
      <DialogContent sx={{ pt: 2 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* KPI Name */}
          <TextField
            label="KPI Name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            fullWidth
            placeholder="e.g., Product Match Rate"
            disabled={loading || (kpi ? true : false)}
            helperText={kpi ? 'Name cannot be changed' : ''}
          />

          {/* Alias Name */}
          <TextField
            label="Alias Name (Optional)"
            name="alias_name"
            value={formData.alias_name}
            onChange={handleChange}
            fullWidth
            placeholder="e.g., PMR"
            disabled={loading}
            helperText="Business-friendly short name"
          />

          {/* Group */}
          <FormControl fullWidth disabled={loading}>
            <InputLabel>Group (Optional)</InputLabel>
            <Select
              name="group_name"
              value={formData.group_name}
              onChange={handleChange}
              label="Group (Optional)"
            >
              <MenuItem value="">
                <em>None</em>
              </MenuItem>
              {groups.map((group) => (
                <MenuItem key={group} value={group}>
                  {group}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Description */}
          <TextField
            label="Description (Optional)"
            name="description"
            value={formData.description}
            onChange={handleChange}
            fullWidth
            multiline
            rows={2}
            placeholder="Detailed description of what this KPI measures"
            disabled={loading}
          />

          {/* NL Definition */}
          <TextField
            label="Natural Language Definition"
            name="nl_definition"
            value={formData.nl_definition}
            onChange={handleChange}
            fullWidth
            multiline
            rows={3}
            placeholder="e.g., Show me all products in RBP that are not in OPS"
            disabled={loading}
            helperText="The natural language query that defines this KPI"
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : null}
        >
          {loading ? 'Saving...' : kpi ? 'Update' : 'Create'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default KPIForm;

