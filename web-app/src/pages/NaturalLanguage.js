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
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Slider,
} from '@mui/material';
import { Add, Delete, Send } from '@mui/icons-material';
import { parseNLRelationships, listSchemas, listKGs } from '../services/api';

export default function NaturalLanguage() {
  const [schemas, setSchemas] = useState([]);
  const [kgs, setKgs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    kg_name: '',
    schemas: [],
    definitions: [''],
    use_llm: true,
    min_confidence: 0.7,
  });

  const [results, setResults] = useState(null);

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

    try {
      const payload = {
        kg_name: formData.kg_name,
        schemas: formData.schemas,
        definitions: formData.definitions.filter((def) => def.trim() !== ''),
        use_llm: formData.use_llm,
        min_confidence: formData.min_confidence,
      };

      const response = await parseNLRelationships(payload);
      setResults(response.data);
      setSuccess(
        `Parsed ${response.data.parsed_count} definitions. ${response.data.valid_count} valid, ${response.data.invalid_count} invalid.`
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
          Natural Language Relationships
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Define relationships between schemas using plain English
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

            <Button
              variant="contained"
              startIcon={loading ? <CircularProgress size={20} /> : <Send />}
              onClick={handleSubmit}
              disabled={
                loading ||
                !formData.kg_name ||
                formData.schemas.length === 0 ||
                formData.definitions.filter((d) => d.trim()).length === 0
              }
              fullWidth
            >
              Parse Relationships
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
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Parsing Results
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Chip
                  label={`${results.parsed_count} Parsed`}
                  color="primary"
                  sx={{ mr: 1 }}
                />
                <Chip
                  label={`${results.valid_count} Valid`}
                  color="success"
                  sx={{ mr: 1 }}
                />
                <Chip label={`${results.invalid_count} Invalid`} color="error" />
              </Box>

              <Divider sx={{ my: 2 }} />

              <List>
                {results.relationships?.map((rel, index) => (
                  <ListItem
                    key={index}
                    divider={index < results.relationships.length - 1}
                    sx={{
                      flexDirection: 'column',
                      alignItems: 'flex-start',
                      bgcolor:
                        rel.status === 'valid' ? 'success.light' : 'error.light',
                      borderRadius: 1,
                      mb: 1,
                    }}
                  >
                    <Box sx={{ width: '100%', mb: 1 }}>
                      <Chip
                        label={rel.status}
                        size="small"
                        color={rel.status === 'valid' ? 'success' : 'error'}
                      />
                    </Box>
                    <ListItemText
                      primary={rel.definition}
                      secondary={
                        rel.status === 'valid' ? (
                          <Box component="span">
                            <Typography variant="body2" component="span">
                              {rel.parsed?.source_entity} → {rel.parsed?.target_entity}
                            </Typography>
                            <br />
                            <Typography variant="caption" component="span">
                              Type: {rel.parsed?.relationship_type} | Confidence:{' '}
                              {rel.parsed?.confidence?.toFixed(2)}
                            </Typography>
                          </Box>
                        ) : (
                          <Typography variant="body2" color="error">
                            {rel.error}
                          </Typography>
                        )
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          )}
        </Grid>
      </Grid>

      <Paper sx={{ p: 3, mt: 3 }}>
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
    </Container>
  );
}
