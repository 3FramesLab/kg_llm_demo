import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Alert,
  CircularProgress,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Button
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Schedule as ScheduleIcon,
  Sync as SyncIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon
} from '@mui/icons-material';

const ScheduleMonitoringDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    fetchDashboardData();
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all active schedules and their statistics
      const response = await fetch('/v1/kpi-schedules/dashboard-overview');
      
      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data');
      }

      const data = await response.json();
      setDashboardData(data);

    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load monitoring dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleSyncAllToAirflow = async () => {
    try {
      setSyncing(true);
      
      const response = await fetch('/v1/kpi-schedules/sync-all-to-airflow', {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to sync schedules to Airflow');
      }

      const result = await response.json();
      
      // Show success message and refresh data
      setTimeout(() => {
        fetchDashboardData();
      }, 2000);

    } catch (err) {
      console.error('Error syncing to Airflow:', err);
      setError(err.message);
    } finally {
      setSyncing(false);
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

  const formatDateTime = (dateTime) => {
    if (!dateTime) return 'N/A';
    return new Date(dateTime).toLocaleString();
  };

  if (loading && !dashboardData) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <DashboardIcon />
          Schedule Monitoring Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<SyncIcon />}
            onClick={handleSyncAllToAirflow}
            disabled={syncing}
          >
            {syncing ? 'Syncing...' : 'Sync to Airflow'}
          </Button>
          <IconButton
            onClick={fetchDashboardData}
            disabled={loading}
            color="primary"
          >
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Overview Cards */}
      {dashboardData && (
        <>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <ScheduleIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                  <Typography variant="h4" color="primary">
                    {dashboardData.total_schedules || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Schedules
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    ({dashboardData.active_schedules || 0} active)
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <SuccessIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                  <Typography variant="h4" color="success.main">
                    {dashboardData.success_rate ? `${dashboardData.success_rate.toFixed(1)}%` : 'N/A'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Success Rate (24h)
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={dashboardData.success_rate || 0}
                    sx={{ mt: 1 }}
                    color="success"
                  />
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <ErrorIcon sx={{ fontSize: 40, color: 'error.main', mb: 1 }} />
                  <Typography variant="h4" color="error.main">
                    {dashboardData.failed_executions_24h || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Failed Executions (24h)
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <TrendingUpIcon sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
                  <Typography variant="h4" color="info.main">
                    {dashboardData.total_executions_24h || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Executions (24h)
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Recent Executions Table */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Schedule Executions
              </Typography>

              {dashboardData.recent_executions && dashboardData.recent_executions.length > 0 ? (
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                        <TableCell>Schedule</TableCell>
                        <TableCell>KPI</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Scheduled Time</TableCell>
                        <TableCell>Duration</TableCell>
                        <TableCell>Next Run</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {dashboardData.recent_executions.map((execution) => (
                        <TableRow key={execution.id} hover>
                          <TableCell>
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>
                              {execution.schedule_name}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {execution.kpi_name}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={execution.execution_status.toUpperCase()}
                              size="small"
                              color={getStatusColor(execution.execution_status)}
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {formatDateTime(execution.scheduled_time)}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {execution.duration || 'N/A'}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {formatDateTime(execution.next_execution)}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <ScheduleIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No Recent Executions
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Schedule executions will appear here once KPIs start running.
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>

          {/* System Health Indicators */}
          <Grid container spacing={2} sx={{ mt: 2 }}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <SyncIcon />
                    Airflow Sync Status
                  </Typography>

                  {dashboardData.airflow_sync_status ? (
                    <Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">Synced Schedules:</Typography>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          {dashboardData.airflow_sync_status.synced_successfully} / {dashboardData.airflow_sync_status.total_schedules}
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={(dashboardData.airflow_sync_status.synced_successfully / dashboardData.airflow_sync_status.total_schedules) * 100}
                        sx={{ mb: 1 }}
                        color={dashboardData.airflow_sync_status.sync_failures > 0 ? 'warning' : 'success'}
                      />
                      {dashboardData.airflow_sync_status.sync_failures > 0 && (
                        <Alert severity="warning" sx={{ mt: 1 }}>
                          {dashboardData.airflow_sync_status.sync_failures} schedule(s) failed to sync
                        </Alert>
                      )}
                    </Box>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      Sync status not available
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <WarningIcon />
                    Alerts & Issues
                  </Typography>

                  {dashboardData.alerts && dashboardData.alerts.length > 0 ? (
                    <Box>
                      {dashboardData.alerts.map((alert, index) => (
                        <Alert key={index} severity={alert.severity} sx={{ mb: 1 }}>
                          {alert.message}
                        </Alert>
                      ))}
                    </Box>
                  ) : (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <SuccessIcon sx={{ color: 'success.main' }} />
                      <Typography variant="body2" color="success.main">
                        All systems operational
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </>
      )}
    </Box>
  );
};

export default ScheduleMonitoringDashboard;
