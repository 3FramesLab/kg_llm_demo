/**
 * KPI Execution History Page - Full page view for KPI execution history
 * Shows execution history for a specific KPI with back navigation
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  Breadcrumbs,
  Link,
  Collapse,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Visibility as VisibilityIcon,
  Home as HomeIcon,
  Assessment as AssessmentIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Error as ErrorIcon,
  Code as CodeIcon,
} from '@mui/icons-material';
import { getKPIExecutions, getKPI } from '../services/api';
import KPIDrilldown from '../components/kpi-management/KPIDrilldown';

const KPIExecutionHistoryPage = () => {
  const { kpiId } = useParams();
  const navigate = useNavigate();
  
  const [kpi, setKpi] = useState(null);
  const [executions, setExecutions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedRows, setExpandedRows] = useState(new Set());
  const [drilldownDialogOpen, setDrilldownDialogOpen] = useState(false);
  const [selectedExecution, setSelectedExecution] = useState(null);

  useEffect(() => {
    if (kpiId) {
      fetchKPIAndExecutions();
    }
  }, [kpiId]);

  const fetchKPIAndExecutions = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch KPI details and execution history in parallel
      const [kpiResponse, executionsResponse] = await Promise.all([
        getKPI(kpiId),
        getKPIExecutions(kpiId)
      ]);
      
      setKpi(kpiResponse.data.data);
      
      // Handle both old format (response.data.executions) and new format (response.data)
      const executionsData = executionsResponse.data.executions || executionsResponse.data.data || executionsResponse.data || [];
      setExecutions(Array.isArray(executionsData) ? executionsData : []);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch KPI execution history');
      console.error('Error fetching KPI execution history:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/landing-kpi');
  };

  const handleViewDrilldown = (execution) => {
    console.log('View drilldown for execution:', execution.id);
    console.log('Execution data:', execution);

    // Open the drilldown dialog to show detailed results
    setSelectedExecution(execution);
    setDrilldownDialogOpen(true);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'failed':
      case 'error':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  const toggleRowExpansion = (executionId) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(executionId)) {
      newExpanded.delete(executionId);
    } else {
      newExpanded.add(executionId);
    }
    setExpandedRows(newExpanded);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatExecutionTime = (ms) => {
    if (!ms) return '-';
    return `${ms.toFixed(2)}ms`;
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress size={60} />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header with Breadcrumbs */}
      <Box sx={{ mb: 4 }}>
        <Breadcrumbs sx={{ mb: 2 }}>
          <Link
            component="button"
            variant="body1"
            onClick={() => navigate('/')}
            sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
          >
            <HomeIcon fontSize="small" />
            Home
          </Link>
          <Link
            component="button"
            variant="body1"
            onClick={() => navigate('/landing-kpi')}
            sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
          >
            <AssessmentIcon fontSize="small" />
            KPI Analytics
          </Link>
          <Typography color="text.primary">
            Execution History
          </Typography>
        </Breadcrumbs>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Button
            variant="outlined"
            startIcon={<ArrowBackIcon />}
            onClick={handleBack}
            sx={{ minWidth: 120 }}
          >
            Back to KPIs
          </Button>
        </Box>

        {kpi && (
          <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h4" fontWeight="600" sx={{ mb: 1 }}>
                {kpi.name}
              </Typography>
              {/* Only show alias_name if it's different from name */}
              {kpi.alias_name && kpi.alias_name !== kpi.name && (
                <Typography variant="h6" sx={{ opacity: 0.9, mb: 1 }}>
                  {kpi.alias_name}
                </Typography>
              )}
              {/* Only show description if it's different from both name and alias_name */}
              {kpi.description &&
               kpi.description !== kpi.name &&
               kpi.description !== kpi.alias_name && (
                <Typography variant="body1" sx={{ opacity: 0.8, mb: 2 }}>
                  {kpi.description}
                </Typography>
              )}
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {kpi.group_name && (
                  <Chip
                    label={`Group: ${kpi.group_name}`}
                    sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                  />
                )}
                <Chip
                  label={`Total Executions: ${executions.length}`}
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                />
              </Box>
            </CardContent>
          </Card>
        )}
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Execution History Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
            Execution History
          </Typography>
          
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold', width: '40px' }}></TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Execution ID</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>KG Name</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Records</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Time</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Confidence</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Timestamp</TableCell>
                  <TableCell sx={{ fontWeight: 'bold', textAlign: 'center' }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {executions.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                      <Typography variant="body1" color="text.secondary">
                        No executions found for this KPI
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        Execute the KPI to see results here
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  executions.map((execution) => (
                    <React.Fragment key={execution.id}>
                      <TableRow hover>
                        <TableCell>
                          <IconButton
                            size="small"
                            onClick={() => toggleRowExpansion(execution.id)}
                            sx={{
                              color: (execution.error_message || execution.generated_sql) ? 'primary.main' : 'text.disabled'
                            }}
                            disabled={!execution.error_message && !execution.generated_sql}
                          >
                            {expandedRows.has(execution.id) ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                          </IconButton>
                        </TableCell>
                        <TableCell>#{execution.id}</TableCell>
                        <TableCell>
                          <Chip
                            label={execution.kg_name || 'N/A'}
                            size="small"
                            variant="outlined"
                            sx={{
                              backgroundColor: '#e3f2fd',
                              color: '#1976d2',
                              fontFamily: 'monospace',
                              fontSize: '0.75rem'
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Chip
                              label={execution.execution_status}
                              size="small"
                              color={getStatusColor(execution.execution_status)}
                              variant="outlined"
                            />
                            {execution.execution_status === 'error' && execution.error_message && (
                              <Tooltip title="Click expand button to view error details">
                                <ErrorIcon color="error" fontSize="small" />
                              </Tooltip>
                            )}
                          </Box>
                        </TableCell>
                        <TableCell>{execution.number_of_records || 0}</TableCell>
                        <TableCell>{formatExecutionTime(execution.execution_time_ms)}</TableCell>
                        <TableCell>
                          {execution.confidence_score
                            ? `${(execution.confidence_score * 100).toFixed(1)}%`
                            : '-'}
                        </TableCell>
                        <TableCell>{formatDate(execution.execution_timestamp)}</TableCell>
                        <TableCell align="center">
                          {execution.execution_status === 'success' && execution.number_of_records > 0 ? (
                            <Tooltip title="View Results">
                              <IconButton
                                size="small"
                                color="primary"
                                onClick={() => handleViewDrilldown(execution)}
                              >
                                <VisibilityIcon />
                              </IconButton>
                            </Tooltip>
                          ) : (
                            <Typography variant="caption" color="text.secondary">
                              No data
                            </Typography>
                          )}
                        </TableCell>
                      </TableRow>

                      {/* Expandable row for error details and SQL */}
                      <TableRow>
                        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={9}>
                          <Collapse in={expandedRows.has(execution.id)} timeout="auto" unmountOnExit>
                            <Box sx={{ margin: 2 }}>
                              {/* Error Message Section */}
                              {execution.error_message && (
                                <Alert severity="error" sx={{ mb: 2 }}>
                                  <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                                    Error Message:
                                  </Typography>
                                  <Typography
                                    variant="body2"
                                    sx={{
                                      fontFamily: 'monospace',
                                      fontSize: '0.85rem',
                                      whiteSpace: 'pre-wrap',
                                      wordBreak: 'break-word'
                                    }}
                                  >
                                    {execution.error_message}
                                  </Typography>
                                </Alert>
                              )}

                              {/* Generated SQL Section */}
                              {execution.generated_sql && (
                                <Box>
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                    <CodeIcon color="primary" fontSize="small" />
                                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                                      Generated SQL Query:
                                    </Typography>
                                  </Box>
                                  <Paper
                                    sx={{
                                      p: 2,
                                      backgroundColor: '#f5f5f5',
                                      fontFamily: 'monospace',
                                      fontSize: '0.85rem',
                                      overflow: 'auto',
                                      maxHeight: '300px',
                                      border: '1px solid #e0e0e0'
                                    }}
                                  >
                                    <Typography
                                      component="pre"
                                      sx={{
                                        m: 0,
                                        whiteSpace: 'pre-wrap',
                                        wordBreak: 'break-word',
                                        fontFamily: 'monospace',
                                      }}
                                    >
                                      {execution.generated_sql}
                                    </Typography>
                                  </Paper>
                                </Box>
                              )}

                              {/* Show message if no additional details */}
                              {!execution.error_message && !execution.generated_sql && (
                                <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                                  No additional execution details available.
                                </Typography>
                              )}
                            </Box>
                          </Collapse>
                        </TableCell>
                      </TableRow>
                    </React.Fragment>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Drilldown Dialog */}
      <KPIDrilldown
        open={drilldownDialogOpen}
        execution={selectedExecution}
        onClose={() => setDrilldownDialogOpen(false)}
      />
    </Container>
  );
};

export default KPIExecutionHistoryPage;
