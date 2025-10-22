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
import {
  generateKG,
  listKGs,
  listSchemas,
  getKGEntities,
  getKGRelationships,
  exportKG,
  deleteKG,
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
  });

  // Selected KG details
  const [selectedKG, setSelectedKG] = useState(null);
  const [kgEntities, setKgEntities] = useState([]);
  const [kgRelationships, setKgRelationships] = useState([]);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [schemasRes, kgsRes] = await Promise.all([
        listSchemas(),
        listKGs(),
      ]);
      setSchemas(schemasRes.data.schemas || []);
      setKnowledgeGraphs(kgsRes.data.graphs || []);
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

      const response = await generateKG(payload);
      setSuccess(`Knowledge graph "${response.data.kg_name}" created successfully!`);

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
      setError(err.response?.data?.detail || err.message);
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
      setError(err.response?.data?.detail || err.message);
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
          Knowledge Graph Builder
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Generate and visualize knowledge graphs from database schemas
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

              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.use_llm_enhancement}
                    onChange={(e) =>
                      setFormData({ ...formData, use_llm_enhancement: e.target.checked })
                    }
                  />
                }
                label="Use LLM Enhancement (Recommended)"
                sx={{ mt: 2 }}
              />

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
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Chip label={`${kgEntities.length} Entities`} icon={<Hub />} />
                    <Chip
                      label={`${kgRelationships.length} Relationships`}
                      icon={<AccountTree />}
                    />
                  </Box>
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
                          {kgRelationships.slice(0, 50).map((rel, index) => (
                            <ListItem key={index}>
                              <ListItemText
                                primary={`${rel.source_id} → ${rel.target_id}`}
                                secondary={`Type: ${rel.relationship_type}`}
                              />
                            </ListItem>
                          ))}
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
