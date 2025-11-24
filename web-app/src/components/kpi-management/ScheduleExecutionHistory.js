import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  CircularProgress,
  Grid,
  LinearProgress
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  PlayArrow as TriggerIcon,
  Timeline as TimelineIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Schedule as PendingIcon,
  Cached as RetryIcon
} from '@mui/icons-material';

const ScheduleExecutionHistory = ({ scheduleId, scheduleName }) => {
  const [executions, setExecutions] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  useEffect(() => {
    if (scheduleId) {
      fetchExecutionData();
    }
  }, [scheduleId]);

  const fetchExecutionData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch execution history and statistics in parallel
      const [executionsResponse, statisticsResponse] = await Promise.all([
        fetch(`/v1/kpi-schedules/${scheduleId}/executions`),
        fetch(`/v1/kpi-schedules/${scheduleId}/statistics`)
      ]);

      if (!executionsResponse.ok || !statisticsResponse.ok) {
        throw new Error('Failed to fetch execution data');
      }

      const executionsData = await executionsResponse.json();
      const statisticsData = await statisticsResponse.json();

      setExecutions(executionsData);
      setStatistics(statisticsData);

    } catch (err) {
      console.error('Error fetching execution data:', err);
      setError('Failed to load execution history');
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerManually = async () => {
    try {
      setLoading(true);
      
      const response = await fetch(`/v1/kpi-schedules/${scheduleId}/trigger`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to trigger schedule');
      }

      // Refresh data after triggering
      setTimeout(() => {
        fetchExecutionData();
      }, 2000);

    } catch (err) {
      console.error('Error triggering schedule:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <SuccessIcon sx={{ color: 'success.main' }} />;
      case 'failed':
        return <ErrorIcon sx={{ color: 'error.main' }} />;
      case 'running':
        return <CircularProgress size={20} />;
      case 'retrying':
        return <RetryIcon sx={{ color: 'warning.main' }} />;
      case 'pending':
        return <PendingIcon sx={{ color: 'info.main' }} />;
      default:
        return <PendingIcon sx={{ color: 'grey.500' }} />;
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      success: 'success',
      failed: 'error',
      running: 'info',
      retrying: 'warning',
      pending: 'default'
    };
    return colors[status] || 'default';
  };

  const formatDuration = (startTime, endTime) => {
    if (!startTime || !endTime) return 'N/A';
    
    const start = new Date(startTime);
    const end = new Date(endTime);
    const durationMs = end - start;
    
    if (durationMs < 1000) return `${durationMs}ms`;
    if (durationMs < 60000) return `${Math.round(durationMs / 1000)}s`;
    return `${Math.round(durationMs / 60000)}m`;
  };

  const formatDateTime = (dateTime) => {
    if (!dateTime) return 'N/A';
    return new Date(dateTime).toLocaleString();
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TimelineIcon />
          Execution History - {scheduleName}
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Trigger Manually">
            <IconButton
              onClick={handleTriggerManually}
              disabled={loading}
              color="primary"
            >
              <TriggerIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Refresh">
            <IconButton
              onClick={fetchExecutionData}
              disabled={loading}
            >
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Statistics Cards */}
      {statistics && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {statistics.total_executions}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Executions
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="success.main">
                  {statistics.success_rate.toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Success Rate
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={statistics.success_rate}
                  sx={{ mt: 1 }}
                  color="success"
                />
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="error.main">
                  {statistics.failed_executions}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Failed Executions
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="text.primary">
                  {statistics.avg_execution_time_seconds 
                    ? `${Math.round(statistics.avg_execution_time_seconds)}s`
                    : 'N/A'
                  }
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Avg Duration
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Execution History Table */}
      {loading && !executions.length ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Executions
            </Typography>

            {executions.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <TimelineIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No Executions Yet
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  This schedule hasn't been executed yet. You can trigger it manually or wait for the next scheduled run.
                </Typography>
              </Box>
            ) : (
              <>
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                        <TableCell>Status</TableCell>
                        <TableCell>Scheduled Time</TableCell>
                        <TableCell>Start Time</TableCell>
                        <TableCell>End Time</TableCell>
                        <TableCell>Duration</TableCell>
                        <TableCell>Retries</TableCell>
                        <TableCell>Error</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {executions
                        .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                        .map((execution) => (
                          <TableRow key={execution.id} hover>
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                {getStatusIcon(execution.execution_status)}
                                <Chip
                                  label={execution.execution_status.toUpperCase()}
                                  size="small"
                                  color={getStatusColor(execution.execution_status)}
                                  variant="outlined"
                                />
                              </Box>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">
                                {formatDateTime(execution.scheduled_time)}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">
                                {formatDateTime(execution.actual_start_time)}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">
                                {formatDateTime(execution.actual_end_time)}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">
                                {formatDuration(execution.actual_start_time, execution.actual_end_time)}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">
                                {execution.retry_count || 0}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              {execution.error_message ? (
                                <Tooltip title={execution.error_message}>
                                  <Typography
                                    variant="body2"
                                    sx={{
                                      color: 'error.main',
                                      maxWidth: 200,
                                      overflow: 'hidden',
                                      textOverflow: 'ellipsis',
                                      whiteSpace: 'nowrap',
                                      cursor: 'help'
                                    }}
                                  >
                                    {execution.error_message}
                                  </Typography>
                                </Tooltip>
                              ) : (
                                <Typography variant="body2" color="text.secondary">
                                  -
                                </Typography>
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                    </TableBody>
                  </Table>
                </TableContainer>

                <TablePagination
                  rowsPerPageOptions={[5, 10, 25, 50]}
                  component="div"
                  count={executions.length}
                  rowsPerPage={rowsPerPage}
                  page={page}
                  onPageChange={handleChangePage}
                  onRowsPerPageChange={handleChangeRowsPerPage}
                />
              </>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default ScheduleExecutionHistory;
