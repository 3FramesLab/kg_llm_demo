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
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import KPIList from '../components/KPIList';
import KPIForm from '../components/KPIForm';
import KPIExecutionDialog from '../components/KPIExecutionDialog';
import KPIExecutionHistory from '../components/KPIExecutionHistory';
import KPIDrilldown from '../components/KPIDrilldown';

const LandingKPIManagement = () => {
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
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
          KPI Management
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Create, manage, and execute Key Performance Indicators using natural language definitions
        </Typography>
      </Box>

      {/* Success Message */}
      {successMessage && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccessMessage('')}>
          {successMessage}
        </Alert>
      )}

      {/* Main Content */}
      <Paper sx={{ p: 3 }}>
        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab label="KPI Definitions" />
            <Tab label="About" />
          </Tabs>
        </Box>

        {/* Tab Content */}
        {activeTab === 0 && (
          <Box>
            {/* Create Button */}
            <Box sx={{ mb: 3 }}>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleCreateKPI}
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
        )}

        {activeTab === 1 && (
          <Box sx={{ py: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              About KPI Management
            </Typography>
            <Typography variant="body2" paragraph>
              The Landing KPI Management system allows you to:
            </Typography>
            <ul>
              <li>
                <Typography variant="body2">
                  <strong>Create KPIs</strong> - Define Key Performance Indicators using natural language
                </Typography>
              </li>
              <li>
                <Typography variant="body2">
                  <strong>Execute KPIs</strong> - Run KPI queries against your Knowledge Graphs
                </Typography>
              </li>
              <li>
                <Typography variant="body2">
                  <strong>Track History</strong> - View execution history and results
                </Typography>
              </li>
              <li>
                <Typography variant="body2">
                  <strong>Drill-down</strong> - Explore detailed results with pagination
                </Typography>
              </li>
            </ul>
            <Typography variant="body2" sx={{ mt: 3, color: 'textSecondary' }}>
              <strong>Getting Started:</strong> Click "Create New KPI" to define your first KPI using a natural language query.
            </Typography>
          </Box>
        )}
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

