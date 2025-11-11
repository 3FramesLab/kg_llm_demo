/**
 * KPI Analytics Dashboard - Enhanced dashboard for separate KPI database
 * Shows KPIs with analytics features, SQL preview, and enhanced execution info
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  Chip,
  Grid,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Skeleton,
  Badge,
  LinearProgress
} from '@mui/material';
import {
  Error as ErrorIcon,
  Schedule as ScheduleIcon,
  Visibility as VisibilityIcon,
  Refresh as RefreshIcon,
  Assessment as AssessmentIcon,
  Dashboard as DashboardIcon,
  ExpandMore as ExpandMoreIcon,
  PlayArrow as PlayArrowIcon,
  Code as CodeIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon,
  TrendingUp as TrendingUpIcon,
  History as HistoryIcon
} from '@mui/icons-material';
import { 
  listKPIs, 
  executeKPI, 
  formatExecutionTime, 
  getStatusColor, 
  getPriorityColor,
  hasOpsPlanner,
  involvesHanaMaster
} from '../services/kpiAnalyticsApi';
import KPIAnalyticsForm from './KPIAnalyticsForm';
import KPIAnalyticsExecutionDialog from './KPIAnalyticsExecutionDialog';

const KPIAnalyticsDashboard = () => {
  const navigate = useNavigate();
  const [kpis, setKpis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  
  // Dialog states
  const [createFormOpen, setCreateFormOpen] = useState(false);
  const [executionDialogOpen, setExecutionDialogOpen] = useState(false);
  const [selectedKPI, setSelectedKPI] = useState(null);

  useEffect(() => {
    fetchKPIs();
  }, []);

  const fetchKPIs = async () => {
    try {
      setError(null);
      const response = await listKPIs();
      setKpis(response.data.data || []);
    } catch (err) {
      setError('Failed to fetch KPIs: ' + (err.response?.data?.error || err.message));
      console.error('Error fetching KPIs:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchKPIs();
  };

  const handleExecuteKPI = (kpi) => {
    setSelectedKPI(kpi);
    setExecutionDialogOpen(true);
  };

  const handleCreateSuccess = () => {
    fetchKPIs();
  };

  const handleExecutionSuccess = (executionResult, kpiData) => {
    console.log('handleExecutionSuccess called with:', executionResult);
    console.log('kpiData passed:', kpiData);
    console.log('selectedKPI:', selectedKPI);

    fetchKPIs();

    // Use the passed KPI data first, fallback to selectedKPI
    const kpiToUse = kpiData || selectedKPI;

    // Navigate to execution history page to show the results
    if (kpiToUse) {
      console.log('Navigating to execution history for KPI:', kpiToUse.id);
      const historyPath = `/landing-kpi/${kpiToUse.id}/history`;
      console.log('Navigation path:', historyPath);
      console.log('Current location before navigation:', window.location.pathname);

      try {
        navigate(historyPath);
        console.log('Navigation initiated successfully');

        // Verify navigation after a short delay
        setTimeout(() => {
          console.log('Current location after navigation:', window.location.pathname);
          // If navigation didn't work, try fallback
          if (window.location.pathname !== historyPath) {
            console.warn('Navigation may have failed, trying fallback method');
            window.location.href = historyPath;
          }
        }, 500);
      } catch (navError) {
        console.error('Navigation error:', navError);
        // Fallback to direct window navigation
        console.log('Using fallback navigation method');
        window.location.href = historyPath;
      }
    } else {
      console.warn('No KPI data available for navigation');
    }
  };

  const handleViewResults = (kpi) => {
    navigate(`/landing-kpi/${kpi.id}/history`);
  };

  // Group KPIs by group_name
  const groupedKPIs = kpis.reduce((groups, kpi) => {
    const group = kpi.group_name || 'Ungrouped';
    if (!groups[group]) {
      groups[group] = [];
    }
    groups[group].push(kpi);
    return groups;
  }, {});

  const getExecutionStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'success':
        return <AssessmentIcon color="success" />;
      case 'error':
      case 'failed':
        return <ErrorIcon color="error" />;
      case 'pending':
      case 'running':
        return <ScheduleIcon color="warning" />;
      default:
        return <ScheduleIcon color="disabled" />;
    }
  };

  const getSLAStatus = (executionTime, targetSLA) => {
    if (!executionTime || !targetSLA) return 'unknown';
    const executionSeconds = executionTime / 1000;
    if (executionSeconds <= targetSLA) return 'good';
    if (executionSeconds <= targetSLA * 1.5) return 'warning';
    return 'critical';
  };

  const getSLAColor = (status) => {
    switch (status) {
      case 'good': return 'success';
      case 'warning': return 'warning';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box sx={{ mb: 4 }}>
          <Skeleton variant="text" width={300} height={40} />
          <Skeleton variant="text" width={500} height={24} />
        </Box>
        <Grid container spacing={3}>
          {[1, 2, 3, 4].map((i) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={i}>
              <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 2 }} />
            </Grid>
          ))}
        </Grid>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        mb: 4,
        p: 3,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: 2,
        color: 'white'
      }}>
        <Box>
          <Typography variant="h4" fontWeight="bold" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <DashboardIcon fontSize="large" />
            KPI Analytics Dashboard
          </Typography>
          <Typography variant="subtitle1" sx={{ opacity: 0.9, mt: 0.5 }}>
            Monitor KPIs with separate analytics database • Enhanced with ops_planner
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
            <Chip 
              icon={<StorageIcon />} 
              label="Analytics Database" 
              variant="outlined" 
              sx={{ color: 'white', borderColor: 'white' }} 
            />
            <Chip 
              icon={<CodeIcon />} 
              label="SQL Enhancement" 
              variant="outlined" 
              sx={{ color: 'white', borderColor: 'white' }} 
            />
          </Box>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh KPIs">
            <IconButton 
              onClick={handleRefresh} 
              disabled={refreshing}
              sx={{ color: 'white' }}
            >
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<AssessmentIcon />}
            onClick={() => setCreateFormOpen(true)}
            sx={{
              bgcolor: 'rgba(255,255,255,0.2)',
              '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' }
            }}
          >
            Create KPI
          </Button>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Loading Progress */}
      {refreshing && (
        <LinearProgress sx={{ mb: 2 }} />
      )}

      {/* Empty State */}
      {kpis.length === 0 && !loading && (
        <Box sx={{ 
          textAlign: 'center', 
          py: 8,
          background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
          borderRadius: 3
        }}>
          <AssessmentIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h5" fontWeight="600" sx={{ mb: 1.5 }}>
            No KPIs Available
          </Typography>
          <Typography variant="body1" sx={{ mb: 3, color: 'text.secondary' }}>
            Create your first KPI to start monitoring with the analytics database
          </Typography>
          <Button
            variant="contained"
            startIcon={<AssessmentIcon />}
            onClick={() => setCreateFormOpen(true)}
            size="large"
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
              }
            }}
          >
            Create First KPI
          </Button>
        </Box>
      )}

      {/* KPI Groups */}
      {Object.entries(groupedKPIs).map(([groupName, groupKPIs]) => (
        <Accordion key={groupName} defaultExpanded sx={{ mb: 2, borderRadius: 2 }}>
          <AccordionSummary 
            expandIcon={<ExpandMoreIcon />}
            sx={{ 
              bgcolor: 'grey.50',
              borderRadius: '8px 8px 0 0',
              '&.Mui-expanded': {
                borderRadius: '8px 8px 0 0'
              }
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
              <Typography variant="h6" fontWeight="600">
                {groupName}
              </Typography>
              <Badge badgeContent={groupKPIs.length} color="primary" />
              <Box sx={{ ml: 'auto', display: 'flex', gap: 1 }}>
                {groupKPIs.map(kpi => (
                  <Chip
                    key={kpi.id}
                    label={kpi.business_priority}
                    color={getPriorityColor(kpi.business_priority)}
                    size="small"
                  />
                ))}
              </Box>
            </Box>
          </AccordionSummary>
          <AccordionDetails sx={{ p: 0 }}>
            <Grid container spacing={2} sx={{ p: 2 }}>
              {groupKPIs.map((kpi) => (
                <Grid item xs={12} sm={6} md={4} lg={3} key={kpi.id}>
                  <Card
                    elevation={2}
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      borderRadius: 2,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: 4
                      }
                    }}
                  >
                    <CardContent sx={{ flexGrow: 1, p: 2.5 }}>
                      {/* KPI Header */}
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Box>
                          <Typography variant="h6" fontWeight="600" sx={{ mb: 0.5 }}>
                            {kpi.name}
                          </Typography>
                          {kpi.alias_name && (
                            <Typography variant="caption" color="text.secondary">
                              {kpi.alias_name}
                            </Typography>
                          )}
                        </Box>
                        <Chip
                          label={kpi.business_priority}
                          color={getPriorityColor(kpi.business_priority)}
                          size="small"
                        />
                      </Box>

                      {/* Description */}
                      {kpi.description && (
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          {kpi.description}
                        </Typography>
                      )}

                      {/* Latest Execution Info */}
                      {kpi.latest_execution ? (
                        <Box sx={{ mb: 2 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            {getExecutionStatusIcon(kpi.latest_execution.status)}
                            <Typography variant="body2" fontWeight="500">
                              Latest Execution
                            </Typography>
                            <Chip
                              label={kpi.latest_execution.status}
                              color={getStatusColor(kpi.latest_execution.status)}
                              size="small"
                            />
                          </Box>
                          
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                            {new Date(kpi.latest_execution.timestamp).toLocaleString()}
                          </Typography>
                          
                          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                            <Chip
                              icon={<SpeedIcon />}
                              label={formatExecutionTime(kpi.latest_execution.execution_time_ms)}
                              color={getSLAColor(getSLAStatus(kpi.latest_execution.execution_time_ms, kpi.target_sla_seconds))}
                              size="small"
                            />
                            <Chip
                              label={`${kpi.latest_execution.record_count || 0} records`}
                              size="small"
                              variant="outlined"
                            />
                          </Box>

                          {/* SQL Enhancement Indicators */}
                          {kpi.latest_execution.enhanced_sql && (
                            <Box sx={{ mt: 1, display: 'flex', gap: 0.5 }}>
                              {hasOpsPlanner(kpi.latest_execution.enhanced_sql) && (
                                <Chip
                                  label="ops_planner"
                                  color="success"
                                  size="small"
                                  variant="outlined"
                                />
                              )}
                              {involvesHanaMaster(kpi.latest_execution.enhanced_sql) && (
                                <Chip
                                  label="hana_master"
                                  color="info"
                                  size="small"
                                  variant="outlined"
                                />
                              )}
                            </Box>
                          )}
                        </Box>
                      ) : (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="body2" color="text.secondary">
                            No executions yet
                          </Typography>
                        </Box>
                      )}

                      {/* Actions */}
                      <Box sx={{ display: 'flex', gap: 1, mt: 'auto' }}>
                        <Button
                          variant="contained"
                          size="small"
                          startIcon={<PlayArrowIcon />}
                          onClick={() => handleExecuteKPI(kpi)}
                          sx={{
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            '&:hover': {
                              background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
                            }
                          }}
                        >
                          Execute
                        </Button>
                        <Tooltip title="View Results">
                          <IconButton
                            size="small"
                            color="primary"
                            onClick={() => handleViewResults(kpi)}
                            disabled={!kpi.latest_execution}
                          >
                            <HistoryIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </AccordionDetails>
        </Accordion>
      ))}

      {/* Dialogs */}
      <KPIAnalyticsForm
        open={createFormOpen}
        onClose={() => setCreateFormOpen(false)}
        onSuccess={handleCreateSuccess}
      />

      <KPIAnalyticsExecutionDialog
        open={executionDialogOpen}
        kpi={selectedKPI}
        onClose={() => setExecutionDialogOpen(false)}
        onSuccess={handleExecutionSuccess}
      />
    </Container>
  );
};

export default KPIAnalyticsDashboard;
