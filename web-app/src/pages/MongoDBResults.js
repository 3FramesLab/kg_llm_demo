import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Button,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  InputAdornment,
  Pagination,
  Tooltip,
  Collapse,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Refresh,
  Delete,
  Visibility,
  Search,
  DataObject,
  CheckCircle,
  Cancel,
  ExpandMore,
  ExpandLess,
  Assessment,
  Storage,
} from '@mui/icons-material';
import {
  listMongoDBResults,
  getMongoDBResult,
  deleteMongoDBResult,
  getMongoDBStatistics,
} from '../services/api';

export default function MongoDBResults() {
  const [results, setResults] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [selectedResult, setSelectedResult] = useState(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [resultToDelete, setResultToDelete] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [tabValue, setTabValue] = useState(0);
  const [expandedCards, setExpandedCards] = useState({});

  const resultsPerPage = 10;

  useEffect(() => {
    loadResults();
    loadStatistics();
  }, [page, searchTerm]);

  const loadResults = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        limit: resultsPerPage,
        skip: (page - 1) * resultsPerPage,
      };
      if (searchTerm) {
        params.ruleset_id = searchTerm;
      }

      const response = await listMongoDBResults(params);
      setResults(response.data.results || []);
      const totalResults = response.data.count || 0;
      setTotalPages(Math.ceil(totalResults / resultsPerPage) || 1);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load results');
    } finally {
      setLoading(false);
    }
  };

  const loadStatistics = async () => {
    try {
      const response = await getMongoDBStatistics(searchTerm || null);
      setStatistics(response.data.statistics || null);
    } catch (err) {
      console.error('Failed to load statistics:', err);
    }
  };

  const handleViewDetails = async (documentId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await getMongoDBResult(documentId);
      setSelectedResult(response.data.result);
      setDetailsOpen(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load result details');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (result) => {
    setResultToDelete(result);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!resultToDelete) return;

    setLoading(true);
    setError(null);
    try {
      await deleteMongoDBResult(resultToDelete._id);
      setSuccess(`Result ${resultToDelete._id} deleted successfully`);
      setDeleteDialogOpen(false);
      setResultToDelete(null);
      loadResults();
      loadStatistics();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete result');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadResults();
    loadStatistics();
  };

  const toggleCardExpand = (id) => {
    setExpandedCards(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const renderStatistics = () => {
    if (!statistics) return null;

    return (
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Assessment color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6" fontWeight="700" fontSize="0.95rem">Total Executions</Typography>
              </Box>
              <Typography variant="h6" fontWeight="600" fontSize="0.9rem" color="primary">
                {statistics.total_executions || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <CheckCircle color="success" sx={{ mr: 1 }} />
                <Typography variant="h6" fontWeight="700" fontSize="0.95rem">Total Matched</Typography>
              </Box>
              <Typography variant="h6" fontWeight="600" fontSize="0.9rem" color="success.main">
                {statistics.total_matched || 0}
              </Typography>
              <Typography variant="caption" fontSize="0.65rem" color="text.secondary">
                Avg: {(statistics.avg_matched || 0).toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Cancel color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6" fontWeight="700" fontSize="0.95rem">Unmatched Source</Typography>
              </Box>
              <Typography variant="h6" fontWeight="600" fontSize="0.9rem" color="warning.main">
                {statistics.total_unmatched_source || 0}
              </Typography>
              <Typography variant="caption" fontSize="0.65rem" color="text.secondary">
                Avg: {(statistics.avg_unmatched_source || 0).toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Cancel color="error" sx={{ mr: 1 }} />
                <Typography variant="h6" fontWeight="700" fontSize="0.95rem">Unmatched Target</Typography>
              </Box>
              <Typography variant="h6" fontWeight="600" fontSize="0.9rem" color="error.main">
                {statistics.total_unmatched_target || 0}
              </Typography>
              <Typography variant="caption" fontSize="0.65rem" color="text.secondary">
                Avg: {(statistics.avg_unmatched_target || 0).toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderResultCard = (result) => {
    const isExpanded = expandedCards[result._id];

    return (
      <Card key={result._id} sx={{ mb: 2 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <Box display="flex" alignItems="center" mb={1}>
                <Storage color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6" fontWeight="700" fontSize="0.95rem" component="div">
                  {result.ruleset_id}
                </Typography>
              </Box>
              <Typography variant="caption" fontSize="0.65rem" color="text.secondary" display="block">
                Document ID: {result._id}
              </Typography>
              <Typography variant="caption" fontSize="0.65rem" color="text.secondary" display="block">
                {formatTimestamp(result.execution_timestamp)}
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box display="flex" justifyContent="flex-end" gap={1} flexWrap="wrap">
                <Chip
                  label={`Matched: ${result.matched_count || 0}`}
                  color="success"
                  size="small"
                  sx={{ fontSize: '0.7rem' }}
                />
                <Chip
                  label={`Source: ${result.unmatched_source_count || 0}`}
                  color="warning"
                  size="small"
                />
                <Chip
                  label={`Target: ${result.unmatched_target_count || 0}`}
                  color="error"
                  size="small"
                />
              </Box>
            </Grid>
          </Grid>

          <Collapse in={isExpanded}>
            <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Summary
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                  <Typography variant="body2" color="text.secondary">
                    Matched Records: {result.matched_count || 0}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Typography variant="body2" color="text.secondary">
                    Unmatched Source: {result.unmatched_source_count || 0}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Typography variant="body2" color="text.secondary">
                    Unmatched Target: {result.unmatched_target_count || 0}
                  </Typography>
                </Grid>
              </Grid>
              {result.metadata && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Execution Metadata
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Execution Time: {result.metadata.execution_time_ms?.toFixed(2)} ms
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Source DB: {result.metadata.source_db_type}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Target DB: {result.metadata.target_db_type}
                  </Typography>
                </Box>
              )}
            </Box>
          </Collapse>
        </CardContent>
        <CardActions>
          <Button
            size="small"
            startIcon={isExpanded ? <ExpandLess /> : <ExpandMore />}
            onClick={() => toggleCardExpand(result._id)}
          >
            {isExpanded ? 'Less' : 'More'}
          </Button>
          <Button
            size="small"
            startIcon={<Visibility />}
            onClick={() => handleViewDetails(result._id)}
          >
            View Full Details
          </Button>
          <Button
            size="small"
            color="error"
            startIcon={<Delete />}
            onClick={() => handleDeleteClick(result)}
          >
            Delete
          </Button>
        </CardActions>
      </Card>
    );
  };

  const renderDetailsDialog = () => {
    if (!selectedResult) return null;

    return (
      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Typography variant="h6" fontWeight="700" fontSize="0.95rem">Reconciliation Result Details</Typography>
            <Chip label={selectedResult.ruleset_id} color="primary" size="small" sx={{ fontSize: '0.7rem' }} />
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ mb: 2 }}>
            <Tab label="Summary" />
            <Tab label={`Matched (${selectedResult.matched_count || 0})`} />
            <Tab label={`Unmatched Source (${selectedResult.unmatched_source_count || 0})`} />
            <Tab label={`Unmatched Target (${selectedResult.unmatched_target_count || 0})`} />
            <Tab label="Raw JSON" />
          </Tabs>

          {/* Summary Tab */}
          {tabValue === 0 && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Execution Information
              </Typography>
              <TableContainer component={Paper} variant="outlined" sx={{ mb: 2 }}>
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell><strong>Document ID</strong></TableCell>
                      <TableCell>{selectedResult._id}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell><strong>Ruleset ID</strong></TableCell>
                      <TableCell>{selectedResult.ruleset_id}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell><strong>Execution Time</strong></TableCell>
                      <TableCell>{formatTimestamp(selectedResult.execution_timestamp)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell><strong>Matched Count</strong></TableCell>
                      <TableCell>{selectedResult.matched_count || 0}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell><strong>Unmatched Source</strong></TableCell>
                      <TableCell>{selectedResult.unmatched_source_count || 0}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell><strong>Unmatched Target</strong></TableCell>
                      <TableCell>{selectedResult.unmatched_target_count || 0}</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>

              {selectedResult.metadata && (
                <>
                  <Typography variant="subtitle1" gutterBottom>
                    Execution Metadata
                  </Typography>
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableBody>
                        {Object.entries(selectedResult.metadata).map(([key, value]) => (
                          <TableRow key={key}>
                            <TableCell><strong>{key}</strong></TableCell>
                            <TableCell>{JSON.stringify(value)}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </>
              )}
            </Box>
          )}

          {/* Matched Records Tab */}
          {tabValue === 1 && (
            <Box>
              {selectedResult.matched_records && selectedResult.matched_records.length > 0 ? (
                <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 400 }}>
                  <Table size="small" stickyHeader>
                    <TableHead>
                      <TableRow>
                        <TableCell>#</TableCell>
                        <TableCell>Rule Name</TableCell>
                        <TableCell>Confidence</TableCell>
                        <TableCell>Source Record</TableCell>
                        <TableCell>Target Record</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {selectedResult.matched_records.map((record, idx) => (
                        <TableRow key={idx}>
                          <TableCell>{idx + 1}</TableCell>
                          <TableCell>{record.rule_name}</TableCell>
                          <TableCell>{(record.match_confidence * 100).toFixed(0)}%</TableCell>
                          <TableCell>
                            <pre style={{ fontSize: '0.65rem', margin: 0 }}>
                              {JSON.stringify(record.source_record, null, 2)}
                            </pre>
                          </TableCell>
                          <TableCell>
                            <pre style={{ fontSize: '0.65rem', margin: 0 }}>
                              {JSON.stringify(record.target_record, null, 2)}
                            </pre>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Alert severity="info">No matched records found</Alert>
              )}
            </Box>
          )}

          {/* Unmatched Source Tab */}
          {tabValue === 2 && (
            <Box>
              {selectedResult.unmatched_source && selectedResult.unmatched_source.length > 0 ? (
                <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 400 }}>
                  <Table size="small" stickyHeader>
                    <TableHead>
                      <TableRow>
                        <TableCell>#</TableCell>
                        <TableCell>Record Data</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {selectedResult.unmatched_source.map((record, idx) => (
                        <TableRow key={idx}>
                          <TableCell>{idx + 1}</TableCell>
                          <TableCell>
                            <pre style={{ fontSize: '0.65rem', margin: 0 }}>
                              {JSON.stringify(record, null, 2)}
                            </pre>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Alert severity="info">No unmatched source records found</Alert>
              )}
            </Box>
          )}

          {/* Unmatched Target Tab */}
          {tabValue === 3 && (
            <Box>
              {selectedResult.unmatched_target && selectedResult.unmatched_target.length > 0 ? (
                <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 400 }}>
                  <Table size="small" stickyHeader>
                    <TableHead>
                      <TableRow>
                        <TableCell>#</TableCell>
                        <TableCell>Record Data</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {selectedResult.unmatched_target.map((record, idx) => (
                        <TableRow key={idx}>
                          <TableCell>{idx + 1}</TableCell>
                          <TableCell>
                            <pre style={{ fontSize: '0.65rem', margin: 0 }}>
                              {JSON.stringify(record, null, 2)}
                            </pre>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Alert severity="info">No unmatched target records found</Alert>
              )}
            </Box>
          )}

          {/* Raw JSON Tab */}
          {tabValue === 4 && (
            <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.100', maxHeight: 500, overflow: 'auto' }}>
              <pre style={{ margin: 0, fontSize: '0.75rem' }}>
                {JSON.stringify(selectedResult, null, 2)}
              </pre>
            </Paper>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    );
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box mb={3}>
        <Typography variant="h5" fontWeight="700" sx={{ mb: 0.25, lineHeight: 1.2, fontSize: '1.15rem' }} gutterBottom>
          MongoDB Reconciliation Results
        </Typography>
        <Typography variant="body2" fontSize="0.8rem" color="text.secondary">
          View and manage reconciliation execution results stored in MongoDB
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {renderStatistics()}

      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <TextField
            placeholder="Filter by Ruleset ID"
            variant="outlined"
            size="small"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
            sx={{ width: 300 }}
          />
          <Button
            variant="contained"
            startIcon={<Refresh />}
            onClick={handleRefresh}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>

        {loading && (
          <Box display="flex" justifyContent="center" p={3}>
            <CircularProgress />
          </Box>
        )}

        {!loading && results.length === 0 && (
          <Alert severity="info">
            No reconciliation results found in MongoDB.
            {searchTerm && ' Try a different search term or '}
            Execute a reconciliation to create results.
          </Alert>
        )}

        {!loading && results.length > 0 && (
          <>
            {results.map(renderResultCard)}
            <Box display="flex" justifyContent="center" mt={3}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={(e, value) => setPage(value)}
                color="primary"
              />
            </Box>
          </>
        )}
      </Paper>

      {renderDetailsDialog()}

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this reconciliation result?
          </Typography>
          {resultToDelete && (
            <Box mt={2}>
              <Typography variant="body2" color="text.secondary">
                Document ID: {resultToDelete._id}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Ruleset: {resultToDelete.ruleset_id}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
