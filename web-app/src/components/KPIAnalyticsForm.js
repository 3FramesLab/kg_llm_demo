/**
 * KPI Analytics Form - Enhanced form for separate KPI database
 * Supports new analytics features like business priority, SLA targets, etc.
 */

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
  Chip,
  Typography,
  Divider,
  Grid,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  Info as InfoIcon,
  Preview as PreviewIcon,
  Analytics as AnalyticsIcon
} from '@mui/icons-material';
import { createKPI, updateKPI, previewSQL } from '../services/kpiAnalyticsApi';
import SQLViewer from './SQLViewer';

const KPIAnalyticsForm = ({ open, kpi, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    alias_name: '',
    group_name: '',
    description: '',
    nl_definition: '',
    business_priority: 'medium',
    target_sla_seconds: 30,
    execution_frequency: 'on_demand',
    data_retention_days: 90
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sqlPreview, setSqlPreview] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  // Initialize form with KPI data if editing
  useEffect(() => {
    if (kpi) {
      setFormData({
        name: kpi.name || '',
        alias_name: kpi.alias_name || '',
        group_name: kpi.group_name || '',
        description: kpi.description || '',
        nl_definition: kpi.nl_definition || '',
        business_priority: kpi.business_priority || 'medium',
        target_sla_seconds: kpi.target_sla_seconds || 30,
        execution_frequency: kpi.execution_frequency || 'on_demand',
        data_retention_days: kpi.data_retention_days || 90
      });
    } else {
      setFormData({
        name: '',
        alias_name: '',
        group_name: '',
        description: '',
        nl_definition: '',
        business_priority: 'medium',
        target_sla_seconds: 30,
        execution_frequency: 'on_demand',
        data_retention_days: 90
      });
    }
    setError(null);
    setSqlPreview(null);
  }, [kpi, open]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handlePreviewSQL = async () => {
    if (!formData.nl_definition.trim()) {
      setError('Please enter a natural language definition first');
      return;
    }

    setPreviewLoading(true);
    try {
      const response = await previewSQL({
        query: formData.nl_definition,
        kg_name: 'default',
        select_schema: 'newdqschemanov'
      });

      setSqlPreview(response.data.data);
      setError(null);
    } catch (err) {
      setError('Failed to preview SQL: ' + (err.response?.data?.error || err.message));
      setSqlPreview(null);
    } finally {
      setPreviewLoading(false);
    }
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
      setError(err.response?.data?.error || 'Failed to save KPI');
      console.error('Error saving KPI:', err);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: { borderRadius: 2 }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 1,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white'
      }}>
        <AnalyticsIcon />
        {kpi ? 'Edit KPI' : 'Create New KPI'}
        <Typography variant="caption" sx={{ ml: 'auto', opacity: 0.9 }}>
          Analytics Database
        </Typography>
      </DialogTitle>
      
      <DialogContent sx={{ mt: 2 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
          {/* Basic Information */}
          <Typography variant="h6" color="primary" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <InfoIcon fontSize="small" />
            Basic Information
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12} sm={8}>
              <TextField
                label="KPI Name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                fullWidth
                required
                placeholder="e.g., Product Match Rate"
                disabled={loading}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                label="Alias"
                name="alias_name"
                value={formData.alias_name}
                onChange={handleChange}
                fullWidth
                placeholder="e.g., PMR"
                disabled={loading}
              />
            </Grid>
          </Grid>

          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Group Name"
                name="group_name"
                value={formData.group_name}
                onChange={handleChange}
                fullWidth
                placeholder="e.g., Data Quality"
                disabled={loading}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Business Priority</InputLabel>
                <Select
                  name="business_priority"
                  value={formData.business_priority}
                  onChange={handleChange}
                  label="Business Priority"
                  disabled={loading}
                >
                  <MenuItem value="high">
                    <Chip label="High" color="error" size="small" sx={{ mr: 1 }} />
                    High Priority
                  </MenuItem>
                  <MenuItem value="medium">
                    <Chip label="Medium" color="warning" size="small" sx={{ mr: 1 }} />
                    Medium Priority
                  </MenuItem>
                  <MenuItem value="low">
                    <Chip label="Low" color="info" size="small" sx={{ mr: 1 }} />
                    Low Priority
                  </MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          <TextField
            label="Description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            fullWidth
            multiline
            rows={2}
            placeholder="Brief description of what this KPI measures"
            disabled={loading}
          />

          <Divider />

          {/* Query Definition */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h6" color="primary">
              Query Definition
            </Typography>
            <Tooltip title="Preview generated SQL">
              <IconButton 
                onClick={handlePreviewSQL} 
                disabled={previewLoading || !formData.nl_definition.trim()}
                color="primary"
              >
                {previewLoading ? <CircularProgress size={20} /> : <PreviewIcon />}
              </IconButton>
            </Tooltip>
          </Box>

          <TextField
            label="Natural Language Definition"
            name="nl_definition"
            value={formData.nl_definition}
            onChange={handleChange}
            fullWidth
            required
            multiline
            rows={3}
            placeholder="e.g., Show me all products in RBP GPU that are not in OPS Excel GPU"
            disabled={loading}
            helperText="The natural language query that defines this KPI"
          />

          {/* SQL Preview */}
          {sqlPreview && (
            <SQLViewer
              originalSql={sqlPreview.generated_sql}
              enhancedSql={sqlPreview.enhanced_sql}
              title="SQL Preview"
              compact={true}
              defaultExpanded={true}
              showAlwaysVisible={false}
              showEnhancementInfo={true}
            />
          )}

          <Divider />

          {/* Analytics Settings */}
          <Typography variant="h6" color="primary">
            Analytics Settings
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <TextField
                label="Target SLA (seconds)"
                name="target_sla_seconds"
                type="number"
                value={formData.target_sla_seconds}
                onChange={handleChange}
                fullWidth
                disabled={loading}
                inputProps={{ min: 1, max: 300 }}
                helperText="Expected execution time"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>Execution Frequency</InputLabel>
                <Select
                  name="execution_frequency"
                  value={formData.execution_frequency}
                  onChange={handleChange}
                  label="Execution Frequency"
                  disabled={loading}
                >
                  <MenuItem value="on_demand">On Demand</MenuItem>
                  <MenuItem value="hourly">Hourly</MenuItem>
                  <MenuItem value="daily">Daily</MenuItem>
                  <MenuItem value="weekly">Weekly</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                label="Data Retention (days)"
                name="data_retention_days"
                type="number"
                value={formData.data_retention_days}
                onChange={handleChange}
                fullWidth
                disabled={loading}
                inputProps={{ min: 1, max: 365 }}
                helperText="How long to keep results"
              />
            </Grid>
          </Grid>
        </Box>
      </DialogContent>
      
      <DialogActions sx={{ p: 2.5, gap: 1 }}>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : null}
          sx={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
            }
          }}
        >
          {loading ? 'Saving...' : kpi ? 'Update KPI' : 'Create KPI'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default KPIAnalyticsForm;
