import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Alert,
  Chip,
  Paper,
  Skeleton,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Schedule as ScheduleIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material';
import KPIResultsViewDialog from './KPIResultsViewDialog';
import { API_BASE_URL } from '../services/api';

const KPIDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedKPI, setSelectedKPI] = useState(null);
  const [resultsDialogOpen, setResultsDialogOpen] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE_URL}/v1/landing-kpi/dashboard`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch dashboard data: ${response.statusText}`);
      }
      
      const data = await response.json();
      setDashboardData(data);
    } catch (err) {
      console.error('Error fetching dashboard:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleViewResults = (kpi) => {
    setSelectedKPI(kpi);
    setResultsDialogOpen(true);
  };

  const handleRefresh = () => {
    fetchDashboardData();
  };

  const getStatusIcon = (status) => {
    if (!status) return <ScheduleIcon sx={{ color: 'warning.main' }} />;
    if (status === 'success') return <CheckCircleIcon sx={{ color: 'success.main' }} />;
    if (status === 'failed') return <ErrorIcon sx={{ color: 'error.main' }} />;
    return <ScheduleIcon sx={{ color: 'warning.main' }} />;
  };

  const getStatusColor = (status) => {
    if (!status) return 'warning';
    if (status === 'success') return 'success';
    if (status === 'failed') return 'error';
    return 'warning';
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
          KPI Dashboard
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {[1, 2, 3].map((i) => (
            <Box key={i}>
              <Skeleton variant="text" width={200} height={40} sx={{ mb: 2 }} />
              <Box sx={{ display: 'flex', gap: 2, overflowX: 'auto' }}>
                {[1, 2, 3].map((j) => (
                  <Skeleton key={j} variant="rectangular" width={320} height={200} />
                ))}
              </Box>
            </Box>
          ))}
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
          KPI Dashboard
        </Typography>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button variant="contained" onClick={handleRefresh}>
          Retry
        </Button>
      </Container>
    );
  }

  const groups = dashboardData?.groups || [];
  const totalKPIs = groups.reduce((sum, group) => sum + group.kpis.length, 0);

  if (totalKPIs === 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
          KPI Dashboard
        </Typography>
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="body1" color="textSecondary" sx={{ mb: 2 }}>
            No KPIs found. Create your first KPI to get started.
          </Typography>
          <Button variant="contained" href="/landing-kpi">
            Go to KPI Management
          </Button>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
            KPI Dashboard
          </Typography>
          <Typography variant="body2" color="textSecondary">
            {totalKPIs} KPI{totalKPIs !== 1 ? 's' : ''} across {groups.length} Group{groups.length !== 1 ? 's' : ''}
          </Typography>
        </Box>
        <Button variant="outlined" onClick={handleRefresh}>
          Refresh
        </Button>
      </Box>

      {/* Group Cards - Horizontal Layout */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {groups.map((group) => (
          <Box key={group.group_name}>
            {/* Group Header */}
            <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                {group.group_name}
              </Typography>
              <Chip
                label={`${group.kpis.length} KPI${group.kpis.length !== 1 ? 's' : ''}`}
                size="small"
                color="primary"
                variant="outlined"
              />
            </Box>

            {/* KPI Cards - Horizontal Scroll */}
            <Box
              sx={{
                display: 'flex',
                gap: 2,
                overflowX: 'auto',
                pb: 2,
                '&::-webkit-scrollbar': {
                  height: 8,
                },
                '&::-webkit-scrollbar-track': {
                  backgroundColor: 'rgba(0,0,0,0.05)',
                  borderRadius: 4,
                },
                '&::-webkit-scrollbar-thumb': {
                  backgroundColor: 'rgba(0,0,0,0.2)',
                  borderRadius: 4,
                  '&:hover': {
                    backgroundColor: 'rgba(0,0,0,0.3)',
                  },
                },
              }}
            >
              {group.kpis.map((kpi) => (
                <Card
                  key={kpi.id}
                  sx={{
                    minWidth: 300,
                    maxWidth: 350,
                    display: 'flex',
                    flexDirection: 'column',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      boxShadow: 6,
                      transform: 'translateY(-4px)',
                    },
                  }}
                >
                  <CardContent sx={{ flex: 1 }}>
                    {/* KPI Name */}
                    <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>
                      {kpi.name}
                    </Typography>

                    {/* KPI Description */}
                    {kpi.description && (
                      <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                        {kpi.description}
                      </Typography>
                    )}

                    {/* Latest Execution Info */}
                    {kpi.latest_execution ? (
                      <Box sx={{ mt: 2 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          {getStatusIcon(kpi.latest_execution.status)}
                          <Chip
                            label={kpi.latest_execution.status || 'pending'}
                            size="small"
                            color={getStatusColor(kpi.latest_execution.status)}
                            variant="outlined"
                          />
                        </Box>

                        <Typography variant="body2" sx={{ mb: 0.5 }}>
                          <strong>Records:</strong> {kpi.latest_execution.record_count}
                        </Typography>

                        {kpi.latest_execution.error_message && (
                          <Alert severity="error" sx={{ mt: 1 }}>
                            {kpi.latest_execution.error_message}
                          </Alert>
                        )}
                      </Box>
                    ) : (
                      <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                        No executions yet
                      </Typography>
                    )}
                  </CardContent>

                  <CardActions>
                    <Button
                      size="small"
                      startIcon={<VisibilityIcon />}
                      onClick={() => handleViewResults(kpi)}
                      disabled={!kpi.latest_execution}
                    >
                      View Results
                    </Button>
                  </CardActions>
                </Card>
              ))}
            </Box>
          </Box>
        ))}
      </Box>

      {/* Results Dialog */}
      <KPIResultsViewDialog
        open={resultsDialogOpen}
        onClose={() => setResultsDialogOpen(false)}
        kpi={selectedKPI}
      />
    </Container>
  );
};

export default KPIDashboard;

