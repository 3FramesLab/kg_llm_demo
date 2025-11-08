/**
 * KPI Analytics Execution Dialog - Enhanced with Always-Visible SQL
 * Shows generated SQL even when there are no records returned
 * Uses the new KPI Analytics API with separate database
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Alert,
  CircularProgress,
  Chip,
  Grid,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Code as CodeIcon,
  Assessment as AssessmentIcon,
  Speed as SpeedIcon,
  Storage as StorageIcon,
  ContentCopy as ContentCopyIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  PlayArrow as PlayArrowIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';
import { 
  executeKPI, 
  formatExecutionTime, 
  getStatusColor, 
  hasOpsPlanner, 
  involvesHanaMaster 
} from '../services/kpiAnalyticsApi';

const KPIAnalyticsExecutionDialog = ({ open, kpi, onClose, onSuccess }) => {
  const [executing, setExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState(null);
  const [error, setError] = useState(null);
  const [sqlCopied, setSqlCopied] = useState(false);
  const [navigating, setNavigating] = useState(false);

  // Reset states when dialog opens
  React.useEffect(() => {
    if (open) {
      setExecuting(false);
      setExecutionResult(null);
      setError(null);
      setSqlCopied(false);
      setNavigating(false);
    }
  }, [open]);

  // Reset state when dialog opens/closes
  useEffect(() => {
    if (open) {
      setExecutionResult(null);
      setError(null);
      setSqlCopied(false);
    }
  }, [open]);

  const handleExecute = async () => {
    if (!kpi) return;

    setExecuting(true);
    setError(null);
    setExecutionResult(null);

    try {
      console.log('Starting KPI execution for:', kpi.id);
      const response = await executeKPI(kpi.id, {
        kg_name: 'KG_102',  // Use proper KG name
        schemas: ['newdqschemanov'],  // Use schemas array as backend expects
        limit: 1000,  // Use 'limit' not 'limit_records'
        use_llm: true,
        db_type: 'sqlserver'
      });

      console.log('KPI execution response:', response);
      console.log('Response data:', response.data);
      console.log('Response success:', response.data?.success);

      if (response.data?.success) {
        setExecutionResult(response.data.data);
      } else {
        console.error('KPI execution failed:', response.data);
        setError(response.data?.error_message || 'KPI execution failed');
        return;
      }

      // Show navigation state and then navigate to execution history
      if (onSuccess) {
        console.log('Success handler available, starting navigation flow');
        // Show success state briefly, then navigate
        setTimeout(() => {
          console.log('Setting navigating state to true');
          setNavigating(true);
          // Navigate immediately after showing navigation state
          setTimeout(() => {
            console.log('Calling success handler with KPI data');
            // Pass the KPI data along with execution result for navigation
            onSuccess(response.data.data, kpi);
            // Close dialog after navigation is initiated
            setTimeout(() => {
              console.log('Closing dialog after navigation');
              onClose();
            }, 100);
          }, 800); // Shorter delay to show "Opening execution history..."
        }, 1000); // Wait 1 second to show success state first
      } else {
        console.warn('No onSuccess handler provided');
      }
    } catch (err) {
      console.error('KPI execution error:', err);
      console.error('Error response:', err.response);
      console.error('Error response data:', err.response?.data);

      setError(err.response?.data?.detail || err.response?.data?.error || err.message || 'Execution failed');
      setNavigating(false); // Reset navigating state on error

      // IMPORTANT: Even on error, show the generated SQL if available
      if (err.response?.data?.generated_sql) {
        setExecutionResult({
          execution_status: 'error',
          generated_sql: err.response.data.generated_sql,
          enhanced_sql: err.response.data.enhanced_sql,
          error_message: err.response?.data?.error,
          number_of_records: 0
        });
      }
    } finally {
      setExecuting(false);
    }
  };

  const handleCopySQL = async (sql) => {
    try {
      await navigator.clipboard.writeText(sql);
      setSqlCopied(true);
      setTimeout(() => setSqlCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy SQL:', err);
    }
  };

  const renderSQLSection = (title, sql, isEnhanced = false) => {
    if (!sql) return null;

    return (
      <Accordion defaultExpanded sx={{ mb: 1 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
            <CodeIcon color="primary" />
            <Typography variant="subtitle1" fontWeight="600">{title}</Typography>
            {isEnhanced && (
              <Box sx={{ display: 'flex', gap: 0.5, ml: 'auto' }}>
                {hasOpsPlanner(sql) && (
                  <Chip label="ops_planner" color="success" size="small" />
                )}
                {involvesHanaMaster(sql) && (
                  <Chip label="hana_master" color="info" size="small" />
                )}
              </Box>
            )}
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box sx={{ position: 'relative' }}>
            <Tooltip title={sqlCopied ? "Copied!" : "Copy SQL"}>
              <IconButton 
                onClick={() => handleCopySQL(sql)} 
                size="small"
                sx={{ position: 'absolute', top: 8, right: 8, zIndex: 1 }}
              >
                {sqlCopied ? <CheckCircleIcon color="success" /> : <ContentCopyIcon />}
              </IconButton>
            </Tooltip>
            <Box sx={{
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              bgcolor: 'grey.50',
              p: 2,
              pr: 6, // Space for copy button
              borderRadius: 1,
              border: '1px solid',
              borderColor: 'grey.200',
              maxHeight: 300,
              overflow: 'auto',
              whiteSpace: 'pre-wrap'
            }}>
              {sql}
            </Box>
          </Box>
        </AccordionDetails>
      </Accordion>
    );
  };

  const renderExecutionMetrics = () => {
    if (!executionResult) return null;

    const isSuccess = executionResult.execution_status === 'success';
    const hasRecords = executionResult.number_of_records > 0;

    return (
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AssessmentIcon color="primary" />
            Execution Results
          </Typography>
          
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center', p: 1 }}>
                {isSuccess ? (
                  <CheckCircleIcon fontSize="large" color="success" />
                ) : (
                  <ErrorIcon fontSize="large" color="error" />
                )}
                <Typography variant="caption" display="block" color="text.secondary">Status</Typography>
                <Typography variant="body2" fontWeight="600" textTransform="capitalize">
                  {executionResult.execution_status}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center', p: 1 }}>
                <Typography variant="h4" color={hasRecords ? "primary" : "text.secondary"}>
                  {executionResult.number_of_records || 0}
                </Typography>
                <Typography variant="caption" display="block" color="text.secondary">Records</Typography>
                <Typography variant="body2" fontWeight="600">
                  {hasRecords ? 'Returned' : 'No Data'}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center', p: 1 }}>
                <SpeedIcon fontSize="large" color="info" />
                <Typography variant="caption" display="block" color="text.secondary">Time</Typography>
                <Typography variant="body2" fontWeight="600">
                  {formatExecutionTime(executionResult.execution_time_ms)}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center', p: 1 }}>
                <StorageIcon fontSize="large" color="secondary" />
                <Typography variant="caption" display="block" color="text.secondary">Evidence</Typography>
                <Typography variant="body2" fontWeight="600">
                  {executionResult.evidence_count || 0}
                </Typography>
              </Box>
            </Grid>
          </Grid>

          {/* Status-specific messages */}
          {isSuccess && !hasRecords && (
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="subtitle2" fontWeight="600">Query Executed Successfully - No Records Found</Typography>
              <Typography variant="body2">
                The SQL query ran without errors but returned no matching records. 
                You can see the exact SQL that was executed below.
              </Typography>
            </Alert>
          )}

          {!isSuccess && (
            <Alert severity="error" sx={{ mb: 2 }}>
              <Typography variant="subtitle2" fontWeight="600">Execution Failed</Typography>
              <Typography variant="body2">
                {executionResult.error_message || 'An error occurred during execution.'}
              </Typography>
            </Alert>
          )}

          {isSuccess && hasRecords && (
            <Alert severity="success" sx={{ mb: 2 }}>
              <Typography variant="subtitle2" fontWeight="600">Query Executed Successfully</Typography>
              <Typography variant="body2">
                Found {executionResult.number_of_records} matching records in {formatExecutionTime(executionResult.execution_time_ms)}.
              </Typography>
            </Alert>
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="lg" 
      fullWidth
      PaperProps={{
        sx: { borderRadius: 2, maxHeight: '90vh' }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 1,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white'
      }}>
        <AssessmentIcon />
        Execute KPI: {kpi?.name}
        {kpi?.alias_name && (
          <Chip label={kpi.alias_name} size="small" sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }} />
        )}
        <Chip label="Analytics DB" size="small" sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', ml: 'auto' }} />
      </DialogTitle>
      
      <DialogContent sx={{ mt: 2 }}>
        {/* KPI Information */}
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>KPI Definition</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              {kpi?.description}
            </Typography>
            <Typography variant="body2" sx={{ 
              fontStyle: 'italic', 
              bgcolor: 'grey.50', 
              p: 1.5, 
              borderRadius: 1,
              border: '1px solid',
              borderColor: 'grey.200'
            }}>
              "{kpi?.nl_definition}"
            </Typography>
          </CardContent>
        </Card>

        {/* Execution Results */}
        {executionResult && (
          <Box>
            {renderExecutionMetrics()}

            {/* ALWAYS Show Generated SQL - Key Feature */}
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <VisibilityIcon color="primary" />
                  <Typography variant="h6">Generated SQL</Typography>
                  <Chip 
                    label="Always Visible" 
                    color="success" 
                    size="small" 
                    variant="outlined"
                  />
                  <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>
                    SQL shown regardless of results
                  </Typography>
                </Box>

                {/* Original SQL */}
                {executionResult.generated_sql && renderSQLSection(
                  "Original Generated SQL", 
                  executionResult.generated_sql, 
                  false
                )}

                {/* Enhanced SQL */}
                {executionResult.enhanced_sql && 
                 executionResult.enhanced_sql !== executionResult.generated_sql && 
                 renderSQLSection(
                  "Enhanced SQL (with ops_planner)", 
                  executionResult.enhanced_sql, 
                  true
                )}
              </CardContent>
            </Card>
          </Box>
        )}

        {/* Execution in Progress */}
        {executing && (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
            <CircularProgress size={60} sx={{ mb: 2 }} />
            <Typography variant="h6" gutterBottom>Executing KPI...</Typography>
            <Typography variant="body2" color="text.secondary" textAlign="center">
              Generating SQL with ops_planner enhancement and executing query
            </Typography>
          </Box>
        )}

        {navigating && (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
            <CircularProgress size={60} sx={{ mb: 2, color: 'success.main' }} />
            <Typography variant="h6" gutterBottom color="success.main">
              Opening Execution History...
            </Typography>
            <Typography variant="body2" color="text.secondary" textAlign="center">
              Redirecting to view detailed results and execution history
            </Typography>
          </Box>
        )}

        {/* Error without execution result */}
        {error && !executionResult && (
          <Alert severity="error" sx={{ mb: 2 }}>
            <Typography variant="subtitle2" fontWeight="600">Execution Error</Typography>
            <Typography variant="body2">{error}</Typography>
          </Alert>
        )}
      </DialogContent>
      
      <DialogActions sx={{ p: 2.5, gap: 1 }}>
        <Button onClick={onClose} disabled={executing}>
          Close
        </Button>
        <Button
          onClick={handleExecute}
          variant="contained"
          disabled={executing || !kpi}
          startIcon={executing ? <CircularProgress size={20} /> : <PlayArrowIcon />}
          sx={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
            }
          }}
        >
          {executing ? 'Executing...' : 'Execute KPI'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default KPIAnalyticsExecutionDialog;
