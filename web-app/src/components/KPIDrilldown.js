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
} from '@mui/material';
import { getKPIDrilldownData } from '../services/api';

const KPIDrilldown = ({ open, execution, onClose }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
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

  const getColumnNames = () => {
    if (!data?.data || data.data.length === 0) {
      return [];
    }
    return Object.keys(data.data[0]);
  };

  const columns = getColumnNames();

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
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
            {/* Summary */}
            <Box sx={{ mb: 2, p: 2, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
              <Typography variant="body2">
                <strong>Total Records:</strong> {data.total}
              </Typography>
              <Typography variant="body2">
                <strong>Page:</strong> {data.page} of {data.total_pages}
              </Typography>
              <Typography variant="body2">
                <strong>Records per Page:</strong> {data.page_size}
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

