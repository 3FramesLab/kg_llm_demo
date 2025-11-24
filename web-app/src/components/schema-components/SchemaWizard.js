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
import { saveSchemaConfiguration } from '../../services/api';

const steps = [
  { label: 'Sources & Entities' },
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
    hasSelectedColumns: false,
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
      hasSelectedColumns: false,
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
          const primaryAlias = wizardData.primaryAliases?.[tableKey] || null;

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
            primaryAlias: primaryAlias,
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
      const errorDetail = error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        'Failed to save schema configuration';
      // Ensure error message is a string
      const errorMessage = typeof errorDetail === 'string' ? errorDetail : JSON.stringify(errorDetail);
      showSnackbar(errorMessage, 'error');
    } finally {
      setSaving(false);
    }
  };

  const isStepValid = (step) => {
    switch (step) {
      case 0:
        // For DatabaseConnectionsStep, require at least one table to be selected
        return selectedTables.length > 0;
      case 1:
        // For Aliases step, require at least one column to be selected
        return selectedTables.length > 0 && wizardData.hasSelectedColumns;
      case 2:
        // For ColumnPreviewStep, require a valid schema name
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
            selectedSchemaTables={selectedTables}
            setSelectedSchemaTables={setSelectedTables}
            onTableDataChange={(data) => setWizardData({ ...wizardData, selectedTables: data })}
          />
        );
      case 1:
        return (
          <AliasesStep
            selectedTables={selectedTables}
            onDataChange={(data) => setWizardData({
              ...wizardData,
              aliases: data.aliases,
              selectedColumns: data.selectedColumns,
              columnAliases: data.columnAliases,
              primaryAliases: data.primaryAliases,
              hasSelectedColumns: data.hasSelectedColumns
            })}
          />
        );
      case 2:
        return (
          <ColumnPreviewStep
            selectedTables={selectedTables}
            selectedColumns={wizardData.selectedColumns}
            tableAliases={wizardData.aliases}
            columnAliases={wizardData.columnAliases}
            primaryAliases={wizardData.primaryAliases}
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
        height: 'calc(100vh - 64px)',
        p: 2,
        bgcolor: '#FFFFFF',
        border: '1px solid #E5E7EB',
        borderRadius: 4,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      {/* Header Section - Fixed */}
      <Box sx={{ mb: 1.5, flexShrink: 0 }}>
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
      <Divider sx={{ mb: 3, flexShrink: 0 }} />

      {/* Stepper - Fixed */}
      <Stepper
        activeStep={activeStep}
        sx={{
          mb: 2,
          flexShrink: 0,
          '& .MuiStepLabel-label': { fontSize: '0.875rem' }
        }}
      >
        {steps.map((stepperItem) => (
          <Step key={stepperItem.label}>
            <StepLabel>{stepperItem.label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {/* Content Area - Scrollable */}
      <Box
        sx={{
          flex: 1,
          bgcolor: '#F9FAFB',
          p: 1.5,
          borderRadius: 1,
          overflow: 'auto',
          minHeight: 0,
        }}
      >
        {getStepContent(activeStep)}
      </Box>

      {/* Action Buttons - Fixed at Bottom */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          mt: 1.5,
          pt: 1.5,
          flexShrink: 0,
          borderTop: '1px solid #E5E7EB',
          bgcolor: '#FFFFFF',
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

