import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  IconButton,
  Divider,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  FormControl,
  RadioGroup,
  FormControlLabel,
  Radio,
  Checkbox,
  TextField,
  Select,
  MenuItem,
  InputLabel,
  Tooltip,
} from '@mui/material';
import {
  Close as CloseIcon,
} from '@mui/icons-material';
import {
  createEntity,
  listDatabaseConnections,
  listDatabasesFromConnection,
  listTablesFromDatabase,
  getTableColumns,
} from '../services/api';

/**
 * AddNodeDialog Component
 * Multi-step modal dialog for creating new entities in the knowledge graph with backend persistence
 *
 * Props:
 * - open: boolean - Controls dialog visibility
 * - onClose: () => void - Callback when dialog is closed
 * - existingEntities: array - Array of existing entities to extract schemas and types
 * - onAddNode: (nodeData) => void - Callback when entity is added
 * - kgName: string - Knowledge graph name for API calls
 * - onRefresh: () => void - Callback to refresh graph data after creation
 */
export default function AddNodeDialog({
  open,
  onClose,
  existingEntities = [],
  onAddNode,
  kgName = null,
  onRefresh = null,
}) {
  // Multi-step workflow state
  const [currentStep, setCurrentStep] = useState(0);

  // Entity Name Input (moved to last step)
  const [entityName, setEntityName] = useState('');

  // Step 0: Source Selection
  const [dataSources, setDataSources] = useState([]);
  const [selectedSource, setSelectedSource] = useState(null);
  const [loadingSources, setLoadingSources] = useState(false);

  // Step 1: Schema Loading and Selection
  const [schemas, setSchemas] = useState([]);
  const [selectedSchema, setSelectedSchema] = useState(null);
  const [loadingSchemas, setLoadingSchemas] = useState(false);

  // Step 2: Table Loading and Selection (Single Selection)
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState('');
  const [loadingTables, setLoadingTables] = useState(false);

  // Step 3: Column Loading and Selection
  const [columns, setColumns] = useState([]);
  const [selectedColumns, setSelectedColumns] = useState([]);
  const [loadingColumns, setLoadingColumns] = useState(false);

  // General state
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const steps = [
    'Select Data Source',
    'Select Schema',
    'Select Table',
    'Select Columns',
    'Enter Entity Name',
  ];

  // Load data sources when dialog opens
  useEffect(() => {
    if (open) {
      loadDataSources();
    }
  }, [open]);

  // Reset form when dialog closes
  useEffect(() => {
    if (!open) {
      setCurrentStep(0);
      setEntityName('');
      setSelectedSource(null);
      setSelectedSchema(null);
      setSelectedTable('');
      setSelectedColumns([]);
      setSchemas([]);
      setTables([]);
      setColumns([]);
      setError('');
    }
  }, [open]);

  // Load schemas when source is selected
  useEffect(() => {
    if (selectedSource) {
      loadSchemas();
    }
  }, [selectedSource]);

  // Load tables when schema is selected
  useEffect(() => {
    if (selectedSchema && selectedSource) {
      loadTables();
    }
  }, [selectedSchema, selectedSource]);

  // Load columns when table is selected
  useEffect(() => {
    if (selectedTable && selectedSource && selectedSchema) {
      loadColumns();
    }
  }, [selectedTable, selectedSource, selectedSchema]);

  // Step 1: Load Data Sources
  const loadDataSources = async () => {
    setLoadingSources(true);
    setError('');
    try {
      const response = await listDatabaseConnections();
      if (response.data.success) {
        setDataSources(response.data.connections || []);
      }
    } catch (err) {
      console.error('Error loading data sources:', err);
      setError('Failed to load data sources. Please try again.');
    } finally {
      setLoadingSources(false);
    }
  };

  // Step 2: Load Schemas/Databases
  const loadSchemas = async () => {
    if (!selectedSource) return;

    setLoadingSchemas(true);
    setError('');
    setSchemas([]);
    setSelectedSchema(null);
    setTables([]);
    setSelectedTable('');
    setColumns([]);
    setSelectedColumns([]);

    try {
      // Skip loading schemas for Excel connections
      if (selectedSource.type === 'excel') {
        setError('Excel files are not yet supported for node creation. Please use a database connection.');
        setLoadingSchemas(false);
        return;
      }

      const response = await listDatabasesFromConnection(selectedSource.id);
      if (response.data.success) {
        const schemaList = response.data.databases || [];
        setSchemas(schemaList);
      }
    } catch (err) {
      console.error('Error loading schemas:', err);
      setError('Failed to load schemas. Please try again.');
    } finally {
      setLoadingSchemas(false);
    }
  };

  // Step 3: Load Tables
  const loadTables = async () => {
    if (!selectedSource || !selectedSchema) return;

    setLoadingTables(true);
    setError('');
    setTables([]);
    setSelectedTable('');
    setColumns([]);
    setSelectedColumns([]);

    try {
      const response = await listTablesFromDatabase(selectedSource.id, selectedSchema);
      if (response.data.success) {
        const tableList = response.data.tables || [];
        setTables(tableList);
      }
    } catch (err) {
      console.error('Error loading tables:', err);
      setError('Failed to load tables. Please try again.');
    } finally {
      setLoadingTables(false);
    }
  };

  // Step 4: Load Columns
  const loadColumns = async () => {
    if (!selectedSource || !selectedSchema || !selectedTable) return;

    setLoadingColumns(true);
    setError('');

    try {
      const tableName = typeof selectedTable === 'string' ? selectedTable : selectedTable.name || selectedTable;
      const response = await getTableColumns(selectedSource.id, selectedSchema, tableName);

      if (response.data.success) {
        const columnsList = response.data.columns || [];
        setColumns(columnsList);

        // Auto-select all columns by default
        setSelectedColumns(columnsList.map(col => col.name));
      }
    } catch (err) {
      console.error('Error loading columns:', err);
      setError('Failed to load columns. Please try again.');
    } finally {
      setLoadingColumns(false);
    }
  };

  // Navigation handlers
  const handleNext = () => {
    setError('');

    // Validation for each step
    if (currentStep === 0 && !selectedSource) {
      setError('Please select a data source');
      return;
    }
    if (currentStep === 1 && !selectedSchema) {
      setError('Please select a schema');
      return;
    }
    if (currentStep === 2 && !selectedTable) {
      setError('Please select a table');
      return;
    }
    if (currentStep === 3 && selectedColumns.length === 0) {
      setError('Please select at least one column');
      return;
    }

    setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
  };

  const handleBack = () => {
    setError('');
    setCurrentStep(prev => Math.max(prev - 1, 0));
  };

  const canProceed = () => {
    switch (currentStep) {
      case 0:
        return selectedSource !== null && !loadingSources;
      case 1:
        return selectedSchema !== null && !loadingSchemas;
      case 2:
        return selectedTable !== '' && !loadingTables;
      case 3:
        return selectedColumns.length > 0 && !loadingColumns;
      case 4:
        return entityName.trim() !== '';
      default:
        return false;
    }
  };

  const handleToggleColumn = (columnName) => {
    setSelectedColumns(prev => {
      const isSelected = prev.includes(columnName);

      if (isSelected) {
        return prev.filter(col => col !== columnName);
      } else {
        return [...prev, columnName];
      }
    });
  };

  const handleToggleAllColumns = () => {
    const allColumns = columns || [];
    const currentSelected = selectedColumns || [];

    if (currentSelected.length === allColumns.length) {
      // Deselect all
      setSelectedColumns([]);
    } else {
      // Select all
      setSelectedColumns(allColumns.map(col => col.name));
    }
  };

  const handleAddEntity = async () => {
    // Validation
    if (!entityName.trim() || !selectedSource || !selectedSchema || !selectedTable) {
      setError('Please complete all steps');
      return;
    }

    if (selectedColumns.length === 0) {
      setError('Please select at least one column');
      return;
    }

    // If kgName is provided, use backend API integration
    if (kgName) {
      setLoading(true);
      try {
        const tableName = typeof selectedTable === 'string' ? selectedTable : selectedTable.name || selectedTable;

        const entityData = {
          name: entityName.trim(),
          labels: [tableName],
          properties: {
            schema: selectedSchema,
            source: selectedSource.name,
            source_type: selectedSource.type,
            primary_alias: entityName.trim(),
            source_table: tableName,
            columns: columns
              .filter(col => selectedColumns.includes(col.name))
              .map(col => ({
                name: col.name,
                type: col.type,
                nullable: col.nullable
              })),
          },
        };

        // Call backend API to create entity
        await createEntity(kgName, entityData);

        // Refresh graph data from backend if callback provided
        if (onRefresh) {
          await onRefresh();
        }

        // Close dialog on success
        onClose();
      } catch (error) {
        console.error('Error creating entity:', error);
        setError(error.response?.data?.detail || 'Failed to create entity. Please try again.');
      } finally {
        setLoading(false);
      }
    } else {
      // Fallback to client-side only mode (for backward compatibility)
      const tableName = typeof selectedTable === 'string' ? selectedTable : selectedTable.name || selectedTable;

      const newNode = {
        id: `manual_node_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
        name: entityName.trim(),
        labels: [tableName],
        primaryLabel: tableName,
        type: tableName,
        properties: {
          schema: selectedSchema,
          source: selectedSource.name,
          source_type: selectedSource.type,
          primary_alias: entityName.trim(),
          source_table: tableName,
          columns: columns
            .filter(col => selectedColumns.includes(col.name))
            .map(col => ({
              name: col.name,
              type: col.type,
              nullable: col.nullable
            })),
        },
        isManuallyAdded: true,
      };

      if (onAddNode) {
        onAddNode(newNode);
      }
      onClose();
    }
  };

  // Render step content
  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return renderSourceSelection();
      case 1:
        return renderSchemaSelection();
      case 2:
        return renderTableSelection();
      case 3:
        return renderColumnSelection();
      case 4:
        return renderEntityNameInput();
      default:
        return null;
    }
  };

  const renderEntityNameInput = () => (
    <Box>
      <Typography variant="body2" sx={{ mb: 1.25, color: '#6B7280', fontSize: '0.875rem' }}>
        Enter a meaningful name for this entity (primary alias)
      </Typography>

      <TextField
        fullWidth
        label="Entity Name"
        placeholder="e.g., User Activities, Material Master, etc."
        value={entityName}
        onChange={(e) => setEntityName(e.target.value)}
        required
        autoFocus
        sx={{
          '& .MuiOutlinedInput-root': {
            bgcolor: '#F9FAFB',
            '& fieldset': {
              borderColor: '#E5E7EB',
            },
            '&:hover fieldset': {
              borderColor: '#D1D5DB',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#5B6FE5',
            },
          },
          '& .MuiInputLabel-root': {
            color: '#6B7280',
            fontSize: '0.875rem',
            '&.Mui-focused': {
              color: '#5B6FE5',
            },
          },
          '& .MuiInputBase-input': {
            fontSize: '0.875rem',
            color: '#1F2937',
          },
        }}
      />

      <Alert severity="info" sx={{ mt: 1.5, py: 0.5 }}>
        <Typography variant="body2" sx={{ fontSize: '0.8125rem' }}>
          This name will be used as the primary identifier for the entity in the knowledge graph.
        </Typography>
      </Alert>
    </Box>
  );

  const renderSourceSelection = () => (
    <Box>
      <Typography variant="body2" sx={{ mb: 1.25, color: '#6B7280', fontSize: '0.875rem' }}>
        Select a data source to begin creating entities from your database
      </Typography>

      {loadingSources ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 2.5 }}>
          <CircularProgress size={28} sx={{ color: '#5B6FE5' }} />
        </Box>
      ) : dataSources.length === 0 ? (
        <Alert severity="info" sx={{ fontSize: '0.8125rem', py: 0.5 }}>
          No data sources available. Please add a database connection first.
        </Alert>
      ) : (
        <FormControl component="fieldset" fullWidth>
          <RadioGroup
            value={selectedSource?.id || ''}
            onChange={(e) => {
              const source = dataSources.find(s => s.id === e.target.value);
              setSelectedSource(source);
            }}
          >
            {dataSources.map((source) => (
              <FormControlLabel
                key={source.id}
                value={source.id}
                control={
                  <Radio
                    sx={{
                      color: '#D1D5DB',
                      '&.Mui-checked': { color: '#5B6FE5' },
                      padding: '6px'
                    }}
                  />
                }
                label={
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 600, fontSize: '0.875rem' }}>
                      {source.name}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.75rem' }}>
                      {source.type} • {source.host}:{source.port}
                    </Typography>
                  </Box>
                }
                sx={{
                  border: '1px solid #E5E7EB',
                  borderRadius: 1,
                  mb: 0.75,
                  px: 1,
                  py: 0.5,
                  '&:hover': {
                    bgcolor: '#F9FAFB',
                  },
                }}
              />
            ))}
          </RadioGroup>
        </FormControl>
      )}
    </Box>
  );

  const renderSchemaSelection = () => (
    <Box>
      <Typography variant="body2" sx={{ mb: 1.25, color: '#6B7280', fontSize: '0.875rem' }}>
        Select a schema/database from <strong>{selectedSource?.name}</strong>
      </Typography>

      {loadingSchemas ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 2.5 }}>
          <CircularProgress size={28} sx={{ color: '#5B6FE5' }} />
        </Box>
      ) : schemas.length === 0 ? (
        <Alert severity="warning" sx={{ fontSize: '0.8125rem', py: 0.5 }}>
          No schemas found in this data source.
        </Alert>
      ) : (
        <FormControl component="fieldset" fullWidth>
          <RadioGroup
            value={selectedSchema || ''}
            onChange={(e) => setSelectedSchema(e.target.value)}
          >
            {schemas.map((schema) => (
              <FormControlLabel
                key={schema}
                value={schema}
                control={
                  <Radio
                    sx={{
                      color: '#D1D5DB',
                      '&.Mui-checked': { color: '#5B6FE5' },
                      padding: '6px'
                    }}
                  />
                }
                label={
                  <Typography variant="body2" sx={{ fontSize: '0.875rem' }}>
                    {schema}
                  </Typography>
                }
                sx={{
                  border: '1px solid #E5E7EB',
                  borderRadius: 1,
                  mb: 0.75,
                  px: 1,
                  py: 0.5,
                  '&:hover': {
                    bgcolor: '#F9FAFB',
                  },
                }}
              />
            ))}
          </RadioGroup>
        </FormControl>
      )}
    </Box>
  );

  const renderTableSelection = () => {
    // Helper function to check if a table already exists in the KG
    const isTableInKG = (tableName) => {
      return existingEntities.some(entity => {
        const entityLabel = entity.label || entity.name || '';
        const entitySourceTable = entity.properties?.source_table || entity.source_table || '';
        return entityLabel.toLowerCase() === tableName.toLowerCase() ||
               entitySourceTable.toLowerCase() === tableName.toLowerCase();
      });
    };

    // Filter and categorize tables
    const availableTables = [];
    const existingTables = [];

    tables.forEach(table => {
      const tableName = typeof table === 'string' ? table : table.name || table;
      if (isTableInKG(tableName)) {
        existingTables.push({ name: tableName, disabled: true });
      } else {
        availableTables.push({ name: tableName, disabled: false });
      }
    });

    return (
      <Box>
        <Typography variant="body2" sx={{ mb: 1.25, color: '#6B7280', fontSize: '0.875rem' }}>
          Select a table from <strong>{selectedSchema}</strong>
        </Typography>

        {loadingTables ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 2.5 }}>
            <CircularProgress size={28} sx={{ color: '#5B6FE5' }} />
          </Box>
        ) : tables.length === 0 ? (
          <Alert severity="warning" sx={{ fontSize: '0.8125rem', py: 0.5 }}>
            No tables found in this schema.
          </Alert>
        ) : (
          <>
            <FormControl fullWidth>
              <InputLabel
                sx={{
                  color: '#6B7280',
                  fontSize: '0.875rem',
                  '&.Mui-focused': {
                    color: '#5B6FE5',
                  },
                }}
              >
                Select Table
              </InputLabel>
              <Select
                value={selectedTable}
                onChange={(e) => setSelectedTable(e.target.value)}
                label="Select Table"
                sx={{
                  bgcolor: '#F9FAFB',
                  '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: '#E5E7EB',
                  },
                  '&:hover .MuiOutlinedInput-notchedOutline': {
                    borderColor: '#D1D5DB',
                  },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: '#5B6FE5',
                  },
                  '& .MuiSelect-select': {
                    fontSize: '0.875rem',
                    color: '#1F2937',
                  },
                }}
              >
                {availableTables.map((table) => (
                  <MenuItem
                    key={table.name}
                    value={table.name}
                    sx={{
                      fontSize: '0.875rem',
                      '&:hover': {
                        bgcolor: '#F9FAFB',
                      },
                      '&.Mui-selected': {
                        bgcolor: '#F0F4FF',
                        '&:hover': {
                          bgcolor: '#E8EFFF',
                        },
                      },
                    }}
                  >
                    {table.name}
                  </MenuItem>
                ))}
                {existingTables.map((table) => (
                  <MenuItem
                    key={table.name}
                    value={table.name}
                    disabled
                    sx={{
                      fontSize: '0.875rem',
                      color: '#9CA3AF',
                      '&.Mui-disabled': {
                        opacity: 0.6,
                      },
                    }}
                  >
                    <Tooltip title="This table is already in the Knowledge Graph" placement="left">
                      <Box component="span">
                        {table.name} (Already in KG)
                      </Box>
                    </Tooltip>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {existingTables.length > 0 && (
              <Alert severity="info" sx={{ mt: 1.5, py: 0.5 }}>
                <Typography variant="body2" sx={{ fontSize: '0.8125rem' }}>
                  {existingTables.length} table(s) are already in the Knowledge Graph and cannot be selected.
                </Typography>
              </Alert>
            )}
          </>
        )}
      </Box>
    );
  };

  const renderColumnSelection = () => {
    const tableName = typeof selectedTable === 'string' ? selectedTable : selectedTable.name || selectedTable;

    return (
      <Box>
        <Typography variant="body2" sx={{ mb: 1.25, color: '#6B7280', fontSize: '0.875rem' }}>
          Select columns for <strong>{tableName}</strong>
        </Typography>

        {loadingColumns ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 2.5 }}>
            <CircularProgress size={28} sx={{ color: '#5B6FE5' }} />
          </Box>
        ) : (
          <Box>
            <Box sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              mb: 0.75,
              pb: 0.5,
              borderBottom: '2px solid #E5E7EB'
            }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, fontSize: '0.875rem' }}>
                Columns ({selectedColumns.length} of {columns.length} selected)
              </Typography>
              <Button
                size="small"
                onClick={handleToggleAllColumns}
                sx={{
                  textTransform: 'none',
                  fontSize: '0.75rem',
                  color: '#5B6FE5',
                  minWidth: 'auto',
                  padding: '2px 6px',
                }}
              >
                {selectedColumns.length === columns.length ? 'Deselect All' : 'Select All'}
              </Button>
            </Box>

            <Box sx={{
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gap: 1,
              maxHeight: 400,
              overflow: 'auto',
              py: 1
            }}>
              {columns.map((column) => {
                const isSelected = selectedColumns.includes(column.name);

                return (
                  <Box
                    key={column.name}
                    onClick={() => handleToggleColumn(column.name)}
                    sx={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: 0.5,
                      p: 0.75,
                      border: '1px solid #E5E7EB',
                      borderRadius: 1,
                      cursor: 'pointer',
                      bgcolor: isSelected ? '#F0F4FF' : '#FFFFFF',
                      '&:hover': {
                        bgcolor: isSelected ? '#E8EFFF' : '#F9FAFB',
                      },
                    }}
                  >
                    <Checkbox
                      checked={isSelected}
                      tabIndex={-1}
                      disableRipple
                      sx={{
                        color: '#D1D5DB',
                        '&.Mui-checked': { color: '#5B6FE5' },
                        padding: 0,
                        mt: 0.25,
                      }}
                    />
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                      <Typography
                        variant="body2"
                        sx={{
                          fontSize: '0.8125rem',
                          fontWeight: isSelected ? 600 : 400,
                          color: '#1F2937',
                          wordBreak: 'break-word',
                        }}
                      >
                        {column.name}
                      </Typography>
                      <Typography
                        variant="caption"
                        sx={{
                          fontSize: '0.7rem',
                          color: '#6B7280',
                        }}
                      >
                        {column.type}
                      </Typography>
                    </Box>
                  </Box>
                );
              })}
            </Box>
          </Box>
        )}
      </Box>
    );
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
        px: 1.5
      }}>
        <Typography variant="h6" component="div" sx={{ fontWeight: 700, color: '#1F2937', fontSize: '1.0625rem' }}>
          Add New Entity
        </Typography>
        <IconButton onClick={onClose} size="small" disabled={loading} sx={{ padding: '4px' }}>
          <CloseIcon fontSize="small" />
        </IconButton>
      </DialogTitle>

      <Divider />

      <DialogContent sx={{ pt: 1.5, px: 1.5, pb: 1 }}>
        {/* Stepper */}
        <Stepper activeStep={currentStep} sx={{ mb: 2 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel
                sx={{
                  '& .MuiStepLabel-label': {
                    fontSize: '0.8125rem',
                    '&.Mui-active': {
                      color: '#5B6FE5',
                      fontWeight: 600,
                    },
                  },
                  '& .MuiStepIcon-root': {
                    fontSize: '1.25rem',
                    '&.Mui-active': {
                      color: '#5B6FE5',
                    },
                    '&.Mui-completed': {
                      color: '#5B6FE5',
                    },
                  },
                }}
              >
                {label}
              </StepLabel>
            </Step>
          ))}
        </Stepper>

        {error && (
          <Alert severity="error" sx={{ mb: 1.5, py: 0.5 }} onClose={() => setError('')}>
            <Typography variant="body2" sx={{ fontSize: '0.8125rem' }}>
              {error}
            </Typography>
          </Alert>
        )}

        {/* Step Content */}
        {renderStepContent()}
      </DialogContent>

      <Divider />

      <DialogActions sx={{ px: 1.5, py: 1, gap: 0.5 }}>
        <Button
          onClick={onClose}
          disabled={loading}
          size="small"
        >
          Cancel
        </Button>

        {currentStep > 0 && (
          <Button
            onClick={handleBack}
            disabled={loading}
            size="small"
          >
            Back
          </Button>
        )}

        {currentStep < steps.length - 1 ? (
          <Button
            onClick={handleNext}
            variant="contained"
            disabled={!canProceed()}
            size="small"
          >
            Next
          </Button>
        ) : (
          <Button
            onClick={handleAddEntity}
            variant="contained"
            disabled={!canProceed() || loading}
            size="small"
          >
            {loading ? (
              <>
                <CircularProgress size={14} sx={{ color: '#FFFFFF', mr: 0.75 }} />
                Creating...
              </>
            ) : (
              'Create Entity'
            )}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
}
