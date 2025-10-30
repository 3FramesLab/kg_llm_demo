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
import AssessmentIcon from '@mui/icons-material/Assessment';

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
    <Container maxWidth="xl" sx={{ py: 1.5  }}>
      {/* Header Section */}
      <Paper
        elevation={0}
        sx={{
          mb: 4,
          p: 4,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: 3,
          color: 'white'
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h5" fontWeight="700" sx={{ mb: 0.25, lineHeight: 1.2, fontSize: '1.15rem' }}>
              KPI Dashboard
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.95, fontWeight: 400, fontSize: '0.8rem' }}>
              Monitor key performance indicators and analyze evidence data
            </Typography>
          </Box>
          <Button
            variant="contained"
            size="small"
            startIcon={<RefreshIcon />}
            onClick={loadKPIs}
            disabled={loading}
            sx={{
              bgcolor: 'rgba(255, 255, 255, 0.2)',
              color: 'white',
              backdropFilter: 'blur(10px)',
              '&:hover': {
                bgcolor: 'rgba(255, 255, 255, 0.3)',
              },
              px: 2,
              py: 0.75,
              borderRadius: 1,
              textTransform: 'none',
              fontSize: '0.85rem',
              fontWeight: 700
            }}
          >
            Refresh Data
          </Button>
        </Box>
      </Paper>

      {error && (
        <Alert
          severity="error"
          sx={{
            mb: 3,
            borderRadius: 2,
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}
        >
          {error}
        </Alert>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
          <CircularProgress size={60} thickness={4} />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {kpis.length === 0 ? (
            <Grid item xs={12}>
              <Paper
                elevation={0}
                sx={{
                  p: 6,
                  textAlign: 'center',
                  borderRadius: 3,
                  border: '2px dashed #e0e0e0',
                  bgcolor: '#fafafa'
                }}
              >
                <AssessmentIcon sx={{ fontSize: 64, color: '#bdbdbd', mb: 2 }} />
                <Typography variant="h6" color="textSecondary" gutterBottom>
                  No KPIs Available
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Create a KPI in the KPI Management section to get started.
                </Typography>
              </Paper>
            </Grid>
          ) : (
            kpis.map((kpi) => (
              <Grid item xs={12} md={6} lg={4} key={kpi.kpi_id}>
                <Card
                  elevation={0}
                  sx={{
                    height: '100%',
                    borderRadius: 3,
                    border: '1px solid #e0e0e0',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 12px 24px rgba(0,0,0,0.1)',
                      borderColor: '#667eea'
                    }
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    {/* KPI Header */}
                    <Box sx={{ mb: 3 }}>
                      <Typography
                        variant="h6"
                        fontWeight="700"
                        fontSize="0.95rem"
                        sx={{
                          mb: 1,
                          color: '#1a1a1a'
                        }}
                      >
                        {kpi.kpi_name}
                      </Typography>
                      <Typography
                        variant="body2"
                        fontSize="0.8rem"
                        sx={{
                          color: '#666',
                          lineHeight: 1.6
                        }}
                      >
                        {kpi.kpi_description}
                      </Typography>
                    </Box>

                    {/* KPI Metadata */}
                    <Box sx={{ mb: 3, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Chip
                        label={kpiTypeLabels[kpi.kpi_type] || kpi.kpi_type}
                        size="small"
                        sx={{
                          bgcolor: '#e3f2fd',
                          color: '#1976d2',
                          fontWeight: 500,
                          fontSize: '0.7rem',
                          border: 'none'
                        }}
                      />
                      <Chip
                        label={`Ruleset: ${kpi.ruleset_id}`}
                        size="small"
                        sx={{
                          bgcolor: '#f3e5f5',
                          color: '#7b1fa2',
                          fontWeight: 500,
                          fontSize: '0.7rem',
                          border: 'none'
                        }}
                      />
                    </Box>

                    {/* Thresholds Section */}
                    <Box
                      sx={{
                        mb: 3,
                        p: 2.5,
                        bgcolor: '#f8f9fa',
                        borderRadius: 2,
                        border: '1px solid #e9ecef'
                      }}
                    >
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                        <Box>
                          <Typography variant="caption" fontSize="0.65rem" sx={{ color: '#666', display: 'block', mb: 0.5 }}>
                            Warning
                          </Typography>
                          <Typography variant="body2" fontSize="0.8rem" sx={{ fontWeight: 600, color: '#ed6c02' }}>
                            {kpi.thresholds.warning_threshold}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="caption" fontSize="0.65rem" sx={{ color: '#666', display: 'block', mb: 0.5 }}>
                            Critical
                          </Typography>
                          <Typography variant="body2" fontSize="0.8rem" sx={{ fontWeight: 600, color: '#d32f2f' }}>
                            {kpi.thresholds.critical_threshold}
                          </Typography>
                        </Box>
                      </Box>
                      <Typography variant="caption" fontSize="0.65rem" sx={{ color: '#666' }}>
                        Operator: <strong>{kpi.thresholds.comparison_operator}</strong>
                      </Typography>
                    </Box>

                    {/* Action Buttons */}
                    <Box sx={{ display: 'flex', gap: 1.5 }}>
                      <Button
                        variant="contained"
                        size="small"
                        fullWidth
                        endIcon={<ExpandMoreIcon />}
                        onClick={() => handleDrillDown(kpi)}
                        sx={{
                          py: 0.9,
                          borderRadius: 1,
                          fontSize: '0.85rem',
                          fontWeight: 700,
                          textTransform: 'none',
                          bgcolor: '#667eea',
                          '&:hover': {
                            bgcolor: '#5568d3'
                          }
                        }}
                      >
                        View Evidence
                      </Button>
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={<DownloadIcon />}
                        sx={{
                          py: 0.9,
                          px: 2,
                          borderRadius: 1,
                          fontSize: '0.85rem',
                          fontWeight: 700,
                          textTransform: 'none',
                          borderColor: '#e0e0e0',
                          color: '#666',
                          '&:hover': {
                            borderColor: '#667eea',
                            bgcolor: 'rgba(102, 126, 234, 0.04)'
                          }
                        }}
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
        PaperProps={{
          sx: {
            borderRadius: 3,
            maxHeight: '90vh'
          }
        }}
      >
        <DialogTitle
          sx={{
            bgcolor: '#f8f9fa',
            borderBottom: '1px solid #e0e0e0',
            py: 3
          }}
        >
          <Typography variant="h6" fontWeight="700" fontSize="0.95rem" sx={{ color: '#1a1a1a' }}>
            Evidence Data
          </Typography>
          {selectedKPI && (
            <Typography variant="body2" fontSize="0.8rem" sx={{ color: '#666', mt: 0.5 }}>
              {selectedKPI.kpi_name}
            </Typography>
          )}
        </DialogTitle>
        <DialogContent sx={{ pt: 3 }}>
          {selectedKPI && (
            <Paper
              elevation={0}
              sx={{
                mb: 3,
                p: 2.5,
                bgcolor: '#f0f7ff',
                borderRadius: 2,
                border: '1px solid #b3d9ff'
              }}
            >
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="caption" fontSize="0.65rem" sx={{ color: '#666', display: 'block', mb: 0.5 }}>
                    KPI Type
                  </Typography>
                  <Typography variant="body2" fontSize="0.8rem" sx={{ fontWeight: 600, color: '#1976d2' }}>
                    {kpiTypeLabels[selectedKPI.kpi_type] || selectedKPI.kpi_type}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" fontSize="0.65rem" sx={{ color: '#666', display: 'block', mb: 0.5 }}>
                    Ruleset ID
                  </Typography>
                  <Typography variant="body2" fontSize="0.8rem" sx={{ fontWeight: 600, color: '#1976d2' }}>
                    {selectedKPI.ruleset_id}
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          )}

          {/* Filter Controls */}
          <Paper
            elevation={0}
            sx={{
              mb: 3,
              p: 2.5,
              bgcolor: '#fafafa',
              borderRadius: 2,
              border: '1px solid #e0e0e0'
            }}
          >
            <Typography variant="subtitle2" fontSize="0.8rem" sx={{ mb: 2, fontWeight: 600, color: '#1a1a1a' }}>
              Filter Options
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
              <FormControl sx={{ minWidth: 220 }} size="small">
                <InputLabel>Filter by Status</InputLabel>
                <Select
                  value={matchStatusFilter}
                  label="Filter by Status"
                  onChange={(e) => setMatchStatusFilter(e.target.value)}
                  sx={{ bgcolor: 'white', borderRadius: 1.5 }}
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
                size="small"
                value={evidenceLimit}
                onChange={(e) => setEvidenceLimit(parseInt(e.target.value))}
                sx={{ width: 120, bgcolor: 'white', borderRadius: 1.5 }}
              />

              <Button
                variant="contained"
                size="small"
                onClick={() => handleDrillDown(selectedKPI)}
                disabled={evidenceLoading}
                sx={{
                  py: 0.9,
                  px: 2,
                  borderRadius: 1,
                  fontSize: '0.85rem',
                  fontWeight: 700,
                  textTransform: 'none',
                  bgcolor: '#667eea',
                  '&:hover': {
                    bgcolor: '#5568d3'
                  }
                }}
              >
                {evidenceLoading ? <CircularProgress size={20} sx={{ color: 'white' }} /> : 'Apply Filters'}
              </Button>
            </Box>
          </Paper>

          {/* Evidence Table */}
          {evidenceLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
              <CircularProgress size={50} thickness={4} />
            </Box>
          ) : (
            <TableContainer
              component={Paper}
              elevation={0}
              sx={{
                borderRadius: 2,
                border: '1px solid #e0e0e0',
                maxHeight: '500px'
              }}
            >
              <Table stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell
                      sx={{
                        bgcolor: '#f8f9fa',
                        fontWeight: 700,
                        color: '#1a1a1a',
                        borderBottom: '2px solid #e0e0e0',
                        py: 2
                      }}
                    >
                      Record ID
                    </TableCell>
                    <TableCell
                      sx={{
                        bgcolor: '#f8f9fa',
                        fontWeight: 700,
                        color: '#1a1a1a',
                        borderBottom: '2px solid #e0e0e0',
                        py: 2
                      }}
                    >
                      Status
                    </TableCell>
                    <TableCell
                      sx={{
                        bgcolor: '#f8f9fa',
                        fontWeight: 700,
                        color: '#1a1a1a',
                        borderBottom: '2px solid #e0e0e0',
                        py: 2
                      }}
                    >
                      Rule
                    </TableCell>
                    <TableCell
                      sx={{
                        bgcolor: '#f8f9fa',
                        fontWeight: 700,
                        color: '#1a1a1a',
                        borderBottom: '2px solid #e0e0e0',
                        py: 2
                      }}
                    >
                      Data
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {evidenceData.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={4} align="center" sx={{ py: 6, border: 'none' }}>
                        <Box sx={{ textAlign: 'center' }}>
                          <AssessmentIcon sx={{ fontSize: 48, color: '#bdbdbd', mb: 2 }} />
                          <Typography variant="body1" fontSize="0.8rem" sx={{ fontWeight: 600, color: '#666', mb: 1 }}>
                            No Evidence Records Found
                          </Typography>
                          <Typography variant="body2" fontSize="0.8rem" color="textSecondary" sx={{ mb: 2 }}>
                            This could mean:
                          </Typography>
                          <Box sx={{ textAlign: 'left', display: 'inline-block' }}>
                            <Typography variant="body2" fontSize="0.8rem" color="textSecondary" sx={{ mb: 0.5 }}>
                              • No reconciliation data exists for this ruleset
                            </Typography>
                            <Typography variant="body2" fontSize="0.8rem" color="textSecondary" sx={{ mb: 0.5 }}>
                              • No records match the selected filter
                            </Typography>
                            <Typography variant="body2" fontSize="0.8rem" color="textSecondary">
                              • Check browser console for detailed error logs
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ) : (
                    evidenceData.map((record, idx) => (
                      <TableRow
                        key={idx}
                        sx={{
                          '&:hover': {
                            bgcolor: '#f8f9fa'
                          },
                          '&:last-child td': {
                            borderBottom: 'none'
                          }
                        }}
                      >
                        <TableCell sx={{ py: 2, color: '#1a1a1a', fontWeight: 500 }}>
                          {record.record_id || 'N/A'}
                        </TableCell>
                        <TableCell sx={{ py: 2 }}>
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
                            sx={{ fontWeight: 600, fontSize: '0.7rem' }}
                          />
                        </TableCell>
                        <TableCell sx={{ py: 2, color: '#666' }}>
                          {record.rule_name || 'N/A'}
                        </TableCell>
                        <TableCell sx={{ py: 2 }}>
                          <Typography
                            variant="body2"
                            sx={{
                              maxWidth: 400,
                              overflow: 'auto',
                              color: '#666',
                              fontFamily: 'monospace',
                              fontSize: '0.75rem',
                              bgcolor: '#f8f9fa',
                              p: 1,
                              borderRadius: 1
                            }}
                          >
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
        <DialogActions
          sx={{
            px: 3,
            py: 2.5,
            borderTop: '1px solid #e0e0e0',
            bgcolor: '#fafafa'
          }}
        >
          <Button
            onClick={() => setEvidenceDialogOpen(false)}
            sx={{
              textTransform: 'none',
              fontWeight: 600,
              px: 3,
              py: 1,
              borderRadius: 1.5,
              color: '#666',
              '&:hover': {
                bgcolor: '#e0e0e0'
              }
            }}
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default KPIResults;

