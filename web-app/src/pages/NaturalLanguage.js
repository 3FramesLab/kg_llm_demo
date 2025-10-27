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
  Radio,
  RadioGroup,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  List,
  ListItem,
  IconButton,
  Slider,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import { Add, Delete, Send, PlayArrow } from '@mui/icons-material';
import { integrateNLRelationships, generateRules, listSchemas, listKGs, executeNLQueries } from '../services/api';

export default function NaturalLanguage() {
  const [schemas, setSchemas] = useState([]);
  const [kgs, setKgs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Tab selection: 'integrate' or 'execute'
  const [activeTab, setActiveTab] = useState('integrate');

  // Form state
  const [formData, setFormData] = useState({
    kg_name: '',
    schemas: [],
    definitions: [''],
    use_llm: true,
    min_confidence: 0.7,
    db_type: 'sqlserver',
    limit: 1000,
  });

  // Mode selection: 'nl' (natural language) or 'pairs' (explicit relationship pairs)
  const [inputMode, setInputMode] = useState('nl');

  // Explicit relationship pairs (JSON input)
  const [relationshipPairsInput, setRelationshipPairsInput] = useState('');

  // Excluded fields input (JSON array)
  const [excludedFieldsInput, setExcludedFieldsInput] = useState('');

  const [results, setResults] = useState(null);
  const [rulesetData, setRulesetData] = useState(null);
  const [queryResults, setQueryResults] = useState(null);
  const [currentStep, setCurrentStep] = useState(null); // 'integrating', 'generating', 'complete'

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [schemasRes, kgsRes] = await Promise.all([listSchemas(), listKGs()]);
      setSchemas(schemasRes.data.schemas || []);
      setKgs(kgsRes.data.graphs || []);
    } catch (err) {
      console.error('Error loading data:', err);
    }
  };

  const handleAddDefinition = () => {
    setFormData({
      ...formData,
      definitions: [...formData.definitions, ''],
    });
  };

  const handleRemoveDefinition = (index) => {
    const newDefinitions = formData.definitions.filter((_, i) => i !== index);
    setFormData({ ...formData, definitions: newDefinitions });
  };

  const handleDefinitionChange = (index, value) => {
    const newDefinitions = [...formData.definitions];
    newDefinitions[index] = value;
    setFormData({ ...formData, definitions: newDefinitions });
  };

  const handleSchemaToggle = (schema) => {
    const currentIndex = formData.schemas.indexOf(schema);
    const newSchemas = [...formData.schemas];

    if (currentIndex === -1) {
      newSchemas.push(schema);
    } else {
      newSchemas.splice(currentIndex, 1);
    }

    setFormData({ ...formData, schemas: newSchemas });
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    setResults(null);
    setRulesetData(null);

    try {
      // Step 1: Integrate relationships to KG (supports both NL and explicit pairs)
      setCurrentStep('integrating');
      const integratePayload = {
        kg_name: formData.kg_name,
        schemas: formData.schemas,
        use_llm: formData.use_llm,
        min_confidence: formData.min_confidence,
      };

      // Add NL definitions if in NL mode
      if (inputMode === 'nl') {
        integratePayload.nl_definitions = formData.definitions.filter((def) => def.trim() !== '');
      }

      // Add relationship pairs if in pairs mode
      if (inputMode === 'pairs' && relationshipPairsInput.trim()) {
        try {
          integratePayload.relationship_pairs = JSON.parse(relationshipPairsInput);
        } catch (e) {
          setError('Invalid JSON in relationship pairs: ' + e.message);
          setLoading(false);
          setCurrentStep(null);
          return;
        }
      }

      // Add excluded_fields if provided
      if (excludedFieldsInput.trim()) {
        try {
          integratePayload.excluded_fields = JSON.parse(excludedFieldsInput);
          console.log('✅ Excluded fields parsed:', integratePayload.excluded_fields);
        } catch (err) {
          setError('Invalid JSON in excluded fields: ' + err.message);
          setLoading(false);
          setCurrentStep(null);
          return;
        }
      }

      const integrateResponse = await integrateNLRelationships(integratePayload);
      setResults(integrateResponse.data);

      // Step 2: Generate reconciliation rules from the KG
      setCurrentStep('generating');
      const rulesPayload = {
        kg_name: formData.kg_name,
        schema_names: formData.schemas,
        use_llm_enhancement: formData.use_llm,
        min_confidence: formData.min_confidence,
      };

      const rulesResponse = await generateRules(rulesPayload);
      setRulesetData(rulesResponse.data);

      setCurrentStep('complete');

      // Build success message
      const nlAdded = integrateResponse.data.nl_relationships_added || 0;
      const pairsAdded = integrateResponse.data.explicit_pairs_added || 0;

      let integrationMsg = '';
      if (nlAdded > 0 && pairsAdded > 0) {
        integrationMsg = `${nlAdded} NL relationships and ${pairsAdded} explicit pairs`;
      } else if (nlAdded > 0) {
        integrationMsg = `${nlAdded} NL relationships`;
      } else if (pairsAdded > 0) {
        integrationMsg = `${pairsAdded} explicit pairs`;
      }

      setSuccess(
        `✅ Success! Integrated ${integrationMsg} and created ruleset ${rulesResponse.data.ruleset_id} with ${rulesResponse.data.rules_count} rules.`
      );
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      setCurrentStep(null);
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteQueries = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    setQueryResults(null);

    try {
      const validDefinitions = formData.definitions.filter((def) => def.trim() !== '');

      if (validDefinitions.length === 0) {
        setError('Please enter at least one definition');
        setLoading(false);
        return;
      }

      if (!formData.kg_name) {
        setError('Please select a Knowledge Graph');
        setLoading(false);
        return;
      }

      if (formData.schemas.length === 0) {
        setError('Please select at least one schema');
        setLoading(false);
        return;
      }

      const payload = {
        kg_name: formData.kg_name,
        schemas: formData.schemas,
        definitions: validDefinitions,
        use_llm: formData.use_llm,
        min_confidence: formData.min_confidence,
        limit: formData.limit,
        db_type: formData.db_type,
      };

      // Add excluded_fields if provided
      if (excludedFieldsInput.trim()) {
        try {
          payload.excluded_fields = JSON.parse(excludedFieldsInput);
          console.log('✅ Excluded fields parsed:', payload.excluded_fields);
        } catch (err) {
          setError('Invalid JSON in excluded fields: ' + err.message);
          setLoading(false);
          return;
        }
      }

      const response = await executeNLQueries(payload);
      setQueryResults(response.data);

      if (response.data.success) {
        setSuccess(
          `✅ Success! Executed ${response.data.total_definitions} queries. ${response.data.successful} successful, ${response.data.failed} failed.`
        );
      } else {
        setError(response.data.error || 'Query execution failed');
      }
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
          Natural Language to Reconciliation Rules
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Define relationships using plain English and automatically generate reconciliation rulesets
        </Typography>
        <Alert severity="info" sx={{ mt: 2 }}>
          This page integrates relationships into the Knowledge Graph and then automatically generates reconciliation rules.
        </Alert>
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

      {/* Tab Navigation */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Execute Queries" value="execute" />
        </Tabs>
      </Paper>

      {/* Integrate Tab - HIDDEN */}
      {activeTab === 'integrate' && false && (
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Define Relationships
            </Typography>

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

            <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
              Select Schemas
            </Typography>
            <Paper variant="outlined" sx={{ p: 2, maxHeight: 150, overflow: 'auto', mb: 2 }}>
              {schemas.map((schema) => (
                <FormControlLabel
                  key={schema}
                  control={
                    <Checkbox
                      checked={formData.schemas.includes(schema)}
                      onChange={() => handleSchemaToggle(schema)}
                    />
                  }
                  label={schema}
                />
              ))}
            </Paper>

            {/* Input Mode Selector */}
            <Box sx={{ mt: 3, mb: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Relationship Input Mode
              </Typography>
              <RadioGroup
                value={inputMode}
                onChange={(e) => setInputMode(e.target.value)}
                row
              >
                <FormControlLabel
                  value="nl"
                  control={<Radio />}
                  label="Natural Language (V1)"
                />
                <FormControlLabel
                  value="pairs"
                  control={<Radio />}
                  label="Explicit Pairs (V2 - Recommended)"
                />
              </RadioGroup>
            </Box>

            {/* V1: Natural Language Definitions */}
            {inputMode === 'nl' && (
              <>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Natural Language Definitions
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
                  Examples: "Products are supplied by Vendors", "Orders contain Products",
                  "catalog.product_id → designcode.item_id (REFERENCES)"
                </Typography>

                {formData.definitions.map((definition, index) => (
              <Box key={index} sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  value={definition}
                  onChange={(e) => handleDefinitionChange(index, e.target.value)}
                  placeholder="Enter a relationship definition..."
                />
                {formData.definitions.length > 1 && (
                  <IconButton
                    color="error"
                    onClick={() => handleRemoveDefinition(index)}
                    sx={{ height: 'fit-content' }}
                  >
                    <Delete />
                  </IconButton>
                )}
              </Box>
            ))}

                <Button
                  variant="outlined"
                  startIcon={<Add />}
                  onClick={handleAddDefinition}
                  sx={{ mb: 2 }}
                >
                  Add Definition
                </Button>
              </>
            )}

            {/* V2: Explicit Relationship Pairs */}
            {inputMode === 'pairs' && (
              <Box>
                <Alert severity="success" sx={{ mb: 2 }}>
                  <strong>V2 Mode (Recommended):</strong> Explicit source→target pairs stored directly in KG. No ambiguity!
                </Alert>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Relationship Pairs (JSON)
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
                  Define explicit source→target relationships with column-level precision.
                </Typography>
                <TextField
                  fullWidth
                  multiline
                  rows={12}
                  label="Relationship Pairs (JSON)"
                  placeholder={JSON.stringify([
                    {
                      source_table: "hana_material_master",
                      source_column: "MATERIAL",
                      target_table: "brz_lnd_OPS_EXCEL_GPU",
                      target_column: "PLANNING_SKU",
                      relationship_type: "MATCHES",
                      confidence: 0.98,
                      bidirectional: true
                    },
                    {
                      source_table: "brz_lnd_OPS_EXCEL_GPU",
                      source_column: "PLANNING_SKU",
                      target_table: "brz_lnd_RBP_GPU",
                      target_column: "Material",
                      relationship_type: "MATCHES",
                      confidence: 0.95
                    }
                  ], null, 2)}
                  value={relationshipPairsInput}
                  onChange={(e) => setRelationshipPairsInput(e.target.value)}
                  helperText="Explicit pairs are stored directly in the Knowledge Graph with clear source→target direction."
                />
              </Box>
            )}

            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.use_llm}
                  onChange={(e) => setFormData({ ...formData, use_llm: e.target.checked })}
                />
              }
              label="Use LLM for Enhanced Parsing"
              sx={{ display: 'block', mb: 2 }}
            />

            <Box sx={{ mb: 3 }}>
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

            <Divider sx={{ my: 3 }} />

            <Typography variant="subtitle1" gutterBottom>
              ⛔ Excluded Fields (Optional)
            </Typography>
            <Alert severity="info" sx={{ mb: 2 }}>
              Specify fields to exclude from relationship creation. These fields won't be used to link tables in the Knowledge Graph.
            </Alert>
            <TextField
              fullWidth
              multiline
              rows={6}
              label="Excluded Fields (JSON Array)"
              placeholder={JSON.stringify([
                "Product_Line",
                "product_line",
                "Business_Unit",
                "business_unit",
                "[Product Type]",
                "Product Type"
              ], null, 2)}
              value={excludedFieldsInput}
              onChange={(e) => setExcludedFieldsInput(e.target.value)}
              helperText="Provide a JSON array of field names to exclude. Leave empty to allow all fields."
              margin="normal"
            />

            {currentStep && (
              <Alert severity="info" sx={{ mb: 2 }}>
                {currentStep === 'integrating' && '⏳ Step 1/2: Integrating relationships to Knowledge Graph...'}
                {currentStep === 'generating' && '⏳ Step 2/2: Generating reconciliation rules...'}
                {currentStep === 'complete' && '✅ Complete! Rules generated successfully.'}
              </Alert>
            )}

            <Button
              variant="contained"
              startIcon={loading ? <CircularProgress size={20} /> : <Send />}
              onClick={handleSubmit}
              disabled={
                loading ||
                !formData.kg_name ||
                formData.schemas.length === 0 ||
                (inputMode === 'nl' && formData.definitions.filter((d) => d.trim()).length === 0) ||
                (inputMode === 'pairs' && !relationshipPairsInput.trim())
              }
              fullWidth
            >
              {loading ? 'Processing...' : 'Integrate & Generate Rules'}
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, mb: 3 }}>
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
                  kg_name: formData.kg_name || 'unified_kg',
                  schemas:
                    formData.schemas.length > 0
                      ? formData.schemas
                      : ['orderMgmt-catalog', 'qinspect-designcode'],
                  definitions:
                    formData.definitions.filter((d) => d.trim()).length > 0
                      ? formData.definitions.filter((d) => d.trim())
                      : [
                          'Products are supplied by Vendors',
                          'Orders contain Products',
                          'Inspection results reference design codes',
                        ],
                  use_llm: formData.use_llm,
                  min_confidence: formData.min_confidence,
                },
                null,
                2
              )}
            </Box>
          </Paper>

          {results && (
            <Paper sx={{ p: 3, mb: 2 }}>
              <Typography variant="h6" gutterBottom>
                Step 1: Knowledge Graph Integration
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Chip
                  label={`${results.total_relationships || 0} Total Relationships`}
                  color="primary"
                  sx={{ mr: 1 }}
                />
                <Chip
                  label={`${results.nl_relationships_added || 0} Added`}
                  color="success"
                  sx={{ mr: 1 }}
                />
                <Chip
                  label={`${results.auto_detected_relationships || 0} Auto-detected`}
                  color="info"
                />
              </Box>
              <Alert severity="success" sx={{ mt: 2 }}>
                ✅ Relationships successfully integrated into Knowledge Graph "{results.kg_name}"
              </Alert>
            </Paper>
          )}

          {rulesetData && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Step 2: Reconciliation Rules Generated
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Chip
                  label={`Ruleset ID: ${rulesetData.ruleset_id}`}
                  color="primary"
                  sx={{ mr: 1, mb: 1 }}
                />
                <Chip
                  label={`${rulesetData.rules_count} Rules Created`}
                  color="success"
                  sx={{ mr: 1, mb: 1 }}
                />
                <Chip
                  label={`${rulesetData.generation_time_ms?.toFixed(0) || 0}ms`}
                  color="info"
                  sx={{ mb: 1 }}
                />
              </Box>

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" gutterBottom>
                Generated Rules:
              </Typography>
              <List>
                {rulesetData.rules?.slice(0, 5).map((rule, index) => (
                  <ListItem
                    key={index}
                    sx={{
                      flexDirection: 'column',
                      alignItems: 'flex-start',
                      bgcolor: 'success.light',
                      borderRadius: 1,
                      mb: 1,
                      p: 2,
                    }}
                  >
                    <Typography variant="body2" fontWeight="bold">
                      {rule.rule_name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {rule.source_schema}.{rule.source_table} ({rule.source_columns?.join(', ')})
                      <br />
                      → {rule.target_schema}.{rule.target_table} ({rule.target_columns?.join(', ')})
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      <Chip
                        size="small"
                        label={`${rule.match_type}`}
                        sx={{ mr: 1 }}
                      />
                      <Chip
                        size="small"
                        label={`Confidence: ${(rule.confidence_score * 100).toFixed(0)}%`}
                        color={rule.confidence_score >= 0.8 ? 'success' : 'warning'}
                      />
                    </Box>
                  </ListItem>
                ))}
              </List>

              {rulesetData.rules_count > 5 && (
                <Typography variant="caption" color="text.secondary">
                  ... and {rulesetData.rules_count - 5} more rules
                </Typography>
              )}

              <Divider sx={{ my: 2 }} />

              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="outlined"
                  onClick={() => window.open(`/reconciliation?ruleset=${rulesetData.ruleset_id}`, '_blank')}
                >
                  View Ruleset Details
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => window.open(`${process.env.REACT_APP_API_URL || 'http://localhost:8000/v1'}/reconciliation/rulesets/${rulesetData.ruleset_id}/export/sql`, '_blank')}
                >
                  Export to SQL
                </Button>
              </Box>
            </Paper>
          )}
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Supported Formats
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  1. Natural Language
                </Typography>
                <Box component="code" sx={{ display: 'block', p: 1, bgcolor: 'grey.100' }}>
                  "Products are supplied by Vendors"
                  <br />
                  "Orders contain Products"
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  2. Semi-Structured
                </Typography>
                <Box component="code" sx={{ display: 'block', p: 1, bgcolor: 'grey.100' }}>
                  "catalog.product_id → vendor.vendor_id (SUPPLIED_BY)"
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  3. Pseudo-SQL
                </Typography>
                <Box component="code" sx={{ display: 'block', p: 1, bgcolor: 'grey.100' }}>
                  "SELECT * FROM products JOIN vendors ON products.vendor_id = vendors.id"
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  4. Business Rules
                </Typography>
                <Box component="code" sx={{ display: 'block', p: 1, bgcolor: 'grey.100' }}>
                  "IF product.status='active' THEN it must have a vendor assigned"
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
      )}

      {/* Execute Queries Tab */}
      {activeTab === 'execute' && (
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Execute NL Queries
            </Typography>

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
            >
              <option value="">Select a knowledge graph</option>
              {kgs.map((kg) => (
                <option key={kg.name} value={kg.name}>
                  {kg.name}
                </option>
              ))}
            </TextField>

            <Typography variant="subtitle2" sx={{ mt: 3, mb: 1 }}>
              Select Schemas
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
              {schemas.map((schema) => (
                <Chip
                  key={schema}
                  label={schema}
                  onClick={() => handleSchemaToggle(schema)}
                  color={formData.schemas.includes(schema) ? 'primary' : 'default'}
                  variant={formData.schemas.includes(schema) ? 'filled' : 'outlined'}
                />
              ))}
            </Box>

            <Typography variant="subtitle2" sx={{ mt: 3, mb: 1 }}>
              Query Definitions
            </Typography>
            {formData.definitions.map((definition, index) => (
              <Box key={index} sx={{ display: 'flex', gap: 1, mb: 1 }}>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  placeholder="e.g., Show me all products in RBP GPU which are not in OPS Excel"
                  value={definition}
                  onChange={(e) => handleDefinitionChange(index, e.target.value)}
                />
                {formData.definitions.length > 1 && (
                  <IconButton
                    color="error"
                    onClick={() => handleRemoveDefinition(index)}
                    size="small"
                  >
                    <Delete />
                  </IconButton>
                )}
              </Box>
            ))}

            <Button
              startIcon={<Add />}
              onClick={handleAddDefinition}
              variant="outlined"
              sx={{ mb: 2 }}
            >
              Add Definition
            </Button>

            <Divider sx={{ my: 2 }} />

            <TextField
              fullWidth
              type="number"
              label="Result Limit"
              value={formData.limit}
              onChange={(e) => setFormData({ ...formData, limit: parseInt(e.target.value) })}
              margin="normal"
              inputProps={{ min: 1, max: 10000 }}
            />

            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.use_llm}
                  onChange={(e) => setFormData({ ...formData, use_llm: e.target.checked })}
                />
              }
              label="Use LLM for Enhanced Parsing"
              sx={{ mt: 2 }}
            />

            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Minimum Confidence: {formData.min_confidence.toFixed(2)}
              </Typography>
              <Slider
                value={formData.min_confidence}
                onChange={(e, newValue) => setFormData({ ...formData, min_confidence: newValue })}
                min={0}
                max={1}
                step={0.05}
                marks={[
                  { value: 0, label: '0' },
                  { value: 0.5, label: '0.5' },
                  { value: 1, label: '1' },
                ]}
              />
            </Box>

            {/* Excluded Fields - HIDDEN */}
            {false && (
            <>
            <Divider sx={{ my: 3 }} />

            <Typography variant="subtitle1" gutterBottom>
              ⛔ Excluded Fields (Optional)
            </Typography>
            <Alert severity="info" sx={{ mb: 2 }}>
              Specify fields to exclude from join column detection. These fields won't be used to link tables in SQL generation.
            </Alert>
            <TextField
              fullWidth
              multiline
              rows={6}
              label="Excluded Fields (JSON Array)"
              placeholder={JSON.stringify([
                "Product_Line",
                "product_line",
                "Business_Unit",
                "business_unit",
                "[Product Type]",
                "Product Type"
              ], null, 2)}
              value={excludedFieldsInput}
              onChange={(e) => setExcludedFieldsInput(e.target.value)}
              helperText="Provide a JSON array of field names to exclude. Leave empty to allow all fields."
              margin="normal"
            />
            </>
            )}

            <Button
              fullWidth
              variant="contained"
              color="primary"
              startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
              onClick={handleExecuteQueries}
              disabled={loading}
              sx={{ mt: 3 }}
            >
              {loading ? 'Executing...' : 'Execute Queries'}
            </Button>
          </Paper>
        </Grid>

        {/* Query Results */}
        {queryResults && (
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Query Results
            </Typography>

            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2">
                Total Queries: {queryResults.total_definitions}
              </Typography>
              <Typography variant="subtitle2" color="success.main">
                Successful: {queryResults.successful}
              </Typography>
              {queryResults.failed > 0 && (
                <Typography variant="subtitle2" color="error">
                  Failed: {queryResults.failed}
                </Typography>
              )}
            </Box>

            {queryResults.statistics && (
            <Box sx={{ mb: 2, p: 1, bgcolor: 'grey.100', borderRadius: 1 }}>
              <Typography variant="subtitle2">Statistics</Typography>
              <Typography variant="body2">
                Total Records: {queryResults.statistics.total_records}
              </Typography>
              <Typography variant="body2">
                Execution Time: {queryResults.statistics.total_execution_time_ms.toFixed(2)}ms
              </Typography>
              <Typography variant="body2">
                Avg Confidence: {queryResults.statistics.average_confidence.toFixed(2)}
              </Typography>
            </Box>
            )}

            <Divider sx={{ my: 2 }} />

            {queryResults.results && queryResults.results.map((result, index) => (
            <Box key={index} sx={{ mb: 3, p: 2, border: '1px solid #ddd', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Query {index + 1}: {result.definition}
              </Typography>

              <Box sx={{ mb: 1 }}>
                <Chip
                  label={`Type: ${result.query_type}`}
                  size="small"
                  sx={{ mr: 1 }}
                />
                {result.operation && (
                  <Chip
                    label={`Operation: ${result.operation}`}
                    size="small"
                    sx={{ mr: 1 }}
                  />
                )}
                <Chip
                  label={`Confidence: ${result.confidence.toFixed(2)}`}
                  size="small"
                  color={result.confidence >= 0.8 ? 'success' : 'warning'}
                />
              </Box>

              {result.error ? (
                <Alert severity="error" sx={{ mb: 1 }}>
                  {result.error}
                </Alert>
              ) : (
                <>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Records Found:</strong> {result.record_count}
                  </Typography>

                  {result.join_columns && result.join_columns.length > 0 && (
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>Join Columns:</strong> {result.join_columns.map(jc => `${jc[0]} ← → ${jc[1]}`).join(', ')}
                    </Typography>
                  )}

                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Execution Time:</strong> {result.execution_time_ms.toFixed(2)}ms
                  </Typography>

                  <Box sx={{ mb: 1, p: 1, bgcolor: '#f5f5f5', borderRadius: 1, maxHeight: 150, overflow: 'auto' }}>
                    <Typography variant="caption" component="div" sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                      <strong>SQL:</strong>
                    </Typography>
                    <Typography variant="caption" component="div" sx={{ fontFamily: 'monospace', fontSize: '0.7rem', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                      {result.sql}
                    </Typography>
                  </Box>

                  {result.records && result.records.length > 0 && (
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="caption">
                        <strong>Sample Records (first 5):</strong>
                      </Typography>
                      <TableContainer sx={{ mt: 1 }}>
                        <Table size="small">
                          <TableHead>
                            <TableRow sx={{ bgcolor: 'grey.200' }}>
                              {Object.keys(result.records[0]).map((key) => (
                                <TableCell key={key} sx={{ fontSize: '0.75rem' }}>
                                  {key}
                                </TableCell>
                              ))}
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {result.records.slice(0, 5).map((record, rIdx) => (
                              <TableRow key={rIdx}>
                                {Object.values(record).map((value, vIdx) => (
                                  <TableCell key={vIdx} sx={{ fontSize: '0.75rem' }}>
                                    {String(value).substring(0, 50)}
                                  </TableCell>
                                ))}
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </Box>
                  )}
                </>
              )}
            </Box>
            ))}
          </Paper>
        </Grid>
        )}
      </Grid>
      )}
    </Container>
  );
}
