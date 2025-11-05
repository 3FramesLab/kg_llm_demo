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
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Fade,
  Skeleton,
  Tooltip,
  IconButton,
  Badge,
  Backdrop,
} from '@mui/material';
import {
  Add,
  Refresh,
  Delete,
  Download,
  ExpandMore,
  AccountTree,
  Hub,
  Info,
  CheckCircle,
  Warning,
  AutoAwesome,
  Visibility,
  Person,
  Business,
  LocationOn,
  Category,
  Link,
  Search,
  FilterList,
  ArrowForward,
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
  suggestRelationships,
} from '../services/api';
import KnowledgeGraphEditor from '../components/KnowledgeGraphEditor';


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

  // Relationship pairs input (JSON string)
  const [relationshipPairsInput, setRelationshipPairsInput] = useState('');

  // Excluded fields input (JSON array - list of field names to exclude)
  const [excludedFieldsInput, setExcludedFieldsInput] = useState('');

  // Selected KG details
  const [selectedKG, setSelectedKG] = useState(null);
  const [kgEntities, setKgEntities] = useState([]);
  const [kgRelationships, setKgRelationships] = useState([]);

  // Search and filter state for entities and relationships
  const [entitySearchTerm, setEntitySearchTerm] = useState('');
  const [relationshipSearchTerm, setRelationshipSearchTerm] = useState('');
  const [selectedEntityType, setSelectedEntityType] = useState('all');
  const [selectedRelationType, setSelectedRelationType] = useState('all');
  const [entitiesExpanded, setEntitiesExpanded] = useState(false);
  const [relationshipsExpanded, setRelationshipsExpanded] = useState(false);

  // LLM status
  const [llmStatus, setLlmStatus] = useState({ enabled: false, model: null });

  // LLM relationship suggestions
  const [suggestingRelationships, setSuggestingRelationships] = useState(false);
  const [suggestionSourceTable, setSuggestionSourceTable] = useState('');

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

      // V2: Add relationship_pairs
      if (relationshipPairsInput.trim()) {
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
      const successMsg = `Knowledge graph "${response.data.kg_name}" created successfully!${llmUsed ? ' (LLM enhancement applied)' : ''
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

  const handleSuggestRelationships = async () => {
    if (!suggestionSourceTable.trim()) {
      setError('Please enter a source table name');
      return;
    }

    if (formData.schema_names.length === 0) {
      setError('Please select at least one schema');
      return;
    }

    setSuggestingRelationships(true);
    setError(null);

    try {
      const response = await suggestRelationships({
        source_table: suggestionSourceTable.trim(),
        schema_names: formData.schema_names,
      });

      if (response.data.success && response.data.suggestions && response.data.suggestions.length > 0) {
        // Format suggestions as relationship pairs
        const suggestions = response.data.suggestions.map(sug => ({
          source_table: suggestionSourceTable.trim(),
          source_column: sug.source_column,
          target_table: sug.target_table,
          target_column: sug.target_column,
          relationship_type: sug.relationship_type || 'MATCHES',
          confidence: sug.confidence || 0.9,
          bidirectional: true,
          // Add reasoning as a comment
          _comment: sug.reasoning
        }));

        // Update the relationship pairs input with suggestions
        const currentPairs = relationshipPairsInput.trim() ? JSON.parse(relationshipPairsInput) : [];
        const updatedPairs = [...currentPairs, ...suggestions];
        setRelationshipPairsInput(JSON.stringify(updatedPairs, null, 2));

        setSuccess(`Added ${suggestions.length} relationship suggestions from LLM!`);
      } else {
        setError('No relationship suggestions found. Try a different table or check if schemas are loaded.');
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to get suggestions';
      setError(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
      console.error('Suggest Relationships Error:', err);
    } finally {
      setSuggestingRelationships(false);
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
      {/* Enhanced Header with Gradient */}
      <Box
        sx={{
          mb: 1.5,
          p: 1.5,
          borderRadius: 2,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          boxShadow: '0 3px 15px rgba(102, 126, 234, 0.25)',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <Hub sx={{ fontSize: 28 }} />
          <Box>
            <Typography variant="h5" fontWeight="700" sx={{ mb: 0.25, lineHeight: 1.2, fontSize: '1.15rem' }}>
              Knowledge Graph Builder
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.95, fontWeight: 400, fontSize: '0.8rem' }}>
              Generate and visualize knowledge graphs from database schemas
            </Typography>
          </Box>
        </Box>

        {/* Stats Row */}
        <Box sx={{ display: 'flex', gap: 1.5, mt: 1, flexWrap: 'wrap' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <AccountTree sx={{ fontSize: 16 }} />
            <Box>
              <Typography variant="h6" fontWeight="600" sx={{ lineHeight: 1.2, fontSize: '0.9rem' }}>{knowledgeGraphs.length}</Typography>
              <Typography variant="caption" sx={{ opacity: 0.9, fontSize: '0.65rem' }}>Knowledge Graphs</Typography>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Hub sx={{ fontSize: 16 }} />
            <Box>
              <Typography variant="h6" fontWeight="600" sx={{ lineHeight: 1.2, fontSize: '0.9rem' }}>{schemas.length}</Typography>
              <Typography variant="caption" sx={{ opacity: 0.9, fontSize: '0.65rem' }}>Available Schemas</Typography>
            </Box>
          </Box>
        </Box>
      </Box>

      {/* Alerts with Animation */}
      {error && (
        <Fade in={!!error}>
          <Alert
            severity="error"
            onClose={() => setError(null)}
            sx={{
              mb: 1,
              borderRadius: 1,
              boxShadow: '0 1px 6px rgba(211, 47, 47, 0.15)',
              py: 0.25,
            }}
            icon={<Warning />}
          >
            {typeof error === 'string' ? error : JSON.stringify(error)}
          </Alert>
        </Fade>
      )}

      {success && (
        <Fade in={!!success}>
          <Alert
            severity="success"
            onClose={() => setSuccess(null)}
            sx={{
              mb: 1,
              borderRadius: 1,
              boxShadow: '0 1px 6px rgba(46, 125, 50, 0.15)',
              py: 0.25,
            }}
            icon={<CheckCircle />}
          >
            {success}
          </Alert>
        </Fade>
      )}

      {/* Enhanced Tabs */}
      <Paper
        elevation={0}
        sx={{
          mb: 1.5,
          borderRadius: 1.5,
          overflow: 'hidden',
          border: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Tabs
          value={tabValue}
          onChange={(e, newValue) => setTabValue(newValue)}
          aria-label="Knowledge graph management tabs"
          sx={{
            minHeight: 42,
            '& .MuiTab-root': {
              fontSize: '0.85rem',
              fontWeight: 600,
              textTransform: 'none',
              minHeight: 42,
              py: 0.75,
              transition: 'all 0.3s ease',
              '&:hover': {
                backgroundColor: 'action.hover',
              },
              '&:focus-visible': {
                outline: '3px solid #667eea',
                outlineOffset: '-3px',
              },
            },
            '& .Mui-selected': {
              color: '#667eea',
            },
            '& .MuiTabs-indicator': {
              height: 2.5,
              borderRadius: '2.5px 2.5px 0 0',
              background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
            },
          }}
        >
          <Tab
            label="Generate KG"
            icon={<Add />}
            iconPosition="start"
            aria-label="Generate knowledge graph tab"
            id="tab-0"
            aria-controls="tabpanel-0"
          />
          <Tab
            label="View KG"
            icon={<Visibility />}
            iconPosition="start"
            aria-label="View knowledge graph tab"
            id="tab-1"
            aria-controls="tabpanel-1"
          />
          <Tab
            label="Manage KGs"
            icon={<AccountTree />}
            iconPosition="start"
            aria-label="Manage knowledge graphs tab"
            id="tab-2"
            aria-controls="tabpanel-2"
          />
        </Tabs>
      </Paper>

      {/* Tab 1: Generate */}
      {tabValue === 0 && (
        <Fade in={tabValue === 0}>
          <Grid
            container
            spacing={1.5}
            role="tabpanel"
            id="tabpanel-0"
            aria-labelledby="tab-0"
          >
            {/* Left Side - Main Form */}
            <Grid item xs={12} lg={6}>
              <Paper
                elevation={0}
                sx={{
                  p: 2,
                  borderRadius: 1.5,
                  border: '1px solid',
                  borderColor: 'divider',
                  height: '100%',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    boxShadow: '0 3px 12px rgba(0,0,0,0.08)',
                  },
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
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
                    <Add sx={{ color: 'white', fontSize: 20 }} />
                  </Box>
                  <Typography variant="h6" fontWeight="700" fontSize="0.95rem">
                    Generate Knowledge Graph
                  </Typography>
                </Box>

                <TextField
                  fullWidth
                  label="Knowledge Graph Name"
                  value={formData.kg_name}
                  onChange={(e) => setFormData({ ...formData, kg_name: e.target.value })}
                  placeholder="e.g., my_knowledge_graph"
                  margin="normal"
                  required
                  size="small"
                  inputProps={{
                    'aria-label': 'Knowledge Graph Name',
                    'aria-required': 'true',
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 1.5,
                      fontSize: '0.85rem',
                      '&:hover fieldset': {
                        borderColor: '#667eea',
                      },
                      '&.Mui-focused fieldset': {
                        borderColor: '#667eea',
                      },
                    },
                  }}
                />

                <Box sx={{ mt: 1.5, mb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.75 }}>
                    <Typography variant="body2" fontWeight="600" fontSize="0.8rem">
                      Select Schema(s)
                    </Typography>
                    <Tooltip title="Choose one or more schemas to generate the knowledge graph">
                      <Info sx={{ fontSize: 14, color: 'text.secondary' }} />
                    </Tooltip>
                  </Box>
                  <Paper
                    variant="outlined"
                    component="fieldset"
                    role="group"
                    aria-label="Schema selection"
                    sx={{
                      p: 1.25,
                      maxHeight: 160,
                      overflow: 'auto',
                      borderRadius: 1,
                      bgcolor: 'grey.50',
                      '&::-webkit-scrollbar': {
                        width: '5px',
                      },
                      '&::-webkit-scrollbar-track': {
                        background: '#f1f1f1',
                        borderRadius: '10px',
                      },
                      '&::-webkit-scrollbar-thumb': {
                        background: '#888',
                        borderRadius: '10px',
                        '&:hover': {
                          background: '#555',
                        },
                      },
                    }}
                  >
                    {schemas.length === 0 ? (
                      <Typography color="text.secondary" textAlign="center" py={1.5} fontSize="0.85rem">
                        No schemas available
                      </Typography>
                    ) : (
                      schemas.map((schema) => (
                        <FormControlLabel
                          key={schema}
                          control={
                            <Checkbox
                              checked={formData.schema_names.includes(schema)}
                              onChange={() => handleSchemaToggle(schema)}
                              size="small"
                              sx={{
                                color: '#667eea',
                                '&.Mui-checked': {
                                  color: '#667eea',
                                },
                                py: 0.25,
                              }}
                            />
                          }
                          label={
                            <Typography variant="body2" fontWeight={500} fontSize="0.8rem">
                              {schema}
                            </Typography>
                          }
                          sx={{
                            display: 'flex',
                            width: '100%',
                            m: 0,
                            py: 0.15,
                            px: 0.5,
                            borderRadius: 0.75,
                            transition: 'background-color 0.2s',
                            '&:hover': {
                              bgcolor: 'action.hover',
                            },
                          }}
                        />
                      ))
                    )}
                  </Paper>
                </Box>

                <Box sx={{ mt: 1.5 }}>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 1.25,
                      borderRadius: 1,
                      border: '2px solid',
                      borderColor: llmStatus.enabled ? '#667eea' : 'divider',
                      bgcolor: llmStatus.enabled ? 'rgba(102, 126, 234, 0.05)' : 'grey.50',
                      transition: 'all 0.3s ease',
                    }}
                  >
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={formData.use_llm_enhancement}
                          onChange={(e) =>
                            setFormData({ ...formData, use_llm_enhancement: e.target.checked })
                          }
                          disabled={!llmStatus.enabled}
                          size="small"
                          sx={{
                            color: '#667eea',
                            '&.Mui-checked': {
                              color: '#667eea',
                            },
                          }}
                        />
                      }
                      label={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <AutoAwesome sx={{ fontSize: 16, color: llmStatus.enabled ? '#667eea' : 'text.disabled' }} />
                          <Typography variant="body2" fontWeight={600} fontSize="0.8rem">
                            Use AI Enhancement
                          </Typography>
                        </Box>
                      }
                    />
                    {!llmStatus.enabled && (
                      <Alert
                        severity="warning"
                        sx={{
                          mt: 1,
                          borderRadius: 0.75,
                          py: 0.25,
                          '& .MuiAlert-icon': {
                            fontSize: 18,
                          },
                        }}
                      >
                        <Typography variant="body2" fontWeight={500} fontSize="0.8rem">
                          LLM service is not enabled
                        </Typography>
                        <Typography variant="caption" color="text.secondary" fontSize="0.65rem">
                          Configure OPENAI_API_KEY in your .env file to use AI enhancement.
                        </Typography>
                      </Alert>
                    )}

                  </Paper>
                </Box>

                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    size="small"
                    startIcon={loading ? <CircularProgress size={16} color="inherit" /> : <Add sx={{ fontSize: 18 }} />}
                    onClick={handleGenerate}
                    disabled={loading || !formData.kg_name || formData.schema_names.length === 0}
                    fullWidth
                    aria-label={loading ? 'Generating knowledge graph' : 'Generate knowledge graph'}
                    sx={{
                      py: 0.9,
                      borderRadius: 1,
                      fontSize: '0.85rem',
                      fontWeight: 700,
                      textTransform: 'none',
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      boxShadow: '0 2px 10px rgba(102, 126, 234, 0.35)',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #5568d3 0%, #653a8b 100%)',
                        boxShadow: '0 3px 12px rgba(102, 126, 234, 0.45)',
                        transform: 'translateY(-1px)',
                      },
                      '&:disabled': {
                        background: 'linear-gradient(135deg, #ccc 0%, #999 100%)',
                        boxShadow: 'none',
                      },
                      '&:focus-visible': {
                        outline: '3px solid #667eea',
                        outlineOffset: '2px',
                      },
                    }}
                  >
                    {loading ? 'Generating...' : 'Generate Knowledge Graph'}
                  </Button>
                </Box>
              </Paper>
            </Grid>

            {/* Right Side - Advanced Options and Excluded Fields */}
            <Grid item xs={12} lg={6}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                {/* Advanced Options - Relationship Pairs */}
                {formData.use_llm_enhancement && llmStatus.enabled && (
                  <Accordion
                    sx={{
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
                        minHeight: 48,
                        '&.Mui-expanded': {
                          minHeight: 48,
                        },
                        '& .MuiAccordionSummary-content': {
                          my: 1,
                        },
                        '&:hover': {
                          bgcolor: 'action.hover',
                        },
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
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
                          <Info sx={{ color: 'white', fontSize: 20 }} />
                        </Box>
                        <Typography variant="h6" fontWeight="700" fontSize="0.95rem">
                          Advanced Options (Optional)
                        </Typography>
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails sx={{ pt: 0, pb: 2 }}>
                      <Alert severity="info" sx={{ mb: 2 }}>
                        <strong>Relationship Pairs:</strong> Define explicit source→target pairs stored in KG with no ambiguity.
                      </Alert>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        Define explicit relationships with source→target column precision.
                      </Typography>

                      {/* LLM Relationship Suggestions */}
                      {llmStatus.enabled && (
                        <Box sx={{ mb: 2, p: 2, bgcolor: 'background.default', borderRadius: 1, border: '1px solid', borderColor: 'divider' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <AutoAwesome sx={{ fontSize: 18, color: 'primary.main' }} />
                            <Typography variant="subtitle2" fontWeight={600}>
                              LLM-Powered Relationship Suggestions
                            </Typography>
                          </Box>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            Let AI suggest relationships for a table based on column name analysis.
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <TextField
                              size="small"
                              label="Source Table Name"
                              placeholder="e.g., brz_lnd_RBP_GPU"
                              value={suggestionSourceTable}
                              onChange={(e) => setSuggestionSourceTable(e.target.value)}
                              disabled={suggestingRelationships}
                              sx={{ flex: 1 }}
                            />
                            <Button
                              variant="contained"
                              startIcon={suggestingRelationships ? <CircularProgress size={16} /> : <AutoAwesome />}
                              onClick={handleSuggestRelationships}
                              disabled={suggestingRelationships || !suggestionSourceTable.trim() || formData.schema_names.length === 0}
                            >
                              {suggestingRelationships ? 'Suggesting...' : 'Suggest'}
                            </Button>
                          </Box>
                          {formData.schema_names.length === 0 && (
                            <Typography variant="caption" color="warning.main" sx={{ mt: 1, display: 'block' }}>
                              ⚠️ Please select schemas above before using suggestions
                            </Typography>
                          )}
                        </Box>
                      )}

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
                    </AccordionDetails>
                  </Accordion>
                )}

                {/* Excluded Fields Configuration */}
                <Accordion
                  sx={{
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
                      minHeight: 48,
                      '&.Mui-expanded': {
                        minHeight: 48,
                      },
                      '& .MuiAccordionSummary-content': {
                        my: 1,
                      },
                      '&:hover': {
                        bgcolor: 'action.hover',
                      },
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box
                        sx={{
                          p: 0.75,
                          borderRadius: 1,
                          background: 'linear-gradient(135deg, #ff9800 0%, #f57c00 100%)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}
                      >
                        <Warning sx={{ color: 'white', fontSize: 20 }} />
                      </Box>
                      <Typography variant="h6" fontWeight="700" fontSize="0.95rem">
                        Excluded Fields (Optional)
                      </Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails sx={{ pt: 0, pb: 2 }}>
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
              </Box>
            </Grid>
          </Grid>
        </Fade>
      )}

      {/* Tab 2: View */}
      {tabValue === 1 && (
        <Fade in={tabValue === 1}>
          <Grid
            container
            spacing={1.5}
            role="tabpanel"
            id="tabpanel-1"
            aria-labelledby="tab-1"
          >
            <Grid item xs={12}>


              {selectedKG ? (
                <>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 2.5,
                      mb: 2,
                      borderRadius: 2,
                      border: '1px solid',
                      borderColor: 'divider',
                      background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)',
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, flexWrap: 'wrap', gap: 1.5 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
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
                          <Hub sx={{ color: 'white', fontSize: 22 }} />
                        </Box>
                        <Box>
                          <Typography variant="h6" fontWeight="700">
                            {selectedKG}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" fontSize="0.8rem">
                            Knowledge Graph Visualization
                          </Typography>
                        </Box>
                      </Box>
                      {selectedKG === 'Sample Knowledge Graph' && (
                        <Chip
                          label="Sample Data"
                          color="info"
                          icon={<Info />}
                          size="small"
                          sx={{
                            fontWeight: 600,
                            fontSize: '0.65rem',
                            height: 20,
                          }}
                        />
                      )}
                    </Box>
                    <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
                      <Chip
                        label={`${kgEntities.length} Entities`}
                        icon={<Hub />}
                        sx={{
                          bgcolor: 'rgba(102, 126, 234, 0.1)',
                          color: '#667eea',
                          fontWeight: 600,
                          fontSize: '0.95rem',
                          px: 1,
                          '& .MuiChip-icon': {
                            color: '#667eea',
                          },
                        }}
                      />
                      <Chip
                        label={`${kgRelationships.length} Relationships`}
                        icon={<AccountTree />}
                        sx={{
                          bgcolor: 'rgba(118, 75, 162, 0.1)',
                          color: '#764ba2',
                          fontWeight: 600,
                          fontSize: '0.95rem',
                          px: 1,
                          '& .MuiChip-icon': {
                            color: '#764ba2',
                          },
                        }}
                      />
                    </Box>

                    {/* Relationship Type Breakdown */}

                  </Paper>

                  {/* Force-Directed Graph Visualization */}
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      borderRadius: 3,
                      mb: 3,
                      border: '1px solid',
                      borderColor: 'divider',
                      boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                      <Box
                        sx={{
                          p: 1.5,
                          borderRadius: 2,
                          bgcolor: 'primary.light',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}
                      >
                        <AccountTree sx={{ color: 'primary.dark', fontSize: 28 }} />
                      </Box>
                      <Typography variant="h5" fontWeight="700">
                        Graph Visualization
                      </Typography>
                    </Box>
                    <KnowledgeGraphEditor entities={kgEntities} relationships={kgRelationships} />
                  </Paper>

                  {/* Enhanced Entities and Relationships Accordions */}
                  <Grid container spacing={1.5} sx={{ mt: 1.5 }}>
                    {/* Entities Accordion */}
                    <Grid item xs={12} md={6}>
                      <Accordion
                        expanded={entitiesExpanded}
                        onChange={(e, isExpanded) => setEntitiesExpanded(isExpanded)}
                        elevation={0}
                        sx={{
                          border: '2px solid',
                          borderColor: 'divider',
                          borderRadius: 1.5,
                          '&:before': { display: 'none' },
                          overflow: 'hidden',
                        }}
                      >
                        <AccordionSummary
                          expandIcon={<ExpandMore />}
                          sx={{
                            minHeight: 48,
                            bgcolor: 'linear-gradient(135deg, #667eea15 0%, #764ba215 100%)',
                            borderBottom: entitiesExpanded ? '1px solid' : 'none',
                            borderColor: 'divider',
                            '&:hover': {
                              bgcolor: 'action.hover',
                            },
                            '& .MuiAccordionSummary-content': {
                              my: 1,
                            },
                          }}
                        >
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                            <Box
                              sx={{
                                p: 0.75,
                                borderRadius: 1,
                                bgcolor: 'primary.main',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                              }}
                            >
                              <Hub sx={{ color: 'white', fontSize: 18 }} />
                            </Box>
                            <Typography variant="body1" fontWeight={700} fontSize="0.9rem">
                              Entities
                            </Typography>
                            <Badge
                              badgeContent={kgEntities.length}
                              color="primary"
                              sx={{
                                ml: 'auto',
                                '& .MuiBadge-badge': {
                                  fontSize: '0.7rem',
                                  height: 20,
                                  minWidth: 20,
                                  fontWeight: 700,
                                },
                              }}
                            />
                          </Box>
                        </AccordionSummary>
                        <AccordionDetails sx={{ p: 0 }}>
                          {/* Search and Filter Controls */}
                          <Box sx={{ p: 1.5, bgcolor: 'grey.50', borderBottom: '1px solid', borderColor: 'divider' }}>
                            <TextField
                              fullWidth
                              size="small"
                              placeholder="Search entities..."
                              value={entitySearchTerm}
                              onChange={(e) => setEntitySearchTerm(e.target.value)}
                              InputProps={{
                                startAdornment: <Search sx={{ fontSize: 18, mr: 0.75, color: 'text.secondary' }} />,
                              }}
                              sx={{
                                mb: 1,
                                '& .MuiOutlinedInput-root': {
                                  fontSize: '0.8rem',
                                  bgcolor: 'white',
                                },
                              }}
                            />
                            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', alignItems: 'center' }}>
                              <FilterList sx={{ fontSize: 16, color: 'text.secondary' }} />
                              <Chip
                                label="All"
                                size="small"
                                onClick={() => setSelectedEntityType('all')}
                                color={selectedEntityType === 'all' ? 'primary' : 'default'}
                                sx={{ fontSize: '0.7rem', height: 22, fontWeight: 600 }}
                              />
                              {[...new Set(kgEntities.map(e => e.type || 'Unknown'))].sort().map(type => (
                                <Chip
                                  key={type}
                                  label={type}
                                  size="small"
                                  onClick={() => setSelectedEntityType(type)}
                                  color={selectedEntityType === type ? 'primary' : 'default'}
                                  sx={{ fontSize: '0.7rem', height: 22 }}
                                />
                              ))}
                            </Box>
                          </Box>

                          {/* Entities List */}
                          <List dense sx={{ maxHeight: 400, overflow: 'auto', p: 0 }}>
                            {kgEntities
                              .filter(entity => {
                                const matchesSearch = !entitySearchTerm ||
                                  (entity.label || entity.id).toLowerCase().includes(entitySearchTerm.toLowerCase()) ||
                                  (entity.type || '').toLowerCase().includes(entitySearchTerm.toLowerCase());
                                const matchesType = selectedEntityType === 'all' || entity.type === selectedEntityType;
                                return matchesSearch && matchesType;
                              })
                              .map((entity, index) => {
                                const typeColors = {
                                  'Person': '#764ba2',
                                  'Company': '#667eea',
                                  'Organization': '#f093fb',
                                  'Location': '#4facfe',
                                  'Product': '#43e97b',
                                  'Project': '#43e97b',
                                  'Skill': '#fa709a',
                                  'Order': '#fa709a',
                                  'Supplier': '#30cfd0',
                                  'Warehouse': '#a8edea',
                                  'Category': '#fed6e3',
                                };
                                const typeColor = typeColors[entity.type] || '#999999';

                                return (
                                  <ListItem
                                    key={index}
                                    sx={{
                                      py: 1,
                                      px: 1.5,
                                      borderBottom: '1px solid',
                                      borderColor: 'divider',
                                      '&:hover': {
                                        bgcolor: 'action.hover',
                                        cursor: 'pointer',
                                      },
                                      '&:last-child': {
                                        borderBottom: 'none',
                                      },
                                    }}
                                  >
                                    <Box
                                      sx={{
                                        width: 8,
                                        height: 8,
                                        borderRadius: '50%',
                                        bgcolor: typeColor,
                                        mr: 1.5,
                                        flexShrink: 0,
                                      }}
                                    />
                                    <ListItemText
                                      primary={
                                        <Typography variant="body2" fontWeight={600} fontSize="0.85rem">
                                          {entity.label || entity.id}
                                        </Typography>
                                      }
                                      secondary={
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.25 }}>
                                          <Chip
                                            label={entity.type || 'Unknown'}
                                            size="small"
                                            sx={{
                                              height: 18,
                                              fontSize: '0.65rem',
                                              bgcolor: typeColor + '20',
                                              color: typeColor,
                                              fontWeight: 600,
                                              border: `1px solid ${typeColor}40`,
                                            }}
                                          />
                                          {entity.id && (
                                            <Typography variant="caption" color="text.secondary" fontSize="0.7rem">
                                              ID: {entity.id.length > 20 ? entity.id.substring(0, 20) + '...' : entity.id}
                                            </Typography>
                                          )}
                                        </Box>
                                      }
                                    />
                                  </ListItem>
                                );
                              })}
                            {kgEntities.filter(entity => {
                              const matchesSearch = !entitySearchTerm ||
                                (entity.label || entity.id).toLowerCase().includes(entitySearchTerm.toLowerCase()) ||
                                (entity.type || '').toLowerCase().includes(entitySearchTerm.toLowerCase());
                              const matchesType = selectedEntityType === 'all' || entity.type === selectedEntityType;
                              return matchesSearch && matchesType;
                            }).length === 0 && (
                                <ListItem>
                                  <ListItemText
                                    primary={
                                      <Typography variant="body2" color="text.secondary" textAlign="center" fontSize="0.8rem">
                                        No entities found
                                      </Typography>
                                    }
                                  />
                                </ListItem>
                              )}
                          </List>
                        </AccordionDetails>
                      </Accordion>
                    </Grid>

                    {/* Relationships Accordion */}
                    <Grid item xs={12} md={6}>
                      <Accordion
                        expanded={relationshipsExpanded}
                        onChange={(e, isExpanded) => setRelationshipsExpanded(isExpanded)}
                        elevation={0}
                        sx={{
                          border: '2px solid',
                          borderColor: 'divider',
                          borderRadius: 1.5,
                          '&:before': { display: 'none' },
                          overflow: 'hidden',
                        }}
                      >
                        <AccordionSummary
                          expandIcon={<ExpandMore />}
                          sx={{
                            minHeight: 48,
                            bgcolor: 'linear-gradient(135deg, #43e97b15 0%, #38f9d715 100%)',
                            borderBottom: relationshipsExpanded ? '1px solid' : 'none',
                            borderColor: 'divider',
                            '&:hover': {
                              bgcolor: 'action.hover',
                            },
                            '& .MuiAccordionSummary-content': {
                              my: 1,
                            },
                          }}
                        >
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                            <Box
                              sx={{
                                p: 0.75,
                                borderRadius: 1,
                                bgcolor: 'success.main',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                              }}
                            >
                              <AccountTree sx={{ color: 'white', fontSize: 18 }} />
                            </Box>
                            <Typography variant="body1" fontWeight={700} fontSize="0.9rem">
                              Relationships
                            </Typography>
                            <Badge
                              badgeContent={kgRelationships.length}
                              color="success"
                              sx={{
                                ml: 'auto',
                                '& .MuiBadge-badge': {
                                  fontSize: '0.7rem',
                                  height: 20,
                                  minWidth: 20,
                                  fontWeight: 700,
                                },
                              }}
                            />
                          </Box>
                        </AccordionSummary>
                        <AccordionDetails sx={{ p: 0 }}>
                          {/* Search and Filter Controls */}
                          <Box sx={{ p: 1.5, bgcolor: 'grey.50', borderBottom: '1px solid', borderColor: 'divider' }}>
                            <TextField
                              fullWidth
                              size="small"
                              placeholder="Search relationships..."
                              value={relationshipSearchTerm}
                              onChange={(e) => setRelationshipSearchTerm(e.target.value)}
                              InputProps={{
                                startAdornment: <Search sx={{ fontSize: 18, mr: 0.75, color: 'text.secondary' }} />,
                              }}
                              sx={{
                                mb: 1,
                                '& .MuiOutlinedInput-root': {
                                  fontSize: '0.8rem',
                                  bgcolor: 'white',
                                },
                              }}
                            />
                            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', alignItems: 'center' }}>
                              <FilterList sx={{ fontSize: 16, color: 'text.secondary' }} />
                              <Chip
                                label="All"
                                size="small"
                                onClick={() => setSelectedRelationType('all')}
                                color={selectedRelationType === 'all' ? 'success' : 'default'}
                                sx={{ fontSize: '0.7rem', height: 22, fontWeight: 600 }}
                              />
                              {[...new Set(kgRelationships.map(r => r.relationship_type))].sort().map(type => (
                                <Chip
                                  key={type}
                                  label={type}
                                  size="small"
                                  onClick={() => setSelectedRelationType(type)}
                                  color={selectedRelationType === type ? 'success' : 'default'}
                                  sx={{ fontSize: '0.7rem', height: 22 }}
                                />
                              ))}
                            </Box>
                          </Box>

                          {/* Relationships List */}
                          <List dense sx={{ maxHeight: 400, overflow: 'auto', p: 0 }}>
                            {kgRelationships
                              .filter(rel => {
                                const sourceEntity = kgEntities.find(e => e.id === rel.source_id);
                                const targetEntity = kgEntities.find(e => e.id === rel.target_id);
                                const sourceName = sourceEntity?.label || rel.source_id;
                                const targetName = targetEntity?.label || rel.target_id;

                                const matchesSearch = !relationshipSearchTerm ||
                                  sourceName.toLowerCase().includes(relationshipSearchTerm.toLowerCase()) ||
                                  targetName.toLowerCase().includes(relationshipSearchTerm.toLowerCase()) ||
                                  rel.relationship_type.toLowerCase().includes(relationshipSearchTerm.toLowerCase());
                                const matchesType = selectedRelationType === 'all' || rel.relationship_type === selectedRelationType;
                                return matchesSearch && matchesType;
                              })
                              .map((rel, index) => {
                                const sourceEntity = kgEntities.find(e => e.id === rel.source_id);
                                const targetEntity = kgEntities.find(e => e.id === rel.target_id);
                                const sourceName = sourceEntity?.label || rel.source_id;
                                const targetName = targetEntity?.label || rel.target_id;

                                const relationshipColors = {
                                  'WORKS_AT': '#667eea',
                                  'LEADS': '#764ba2',
                                  'CONTRIBUTES_TO': '#43e97b',
                                  'HAS_SKILL': '#fa709a',
                                  'SPONSORS': '#30cfd0',
                                  'MANAGES': '#f093fb',
                                  'REPORTS_TO': '#4facfe',
                                };
                                const relColor = relationshipColors[rel.relationship_type] || '#999999';

                                return (
                                  <ListItem
                                    key={index}
                                    sx={{
                                      py: 1,
                                      px: 1.5,
                                      borderBottom: '1px solid',
                                      borderColor: 'divider',
                                      '&:hover': {
                                        bgcolor: 'action.hover',
                                        cursor: 'pointer',
                                      },
                                      '&:last-child': {
                                        borderBottom: 'none',
                                      },
                                    }}
                                  >
                                    <ListItemText
                                      primary={
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75, flexWrap: 'wrap' }}>
                                          <Typography variant="body2" fontWeight={600} fontSize="0.8rem" sx={{ color: 'text.primary' }}>
                                            {sourceName}
                                          </Typography>
                                          <ArrowForward sx={{ fontSize: 14, color: relColor }} />
                                          <Chip
                                            label={rel.relationship_type}
                                            size="small"
                                            sx={{
                                              height: 20,
                                              fontSize: '0.65rem',
                                              bgcolor: relColor + '20',
                                              color: relColor,
                                              fontWeight: 700,
                                              border: `1px solid ${relColor}40`,
                                            }}
                                          />
                                          <ArrowForward sx={{ fontSize: 14, color: relColor }} />
                                          <Typography variant="body2" fontWeight={600} fontSize="0.8rem" sx={{ color: 'text.primary' }}>
                                            {targetName}
                                          </Typography>
                                        </Box>
                                      }
                                      secondary={
                                        sourceEntity && targetEntity && (
                                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
                                            <Chip
                                              label={sourceEntity.type || 'Unknown'}
                                              size="small"
                                              sx={{
                                                height: 16,
                                                fontSize: '0.6rem',
                                                bgcolor: 'grey.200',
                                                color: 'text.secondary',
                                              }}
                                            />
                                            <Typography variant="caption" color="text.secondary" fontSize="0.65rem">
                                              →
                                            </Typography>
                                            <Chip
                                              label={targetEntity.type || 'Unknown'}
                                              size="small"
                                              sx={{
                                                height: 16,
                                                fontSize: '0.6rem',
                                                bgcolor: 'grey.200',
                                                color: 'text.secondary',
                                              }}
                                            />
                                          </Box>
                                        )
                                      }
                                    />
                                  </ListItem>
                                );
                              })}
                            {kgRelationships.filter(rel => {
                              const sourceEntity = kgEntities.find(e => e.id === rel.source_id);
                              const targetEntity = kgEntities.find(e => e.id === rel.target_id);
                              const sourceName = sourceEntity?.label || rel.source_id;
                              const targetName = targetEntity?.label || rel.target_id;

                              const matchesSearch = !relationshipSearchTerm ||
                                sourceName.toLowerCase().includes(relationshipSearchTerm.toLowerCase()) ||
                                targetName.toLowerCase().includes(relationshipSearchTerm.toLowerCase()) ||
                                rel.relationship_type.toLowerCase().includes(relationshipSearchTerm.toLowerCase());
                              const matchesType = selectedRelationType === 'all' || rel.relationship_type === selectedRelationType;
                              return matchesSearch && matchesType;
                            }).length === 0 && (
                                <ListItem>
                                  <ListItemText
                                    primary={
                                      <Typography variant="body2" color="text.secondary" textAlign="center" fontSize="0.8rem">
                                        No relationships found
                                      </Typography>
                                    }
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
                <Paper
                  elevation={0}
                  sx={{
                    p: 4,
                    borderRadius: 2,
                    border: '2px dashed',
                    borderColor: 'divider',
                    textAlign: 'center',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minHeight: 400,
                  }}
                >
                  <Box
                    sx={{
                      display: 'inline-flex',
                      p: 2,
                      borderRadius: '50%',
                      bgcolor: 'action.hover',
                      mb: 2,
                    }}
                  >
                    <AccountTree sx={{ fontSize: 48, color: 'text.secondary' }} />
                  </Box>
                  <Typography variant="h6" fontWeight="700" gutterBottom sx={{ mb: 1 }}>
                    No Knowledge Graph Selected
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3, maxWidth: 400 }}>
                    Select a knowledge graph from the "Manage KGs" tab to view its details, or create a new one using the "Generate KG" tab.
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', justifyContent: 'center' }}>
                    <Button
                      variant="outlined"
                      startIcon={<Add sx={{ fontSize: 18 }} />}
                      onClick={() => setTabValue(0)}
                      sx={{
                        borderRadius: 1,
                        textTransform: 'none',
                        fontWeight: 600,
                      }}
                    >
                      Generate KG
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<Visibility sx={{ fontSize: 18 }} />}
                      onClick={() => setTabValue(2)}
                      sx={{
                        borderRadius: 1,
                        textTransform: 'none',
                        fontWeight: 600,
                      }}
                    >
                      Manage KGs
                    </Button>
                  </Box>
                </Paper>
              )}
            </Grid>
          </Grid>
        </Fade>
      )}

      {/* Tab 3: Manage */}
      {tabValue === 2 && (
        <Fade in={tabValue === 2}>
          <Grid
            container
            spacing={1.5}
            role="tabpanel"
            id="tabpanel-2"
            aria-labelledby="tab-2"
          >
            <Grid item xs={12}>
              <Box sx={{ mb: 1.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 1 }}>
                <Box>
                  <Typography variant="h6" fontWeight="700" gutterBottom sx={{ mb: 0.25, fontSize: '0.95rem' }}>
                    Manage Knowledge Graphs
                  </Typography>
                  <Typography variant="body2" color="text.secondary" fontSize="0.75rem">
                    View, export, and manage your knowledge graphs
                  </Typography>
                </Box>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<Refresh sx={{ fontSize: 18 }} />}
                  onClick={loadInitialData}
                  sx={{
                    borderRadius: 1,
                    textTransform: 'none',
                    fontWeight: 600,
                    fontSize: '0.8rem',
                    borderWidth: 2,
                    py: 0.5,
                    '&:hover': {
                      borderWidth: 2,
                    },
                  }}
                >
                  Refresh List
                </Button>
              </Box>
            </Grid>

            {knowledgeGraphs.length === 0 ? (
              <Grid item xs={12}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 3,
                    borderRadius: 1.5,
                    border: '2px dashed',
                    borderColor: 'divider',
                    textAlign: 'center',
                  }}
                >
                  <Box
                    sx={{
                      display: 'inline-flex',
                      p: 1.5,
                      borderRadius: '50%',
                      bgcolor: 'action.hover',
                      mb: 1,
                    }}
                  >
                    <AccountTree sx={{ fontSize: 36, color: 'text.secondary' }} />
                  </Box>
                  <Typography variant="body2" fontWeight="600" gutterBottom fontSize="0.85rem">
                    No Knowledge Graphs Found
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ mb: 1.5 }} fontSize="0.75rem">
                    Create your first knowledge graph using the "Generate KG" tab.
                  </Typography>
                  <Button
                    variant="contained"
                    size="small"
                    startIcon={<Add sx={{ fontSize: 18 }} />}
                    onClick={() => setTabValue(0)}
                    sx={{
                      borderRadius: 1,
                      fontSize: '0.8rem',
                      textTransform: 'none',
                      fontWeight: 600,
                      fontSize: '0.9rem',
                      px: 3,
                      py: 0.75,
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      boxShadow: '0 3px 12px rgba(102, 126, 234, 0.35)',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #5568d3 0%, #653a8b 100%)',
                      },
                    }}
                  >
                    Create Knowledge Graph
                  </Button>
                </Paper>
              </Grid>
            ) : (
              knowledgeGraphs.map((kg) => (
                <Grid item xs={12} md={6} lg={4} key={kg.name}>
                  <Card
                    elevation={0}
                    sx={{
                      height: '100%',
                      borderRadius: 1.5,
                      border: '1px solid',
                      borderColor: 'divider',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        boxShadow: '0 4px 16px rgba(0,0,0,0.12)',
                        transform: 'translateY(-2px)',
                        borderColor: 'primary.main',
                      },
                    }}
                  >
                    <CardContent sx={{ p: 1.5 }}>
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 1 }}>
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
                          <Hub sx={{ color: 'white', fontSize: 18 }} />
                        </Box>
                        <Box sx={{ flex: 1, minWidth: 0 }}>
                          <Typography variant="body2" fontWeight="700" gutterBottom noWrap fontSize="0.85rem" sx={{ mb: 0.25 }}>
                            {kg.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary" fontSize="0.65rem">
                            {kg.created_at ? new Date(kg.created_at).toLocaleString('en-US', {
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                              timeZoneName: 'short'
                            }) : 'Unknown date'}
                          </Typography>
                        </Box>
                      </Box>

                      <Box sx={{ mb: 1.5, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {kg.backends?.map((backend) => (
                          <Chip
                            key={backend}
                            label={backend}
                            size="small"
                            sx={{
                              fontWeight: 600,
                              fontSize: '0.65rem',
                              height: 20,
                              bgcolor: 'rgba(102, 126, 234, 0.1)',
                              color: '#667eea',
                              borderRadius: 0.75,
                            }}
                          />
                        ))}
                      </Box>

                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                        <Button
                          fullWidth
                          variant="contained"
                          size="small"
                          startIcon={<Visibility sx={{ fontSize: 16 }} />}
                          onClick={() => handleLoadKG(kg.name)}
                          sx={{
                            borderRadius: 1.5,
                            textTransform: 'none',
                            fontWeight: 600,
                            fontSize: '0.85rem',
                            py: 0.6,
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            '&:hover': {
                              background: 'linear-gradient(135deg, #5568d3 0%, #653a8b 100%)',
                            },
                          }}
                        >
                          View Graph
                        </Button>
                        <Box sx={{ display: 'flex', gap: 0.75 }}>
                          <Button
                            fullWidth
                            size="small"
                            variant="outlined"
                            startIcon={<Download sx={{ fontSize: 16 }} />}
                            onClick={() => handleExport(kg.name)}
                            sx={{
                              borderRadius: 1.5,
                              textTransform: 'none',
                              fontWeight: 600,
                              fontSize: '0.8rem',
                              py: 0.5,
                            }}
                          >
                            Export
                          </Button>
                          <Button
                            fullWidth
                            size="small"
                            variant="outlined"
                            color="error"
                            startIcon={<Delete sx={{ fontSize: 16 }} />}
                            onClick={() => handleDelete(kg.name)}
                            sx={{
                              borderRadius: 1.5,
                              textTransform: 'none',
                              fontWeight: 600,
                              fontSize: '0.8rem',
                              py: 0.5,
                            }}
                          >
                            Delete
                          </Button>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))
            )}
          </Grid>
        </Fade>
      )}

      {/* Overlay Loader */}
      <Backdrop
        sx={{
          color: '#fff',
          zIndex: (theme) => theme.zIndex.drawer + 1,
          backdropFilter: 'blur(4px)',
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
        }}
        open={loading}
      >
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 2,
          }}
        >
          <CircularProgress
            size={60}
            thickness={4}
            sx={{
              color: '#667eea',
            }}
          />
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h6" fontWeight="600" sx={{ mb: 0.5 }}>
              Generating Knowledge Graph...
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9 }}>
              This may take a few moments
            </Typography>
          </Box>
        </Box>
      </Backdrop>
    </Container>
  );
}
