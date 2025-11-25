import React, { useState } from 'react';
import {
  Box,
  Container,
  Fade,
  Paper,
  Tabs,
  Tab,
  Typography,
  Divider,
  useTheme,
  alpha,
} from '@mui/material';
import {
  GridView as GridViewIcon,
  Dashboard as DashboardIcon,
} from '@mui/icons-material';
import GroupsManagement from '../components/GroupsManagement';
import DashboardsManagement from '../components/DashboardsManagement';

/**
 * MasterPage Component
 * Main page for managing groups and dashboards with tab-based navigation
 */
const MasterPage = () => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleRefresh = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 0:
        return <GroupsManagement refreshTrigger={refreshTrigger} onRefresh={handleRefresh} />;
      case 1:
        return <DashboardsManagement refreshTrigger={refreshTrigger} onRefresh={handleRefresh} />;
      default:
        return null;
    }
  };

  return (
    <Box sx={{ p: 1.5 }}>
      <Container maxWidth="auto" disableGutters>
        <Fade in timeout={600}>
          <Box
            sx={{
              position: 'relative',
              '&::before': {
                content: '""',
                position: 'absolute',
                top: -4,
                left: -4,
                right: -4,
                bottom: -4,
                borderRadius: '12px',
                background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.05)} 0%, ${alpha(theme.palette.secondary.main, 0.05)} 100%)`,
                opacity: 0,
                transition: 'opacity 0.3s ease-in-out',
                pointerEvents: 'none',
                zIndex: -1,
              },
              '&:hover::before': {
                opacity: 1,
              },
            }}
          >
            <Paper
              elevation={0}
              sx={{
                height: '100%',
                minHeight: 'calc(100vh - 64px)',
                p: 1.5,
                bgcolor: '#FFFFFF',
                border: '1px solid #E5E7EB',
                borderRadius: 1.5,
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              {/* Header Section - Compact */}
              <Box sx={{ mb: 1 }}>
                <Typography
                  variant="h5"
                  sx={{
                    mb: 0.5,
                    fontWeight: 600,
                    fontSize: '1.25rem',
                    color: '#5B6FE5',
                    lineHeight: 1.3,
                  }}
                >
                  Master Configuration
                </Typography>

                <Typography
                  variant="body2"
                  sx={{
                    color: '#6B7280',
                    fontSize: '0.875rem',
                    lineHeight: 1.5,
                  }}
                >
                  Manage groups and dashboards for your application
                </Typography>
              </Box>
              <Divider sx={{ mb: 1.5 }} />

              {/* Tabs Navigation - Compact */}
              <Tabs
                value={activeTab}
                onChange={handleTabChange}
                sx={{
                  mb: 1,
                  '& .MuiTab-root': {
                    fontSize: '0.875rem',
                    fontWeight: 600,
                    textTransform: 'none',
                    minHeight: 44,
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
                  icon={<GridViewIcon sx={{ fontSize: 20, mb: 0.5 }} />}
                  iconPosition="start"
                  label="Groups Management"
                />
                <Tab
                  icon={<DashboardIcon sx={{ fontSize: 20, mb: 0.5 }} />}
                  iconPosition="start"
                  label="Dashboards Management"
                />
              </Tabs>

              {/* Content Area - Compact Design */}
              <Box
                sx={{
                  flex: 1,
                  bgcolor: '#F9FAFB',
                  p: 1,
                  borderRadius: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  minHeight: 300,
                }}
              >
                <Fade in={activeTab === 0} timeout={500}>
                  <Box sx={{ display: activeTab === 0 ? 'flex' : 'none', flexDirection: 'column', height: '100%' }}>
                    {renderTabContent()}
                  </Box>
                </Fade>
                <Fade in={activeTab === 1} timeout={500}>
                  <Box sx={{ display: activeTab === 1 ? 'flex' : 'none', flexDirection: 'column', height: '100%' }}>
                    {renderTabContent()}
                  </Box>
                </Fade>
              </Box>
            </Paper>
          </Box>
        </Fade>
      </Container>
    </Box>
  );
};

export default MasterPage;

