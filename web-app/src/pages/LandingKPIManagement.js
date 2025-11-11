import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Button,
  Typography,
  Paper,
  Tabs,
  Tab,
  Alert,
  Card,
  CardContent,
  Grid,
  Fade,
  Slide,
  useTheme,
  useMediaQuery,
  Divider,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Add as AddIcon,
  PlayArrow as PlayArrowIcon,
  History as HistoryIcon,
  TrendingUp as TrendingUpIcon,
  Description as DescriptionIcon,
  Refresh as RefreshIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import KPIList from '../components/KPIList';
import KPIForm from '../components/KPIForm';
import KPIExecutionDialog from '../components/KPIExecutionDialog';
import KPIExecutionHistory from '../components/KPIExecutionHistory';
import KPIDrilldown from '../components/KPIDrilldown';
import ScheduleManagement from '../components/ScheduleManagement';
import ScheduleMonitoringDashboard from '../components/ScheduleMonitoringDashboard';

const LandingKPIManagement = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));

  const [formOpen, setFormOpen] = useState(false);
  const [selectedKPI, setSelectedKPI] = useState(null);
  const [executionDialogOpen, setExecutionDialogOpen] = useState(false);
  const [historyDialogOpen, setHistoryDialogOpen] = useState(false);
  const [drilldownDialogOpen, setDrilldownDialogOpen] = useState(false);
  const [selectedExecution, setSelectedExecution] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [successMessage, setSuccessMessage] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [scheduleDialogOpen, setScheduleDialogOpen] = useState(false);
  const [monitoringDialogOpen, setMonitoringDialogOpen] = useState(false);

  const handleCreateKPI = () => {
    setSelectedKPI(null);
    setFormOpen(true);
  };

  const handleEditKPI = (kpi) => {
    setSelectedKPI(kpi);
    setFormOpen(true);
  };

  const handleExecuteKPI = (kpi) => {
    setSelectedKPI(kpi);
    setExecutionDialogOpen(true);
  };

  const handleViewHistory = (kpi) => {
    setSelectedKPI(kpi);
    setHistoryDialogOpen(true);
  };

  const handleViewDrilldown = (execution) => {
    setSelectedExecution(execution);
    setDrilldownDialogOpen(true);
  };

  const handleManageSchedule = (kpi) => {
    setSelectedKPI(kpi);
    setScheduleDialogOpen(true);
  };

  const handleFormSuccess = () => {
    setSuccessMessage(selectedKPI ? 'KPI updated successfully!' : 'KPI created successfully!');
    setRefreshTrigger((prev) => prev + 1);
    setTimeout(() => setSuccessMessage(''), 3000);
  };

  const handleExecutionSuccess = () => {
    console.log('KPI execution completed successfully');
    console.log('Selected KPI for navigation:', selectedKPI);

    setSuccessMessage('KPI execution completed successfully!');
    setRefreshTrigger((prev) => prev + 1);

    // Navigate to execution history page after successful execution
    if (selectedKPI) {
      console.log('Navigating to execution history for KPI:', selectedKPI.id);
      const historyPath = `/landing-kpi/${selectedKPI.id}/history`;
      console.log('Navigation path:', historyPath);

      // Small delay to show success message briefly, then navigate
      setTimeout(() => {
        navigate(historyPath);
      }, 1500);
    } else {
      console.warn('No selectedKPI available for navigation');
      setTimeout(() => setSuccessMessage(''), 3000);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleRefresh = () => {
    setRefreshTrigger((prev) => prev + 1);
    setSuccessMessage('Data refreshed successfully!');
    setTimeout(() => setSuccessMessage(''), 2000);
  };

  return (
    <Container sx={{ p: 0 }}>
      {/* Refresh Button */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1.5 }}>
        <Tooltip title="Refresh data">
          <IconButton
            onClick={handleRefresh}
            sx={{
              bgcolor: 'white',
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 1.5,
              '&:hover': {
                bgcolor: '#f3f4f6',
                borderColor: '#667eea',
              },
            }}
            aria-label="refresh"
          >
            <RefreshIcon
              sx={{
                fontSize: 20,
                color: '#667eea',
              }}
            />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Animated Success Message */}
      <Slide direction="down" in={!!successMessage} mountOnEnter unmountOnExit>
        <Box sx={{ mb: 1.5 }}>
          <Alert
            severity="success"
            onClose={() => setSuccessMessage('')}
            sx={{
              borderRadius: 2,
              boxShadow: '0 4px 12px rgba(46, 125, 50, 0.15)',
              '& .MuiAlert-icon': {
                fontSize: 28,
              },
            }}
          >
            {successMessage}
          </Alert>
        </Box>
      </Slide>

      {/* Main Content with Enhanced Styling */}
      <Paper
        elevation={0}
        sx={{
          borderRadius: 3,
          overflow: 'hidden',
          border: '1px solid',
          borderColor: 'divider',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
        }}
      >
        {/* Enhanced Tabs */}
        <Box
          sx={{
            borderBottom: 1,
            borderColor: 'divider',
            bgcolor: 'grey.50',
            px: { xs: 1.5, sm: 2 },
          }}
        >
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            sx={{
              minHeight: 42,
              '& .MuiTab-root': {
                fontSize: '0.85rem',
                fontWeight: 600,
                textTransform: 'none',
                minHeight: 42,
                py: 0.75,
                transition: 'all 0.3s ease',
                '&:hover': {
                  color: 'primary.main',
                  bgcolor: 'rgba(25, 118, 210, 0.04)',
                },
                '&.Mui-selected': {
                  color: 'primary.main',
                },
              },
              '& .MuiTabs-indicator': {
                height: 3,
                borderRadius: '3px 3px 0 0',
              },
            }}
          >
            <Tab
              icon={<DescriptionIcon sx={{ fontSize: 20, mb: 0.5 }} />}
              iconPosition="start"
              label="KPI Definitions"
            />
            <Tab
              icon={<TrendingUpIcon sx={{ fontSize: 20, mb: 0.5 }} />}
              iconPosition="start"
              label="About"
            />
          </Tabs>
        </Box>

        {/* Tab Content */}
        <Box sx={{ p: { xs: 1.5, sm: 2, md: 2.5 } }}>
          {activeTab === 0 && (
            <Fade in={activeTab === 0} timeout={500}>
              <Box>
                {/* Create Button with Enhanced Styling */}
                <Box sx={{ mb: 2 }}>
                  <Button
                    variant="contained"
                    size="small"
                    startIcon={<AddIcon />}
                    onClick={handleCreateKPI}
                    sx={{
                      py: 0.9,
                      px: 2,
                      borderRadius: 1,
                      fontSize: '0.85rem',
                      fontWeight: 700,
                      textTransform: 'none',
                      boxShadow: '0 4px 14px rgba(25, 118, 210, 0.3)',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: '0 6px 20px rgba(25, 118, 210, 0.4)',
                      },
                      '&:active': {
                        transform: 'translateY(0)',
                      },
                    }}
                  >
                    Create New KPI
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<ScheduleIcon />}
                    onClick={() => setMonitoringDialogOpen(true)}
                    sx={{ ml: 2 }}
                  >
                    Schedule Monitor
                  </Button>
                </Box>

                {/* KPI List */}
                <KPIList
                  onEdit={handleEditKPI}
                  onExecute={handleExecuteKPI}
                  onViewHistory={handleViewHistory}
                  onManageSchedule={handleManageSchedule}
                  refreshTrigger={refreshTrigger}
                />
              </Box>
            </Fade>
          )}

          {activeTab === 1 && (
            <Fade in={activeTab === 1} timeout={500}>
              <Box>
                <Typography
                  variant="h6"
                  fontWeight="700"
                  fontSize="0.95rem"
                  sx={{
                    mb: 2,
                    color: 'text.primary'
                  }}
                >
                  About Landing KPI Management
                </Typography>

                <Typography variant="body2" fontSize="0.8rem" paragraph sx={{ mb: 2.5, color: 'text.secondary' }}>
                  The Landing KPI Management system provides a comprehensive solution for managing and
                  executing Key Performance Indicators:
                </Typography>

                {/* Feature Cards Grid */}
                <Grid container spacing={{ xs: 1.5, sm: 2 }}>
                  {/* Create KPIs Card */}
                  <Grid item xs={12} sm={6} md={6}>
                    <Card
                      elevation={0}
                      sx={{
                        height: '100%',
                        border: '1px solid',
                        borderColor: 'divider',
                        borderRadius: 2,
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          borderColor: 'primary.main',
                          boxShadow: '0 8px 24px rgba(25, 118, 210, 0.15)',
                          transform: 'translateY(-4px)',
                        },
                      }}
                    >
                      <CardContent sx={{ p: { xs: 2, sm: 2.5 }, '&:last-child': { pb: { xs: 2, sm: 2.5 } } }}>
                        <Box
                          sx={{
                            display: 'flex',
                            alignItems: 'center',
                            mb: 1.5,
                          }}
                        >
                          <Box
                            sx={{
                              p: 1.25,
                              borderRadius: 2,
                              bgcolor: 'primary.main',
                              color: 'white',
                              display: 'flex',
                              mr: 1.5,
                            }}
                          >
                            <AddIcon sx={{ fontSize: 24 }} />
                          </Box>
                          <Typography variant="h6" fontWeight="700" fontSize="0.95rem">
                            Create KPIs
                          </Typography>
                        </Box>
                        <Typography variant="body2" fontSize="0.8rem" color="text.secondary">
                          Define Key Performance Indicators using natural language queries. Our
                          intelligent system translates your requirements into actionable metrics.
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  {/* Execute KPIs Card */}
                  <Grid item xs={12} sm={6} md={6}>
                    <Card
                      elevation={0}
                      sx={{
                        height: '100%',
                        border: '1px solid',
                        borderColor: 'divider',
                        borderRadius: 2,
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          borderColor: 'success.main',
                          boxShadow: '0 8px 24px rgba(46, 125, 50, 0.15)',
                          transform: 'translateY(-4px)',
                        },
                      }}
                    >
                      <CardContent sx={{ p: { xs: 2, sm: 2.5 }, '&:last-child': { pb: { xs: 2, sm: 2.5 } } }}>
                        <Box
                          sx={{
                            display: 'flex',
                            alignItems: 'center',
                            mb: 1.5,
                          }}
                        >
                          <Box
                            sx={{
                              p: 1.25,
                              borderRadius: 2,
                              bgcolor: 'success.main',
                              color: 'white',
                              display: 'flex',
                              mr: 1.5,
                            }}
                          >
                            <PlayArrowIcon sx={{ fontSize: 24 }} />
                          </Box>
                          <Typography variant="h6" fontWeight="700" fontSize="0.95rem">
                            Execute KPIs
                          </Typography>
                        </Box>
                        <Typography variant="body2" fontSize="0.8rem" color="text.secondary">
                          Run KPI queries against your Knowledge Graphs with a single click. Get
                          real-time insights and performance metrics instantly.
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  {/* Track History Card */}
                  <Grid item xs={12} sm={6} md={6}>
                    <Card
                      elevation={0}
                      sx={{
                        height: '100%',
                        border: '1px solid',
                        borderColor: 'divider',
                        borderRadius: 2,
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          borderColor: 'warning.main',
                          boxShadow: '0 8px 24px rgba(237, 108, 2, 0.15)',
                          transform: 'translateY(-4px)',
                        },
                      }}
                    >
                      <CardContent sx={{ p: { xs: 2, sm: 2.5 }, '&:last-child': { pb: { xs: 2, sm: 2.5 } } }}>
                        <Box
                          sx={{
                            display: 'flex',
                            alignItems: 'center',
                            mb: 1.5,
                          }}
                        >
                          <Box
                            sx={{
                              p: 1.25,
                              borderRadius: 2,
                              bgcolor: 'warning.main',
                              color: 'white',
                              display: 'flex',
                              mr: 1.5,
                            }}
                          >
                            <HistoryIcon sx={{ fontSize: 24 }} />
                          </Box>
                          <Typography variant="h6" fontWeight="700" fontSize="0.95rem">
                            Track History
                          </Typography>
                        </Box>
                        <Typography variant="body2" fontSize="0.8rem" color="text.secondary">
                          View comprehensive execution history and results. Monitor trends and track
                          performance over time with detailed analytics.
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  {/* Drill-down Card */}
                  <Grid item xs={12} sm={6} md={6}>
                    <Card
                      elevation={0}
                      sx={{
                        height: '100%',
                        border: '1px solid',
                        borderColor: 'divider',
                        borderRadius: 2,
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          borderColor: 'secondary.main',
                          boxShadow: '0 8px 24px rgba(220, 0, 78, 0.15)',
                          transform: 'translateY(-4px)',
                        },
                      }}
                    >
                      <CardContent sx={{ p: { xs: 2, sm: 2.5 }, '&:last-child': { pb: { xs: 2, sm: 2.5 } } }}>
                        <Box
                          sx={{
                            display: 'flex',
                            alignItems: 'center',
                            mb: 1.5,
                          }}
                        >
                          <Box
                            sx={{
                              p: 1.25,
                              borderRadius: 2,
                              bgcolor: 'secondary.main',
                              color: 'white',
                              display: 'flex',
                              mr: 1.5,
                            }}
                          >
                            <TrendingUpIcon sx={{ fontSize: 24 }} />
                          </Box>
                          <Typography variant="h6" fontWeight="700" fontSize="0.95rem">
                            Drill-down Analysis
                          </Typography>
                        </Box>
                        <Typography variant="body2" fontSize="0.8rem" color="text.secondary">
                          Explore detailed results with advanced pagination and filtering. Deep dive
                          into your data for comprehensive insights.
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                {/* Getting Started Section */}
                <Divider sx={{ my: 2.5 }} />
                <Box
                  sx={{
                    p: { xs: 2, sm: 2.5 },
                    borderRadius: 2,
                    bgcolor: 'primary.50',
                    border: '1px solid',
                    borderColor: 'primary.100',
                  }}
                >
                  <Typography
                    variant="subtitle1"
                    fontSize="0.8rem"
                    sx={{
                      fontWeight: 700,
                      color: 'primary.main',
                      mb: 0.75,
                      display: 'flex',
                      alignItems: 'center'
                    }}
                  >
                    <TrendingUpIcon sx={{ mr: 1, fontSize: 22 }} />
                    Getting Started
                  </Typography>
                  <Typography variant="body2" fontSize="0.8rem" color="text.secondary">
                    Click the <strong>"Create New KPI"</strong> button above to define your first KPI
                    using a natural language query. Our system will guide you through the process of
                    creating powerful, actionable metrics for your organization.
                  </Typography>
                </Box>
              </Box>
            </Fade>
          )}
        </Box>
      </Paper>

      {/* Dialogs */}
      <KPIForm
        open={formOpen}
        kpi={selectedKPI}
        onClose={() => setFormOpen(false)}
        onSuccess={handleFormSuccess}
      />

      <KPIExecutionDialog
        open={executionDialogOpen}
        kpi={selectedKPI}
        onClose={() => setExecutionDialogOpen(false)}
        onSuccess={handleExecutionSuccess}
      />

      <KPIExecutionHistory
        open={historyDialogOpen}
        kpi={selectedKPI}
        onClose={() => setHistoryDialogOpen(false)}
        onViewDrilldown={handleViewDrilldown}
      />

      <KPIDrilldown
        open={drilldownDialogOpen}
        execution={selectedExecution}
        onClose={() => setDrilldownDialogOpen(false)}
      />

      {/* Schedule Management Dialog */}
      <Dialog
        open={scheduleDialogOpen}
        onClose={() => setScheduleDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ScheduleIcon />
          Schedule Management - {selectedKPI?.name || selectedKPI?.alias_name}
        </DialogTitle>
        <DialogContent>
          {selectedKPI && (
            <ScheduleManagement
              kpiId={selectedKPI.id}
              kpiName={selectedKPI.name || selectedKPI.alias_name}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setScheduleDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Schedule Monitoring Dashboard Dialog */}
      <Dialog
        open={monitoringDialogOpen}
        onClose={() => setMonitoringDialogOpen(false)}
        maxWidth="xl"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ScheduleIcon />
          Schedule Monitoring Dashboard
        </DialogTitle>
        <DialogContent>
          <ScheduleMonitoringDashboard />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMonitoringDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default LandingKPIManagement;

