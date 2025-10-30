import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

const KPIManagement = () => {
  const [kpis, setKpis] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [rulesetFilter, setRulesetFilter] = useState('');
  const [rulesets, setRulesets] = useState([]);
  const [executingKpiId, setExecutingKpiId] = useState(null);
  const [executionResult, setExecutionResult] = useState(null);
  const [executionDialogOpen, setExecutionDialogOpen] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    kpi_name: '',
    kpi_description: '',
    kpi_type: 'match_rate',
    ruleset_id: '',
    warning_threshold: 80,
    critical_threshold: 70,
    comparison_operator: 'less_than',
    enabled: true,
  });

  // Load KPIs on mount
  useEffect(() => {
    loadKPIs();
    loadRulesets();
  }, [rulesetFilter]);

  const loadKPIs = async () => {
    try {
      setLoading(true);
      setError('');
      const url = rulesetFilter
        ? `/v1/reconciliation/kpi/list?ruleset_id=${rulesetFilter}`
        : '/v1/reconciliation/kpi/list';

      // Add cache-busting headers to prevent 304 responses
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0',
        },
        cache: 'no-store',
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error('Server returned non-JSON response. Backend may not be running.');
      }

      const data = await response.json();

      if (data.success) {
        setKpis(data.kpis || []);
      } else {
        setError(data.error || 'Failed to load KPIs');
      }
    } catch (err) {
      setError(`Error loading KPIs: ${err.message}`);
      console.error('KPI loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadRulesets = async () => {
    try {
      // Add cache-busting headers to prevent 304 responses
      const response = await fetch('/v1/reconciliation/rulesets', {
        method: 'GET',
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0',
        },
        cache: 'no-store',
      });

      console.log(`Rulesets API Response Status: ${response.status} ${response.statusText}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error('Server returned non-JSON response');
      }

      const data = await response.json();
      console.log('Raw rulesets response:', data);

      if (data.success && data.rulesets) {
        console.log('Rulesets array:', data.rulesets);
        console.log('First ruleset:', data.rulesets[0]);

        // Ensure rulesets have required fields
        const validRulesets = data.rulesets.filter(rs => rs.ruleset_id);
        setRulesets(validRulesets);
        console.log(`✅ Loaded ${validRulesets.length} valid rulesets`);
      } else if (Array.isArray(data)) {
        // Handle case where response is directly an array
        const validRulesets = data.filter(rs => rs.ruleset_id);
        setRulesets(validRulesets);
        console.log(`✅ Loaded ${validRulesets.length} valid rulesets (direct array)`);
      } else {
        console.warn('Unexpected rulesets response format:', data);
        setRulesets([]);
      }
    } catch (err) {
      console.error('❌ Error loading rulesets:', err);
      setRulesets([]);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  const handleCreateKPI = async () => {
    try {
      setLoading(true);
      setError('');
      setSuccess('');

      const payload = {
        kpi_name: formData.kpi_name,
        kpi_description: formData.kpi_description,
        kpi_type: formData.kpi_type,
        ruleset_id: formData.ruleset_id,
        thresholds: {
          warning_threshold: parseFloat(formData.warning_threshold),
          critical_threshold: parseFloat(formData.critical_threshold),
          comparison_operator: formData.comparison_operator,
        },
        enabled: formData.enabled,
      };

      const response = await fetch('/v1/reconciliation/kpi/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (data.success) {
        setSuccess(`KPI created successfully: ${formData.kpi_name}`);
        setOpenDialog(false);
        setFormData({
          kpi_name: '',
          kpi_description: '',
          kpi_type: 'match_rate',
          ruleset_id: '',
          warning_threshold: 80,
          critical_threshold: 70,
          comparison_operator: 'less_than',
          enabled: true,
        });
        loadKPIs();
      } else {
        setError(data.error || 'Failed to create KPI');
      }
    } catch (err) {
      setError(`Error creating KPI: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const executeKPI = async (kpi) => {
    try {
      setExecutingKpiId(kpi.kpi_id);
      setError('');

      const response = await fetch(`/v1/reconciliation/kpi/${kpi.kpi_id}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0',
        },
        cache: 'no-store',
        body: JSON.stringify({
          ruleset_id: kpi.ruleset_id,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.success) {
        setExecutionResult(data.result);
        setExecutionDialogOpen(true);
        setSuccess(`KPI executed successfully! Value: ${data.result.calculated_value}`);
        console.log('✅ KPI executed:', data.result);
      } else {
        setError(data.error || 'Failed to execute KPI');
      }
    } catch (err) {
      setError(`Error executing KPI: ${err.message}`);
      console.error('KPI execution error:', err);
    } finally {
      setExecutingKpiId(null);
    }
  };

  const kpiTypeLabels = {
    match_rate: 'Match Rate (%)',
    match_percentage: 'Match Percentage (%)',
    unmatched_source_count: 'Unmatched Source Count',
    unmatched_target_count: 'Unmatched Target Count',
    inactive_record_count: 'Inactive Record Count',
    data_quality_score: 'Data Quality Score',
  };

  return (
    <Container maxWidth="xl" sx={{ py: 1.5  }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" fontWeight="700" sx={{ mb: 0.25, lineHeight: 1.2, fontSize: '1.15rem' }} gutterBottom>
          KPI Management
        </Typography>
        <Typography variant="body2" fontSize="0.8rem" color="textSecondary">
          Create and manage Key Performance Indicators for reconciliation monitoring
        </Typography>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

      <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Filter by Ruleset</InputLabel>
          <Select
            value={rulesetFilter}
            label="Filter by Ruleset"
            onChange={(e) => setRulesetFilter(e.target.value)}
          >
            <MenuItem value="">All Rulesets</MenuItem>
            {rulesets.map((rs) => (
              <MenuItem key={rs.ruleset_id} value={rs.ruleset_id}>
                {rs.ruleset_name || rs.ruleset_id}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Create KPI
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
              <TableRow>
                <TableCell><strong>KPI Name</strong></TableCell>
                <TableCell><strong>Type</strong></TableCell>
                <TableCell><strong>Ruleset ID</strong></TableCell>
                <TableCell><strong>Warning Threshold</strong></TableCell>
                <TableCell><strong>Critical Threshold</strong></TableCell>
                <TableCell><strong>Status</strong></TableCell>
                <TableCell align="center"><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {kpis.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 3 }}>
                    No KPIs found. Create one to get started.
                  </TableCell>
                </TableRow>
              ) : (
                kpis.map((kpi) => (
                  <TableRow key={kpi.kpi_id}>
                    <TableCell>{kpi.kpi_name}</TableCell>
                    <TableCell>{kpiTypeLabels[kpi.kpi_type] || kpi.kpi_type}</TableCell>
                    <TableCell>{kpi.ruleset_id}</TableCell>
                    <TableCell>{kpi.thresholds.warning_threshold}</TableCell>
                    <TableCell>{kpi.thresholds.critical_threshold}</TableCell>
                    <TableCell>
                      <Typography
                        variant="body2"
                        sx={{
                          color: kpi.enabled ? 'green' : 'red',
                          fontWeight: 600,
                          fontSize: '0.8rem'
                        }}
                      >
                        {kpi.enabled ? 'Enabled' : 'Disabled'}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Button
                        size="small"
                        startIcon={<PlayArrowIcon />}
                        color="success"
                        onClick={() => executeKPI(kpi)}
                        disabled={executingKpiId === kpi.kpi_id}
                      >
                        {executingKpiId === kpi.kpi_id ? 'Executing...' : 'Execute'}
                      </Button>
                      <Button size="small" startIcon={<EditIcon />}>
                        Edit
                      </Button>
                      <Button size="small" startIcon={<DeleteIcon />} color="error">
                        Delete
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Create KPI Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New KPI</DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="KPI Name"
              name="kpi_name"
              value={formData.kpi_name}
              onChange={handleInputChange}
              fullWidth
              required
            />

            <TextField
              label="Description"
              name="kpi_description"
              value={formData.kpi_description}
              onChange={handleInputChange}
              fullWidth
              multiline
              rows={3}
            />

            <FormControl fullWidth>
              <InputLabel>KPI Type</InputLabel>
              <Select
                name="kpi_type"
                value={formData.kpi_type}
                label="KPI Type"
                onChange={handleInputChange}
              >
                {Object.entries(kpiTypeLabels).map(([key, label]) => (
                  <MenuItem key={key} value={key}>
                    {label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Ruleset</InputLabel>
              <Select
                name="ruleset_id"
                value={formData.ruleset_id}
                label="Ruleset"
                onChange={handleInputChange}
                required
              >
                {rulesets.length === 0 ? (
                  <MenuItem disabled>No rulesets available</MenuItem>
                ) : (
                  rulesets.map((rs) => (
                    <MenuItem key={rs.ruleset_id} value={rs.ruleset_id}>
                      {rs.ruleset_name || rs.ruleset_id}
                    </MenuItem>
                  ))
                )}
              </Select>
            </FormControl>

            <TextField
              label="Warning Threshold"
              name="warning_threshold"
              type="number"
              value={formData.warning_threshold}
              onChange={handleInputChange}
              fullWidth
            />

            <TextField
              label="Critical Threshold"
              name="critical_threshold"
              type="number"
              value={formData.critical_threshold}
              onChange={handleInputChange}
              fullWidth
            />

            <FormControl fullWidth>
              <InputLabel>Comparison Operator</InputLabel>
              <Select
                name="comparison_operator"
                value={formData.comparison_operator}
                label="Comparison Operator"
                onChange={handleInputChange}
              >
                <MenuItem value="less_than">Less Than</MenuItem>
                <MenuItem value="greater_than">Greater Than</MenuItem>
                <MenuItem value="equal_to">Equal To</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button
            onClick={handleCreateKPI}
            variant="contained"
            disabled={loading || !formData.kpi_name || !formData.ruleset_id}
          >
            {loading ? <CircularProgress size={24} /> : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* KPI Execution Result Dialog */}
      <Dialog open={executionDialogOpen} onClose={() => setExecutionDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>KPI Execution Result</DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          {executionResult && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box>
                <Typography variant="subtitle2" color="textSecondary">KPI Name</Typography>
                <Typography variant="body1">{executionResult.kpi_name}</Typography>
              </Box>

              <Box>
                <Typography variant="subtitle2" fontSize="0.8rem" color="textSecondary">Calculated Value</Typography>
                <Typography variant="h6" fontWeight="700" fontSize="0.95rem" sx={{ color: '#1976d2' }}>
                  {executionResult.calculated_value}
                </Typography>
              </Box>

              <Box>
                <Typography variant="subtitle2" color="textSecondary">Status</Typography>
                <Typography
                  variant="body1"
                  sx={{
                    fontWeight: 600,
                    fontSize: '0.8rem',
                    color:
                      executionResult.status === 'OK' ? 'green' :
                      executionResult.status === 'WARNING' ? 'orange' :
                      'red'
                  }}
                >
                  {executionResult.status}
                </Typography>
              </Box>

              <Box>
                <Typography variant="subtitle2" color="textSecondary">Execution Timestamp</Typography>
                <Typography variant="body2">
                  {new Date(executionResult.execution_timestamp).toLocaleString()}
                </Typography>
              </Box>

              <Box>
                <Typography variant="subtitle2" color="textSecondary">Result ID</Typography>
                <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                  {executionResult.result_id}
                </Typography>
              </Box>

              {executionResult.metrics && (
                <Box>
                  <Typography variant="subtitle2" color="textSecondary">Metrics</Typography>
                  <Typography variant="body2" component="pre" sx={{
                    backgroundColor: '#f5f5f5',
                    p: 1,
                    borderRadius: 1,
                    overflow: 'auto',
                    maxHeight: 200
                  }}>
                    {JSON.stringify(executionResult.metrics, null, 2)}
                  </Typography>
                </Box>
              )}

              {executionResult.thresholds && (
                <Box>
                  <Typography variant="subtitle2" color="textSecondary">Thresholds</Typography>
                  <Typography variant="body2">
                    Warning: {executionResult.thresholds.warning_threshold} |
                    Critical: {executionResult.thresholds.critical_threshold}
                  </Typography>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExecutionDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default KPIManagement;

