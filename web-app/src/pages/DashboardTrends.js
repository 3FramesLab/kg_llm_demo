import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Paper,
  Skeleton,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Schedule as ScheduleIcon,
  Refresh as RefreshIcon,
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  ShowChart as ShowChartIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';
import KPIResultsViewDialog from '../components/KPIResultsViewDialog';
import { API_BASE_URL, getKPIExecutions } from '../services/api';

const DashboardTrend = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedKPI, setSelectedKPI] = useState(null);
  const [resultsDialogOpen, setResultsDialogOpen] = useState(false);
  const [trendChartDialogOpen, setTrendChartDialogOpen] = useState(false);
  const [selectedKPIForChart, setSelectedKPIForChart] = useState(null);
  const [detailedTrendData, setDetailedTrendData] = useState([]);

  // Custom label component to display count on each data point
  const renderCustomLabel = (props) => {
    const { x, y, value } = props;
    return (
      <text
        x={x}
        y={y - 10}
        fill="#111827"
        textAnchor="middle"
        fontSize="0.75rem"
        fontWeight="600"
      >
        {value.toLocaleString()}
      </text>
    );
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    const response = await fetch(`${API_BASE_URL}/landing-kpi/dashboard`);
    const data = await response.json();
    setDashboardData(data);
    setLoading(false);
  };



  const handleViewResults = (kpi) => {
    setSelectedKPI(kpi);
    setResultsDialogOpen(true);
  };

  const handleSparklineClick = async (kpi) => {
    setSelectedKPIForChart(kpi);
    setTrendChartDialogOpen(true);

    // Fetch execution data when sparkline is clicked
    try {
      const result = await getKPIExecutions(kpi.id);

      if (result.data.success && result.data.executions) {
        // Get last 10 executions and extract record counts
        const executions = result.data.executions
          .filter(exec => exec.execution_status === 'success' && exec.number_of_records != null)
          .slice(0, 10)
          .reverse(); // Oldest to newest for chart

        const chartData = executions.map((exec) => ({
          date: new Date(exec.execution_timestamp).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric'
          }),
          records: exec.number_of_records,
          fullDate: exec.execution_timestamp
        }));
        setDetailedTrendData(chartData);
      } else {
        setDetailedTrendData([]);
      }
    } catch (error) {
      console.error('Error fetching execution data:', error);
      setDetailedTrendData([]);
    }
  };

  const handleRecordsClick = (kpi) => {
    // Same action as View Results button
    handleViewResults(kpi);
  };

  const handleRefresh = () => {
    fetchDashboardData();
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 1.5 }}>
        {/* Header Skeleton */}
        <Paper
          elevation={0}
          sx={{
            mb: 3,
            p: 2,
            borderRadius: 2,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            boxShadow: '0 4px 20px rgba(102, 126, 234, 0.3)',
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 3 }}>
            <Box sx={{ flex: '1 1 auto', minWidth: '250px' }}>
              <Skeleton variant="text" width={250} height={40} sx={{ bgcolor: 'rgba(255,255,255,0.2)' }} />
              <Skeleton variant="text" width={180} height={24} sx={{ bgcolor: 'rgba(255,255,255,0.15)', mt: 0.5 }} />
            </Box>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Skeleton variant="rectangular" width={160} height={70} sx={{ bgcolor: 'rgba(255,255,255,0.15)', borderRadius: 2 }} />
              <Skeleton variant="rectangular" width={160} height={70} sx={{ bgcolor: 'rgba(255,255,255,0.15)', borderRadius: 2 }} />
              <Skeleton variant="rectangular" width={120} height={70} sx={{ bgcolor: 'rgba(255,255,255,0.15)', borderRadius: 2 }} />
            </Box>
          </Box>
        </Paper>

        {/* Tabs Skeleton */}
        <Paper
          elevation={0}
          sx={{
            mb: 1.25,
            borderRadius: 2,
            border: '1px solid #e5e7eb',
            bgcolor: 'white',
          }}
        >
          <Skeleton variant="rectangular" height={42} sx={{ borderRadius: 2 }} />
        </Paper>

        {/* Content Skeletons */}
        <Grid container spacing={1.5}>
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={i}>
              <Skeleton
                variant="rectangular"
                height={240}
                sx={{ borderRadius: 2.5, boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}
              />
            </Grid>
          ))}
        </Grid>
      </Container>
    );
  }

  const groups = dashboardData?.groups || [];
  const totalKPIs = groups.reduce((sum, group) => sum + group.kpis.length, 0);

  if (totalKPIs === 0) {
    return (
      <Container maxWidth="xl" sx={{ py: 1.5 }}>
        {/* Header */}
        <Paper
          elevation={0}
          sx={{
            mb: 3,
            p: 2,
            borderRadius: 2,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            boxShadow: '0 4px 20px rgba(102, 126, 234, 0.3)',
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 3 }}>
            <Box sx={{ flex: '1 1 auto', minWidth: '250px' }}>
              <Typography variant="h4" fontWeight="700" sx={{ mb: 0.5, lineHeight: 1.2, fontSize: '1.875rem', letterSpacing: '-0.02em' }}>
                Dashboard Trends
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 500, fontSize: '0.9375rem', opacity: 0.95 }}>
                Monitor and track your key performance indicators
              </Typography>
            </Box>
          </Box>
        </Paper>

        {/* Empty State */}
        <Paper
          elevation={0}
          sx={{
            p: 4,
            textAlign: 'center',
            borderRadius: 3,
            border: '2px dashed #e5e7eb',
            bgcolor: '#fafbfc',
            boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
          }}
        >
          <Box
            sx={{
              width: 80,
              height: 80,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.5rem',
              boxShadow: '0 8px 24px rgba(99, 102, 241, 0.2)'
            }}
          >
            <AssessmentIcon sx={{ fontSize: 40, color: 'white' }} />
          </Box>
          <Typography variant="h5" fontWeight="700" sx={{ mb: 1, color: '#111827', fontSize: '1.375rem', letterSpacing: '-0.01em' }}>
            No KPIs Available
          </Typography>
          <Typography variant="body2" fontSize="0.9375rem" sx={{ mb: 2.5, maxWidth: 500, mx: 'auto', lineHeight: 1.6, color: '#6b7280' }}>
            Get started by creating your first KPI to monitor and track your key performance indicators.
          </Typography>
          <Button
            variant="contained"
            href="/landing-kpi"
            size="medium"
            sx={{
              py: 0.875,
              px: 2.5,
              borderRadius: 2,
              fontSize: '0.875rem',
              fontWeight: 600,
              textTransform: 'none',
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              boxShadow: '0 4px 12px rgba(99, 102, 241, 0.25)',
              '&:hover': {
                background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
                boxShadow: '0 6px 20px rgba(99, 102, 241, 0.35)',
                transform: 'translateY(-1px)'
              },
              transition: 'all 0.2s ease-in-out'
            }}
          >
            Go to KPI Management
          </Button>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 1.5 }}>
      {/* Header Section */}
      <Paper
        elevation={0}
        sx={{
          mb: 3,
          p: 2,
          borderRadius: 2,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          boxShadow: '0 4px 20px rgba(102, 126, 234, 0.3)',
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 3 }}>
          {/* Left Side - Title and Subtitle */}
          <Box sx={{ flex: '1 1 auto', minWidth: '250px' }}>
            <Typography variant="h5" fontWeight="700" sx={{ mb: 0.25, lineHeight: 1.2, fontSize: '1.15rem' }}>
              Dashboard Trends
            </Typography>
            <Typography variant="body2" sx={{ fontWeight: 500, fontSize: '0.9375rem', opacity: 0.95 }}>
              Monitor and track your key performance indicators
            </Typography>
          </Box>

          {/* Right Side - Refresh Icon */}
          <Tooltip title="Refresh Dashboard">
            <IconButton
              onClick={handleRefresh}
              disabled={loading}
              sx={{
                color: 'white',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                },
                '&:disabled': {
                  color: 'rgba(255, 255, 255, 0.5)',
                },
              }}
            >
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Paper>

      {/* KPI Cards - Grid Layout */}
      <Grid container spacing={1}>
        {groups.map((group) => (
          group.kpis.map((kpi) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={kpi.id}>
              <Card
                elevation={0}
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  borderRadius: 2,
                  border: '1px solid #e5e7eb',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  bgcolor: 'white',
                  boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
                  position: 'relative',
                  overflow: 'hidden',
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: '3px',
                    background: 'linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%)',
                    opacity: 0.9,
                  },
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 12px 24px -4px rgba(99, 102, 241, 0.12), 0 8px 16px -4px rgba(99, 102, 241, 0.08)',
                    borderColor: '#c7d2fe',
                    '&::before': {
                      opacity: 1,
                    },
                  },
                }}
              >
                <CardContent sx={{ flex: 1, p: 1.5, display: 'flex', flexDirection: 'column' }}>
                  {/* KPI Name */}
                  <Typography
                    variant="h6"
                    fontWeight="600"
                    fontSize="0.9375rem"
                    sx={{
                      mb: kpi.description ? 0.5 : 0.75,
                      color: '#111827',
                      lineHeight: 1.3,
                      letterSpacing: '-0.01em',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                      wordBreak: 'break-word'
                    }}
                  >
                    {kpi.name}
                  </Typography>

                  {/* KPI Description - Only 2 lines if exists */}
                  {kpi.description && (
                    <Typography
                      variant="body2"
                      fontSize="0.8125rem"
                      sx={{
                        color: '#6b7280',
                        mb: 1,
                        lineHeight: 1.5,
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                        wordBreak: 'break-word'
                      }}
                    >
                      {kpi.description}
                    </Typography>
                  )}

                  {/* Sparkline and Records Count in Same Row */}
                  {kpi.latest_execution ? (
                    <Box sx={{ mt: 'auto', pt: 1 }}>
                      <Box
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          gap: 1.5,
                          p: 1.25,
                          bgcolor: '#f8fafc',
                          borderRadius: 1.5,
                          border: '1px solid #e2e8f0',
                          boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
                        }}
                      >
                        {/* Sparkline Chart - LEFT SIDE - Clickable */}
                        <Box
                          onClick={() => handleSparklineClick(kpi)}
                          sx={{
                            height: 48,
                            width: 90,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            cursor: 'pointer',
                            borderRadius: 1.5,
                            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                            bgcolor: '#f8fafc',
                            border: '2px solid #e2e8f0',
                            padding: '6px',
                            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.08)',
                            '&:hover': {
                              bgcolor: '#e2e8f0',
                              transform: 'scale(1.08) translateY(-2px)',
                              borderColor: '#94a3b8',
                              boxShadow: '0 6px 12px rgba(0, 0, 0, 0.15), 0 3px 6px rgba(0, 0, 0, 0.1)',
                            }
                          }}
                        >
                          <ShowChartIcon
                            sx={{
                              fontSize: 28,
                              color: '#6366f1',
                              opacity: 0.7,
                              transition: 'all 0.3s ease',
                            }}
                          />
                        </Box>

                        {/* Records Count Section - RIGHT SIDE - Clickable */}
                        <Box
                          onClick={() => handleRecordsClick(kpi)}
                          sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 1,
                            minWidth: 'fit-content',
                            cursor: 'pointer',
                            px: 1.5,
                            py: 0.75,
                            borderRadius: 1.5,
                            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                            bgcolor: 'rgba(59, 130, 246, 0.12)',
                            '&:hover': {
                              bgcolor: 'rgba(59, 130, 246, 0.20)',
                              transform: 'translateY(-2px)',
                              '& .records-icon': {
                                transform: 'scale(1.15) rotate(5deg)',
                                boxShadow: '0 4px 8px rgba(59, 130, 246, 0.25)',
                              }
                            }
                          }}
                        >
                          <Typography
                            variant="h6"
                            sx={{
                              fontSize: '1.5rem',
                              fontWeight: 700,
                              color: '#111827',
                              lineHeight: 1,
                              whiteSpace: 'nowrap',
                              letterSpacing: '-0.02em',
                            }}
                          >
                            {kpi.latest_execution.record_count.toLocaleString()}
                          </Typography>
                        </Box>
                      </Box>
                    </Box>

                  ) : (
                    <Box
                      sx={{
                        mt: 'auto',
                        pt: 1,
                        p: 1.5,
                        bgcolor: '#f8fafc',
                        borderRadius: 1.5,
                        border: '1.5px dashed #cbd5e1',
                        textAlign: 'center',
                      }}
                    >
                      <Box
                        sx={{
                          width: 40,
                          height: 40,
                          borderRadius: '50%',
                          bgcolor: '#e2e8f0',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          margin: '0 auto 0.75rem',
                        }}
                      >
                        <ScheduleIcon sx={{ fontSize: 20, color: '#94a3b8' }} />
                      </Box>
                      <Typography
                        variant="body2"
                        fontSize="0.8125rem"
                        sx={{
                          color: '#64748b',
                          fontWeight: 500,
                          lineHeight: 1.4
                        }}
                      >
                        No Executions Yet
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))
        ))}
      </Grid>

      {/* Results Dialog */}
      <KPIResultsViewDialog
        open={resultsDialogOpen}
        onClose={() => setResultsDialogOpen(false)}
        kpi={selectedKPI}
        showMetadata={false}
      />

      {/* Trend Chart Dialog */}
      <Dialog
        open={trendChartDialogOpen}
        onClose={() => setTrendChartDialogOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 2,
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)'
          }
        }}
      >
        <DialogTitle
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            pb: 2,
            borderBottom: '1px solid #e5e7eb'
          }}
        >
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700, color: '#111827', mb: 0.5 }}>
              {selectedKPIForChart?.name || 'KPI'} - Trend Analysis
            </Typography>
            <Typography variant="body2" sx={{ color: '#6b7280', fontSize: '0.875rem' }}>
              Last 7 days execution history
            </Typography>
          </Box>
          <IconButton
            onClick={() => setTrendChartDialogOpen(false)}
            sx={{
              color: '#6b7280',
              '&:hover': {
                bgcolor: '#f3f4f6'
              }
            }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>

        <DialogContent sx={{ pt: 3, pb: 2 }}>
          {detailedTrendData.length > 0 ? (
            <Box sx={{ width: '100%', height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={detailedTrendData}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis
                    dataKey="date"
                    stroke="#6b7280"
                    style={{ fontSize: '0.75rem' }}
                    angle={0}
                    textAnchor="middle"
                  />
                  <YAxis
                    stroke="#6b7280"
                    style={{ fontSize: '0.75rem' }}
                    domain={[
                      (dataMin) => Math.floor(dataMin * 0.95),
                      (dataMax) => Math.ceil(dataMax * 1.05)
                    ]}
                    label={{
                      value: 'Record Count',
                      angle: -90,
                      position: 'insideLeft',
                      style: { fontSize: '0.875rem', fill: '#6b7280' }
                    }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
                    }}
                    labelStyle={{ color: '#111827', fontWeight: 600 }}
                  />
                  <Legend
                    wrapperStyle={{ fontSize: '0.875rem' }}
                    iconType="line"
                  />
                  <Line
                    type="monotone"
                    dataKey="records"
                    stroke="#6366f1"
                    strokeWidth={3}
                    dot={{ fill: '#6366f1', r: 5 }}
                    activeDot={{ r: 7 }}
                    name="Records"
                    label={renderCustomLabel}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          ) : (
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: 300,
                color: '#9ca3af'
              }}
            >
              <ShowChartIcon sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
              <Typography variant="body1" sx={{ fontWeight: 600 }}>
                No trend data available
              </Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                Execute this KPI to start collecting trend data
              </Typography>
            </Box>
          )}
        </DialogContent>

        <DialogActions sx={{ px: 3, py: 2, borderTop: '1px solid #e5e7eb' }}>
          <Button
            onClick={() => setTrendChartDialogOpen(false)}
            variant="contained"
            sx={{
              bgcolor: '#6366f1',
              color: 'white',
              textTransform: 'none',
              fontWeight: 600,
              px: 3,
              '&:hover': {
                bgcolor: '#4f46e5'
              }
            }}
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default DashboardTrend;

