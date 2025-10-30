import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  Chip,
  Paper,
  Skeleton,
  Grid,
  IconButton,
} from '@mui/material';
import {
  Error as ErrorIcon,
  Schedule as ScheduleIcon,
  Visibility as VisibilityIcon,
  Refresh as RefreshIcon,
  Assessment as AssessmentIcon,
  Dashboard as DashboardIcon,
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

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Header Skeleton */}
        <Paper
          elevation={0}
          sx={{
            mb: 4,
            p: 3.5,
            borderRadius: 3,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            boxShadow: '0 8px 32px rgba(102, 126, 234, 0.25)',
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 3 }}>
            <Box sx={{ flex: '1 1 auto', minWidth: '250px' }}>
              <Skeleton variant="text" width={250} height={48} sx={{ bgcolor: 'rgba(255,255,255,0.2)' }} />
              <Skeleton variant="text" width={180} height={28} sx={{ bgcolor: 'rgba(255,255,255,0.15)', mt: 1 }} />
            </Box>
            <Box sx={{ display: 'flex', gap: 2.5, flexWrap: 'wrap' }}>
              <Skeleton variant="rectangular" width={180} height={80} sx={{ bgcolor: 'rgba(255,255,255,0.15)', borderRadius: 2.5 }} />
              <Skeleton variant="rectangular" width={180} height={80} sx={{ bgcolor: 'rgba(255,255,255,0.15)', borderRadius: 2.5 }} />
              <Skeleton variant="rectangular" width={140} height={80} sx={{ bgcolor: 'rgba(255,255,255,0.15)', borderRadius: 2.5 }} />
            </Box>
          </Box>
        </Paper>

        {/* Content Skeletons */}
        <Grid container spacing={2.5}>
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={i}>
              <Skeleton
                variant="rectangular"
                height={260}
                sx={{ borderRadius: 3, boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}
              />
            </Grid>
          ))}
        </Grid>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Header */}
        <Paper
          elevation={0}
          sx={{
            mb: 4,
            p: 3.5,
            borderRadius: 3,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            boxShadow: '0 8px 32px rgba(102, 126, 234, 0.25)',
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 3 }}>
            <Box sx={{ flex: '1 1 auto', minWidth: '250px' }}>
              <Typography variant="h4" fontWeight="700" sx={{ mb: 0.75, lineHeight: 1.2, fontSize: '2rem', letterSpacing: '-0.02em' }}>
                KPI Dashboard
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 500, fontSize: '1rem', opacity: 0.95 }}>
                Monitor and track your key performance indicators
              </Typography>
            </Box>
          </Box>
        </Paper>

        {/* Error Alert */}
        <Alert
          severity="error"
          icon={<ErrorIcon sx={{ fontSize: 24 }} />}
          sx={{
            mb: 3,
            borderRadius: 3,
            border: '1px solid #fee2e2',
            bgcolor: '#fef8f8',
            boxShadow: '0 2px 8px rgba(220, 38, 38, 0.08)',
            p: 2,
            '& .MuiAlert-message': {
              fontWeight: 500,
              fontSize: '0.9375rem',
              color: '#dc2626'
            }
          }}
        >
          {error}
        </Alert>

        <Button
          variant="contained"
          size="large"
          onClick={handleRefresh}
          startIcon={<RefreshIcon />}
          sx={{
            py: 1.25,
            px: 3.5,
            borderRadius: 2.5,
            fontSize: '0.9375rem',
            fontWeight: 600,
            textTransform: 'none',
            background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
            boxShadow: '0 4px 16px rgba(99, 102, 241, 0.3)',
            '&:hover': {
              background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
              boxShadow: '0 8px 24px rgba(99, 102, 241, 0.4)',
              transform: 'translateY(-2px)'
            },
            transition: 'all 0.3s ease-in-out'
          }}
        >
          Retry
        </Button>
      </Container>
    );
  }

  const groups = dashboardData?.groups || [];
  const totalKPIs = groups.reduce((sum, group) => sum + group.kpis.length, 0);

  if (totalKPIs === 0) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Header */}
        <Paper
          elevation={0}
          sx={{
            mb: 4,
            p: 3.5,
            borderRadius: 3,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            boxShadow: '0 8px 32px rgba(102, 126, 234, 0.25)',
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 3 }}>
            <Box sx={{ flex: '1 1 auto', minWidth: '250px' }}>
              <Typography variant="h4" fontWeight="700" sx={{ mb: 0.75, lineHeight: 1.2, fontSize: '2rem', letterSpacing: '-0.02em' }}>
                KPI Dashboard
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 500, fontSize: '1rem', opacity: 0.95 }}>
                Monitor and track your key performance indicators
              </Typography>
            </Box>
          </Box>
        </Paper>

        {/* Empty State */}
        <Paper
          elevation={0}
          sx={{
            p: 6,
            textAlign: 'center',
            borderRadius: 4,
            border: '2px dashed #e5e7eb',
            bgcolor: '#fafbfc',
            boxShadow: '0 2px 8px rgba(0,0,0,0.05)'
          }}
        >
          <Box
            sx={{
              width: 96,
              height: 96,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 2rem',
              boxShadow: '0 12px 32px rgba(99, 102, 241, 0.25)'
            }}
          >
            <AssessmentIcon sx={{ fontSize: 48, color: 'white' }} />
          </Box>
          <Typography variant="h5" fontWeight="700" sx={{ mb: 1.5, color: '#111827', fontSize: '1.5rem', letterSpacing: '-0.01em' }}>
            No KPIs Available
          </Typography>
          <Typography variant="body1" fontSize="1rem" sx={{ mb: 3, maxWidth: 520, mx: 'auto', lineHeight: 1.7, color: '#6b7280' }}>
            Get started by creating your first KPI to monitor and track your key performance indicators.
          </Typography>
          <Button
            variant="contained"
            href="/landing-kpi"
            size="large"
            sx={{
              py: 1.25,
              px: 3.5,
              borderRadius: 2.5,
              fontSize: '0.9375rem',
              fontWeight: 600,
              textTransform: 'none',
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              boxShadow: '0 4px 16px rgba(99, 102, 241, 0.3)',
              '&:hover': {
                background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
                boxShadow: '0 8px 24px rgba(99, 102, 241, 0.4)',
                transform: 'translateY(-2px)'
              },
              transition: 'all 0.3s ease-in-out'
            }}
          >
            Go to KPI Management
          </Button>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header Section */}
      <Paper
        elevation={0}
        sx={{
          mb: 4,
          p: 3.5,
          borderRadius: 3,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          boxShadow: '0 8px 32px rgba(102, 126, 234, 0.25)',
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 3 }}>
          {/* Left Side - Title and Subtitle */}
          <Box sx={{ flex: '1 1 auto', minWidth: '250px' }}>
            <Typography variant="h4" fontWeight="700" sx={{ mb: 0.75, lineHeight: 1.2, fontSize: '2rem', letterSpacing: '-0.02em' }}>
              KPI Dashboard
            </Typography>
            <Typography variant="body1" sx={{ fontWeight: 500, fontSize: '1rem', opacity: 0.95 }}>
              Monitor and track your key performance indicators
            </Typography>
          </Box>

          {/* Right Side - Stats Boxes */}
          <Box sx={{ display: 'flex', gap: 1.5, flexWrap: 'wrap', alignItems: 'center' }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1.25,
                bgcolor: 'rgba(255, 255, 255, 0.2)',
                px: 2,
                py: 1.25,
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.3)',
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  bgcolor: 'rgba(255, 255, 255, 0.25)',
                  borderColor: 'rgba(255, 255, 255, 0.4)',
                }
              }}
            >
              <Box
                sx={{
                  width: 36,
                  height: 36,
                  borderRadius: 1.5,
                  background: 'rgba(255, 255, 255, 0.3)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <AssessmentIcon sx={{ fontSize: 20, color: 'white' }} />
              </Box>
              <Box>
                <Typography variant="h6" fontWeight="700" sx={{ lineHeight: 1.2, fontSize: '1.25rem', color: 'white' }}>{totalKPIs}</Typography>
                <Typography variant="body2" sx={{ fontSize: '0.75rem', fontWeight: 500, color: 'rgba(255, 255, 255, 0.9)' }}>KPI{totalKPIs !== 1 ? 's' : ''}</Typography>
              </Box>
            </Box>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1.25,
                bgcolor: 'rgba(255, 255, 255, 0.2)',
                px: 2,
                py: 1.25,
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.3)',
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  bgcolor: 'rgba(255, 255, 255, 0.25)',
                  borderColor: 'rgba(255, 255, 255, 0.4)',
                }
              }}
            >
              <Box
                sx={{
                  width: 36,
                  height: 36,
                  borderRadius: 1.5,
                  background: 'rgba(255, 255, 255, 0.3)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <DashboardIcon sx={{ fontSize: 20, color: 'white' }} />
              </Box>
              <Box>
                <Typography variant="h6" fontWeight="700" sx={{ lineHeight: 1.2, fontSize: '1.25rem', color: 'white' }}>{groups.length}</Typography>
                <Typography variant="body2" sx={{ fontSize: '0.75rem', fontWeight: 500, color: 'rgba(255, 255, 255, 0.9)' }}>Group{groups.length !== 1 ? 's' : ''}</Typography>
              </Box>
            </Box>
            <IconButton
              onClick={handleRefresh}
              sx={{
                background: 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                '&:hover': {
                  background: 'rgba(255, 255, 255, 0.3)',
                  border: '1px solid rgba(255, 255, 255, 0.4)',
                  transform: 'translateY(-1px)',
                  boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)'
                },
                width: '48px',
                height: '48px',
                borderRadius: 2,
                boxShadow: 'none',
                transition: 'all 0.2s ease-in-out',
              }}
            >
              <RefreshIcon sx={{ fontSize: 24 }} />
            </IconButton>
          </Box>
        </Box>
      </Paper>

      {/* KPI Cards - Grid Layout */}
      <Grid container spacing={2.5}>
            {groups.map((group) => (
              group.kpis.map((kpi) => (
                <Grid item xs={12} sm={6} md={4} lg={3} key={kpi.id}>
                  <Card
                    elevation={0}
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      borderRadius: 2.5,
                      border: '1px solid #e5e7eb',
                      transition: 'all 0.3s ease',
                      bgcolor: 'white',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
                      position: 'relative',
                      overflow: 'hidden',
                      '&::before': {
                        content: '""',
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        height: '3px',
                        background: 'linear-gradient(90deg, #c7d2fe 0%, #ddd6fe 50%, #f5d0fe 100%)',
                      },
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: '0 8px 24px rgba(139, 92, 246, 0.15)',
                        borderColor: '#c7d2fe',
                      },
                    }}
                  >
                    {/* Compact Header */}
                    <Box
                      sx={{
                        px: 1.5,
                        py: 1,
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        borderBottom: '1px solid #f3f4f6',
                        bgcolor: '#fafbfc'
                      }}
                    >
                      <Chip
                        label={group.group_name}
                        size="small"
                        sx={{
                          background: '#faf5ff',
                          color: '#9333ea',
                          fontWeight: 600,
                          border: 'none',
                          fontSize: '0.6875rem',
                          height: 22,
                          borderRadius: 1.5,
                          '& .MuiChip-label': {
                            px: 1,
                            py: 0
                          },
                        }}
                      />
                    </Box>

                    <CardContent sx={{ flex: 1, p: 1.5, display: 'flex', flexDirection: 'column' }}>
                      {/* KPI Name and Records Row */}
                      {kpi.latest_execution ? (
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 1.5, mb: kpi.description ? 0.5 : 1 }}>
                          {/* KPI Name */}
                          <Typography
                            variant="h6"
                            fontWeight="700"
                            fontSize="0.9375rem"
                            sx={{
                              color: '#111827',
                              lineHeight: 1.3,
                              letterSpacing: '-0.01em',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                              flex: 1,
                              minWidth: 0
                            }}
                          >
                            {kpi.name}
                          </Typography>

                          {/* Records */}
                          <Box
                            sx={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: 0.75,
                              px: 1.25,
                              py: 0.75,
                              bgcolor: '#fafbfc',
                              borderRadius: 2,
                              border: '1px solid #f3f4f6',
                              flexShrink: 0
                            }}
                          >
                            <Box>
                              <Typography
                                variant="caption"
                                sx={{
                                  display: 'block',
                                  fontSize: '0.625rem',
                                  fontWeight: 600,
                                  color: '#6b7280',
                                  textTransform: 'uppercase',
                                  letterSpacing: '0.02em',
                                  lineHeight: 1.2,
                                }}
                              >
                                Records
                              </Typography>
                              <Typography
                                variant="h6"
                                sx={{
                                  fontSize: '0.8125rem',
                                  fontWeight: 700,
                                  color: '#111827',
                                  lineHeight: 1.3,
                                  whiteSpace: 'nowrap',
                                }}
                              >
                                {kpi.latest_execution.record_count.toLocaleString()}
                              </Typography>
                            </Box>
                          </Box>
                        </Box>
                      ) : (
                        <Typography
                          variant="h6"
                          fontWeight="700"
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
                      )}

                      {/* KPI Description */}
                      {kpi.description && (
                        <Typography
                          variant="body2"
                          fontSize="0.8125rem"
                          sx={{
                            color: '#6b7280',
                            mb: 1,
                            lineHeight: 1.4,
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

                      {/* Error Message */}
                      {kpi.latest_execution && kpi.latest_execution.error_message && (
                        <Alert
                          severity="error"
                          icon={<ErrorIcon sx={{ fontSize: 14 }} />}
                          sx={{
                            mt: 'auto',
                            mb: 0,
                            borderRadius: 2,
                            fontSize: '0.6875rem',
                            py: 0.5,
                            bgcolor: '#fef8f8',
                            border: '1px solid #fee2e2',
                            boxShadow: 'none',
                            '& .MuiAlert-icon': {
                              fontSize: 14,
                              color: '#f87171',
                              mr: 0.75
                            },
                            '& .MuiAlert-message': {
                              color: '#dc2626',
                              fontWeight: 500,
                              lineHeight: 1.4,
                              padding: 0
                            }
                          }}
                        >
                          {kpi.latest_execution.error_message}
                        </Alert>
                      )}

                      {/* No Executions Yet State */}
                      {!kpi.latest_execution && (
                        <Box
                          sx={{
                            mt: 'auto',
                            p: 1.5,
                            bgcolor: '#fafbfc',
                            borderRadius: 2,
                            border: '1px dashed #e5e7eb',
                            textAlign: 'center',
                          }}
                        >
                          <Box
                            sx={{
                              width: 36,
                              height: 36,
                              borderRadius: '50%',
                              bgcolor: '#f3f4f6',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              margin: '0 auto 0.5rem',
                            }}
                          >
                            <ScheduleIcon sx={{ fontSize: 18, color: '#9ca3af' }} />
                          </Box>
                          <Typography
                            variant="body2"
                            fontSize="0.75rem"
                            sx={{
                              color: '#6b7280',
                              fontWeight: 600,
                              lineHeight: 1.3
                            }}
                          >
                            No Executions Yet
                          </Typography>
                        </Box>
                      )}
                    </CardContent>

                    {/* Card Footer with Action Button */}
                    <Box
                      sx={{
                        px: 1.5,
                        pb: 1.5,
                        pt: 0
                      }}
                    >
                      <Button
                        fullWidth
                        variant="contained"
                        size="medium"
                        startIcon={<VisibilityIcon sx={{ fontSize: 16 }} />}
                        onClick={() => handleViewResults(kpi)}
                        disabled={!kpi.latest_execution}
                        sx={{
                          py: 0.875,
                          borderRadius: 2,
                          fontSize: '0.8125rem',
                          fontWeight: 600,
                          textTransform: 'none',
                          background: kpi.latest_execution
                            ? 'linear-gradient(135deg, #c7d2fe 0%, #ddd6fe 100%)'
                            : '#f9fafb',
                          color: kpi.latest_execution ? '#6366f1' : '#9ca3af',
                          boxShadow: 'none',
                          border: kpi.latest_execution ? '1px solid #e9d5ff' : '1px solid #f3f4f6',
                          minHeight: 'unset',
                          '&:hover': {
                            background: kpi.latest_execution
                              ? 'linear-gradient(135deg, #a5b4fc 0%, #c4b5fd 100%)'
                              : '#f3f4f6',
                            boxShadow: kpi.latest_execution ? '0 2px 8px rgba(99, 102, 241, 0.2)' : 'none',
                            transform: kpi.latest_execution ? 'translateY(-1px)' : 'none',
                            borderColor: kpi.latest_execution ? '#ddd6fe' : '#e5e7eb'
                          },
                          '&:disabled': {
                            background: '#f9fafb',
                            color: '#9ca3af',
                            boxShadow: 'none',
                            border: '1px solid #f3f4f6'
                          },
                          transition: 'all 0.3s ease-in-out'
                        }}
                      >
                        {kpi.latest_execution ? 'View Results' : 'No Results'}
                      </Button>
                    </Box>
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
        showMetadata={true}
      />
    </Container>
  );
};

export default KPIDashboard;

