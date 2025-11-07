import { useState, useEffect } from 'react';
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
  Card,
  CardContent,
  Tabs,
  Tab,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Add,
  Delete,
  Edit,
  Save,
  Cancel,
  Link as LinkIcon,
  ArrowForward,
  Refresh,
  TableChart,
  SwapHoriz,
  Close,
  DragIndicator,
  Download,
} from '@mui/icons-material';
import {
  listSchemas,
  createRelationship,
  listRelationships,
  updateRelationship,
  deleteRelationship,
} from '../services/api';

export default function Relationships() {
  const [tabValue, setTabValue] = useState(0);
  const [schemas, setSchemas] = useState([]);
  const [relationships, setRelationships] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Form state for creating/editing relationships
  const [formData, setFormData] = useState({
    name: '',
    source_table: '',
    target_table: '',
    relationship_type: 'REFERENCES',
  });

  const [sourceColumns, setSourceColumns] = useState([]);
  const [targetColumns, setTargetColumns] = useState([]);
  const [columnMappings, setColumnMappings] = useState([]);
  const [editingRelationship, setEditingRelationship] = useState(null);

  // Load schemas and relationships on mount
  useEffect(() => {
    loadSchemas();
    loadRelationships();
  }, []);

  const loadSchemas = async () => {
    try {
      const response = await listSchemas();
      setSchemas(response.data.schemas || []);
    } catch (err) {
      console.error('Error loading schemas:', err);
      setError('Failed to load schemas');
    }
  };

  const loadRelationships = async () => {
    try {
      setLoading(true);
      const response = await listRelationships();
      setRelationships(response.data.relationships || []);
    } catch (err) {
      console.error('Error loading relationships:', err);
      setError('Failed to load relationships');
    } finally {
      setLoading(false);
    }
  };

  const handleSourceTableChange = async (tableName) => {
    setFormData({ ...formData, source_table: tableName });
    // In a real implementation, you would fetch columns from the schema
    // For now, we'll use mock data
    setSourceColumns([
      'id', 'name', 'email', 'created_at', 'updated_at',
      'product_id', 'supplier_id', 'category_id', 'status'
    ]);
  };

  const handleTargetTableChange = async (tableName) => {
    setFormData({ ...formData, target_table: tableName });
    // In a real implementation, you would fetch columns from the schema
    setTargetColumns([
      'id', 'name', 'description', 'created_at', 'updated_at',
      'reference_id', 'code', 'type', 'active'
    ]);
  };

  const addColumnMapping = () => {
    setColumnMappings([
      ...columnMappings,
      {
        source_column: '',
        target_column: '',
        _comment: '',
        bidirectional: false
      }
    ]);
  };

  const updateColumnMapping = (index, field, value) => {
    // Check for duplicate mappings (one-to-one validation)
    const isDuplicate = columnMappings.some((mapping, idx) => {
      if (idx === index) return false; // Skip current mapping
      if (field === 'source_column') {
        return mapping.source_column === value && value !== '';
      } else if (field === 'target_column') {
        return mapping.target_column === value && value !== '';
      }
      return false;
    });

    if (isDuplicate) {
      setError(`Column "${value}" is already mapped. Each column can only be mapped once (one-to-one mapping).`);
      return;
    }

    // Clear error if validation passes
    setError(null);

    const updated = [...columnMappings];
    updated[index][field] = value;
    setColumnMappings(updated);
  };

  const removeColumnMapping = (index) => {
    setColumnMappings(columnMappings.filter((_, i) => i !== index));
  };

  const handleCreateRelationship = async () => {
    try {
      setLoading(true);
      setError(null);

      // Validate
      if (!formData.name || !formData.source_table || !formData.target_table) {
        setError('Please fill in all required fields');
        return;
      }

      if (columnMappings.length === 0) {
        setError('Please add at least one column mapping');
        return;
      }

      // Check for incomplete mappings
      const incompleteMappings = columnMappings.some(
        m => !m.source_column || !m.target_column
      );
      if (incompleteMappings) {
        setError('Please complete all column mappings');
        return;
      }

      // Validate one-to-one mapping (no duplicate source columns)
      const sourceColumns = columnMappings.map(m => m.source_column);
      const duplicateSources = sourceColumns.filter((col, idx) => sourceColumns.indexOf(col) !== idx);
      if (duplicateSources.length > 0) {
        setError(`Duplicate source column mapping detected: "${duplicateSources[0]}". Each column can only be mapped once (one-to-one mapping).`);
        return;
      }

      // Validate one-to-one mapping (no duplicate target columns)
      const targetColumns = columnMappings.map(m => m.target_column);
      const duplicateTargets = targetColumns.filter((col, idx) => targetColumns.indexOf(col) !== idx);
      if (duplicateTargets.length > 0) {
        setError(`Duplicate target column mapping detected: "${duplicateTargets[0]}". Each column can only be mapped once (one-to-one mapping).`);
        return;
      }

      const payload = {
        name: formData.name,
        source_table: formData.source_table,
        target_table: formData.target_table,
        column_mappings: columnMappings,
        relationship_type: formData.relationship_type,
      };

      if (editingRelationship) {
        await updateRelationship(editingRelationship.id, payload);
        setSuccess('Relationship updated successfully');
      } else {
        await createRelationship(payload);
        setSuccess('Relationship created successfully');
      }

      // Reset form
      setFormData({
        name: '',
        source_table: '',
        target_table: '',
        relationship_type: 'REFERENCES',
      });
      setColumnMappings([]);
      setSourceColumns([]);
      setTargetColumns([]);
      setEditingRelationship(null);

      // Reload relationships
      await loadRelationships();

      // Switch to list tab
      setTabValue(1);
    } catch (err) {
      console.error('Error saving relationship:', err);
      setError(err.response?.data?.detail || 'Failed to save relationship');
    } finally {
      setLoading(false);
    }
  };

  const handleEditRelationship = (relationship) => {
    setEditingRelationship(relationship);
    setFormData({
      name: relationship.name,
      source_table: relationship.source_table,
      target_table: relationship.target_table,
      relationship_type: relationship.relationship_type,
    });
    setColumnMappings(relationship.column_mappings);
    
    // Load columns for both tables
    handleSourceTableChange(relationship.source_table);
    handleTargetTableChange(relationship.target_table);
    
    // Switch to create tab
    setTabValue(0);
  };

  const handleDeleteRelationship = async (relationshipId) => {
    if (!window.confirm('Are you sure you want to delete this relationship?')) {
      return;
    }

    try {
      setLoading(true);
      await deleteRelationship(relationshipId);
      setSuccess('Relationship deleted successfully');
      await loadRelationships();
    } catch (err) {
      console.error('Error deleting relationship:', err);
      setError('Failed to delete relationship');
    } finally {
      setLoading(false);
    }
  };

  const handleClearForm = () => {
    setFormData({
      name: '',
      source_table: '',
      target_table: '',
      relationship_type: 'REFERENCES',
    });
    setColumnMappings([]);
    setSourceColumns([]);
    setTargetColumns([]);
    setEditingRelationship(null);
    setError(null);
  };

  const handleDownloadJSON = () => {
    try {
      // Transform relationships data to the desired format
      const exportData = relationships.flatMap((relationship) =>
        relationship.column_mappings.map((mapping) => ({
          source_table: relationship.source_table,
          source_column: mapping.source_column,
          target_table: relationship.target_table,
          target_column: mapping.target_column,
          relationship_type: relationship.relationship_type,
          confidence: 0.95, // Default confidence value
          bidirectional: mapping.bidirectional || false,
          _comment: mapping._comment || ""
        }))
      );

      // Create a blob with the JSON data
      const jsonString = JSON.stringify(exportData, null, 2);
      const blob = new Blob([jsonString], { type: 'application/json' });

      // Create a download link and trigger it
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `relationships_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();

      // Cleanup
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      setSuccess('Relationships exported successfully');
    } catch (err) {
      console.error('Error downloading JSON:', err);
      setError('Failed to export relationships');
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 1, mb: 1, py: 1 }}>
      <Box sx={{ mb: 1 }}>
        <Typography variant="h5" gutterBottom sx={{ mb: 0.5 }}>
          Table Relationships
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Create and manage relationships between database tables with column mappings
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 1, py: 0.5 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 1, py: 0.5 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <Paper sx={{ mb: 1 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ minHeight: 40 }}>
          <Tab label="Create Relationship" icon={<Add />} iconPosition="start" sx={{ minHeight: 40, py: 1 }} />
          <Tab label="View Relationships" icon={<TableChart />} iconPosition="start" sx={{ minHeight: 40, py: 1 }} />
        </Tabs>
      </Paper>

      {/* Tab 0: Create Relationship */}
      {tabValue === 0 && (
        <Paper sx={{ p: 1.5 }}>
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600, mb: 1 }}>
            {editingRelationship ? 'Edit Relationship' : 'Create New Relationship'}
          </Typography>

          <Grid container spacing={1.5}>
            {/* Relationship Name */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Relationship Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Product to Supplier Relationship"
                required
                size="small"
              />
            </Grid>

            {/* Source Table */}
            <Grid item xs={12} md={5}>
              <FormControl fullWidth required size="small">
                <InputLabel>Source Table</InputLabel>
                <Select
                  value={formData.source_table}
                  onChange={(e) => handleSourceTableChange(e.target.value)}
                  label="Source Table"
                >
                  {schemas.map((schema) => (
                    <MenuItem key={schema} value={schema}>
                      {schema}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Arrow Icon */}
            <Grid item xs={12} md={2} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ArrowForward sx={{ fontSize: 28, color: 'primary.main' }} />
            </Grid>

            {/* Target Table */}
            <Grid item xs={12} md={5}>
              <FormControl fullWidth required size="small">
                <InputLabel>Target Table</InputLabel>
                <Select
                  value={formData.target_table}
                  onChange={(e) => handleTargetTableChange(e.target.value)}
                  label="Target Table"
                >
                  {schemas.map((schema) => (
                    <MenuItem key={schema} value={schema}>
                      {schema}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Relationship Type */}
            <Grid item xs={12}>
              <FormControl fullWidth size="small">
                <InputLabel>Relationship Type</InputLabel>
                <Select
                  value={formData.relationship_type}
                  onChange={(e) => setFormData({ ...formData, relationship_type: e.target.value })}
                  label="Relationship Type"
                >
                  <MenuItem value="REFERENCES">REFERENCES</MenuItem>
                  <MenuItem value="FOREIGN_KEY">FOREIGN_KEY</MenuItem>
                  <MenuItem value="MATCHES">MATCHES</MenuItem>
                  <MenuItem value="CONTAINS">CONTAINS</MenuItem>
                  <MenuItem value="BELONGS_TO">BELONGS_TO</MenuItem>
                  <MenuItem value="RELATED_TO">RELATED_TO</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Column Mappings Section */}
            {formData.source_table && formData.target_table && (
              <Grid item xs={12}>
                <Divider sx={{ my: 1 }} />
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    Column Mappings ({columnMappings.length})
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<Add />}
                    onClick={addColumnMapping}
                    size="small"
                    sx={{ py: 0.5 }}
                  >
                    Add Mapping
                  </Button>
                </Box>

                {columnMappings.length === 0 ? (
                  <Alert severity="info" sx={{ py: 0.5 }}>
                    Click "Add Mapping" to create column mappings between the source and target tables.
                  </Alert>
                ) : (
                  <Paper variant="outlined" sx={{ p: 1.5, bgcolor: 'grey.50' }}>
                    {/* Header Row */}
                    <Grid container spacing={1} sx={{ mb: 1 }}>
                      <Grid item xs={5}>
                        <Box sx={{
                          p: 0.5,
                          bgcolor: 'primary.main',
                          color: 'white',
                          borderRadius: 1,
                          textAlign: 'center'
                        }}>
                          <Typography variant="caption" sx={{ fontWeight: 600 }}>
                            {formData.source_table || 'Source Table'}
                          </Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={2} sx={{ textAlign: 'center' }}>
                        <Box sx={{ p: 0.5 }}>
                          <SwapHoriz color="action" fontSize="small" />
                        </Box>
                      </Grid>
                      <Grid item xs={5}>
                        <Box sx={{
                          p: 0.5,
                          bgcolor: 'secondary.main',
                          color: 'white',
                          borderRadius: 1,
                          textAlign: 'center'
                        }}>
                          <Typography variant="caption" sx={{ fontWeight: 600 }}>
                            {formData.target_table || 'Target Table'}
                          </Typography>
                        </Box>
                      </Grid>
                    </Grid>

                    {/* Mapping Rows */}
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.75 }}>
                      {columnMappings.map((mapping, index) => (
                        <Box
                          key={index}
                          sx={{
                            bgcolor: 'white',
                            borderRadius: 1,
                            border: '1px solid',
                            borderColor: 'divider',
                            p: 1,
                            transition: 'all 0.2s',
                            '&:hover': {
                              borderColor: 'primary.main',
                              boxShadow: 1,
                            }
                          }}
                        >
                          <Grid container spacing={1} alignItems="center">
                            {/* Source Column */}
                            <Grid item xs={5}>
                              <FormControl fullWidth size="small">
                                <Select
                                  value={mapping.source_column}
                                  onChange={(e) => updateColumnMapping(index, 'source_column', e.target.value)}
                                  displayEmpty
                                  sx={{
                                    bgcolor: 'white',
                                    '& .MuiSelect-select': {
                                      py: 0.75,
                                    }
                                  }}
                                >
                                  <MenuItem value="" disabled>
                                    <em>Select source column</em>
                                  </MenuItem>
                                  {sourceColumns.map((col) => {
                                    const isAlreadyMapped = columnMappings.some(
                                      (m, idx) => idx !== index && m.source_column === col
                                    );
                                    return (
                                      <MenuItem
                                        key={col}
                                        value={col}
                                        disabled={isAlreadyMapped}
                                      >
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                          <DragIndicator sx={{ fontSize: 14, color: 'text.secondary' }} />
                                          <Typography variant="body2">{col}</Typography>
                                          {isAlreadyMapped && (
                                            <Chip
                                              label="Mapped"
                                              size="small"
                                              color="warning"
                                              sx={{ height: 16, fontSize: '0.6rem', ml: 0.5 }}
                                            />
                                          )}
                                        </Box>
                                      </MenuItem>
                                    );
                                  })}
                                </Select>
                              </FormControl>
                            </Grid>

                            {/* Arrow/Link Icon */}
                            <Grid item xs={2} sx={{ textAlign: 'center' }}>
                              <Box sx={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                height: '100%'
                              }}>
                                <ArrowForward
                                  sx={{
                                    fontSize: 20,
                                    color: mapping.source_column && mapping.target_column
                                      ? 'success.main'
                                      : 'text.disabled'
                                  }}
                                />
                              </Box>
                            </Grid>

                            {/* Target Column */}
                            <Grid item xs={4}>
                              <FormControl fullWidth size="small">
                                <Select
                                  value={mapping.target_column}
                                  onChange={(e) => updateColumnMapping(index, 'target_column', e.target.value)}
                                  displayEmpty
                                  sx={{
                                    bgcolor: 'white',
                                    '& .MuiSelect-select': {
                                      py: 0.75,
                                    }
                                  }}
                                >
                                  <MenuItem value="" disabled>
                                    <em>Select target column</em>
                                  </MenuItem>
                                  {targetColumns.map((col) => {
                                    const isAlreadyMapped = columnMappings.some(
                                      (m, idx) => idx !== index && m.target_column === col
                                    );
                                    return (
                                      <MenuItem
                                        key={col}
                                        value={col}
                                        disabled={isAlreadyMapped}
                                      >
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                          <DragIndicator sx={{ fontSize: 14, color: 'text.secondary' }} />
                                          <Typography variant="body2">{col}</Typography>
                                          {isAlreadyMapped && (
                                            <Chip
                                              label="Mapped"
                                              size="small"
                                              color="warning"
                                              sx={{ height: 16, fontSize: '0.6rem', ml: 0.5 }}
                                            />
                                          )}
                                        </Box>
                                      </MenuItem>
                                    );
                                  })}
                                </Select>
                              </FormControl>
                            </Grid>

                            {/* Delete Button */}
                            <Grid item xs={1} sx={{ textAlign: 'center' }}>
                              <Tooltip title="Remove mapping">
                                <IconButton
                                  onClick={() => removeColumnMapping(index)}
                                  size="small"
                                  sx={{
                                    color: 'error.main',
                                    '&:hover': {
                                      bgcolor: 'error.lighter',
                                    }
                                  }}
                                >
                                  <Close fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            </Grid>
                          </Grid>

                          {/* Comment and Bidirectional Fields */}
                          <Box sx={{ mt: 1 }}>
                            <Grid container spacing={1} alignItems="center">
                              {/* Comment Field */}
                              <Grid item xs={8}>
                                <TextField
                                  fullWidth
                                  size="small"
                                  placeholder="Add comment for this mapping (optional)"
                                  value={mapping._comment || ''}
                                  onChange={(e) => updateColumnMapping(index, '_comment', e.target.value)}
                                  sx={{
                                    '& .MuiInputBase-input': {
                                      py: 0.5,
                                      fontSize: '0.8rem',
                                    }
                                  }}
                                />
                              </Grid>

                              {/* Bidirectional Toggle */}
                              <Grid item xs={4}>
                                <FormControlLabel
                                  control={
                                    <Switch
                                      size="small"
                                      checked={mapping.bidirectional || false}
                                      onChange={(e) => updateColumnMapping(index, 'bidirectional', e.target.checked)}
                                      color="primary"
                                    />
                                  }
                                  label={
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                      <Typography variant="caption" sx={{ fontSize: '0.75rem' }}>
                                        Bidirectional
                                      </Typography>
                                      <Tooltip title="Enable if the relationship works in both directions">
                                        <Box component="span" sx={{
                                          display: 'inline-flex',
                                          alignItems: 'center',
                                          cursor: 'help',
                                          color: 'text.secondary',
                                          fontSize: '0.75rem'
                                        }}>
                                          ⓘ
                                        </Box>
                                      </Tooltip>
                                    </Box>
                                  }
                                  sx={{ m: 0 }}
                                />
                              </Grid>
                            </Grid>
                          </Box>

                          {/* Mapping Status Indicator */}
                          {mapping.source_column && mapping.target_column && (
                            <Box sx={{ mt: 0.5, display: 'flex', alignItems: 'center', gap: 0.5 }}>
                              <Chip
                                label={`${mapping.source_column} → ${mapping.target_column}`}
                                size="small"
                                color="success"
                                variant="outlined"
                                sx={{
                                  height: 18,
                                  fontSize: '0.65rem',
                                  '& .MuiChip-label': { px: 0.75 }
                                }}
                              />
                              {mapping.bidirectional && (
                                <Chip
                                  label="↔ Bidirectional"
                                  size="small"
                                  color="info"
                                  variant="outlined"
                                  sx={{
                                    height: 18,
                                    fontSize: '0.65rem',
                                    '& .MuiChip-label': { px: 0.75 }
                                  }}
                                />
                              )}
                              {mapping._comment && (
                                <Tooltip title={mapping._comment}>
                                  <Chip
                                    label="📝"
                                    size="small"
                                    variant="outlined"
                                    sx={{
                                      height: 18,
                                      fontSize: '0.65rem',
                                      '& .MuiChip-label': { px: 0.5 }
                                    }}
                                  />
                                </Tooltip>
                              )}
                            </Box>
                          )}
                        </Box>
                      ))}
                    </Box>
                  </Paper>
                )}
              </Grid>
            )}

            {/* Action Buttons */}
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end', mt: 0.5 }}>
                <Button
                  variant="outlined"
                  startIcon={<Cancel />}
                  onClick={handleClearForm}
                  size="small"
                  sx={{ py: 0.5 }}
                >
                  Clear
                </Button>
                <Button
                  variant="contained"
                  startIcon={<Save />}
                  onClick={handleCreateRelationship}
                  disabled={loading || !formData.source_table || !formData.target_table || columnMappings.length === 0}
                  size="small"
                  sx={{ py: 0.5 }}
                >
                  {loading ? <CircularProgress size={16} /> : editingRelationship ? 'Update Relationship' : 'Save Relationship'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Tab 1: View Relationships */}
      {tabValue === 1 && (
        <Paper sx={{ p: 1.5 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
              All Relationships ({relationships.length})
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={handleDownloadJSON}
                disabled={loading || relationships.length === 0}
                size="small"
                sx={{ py: 0.5 }}
              >
                Download JSON
              </Button>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={loadRelationships}
                disabled={loading}
                size="small"
                sx={{ py: 0.5 }}
              >
                Refresh
              </Button>
            </Box>
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
              <CircularProgress size={32} />
            </Box>
          ) : relationships.length === 0 ? (
            <Alert severity="info" sx={{ py: 0.5 }}>
              No relationships found. Create your first relationship using the "Create Relationship" tab.
            </Alert>
          ) : (
            <Grid container spacing={1}>
              {relationships.map((relationship) => (
                <Grid item xs={12} key={relationship.id}>
                  <Card>
                    <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                        <Box>
                          <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600, mb: 0.5 }}>
                            {relationship.name}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center', mb: 0.5 }}>
                            <Chip
                              label={relationship.source_table}
                              color="primary"
                              size="small"
                              variant="outlined"
                              sx={{ height: 20, fontSize: '0.7rem' }}
                            />
                            <ArrowForward sx={{ fontSize: 14 }} color="action" />
                            <Chip
                              label={relationship.target_table}
                              color="secondary"
                              size="small"
                              variant="outlined"
                              sx={{ height: 20, fontSize: '0.7rem' }}
                            />
                            <Chip
                              label={relationship.relationship_type}
                              size="small"
                              sx={{ ml: 0.5, height: 20, fontSize: '0.7rem' }}
                            />
                          </Box>
                        </Box>
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          <Tooltip title="Edit">
                            <IconButton
                              color="primary"
                              onClick={() => handleEditRelationship(relationship)}
                              size="small"
                            >
                              <Edit fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton
                              color="error"
                              onClick={() => handleDeleteRelationship(relationship.id)}
                              size="small"
                            >
                              <Delete fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </Box>

                      <Divider sx={{ my: 0.5 }} />

                      <Typography variant="caption" gutterBottom color="text.secondary" sx={{ fontWeight: 600, display: 'block', mb: 0.5 }}>
                        Column Mappings ({relationship.column_mappings.length})
                      </Typography>

                      <TableContainer>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}><strong>Source Column</strong></TableCell>
                              <TableCell align="center" sx={{ py: 0.5, fontSize: '0.75rem' }}><strong>→</strong></TableCell>
                              <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}><strong>Target Column</strong></TableCell>
                              <TableCell sx={{ py: 0.5, fontSize: '0.75rem' }}><strong>Comment</strong></TableCell>
                              <TableCell align="center" sx={{ py: 0.5, fontSize: '0.75rem' }}><strong>Bidirectional</strong></TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {relationship.column_mappings.map((mapping, idx) => (
                              <TableRow key={idx}>
                                <TableCell sx={{ py: 0.5 }}>
                                  <Chip
                                    label={mapping.source_column}
                                    size="small"
                                    variant="outlined"
                                    sx={{ height: 20, fontSize: '0.7rem' }}
                                  />
                                </TableCell>
                                <TableCell align="center" sx={{ py: 0.5 }}>
                                  {mapping.bidirectional ? (
                                    <Tooltip title="Bidirectional">
                                      <SwapHoriz sx={{ fontSize: 14 }} color="info" />
                                    </Tooltip>
                                  ) : (
                                    <ArrowForward sx={{ fontSize: 14 }} color="action" />
                                  )}
                                </TableCell>
                                <TableCell sx={{ py: 0.5 }}>
                                  <Chip
                                    label={mapping.target_column}
                                    size="small"
                                    variant="outlined"
                                    sx={{ height: 20, fontSize: '0.7rem' }}
                                  />
                                </TableCell>
                                <TableCell sx={{ py: 0.5 }}>
                                  <Typography variant="caption" color="text.secondary">
                                    {mapping._comment || '-'}
                                  </Typography>
                                </TableCell>
                                <TableCell align="center" sx={{ py: 0.5 }}>
                                  {mapping.bidirectional ? (
                                    <Chip
                                      label="Yes"
                                      size="small"
                                      color="info"
                                      sx={{ height: 18, fontSize: '0.65rem' }}
                                    />
                                  ) : (
                                    <Chip
                                      label="No"
                                      size="small"
                                      variant="outlined"
                                      sx={{ height: 18, fontSize: '0.65rem' }}
                                    />
                                  )}
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>

                      {relationship.created_at && (
                        <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                          Created: {new Date(relationship.created_at).toLocaleString()}
                          {relationship.updated_at && relationship.updated_at !== relationship.created_at && (
                            <> • Updated: {new Date(relationship.updated_at).toLocaleString()}</>
                          )}
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Paper>
      )}
    </Container>
  );
}

