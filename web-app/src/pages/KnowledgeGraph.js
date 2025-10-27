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
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  Add,
  Refresh,
  Delete,
  Download,
  ExpandMore,
  AccountTree,
  Hub,
} from '@mui/icons-material';
import { Radio, RadioGroup } from '@mui/material';
import {
  generateKG,
  listKGs,
  listSchemas,
  getKGEntities,
  getKGRelationships,
  exportKG,
  deleteKG,
  checkLLMStatus,
} from '../services/api';
import GraphVisualization from '../components/GraphVisualization';

export default function KnowledgeGraph() {
  const [tabValue, setTabValue] = useState(0);
  const [schemas, setSchemas] = useState([]);
  const [knowledgeGraphs, setKnowledgeGraphs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    schema_name: '',
    schema_names: [],
    kg_name: '',
    use_llm_enhancement: true,
    backends: ['graphiti'],
    field_preferences: null,
  });

  // Input mode: 'field_preferences' (v1) or 'relationship_pairs' (v2)
  const [inputMode, setInputMode] = useState('field_preferences');

  // Field preferences input (JSON string - v1)
  const [fieldPreferencesInput, setFieldPreferencesInput] = useState('');

  // Relationship pairs input (JSON string - v2)
  const [relationshipPairsInput, setRelationshipPairsInput] = useState('');

  // Excluded fields input (JSON array - list of field names to exclude)
  const [excludedFieldsInput, setExcludedFieldsInput] = useState('');

  // Selected KG details
  const [selectedKG, setSelectedKG] = useState(null);
  const [kgEntities, setKgEntities] = useState([]);
  const [kgRelationships, setKgRelationships] = useState([]);

  // LLM status
  const [llmStatus, setLlmStatus] = useState({ enabled: false, model: null });

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [schemasRes, kgsRes, llmStatusRes] = await Promise.all([
        listSchemas(),
        listKGs(),
        checkLLMStatus(),
      ]);
      setSchemas(schemasRes.data.schemas || []);
      setKnowledgeGraphs(kgsRes.data.graphs || []);
      setLlmStatus(llmStatusRes.data);
    } catch (err) {
      console.error('Error loading data:', err);
    }
  };

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const payload = {
        kg_name: formData.kg_name,
        backends: formData.backends,
        use_llm_enhancement: formData.use_llm_enhancement,
      };

      if (formData.schema_names.length > 0) {
        payload.schema_names = formData.schema_names;
      } else {
        payload.schema_name = formData.schema_name;
      }

      // V1: Add field_preferences if in v1 mode
      if (inputMode === 'field_preferences' && fieldPreferencesInput.trim()) {
        try {
          let parsed = JSON.parse(fieldPreferencesInput);

          // Handle both formats:
          // 1. Direct array: [{ table_name: "...", ... }]
          // 2. Wrapped object: { field_preferences: [{ table_name: "...", ... }] }
          if (parsed.field_preferences && Array.isArray(parsed.field_preferences)) {
            payload.field_preferences = parsed.field_preferences;
          } else if (Array.isArray(parsed)) {
            payload.field_preferences = parsed;
          } else {
            setError('Field preferences must be a JSON array or object with field_preferences array');
            setLoading(false);
            return;
          }

          console.log('✅ Field preferences parsed:', payload.field_preferences);
        } catch (err) {
          setError('Invalid JSON in field preferences: ' + err.message);
          setLoading(false);
          return;
        }
      }

      // V2: Add relationship_pairs if in v2 mode
      if (inputMode === 'relationship_pairs' && relationshipPairsInput.trim()) {
        try {
          payload.relationship_pairs = JSON.parse(relationshipPairsInput);
          console.log('✅ Relationship pairs parsed:', payload.relationship_pairs);
        } catch (err) {
          setError('Invalid JSON in relationship pairs: ' + err.message);
          setLoading(false);
          return;
        }
      }

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

      const response = await generateKG(payload);
      const llmUsed = formData.schema_names.length > 1 && formData.use_llm_enhancement;
      const successMsg = `Knowledge graph "${response.data.kg_name}" created successfully!${
        llmUsed ? ' (LLM enhancement applied)' : ''
      }`;
      setSuccess(successMsg);

      // Reset form
      setFormData({
        ...formData,
        kg_name: '',
        schema_name: '',
        schema_names: [],
      });

      // Reload KGs list
      loadInitialData();
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Unknown error occurred';
      setError(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
      console.error('KG Generation Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadKG = async (kgName) => {
    setLoading(true);
    try {
      const [entitiesRes, relationshipsRes] = await Promise.all([
        getKGEntities(kgName),
        getKGRelationships(kgName),
      ]);

      setSelectedKG(kgName);
      setKgEntities(entitiesRes.data.entities || []);
      setKgRelationships(relationshipsRes.data.relationships || []);
      setTabValue(1);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to load KG';
      setError(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
      console.error('Load KG Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (kgName) => {
    try {
      const response = await exportKG(kgName);
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${kgName}_export.json`;
      a.click();
      setSuccess(`Knowledge graph "${kgName}" exported successfully!`);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    }
  };

  const handleDelete = async (kgName) => {
    if (!window.confirm(`Are you sure you want to delete "${kgName}"?`)) {
      return;
    }

    try {
      await deleteKG(kgName);
      setSuccess(`Knowledge graph "${kgName}" deleted successfully!`);
      loadInitialData();
      if (selectedKG === kgName) {
        setSelectedKG(null);
        setKgEntities([]);
        setKgRelationships([]);
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to delete KG';
      setError(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
      console.error('Delete KG Error:', err);
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
          Knowledge Graph Builder
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Generate and visualize knowledge graphs from database schemas
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {typeof error === 'string' ? error : JSON.stringify(error)}
        </Alert>
      )}

      {success && (
        <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)} sx={{ mb: 3 }}>
        <Tab label="Generate KG" />
        <Tab label="View KG" />
        <Tab label="Manage KGs" />
      </Tabs>

      {/* Tab 1: Generate */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Generate Knowledge Graph
              </Typography>

              <TextField
                fullWidth
                label="Knowledge Graph Name"
                value={formData.kg_name}
                onChange={(e) => setFormData({ ...formData, kg_name: e.target.value })}
                placeholder="e.g., my_knowledge_graph"
                margin="normal"
                required
              />

              <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
                Select Schema(s)
              </Typography>
              <Paper variant="outlined" sx={{ p: 2, maxHeight: 200, overflow: 'auto' }}>
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

              <Box sx={{ mt: 2 }}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formData.use_llm_enhancement}
                      onChange={(e) =>
                        setFormData({ ...formData, use_llm_enhancement: e.target.checked })
                      }
                      disabled={!llmStatus.enabled}
                    />
                  }
                  label="Use LLM Enhancement"
                />
                {!llmStatus.enabled && (
                  <Alert severity="warning" sx={{ mt: 1 }}>
                    LLM service is not enabled. Configure OPENAI_API_KEY in your .env file to use LLM enhancement.
                  </Alert>
                )}
                {llmStatus.enabled && formData.schema_names.length === 1 && (
                  <Alert severity="success" sx={{ mt: 1 }}>
                    LLM enabled: Using {llmStatus.model} for intelligent entity and relationship extraction
                  </Alert>
                )}
                {llmStatus.enabled && formData.schema_names.length > 1 && (
                  <Alert severity="success" sx={{ mt: 1 }}>
                    LLM enabled: Using {llmStatus.model} for cross-schema relationship inference
                  </Alert>
                )}
              </Box>

              {formData.use_llm_enhancement && llmStatus.enabled && (
                <Accordion sx={{ mt: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography>Advanced Options (Optional)</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    {/* Mode Selector */}
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>
                      Relationship Input Mode
                    </Typography>
                    <RadioGroup
                      value={inputMode}
                      onChange={(e) => setInputMode(e.target.value)}
                      sx={{ mb: 2 }}
                    >
                      <FormControlLabel
                        value="field_preferences"
                        control={<Radio />}
                        label="V1: Field Preferences (Table hints - deprecated)"
                      />
                      <FormControlLabel
                        value="relationship_pairs"
                        control={<Radio />}
                        label="V2: Relationship Pairs (Explicit source→target) - Recommended"
                      />
                    </RadioGroup>

                    {/* V1: Field Preferences */}
                    {inputMode === 'field_preferences' && (
                      <Box>
                        <Alert severity="warning" sx={{ mb: 2 }}>
                          <strong>V1 Mode (Deprecated):</strong> Table-centric hints. Consider using V2 for clarity.
                        </Alert>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          Guide LLM inference with specific field hints. Provide JSON array with table-specific preferences.
                        </Typography>
                        <Typography variant="caption" color="info.main" sx={{ mb: 2, display: 'block' }}>
                          💡 Tip: Paste either a JSON array directly or an object with "field_preferences" key. Both formats are supported.
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
                          helperText="Provide field hints to guide LLM relationship inference. Leave empty to let LLM infer automatically."
                        />
                      </Box>
                    )}

                    {/* V2: Relationship Pairs */}
                    {inputMode === 'relationship_pairs' && (
                      <Box>
                        <Alert severity="success" sx={{ mb: 2 }}>
                          <strong>V2 Mode (Recommended):</strong> Explicit source→target pairs stored in KG. No ambiguity!
                        </Alert>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          Define explicit relationships with source→target column precision.
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
                              relationship_type: "MATCHES"
                            }
                          ], null, 2)}
                          value={relationshipPairsInput}
                          onChange={(e) => setRelationshipPairsInput(e.target.value)}
                          helperText="Explicit pairs are added to the Knowledge Graph with clear source→target direction."
                        />
                      </Box>
                    )}
                  </AccordionDetails>
                </Accordion>
              )}

              {/* Excluded Fields Configuration */}
              <Accordion sx={{ mt: 2 }}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="subtitle1">
                    ⛔ Excluded Fields (Optional)
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Alert severity="info" sx={{ mb: 2 }}>
                    <strong>Field Exclusion:</strong> Specify fields to exclude from automatic relationship detection.
                    This prevents certain columns (like "Product_Line", "Business_Unit", etc.) from being used in KG relationships.
                  </Alert>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    Provide a JSON array of field names (case-sensitive) to exclude from relationship creation.
                  </Typography>
                  <TextField
                    fullWidth
                    multiline
                    rows={8}
                    label="Excluded Fields (JSON Array)"
                    placeholder={JSON.stringify([
                      "Product_Line",
                      "product_line",
                      "PRODUCT_LINE",
                      "Business_Unit",
                      "business_unit",
                      "BUSINESS_UNIT",
                      "Product Type",
                      "[Product Type]",
                      "Business Unit",
                      "[Business Unit]"
                    ], null, 2)}
                    value={excludedFieldsInput}
                    onChange={(e) => setExcludedFieldsInput(e.target.value)}
                    helperText="Fields in this list will not be used for automatic relationship detection. Leave empty to use system defaults."
                  />
                </AccordionDetails>
              </Accordion>

              <Box sx={{ mt: 3 }}>
                <Button
                  variant="contained"
                  startIcon={loading ? <CircularProgress size={20} /> : <Add />}
                  onClick={handleGenerate}
                  disabled={loading || !formData.kg_name || formData.schema_names.length === 0}
                  fullWidth
                >
                  Generate Knowledge Graph
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
                    kg_name: formData.kg_name || 'example_kg',
                    schema_names: formData.schema_names.length > 0
                      ? formData.schema_names
                      : ['orderMgmt-catalog', 'qinspect-designcode'],
                    use_llm_enhancement: formData.use_llm_enhancement,
                    backends: formData.backends,
                    // Show field_preferences or relationship_pairs based on mode
                    ...(inputMode === 'field_preferences'
                      ? (fieldPreferencesInput.trim()
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
                      : (relationshipPairsInput.trim()
                          ? { relationship_pairs: (() => { try { return JSON.parse(relationshipPairsInput); } catch { return undefined; } })() }
                          : { relationship_pairs: [
                              {
                                source_table: 'hana_material_master',
                                source_column: 'MATERIAL',
                                target_table: 'brz_lnd_OPS_EXCEL_GPU',
                                target_column: 'PLANNING_SKU',
                                relationship_type: 'MATCHES',
                                confidence: 0.98,
                                bidirectional: true
                              }
                            ] }
                        )
                    )
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
                }}
              >
                {JSON.stringify(
                  {
                    kg_name: 'example_kg',
                    status: 'created',
                    node_count: 58,
                    relationship_count: 47,
                    llm_enhanced: true,
                    schemas_processed: 2,
                    backends: ['falkordb', 'graphiti'],
                  },
                  null,
                  2
                )}
              </Box>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Tab 2: View */}
      {tabValue === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            {selectedKG ? (
              <>
                <Paper sx={{ p: 3, mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Knowledge Graph: {selectedKG}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <Chip label={`${kgEntities.length} Entities`} icon={<Hub />} />
                    <Chip
                      label={`${kgRelationships.length} Relationships`}
                      icon={<AccountTree />}
                    />
                  </Box>

                  {/* Relationship Type Breakdown */}
                  {kgRelationships.length > 0 && (
                    <Box>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Relationship Types:
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {Object.entries(
                          kgRelationships.reduce((acc, rel) => {
                            acc[rel.relationship_type] = (acc[rel.relationship_type] || 0) + 1;
                            return acc;
                          }, {})
                        )
                          .sort((a, b) => b[1] - a[1])
                          .map(([type, count]) => (
                            <Chip
                              key={type}
                              label={`${type} (${count})`}
                              size="small"
                              variant="outlined"
                              color="primary"
                            />
                          ))}
                      </Box>
                    </Box>
                  )}
                </Paper>

                <GraphVisualization entities={kgEntities} relationships={kgRelationships} />

                <Grid container spacing={2} sx={{ mt: 2 }}>
                  <Grid item xs={12} md={6}>
                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Typography>Entities ({kgEntities.length})</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List dense>
                          {kgEntities.slice(0, 50).map((entity, index) => (
                            <ListItem key={index}>
                              <ListItemText
                                primary={entity.label || entity.id}
                                secondary={`Type: ${entity.type || 'N/A'}`}
                              />
                            </ListItem>
                          ))}
                          {kgEntities.length > 50 && (
                            <ListItem>
                              <ListItemText secondary={`... and ${kgEntities.length - 50} more`} />
                            </ListItem>
                          )}
                        </List>
                      </AccordionDetails>
                    </Accordion>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Typography>Relationships ({kgRelationships.length})</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List dense>
                          {kgRelationships.slice(0, 50).map((rel, index) => {
                            // Find entity labels for source and target
                            const sourceEntity = kgEntities.find(e => e.id === rel.source_id);
                            const targetEntity = kgEntities.find(e => e.id === rel.target_id);
                            const sourceName = sourceEntity?.label || rel.source_id;
                            const targetName = targetEntity?.label || rel.target_id;

                            return (
                              <ListItem key={index}>
                                <ListItemText
                                  primary={
                                    <Box component="span" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                      <Typography component="span" variant="body2" fontWeight="medium">
                                        {sourceName}
                                      </Typography>
                                      <Typography component="span" variant="body2" color="text.secondary">
                                        →
                                      </Typography>
                                      <Chip
                                        label={rel.relationship_type}
                                        size="small"
                                        variant="outlined"
                                        sx={{ height: 20, fontSize: '0.7rem' }}
                                      />
                                      <Typography component="span" variant="body2" color="text.secondary">
                                        →
                                      </Typography>
                                      <Typography component="span" variant="body2" fontWeight="medium">
                                        {targetName}
                                      </Typography>
                                    </Box>
                                  }
                                  secondary={
                                    sourceEntity && targetEntity &&
                                    `${sourceEntity.type || 'Unknown'} → ${targetEntity.type || 'Unknown'}`
                                  }
                                />
                              </ListItem>
                            );
                          })}
                          {kgRelationships.length > 50 && (
                            <ListItem>
                              <ListItemText
                                secondary={`... and ${kgRelationships.length - 50} more`}
                              />
                            </ListItem>
                          )}
                        </List>
                      </AccordionDetails>
                    </Accordion>
                  </Grid>
                </Grid>
              </>
            ) : (
              <Alert severity="info">
                Select a knowledge graph from the "Manage KGs" tab to view its details
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

          {knowledgeGraphs.length === 0 ? (
            <Grid item xs={12}>
              <Alert severity="info">
                No knowledge graphs found. Create one using the "Generate KG" tab.
              </Alert>
            </Grid>
          ) : (
            knowledgeGraphs.map((kg) => (
              <Grid item xs={12} md={6} key={kg.name}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {kg.name}
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      {kg.backends?.map((backend) => (
                        <Chip
                          key={backend}
                          label={backend}
                          size="small"
                          sx={{ mr: 0.5 }}
                        />
                      ))}
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      Created: {new Date(kg.created_at).toLocaleString()}
                    </Typography>
                    <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => handleLoadKG(kg.name)}
                      >
                        View
                      </Button>
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<Download />}
                        onClick={() => handleExport(kg.name)}
                      >
                        Export
                      </Button>
                      <Button
                        size="small"
                        variant="outlined"
                        color="error"
                        startIcon={<Delete />}
                        onClick={() => handleDelete(kg.name)}
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
