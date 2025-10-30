import React, { useState } from 'react';
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
} from '@mui/material';
import {
  Add as AddIcon,
  Assessment as AssessmentIcon,
  PlayArrow as PlayArrowIcon,
  History as HistoryIcon,
  TrendingUp as TrendingUpIcon,
  Description as DescriptionIcon,
} from '@mui/icons-material';
import KPIList from '../components/KPIList';
import KPIForm from '../components/KPIForm';
import KPIExecutionDialog from '../components/KPIExecutionDialog';
import KPIExecutionHistory from '../components/KPIExecutionHistory';
import KPIDrilldown from '../components/KPIDrilldown';

const LandingKPIManagement = () => {
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

  const handleFormSuccess = () => {
    setSuccessMessage(selectedKPI ? 'KPI updated successfully!' : 'KPI created successfully!');
    setRefreshTrigger((prev) => prev + 1);
    setTimeout(() => setSuccessMessage(''), 3000);
  };

  const handleExecutionSuccess = () => {
    setSuccessMessage('KPI execution started successfully!');
    setRefreshTrigger((prev) => prev + 1);
    setTimeout(() => setSuccessMessage(''), 3000);
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Container maxWidth="xl" sx={{ py: 1.5  }}>
      {/* Enhanced Header with Gradient Background */}
      <Box
        sx={{
          mb: 2.5,
          p: { xs: 2, sm: 2.5, md: 3 },
          borderRadius: 3,
          background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
          color: 'white',
          boxShadow: '0 8px 32px rgba(25, 118, 210, 0.25)',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            right: 0,
            width: '200px',
            height: '200px',
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '50%',
            transform: 'translate(50%, -50%)',
          },
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.75, position: 'relative', zIndex: 1 }}>
          <AssessmentIcon sx={{ fontSize: { xs: 24, sm: 28 }, mr: 2 }} />
          <Typography
            variant="h5"
            fontWeight="700"
            sx={{
              mb: 0.25,
              lineHeight: 1.2,
              fontSize: '1.15rem'
            }}
          >
            Landing KPI Management
          </Typography>
        </Box>
        <Typography
          variant="body2"
          fontSize="0.8rem"
          sx={{
            opacity: 0.95,
            fontWeight: 400,
            maxWidth: '800px',
            position: 'relative',
            zIndex: 1,
          }}
        >
          Create, manage, and execute Key Performance Indicators using natural language definitions
        </Typography>
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
                </Box>

                {/* KPI List */}
                <KPIList
                  onEdit={handleEditKPI}
                  onExecute={handleExecuteKPI}
                  onViewHistory={handleViewHistory}
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
                    <AssessmentIcon sx={{ mr: 1, fontSize: 22 }} />
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
    </Container>
  );
};

export default LandingKPIManagement;

