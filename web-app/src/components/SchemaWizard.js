import { useState } from 'react';
import {
  Box,
  Paper,
  Stepper,
  Step,
  StepLabel,
  Button,
  Typography,
  Divider,
  Snackbar,
  Alert,
  CircularProgress,
} from '@mui/material';
import DatabaseConnectionsStep from './schema-wizard/DatabaseConnectionsStep';
import TableSelectionStep from './schema-wizard/TableSelectionStep';
import AliasesStep from './schema-wizard/AliasesStep';
import ColumnPreviewStep from './schema-wizard/ColumnPreviewStep';
import { saveSchemaConfiguration } from '../services/api';

const steps = [
  { label: 'Sources' },
  { label: 'Entities' },
  { label: 'Aliases' },
  { label: 'Preview' },
];

/**
 * SchemaWizard Component
 * Multi-step wizard for database connection, table selection, and column preview
 */
function SchemaWizard() {
  const [activeStep, setActiveStep] = useState(0);
  const [connections, setConnections] = useState([]);
  const [selectedTables, setSelectedTables] = useState([]);
  const [wizardData, setWizardData] = useState({
    connections: [],
    selectedTables: [],
    aliases: [],
    selectedColumns: {},
    columnAliases: {},
    columns: [],
    schemaName: '',
  });
  const [saving, setSaving] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success',
  });

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    setConnections([]);
    setSelectedTables([]);
    setWizardData({
      connections: [],
      selectedTables: [],
      aliases: [],
      selectedColumns: {},
      columnAliases: {},
      columns: [],
      schemaName: '',
    });
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleFinish = async () => {
    setSaving(true);

    try {
      // Prepare the schema configuration data
      const schemaConfiguration = {
        schemaName: wizardData.schemaName.trim(),
        tables: selectedTables.map(table => {
          const tableKey = table.key;
          const aliasData = wizardData.aliases.find(a => a.key === tableKey);
          const tableColumns = wizardData.selectedColumns[tableKey] || {};
          const tableColumnAliases = wizardData.columnAliases?.[tableKey] || {};

          // Get selected columns with their aliases
          const selectedColumnsWithAliases = Object.entries(tableColumns)
            .filter(([_, isSelected]) => isSelected)
            .map(([columnName]) => ({
              name: columnName,
              aliases: tableColumnAliases[columnName] || [],
            }));

          return {
            connectionId: table.connectionId,
            connectionName: table.connectionName,
            databaseName: table.databaseName,
            tableName: table.tableName,
            tableAliases: aliasData?.aliases || [],
            columns: selectedColumnsWithAliases,
          };
        }),
      };

      console.log('Saving schema configuration:', schemaConfiguration);

      // Call the API to save the configuration
      const response = await saveSchemaConfiguration(schemaConfiguration);

      if (response.data.success) {
        showSnackbar('Schema configuration saved successfully!', 'success');

        // Wait a moment to show the success message, then reset
        setTimeout(() => {
          handleReset();
        }, 2000);
      } else {
        showSnackbar('Failed to save schema configuration', 'error');
      }
    } catch (error) {
      console.error('Error saving schema configuration:', error);
      const errorMessage = error.response?.data?.detail ||
                          error.response?.data?.message ||
                          error.message ||
                          'Failed to save schema configuration';
      showSnackbar(errorMessage, 'error');
    } finally {
      setSaving(false);
    }
  };

  const isStepValid = (step) => {
    switch (step) {
      case 0:
        return connections.length > 0;
      case 1:
        return selectedTables.length > 0;
      case 2:
        return wizardData.aliases && wizardData.aliases.length > 0;
      case 3:
        return wizardData.schemaName && wizardData.schemaName.trim().length > 0;
      default:
        return false;
    }
  };

  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <DatabaseConnectionsStep
            connections={connections}
            setConnections={setConnections}
            onDataChange={(data) => setWizardData({ ...wizardData, connections: data })}
          />
        );
      case 1:
        return (
          <TableSelectionStep
            connections={connections}
            selectedTables={selectedTables}
            setSelectedTables={setSelectedTables}
            onDataChange={(data) => setWizardData({ ...wizardData, selectedTables: data })}
          />
        );
      case 2:
        return (
          <AliasesStep
            selectedTables={selectedTables}
            onDataChange={(data) => setWizardData({
              ...wizardData,
              aliases: data.aliases,
              selectedColumns: data.selectedColumns,
              columnAliases: data.columnAliases
            })}
          />
        );
      case 3:
        return (
          <ColumnPreviewStep
            selectedTables={selectedTables}
            selectedColumns={wizardData.selectedColumns}
            tableAliases={wizardData.aliases}
            columnAliases={wizardData.columnAliases}
            onDataChange={(data) => setWizardData({
              ...wizardData,
              columns: data.columnsData,
              schemaName: data.schemaName,
            })}
          />
        );
      default:
        return 'Unknown step';
    }
  };

  return (
    <Paper
      elevation={0}
      sx={{
        height: '100%',
        minHeight: 'calc(100vh - 64px)',
        p: 2,
        bgcolor: '#FFFFFF',
        border: '1px solid #E5E7EB',
        borderRadius: 4,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Header Section */}
      <Box sx={{ mb: 1.5 }}>
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
          Schemas
        </Typography>

        <Typography
          variant="body2"
          sx={{
            color: '#6B7280',
            fontSize: '0.875rem',
            lineHeight: 1.5,
          }}
        >
          Transform your schemas into powerful knowledge graphs. Connect entities and columns across multiple sources to unlock deeper insights and enable advanced data quality analysis.
        </Typography>
      </Box>
      <Divider sx={{ mb: 3 }} />
      {/* Stepper - Compact and Aligned */}


      <Stepper activeStep={activeStep} sx={{ mb: 2, '& .MuiStepLabel-label': { fontSize: '0.875rem' } }}>
        {steps.map((stepperItem) => (
          <Step key={stepperItem.label}>
            <StepLabel>{stepperItem.label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {/* Content Area - Compact Design */}
      <Box
        sx={{
          flex: 1,
          bgcolor: '#F9FAFB',
          p: 1.5,
          borderRadius: 1,
          display: 'flex',
          flexDirection: 'column',
          minHeight: 300,
        }}
      >
        {getStepContent(activeStep)}
      </Box>

      {/* Action Buttons - Compact Design */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          mt: 1.5,
          pt: 1,
        }}
      >
        <Button
          disabled={activeStep === 0}
          onClick={handleBack}
          variant="outlined"
          size="small"
          sx={{
            px: 1.5,
            py: 0.5,
            minWidth: 'auto',
            color: '#64748B',
            borderColor: '#CBD5E1',
            fontSize: '0.8125rem',
            textTransform: 'none',
            borderRadius: '8px',
            '&:hover': {
              bgcolor: '#F8FAFC',
              borderColor: '#94A3B8',
              color: '#475569',
            },
            '&:disabled': {
              color: '#D1D5DB',
              borderColor: '#E5E7EB',
            },
          }}
        >
          ← Back
        </Button>
        <Button
          onClick={activeStep === steps.length - 1 ? handleFinish : handleNext}
          variant="contained"
          disabled={!isStepValid(activeStep) || saving}
          size="small"
          sx={{
            px: 2,
            py: 0.5,
            minHeight: 'auto',
            bgcolor: '#5B6FE5',
            color: '#FFFFFF',
            fontSize: '0.8125rem',
            fontWeight: 500,
            textTransform: 'none',
            borderRadius: '8px',
            boxShadow: '0 1px 3px 0 rgba(91, 111, 229, 0.2)',
            '&:hover': {
              bgcolor: '#4C5FD5',
              boxShadow: '0 2px 6px 0 rgba(91, 111, 229, 0.3)',
            },
            '&:disabled': {
              bgcolor: '#E5E7EB',
              color: '#9CA3AF',
              boxShadow: 'none',
            },
          }}
        >
          {saving ? (
            <>
              <CircularProgress size={16} sx={{ color: '#FFFFFF', mr: 1 }} />
              Saving...
            </>
          ) : (
            activeStep === steps.length - 1 ? 'Finish' : 'Next →'
          )}
        </Button>
      </Box>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Paper>
  );
}

export default SchemaWizard;

