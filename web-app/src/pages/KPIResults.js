import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
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
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import DownloadIcon from '@mui/icons-material/Download';
import RefreshIcon from '@mui/icons-material/Refresh';

const KPIResults = () => {
  const [kpis, setKpis] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedKPI, setSelectedKPI] = useState(null);
  const [evidenceDialogOpen, setEvidenceDialogOpen] = useState(false);
  const [evidenceData, setEvidenceData] = useState([]);
  const [evidenceLoading, setEvidenceLoading] = useState(false);
  const [matchStatusFilter, setMatchStatusFilter] = useState('');
  const [evidenceLimit, setEvidenceLimit] = useState(100);

  useEffect(() => {
    loadKPIs();
  }, []);

  const loadKPIs = async () => {
    try {
      setLoading(true);
      // Add cache-busting headers to prevent 304 responses
      const response = await fetch('/v1/reconciliation/kpi/list', {
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

  const handleDrillDown = async (kpi) => {
    try {
      setSelectedKPI(kpi);
      setEvidenceLoading(true);
      setEvidenceData([]);
      setError('');

      const payload = {
        kpi_id: kpi.kpi_id,
        match_status: matchStatusFilter || null,
        limit: evidenceLimit,
        offset: 0,
      };

      console.log('📊 Loading evidence for KPI:', kpi.kpi_id);
      console.log('📋 Payload:', payload);

      // Add cache-busting headers to prevent 304 responses
      const response = await fetch(`/v1/reconciliation/kpi/${kpi.kpi_id}/evidence`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0',
        },
        cache: 'no-store',
        body: JSON.stringify(payload),
      });

      console.log(`📡 Evidence API Response Status: ${response.status} ${response.statusText}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error('Server returned non-JSON response');
      }

      const data = await response.json();

      console.log('✅ Evidence response:', data);
      console.log(`📊 Total records: ${data.total_count}`);
      console.log(`📋 Evidence records: ${data.evidence_records?.length || 0}`);

      if (data.success) {
        setEvidenceData(data.evidence_records || []);
        setEvidenceDialogOpen(true);

        if (data.total_count === 0) {
          console.warn('⚠️ No evidence records found for this KPI');
        }
      } else {
        const errorMsg = data.error || 'Failed to load evidence data';
        console.error('❌ Error:', errorMsg);
        setError(errorMsg);
      }
    } catch (err) {
      const errorMsg = `Error loading evidence: ${err.message}`;
      console.error('❌ Exception:', err);
      setError(errorMsg);
    } finally {
      setEvidenceLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pass':
        return 'success';
      case 'warning':
        return 'warning';
      case 'critical':
        return 'error';
      default:
        return 'default';
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

  const matchStatusLabels = {
    matched: 'Matched',
    unmatched_source: 'Unmatched Source',
    unmatched_target: 'Unmatched Target',
    inactive: 'Inactive',
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            KPI Results
          </Typography>
          <Typography variant="body1" color="textSecondary">
            View KPI calculations and drill down into evidence data
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={loadKPIs}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={2}>
          {kpis.length === 0 ? (
            <Grid item xs={12}>
              <Alert severity="info">
                No KPIs found. Create a KPI in the KPI Management section to get started.
              </Alert>
            </Grid>
          ) : (
            kpis.map((kpi) => (
              <Grid item xs={12} md={6} key={kpi.kpi_id}>
                <Card>
                  <CardContent>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="h6" gutterBottom>
                        {kpi.kpi_name}
                      </Typography>
                      <Typography variant="body2" color="textSecondary" gutterBottom>
                        {kpi.kpi_description}
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Chip
                        label={kpiTypeLabels[kpi.kpi_type] || kpi.kpi_type}
                        size="small"
                        variant="outlined"
                      />
                      <Chip
                        label={`Ruleset: ${kpi.ruleset_id}`}
                        size="small"
                        variant="outlined"
                      />
                    </Box>

                    <Box sx={{ mb: 2, p: 2, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
                      <Typography variant="body2" color="textSecondary">
                        Thresholds
                      </Typography>
                      <Typography variant="body2">
                        Warning: {kpi.thresholds.warning_threshold} | Critical:{' '}
                        {kpi.thresholds.critical_threshold}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Operator: {kpi.thresholds.comparison_operator}
                      </Typography>
                    </Box>

                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button
                        variant="contained"
                        size="small"
                        endIcon={<ExpandMoreIcon />}
                        onClick={() => handleDrillDown(kpi)}
                      >
                        View Evidence
                      </Button>
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={<DownloadIcon />}
                      >
                        Export
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))
          )}
        </Grid>
      )}

      {/* Evidence Drill-Down Dialog */}
      <Dialog
        open={evidenceDialogOpen}
        onClose={() => setEvidenceDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          Evidence Data - {selectedKPI?.kpi_name}
        </DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          {selectedKPI && (
            <Box sx={{ mb: 2, p: 1.5, backgroundColor: '#f0f7ff', borderRadius: 1, border: '1px solid #b3d9ff' }}>
              <Typography variant="body2" color="textSecondary">
                <strong>KPI Type:</strong> {selectedKPI.kpi_type}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                <strong>Ruleset:</strong> {selectedKPI.ruleset_id}
              </Typography>
            </Box>
          )}

          <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Filter by Status</InputLabel>
              <Select
                value={matchStatusFilter}
                label="Filter by Status"
                onChange={(e) => setMatchStatusFilter(e.target.value)}
              >
                <MenuItem value="">All Statuses</MenuItem>
                {Object.entries(matchStatusLabels).map(([key, label]) => (
                  <MenuItem key={key} value={key}>
                    {label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              label="Limit"
              type="number"
              value={evidenceLimit}
              onChange={(e) => setEvidenceLimit(parseInt(e.target.value))}
              sx={{ width: 100 }}
            />

            <Button
              variant="contained"
              onClick={() => handleDrillDown(selectedKPI)}
              disabled={evidenceLoading}
            >
              {evidenceLoading ? <CircularProgress size={24} /> : 'Refresh'}
            </Button>
          </Box>

          {evidenceLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer>
              <Table size="small">
                <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
                  <TableRow>
                    <TableCell><strong>Record ID</strong></TableCell>
                    <TableCell><strong>Status</strong></TableCell>
                    <TableCell><strong>Rule</strong></TableCell>
                    <TableCell><strong>Data</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {evidenceData.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={4} align="center" sx={{ py: 3 }}>
                        <Box sx={{ textAlign: 'center' }}>
                          <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                            ℹ️ No evidence records found
                          </Typography>
                          <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mb: 1 }}>
                            This could mean:
                          </Typography>
                          <Typography variant="caption" color="textSecondary" sx={{ display: 'block' }}>
                            • No reconciliation data exists for this ruleset
                          </Typography>
                          <Typography variant="caption" color="textSecondary" sx={{ display: 'block' }}>
                            • No records match the selected filter
                          </Typography>
                          <Typography variant="caption" color="textSecondary" sx={{ display: 'block' }}>
                            • Check browser console for detailed error logs
                          </Typography>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ) : (
                    evidenceData.map((record, idx) => (
                      <TableRow key={idx}>
                        <TableCell>{record.record_id || 'N/A'}</TableCell>
                        <TableCell>
                          <Chip
                            label={matchStatusLabels[record.match_status] || record.match_status}
                            size="small"
                            color={
                              record.match_status === 'matched'
                                ? 'success'
                                : record.match_status === 'inactive'
                                ? 'warning'
                                : 'error'
                            }
                          />
                        </TableCell>
                        <TableCell>{record.rule_name || 'N/A'}</TableCell>
                        <TableCell>
                          <Typography variant="body2" sx={{ maxWidth: 300, overflow: 'auto' }}>
                            {JSON.stringify(record.record_data).substring(0, 100)}...
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEvidenceDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default KPIResults;

