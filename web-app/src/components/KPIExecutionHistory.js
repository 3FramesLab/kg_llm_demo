import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  CircularProgress,
  Alert,
  Box,
  Chip,
  IconButton,
  Tooltip,
  Typography,
  Collapse,
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Error as ErrorIcon,
  Code as CodeIcon
} from '@mui/icons-material';
import { getKPIExecutions } from '../services/api';

const KPIExecutionHistory = ({ open, kpi, onClose, onViewDrilldown }) => {
  const [executions, setExecutions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedRows, setExpandedRows] = useState(new Set());

  useEffect(() => {
    if (open && kpi) {
      fetchExecutions();
    }
  }, [open, kpi]);

  const fetchExecutions = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getKPIExecutions(kpi.id);
      // Handle both old format (response.data.executions) and new format (response.data)
      const executionsData = response.data.executions || response.data.data || response.data || [];
      setExecutions(Array.isArray(executionsData) ? executionsData : []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch execution history');
      console.error('Error fetching executions:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'failed':
      case 'error':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  const toggleRowExpansion = (executionId) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(executionId)) {
      newExpanded.delete(executionId);
    } else {
      newExpanded.add(executionId);
    }
    setExpandedRows(newExpanded);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatExecutionTime = (ms) => {
    if (!ms) return '-';
    return `${ms.toFixed(2)}ms`;
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>Execution History - {kpi?.name}</DialogTitle>
      <DialogContent sx={{ pt: 2 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="300px">
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold', width: '40px' }}></TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Execution ID</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>KG Name</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Records</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Time</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Confidence</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Timestamp</TableCell>
                  <TableCell sx={{ fontWeight: 'bold', textAlign: 'center' }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {executions.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} align="center" sx={{ py: 3 }}>
                      No executions found
                    </TableCell>
                  </TableRow>
                ) : (
                  executions.map((execution) => (
                    <React.Fragment key={execution.id}>
                      <TableRow hover>
                        <TableCell>
                          <IconButton
                            size="small"
                            onClick={() => toggleRowExpansion(execution.id)}
                            sx={{
                              color: (execution.error_message || execution.generated_sql) ? 'primary.main' : 'text.disabled'
                            }}
                            disabled={!execution.error_message && !execution.generated_sql}
                          >
                            {expandedRows.has(execution.id) ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                          </IconButton>
                        </TableCell>
                        <TableCell>#{execution.id}</TableCell>
                        <TableCell>
                          <Chip
                            label={execution.kg_name || 'N/A'}
                            size="small"
                            variant="outlined"
                            sx={{
                              backgroundColor: '#e3f2fd',
                              color: '#1976d2',
                              fontFamily: 'monospace',
                              fontSize: '0.75rem'
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Chip
                              label={execution.execution_status}
                              size="small"
                              color={getStatusColor(execution.execution_status)}
                              variant="outlined"
                            />
                            {execution.execution_status === 'error' && execution.error_message && (
                              <Tooltip title="Click expand button to view error details">
                                <ErrorIcon color="error" fontSize="small" />
                              </Tooltip>
                            )}
                          </Box>
                        </TableCell>
                        <TableCell>{execution.number_of_records || 0}</TableCell>
                        <TableCell>{formatExecutionTime(execution.execution_time_ms)}</TableCell>
                        <TableCell>
                          {execution.confidence_score
                            ? `${(execution.confidence_score * 100).toFixed(1)}%`
                            : '-'}
                        </TableCell>
                        <TableCell>{formatDate(execution.execution_timestamp)}</TableCell>
                        <TableCell align="center">
                          {execution.execution_status === 'success' && execution.number_of_records > 0 ? (
                            <Tooltip title="View Results">
                              <IconButton
                                size="small"
                                color="primary"
                                onClick={() => onViewDrilldown(execution)}
                              >
                                <VisibilityIcon />
                              </IconButton>
                            </Tooltip>
                          ) : (
                            <span style={{ color: '#999' }}>-</span>
                          )}
                        </TableCell>
                      </TableRow>

                      {/* Expandable row for error details and SQL */}
                      <TableRow>
                        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={9}>
                          <Collapse in={expandedRows.has(execution.id)} timeout="auto" unmountOnExit>
                            <Box sx={{ margin: 2 }}>
                              {/* Error Message Section */}
                              {execution.error_message && (
                                <Alert severity="error" sx={{ mb: 2 }}>
                                  <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                                    Error Message:
                                  </Typography>
                                  <Typography
                                    variant="body2"
                                    sx={{
                                      fontFamily: 'monospace',
                                      fontSize: '0.85rem',
                                      whiteSpace: 'pre-wrap',
                                      wordBreak: 'break-word'
                                    }}
                                  >
                                    {execution.error_message}
                                  </Typography>
                                </Alert>
                              )}

                              {/* Generated SQL Section */}
                              {execution.generated_sql && (
                                <Box>
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                    <CodeIcon color="primary" fontSize="small" />
                                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                                      Generated SQL Query:
                                    </Typography>
                                  </Box>
                                  <Paper
                                    sx={{
                                      p: 2,
                                      backgroundColor: '#f5f5f5',
                                      fontFamily: 'monospace',
                                      fontSize: '0.85rem',
                                      overflow: 'auto',
                                      maxHeight: '300px',
                                      border: '1px solid #e0e0e0'
                                    }}
                                  >
                                    <Typography
                                      component="pre"
                                      sx={{
                                        m: 0,
                                        whiteSpace: 'pre-wrap',
                                        wordBreak: 'break-word',
                                        fontFamily: 'monospace',
                                      }}
                                    >
                                      {execution.generated_sql}
                                    </Typography>
                                  </Paper>
                                </Box>
                              )}

                              {/* Show message if no additional details */}
                              {!execution.error_message && !execution.generated_sql && (
                                <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                                  No additional execution details available.
                                </Typography>
                              )}
                            </Box>
                          </Collapse>
                        </TableCell>
                      </TableRow>
                    </React.Fragment>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default KPIExecutionHistory;

