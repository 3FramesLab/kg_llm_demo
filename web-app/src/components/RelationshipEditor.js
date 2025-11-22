import { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Alert,
  CircularProgress,
  Chip,
  Grid,
  Divider,
  TextField,
  Slider,
} from '@mui/material';
import { Add, Edit, Delete, AutoAwesome, Storage, TableChart } from '@mui/icons-material';
import { suggestRelationships } from '../services/api';

export default function RelationshipEditor({ schemaConfig, onRelationshipsUpdated }) {
  const [relationships, setRelationships] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingIndex, setEditingIndex] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    source_table: '',
    source_column: '',
    target_table: '',
    target_column: '',
    relationship_type: 'MATCHES',
    confidence: 0.8,
    description: '',
  });

  useEffect(() => {
    if (schemaConfig) {
      suggestLLMRelationships();
    }
  }, [schemaConfig]);

  const suggestLLMRelationships = async () => {
    if (!schemaConfig || !schemaConfig.tables || schemaConfig.tables.length === 0) {
      return;
    }

    setLoading(true);
    try {
      // Call the API for each table in the schema to get suggestions
      const allSuggestions = [];

      for (const table of schemaConfig.tables) {
        try {
          const response = await suggestRelationships({
            source_table: table.tableName,
            schema_id: schemaConfig.id,
          });

          if (response.data.success && response.data.suggestions) {
            const suggestedRels = response.data.suggestions.map(rel => ({
              ...rel,
              id: Math.random(),
            }));
            allSuggestions.push(...suggestedRels);
          }
        } catch (tableErr) {
          console.error(`Error suggesting relationships for table ${table.tableName}:`, tableErr);
          // Continue with other tables even if one fails
        }
      }

      // Merge suggestions with all columns from the schema
      const mergedRels = mergeWithAllColumns(allSuggestions);

      setRelationships(mergedRels);
      onRelationshipsUpdated(mergedRels);
    } catch (err) {
      console.error('Error suggesting relationships:', err);
      setError('Failed to generate relationship suggestions');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (index = null) => {
    if (index !== null) {
      setEditingIndex(index);
      const rel = relationships[index];
      // If this is a placeholder row, pre-fill source table and column
      if (rel.is_placeholder) {
        setFormData({
          source_table: rel.source_table,
          source_column: rel.source_column,
          target_table: '',
          target_column: '',
          relationship_type: 'MATCHES',
          confidence: 0.8,
          description: '',
        });
      } else {
        setFormData({
          ...rel,
          confidence: rel.confidence !== null && rel.confidence !== undefined ? rel.confidence : 0.8,
          description: rel.description || rel.reasoning || '',
        });
      }
    } else {
      setEditingIndex(null);
      setFormData({
        source_table: '',
        source_column: '',
        target_table: '',
        target_column: '',
        relationship_type: 'MATCHES',
        confidence: 0.8,
        description: '',
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingIndex(null);
  };

  const handleSave = () => {
    if (!formData.source_table || !formData.target_table) {
      setError('Please fill in all required fields');
      return;
    }

    // Validate confidence is a number between 0 and 1
    const confidence = parseFloat(formData.confidence);
    if (isNaN(confidence) || confidence < 0 || confidence > 1) {
      setError('Confidence must be a number between 0 and 1');
      return;
    }

    let updatedRels;
    if (editingIndex !== null) {
      updatedRels = [...relationships];
      updatedRels[editingIndex] = { ...formData, confidence };
    } else {
      updatedRels = [...relationships, { ...formData, confidence, id: Math.random() }];
    }

    setRelationships(updatedRels);
    onRelationshipsUpdated(updatedRels);
    setError(null);
    handleCloseDialog();
  };

  const handleDelete = (index) => {
    const updatedRels = relationships.filter((_, i) => i !== index);
    setRelationships(updatedRels);
    onRelationshipsUpdated(updatedRels);
  };

  const getTables = () => {
    return schemaConfig?.tables?.map(t => t.tableName) || [];
  };

  const getColumns = (tableName) => {
    const table = schemaConfig?.tables?.find(t => t.tableName === tableName);
    return table?.columns?.map(c => c.name) || [];
  };

  const getAllSourceColumns = () => {
    // Get all columns from ALL tables in the schema
    if (!schemaConfig || !schemaConfig.tables || schemaConfig.tables.length === 0) {
      return [];
    }

    // Collect columns from all tables with their table names
    const allColumns = [];
    schemaConfig.tables.forEach(table => {
      if (table.columns && Array.isArray(table.columns)) {
        table.columns.forEach(column => {
          allColumns.push({
            tableName: table.tableName,
            columnName: column.name
          });
        });
      }
    });

    return allColumns;
  };

  const mergeWithAllColumns = (suggestions) => {
    // Get all columns from all tables in the schema
    const allColumns = getAllSourceColumns();

    // Create a map of suggestions by source_table + source_column for quick lookup
    const suggestionMap = {};
    suggestions.forEach(suggestion => {
      const key = `${suggestion.source_table}:${suggestion.source_column}`;
      suggestionMap[key] = suggestion;
    });

    // Create merged list: suggestions first, then placeholder rows for columns without suggestions
    const merged = [];

    // Add all columns, using suggestions if available
    allColumns.forEach(columnInfo => {
      const key = `${columnInfo.tableName}:${columnInfo.columnName}`;

      if (suggestionMap[key]) {
        // Column has a suggestion - use it
        merged.push(suggestionMap[key]);
      } else {
        // Column has no suggestion - create a placeholder row
        merged.push({
          id: Math.random(),
          source_table: columnInfo.tableName,
          source_column: columnInfo.columnName,
          target_table: '',
          target_column: '',
          relationship_type: '',
          confidence: null,
          is_placeholder: true, // Mark as placeholder for styling
        });
      }
    });

    return merged;
  };

  const getConfidenceBadgeStyle = (confidence) => {
    // Handle missing or invalid confidence values
    if (confidence === null || confidence === undefined || confidence === 'N/A') {
      return {
        bgcolor: '#F3F4F6',
        color: '#6B7280',
        label: 'N/A',
      };
    }

    const score = typeof confidence === 'string' ? parseFloat(confidence) : confidence;

    // High confidence (0.75 - 1.0)
    if (score >= 0.75) {
      return {
        bgcolor: '#D1FAE5',
        color: '#065F46',
        label: `${Math.round(score * 100)}%`,
      };
    }
    // Medium confidence (0.5 - 0.74)
    if (score >= 0.5) {
      return {
        bgcolor: '#FEF3C7',
        color: '#92400E',
        label: `${Math.round(score * 100)}%`,
      };
    }
    // Low confidence (0.0 - 0.49)
    return {
      bgcolor: '#FEE2E2',
      color: '#7F1D1D',
      label: `${Math.round(score * 100)}%`,
    };
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Schema Configuration Summary Section */}
      {schemaConfig && (
        <Paper
          elevation={0}
          sx={{
            p: 1.25,
            mb: 1.25,
            bgcolor: '#F9FAFB',
            border: '1px solid #E5E7EB',
            borderRadius: 1,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.75 }}>
            <Storage sx={{ fontSize: '1.1rem', color: '#5B6FE5' }} />
            <Typography
              sx={{
                fontWeight: 600,
                fontSize: '0.9rem',
                color: '#1F2937',
              }}
            >
              {schemaConfig.schemaName || schemaConfig.id}
            </Typography>
          </Box>

          <Grid container spacing={1.5} sx={{ mb: 0.75 }}>
            <Grid item xs={12} sm={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
                <TableChart sx={{ fontSize: '1rem', color: '#7C8FE5' }} />
                <Typography
                  sx={{
                    fontSize: '0.75rem',
                    color: '#6B7280',
                    fontWeight: 500,
                  }}
                >
                  Tables: {schemaConfig.tables?.length || 0}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography
                sx={{
                  fontSize: '0.75rem',
                  color: '#6B7280',
                  fontWeight: 500,
                }}
              >
                Columns: {schemaConfig.tables?.reduce((sum, table) => sum + (table.columns?.length || 0), 0) || 0}
              </Typography>
            </Grid>
          </Grid>

          <Divider sx={{ my: 0.75 }} />

          <Typography
            sx={{
              fontSize: '0.7rem',
              color: '#9CA3AF',
              fontWeight: 600,
              mb: 0.5,
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
            }}
          >
            Available Tables
          </Typography>

          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
            {schemaConfig.tables?.map((table, idx) => (
              <Chip
                key={idx}
                label={table.tableName}
                size="small"
                sx={{
                  height: '22px',
                  fontSize: '0.7rem',
                  bgcolor: '#EEF2FF',
                  color: '#5B6FE5',
                  fontWeight: 500,
                  '&:hover': {
                    bgcolor: '#E0E7FF',
                  },
                }}
              />
            ))}
          </Box>
        </Paper>
      )}

      {/* Header with Action Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography
          variant="subtitle1"
          sx={{
            fontWeight: 600,
            color: '#1F2937',
            fontSize: '0.9rem',
          }}
        >
          Relationships
        </Typography>
        <Box sx={{ display: 'flex', gap: 0.75 }}>
          <Button
            startIcon={<AutoAwesome />}
            onClick={suggestLLMRelationships}
            disabled={loading}
            variant="outlined"
            size="small"
            sx={{
              px: 1.25,
              py: 0.375,
              minWidth: 'auto',
              color: '#64748B',
              borderColor: '#CBD5E1',
              fontSize: '0.75rem',
              textTransform: 'none',
              borderRadius: '6px',
              '&:hover': {
                bgcolor: '#F8FAFC',
                borderColor: '#94A3B8',
                color: '#475569',
              },
              '&:disabled': {
                color: '#D1D5DB',
                borderColor: '#E5E7EB',
              },
            }}
          >
            {loading ? (
              <>
                <CircularProgress size={14} sx={{ mr: 0.5 }} />
                Suggesting...
              </>
            ) : (
              'Suggest with LLM'
            )}
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleOpenDialog()}
            size="small"
            sx={{
              px: 1.25,
              py: 0.375,
              minHeight: 'auto',
              bgcolor: '#5B6FE5',
              color: '#FFFFFF',
              fontSize: '0.75rem',
              fontWeight: 500,
              textTransform: 'none',
              borderRadius: '6px',
              boxShadow: '0 1px 3px 0 rgba(91, 111, 229, 0.2)',
              '&:hover': {
                bgcolor: '#4C5FD5',
                boxShadow: '0 2px 6px 0 rgba(91, 111, 229, 0.3)',
              },
            }}
          >
            Add Relationship
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 1 }}>
          {error}
        </Alert>
      )}

      {/* Relationships Table */}
      <Paper
        elevation={0}
        sx={{
          flex: 1,
          overflow: 'auto',
          border: '1px solid #E5E7EB',
          borderRadius: 1,
        }}
      >
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ backgroundColor: '#F9FAFB' }}>
                <TableCell
                  sx={{
                    fontWeight: 600,
                    color: '#374151',
                    fontSize: '0.8125rem',
                    borderBottom: '1px solid #E5E7EB',
                    py: 0.75,
                  }}
                >
                  Source Table
                </TableCell>
                <TableCell
                  sx={{
                    fontWeight: 600,
                    color: '#374151',
                    fontSize: '0.8125rem',
                    borderBottom: '1px solid #E5E7EB',
                    py: 0.75,
                  }}
                >
                  Source Column
                </TableCell>
                <TableCell
                  sx={{
                    fontWeight: 600,
                    color: '#374151',
                    fontSize: '0.8125rem',
                    borderBottom: '1px solid #E5E7EB',
                    py: 0.75,
                  }}
                >
                  Target Table
                </TableCell>
                <TableCell
                  sx={{
                    fontWeight: 600,
                    color: '#374151',
                    fontSize: '0.8125rem',
                    borderBottom: '1px solid #E5E7EB',
                    py: 0.75,
                  }}
                >
                  Target Column
                </TableCell>
                <TableCell
                  sx={{
                    fontWeight: 600,
                    color: '#374151',
                    fontSize: '0.8125rem',
                    borderBottom: '1px solid #E5E7EB',
                    py: 0.75,
                  }}
                >
                  Type
                </TableCell>
                <TableCell
                  align="center"
                  sx={{
                    fontWeight: 600,
                    color: '#374151',
                    fontSize: '0.8125rem',
                    borderBottom: '1px solid #E5E7EB',
                    py: 0.75,
                  }}
                >
                  Confidence
                </TableCell>
                <TableCell
                  align="right"
                  sx={{
                    fontWeight: 600,
                    color: '#374151',
                    fontSize: '0.8125rem',
                    borderBottom: '1px solid #E5E7EB',
                    py: 0.75,
                  }}
                >
                  Actions
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {relationships.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 2, color: '#9CA3AF' }}>
                    No relationships defined yet. Click "Add Relationship" or "Suggest with LLM" to get started.
                  </TableCell>
                </TableRow>
              ) : (
                relationships.map((rel, idx) => (
                  <TableRow
                    key={rel.id || idx}
                    hover
                    sx={{
                      bgcolor: rel.is_placeholder
                        ? '#FAFAFA'
                        : (idx % 2 === 0 ? '#FFFFFF' : '#F9FAFB'),
                      borderLeft: rel.is_placeholder ? '3px solid #FCD34D' : 'none',
                      '&:hover': {
                        bgcolor: rel.is_placeholder ? '#F5F5F5' : '#F5F7FF',
                      },
                      '& td': {
                        borderBottom: '1px solid #F3F4F6',
                        fontSize: '0.8125rem',
                        color: rel.is_placeholder ? '#9CA3AF' : '#6B7280',
                        py: 0.5,
                      },
                    }}
                  >
                    <TableCell
                      sx={{
                        fontWeight: 500,
                        color: '#1F2937',
                        fontSize: '0.8125rem',
                        borderBottom: '1px solid #F3F4F6',
                        py: 0.5,
                      }}
                    >
                      {rel.source_table}
                    </TableCell>
                    <TableCell
                      sx={{
                        color: '#6B7280',
                        fontSize: '0.8125rem',
                        borderBottom: '1px solid #F3F4F6',
                        py: 0.5,
                      }}
                    >
                      {rel.source_column}
                    </TableCell>
                    <TableCell
                      sx={{
                        fontWeight: 500,
                        color: rel.target_table ? '#1F2937' : '#D1D5DB',
                        fontSize: '0.8125rem',
                        borderBottom: '1px solid #F3F4F6',
                        py: 0.5,
                        fontStyle: rel.target_table ? 'normal' : 'italic',
                      }}
                    >
                      {rel.target_table || '—'}
                    </TableCell>
                    <TableCell
                      sx={{
                        color: rel.target_column ? '#6B7280' : '#D1D5DB',
                        fontSize: '0.8125rem',
                        borderBottom: '1px solid #F3F4F6',
                        py: 0.5,
                        fontStyle: rel.target_column ? 'normal' : 'italic',
                      }}
                    >
                      {rel.target_column || '—'}
                    </TableCell>
                    <TableCell
                      sx={{
                        fontSize: '0.8125rem',
                        borderBottom: '1px solid #F3F4F6',
                        py: 0.5,
                      }}
                    >
                      {rel.relationship_type ? (
                        <Box
                          component="span"
                          sx={{
                            display: 'inline-block',
                            px: 0.75,
                            py: 0.25,
                            bgcolor: '#EEF2FF',
                            color: '#5B6FE5',
                            borderRadius: '4px',
                            fontSize: '0.75rem',
                            fontWeight: 500,
                          }}
                        >
                          {rel.relationship_type}
                        </Box>
                      ) : (
                        <Box
                          component="span"
                          sx={{
                            display: 'inline-block',
                            px: 0.75,
                            py: 0.25,
                            bgcolor: '#F3F4F6',
                            color: '#D1D5DB',
                            borderRadius: '4px',
                            fontSize: '0.75rem',
                            fontWeight: 500,
                            fontStyle: 'italic',
                          }}
                        >
                          —
                        </Box>
                      )}
                    </TableCell>
                    <TableCell
                      align="center"
                      sx={{
                        fontSize: '0.8125rem',
                        borderBottom: '1px solid #F3F4F6',
                        py: 0.5,
                      }}
                    >
                      {(() => {
                        const badgeStyle = getConfidenceBadgeStyle(rel.confidence);
                        return (
                          <Box
                            component="span"
                            sx={{
                              display: 'inline-block',
                              px: 0.75,
                              py: 0.25,
                              bgcolor: badgeStyle.bgcolor,
                              color: badgeStyle.color,
                              borderRadius: '4px',
                              fontSize: '0.75rem',
                              fontWeight: 600,
                            }}
                          >
                            {badgeStyle.label}
                          </Box>
                        );
                      })()}
                    </TableCell>
                    <TableCell
                      align="right"
                      sx={{
                        fontSize: '0.8125rem',
                        borderBottom: '1px solid #F3F4F6',
                        py: 0.5,
                      }}
                    >
                      <IconButton
                        size="small"
                        onClick={() => handleOpenDialog(idx)}
                        sx={{
                          color: '#64748B',
                          padding: '4px',
                          '&:hover': {
                            bgcolor: '#F1F5F9',
                            color: '#5B6FE5',
                          },
                        }}
                      >
                        <Edit fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(idx)}
                        sx={{
                          color: '#64748B',
                          padding: '4px',
                          '&:hover': {
                            bgcolor: '#FEE2E2',
                            color: '#DC2626',
                          },
                        }}
                      >
                        <Delete fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Dialog for Add/Edit Relationship */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle
          sx={{
            fontWeight: 600,
            color: '#1F2937',
            fontSize: '0.95rem',
            pb: 0.75,
          }}
        >
          {editingIndex !== null ? 'Edit Relationship' : 'Add New Relationship'}
        </DialogTitle>
        <DialogContent sx={{ pt: 1, pb: 1 }}>
          {/* Source Section */}
          <Box sx={{ mb: 1.5 }}>
            <Typography
              sx={{
                fontSize: '0.75rem',
                fontWeight: 600,
                color: '#6B7280',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                mb: 0.75,
              }}
            >
              Source
            </Typography>
            <FormControl fullWidth sx={{ mb: 1 }}>
              <InputLabel sx={{ fontSize: '0.8125rem' }}>Source Table</InputLabel>
              <Select
                value={formData.source_table}
                onChange={(e) => setFormData({ ...formData, source_table: e.target.value })}
                label="Source Table"
                size="small"
              >
                {getTables().map(t => (
                  <MenuItem key={t} value={t}>
                    {t}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel sx={{ fontSize: '0.8125rem' }}>Source Column</InputLabel>
              <Select
                value={formData.source_column}
                onChange={(e) => setFormData({ ...formData, source_column: e.target.value })}
                label="Source Column"
                size="small"
              >
                {getColumns(formData.source_table).map(c => (
                  <MenuItem key={c} value={c}>
                    {c}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          <Divider sx={{ my: 1 }} />

          {/* Target Section */}
          <Box sx={{ mb: 1.5 }}>
            <Typography
              sx={{
                fontSize: '0.75rem',
                fontWeight: 600,
                color: '#6B7280',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                mb: 0.75,
              }}
            >
              Target
            </Typography>
            <FormControl fullWidth sx={{ mb: 1 }}>
              <InputLabel sx={{ fontSize: '0.8125rem' }}>Target Table</InputLabel>
              <Select
                value={formData.target_table}
                onChange={(e) => setFormData({ ...formData, target_table: e.target.value })}
                label="Target Table"
                size="small"
              >
                {getTables().map(t => (
                  <MenuItem key={t} value={t}>
                    {t}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel sx={{ fontSize: '0.8125rem' }}>Target Column</InputLabel>
              <Select
                value={formData.target_column}
                onChange={(e) => setFormData({ ...formData, target_column: e.target.value })}
                label="Target Column"
                size="small"
              >
                {getColumns(formData.target_table).map(c => (
                  <MenuItem key={c} value={c}>
                    {c}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          <Divider sx={{ my: 1 }} />

          {/* Relationship Type Section */}
          <Box sx={{ mb: 1.5 }}>
            <Typography
              sx={{
                fontSize: '0.75rem',
                fontWeight: 600,
                color: '#6B7280',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                mb: 0.75,
              }}
            >
              Configuration
            </Typography>
            <FormControl fullWidth>
              <InputLabel sx={{ fontSize: '0.8125rem' }}>Relationship Type</InputLabel>
              <Select
                value={formData.relationship_type}
                onChange={(e) => setFormData({ ...formData, relationship_type: e.target.value })}
                label="Relationship Type"
                size="small"
              >
                <MenuItem value="MATCHES">MATCHES</MenuItem>
              </Select>
            </FormControl>
          </Box>

          <Divider sx={{ my: 1 }} />

          {/* Confidence and Description Section */}
          <Box>
            <Typography
              sx={{
                fontSize: '0.75rem',
                fontWeight: 600,
                color: '#6B7280',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                mb: 0.75,
              }}
            >
              Additional Details
            </Typography>

            {/* Confidence Field */}
            <Box sx={{ mb: 1.5 }}>
              <Typography
                sx={{
                  fontSize: '0.75rem',
                  color: '#6B7280',
                  mb: 0.5,
                  fontWeight: 500,
                }}
              >
                Confidence: {Math.round(formData.confidence * 100)}%
              </Typography>
              <Slider
                value={formData.confidence}
                onChange={(_, newValue) => setFormData({ ...formData, confidence: newValue })}
                min={0}
                max={1}
                step={0.05}
                marks={[
                  { value: 0, label: '0%' },
                  { value: 0.5, label: '50%' },
                  { value: 1, label: '100%' },
                ]}
                sx={{
                  color: '#5B6FE5',
                  '& .MuiSlider-thumb': {
                    width: 16,
                    height: 16,
                    '&:hover, &.Mui-focusVisible': {
                      boxShadow: '0 0 0 8px rgba(91, 111, 229, 0.16)',
                    },
                  },
                  '& .MuiSlider-track': {
                    height: 4,
                  },
                  '& .MuiSlider-rail': {
                    height: 4,
                    bgcolor: '#E5E7EB',
                  },
                  '& .MuiSlider-mark': {
                    bgcolor: '#9CA3AF',
                    height: 8,
                    width: 2,
                  },
                  '& .MuiSlider-markLabel': {
                    fontSize: '0.7rem',
                    color: '#9CA3AF',
                  },
                }}
              />
            </Box>

            {/* Description Field */}
            <TextField
              fullWidth
              label="Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              multiline
              rows={3}
              size="small"
              placeholder="Enter a description or reasoning for this relationship..."
              sx={{
                '& .MuiOutlinedInput-root': {
                  fontSize: '0.8125rem',
                  '&:hover fieldset': {
                    borderColor: '#5B6FE5',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#5B6FE5',
                  },
                },
                '& .MuiInputLabel-root': {
                  fontSize: '0.8125rem',
                  '&.Mui-focused': {
                    color: '#5B6FE5',
                  },
                },
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 1, gap: 0.75, justifyContent: 'flex-end' }}>
          <Button
            onClick={handleCloseDialog}
            variant="outlined"
            size="small"
            sx={{
              px: 1.25,
              py: 0.375,
              minWidth: 'auto',
              color: '#64748B',
              borderColor: '#CBD5E1',
              fontSize: '0.75rem',
              textTransform: 'none',
              borderRadius: '6px',
              '&:hover': {
                bgcolor: '#F8FAFC',
                borderColor: '#94A3B8',
                color: '#475569',
              },
            }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            variant="contained"
            size="small"
            sx={{
              px: 1.25,
              py: 0.375,
              minHeight: 'auto',
              bgcolor: '#5B6FE5',
              color: '#FFFFFF',
              fontSize: '0.75rem',
              fontWeight: 500,
              textTransform: 'none',
              borderRadius: '6px',
              boxShadow: '0 1px 3px 0 rgba(91, 111, 229, 0.2)',
              '&:hover': {
                bgcolor: '#4C5FD5',
                boxShadow: '0 2px 6px 0 rgba(91, 111, 229, 0.3)',
              },
            }}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

