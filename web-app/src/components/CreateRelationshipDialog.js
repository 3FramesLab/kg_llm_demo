import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Autocomplete,
  Box,
  Typography,
  IconButton,
  Divider,
  Alert,
  CircularProgress,
  Slider,
  FormControl,
  FormControlLabel,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Checkbox,
} from '@mui/material';
import {
  Close as CloseIcon,
  ArrowForward as ArrowForwardIcon,
} from '@mui/icons-material';
import { createRelationship } from '../services/api';

/**
 * CreateRelationshipDialog Component
 * Modal dialog for creating column-level relationships between nodes with backend persistence
 *
 * Props:
 * - open: boolean - Controls dialog visibility
 * - onClose: () => void - Callback when dialog is closed
 * - allNodes: array - Array of all available nodes
 * - sourceNode: object - Pre-selected source node (optional)
 * - onCreateRelationship: (relationshipData) => void - Callback when relationship is created
 * - kgName: string - Knowledge graph name for API calls
 * - onRefresh: () => void - Callback to refresh graph data after creation
 * - existingRelationships: array - Array of existing relationships to check for duplicates
 */
export default function CreateRelationshipDialog({
  open,
  onClose,
  allNodes = [],
  sourceNode = null,
  onCreateRelationship,
  kgName = null,
  onRefresh = null,
  existingRelationships = [],
}) {
  // Table selections
  const [sourceTable, setSourceTable] = useState(sourceNode || null);
  const [targetTable, setTargetTable] = useState(null);

  // Multiple relationship configurations
  const [columnMappings, setColumnMappings] = useState([
    {
      id: Date.now(),
      sourceColumn: '',
      targetColumn: '',
      relationshipType: 'MATCHES',
      confidence: 0.8,
      bidirectional: true,
      _comment: '',
    }
  ]);

  // UI state
  const [error, setError] = useState('');
  const [warning, setWarning] = useState('');
  const [loading, setLoading] = useState(false);

  // Common relationship types
  const relationshipTypes = [
    'MATCHES',
    'REFERENCES',
    'REFERENCED_BY',
    'RELATED_TO',
  ].sort();

  // Helper function to get columns from a node
  const getColumnsFromNode = (node) => {
    if (!node) return [];

    // Check if node has columns in properties
    const columns = node.properties?.columns || [];
    return columns.map(col => col.name || col);
  };

  // Get available source columns
  const sourceColumns = getColumnsFromNode(sourceTable);

  // Get available target columns
  const targetColumns = getColumnsFromNode(targetTable);

  // Reset form when dialog closes
  useEffect(() => {
    if (!open) {
      if (!sourceNode) {
        setSourceTable(null);
      }
      setTargetTable(null);
      setColumnMappings([
        {
          id: Date.now(),
          sourceColumn: '',
          targetColumn: '',
          relationshipType: 'MATCHES',
          confidence: 0.8,
          bidirectional: true,
          _comment: '',
        }
      ]);
      setError('');
      setWarning('');
    }
  }, [open, sourceNode]);

  // Helper functions for managing column mappings
  const handleAddMapping = () => {
    setColumnMappings([
      ...columnMappings,
      {
        id: Date.now() + Math.random(),
        sourceColumn: '',
        targetColumn: '',
        relationshipType: 'MATCHES',
        confidence: 0.8,
        bidirectional: true,
        _comment: '',
      }
    ]);
  };

  const handleRemoveMapping = (id) => {
    if (columnMappings.length > 1) {
      setColumnMappings(columnMappings.filter(m => m.id !== id));
    }
  };

  const handleUpdateMapping = (id, field, value) => {
    setColumnMappings(columnMappings.map(m =>
      m.id === id ? { ...m, [field]: value } : m
    ));
  };

  const getValidMappingsCount = () => {
    return columnMappings.filter(m =>
      m.sourceColumn && m.targetColumn && m.relationshipType.trim()
    ).length;
  };

  // Update source table when sourceNode prop changes
  useEffect(() => {
    if (sourceNode) {
      setSourceTable(sourceNode);
    }
  }, [sourceNode]);

  // Reset column mappings when source or target table changes
  useEffect(() => {
    setColumnMappings([
      {
        id: Date.now(),
        sourceColumn: '',
        targetColumn: '',
        relationshipType: 'MATCHES',
        confidence: 0.8,
        bidirectional: true,
        _comment: '',
      }
    ]);
    setError('');
    setWarning('');
  }, [sourceTable, targetTable]);

  // Real-time duplicate checking as user fills the form
  useEffect(() => {
    if (!sourceTable || !targetTable) {
      setError('');
      setWarning('');
      return;
    }

    // Check each mapping for duplicates
    const validMappings = columnMappings.filter(m =>
      m.sourceColumn && m.targetColumn && m.relationshipType.trim()
    );

    if (validMappings.length === 0) {
      setError('');
      setWarning('');
      return;
    }

    // Check for duplicates
    for (const mapping of validMappings) {
      const duplicateCheck = checkDuplicateRelationship(
        mapping.sourceColumn,
        mapping.targetColumn,
        mapping.relationshipType
      );

      if (duplicateCheck && duplicateCheck.type === 'exact') {
        setError(duplicateCheck.message);
        setWarning('');
        return;
      }

      if (duplicateCheck && duplicateCheck.type === 'warning') {
        setWarning(duplicateCheck.message);
        setError('');
        return;
      }
    }

    // Clear errors and warnings if no duplicates found
    setError('');
    setWarning('');
  }, [columnMappings, sourceTable, targetTable, existingRelationships]);

  // Check if relationship already exists (enhanced with relationship type checking)
  const checkDuplicateRelationship = (srcCol, tgtCol, relType) => {
    if (!srcCol || !tgtCol || !sourceTable || !targetTable || !relType) return null;

    // Normalize relationship type for comparison
    const normalizedRelType = relType.trim().toUpperCase().replace(/\s+/g, '_');

    // Check for exact duplicate (same source, target, columns, and type)
    const exactDuplicate = existingRelationships.find(rel => {
      const relTypeNormalized = (rel.relationship_type || rel.type || '').trim().toUpperCase().replace(/\s+/g, '_');

      const matchesSourceTarget =
        rel.source_id === sourceTable.id &&
        rel.target_id === targetTable.id;

      const matchesColumns =
        rel.source_column === srcCol &&
        rel.target_column === tgtCol;

      const matchesType = relTypeNormalized === normalizedRelType;

      return matchesSourceTarget && matchesColumns && matchesType;
    });

    if (exactDuplicate) {
      return {
        type: 'exact',
        relationship: exactDuplicate,
        message: `A relationship of type '${normalizedRelType}' already exists between ${sourceTable.name || sourceTable.id} (${srcCol}) and ${targetTable.name || targetTable.id} (${tgtCol})`
      };
    }

    // Check for reverse direction duplicate (B→A when creating A→B with same type)
    const reverseDuplicate = existingRelationships.find(rel => {
      const relTypeNormalized = (rel.relationship_type || rel.type || '').trim().toUpperCase().replace(/\s+/g, '_');

      const matchesReverseSourceTarget =
        rel.source_id === targetTable.id &&
        rel.target_id === sourceTable.id;

      const matchesReverseColumns =
        rel.source_column === tgtCol &&
        rel.target_column === srcCol;

      const matchesType = relTypeNormalized === normalizedRelType;

      return matchesReverseSourceTarget && matchesReverseColumns && matchesType;
    });

    if (reverseDuplicate) {
      return {
        type: 'exact',
        relationship: reverseDuplicate,
        message: `A reverse relationship of type '${normalizedRelType}' already exists: ${targetTable.name || targetTable.id} (${tgtCol}) → ${sourceTable.name || sourceTable.id} (${srcCol})`
      };
    }

    // Check for same columns but different type (warning, not blocking)
    const sameColumnsDifferentType = existingRelationships.find(rel => {
      const relTypeNormalized = (rel.relationship_type || rel.type || '').trim().toUpperCase().replace(/\s+/g, '_');

      const matchesSourceTarget =
        rel.source_id === sourceTable.id &&
        rel.target_id === targetTable.id;

      const matchesColumns =
        rel.source_column === srcCol &&
        rel.target_column === tgtCol;

      const differentType = relTypeNormalized !== normalizedRelType;

      return matchesSourceTarget && matchesColumns && differentType;
    });

    if (sameColumnsDifferentType) {
      const existingType = (sameColumnsDifferentType.relationship_type || sameColumnsDifferentType.type || '').trim().toUpperCase().replace(/\s+/g, '_');
      return {
        type: 'warning',
        relationship: sameColumnsDifferentType,
        message: `Note: A relationship of type '${existingType}' already exists between these columns. You're creating a different type: '${normalizedRelType}'`
      };
    }

    return null;
  };

  // Check for duplicate mappings within the current form
  const hasDuplicateMappings = () => {
    const seen = new Set();
    for (const mapping of columnMappings) {
      if (mapping.sourceColumn && mapping.targetColumn) {
        const key = `${mapping.sourceColumn}-${mapping.targetColumn}`;
        if (seen.has(key)) {
          return true;
        }
        seen.add(key);
      }
    }
    return false;
  };

  const handleCreateRelationship = async () => {
    // Validation
    if (!sourceTable) {
      setError('Source table is required');
      return;
    }

    if (!targetTable) {
      setError('Target table is required');
      return;
    }

    const validMappings = columnMappings.filter(m =>
      m.sourceColumn && m.targetColumn && m.relationshipType.trim()
    );

    if (validMappings.length === 0) {
      setError('At least one complete column mapping is required');
      return;
    }

    // Check for duplicate mappings within the form
    if (hasDuplicateMappings()) {
      setError('Duplicate column mappings detected. Each column pair must be unique.');
      return;
    }

    // Check for self-referencing relationships
    for (const mapping of validMappings) {
      if (sourceTable.id === targetTable.id && mapping.sourceColumn === mapping.targetColumn) {
        setError('Cannot create a relationship from a column to itself');
        return;
      }
    }

    // Check for duplicate relationships with existing data
    const warnings = [];
    for (const mapping of validMappings) {
      const duplicateCheck = checkDuplicateRelationship(
        mapping.sourceColumn,
        mapping.targetColumn,
        mapping.relationshipType
      );

      if (duplicateCheck && duplicateCheck.type === 'exact') {
        setError(duplicateCheck.message);
        setWarning('');
        return;
      }

      if (duplicateCheck && duplicateCheck.type === 'warning') {
        warnings.push(duplicateCheck.message);
      }
    }

    // Set warning if any found (but allow to proceed)
    if (warnings.length > 0) {
      setWarning(warnings[0]); // Show first warning
    } else {
      setWarning('');
    }

    // Validate confidence ranges
    for (const mapping of validMappings) {
      if (mapping.confidence < 0 || mapping.confidence > 1) {
        setError('Confidence must be between 0 and 1');
        return;
      }
    }

    setError('');
    setLoading(true);

    try {
      // If kgName is provided, use backend API integration
      if (kgName) {
        // Create all valid mappings using standardized 8-field format
        for (const mapping of validMappings) {
          const relData = {
            source_id: sourceTable.id,
            target_id: targetTable.id,
            relationship_type: mapping.relationshipType.trim().toUpperCase().replace(/\s+/g, '_'),
            source_column: mapping.sourceColumn,
            target_column: mapping.targetColumn,
            properties: {
              confidence: mapping.confidence,
              bidirectional: mapping.bidirectional !== undefined ? mapping.bidirectional : true,
              _comment: mapping._comment || '',
              source: 'manual',
              created_at: new Date().toISOString(),
              source_table: sourceTable.label || sourceTable.id,
              target_table: targetTable.label || targetTable.id,
            },
          };

          const response = await createRelationship(kgName, relData);

          if (!response.data.success) {
            setError(`Failed to create relationship for ${mapping.sourceColumn} -> ${mapping.targetColumn}`);
            setLoading(false);
            return;
          }
        }

        // Refresh graph data from backend if callback provided
        if (onRefresh) {
          await onRefresh();
        }

        // Close dialog on success
        onClose();
      } else {
        // Fallback to client-side only mode (for backward compatibility) - using standardized format
        for (const mapping of validMappings) {
          const newRelationship = {
            id: `manual_rel_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`,
            source: sourceTable.id,
            target: targetTable.id,
            source_id: sourceTable.id,
            target_id: targetTable.id,
            source_table: sourceTable.label || sourceTable.id,
            source_column: mapping.sourceColumn,
            target_table: targetTable.label || targetTable.id,
            target_column: mapping.targetColumn,
            type: mapping.relationshipType.trim().toUpperCase().replace(/\s+/g, '_'),
            relationship_type: mapping.relationshipType.trim().toUpperCase().replace(/\s+/g, '_'),
            confidence: mapping.confidence,
            bidirectional: mapping.bidirectional !== undefined ? mapping.bidirectional : true,
            _comment: mapping._comment || '',
            properties: {
              confidence: mapping.confidence,
              bidirectional: mapping.bidirectional !== undefined ? mapping.bidirectional : true,
              _comment: mapping._comment || '',
              source: 'manual',
              created_at: new Date().toISOString(),
              source_table: sourceTable.label || sourceTable.id,
              target_table: targetTable.label || targetTable.id,
            },
            isManuallyAdded: true,
          };

          // Call the callback
          if (onCreateRelationship) {
            onCreateRelationship(newRelationship);
          }
        }
        onClose();
      }
    } catch (error) {
      console.error('Error creating relationship:', error);
      setError(error.response?.data?.detail || 'Failed to create relationship. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog
      open={open}
      onClose={!loading ? onClose : undefined}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 1.5,
        },
      }}
    >
      <DialogTitle sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        pb: 0.5,
        pt: 1.25,
        px: 1.5,
        fontWeight: 700,
        color: '#1F2937',
        fontSize: '1.0625rem'
      }}>
        Create Relationship
        <IconButton onClick={onClose} size="small" disabled={loading} sx={{ padding: '4px' }}>
          <CloseIcon fontSize="small" />
        </IconButton>
      </DialogTitle>

      <Divider />

      <DialogContent sx={{ pt: 1.25, px: 1.5, pb: 1 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 1, py: 0.5 }} onClose={() => setError('')}>
            <Typography variant="body2" sx={{ fontSize: '0.8125rem' }}>
              {error}
            </Typography>
          </Alert>
        )}

        {warning && !error && (
          <Alert severity="warning" sx={{ mb: 1, py: 0.5 }} onClose={() => setWarning('')}>
            <Typography variant="body2" sx={{ fontSize: '0.8125rem' }}>
              {warning}
            </Typography>
          </Alert>
        )}

        {/* Table Selection Row */}
        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: 1.5, mb: 1 }}>
          {/* Left Column: Source Table */}
          <Box>
            <Typography
              sx={{
                fontSize: '0.7rem',
                fontWeight: 600,
                color: '#4B5563',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                mb: 0.75,
              }}
            >
              Source Table
            </Typography>
            <Autocomplete
              options={allNodes}
              value={sourceTable}
              onChange={(_, value) => setSourceTable(value)}
              getOptionLabel={(node) => {
                const aliasName = node.name || node.properties?.primary_alias || node.id;
                const tableName = node.label || node.id;
                if (aliasName !== tableName) {
                  return `${aliasName} (${tableName})`;
                }
                return aliasName;
              }}
              disabled={!!sourceNode || loading}
              size="small"
              renderInput={(params) => (
                <TextField
                  {...params}
                  placeholder="Select source table"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      fontSize: '0.8125rem',
                      bgcolor: '#FFFFFF',
                      '& fieldset': { borderColor: '#E5E7EB' },
                      '&:hover fieldset': { borderColor: '#D1D5DB' },
                      '&.Mui-focused fieldset': { borderColor: '#5B6FE5' },
                    },
                  }}
                />
              )}
              renderOption={(props, node) => {
                const { key, ...otherProps } = props;
                const aliasName = node.name || node.properties?.primary_alias || node.id;
                const tableName = node.label || node.id;

                return (
                  <Box component="li" key={key} {...otherProps}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                      <Box sx={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
                        <Typography variant="body2" sx={{ fontSize: '0.8125rem', fontWeight: 500 }}>
                          {aliasName}
                        </Typography>
                        {aliasName !== tableName && (
                          <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem' }}>
                            ({tableName})
                          </Typography>
                        )}
                      </Box>
                    </Box>
                  </Box>
                );
              }}
            />

            {sourceNode && (
              <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem', mt: 0.5, display: 'block' }}>
                Pre-selected from node details
              </Typography>
            )}
          </Box>

          {/* Middle Column: Arrow */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', px: 1,marginTop:sourceNode?'1.5rem':0 }}>
            <ArrowForwardIcon sx={{ fontSize: 28, color: '#5B6FE5' }} />
          </Box>

          {/* Right Column: Target Table */}
          <Box>
            <Typography
              sx={{
                fontSize: '0.7rem',
                fontWeight: 600,
                color: '#4B5563',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                mb: 0.75,
              }}
            >
              Target Table
            </Typography>
            <Autocomplete
              options={allNodes.filter(n => n.id !== sourceTable?.id)}
              value={targetTable}
              onChange={(_, value) => setTargetTable(value)}
              getOptionLabel={(node) => {
                const aliasName = node.name || node.properties?.primary_alias || node.id;
                const tableName = node.label || node.id;
                if (aliasName !== tableName) {
                  return `${aliasName} (${tableName})`;
                }
                return aliasName;
              }}
              disabled={loading}
              size="small"
              renderInput={(params) => (
                <TextField
                  {...params}
                  placeholder="Select target table"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      fontSize: '0.8125rem',
                      bgcolor: '#FFFFFF',
                      '& fieldset': { borderColor: '#E5E7EB' },
                      '&:hover fieldset': { borderColor: '#D1D5DB' },
                      '&.Mui-focused fieldset': { borderColor: '#5B6FE5' },
                    },
                  }}
                />
              )}
              renderOption={(props, node) => {
                const { key, ...otherProps} = props;
                const aliasName = node.name || node.properties?.primary_alias || node.id;
                const tableName = node.label || node.id;

                return (
                  <Box component="li" key={key} {...otherProps}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                      <Box sx={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
                        <Typography variant="body2" sx={{ fontSize: '0.8125rem', fontWeight: 500 }}>
                          {aliasName}
                        </Typography>
                        {aliasName !== tableName && (
                          <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem' }}>
                            ({tableName})
                          </Typography>
                        )}
                      </Box>
                    </Box>
                  </Box>
                );
              }}
            />
          </Box>
        </Box>

        {/* Horizontal Divider */}
        {sourceTable && targetTable && (
          <Divider sx={{ my: 1.25 }} />
        )}

        {/* Column Mappings Section */}
        {sourceTable && targetTable && (
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.75 }}>
              <Typography
                sx={{
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  color: '#6B7280',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                }}
              >
                Column Mappings
              </Typography>
              <Typography
                sx={{
                  fontSize: '0.7rem',
                  color: '#6B7280',
                }}
              >
                {getValidMappingsCount()} of {columnMappings.length} complete
              </Typography>
            </Box>

            {/* Render each column mapping */}
            {columnMappings.map((mapping) => (
              <Paper
                key={mapping.id}
                elevation={0}
                sx={{
                  p: 1,
                  mb: 1,
                  bgcolor: '#F9FAFB',
                  border: '1px solid #E5E7EB',
                  borderRadius: 1,
                }}
              >
                {/* 3-Column Grid for each mapping */}
                <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 0.75, mb: 0.75 }}>
                  {/* Source Column */}
                  <FormControl size="small">
                    <InputLabel sx={{ fontSize: '0.75rem' }}>Source Column *</InputLabel>
                    <Select
                      value={mapping.sourceColumn}
                      onChange={(e) => handleUpdateMapping(mapping.id, 'sourceColumn', e.target.value)}
                      label="Source Column *"
                      disabled={loading}
                      sx={{
                        fontSize: '0.8125rem',
                        bgcolor: '#FFFFFF',
                        '& .MuiOutlinedInput-notchedOutline': { borderColor: '#E5E7EB' },
                        '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#D1D5DB' },
                        '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#5B6FE5' },
                      }}
                    >
                      {sourceColumns.length === 0 ? (
                        <MenuItem disabled>
                          <Typography sx={{ fontSize: '0.75rem', color: '#9CA3AF', fontStyle: 'italic' }}>
                            No columns
                          </Typography>
                        </MenuItem>
                      ) : (
                        sourceColumns.map((col) => (
                          <MenuItem key={col} value={col} sx={{ fontSize: '0.8125rem' }}>
                            {col}
                          </MenuItem>
                        ))
                      )}
                    </Select>
                  </FormControl>

                  {/* Relationship Type */}
                  <FormControl size="small">
                    <InputLabel sx={{ fontSize: '0.75rem' }}>Type *</InputLabel>
                    <Select
                      value={mapping.relationshipType}
                      onChange={(e) => handleUpdateMapping(mapping.id, 'relationshipType', e.target.value)}
                      label="Type *"
                      disabled={loading}
                      sx={{
                        fontSize: '0.8125rem',
                        bgcolor: '#FFFFFF',
                        '& .MuiOutlinedInput-notchedOutline': { borderColor: '#E5E7EB' },
                        '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#D1D5DB' },
                        '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#5B6FE5' },
                      }}
                    >
                      {relationshipTypes.map((type) => (
                        <MenuItem key={type} value={type} sx={{ fontSize: '0.8125rem' }}>
                          {type}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>

                  {/* Target Column */}
                  <FormControl size="small">
                    <InputLabel sx={{ fontSize: '0.75rem' }}>Target Column *</InputLabel>
                    <Select
                      value={mapping.targetColumn}
                      onChange={(e) => handleUpdateMapping(mapping.id, 'targetColumn', e.target.value)}
                      label="Target Column *"
                      disabled={loading}
                      sx={{
                        fontSize: '0.8125rem',
                        bgcolor: '#FFFFFF',
                        '& .MuiOutlinedInput-notchedOutline': { borderColor: '#E5E7EB' },
                        '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#D1D5DB' },
                        '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#5B6FE5' },
                      }}
                    >
                      {targetColumns.length === 0 ? (
                        <MenuItem disabled>
                          <Typography sx={{ fontSize: '0.75rem', color: '#9CA3AF', fontStyle: 'italic' }}>
                            No columns
                          </Typography>
                        </MenuItem>
                      ) : (
                        targetColumns.map((col) => (
                          <MenuItem key={col} value={col} sx={{ fontSize: '0.8125rem' }}>
                            {col}
                          </MenuItem>
                        ))
                      )}
                    </Select>
                  </FormControl>
                </Box>

                {/* Confidence and Comment Row */}
                <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 0.75, mb: 0.75 }}>
                  {/* Confidence Slider */}
                  <Box>
                    <Typography
                      sx={{
                        fontSize: '0.7rem',
                        color: '#6B7280',
                        mb: 0.25,
                        fontWeight: 500,
                      }}
                    >
                      Confidence: {Math.round(mapping.confidence * 100)}%
                    </Typography>
                    <Slider
                      value={mapping.confidence}
                      onChange={(_, newValue) => handleUpdateMapping(mapping.id, 'confidence', newValue)}
                      min={0}
                      max={1}
                      step={0.05}
                      disabled={loading}
                      sx={{
                        color: '#5B6FE5',
                        '& .MuiSlider-thumb': {
                          width: 10,
                          height: 10,
                        },
                        '& .MuiSlider-track': {
                          height: 2,
                        },
                        '& .MuiSlider-rail': {
                          height: 2,
                          bgcolor: '#E5E7EB',
                        },
                      }}
                    />
                  </Box>

                  {/* Comment */}
                  <TextField
                    fullWidth
                    label="Comment"
                    size="small"
                    value={mapping._comment || ''}
                    onChange={(e) => handleUpdateMapping(mapping.id, '_comment', e.target.value)}
                    placeholder="Optional..."
                    disabled={loading}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        fontSize: '0.75rem',
                        bgcolor: '#FFFFFF',
                        '& fieldset': { borderColor: '#E5E7EB' },
                        '&:hover fieldset': { borderColor: '#D1D5DB' },
                        '&.Mui-focused fieldset': { borderColor: '#5B6FE5' },
                      },
                      '& .MuiInputLabel-root': {
                        fontSize: '0.75rem',
                      },
                    }}
                  />
                </Box>

                {/* Bidirectional Checkbox */}
                <Box sx={{ mb: 0.75 }}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={mapping.bidirectional !== undefined ? mapping.bidirectional : true}
                        onChange={(e) => handleUpdateMapping(mapping.id, 'bidirectional', e.target.checked)}
                        disabled={loading}
                        size="small"
                        sx={{
                          color: '#5B6FE5',
                          '&.Mui-checked': {
                            color: '#5B6FE5',
                          },
                        }}
                      />
                    }
                    label={
                      <Typography sx={{ fontSize: '0.75rem', color: '#6B7280' }}>
                        Bidirectional relationship
                      </Typography>
                    }
                  />
                </Box>

                {/* Remove Button */}
                {columnMappings.length > 1 && (
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                    <Button
                      onClick={() => handleRemoveMapping(mapping.id)}
                      disabled={loading}
                      size="small"
                      sx={{
                        color: '#EF4444',
                        fontSize: '0.7rem',
                        textTransform: 'none',
                        minWidth: 'auto',
                        px: 1,
                        py: 0.25,
                        '&:hover': { bgcolor: '#FEE2E2' },
                      }}
                    >
                      Remove
                    </Button>
                  </Box>
                )}
              </Paper>
            ))}

            {/* Add Mapping Button */}
            <Button
              onClick={handleAddMapping}
              disabled={loading}
              variant="outlined"
              size="small"
              fullWidth
              sx={{
                color: '#5B6FE5',
                borderColor: '#E5E7EB',
                fontSize: '0.75rem',
                textTransform: 'none',
                py: 0.5,
                '&:hover': {
                  borderColor: '#5B6FE5',
                  bgcolor: '#F9FAFB',
                },
              }}
            >
              + Add Column Mapping
            </Button>
          </Box>
        )}

      </DialogContent>

      <Divider />

      <DialogActions sx={{ px: 1.5, py: 0.75 }}>
        <Button
          onClick={onClose}
          disabled={loading}
          size="small"
        >
          Cancel
        </Button>
        <Button
          onClick={handleCreateRelationship}
          variant="contained"
          disabled={
            !sourceTable ||
            !targetTable ||
            getValidMappingsCount() === 0 ||
            loading
          }
          size="small"
        >
          {loading ? (
            <>
              <CircularProgress size={14} sx={{ color: '#FFFFFF', mr: 0.75 }} />
              Creating {getValidMappingsCount()} relationship{getValidMappingsCount() > 1 ? 's' : ''}...
            </>
          ) : (
            `Create ${getValidMappingsCount()} Relationship${getValidMappingsCount() > 1 ? 's' : ''}`
          )}
        </Button>
      </DialogActions>
    </Dialog>
  );
}


