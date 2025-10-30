import React, { useState, useEffect, useMemo } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TablePagination,
  TextField,
  IconButton,
  Tooltip,
  Chip,
  Divider,
} from '@mui/material';
import {
  Close as CloseIcon,
  Download as DownloadIcon,
  FilterAltOff as ClearFiltersIcon,
  ContentCopy as ContentCopyIcon,
} from '@mui/icons-material';
import { API_BASE_URL } from '../services/api';

const KPIResultsViewDialog = ({ open, onClose, kpi, showMetadata = true }) => {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [columnFilters, setColumnFilters] = useState({});
  const [copiedSQL, setCopiedSQL] = useState(false);

  useEffect(() => {
    if (open && kpi) {
      fetchResults();
    }
  }, [open, kpi]);

  const fetchResults = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE_URL}/landing-kpi/${kpi.id}/latest-results`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch results: ${response.statusText}`);
      }
      
      const data = await response.json();
      setResults(data.results);
      setPage(0);
    } catch (err) {
      console.error('Error fetching results:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleFilterChange = (columnName, value) => {
    setColumnFilters(prev => ({
      ...prev,
      [columnName]: value
    }));
    setPage(0); // Reset to first page when filter changes
  };

  const handleClearFilters = () => {
    setColumnFilters({});
    setPage(0);
  };

  const handleCopySQL = () => {
    if (results?.sql_query) {
      navigator.clipboard.writeText(results.sql_query);
      setCopiedSQL(true);
      setTimeout(() => setCopiedSQL(false), 2000);
    }
  };

  // Filter the data based on column filters
  const filteredData = useMemo(() => {
    if (!results?.result_data) return [];

    const activeFilters = Object.entries(columnFilters).filter(([_, value]) => value && value.trim() !== '');

    if (activeFilters.length === 0) {
      return results.result_data;
    }

    return results.result_data.filter(row => {
      return activeFilters.every(([columnName, filterValue]) => {
        const cellValue = String(row[columnName] ?? '').toLowerCase();
        const searchValue = filterValue.toLowerCase();
        return cellValue.includes(searchValue);
      });
    });
  }, [results?.result_data, columnFilters]);

  const hasActiveFilters = useMemo(() => {
    return Object.values(columnFilters).some(value => value && value.trim() !== '');
  }, [columnFilters]);

  const handleDownloadCSV = () => {
    if (!filteredData || filteredData.length === 0) return;

    const headers = results.column_names || [];
    const rows = filteredData.map((row) =>
      headers.map((header) => {
        const value = row[header];
        // Escape quotes and wrap in quotes if contains comma
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      })
    );

    const csv = [
      headers.join(','),
      ...rows.map((row) => row.join(',')),
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${kpi.name}-results.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  if (!kpi) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">
          {kpi.name} - Results
        </Typography>
        <Button
          size="small"
          onClick={onClose}
          sx={{ minWidth: 'auto', p: 0.5 }}
        >
          <CloseIcon />
        </Button>
      </DialogTitle>

      <DialogContent dividers>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error">{error}</Alert>
        ) : !results ? (
          <Alert severity="info">No results available</Alert>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* Metadata Section - Conditionally rendered based on showMetadata prop */}
            {showMetadata && (
              <>
                <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                    Execution Metadata
                  </Typography>
                  <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                    <Box>
                      <Typography variant="body2" color="textSecondary">
                        Status
                      </Typography>
                      <Chip
                        label={results.execution_status || 'unknown'}
                        color={results.execution_status === 'success' ? 'success' : 'error'}
                        size="small"
                        sx={{ mt: 0.5 }}
                      />
                    </Box>
                    <Box>
                      <Typography variant="body2" color="textSecondary">
                        Record Count
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 'bold', mt: 0.5 }}>
                        {results.record_count}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="textSecondary">
                        Execution Time
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 'bold', mt: 0.5 }}>
                        {results.execution_time_ms ? `${results.execution_time_ms.toFixed(2)}ms` : 'N/A'}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="textSecondary">
                        Confidence Score
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 'bold', mt: 0.5 }}>
                        {results.confidence_score ? `${(results.confidence_score * 100).toFixed(1)}%` : 'N/A'}
                      </Typography>
                    </Box>
                    {results.kg_name && (
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          Knowledge Graph
                        </Typography>
                        <Chip
                          label={results.kg_name}
                          size="small"
                          variant="outlined"
                          sx={{
                            mt: 0.5,
                            backgroundColor: '#e3f2fd',
                            color: '#1976d2',
                            fontFamily: 'monospace',
                            fontSize: '0.75rem'
                          }}
                        />
                      </Box>
                    )}
                    {results.source_table && (
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          Source Table
                        </Typography>
                        <Typography variant="body1" sx={{ fontWeight: 'bold', mt: 0.5 }}>
                          {results.source_table}
                        </Typography>
                      </Box>
                    )}
                    {results.target_table && (
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          Target Table
                        </Typography>
                        <Typography variant="body1" sx={{ fontWeight: 'bold', mt: 0.5 }}>
                          {results.target_table}
                        </Typography>
                      </Box>
                    )}
                  </Box>
                </Box>

                <Divider />

                {/* SQL Query Section */}
                {results.sql_query && (
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                        Generated SQL Query
                      </Typography>
                      <Button
                        size="small"
                        startIcon={<ContentCopyIcon />}
                        onClick={handleCopySQL}
                      >
                        {copiedSQL ? 'Copied!' : 'Copy'}
                      </Button>
                    </Box>
                    <Paper
                      sx={{
                        p: 2,
                        backgroundColor: '#f5f5f5',
                        fontFamily: 'monospace',
                        fontSize: '0.85rem',
                        overflow: 'auto',
                        maxHeight: '200px',
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
                        {results.sql_query}
                      </Typography>
                    </Paper>
                  </Box>
                )}

                <Divider />
              </>
            )}

            {/* Results Table Section */}
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                Query Results ({results.record_count} records)
              </Typography>
              {results.result_data && results.result_data.length > 0 ? (
                <>
                <TableContainer component={Paper}>
                  <Table size="small">
                    <TableHead>
                      <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                        {results.column_names?.map((col) => (
                            <TableCell key={col} sx={{ fontWeight: 'bold' }}>
                            {col}
                          </TableCell>
                        ))}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                        {results.result_data
                          .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                          .map((row, idx) => (
                            <TableRow key={idx}>
                              {results.column_names?.map((col) => (
                                <TableCell key={`${idx}-${col}`}>
                                  {String(row[col] ?? '')}
                                </TableCell>
                              ))}
                            </TableRow>
                          ))}
                    </TableBody>
                  </Table>
                </TableContainer>
                <TablePagination
                  rowsPerPageOptions={[5, 10, 25, 50]}
                  component="div"
                  count={filteredData.length}
                  rowsPerPage={rowsPerPage}
                  page={page}
                  onPageChange={handleChangePage}
                  onRowsPerPageChange={handleChangeRowsPerPage}
                />
              </>
            ) : (
              <Alert severity="info">No data returned from query</Alert>
            )}
          </Box>
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button
          startIcon={<DownloadIcon />}
          onClick={handleDownloadCSV}
          disabled={!filteredData || filteredData.length === 0}
        >
          Download CSV {hasActiveFilters ? '(Filtered)' : ''}
        </Button>
        <Button onClick={onClose} variant="contained">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default KPIResultsViewDialog;

