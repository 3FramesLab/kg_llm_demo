import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  TextField,
  Button,
  CircularProgress,
  Alert,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab,
} from '@mui/material';
import { PlayArrow, ExpandMore } from '@mui/icons-material';
import { executeReconciliation, listRulesets } from '../services/api';

export default function Execution() {
  const [tabValue, setTabValue] = useState(0);
  const [rulesets, setRulesets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Form state for SQL export mode
  const [sqlFormData, setSqlFormData] = useState({
    ruleset_id: '',
    limit: 1000,
  });

  // Form state for direct execution mode
  const [execFormData, setExecFormData] = useState({
    ruleset_id: '',
    limit: 1000,
    source_db_config: {
      db_type: 'oracle',
      host: 'localhost',
      port: 1521,
      database: 'ORCL',
      username: '',
      password: '',
      service_name: '',
    },
    target_db_config: {
      db_type: 'oracle',
      host: 'localhost',
      port: 1521,
      database: 'ORCL',
      username: '',
      password: '',
      service_name: '',
    },
  });

  const [results, setResults] = useState(null);

  useEffect(() => {
    loadRulesets();
  }, []);

  const loadRulesets = async () => {
    try {
      const response = await listRulesets();
      setRulesets(response.data.rulesets || []);
    } catch (err) {
      console.error('Error loading rulesets:', err);
    }
  };

  const handleSQLExport = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await executeReconciliation({
        ...sqlFormData,
        export_sql: true,
      });
      setResults(response.data);
      setSuccess('SQL queries generated successfully!');
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDirectExecution = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await executeReconciliation(execFormData);
      setResults(response.data);
      setSuccess(
        `Reconciliation executed successfully! Total matched: ${response.data.summary?.total_matched || 0}`
      );
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Reconciliation Execution
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Execute reconciliation rules and view results
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)} sx={{ mb: 3 }}>
        <Tab label="SQL Export Mode" />
        <Tab label="Direct Execution Mode" />
        <Tab label="Results" />
      </Tabs>

      {/* Tab 1: SQL Export Mode */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                SQL Export Mode
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Generate SQL queries for manual execution (no database connection required)
              </Typography>

              <TextField
                fullWidth
                select
                label="Ruleset"
                value={sqlFormData.ruleset_id}
                onChange={(e) => setSqlFormData({ ...sqlFormData, ruleset_id: e.target.value })}
                margin="normal"
                SelectProps={{
                  native: true,
                }}
                required
              >
                <option value="">Select a ruleset</option>
                {rulesets.map((ruleset) => (
                  <option key={ruleset.ruleset_id} value={ruleset.ruleset_id}>
                    {ruleset.ruleset_id} ({ruleset.rule_count} rules)
                  </option>
                ))}
              </TextField>

              <TextField
                fullWidth
                type="number"
                label="Limit (max records per query)"
                value={sqlFormData.limit}
                onChange={(e) => setSqlFormData({ ...sqlFormData, limit: parseInt(e.target.value) })}
                margin="normal"
              />

              <Box sx={{ mt: 3 }}>
                <Button
                  variant="contained"
                  startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
                  onClick={handleSQLExport}
                  disabled={loading || !sqlFormData.ruleset_id}
                  fullWidth
                >
                  Generate SQL Queries
                </Button>
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Request Placeholder
              </Typography>
              <Box
                component="pre"
                sx={{
                  p: 2,
                  bgcolor: 'grey.100',
                  borderRadius: 1,
                  overflow: 'auto',
                  fontSize: '0.875rem',
                }}
              >
                {JSON.stringify(
                  {
                    ruleset_id: sqlFormData.ruleset_id || 'RECON_ABC12345',
                    limit: sqlFormData.limit,
                    export_sql: true,
                  },
                  null,
                  2
                )}
              </Box>

              <Divider sx={{ my: 2 }} />

              <Typography variant="h6" gutterBottom>
                Response Placeholder
              </Typography>
              <Box
                component="pre"
                sx={{
                  p: 2,
                  bgcolor: 'grey.100',
                  borderRadius: 1,
                  overflow: 'auto',
                  fontSize: '0.875rem',
                  maxHeight: 300,
                }}
              >
                {JSON.stringify(
                  {
                    mode: 'sql_export',
                    ruleset_id: 'RECON_ABC12345',
                    sql_queries: {
                      RULE_001: {
                        matched_query: 'SELECT s.product_id, t.item_id FROM ...',
                        unmatched_source_query: 'SELECT s.product_id FROM ...',
                        unmatched_target_query: 'SELECT t.item_id FROM ...',
                      },
                    },
                    instructions: 'Execute these SQL queries manually in your database client',
                  },
                  null,
                  2
                )}
              </Box>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Tab 2: Direct Execution Mode */}
      {tabValue === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Direct Execution Mode
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Execute rules directly against databases (requires database credentials)
              </Typography>

              <TextField
                fullWidth
                select
                label="Ruleset"
                value={execFormData.ruleset_id}
                onChange={(e) => setExecFormData({ ...execFormData, ruleset_id: e.target.value })}
                margin="normal"
                SelectProps={{
                  native: true,
                }}
                required
              >
                <option value="">Select a ruleset</option>
                {rulesets.map((ruleset) => (
                  <option key={ruleset.ruleset_id} value={ruleset.ruleset_id}>
                    {ruleset.ruleset_id} ({ruleset.rule_count} rules)
                  </option>
                ))}
              </TextField>

              <TextField
                fullWidth
                type="number"
                label="Limit"
                value={execFormData.limit}
                onChange={(e) => setExecFormData({ ...execFormData, limit: parseInt(e.target.value) })}
                margin="normal"
              />

              <Accordion sx={{ mt: 2 }}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography>Source Database Configuration</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <TextField
                    fullWidth
                    label="Host"
                    value={execFormData.source_db_config.host}
                    onChange={(e) =>
                      setExecFormData({
                        ...execFormData,
                        source_db_config: { ...execFormData.source_db_config, host: e.target.value },
                      })
                    }
                    margin="dense"
                  />
                  <TextField
                    fullWidth
                    type="number"
                    label="Port"
                    value={execFormData.source_db_config.port}
                    onChange={(e) =>
                      setExecFormData({
                        ...execFormData,
                        source_db_config: { ...execFormData.source_db_config, port: parseInt(e.target.value) },
                      })
                    }
                    margin="dense"
                  />
                  <TextField
                    fullWidth
                    label="Database"
                    value={execFormData.source_db_config.database}
                    onChange={(e) =>
                      setExecFormData({
                        ...execFormData,
                        source_db_config: { ...execFormData.source_db_config, database: e.target.value },
                      })
                    }
                    margin="dense"
                  />
                  <TextField
                    fullWidth
                    label="Username"
                    value={execFormData.source_db_config.username}
                    onChange={(e) =>
                      setExecFormData({
                        ...execFormData,
                        source_db_config: { ...execFormData.source_db_config, username: e.target.value },
                      })
                    }
                    margin="dense"
                  />
                  <TextField
                    fullWidth
                    type="password"
                    label="Password"
                    value={execFormData.source_db_config.password}
                    onChange={(e) =>
                      setExecFormData({
                        ...execFormData,
                        source_db_config: { ...execFormData.source_db_config, password: e.target.value },
                      })
                    }
                    margin="dense"
                  />
                </AccordionDetails>
              </Accordion>

              <Accordion sx={{ mt: 1 }}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography>Target Database Configuration</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <TextField
                    fullWidth
                    label="Host"
                    value={execFormData.target_db_config.host}
                    onChange={(e) =>
                      setExecFormData({
                        ...execFormData,
                        target_db_config: { ...execFormData.target_db_config, host: e.target.value },
                      })
                    }
                    margin="dense"
                  />
                  <TextField
                    fullWidth
                    type="number"
                    label="Port"
                    value={execFormData.target_db_config.port}
                    onChange={(e) =>
                      setExecFormData({
                        ...execFormData,
                        target_db_config: { ...execFormData.target_db_config, port: parseInt(e.target.value) },
                      })
                    }
                    margin="dense"
                  />
                  <TextField
                    fullWidth
                    label="Database"
                    value={execFormData.target_db_config.database}
                    onChange={(e) =>
                      setExecFormData({
                        ...execFormData,
                        target_db_config: { ...execFormData.target_db_config, database: e.target.value },
                      })
                    }
                    margin="dense"
                  />
                  <TextField
                    fullWidth
                    label="Username"
                    value={execFormData.target_db_config.username}
                    onChange={(e) =>
                      setExecFormData({
                        ...execFormData,
                        target_db_config: { ...execFormData.target_db_config, username: e.target.value },
                      })
                    }
                    margin="dense"
                  />
                  <TextField
                    fullWidth
                    type="password"
                    label="Password"
                    value={execFormData.target_db_config.password}
                    onChange={(e) =>
                      setExecFormData({
                        ...execFormData,
                        target_db_config: { ...execFormData.target_db_config, password: e.target.value },
                      })
                    }
                    margin="dense"
                  />
                </AccordionDetails>
              </Accordion>

              <Box sx={{ mt: 3 }}>
                <Button
                  variant="contained"
                  startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
                  onClick={handleDirectExecution}
                  disabled={loading || !execFormData.ruleset_id}
                  fullWidth
                >
                  Execute Reconciliation
                </Button>
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Response Placeholder
              </Typography>
              <Box
                component="pre"
                sx={{
                  p: 2,
                  bgcolor: 'grey.100',
                  borderRadius: 1,
                  overflow: 'auto',
                  fontSize: '0.875rem',
                  maxHeight: 600,
                }}
              >
                {JSON.stringify(
                  {
                    mode: 'direct_execution',
                    ruleset_id: 'RECON_ABC12345',
                    execution_time: '2024-10-22T10:45:00Z',
                    results: {
                      RULE_001: {
                        matched_count: 1247,
                        unmatched_source_count: 53,
                        unmatched_target_count: 28,
                        matched_records: [
                          { source_product_id: 'P001', target_item_id: 'P001' },
                          { source_product_id: 'P002', target_item_id: 'P002' },
                        ],
                      },
                    },
                    summary: {
                      total_rules_executed: 12,
                      total_matched: 8934,
                      total_unmatched_source: 412,
                      total_unmatched_target: 287,
                      overall_match_rate: 0.78,
                    },
                  },
                  null,
                  2
                )}
              </Box>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Tab 3: Results */}
      {tabValue === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            {results ? (
              <>
                <Paper sx={{ p: 3, mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Execution Results
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <Chip label={`Mode: ${results.mode}`} />
                    {results.summary && (
                      <>
                        <Chip label={`Matched: ${results.summary.total_matched}`} color="success" />
                        <Chip
                          label={`Unmatched Source: ${results.summary.total_unmatched_source}`}
                          color="warning"
                        />
                        <Chip
                          label={`Unmatched Target: ${results.summary.total_unmatched_target}`}
                          color="warning"
                        />
                        <Chip
                          label={`Match Rate: ${(results.summary.overall_match_rate * 100).toFixed(1)}%`}
                          color="info"
                        />
                      </>
                    )}
                  </Box>
                </Paper>

                {results.mode === 'sql_export' && results.sql_queries && (
                  <Paper sx={{ p: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      Generated SQL Queries
                    </Typography>
                    {Object.entries(results.sql_queries).map(([ruleId, queries]) => (
                      <Accordion key={ruleId}>
                        <AccordionSummary expandIcon={<ExpandMore />}>
                          <Typography>{ruleId}</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Box component="pre" sx={{ overflow: 'auto', fontSize: '0.875rem' }}>
                            {typeof queries === 'object'
                              ? JSON.stringify(queries, null, 2)
                              : queries}
                          </Box>
                        </AccordionDetails>
                      </Accordion>
                    ))}
                  </Paper>
                )}

                {results.mode === 'direct_execution' && results.results && (
                  <TableContainer component={Paper}>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Rule ID</TableCell>
                          <TableCell align="right">Matched</TableCell>
                          <TableCell align="right">Unmatched Source</TableCell>
                          <TableCell align="right">Unmatched Target</TableCell>
                          <TableCell align="right">Match Rate</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {Object.entries(results.results).map(([ruleId, ruleResult]) => {
                          const total =
                            (ruleResult.matched_count || 0) +
                            (ruleResult.unmatched_source_count || 0) +
                            (ruleResult.unmatched_target_count || 0);
                          const matchRate =
                            total > 0 ? (ruleResult.matched_count / total) * 100 : 0;

                          return (
                            <TableRow key={ruleId}>
                              <TableCell>{ruleId}</TableCell>
                              <TableCell align="right">
                                <Chip
                                  label={ruleResult.matched_count}
                                  color="success"
                                  size="small"
                                />
                              </TableCell>
                              <TableCell align="right">
                                {ruleResult.unmatched_source_count}
                              </TableCell>
                              <TableCell align="right">
                                {ruleResult.unmatched_target_count}
                              </TableCell>
                              <TableCell align="right">
                                <Chip
                                  label={`${matchRate.toFixed(1)}%`}
                                  color={matchRate >= 80 ? 'success' : 'warning'}
                                  size="small"
                                />
                              </TableCell>
                            </TableRow>
                          );
                        })}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </>
            ) : (
              <Alert severity="info">
                No results yet. Execute a reconciliation from the other tabs to see results here.
              </Alert>
            )}
          </Grid>
        </Grid>
      )}
    </Container>
  );
}
