import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  TextField,
  Button,
  FormControlLabel,
  Checkbox,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Chip,
  Divider,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Slider,
} from '@mui/material';
import { Add, Refresh, Download, Delete, ExpandMore } from '@mui/icons-material';
import {
  generateRules,
  listRulesets,
  getRuleset,
  deleteRuleset,
  exportRulesetSQL,
  listSchemas,
  listKGs,
} from '../services/api';

export default function Reconciliation() {
  const [tabValue, setTabValue] = useState(0);
  const [schemas, setSchemas] = useState([]);
  const [kgs, setKgs] = useState([]);
  const [rulesets, setRulesets] = useState([]);
  const [selectedRuleset, setSelectedRuleset] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    schema_names: [],
    kg_name: '',
    use_llm_enhancement: true,
    min_confidence: 0.7,
  });

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [schemasRes, kgsRes, rulesetsRes] = await Promise.all([
        listSchemas(),
        listKGs(),
        listRulesets(),
      ]);
      setSchemas(schemasRes.data.schemas || []);
      setKgs(kgsRes.data.graphs || []);
      setRulesets(rulesetsRes.data.rulesets || []);
    } catch (err) {
      console.error('Error loading data:', err);
    }
  };

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await generateRules(formData);
      setSuccess(
        `Generated ${response.data.rule_count} rules in ruleset "${response.data.ruleset_id}"`
      );
      loadInitialData();
      setTabValue(1);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadRuleset = async (rulesetId) => {
    setLoading(true);
    try {
      const response = await getRuleset(rulesetId);
      setSelectedRuleset(response.data);
      setTabValue(1);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExportSQL = async (rulesetId) => {
    try {
      const response = await exportRulesetSQL(rulesetId);
      const blob = new Blob([response.data], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${rulesetId}_queries.sql`;
      a.click();
      setSuccess(`SQL queries exported for ruleset "${rulesetId}"`);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    }
  };

  const handleDelete = async (rulesetId) => {
    if (!window.confirm(`Are you sure you want to delete ruleset "${rulesetId}"?`)) {
      return;
    }

    try {
      await deleteRuleset(rulesetId);
      setSuccess(`Ruleset "${rulesetId}" deleted successfully!`);
      loadInitialData();
      if (selectedRuleset?.ruleset_id === rulesetId) {
        setSelectedRuleset(null);
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    }
  };

  const handleSchemaToggle = (schema) => {
    const currentIndex = formData.schema_names.indexOf(schema);
    const newSchemas = [...formData.schema_names];

    if (currentIndex === -1) {
      newSchemas.push(schema);
    } else {
      newSchemas.splice(currentIndex, 1);
    }

    setFormData({ ...formData, schema_names: newSchemas });
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Reconciliation Rule Generation
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Generate data matching rules from knowledge graphs
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
        <Tab label="Generate Rules" />
        <Tab label="View Rules" />
        <Tab label="Manage Rulesets" />
      </Tabs>

      {/* Tab 1: Generate */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Generate Reconciliation Rules
              </Typography>

              <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
                Select Schemas
              </Typography>
              <Paper variant="outlined" sx={{ p: 2, maxHeight: 200, overflow: 'auto', mb: 2 }}>
                {schemas.map((schema) => (
                  <FormControlLabel
                    key={schema}
                    control={
                      <Checkbox
                        checked={formData.schema_names.includes(schema)}
                        onChange={() => handleSchemaToggle(schema)}
                      />
                    }
                    label={schema}
                  />
                ))}
              </Paper>

              <TextField
                fullWidth
                select
                label="Knowledge Graph"
                value={formData.kg_name}
                onChange={(e) => setFormData({ ...formData, kg_name: e.target.value })}
                margin="normal"
                SelectProps={{
                  native: true,
                }}
                required
              >
                <option value="">Select a knowledge graph</option>
                {kgs.map((kg) => (
                  <option key={kg.name} value={kg.name}>
                    {kg.name}
                  </option>
                ))}
              </TextField>

              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.use_llm_enhancement}
                    onChange={(e) =>
                      setFormData({ ...formData, use_llm_enhancement: e.target.checked })
                    }
                  />
                }
                label="Use LLM Enhancement for Semantic Rules"
                sx={{ mt: 2 }}
              />

              <Box sx={{ mt: 3 }}>
                <Typography gutterBottom>
                  Minimum Confidence: {formData.min_confidence}
                </Typography>
                <Slider
                  value={formData.min_confidence}
                  onChange={(e, value) => setFormData({ ...formData, min_confidence: value })}
                  min={0}
                  max={1}
                  step={0.05}
                  marks={[
                    { value: 0, label: '0' },
                    { value: 0.5, label: '0.5' },
                    { value: 1, label: '1' },
                  ]}
                  valueLabelDisplay="auto"
                />
              </Box>

              <Box sx={{ mt: 3 }}>
                <Button
                  variant="contained"
                  startIcon={loading ? <CircularProgress size={20} /> : <Add />}
                  onClick={handleGenerate}
                  disabled={
                    loading || formData.schema_names.length === 0 || !formData.kg_name
                  }
                  fullWidth
                >
                  Generate Rules
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
                    schema_names:
                      formData.schema_names.length > 0
                        ? formData.schema_names
                        : ['orderMgmt-catalog', 'qinspect-designcode'],
                    kg_name: formData.kg_name || 'unified_kg',
                    use_llm_enhancement: formData.use_llm_enhancement,
                    min_confidence: formData.min_confidence,
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
                  maxHeight: 400,
                }}
              >
                {JSON.stringify(
                  {
                    ruleset_id: 'RECON_ABC12345',
                    rule_count: 12,
                    rules: [
                      {
                        rule_id: 'RULE_001',
                        rule_name: 'catalog_product_to_designcode_item',
                        source_schema: 'orderMgmt-catalog',
                        source_table: 'catalog',
                        source_columns: ['product_id'],
                        target_schema: 'qinspect-designcode',
                        target_table: 'designcode',
                        target_columns: ['item_id'],
                        match_type: 'semantic',
                        confidence_score: 0.85,
                        reasoning: 'LLM matched product_id to item_id based on semantic similarity',
                      },
                    ],
                    created_at: '2024-10-22T10:30:45Z',
                  },
                  null,
                  2
                )}
              </Box>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Tab 2: View Rules */}
      {tabValue === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            {selectedRuleset ? (
              <>
                <Paper sx={{ p: 3, mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Ruleset: {selectedRuleset.ruleset_id}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <Chip label={`${selectedRuleset.rules?.length || 0} Rules`} />
                    <Chip label={`Schemas: ${selectedRuleset.schemas?.join(', ')}`} />
                  </Box>
                  <Button
                    variant="outlined"
                    startIcon={<Download />}
                    onClick={() => handleExportSQL(selectedRuleset.ruleset_id)}
                  >
                    Export as SQL
                  </Button>
                </Paper>

                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Rule Name</TableCell>
                        <TableCell>Source</TableCell>
                        <TableCell>Target</TableCell>
                        <TableCell>Match Type</TableCell>
                        <TableCell>Confidence</TableCell>
                        <TableCell>Details</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {selectedRuleset.rules?.map((rule) => (
                        <TableRow key={rule.rule_id}>
                          <TableCell>{rule.rule_name}</TableCell>
                          <TableCell>
                            {rule.source_schema}.{rule.source_table}
                            <br />
                            <Typography variant="caption">
                              ({rule.source_columns?.join(', ')})
                            </Typography>
                          </TableCell>
                          <TableCell>
                            {rule.target_schema}.{rule.target_table}
                            <br />
                            <Typography variant="caption">
                              ({rule.target_columns?.join(', ')})
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip label={rule.match_type} size="small" />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={rule.confidence_score?.toFixed(2)}
                              size="small"
                              color={rule.confidence_score >= 0.8 ? 'success' : 'warning'}
                            />
                          </TableCell>
                          <TableCell>
                            <Accordion>
                              <AccordionSummary expandIcon={<ExpandMore />}>
                                <Typography variant="caption">View Details</Typography>
                              </AccordionSummary>
                              <AccordionDetails>
                                <Typography variant="body2" paragraph>
                                  <strong>Reasoning:</strong> {rule.reasoning}
                                </Typography>
                                <Typography variant="body2">
                                  <strong>Status:</strong> {rule.validation_status}
                                </Typography>
                                <Typography variant="body2">
                                  <strong>LLM Generated:</strong>{' '}
                                  {rule.llm_generated ? 'Yes' : 'No'}
                                </Typography>
                              </AccordionDetails>
                            </Accordion>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </>
            ) : (
              <Alert severity="info">
                Select a ruleset from the "Manage Rulesets" tab to view its rules
              </Alert>
            )}
          </Grid>
        </Grid>
      )}

      {/* Tab 3: Manage */}
      {tabValue === 2 && (
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Box sx={{ mb: 2 }}>
              <Button variant="outlined" startIcon={<Refresh />} onClick={loadInitialData}>
                Refresh List
              </Button>
            </Box>
          </Grid>

          {rulesets.length === 0 ? (
            <Grid item xs={12}>
              <Alert severity="info">
                No rulesets found. Generate rules using the "Generate Rules" tab.
              </Alert>
            </Grid>
          ) : (
            rulesets.map((ruleset) => (
              <Grid item xs={12} md={6} key={ruleset.ruleset_id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {ruleset.ruleset_id}
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Chip label={`${ruleset.rule_count} Rules`} size="small" sx={{ mr: 0.5 }} />
                      {ruleset.schemas?.map((schema) => (
                        <Chip key={schema} label={schema} size="small" sx={{ mr: 0.5 }} />
                      ))}
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      Created: {new Date(ruleset.created_at).toLocaleString()}
                    </Typography>
                    <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => handleLoadRuleset(ruleset.ruleset_id)}
                      >
                        View
                      </Button>
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<Download />}
                        onClick={() => handleExportSQL(ruleset.ruleset_id)}
                      >
                        Export SQL
                      </Button>
                      <Button
                        size="small"
                        variant="outlined"
                        color="error"
                        startIcon={<Delete />}
                        onClick={() => handleDelete(ruleset.ruleset_id)}
                      >
                        Delete
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))
          )}
        </Grid>
      )}
    </Container>
  );
}
