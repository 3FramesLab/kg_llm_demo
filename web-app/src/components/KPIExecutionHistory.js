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
} from '@mui/material';
import { Visibility as VisibilityIcon } from '@mui/icons-material';
import { getKPIExecutions } from '../services/api';

const KPIExecutionHistory = ({ open, kpi, onClose, onViewDrilldown }) => {
  const [executions, setExecutions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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
      setExecutions(response.data.executions || []);
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
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
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
                  <TableCell sx={{ fontWeight: 'bold' }}>Execution ID</TableCell>
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
                    <TableCell colSpan={7} align="center" sx={{ py: 3 }}>
                      No executions found
                    </TableCell>
                  </TableRow>
                ) : (
                  executions.map((execution) => (
                    <TableRow key={execution.id} hover>
                      <TableCell>#{execution.id}</TableCell>
                      <TableCell>
                        <Chip
                          label={execution.execution_status}
                          size="small"
                          color={getStatusColor(execution.execution_status)}
                          variant="outlined"
                        />
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

