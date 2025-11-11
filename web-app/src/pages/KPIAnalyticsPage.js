/**
 * KPI Analytics Page - Main page for separate KPI database
 * Integrates the new KPI Analytics Dashboard with enhanced features
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Alert,
  Snackbar,
  Fade,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Chip
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon,
  Code as CodeIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import KPIAnalyticsDashboard from '../components/KPIAnalyticsDashboard';
import { checkKPIAnalyticsHealth } from '../services/kpiAnalyticsApi';

const KPIAnalyticsPage = () => {
  const [healthStatus, setHealthStatus] = useState(null);
  const [healthError, setHealthError] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const response = await checkKPIAnalyticsHealth();
      setHealthStatus(response.data);
      setHealthError(null);
    } catch (err) {
      setHealthError(err.response?.data?.error || 'Health check failed');
      setHealthStatus(null);
    }
  };

  const showNotification = (message, severity = 'info') => {
    setNotification({ open: true, message, severity });
  };

  const handleCloseNotification = () => {
    setNotification({ ...notification, open: false });
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'grey.50' }}>
      <Container maxWidth="xl" sx={{ py: 3 }}>
        {/* Health Status Banner */}
        {healthStatus && (
          <Fade in={true}>
            <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%)' }}>
              <CardContent sx={{ py: 2 }}>
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} md={8}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <StorageIcon color="success" />
                      <Box>
                        <Typography variant="h6" color="success.main" fontWeight="600">
                          KPI Analytics Database Connected
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Database: {healthStatus.database} • Host: {healthStatus.host} • KPIs: {healthStatus.kpi_count}
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: { xs: 'flex-start', md: 'flex-end' } }}>
                      <Chip
                        icon={<StorageIcon />}
                        label="Separate DB"
                        color="success"
                        size="small"
                      />
                      <Chip
                        icon={<CodeIcon />}
                        label="SQL Enhanced"
                        color="info"
                        size="small"
                      />
                      <Chip
                        icon={<SpeedIcon />}
                        label="Analytics Ready"
                        color="primary"
                        size="small"
                      />
                      <Button
                        size="small"
                        startIcon={<RefreshIcon />}
                        onClick={checkHealth}
                        sx={{ ml: 1 }}
                      >
                        Refresh
                      </Button>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Fade>
        )}

        {/* Health Error Banner */}
        {healthError && (
          <Alert 
            severity="error" 
            sx={{ mb: 3 }}
            action={
              <Button color="inherit" size="small" onClick={checkHealth}>
                Retry
              </Button>
            }
          >
            <Typography variant="subtitle2" fontWeight="600">
              KPI Analytics Database Connection Failed
            </Typography>
            <Typography variant="body2">
              {healthError}
            </Typography>
          </Alert>
        )}

        {/* Main Dashboard */}
        <KPIAnalyticsDashboard 
          onNotification={showNotification}
          healthStatus={healthStatus}
        />

        {/* Feature Information */}
        <Card sx={{ mt: 4, background: 'linear-gradient(135deg, #f8f9ff 0%, #e8f0ff 100%)' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <AnalyticsIcon color="primary" />
              Enhanced KPI Analytics Features
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5 }}>
                  <StorageIcon color="primary" sx={{ mt: 0.5 }} />
                  <Box>
                    <Typography variant="subtitle2" fontWeight="600">
                      Separate Analytics Database
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Dedicated KPI_Analytics database for optimal performance and isolation from operational data.
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5 }}>
                  <CodeIcon color="primary" sx={{ mt: 0.5 }} />
                  <Box>
                    <Typography variant="subtitle2" fontWeight="600">
                      Enhanced SQL Generation
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Automatic ops_planner column inclusion and always-visible generated SQL for transparency.
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5 }}>
                  <SpeedIcon color="primary" sx={{ mt: 0.5 }} />
                  <Box>
                    <Typography variant="subtitle2" fontWeight="600">
                      Performance Analytics
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      SLA tracking, execution time monitoring, and business priority management.
                    </Typography>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Notification Snackbar */}
        <Snackbar
          open={notification.open}
          autoHideDuration={6000}
          onClose={handleCloseNotification}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert 
            onClose={handleCloseNotification} 
            severity={notification.severity}
            sx={{ width: '100%' }}
          >
            {notification.message}
          </Alert>
        </Snackbar>
      </Container>
    </Box>
  );
};

export default KPIAnalyticsPage;
