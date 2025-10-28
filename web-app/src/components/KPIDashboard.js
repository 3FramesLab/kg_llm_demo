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
  Grid,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Schedule as ScheduleIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material';
import { VegaLite } from 'react-vega';
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
      const response = await fetch(`${API_BASE_URL}/landing-kpi/dashboard`);
      
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

  // Prepare chart data
  const prepareChartData = () => {
    if (!dashboardData || !dashboardData.groups) return null;

    const allKPIs = dashboardData.groups.flatMap(group => group.kpis);

    // Record counts bar chart data
    const recordCountData = allKPIs
      .filter(kpi => kpi.latest_execution && kpi.latest_execution.record_count > 0)
      .map(kpi => ({
        kpi: kpi.name,
        records: kpi.latest_execution.record_count,
        definition: kpi.definition || 'No definition available'
      }));

    // Status distribution pie chart data
    const statusCounts = allKPIs.reduce((acc, kpi) => {
      const status = kpi.latest_execution?.status || 'pending';
      acc[status] = (acc[status] || 0) + 1;
      return acc;
    }, {});

    const statusData = Object.entries(statusCounts).map(([status, count]) => ({
      status: status.charAt(0).toUpperCase() + status.slice(1),
      count
    }));

    // Group distribution
    const groupData = dashboardData.groups.map(group => ({
      group: group.group_name,
      count: group.kpis.length
    }));

    return { recordCountData, statusData, groupData };
  };

  const chartData = prepareChartData();

  // Vega-Lite chart specs
  const recordCountSpec = {
    $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
    description: 'KPI Record Counts',
    width: 500,
    height: 300,
    autosize: {
      type: 'fit',
      contains: 'padding'
    },
    layer: [
      {
        mark: { type: 'bar' },
        encoding: {
          x: {
            field: 'kpi',
            type: 'nominal',
            axis: { labelAngle: 0, labelLimit: 200, labelFontSize: 14, labelFontWeight: 'bold' },
            title: 'KPI Name'
          },
          y: {
            field: 'records',
            type: 'quantitative',
            title: 'Record Count'
          },
          color: {
            field: 'kpi',
            type: 'nominal',
            scale: { scheme: 'category20' },
            legend: null
          },
          tooltip: [
            { field: 'definition', type: 'nominal', title: 'Definition' }
          ]
        }
      },
      {
        mark: { type: 'text', align: 'center', baseline: 'bottom', dy: -5, fontSize: 12, fontWeight: 'bold' },
        encoding: {
          x: {
            field: 'kpi',
            type: 'nominal'
          },
          y: {
            field: 'records',
            type: 'quantitative'
          },
          text: { field: 'records', type: 'quantitative' }
        }
      }
    ]
  };

  const statusDistributionSpec = {
    $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
    description: 'KPI Status Distribution',
    width: 300,
    height: 300,
    mark: { type: 'arc', innerRadius: 50 },
    encoding: {
      theta: { field: 'count', type: 'quantitative' },
      color: {
        field: 'status',
        type: 'nominal',
        scale: {
          domain: ['Success', 'Failed', 'Pending'],
          range: ['#4caf50', '#f44336', '#ff9800']
        },
        title: 'Status'
      },
      tooltip: [
        { field: 'status', type: 'nominal', title: 'Status' },
        { field: 'count', type: 'quantitative', title: 'Count' }
      ]
    }
  };

  const groupDistributionSpec = {
    $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
    description: 'KPIs by Group',
    width: 700,
    height: 300,
    autosize: {
      type: 'fit',
      contains: 'padding'
    },
    mark: 'bar',
    encoding: {
      x: {
        field: 'group',
        type: 'nominal',
        title: 'Group',
        axis: { labelAngle: -45, labelLimit: 100 }
      },
      y: {
        field: 'count',
        type: 'quantitative',
        title: 'Number of KPIs'
      },
      color: { value: '#1976d2' },
      tooltip: [
        { field: 'group', type: 'nominal', title: 'Group' },
        { field: 'count', type: 'quantitative', title: 'KPI Count' }
      ]
    }
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

      {/* Charts Section */}
      {chartData && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {/* Record Counts Bar Chart */}
          {chartData.recordCountData.length > 0 && (
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Record Counts by KPI
                </Typography>
                <Box sx={{ width: '100%', overflowX: 'auto' }}>
                  <VegaLite
                    spec={{
                      ...recordCountSpec,
                      data: { values: chartData.recordCountData }
                    }}
                    actions={false}
                  />
                </Box>
              </Paper>
            </Grid>
          )}

          {/* Status Distribution Pie Chart */}
          {chartData.statusData.length > 0 && (
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  KPI Status Distribution
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                  <VegaLite
                    spec={{
                      ...statusDistributionSpec,
                      data: { values: chartData.statusData }
                    }}
                    actions={false}
                  />
                </Box>
              </Paper>
            </Grid>
          )}

          {/* Group Distribution Bar Chart */}
          {chartData.groupData.length > 0 && (
            <Grid item xs={12}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  KPIs by Group
                </Typography>
                <Box sx={{ width: '100%', overflowX: 'auto' }}>
                  <VegaLite
                    spec={{
                      ...groupDistributionSpec,
                      data: { values: chartData.groupData }
                    }}
                    actions={false}
                  />
                </Box>
              </Paper>
            </Grid>
          )}
        </Grid>
      )}

      {/* KPI List Section */}
      <Typography variant="h5" sx={{ mb: 2, fontWeight: 'bold' }}>
        KPI Details
      </Typography>

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

