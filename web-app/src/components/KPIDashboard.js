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
            {totalKPIs} KPI{totalKPIs !== 1 ? 's' : ''}
          </Typography>
        </Box>
        <Button variant="outlined" onClick={handleRefresh}>
          Refresh
        </Button>
      </Box>

      {/* KPI Cards - Horizontal Layout (Slim Cards) */}
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          gap: 1,
        }}
      >
        {groups.flatMap((group) => group.kpis).map((kpi) => (
          <Card
            key={kpi.id}
            sx={{
              display: 'flex',
              flexDirection: 'row',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: 2,
              transition: 'all 0.3s ease',
              '&:hover': {
                boxShadow: 4,
                backgroundColor: 'rgba(0,0,0,0.02)',
              },
            }}
          >
            {/* Left Section - KPI Info */}
            <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 0.5 }}>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                {kpi.name}
              </Typography>
              {kpi.description && (
                <Typography variant="body2" color="textSecondary">
                  {kpi.description}
                </Typography>
              )}
            </Box>

            {/* Middle Section - Execution Status */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mx: 3 }}>
              {kpi.latest_execution ? (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {getStatusIcon(kpi.latest_execution.status)}
                  <Chip
                    label={kpi.latest_execution.status || 'pending'}
                    size="small"
                    color={getStatusColor(kpi.latest_execution.status)}
                    variant="outlined"
                  />
                  <Typography variant="body2" sx={{ ml: 1 }}>
                    <strong>{kpi.latest_execution.record_count}</strong> records
                  </Typography>
                </Box>
              ) : (
                <Typography variant="body2" color="textSecondary">
                  No executions yet
                </Typography>
              )}
            </Box>

            {/* Right Section - Actions */}
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                size="small"
                variant="outlined"
                startIcon={<VisibilityIcon />}
                onClick={() => handleViewResults(kpi)}
                disabled={!kpi.latest_execution}
              >
                View Results
              </Button>
            </Box>
          </Card>
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

