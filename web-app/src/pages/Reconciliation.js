import React, { useState, useEffect, useCallback } from 'react';
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
  MenuItem,
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

  // Optional field preferences (JSON) to guide rule generation
  const [fieldPreferencesInput, setFieldPreferencesInput] = useState('');

  useEffect(() => {
    loadInitialData();
  }, []);

  // Auto-load first ruleset when switching to View Rules tab (only if no ruleset selected)
  useEffect(() => {
    if (tabValue === 1 && !selectedRuleset && rulesets.length > 0) {
      handleLoadRuleset(rulesets[0].ruleset_id);
    }
  }, [tabValue, rulesets]);

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
      // Build request payload explicitly so we can optionally add field_preferences
      const payload = {
        schema_names: formData.schema_names,
        kg_name: formData.kg_name,
        use_llm_enhancement: formData.use_llm_enhancement,
        min_confidence: formData.min_confidence,
      };

      if (fieldPreferencesInput.trim()) {
        try {
          payload.field_preferences = JSON.parse(fieldPreferencesInput);
        } catch (e) {
          setError('Invalid JSON in field preferences: ' + e.message);
          setLoading(false);
          return;
        }
      }

      const response = await generateRules(payload);
      const ruleCount =
        typeof response.data.rules_count !== 'undefined'
          ? response.data.rules_count
          : response.data.rule_count;
      setSuccess(
        `Generated ${ruleCount} rules in ruleset "${response.data.ruleset_id}"`
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
    setError(null);
    try {
      const response = await getRuleset(rulesetId);
      // Backend returns { success: true, ruleset: {...} }
      const ruleset = response.data.ruleset || response.data;
      setSelectedRuleset(ruleset);
      setTabValue(1);
    } catch (err) {
      console.error('Error loading ruleset:', err);
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
          Generate intelligent rules from knowledge graphs for single-schema joins or cross-schema data reconciliation
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

              {formData.schema_names.length === 1 && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  <strong>Single Schema Mode:</strong> Generating join/query rules within one database for referential integrity and table relationships.
                </Alert>
              )}
              {formData.schema_names.length >= 2 && (
                <Alert severity="success" sx={{ mb: 2 }}>
                  <strong>Multi-Schema Mode:</strong> Generating cross-schema reconciliation rules to match data across different databases.
                </Alert>
              )}

              <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
                Select Schemas (1 or more)
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                Single schema: Generate join rules within database. Multiple schemas: Generate cross-database reconciliation rules.
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

              <Box sx={{ mt: 2 }}>
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
                />
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', ml: 4 }}>
                  LLM will intelligently infer relationships {formData.schema_names.length === 1 ? 'within the schema' : 'across schemas'} and generate high-quality rules.
                </Typography>
              </Box>

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

              {/* Field Preferences (Optional) */}
              {formData.use_llm_enhancement && (
                <Accordion sx={{ mt: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography>Field Preferences (Optional - Advanced)</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      Guide LLM rule generation with table-specific field hints. Provide a JSON array
                      where each object targets a table and includes field_hints, priority_fields, and exclude_fields.
                    </Typography>
                    <TextField
                      fullWidth
                      multiline
                      rows={8}
                      label="Field Preferences (JSON)"
                      placeholder={JSON.stringify([
                        {
                          table_name: "hana_material_master",
                          field_hints: {
                            MATERIAL: "PLANNING_SKU"
                          },
                          priority_fields: ["MATERIAL", "MATERIAL_DESC"],
                          exclude_fields: ["INTERNAL_NOTES", "TEMP_FIELD"]
                        },
                        {
                          table_name: "brz_lnd_OPS_EXCEL_GPU",
                          field_hints: {
                            PLANNING_SKU: "MATERIAL",
                            GPU_MODEL: "PRODUCT_TYPE"
                          },
                          priority_fields: ["PLANNING_SKU", "GPU_MODEL"],
                          exclude_fields: ["STAGING_FLAG"]
                        }
                      ], null, 2)}
                      value={fieldPreferencesInput}
                      onChange={(e) => setFieldPreferencesInput(e.target.value)}
                      helperText="Provide field hints to guide LLM and fallback rule generation. Leave empty to skip."
                    />
                  </AccordionDetails>
                </Accordion>
              )}

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
                Request Example
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
                        : formData.schema_names.length === 1
                          ? ['hana_material_master']
                          : ['orderMgmt-catalog', 'qinspect-designcode'],
                    kg_name: formData.kg_name || (formData.schema_names.length === 1 ? 'single_kg' : 'unified_kg'),
                    use_llm_enhancement: formData.use_llm_enhancement,
                    min_confidence: formData.min_confidence,
                    ...(fieldPreferencesInput.trim()
                      ? { field_preferences: (() => { try { return JSON.parse(fieldPreferencesInput); } catch { return undefined; } })() }
                      : { field_preferences: [
                          {
                            table_name: 'catalog',
                            field_hints: { code: 'code', style_code: 'code', is_active: 'deleted' },
                            priority_fields: [],
                            exclude_fields: []
                          }
                        ] }
                    )
                  },
                  null,
                  2
                )}
              </Box>

              <Divider sx={{ my: 2 }} />

              <Typography variant="h6" gutterBottom>
                Response Example
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                {formData.schema_names.length === 1
                  ? 'Single schema: Rules for joining tables within the same database'
                  : 'Multi-schema: Rules for matching data across different databases'}
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
                {formData.schema_names.length === 1 ? (
                  JSON.stringify(
                    {
                      ruleset_id: 'RECON_ABC12345',
                      rule_count: 8,
                      rules: [
                        {
                          rule_id: 'RULE_001',
                          rule_name: 'SEMANTIC_REFERENCE_orders_customers',
                          source_schema: 'hana_material_master',
                          source_table: 'orders',
                          source_columns: ['customer_id'],
                          target_schema: 'hana_material_master',
                          target_table: 'customers',
                          target_columns: ['id'],
                          match_type: 'exact',
                          confidence_score: 0.95,
                          reasoning: 'Foreign key relationship for referential integrity',
                          llm_generated: false,
                        },
                      ],
                      created_at: '2024-10-25T10:30:45Z',
                    },
                    null,
                    2
                  )
                ) : (
                  JSON.stringify(
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
                          llm_generated: true,
                        },
                      ],
                      created_at: '2024-10-25T10:30:45Z',
                    },
                    null,
                    2
                  )
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
            {loading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
              </Box>
            )}
            {!loading && selectedRuleset ? (
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
            ) : !loading ? (
              <Alert severity="info">
                {rulesets.length === 0
                  ? 'No rulesets available. Generate rules using the "Generate Rules" tab.'
                  : 'Click "View" on a ruleset in the "Manage" tab to view its rules.'}
              </Alert>
            ) : null}
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
