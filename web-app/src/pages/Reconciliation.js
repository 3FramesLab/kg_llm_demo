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
  Radio,
  RadioGroup,
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
  Fade,
} from '@mui/material';
import { Add, Refresh, Download, Delete, ExpandMore, CompareArrows, Settings, Visibility, FolderOpen, CheckCircle, Info } from '@mui/icons-material';
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

  // Mode selection: 'v1' (field_preferences) or 'v2' (reconciliation_pairs)
  const [preferenceMode, setPreferenceMode] = useState('v1');

  // V1: Optional field preferences (JSON) to guide rule generation
  const [fieldPreferencesInput, setFieldPreferencesInput] = useState('');

  // V2: Explicit reconciliation pairs (JSON)
  const [reconciliationPairsInput, setReconciliationPairsInput] = useState('');

  // V2: Auto-discover additional rules from KG
  const [autoDiscoverAdditional, setAutoDiscoverAdditional] = useState(true);

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
      // Build request payload explicitly so we can optionally add field_preferences or reconciliation_pairs
      const payload = {
        schema_names: formData.schema_names,
        kg_name: formData.kg_name,
        use_llm_enhancement: formData.use_llm_enhancement,
        min_confidence: formData.min_confidence,
      };

      // V1 Mode: Add field_preferences
      if (preferenceMode === 'v1' && fieldPreferencesInput.trim()) {
        try {
          payload.field_preferences = JSON.parse(fieldPreferencesInput);
        } catch (e) {
          setError('Invalid JSON in field preferences: ' + e.message);
          setLoading(false);
          return;
        }
      }

      // V2 Mode: Add reconciliation_pairs and auto_discover_additional
      if (preferenceMode === 'v2') {
        if (reconciliationPairsInput.trim()) {
          try {
            payload.reconciliation_pairs = JSON.parse(reconciliationPairsInput);
          } catch (e) {
            setError('Invalid JSON in reconciliation pairs: ' + e.message);
            setLoading(false);
            return;
          }
        }
        payload.auto_discover_additional = autoDiscoverAdditional;
      }

      const response = await generateRules(payload);
      const ruleCount =
        typeof response.data.rules_count !== 'undefined'
          ? response.data.rules_count
          : response.data.rule_count;

      // Show explicit vs discovered counts in success message
      let successMsg = `Generated ${ruleCount} rules in ruleset "${response.data.ruleset_id}"`;
      if (response.data.message && response.data.message.includes('explicit')) {
        successMsg = response.data.message + ` - Ruleset ID: "${response.data.ruleset_id}"`;
      }

      setSuccess(successMsg);
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
    <Container sx={{ p: 0 }}>
      {/* Enhanced Gradient Header */}
      <Box
        sx={{
          mb: 3,
          p: 2,
          borderRadius: 2,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          boxShadow: '0 4px 20px rgba(102, 126, 234, 0.3)',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
          <CompareArrows sx={{ fontSize: 28 }} />
          <Box>
            <Typography variant="h5" fontWeight="700" sx={{ mb: 0.25, lineHeight: 1.2, fontSize: '1.15rem' }}>
              Reconciliation Rule Generation
            </Typography>
            <Typography variant="body2" fontSize="0.8rem" sx={{ opacity: 0.95, fontWeight: 400 }}>
              Generate intelligent rules from knowledge graphs for single-schema joins or cross-schema data reconciliation
            </Typography>
          </Box>
        </Box>

        {/* Stats in Header */}
        {rulesets.length > 0 && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1.5 }}>
            <CheckCircle sx={{ fontSize: 18 }} />
            <Typography variant="body2" fontSize="0.8rem" sx={{ opacity: 0.95, fontWeight: 600 }}>
              {rulesets.length} {rulesets.length === 1 ? 'Ruleset' : 'Rulesets'} Available
            </Typography>
          </Box>
        )}
      </Box>

      {/* Error Alert */}
      {error && (
        <Fade in={!!error}>
          <Alert
            severity="error"
            onClose={() => setError(null)}
            sx={{
              mb: 3,
              borderRadius: 2,
              border: '1px solid',
              borderColor: 'error.light',
              fontWeight: 600,
            }}
          >
            {error}
          </Alert>
        </Fade>
      )}

      {/* Success Alert */}
      {success && (
        <Fade in={!!success}>
          <Alert
            severity="success"
            onClose={() => setSuccess(null)}
            sx={{
              mb: 3,
              borderRadius: 2,
              border: '1px solid',
              borderColor: 'success.light',
              fontWeight: 600,
            }}
          >
            {success}
          </Alert>
        </Fade>
      )}

      {/* Enhanced Tab Navigation */}
      <Paper
        elevation={0}
        sx={{
          mb: 3,
          borderRadius: 2,
          border: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Tabs
          value={tabValue}
          onChange={(e, newValue) => setTabValue(newValue)}
          sx={{
            minHeight: 48,
            '& .MuiTab-root': {
              textTransform: 'none',
              fontSize: '0.85rem',
              fontWeight: 600,
              minHeight: 48,
              py: 1,
              transition: 'all 0.3s ease',
              '&:hover': {
                backgroundColor: 'action.hover',
              },
            },
            '& .Mui-selected': {
              color: '#667eea',
            },
            '& .MuiTabs-indicator': {
              height: 3,
              borderRadius: '3px 3px 0 0',
              background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
            },
          }}
        >
          <Tab icon={<Add />} iconPosition="start" label="Generate Rules" />
          <Tab icon={<Visibility />} iconPosition="start" label="View Rules" />
          <Tab icon={<FolderOpen />} iconPosition="start" label="Manage Rulesets" />
        </Tabs>
      </Paper>

      {/* Tab 1: Generate */}
      {tabValue === 0 && (
        <Fade in={tabValue === 0} timeout={500}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  borderRadius: 2,
                  border: '1px solid',
                  borderColor: 'divider',
                  background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.02) 0%, rgba(118, 75, 162, 0.02) 100%)',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                  <Box
                    sx={{
                      p: 1,
                      borderRadius: 1.5,
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Settings sx={{ color: 'white', fontSize: 22 }} />
                  </Box>
                  <Typography variant="h6" fontWeight="700" fontSize="0.95rem">
                    Generate Reconciliation Rules
                  </Typography>
                </Box>

                {formData.schema_names.length === 1 && (
                  <Alert
                    severity="info"
                    sx={{
                      mb: 2,
                      borderRadius: 1.5,
                      fontWeight: 600,
                    }}
                  >
                    <strong>Single Schema Mode:</strong> Generating join/query rules within one database for referential integrity and table relationships.
                  </Alert>
                )}
                {formData.schema_names.length >= 2 && (
                  <Alert
                    severity="success"
                    sx={{
                      mb: 2,
                      borderRadius: 1.5,
                      fontWeight: 600,
                    }}
                  >
                    <strong>Multi-Schema Mode:</strong> Generating cross-schema reconciliation rules to match data across different databases.
                  </Alert>
                )}

                <Typography variant="subtitle2" sx={{ mt: 2, mb: 1, fontWeight: 700, fontSize: '0.85rem' }}>
                  Select Schemas (1 or more)
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1.5, lineHeight: 1.5 }}>
                  Single schema: Generate join rules within database. Multiple schemas: Generate cross-database reconciliation rules.
                </Typography>
                <Paper
                  variant="outlined"
                  sx={{
                    p: 2,
                    maxHeight: 200,
                    overflow: 'auto',
                    mb: 2,
                    borderRadius: 1.5,
                    borderColor: 'divider',
                    '&:hover': {
                      borderColor: 'primary.main',
                    },
                    transition: 'border-color 0.3s ease',
                  }}
                >
                  {schemas.map((schema) => (
                    <FormControlLabel
                      key={schema}
                      control={
                        <Checkbox
                          checked={formData.schema_names.includes(schema)}
                          onChange={() => handleSchemaToggle(schema)}
                          sx={{
                            '&.Mui-checked': {
                              color: '#667eea',
                            },
                          }}
                        />
                      }
                      label={<Typography variant="body2" fontSize="0.85rem">{schema}</Typography>}
                      sx={{ mb: 0.5 }}
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
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 1.5,
                      '&:hover fieldset': {
                        borderColor: '#667eea',
                      },
                      '&.Mui-focused fieldset': {
                        borderColor: '#667eea',
                      },
                    },
                  }}
                >
                  <option value="">Select a knowledge graph</option>
                  {kgs.map((kg) => (
                    <option key={kg.name} value={kg.name}>
                      {kg.name}
                    </option>
                  ))}
                </TextField>

                <Box sx={{ mt: 2.5 }}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={formData.use_llm_enhancement}
                        onChange={(e) =>
                          setFormData({ ...formData, use_llm_enhancement: e.target.checked })
                        }
                        sx={{
                          '&.Mui-checked': {
                            color: '#667eea',
                          },
                        }}
                      />
                    }
                    label={<Typography variant="body2" fontSize="0.85rem" fontWeight={600}>Use LLM Enhancement for Semantic Rules</Typography>}
                  />
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', ml: 4, lineHeight: 1.5 }}>
                    LLM will intelligently infer relationships {formData.schema_names.length === 1 ? 'within the schema' : 'across schemas'} and generate high-quality rules.
                  </Typography>
                </Box>

                <Box sx={{ mt: 3 }}>
                  <Typography variant="body2" fontWeight={600} fontSize="0.85rem" gutterBottom>
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
                    sx={{
                      color: '#667eea',
                      '& .MuiSlider-thumb': {
                        '&:hover, &.Mui-focusVisible': {
                          boxShadow: '0 0 0 8px rgba(102, 126, 234, 0.16)',
                        },
                      },
                    }}
                  />
                </Box>

                {/* Advanced Options: Mode Selector */}
                <Accordion
                  sx={{
                    mt: 3,
                    borderRadius: 1.5,
                    border: '1px solid',
                    borderColor: 'divider',
                    '&:before': {
                      display: 'none',
                    },
                    boxShadow: 'none',
                  }}
                >
                  <AccordionSummary
                    expandIcon={<ExpandMore />}
                    sx={{
                      '&:hover': {
                        backgroundColor: 'rgba(102, 126, 234, 0.04)',
                      },
                    }}
                  >
                    <Typography variant="body2" fontWeight={600} fontSize="0.85rem">Advanced Options</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                  <Typography variant="subtitle2" sx={{ mb: 2 }}>
                    Rule Generation Mode
                  </Typography>

                  {/* Mode Selector */}
                  <RadioGroup
                    value={preferenceMode}
                    onChange={(e) => setPreferenceMode(e.target.value)}
                    sx={{ mb: 3 }}
                  >
                    <FormControlLabel
                      value="v1"
                      control={<Radio />}
                      label="V1: Field Preferences (Table-centric hints)"
                    />
                    <FormControlLabel
                      value="v2"
                      control={<Radio />}
                      label="V2: Reconciliation Pairs (Explicit source→target) - Recommended"
                    />
                  </RadioGroup>

                  {/* V1 Mode: Field Preferences */}
                  {preferenceMode === 'v1' && (
                    <Box>
                      <Alert severity="info" sx={{ mb: 2 }}>
                        <strong>V1 Mode:</strong> Table-centric field hints. Ambiguous when multiple target tables exist.
                      </Alert>
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
                    </Box>
                  )}

                  {/* V2 Mode: Reconciliation Pairs */}
                  {preferenceMode === 'v2' && (
                    <Box>
                      <Alert severity="success" sx={{ mb: 2 }}>
                        <strong>V2 Mode (Recommended):</strong> Explicit source→target pairs. Unambiguous and precise.
                      </Alert>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        Define explicit reconciliation pairs with source table/columns → target table/columns.
                        Supports filters, transformations, and bidirectional matching.
                      </Typography>
                      <TextField
                        fullWidth
                        multiline
                        rows={12}
                        label="Reconciliation Pairs (JSON)"
                        placeholder={JSON.stringify([
                          {
                            source_table: "hana_material_master",
                            source_columns: ["MATERIAL"],
                            target_table: "brz_lnd_OPS_EXCEL_GPU",
                            target_columns: ["PLANNING_SKU"],
                            match_type: "exact",
                            source_filters: null,
                            target_filters: {
                              Active_Inactive: "Active"
                            },
                            bidirectional: true,
                            priority: "high"
                          },
                          {
                            source_table: "brz_lnd_OPS_EXCEL_GPU",
                            source_columns: ["PLANNING_SKU"],
                            target_table: "brz_lnd_RBP_GPU",
                            target_columns: ["Material"],
                            match_type: "exact",
                            bidirectional: false,
                            priority: "normal"
                          }
                        ], null, 2)}
                        value={reconciliationPairsInput}
                        onChange={(e) => setReconciliationPairsInput(e.target.value)}
                        helperText="Explicit pairs take precedence. Each pair specifies source→target with full control."
                      />

                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={autoDiscoverAdditional}
                            onChange={(e) => setAutoDiscoverAdditional(e.target.checked)}
                          />
                        }
                        label="Auto-discover additional rules from Knowledge Graph"
                        sx={{ mt: 2 }}
                      />
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', ml: 4 }}>
                        Enable to supplement explicit pairs with auto-discovered rules from KG relationships.
                      </Typography>
                    </Box>
                  )}
                </AccordionDetails>
              </Accordion>

                <Box sx={{ mt: 3 }}>
                  <Button
                    variant="contained"
                    size="large"
                    startIcon={loading ? <CircularProgress size={20} sx={{ color: 'white' }} /> : <Add />}
                    onClick={handleGenerate}
                    disabled={
                      loading || formData.schema_names.length === 0 || !formData.kg_name
                    }
                    fullWidth
                    sx={{
                      py: 1.5,
                      borderRadius: 1.5,
                      fontSize: '0.9rem',
                      fontWeight: 700,
                      textTransform: 'none',
                      boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)',
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      '&:hover': {
                        boxShadow: '0 6px 16px rgba(102, 126, 234, 0.4)',
                        transform: 'translateY(-2px)',
                        background: 'linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%)',
                      },
                      '&:disabled': {
                        background: 'rgba(0, 0, 0, 0.12)',
                      },
                      transition: 'all 0.3s ease',
                    }}
                  >
                    {loading ? 'Generating...' : 'Generate Rules'}
                  </Button>
                </Box>
              </Paper>
            </Grid>

            <Grid item xs={12} md={6}>
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  borderRadius: 2,
                  border: '1px solid',
                  borderColor: 'divider',
                  background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.02) 0%, rgba(118, 75, 162, 0.02) 100%)',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                  <Box
                    sx={{
                      p: 1,
                      borderRadius: 1.5,
                      background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Info sx={{ color: 'white', fontSize: 22 }} />
                  </Box>
                  <Typography variant="h6" fontWeight="700" fontSize="0.95rem">
                    Request Example
                  </Typography>
                </Box>
                <Box
                  component="pre"
                  sx={{
                    p: 2,
                    bgcolor: 'rgba(0, 0, 0, 0.03)',
                    borderRadius: 1.5,
                    overflow: 'auto',
                    fontSize: '0.75rem',
                    border: '1px solid',
                    borderColor: 'divider',
                    fontFamily: 'monospace',
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

                <Divider sx={{ my: 3 }} />

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                  <Box
                    sx={{
                      p: 1,
                      borderRadius: 1.5,
                      background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <CheckCircle sx={{ color: 'white', fontSize: 22 }} />
                  </Box>
                  <Box>
                    <Typography variant="h6" fontWeight="700" fontSize="0.95rem">
                      Response Example
                    </Typography>
                    <Typography variant="caption" fontSize="0.7rem" color="text.secondary">
                      {formData.schema_names.length === 1
                        ? 'Single schema: Rules for joining tables within the same database'
                        : 'Multi-schema: Rules for matching data across different databases'}
                    </Typography>
                  </Box>
                </Box>
                <Box
                  component="pre"
                  sx={{
                    p: 2,
                    bgcolor: 'rgba(0, 0, 0, 0.03)',
                    borderRadius: 1.5,
                    overflow: 'auto',
                    fontSize: '0.75rem',
                    maxHeight: 400,
                    border: '1px solid',
                    borderColor: 'divider',
                    fontFamily: 'monospace',
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
        </Fade>
      )}

      {/* Tab 2: View Rules */}
      {tabValue === 1 && (
        <Fade in={tabValue === 1} timeout={500}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              {loading && (
                <Fade in={loading}>
                  <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', p: 6 }}>
                    <CircularProgress size={48} thickness={4} />
                  </Box>
                </Fade>
              )}
              {!loading && selectedRuleset ? (
                <>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      mb: 3,
                      borderRadius: 2,
                      border: '1px solid',
                      borderColor: 'divider',
                      background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.03) 0%, rgba(118, 75, 162, 0.03) 100%)',
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                      <Box
                        sx={{
                          p: 1,
                          borderRadius: 1.5,
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}
                      >
                        <Visibility sx={{ color: 'white', fontSize: 22 }} />
                      </Box>
                      <Typography variant="h6" fontWeight="700" fontSize="0.95rem">
                        Ruleset: {selectedRuleset.ruleset_id}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                      <Chip
                        label={`${selectedRuleset.rules?.length || 0} Rules`}
                        size="medium"
                        sx={{
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          borderRadius: 1.5,
                        }}
                        color="primary"
                      />
                      <Chip
                        label={`Schemas: ${selectedRuleset.schemas?.join(', ')}`}
                        size="medium"
                        sx={{
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          borderRadius: 1.5,
                        }}
                        variant="outlined"
                      />
                    </Box>
                    <Button
                      variant="contained"
                      size="medium"
                      startIcon={<Download />}
                      onClick={() => handleExportSQL(selectedRuleset.ruleset_id)}
                      sx={{
                        py: 1,
                        px: 2.5,
                        borderRadius: 1.5,
                        fontSize: '0.85rem',
                        fontWeight: 600,
                        textTransform: 'none',
                        boxShadow: '0 2px 8px rgba(102, 126, 234, 0.25)',
                        '&:hover': {
                          boxShadow: '0 4px 12px rgba(102, 126, 234, 0.35)',
                          transform: 'translateY(-1px)',
                        },
                        transition: 'all 0.3s ease',
                      }}
                    >
                      Export as SQL
                    </Button>
                  </Paper>

                  <TableContainer
                    component={Paper}
                    elevation={0}
                    sx={{
                      borderRadius: 2,
                      border: '1px solid',
                      borderColor: 'divider',
                    }}
                  >
                    <Table>
                      <TableHead>
                        <TableRow
                          sx={{
                            background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%)',
                          }}
                        >
                          <TableCell sx={{ fontWeight: 700, fontSize: '0.85rem' }}>Rule Name</TableCell>
                          <TableCell sx={{ fontWeight: 700, fontSize: '0.85rem' }}>Source</TableCell>
                          <TableCell sx={{ fontWeight: 700, fontSize: '0.85rem' }}>Target</TableCell>
                          <TableCell sx={{ fontWeight: 700, fontSize: '0.85rem' }}>Match Type</TableCell>
                          <TableCell sx={{ fontWeight: 700, fontSize: '0.85rem' }}>Confidence</TableCell>
                          <TableCell sx={{ fontWeight: 700, fontSize: '0.85rem' }}>Details</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {selectedRuleset.rules?.map((rule, index) => (
                          <TableRow
                            key={rule.rule_id}
                            sx={{
                              '&:hover': {
                                backgroundColor: 'rgba(102, 126, 234, 0.04)',
                              },
                              transition: 'background-color 0.3s ease',
                            }}
                          >
                            <TableCell sx={{ fontSize: '0.8rem', fontWeight: 600 }}>{rule.rule_name}</TableCell>
                            <TableCell sx={{ fontSize: '0.8rem' }}>
                              {rule.source_schema}.{rule.source_table}
                              <br />
                              <Typography variant="caption" color="text.secondary">
                                ({rule.source_columns?.join(', ')})
                              </Typography>
                            </TableCell>
                            <TableCell sx={{ fontSize: '0.8rem' }}>
                              {rule.target_schema}.{rule.target_table}
                              <br />
                              <Typography variant="caption" color="text.secondary">
                                ({rule.target_columns?.join(', ')})
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={rule.match_type}
                                size="small"
                                sx={{
                                  fontWeight: 600,
                                  borderRadius: 1,
                                }}
                              />
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={rule.confidence_score?.toFixed(2)}
                                size="small"
                                color={rule.confidence_score >= 0.8 ? 'success' : 'warning'}
                                sx={{
                                  fontWeight: 600,
                                  borderRadius: 1,
                                }}
                              />
                            </TableCell>
                            <TableCell>
                              <Accordion
                                sx={{
                                  boxShadow: 'none',
                                  '&:before': {
                                    display: 'none',
                                  },
                                }}
                              >
                                <AccordionSummary expandIcon={<ExpandMore />}>
                                  <Typography variant="caption" fontWeight={600}>View Details</Typography>
                                </AccordionSummary>
                                <AccordionDetails>
                                  <Typography variant="body2" paragraph sx={{ fontSize: '0.8rem' }}>
                                    <strong>Reasoning:</strong> {rule.reasoning}
                                  </Typography>
                                  <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
                                    <strong>Status:</strong> {rule.validation_status}
                                  </Typography>
                                  <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
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
                <Paper
                  elevation={0}
                  sx={{
                    p: 4,
                    borderRadius: 2,
                    border: '2px dashed',
                    borderColor: 'divider',
                    textAlign: 'center',
                    background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.03) 0%, rgba(118, 75, 162, 0.03) 100%)',
                  }}
                >
                  <CompareArrows sx={{ fontSize: 64, color: 'text.secondary', mb: 2, opacity: 0.5 }} />
                  <Typography variant="h6" fontWeight="700" fontSize="0.95rem" gutterBottom>
                    {rulesets.length === 0 ? 'No Rulesets Available' : 'No Ruleset Selected'}
                  </Typography>
                  <Typography variant="body2" fontSize="0.8rem" color="text.secondary">
                    {rulesets.length === 0
                      ? 'Generate rules using the "Generate Rules" tab to get started.'
                      : 'Click "View" on a ruleset in the "Manage Rulesets" tab to view its rules.'}
                  </Typography>
                </Paper>
              ) : null}
            </Grid>
          </Grid>
        </Fade>
      )}

      {/* Tab 3: Manage */}
      {tabValue === 2 && (
        <Fade in={tabValue === 2} timeout={500}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Box sx={{ mb: 3 }}>
                <Button
                  variant="contained"
                  size="medium"
                  startIcon={<Refresh />}
                  onClick={loadInitialData}
                  sx={{
                    py: 1,
                    px: 2.5,
                    borderRadius: 1.5,
                    fontSize: '0.85rem',
                    fontWeight: 600,
                    textTransform: 'none',
                    boxShadow: '0 2px 8px rgba(102, 126, 234, 0.25)',
                    '&:hover': {
                      boxShadow: '0 4px 12px rgba(102, 126, 234, 0.35)',
                      transform: 'translateY(-1px)',
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  Refresh List
                </Button>
              </Box>
            </Grid>

            {rulesets.length === 0 ? (
              <Grid item xs={12}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 4,
                    borderRadius: 2,
                    border: '2px dashed',
                    borderColor: 'divider',
                    textAlign: 'center',
                    background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.03) 0%, rgba(118, 75, 162, 0.03) 100%)',
                  }}
                >
                  <FolderOpen sx={{ fontSize: 64, color: 'text.secondary', mb: 2, opacity: 0.5 }} />
                  <Typography variant="h6" fontWeight="700" fontSize="0.95rem" gutterBottom>
                    No Rulesets Found
                  </Typography>
                  <Typography variant="body2" fontSize="0.8rem" color="text.secondary">
                    Generate rules using the "Generate Rules" tab to create your first ruleset.
                  </Typography>
                </Paper>
              </Grid>
            ) : (
              rulesets.map((ruleset) => (
                <Grid item xs={12} md={6} lg={4} key={ruleset.ruleset_id}>
                  <Card
                    elevation={0}
                    sx={{
                      borderRadius: 2,
                      border: '1px solid',
                      borderColor: 'divider',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        borderColor: '#667eea',
                        boxShadow: '0 4px 16px rgba(102, 126, 234, 0.15)',
                        transform: 'translateY(-4px)',
                      },
                    }}
                  >
                    <CardContent sx={{ p: 2.5 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                        <Box
                          sx={{
                            p: 0.75,
                            borderRadius: 1,
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                          }}
                        >
                          <CompareArrows sx={{ color: 'white', fontSize: 18 }} />
                        </Box>
                        <Typography variant="h6" fontWeight="700" fontSize="0.9rem" sx={{ flex: 1 }}>
                          {ruleset.ruleset_id}
                        </Typography>
                      </Box>
                      <Box sx={{ mb: 2, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        <Chip
                          label={`${ruleset.rule_count} Rules`}
                          size="small"
                          sx={{
                            fontSize: '0.7rem',
                            fontWeight: 600,
                            borderRadius: 1,
                          }}
                          color="primary"
                        />
                        {ruleset.schemas?.map((schema) => (
                          <Chip
                            key={schema}
                            label={schema}
                            size="small"
                            sx={{
                              fontSize: '0.7rem',
                              fontWeight: 600,
                              borderRadius: 1,
                            }}
                            variant="outlined"
                          />
                        ))}
                      </Box>
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2, fontSize: '0.7rem' }}>
                        Created: {new Date(ruleset.created_at).toLocaleString()}
                      </Typography>
                      <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        <Button
                          size="small"
                          variant="contained"
                          onClick={() => handleLoadRuleset(ruleset.ruleset_id)}
                          sx={{
                            py: 0.75,
                            px: 1.5,
                            borderRadius: 1,
                            fontSize: '0.8rem',
                            fontWeight: 600,
                            textTransform: 'none',
                            boxShadow: '0 2px 6px rgba(102, 126, 234, 0.25)',
                            '&:hover': {
                              boxShadow: '0 3px 8px rgba(102, 126, 234, 0.35)',
                            },
                          }}
                        >
                          View
                        </Button>
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<Download />}
                          onClick={() => handleExportSQL(ruleset.ruleset_id)}
                          sx={{
                            py: 0.75,
                            px: 1.5,
                            borderRadius: 1,
                            fontSize: '0.8rem',
                            fontWeight: 600,
                            textTransform: 'none',
                          }}
                        >
                          Export SQL
                        </Button>
                        <Button
                          size="small"
                          variant="outlined"
                          color="error"
                          startIcon={<Delete />}
                          onClick={() => handleDelete(ruleset.ruleset_id)}
                          sx={{
                            py: 0.75,
                            px: 1.5,
                            borderRadius: 1,
                            fontSize: '0.8rem',
                            fontWeight: 600,
                            textTransform: 'none',
                            '&:hover': {
                              backgroundColor: 'error.light',
                              color: 'white',
                            },
                          }}
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
        </Fade>
      )}
    </Container>
  );
}
