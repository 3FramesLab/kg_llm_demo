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
  Pagination,
  Typography,
  Chip,
  Divider,
  IconButton,
} from '@mui/material';
import { ContentCopy as ContentCopyIcon } from '@mui/icons-material';
import { getKPIDrilldownData } from '../services/api';

const KPIDrilldown = ({ open, execution, onClose }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [copiedSQL, setCopiedSQL] = useState(false);
  const pageSize = 50;

  useEffect(() => {
    if (open && execution) {
      fetchDrilldownData(1);
    }
  }, [open, execution]);

  const fetchDrilldownData = async (pageNum) => {
    setLoading(true);
    setError(null);
    try {
      const response = await getKPIDrilldownData(execution.id, {
        page: pageNum,
        page_size: pageSize,
      });
      setData(response.data);
      setPage(pageNum);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch drill-down data');
      console.error('Error fetching drill-down data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (event, value) => {
    fetchDrilldownData(value);
  };

  const handleCopySQL = () => {
    if (execution?.generated_sql) {
      navigator.clipboard.writeText(execution.generated_sql);
      setCopiedSQL(true);
      setTimeout(() => setCopiedSQL(false), 2000);
    }
  };

  const getColumnNames = () => {
    if (!data?.data || data.data.length === 0) {
      return [];
    }
    return Object.keys(data.data[0]);
  };

  const columns = getColumnNames();

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xl" fullWidth>
      <DialogTitle>
        Drill-down Results - Execution #{execution?.id}
      </DialogTitle>
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
        ) : data ? (
          <Box>
            {/* Execution Metadata Section */}
            <Box sx={{ mb: 3, p: 2.5, backgroundColor: '#ffffff', borderRadius: 2, border: '1px solid #e0e0e0' }}>
              <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2, fontSize: '0.95rem' }}>
                Execution Metadata
              </Typography>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 3, mb: 2 }}>
                <Box>
                  <Typography variant="caption" color="textSecondary" sx={{ fontSize: '0.75rem', display: 'block', mb: 0.5 }}>
                    Status
                  </Typography>
                  <Chip
                    label={execution?.execution_status || 'unknown'}
                    color={execution?.execution_status === 'success' ? 'success' : 'error'}
                    size="small"
                    sx={{ fontWeight: 'bold' }}
                  />
                </Box>
                <Box>
                  <Typography variant="caption" color="textSecondary" sx={{ fontSize: '0.75rem', display: 'block', mb: 0.5 }}>
                    Record Count
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 'bold', fontSize: '0.95rem' }}>
                    {execution?.number_of_records || data.total || 0}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="textSecondary" sx={{ fontSize: '0.75rem', display: 'block', mb: 0.5 }}>
                    Execution Time
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 'bold', fontSize: '0.95rem' }}>
                    {execution?.execution_time_ms ? `${execution.execution_time_ms.toFixed(2)}ms` : 'N/A'}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="textSecondary" sx={{ fontSize: '0.75rem', display: 'block', mb: 0.5 }}>
                    Confidence Score
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 'bold', fontSize: '0.95rem' }}>
                    {execution?.confidence_score ? `${(execution.confidence_score * 100).toFixed(1)}%` : 'N/A'}
                  </Typography>
                </Box>
                {execution?.source_table && (
                  <Box>
                    <Typography variant="caption" color="textSecondary" sx={{ fontSize: '0.75rem', display: 'block', mb: 0.5 }}>
                      Source Table
                    </Typography>
                    <Typography variant="body1" sx={{ fontWeight: 'bold', fontSize: '0.95rem' }}>
                      {execution.source_table}
                    </Typography>
                  </Box>
                )}
                {execution?.target_table && (
                  <Box>
                    <Typography variant="caption" color="textSecondary" sx={{ fontSize: '0.75rem', display: 'block', mb: 0.5 }}>
                      Target Table
                    </Typography>
                    <Typography variant="body1" sx={{ fontWeight: 'bold', fontSize: '0.95rem' }}>
                      {execution.target_table}
                    </Typography>
                  </Box>
                )}
              </Box>

              {/* SQL Query Section */}
              {execution?.generated_sql && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
                      <Typography variant="h6" sx={{ fontWeight: 'bold', fontSize: '0.95rem' }}>
                        Generated SQL Query
                      </Typography>
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<ContentCopyIcon />}
                        onClick={handleCopySQL}
                        sx={{ textTransform: 'none', fontSize: '0.8rem' }}
                      >
                        {copiedSQL ? 'Copied!' : 'Copy'}
                      </Button>
                    </Box>
                    <Paper
                      sx={{
                        p: 2,
                        backgroundColor: '#f5f5f5',
                        fontFamily: 'monospace',
                        fontSize: '0.8rem',
                        overflow: 'auto',
                        maxHeight: '200px',
                        border: '1px solid #e0e0e0',
                      }}
                    >
                      <Typography
                        component="pre"
                        sx={{
                          m: 0,
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-word',
                          fontFamily: 'monospace',
                          fontSize: '0.8rem',
                        }}
                      >
                        {execution.generated_sql}
                      </Typography>
                    </Paper>
                  </Box>
                </>
              )}
            </Box>

            {/* Pagination Info */}
            <Box sx={{ mb: 2, p: 1.5, backgroundColor: '#f9f9f9', borderRadius: 1 }}>
              <Typography variant="body2" sx={{ fontSize: '0.85rem' }}>
                <strong>Total Records:</strong> {data.total} | <strong>Page:</strong> {data.page} of {data.total_pages} | <strong>Records per Page:</strong> {data.page_size}
              </Typography>
            </Box>
            {/* Data Table */}
            <TableContainer component={Paper} sx={{ maxHeight: '500px', overflow: 'auto' }}>
              <Table stickyHeader size="small">
                <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
                  <TableRow>
                    {columns.map((col) => (
                      <TableCell key={col} sx={{ fontWeight: 'bold' }}>
                        {col}
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {data.data.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={columns.length} align="center" sx={{ py: 3 }}>
                        No data available
                      </TableCell>
                    </TableRow>
                  ) : (
                    data.data.map((row, idx) => (
                      <TableRow key={idx} hover>
                        {columns.map((col) => (
                          <TableCell key={`${idx}-${col}`}>
                            {row[col] !== null && row[col] !== undefined
                              ? String(row[col]).substring(0, 100)
                              : '-'}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>

            {/* Pagination */}
            {data.total_pages > 1 && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                <Pagination
                  count={data.total_pages}
                  page={data.page}
                  onChange={handlePageChange}
                  color="primary"
                />
              </Box>
            )}
          </Box>
        ) : null}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default KPIDrilldown;

