import React, { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Box,
  CircularProgress,
  Alert,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
  useMediaQuery,
  useTheme,
  Card,
  CardContent,
  CardActions,
  Divider,
  Typography,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as PlayArrowIcon,
  History as HistoryIcon,
  CheckCircle as CheckCircleIcon,
  Cached as CacheIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { listKPIs, deleteKPI, updateKPICacheFlags, clearKPICacheFlags, getKPIExecutions } from '../services/api';

const KPIList = ({ onEdit, onExecute, onViewHistory, refreshTrigger }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.down('lg'));

  const [kpis, setKpis] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [selectedKPI, setSelectedKPI] = useState(null);
  const [updatingCache, setUpdatingCache] = useState({});

  // Fetch KPIs
  useEffect(() => {
    fetchKPIs();
  }, [refreshTrigger]);

  const fetchKPIs = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        is_active: true,
      };

      const response = await listKPIs(params);
      // Handle both old format (response.data.kpis) and new format (response.data)
      const kpisData = response.data.kpis || response.data.data || response.data || [];
      setKpis(Array.isArray(kpisData) ? kpisData : []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch KPIs');
      console.error('Error fetching KPIs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (kpi) => {
    setSelectedKPI(kpi);
    setDeleteConfirmOpen(true);
  };

  const handleDeleteConfirm = async () => {
    try {
      await deleteKPI(selectedKPI.id);
      setDeleteConfirmOpen(false);
      setSelectedKPI(null);
      fetchKPIs();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete KPI');
    }
  };

  const handleToggleAccept = async (kpi) => {
    const newValue = !kpi.isAccept;
    setUpdatingCache(prev => ({ ...prev, [`${kpi.id}_accept`]: true }));

    try {
      let updateData = { isAccept: newValue };

      // If accepting (newValue = true), we need to get the latest SQL to cache
      if (newValue) {
        console.log('🔍 Fetching latest execution to get SQL for caching...');

        try {
          // First try to get from latest_execution in the KPI object itself
          if (kpi.latest_execution && kpi.latest_execution.generated_sql) {
            updateData.cached_sql = kpi.latest_execution.generated_sql;
            console.log('✅ Found SQL in KPI latest_execution:', updateData.cached_sql.substring(0, 100) + '...');
          } else {
            // Fallback: Get the latest execution from API
            console.log('🔄 Fetching executions from API...');
            const executionsResponse = await getKPIExecutions(kpi.id);
            console.log('📊 Executions response:', executionsResponse);

            // Handle different response formats from the updated getKPIExecutions function
            const executions = executionsResponse.data?.executions || [];
            console.log(`📋 Found ${executions.length} executions`);

            if (executions.length > 0) {
              const latestExecution = executions[0]; // Most recent execution
              console.log('🎯 Latest execution:', latestExecution);

              if (latestExecution.generated_sql) {
                updateData.cached_sql = latestExecution.generated_sql;
                console.log('✅ Found SQL in latest execution:', updateData.cached_sql.substring(0, 100) + '...');
              } else {
                console.warn('⚠️ Latest execution has no generated_sql field');
                console.log('Available fields:', Object.keys(latestExecution));
              }
            } else {
              console.warn('⚠️ No executions found for this KPI');
            }
          }

          if (!updateData.cached_sql) {
            console.warn('⚠️ Could not find SQL to cache. User needs to execute KPI first.');
            setError('Please execute the KPI first to generate SQL before accepting it.');
            return;
          }
        } catch (execErr) {
          console.error('❌ Error fetching latest SQL for caching:', execErr);
          setError('Could not fetch latest SQL. Please execute the KPI first.');
          return;
        }
      } else {
        // If un-accepting, clear the cached SQL
        updateData.cached_sql = null;
        console.log('🗑️ Clearing cached SQL (un-accepting)');
      }

      console.log('📤 Updating cache flags:', updateData);
      await updateKPICacheFlags(kpi.id, updateData);

      // Update local state
      setKpis(prev => prev.map(k =>
        k.id === kpi.id ? {
          ...k,
          isAccept: newValue,
          cached_sql: updateData.cached_sql
        } : k
      ));

      console.log('✅ Cache flags updated successfully');
    } catch (err) {
      console.error('❌ Error updating isAccept flag:', err);
      setError('Failed to update accept flag: ' + err.message);
    } finally {
      setUpdatingCache(prev => ({ ...prev, [`${kpi.id}_accept`]: false }));
    }
  };

  const handleToggleCache = async (kpi) => {
    const newValue = !kpi.isSQLCached;
    setUpdatingCache(prev => ({ ...prev, [`${kpi.id}_cache`]: true }));

    try {
      await updateKPICacheFlags(kpi.id, { isSQLCached: newValue });
      setKpis(prev => prev.map(k =>
        k.id === kpi.id ? { ...k, isSQLCached: newValue } : k
      ));
    } catch (err) {
      console.error('Error updating isSQLCached flag:', err);
      setError('Failed to update cache flag');
    } finally {
      setUpdatingCache(prev => ({ ...prev, [`${kpi.id}_cache`]: false }));
    }
  };

  const handleClearCache = async (kpi) => {
    setUpdatingCache(prev => ({ ...prev, [`${kpi.id}_clear`]: true }));

    try {
      await clearKPICacheFlags(kpi.id);
      setKpis(prev => prev.map(k =>
        k.id === kpi.id ? { ...k, isAccept: false, isSQLCached: false, cached_sql: null } : k
      ));
    } catch (err) {
      console.error('Error clearing cache flags:', err);
      setError('Failed to clear cache flags');
    } finally {
      setUpdatingCache(prev => ({ ...prev, [`${kpi.id}_clear`]: false }));
    }
  };





  if (loading && kpis.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  // Mobile/Tablet Card View
  if (isMobile || isTablet) {
    return (
      <Box>
        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {kpis.length === 0 ? (
          <Alert severity="info" sx={{ textAlign: 'center', py: 4 }}>
            No KPIs found. Create your first KPI to get started.
          </Alert>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {kpis.map((kpi) => (
              <Card key={kpi.id} sx={{ boxShadow: 2 }}>
                <CardContent sx={{ pb: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" sx={{ fontWeight: 'bold', flex: 1 }}>
                      {kpi.name}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, ml: 2 }}>
                      <Tooltip title={kpi.isAccept ? "SQL is accepted" : "SQL not accepted"}>
                        <IconButton
                          size="small"
                          color={kpi.isAccept ? "success" : "default"}
                          onClick={() => handleToggleAccept(kpi)}
                          disabled={updatingCache[`${kpi.id}_accept`]}
                        >
                          <CheckCircleIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title={kpi.isSQLCached ? "Using cached SQL" : "Generate SQL with LLM"}>
                        <IconButton
                          size="small"
                          color={kpi.isSQLCached ? "primary" : "default"}
                          onClick={() => handleToggleCache(kpi)}
                          disabled={updatingCache[`${kpi.id}_cache`]}
                        >
                          <CacheIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Box>

                  {kpi.alias_name && (
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                      <strong>Alias:</strong> {kpi.alias_name}
                    </Typography>
                  )}

                  {kpi.group_name && (
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                      <strong>Group:</strong> {kpi.group_name}
                    </Typography>
                  )}

                  <Typography variant="body2" sx={{ mb: 2 }}>
                    <strong>Definition:</strong> {kpi.nl_definition}
                  </Typography>

                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
                    <Chip
                      label={kpi.isAccept ? "Accepted" : "Not Accepted"}
                      size="small"
                      color={kpi.isAccept ? "success" : "default"}
                      variant="outlined"
                    />
                    <Chip
                      label={kpi.isSQLCached ? "Cached" : "Not Cached"}
                      size="small"
                      color={kpi.isSQLCached ? "primary" : "default"}
                      variant="outlined"
                    />
                  </Box>
                </CardContent>

                <Divider />

                <CardActions sx={{ justifyContent: 'space-between', px: 2, py: 1 }}>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Tooltip title="Execute">
                      <IconButton size="small" color="success" onClick={() => onExecute(kpi)}>
                        <PlayArrowIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Edit">
                      <IconButton size="small" color="primary" onClick={() => onEdit(kpi)}>
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="History">
                      <IconButton size="small" color="info" onClick={() => onViewHistory(kpi)}>
                        <HistoryIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>

                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Tooltip title="Clear Cache Flags">
                      <IconButton
                        size="small"
                        color="secondary"
                        onClick={() => handleClearCache(kpi)}
                        disabled={updatingCache[`${kpi.id}_clear`]}
                      >
                        <ClearIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton size="small" color="error" onClick={() => handleDeleteClick(kpi)}>
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </CardActions>
              </Card>
            ))}
          </Box>
        )}
      </Box>
    );
  }

  // Desktop Table View
  return (
    <Box>
      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* KPI Table */}
      <TableContainer component={Paper} sx={{ overflowX: 'auto' }}>
        <Table stickyHeader>
          <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold', minWidth: '150px' }}>Name</TableCell>
              <TableCell sx={{ fontWeight: 'bold', minWidth: '120px' }}>Alias</TableCell>
              <TableCell sx={{ fontWeight: 'bold', minWidth: '150px' }}>Group</TableCell>
              <TableCell sx={{ fontWeight: 'bold', minWidth: '300px' }}>NL Definition</TableCell>
              <TableCell sx={{ fontWeight: 'bold', textAlign: 'center', minWidth: '80px' }}>Accepted</TableCell>
              <TableCell sx={{ fontWeight: 'bold', textAlign: 'center', minWidth: '80px' }}>Cached</TableCell>
              <TableCell sx={{ fontWeight: 'bold', textAlign: 'center', minWidth: '250px' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {kpis.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 4, color: '#666' }}>
                  No KPIs found. Create your first KPI to get started.
                </TableCell>
              </TableRow>
            ) : (
              kpis.map((kpi) => (
                <TableRow key={kpi.id} hover>
                  <TableCell sx={{ fontWeight: 'medium', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {kpi.name}
                  </TableCell>
                  <TableCell sx={{ maxWidth: '150px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {kpi.alias_name ? (
                      <Chip label={kpi.alias_name} size="small" variant="outlined" />
                    ) : (
                      <span style={{ color: '#999' }}>-</span>
                    )}
                  </TableCell>
                  <TableCell sx={{ maxWidth: '150px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {kpi.group_name || <span style={{ color: '#999' }}>-</span>}
                  </TableCell>
                  <TableCell sx={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', wordBreak: 'break-word' }}>
                    {kpi.nl_definition}
                  </TableCell>

                  {/* Accepted Status */}
                  <TableCell align="center">
                    <Tooltip title={kpi.isAccept ? "SQL is accepted" : "SQL not accepted"}>
                      <IconButton
                        size="small"
                        color={kpi.isAccept ? "success" : "default"}
                        onClick={() => handleToggleAccept(kpi)}
                        disabled={updatingCache[`${kpi.id}_accept`]}
                      >
                        <CheckCircleIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>

                  {/* Cached Status */}
                  <TableCell align="center">
                    <Tooltip title={kpi.isSQLCached ? "Using cached SQL" : "Generate SQL with LLM"}>
                      <IconButton
                        size="small"
                        color={kpi.isSQLCached ? "primary" : "default"}
                        onClick={() => handleToggleCache(kpi)}
                        disabled={updatingCache[`${kpi.id}_cache`]}
                      >
                        <CacheIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>

                  <TableCell align="center">
                    <Tooltip title="Execute">
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => onExecute(kpi)}
                      >
                        <PlayArrowIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="History">
                      <IconButton
                        size="small"
                        color="info"
                        onClick={() => onViewHistory(kpi)}
                      >
                        <HistoryIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Edit">
                      <IconButton
                        size="small"
                        color="warning"
                        onClick={() => onEdit(kpi)}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Clear Cache Flags">
                      <IconButton
                        size="small"
                        color="secondary"
                        onClick={() => handleClearCache(kpi)}
                        disabled={updatingCache[`${kpi.id}_clear`]}
                      >
                        <ClearIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDeleteClick(kpi)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmOpen} onClose={() => setDeleteConfirmOpen(false)}>
        <DialogTitle>Delete KPI</DialogTitle>
        <DialogContent>
          Are you sure you want to delete the KPI "{selectedKPI?.name}"?
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirmOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Loading Indicator */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
          <CircularProgress size={30} />
        </Box>
      )}
    </Box>
  );
};

export default KPIList;

