import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  TextField,
  Typography,
  Alert,
  AlertTitle,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Collapse,
  Checkbox,
  Button,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Radio,
  RadioGroup,
  FormControlLabel,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  KeyboardArrowDown as KeyboardArrowDownIcon,
  KeyboardArrowUp as KeyboardArrowUpIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Close as CloseIcon,
  Info as InfoIcon,
  AutoAwesome as AutoAwesomeIcon,
  CloudOff as CloudOffIcon,
} from '@mui/icons-material';
import { generateTableAliases, generateColumnAliases, getTableColumns } from '../../../services/api';

/**
 * AliasesStep Component
 * Step 3: Aliases - Generate and manage table aliases with column selection
 */
function AliasesStep({ selectedTables, onDataChange }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [aliasesData, setAliasesData] = useState([]);
  const [editingRow, setEditingRow] = useState(null);
  const [editValue, setEditValue] = useState('');
  const [expandedRows, setExpandedRows] = useState({});
  const [columnsData, setColumnsData] = useState({});
  const [selectedColumns, setSelectedColumns] = useState({});
  const [columnAliases, setColumnAliases] = useState({}); // { tableKey: { columnName: [alias1, alias2, ...] } }
  const [primaryAliases, setPrimaryAliases] = useState({}); // { tableKey: primaryAliasString }

  // Dialog state for table alias management
  const [dialogOpen, setDialogOpen] = useState(false);
  const [currentTableKey, setCurrentTableKey] = useState(null);
  const [newAliasInput, setNewAliasInput] = useState('');
  const [isEditMode, setIsEditMode] = useState(false);
  const [editingAliasOriginal, setEditingAliasOriginal] = useState('');

  // Dialog state for column alias management
  const [columnDialogOpen, setColumnDialogOpen] = useState(false);
  const [currentColumnTableKey, setCurrentColumnTableKey] = useState(null);
  const [currentColumnName, setCurrentColumnName] = useState(null);
  const [newColumnAliasInput, setNewColumnAliasInput] = useState('');
  const [isColumnEditMode, setIsColumnEditMode] = useState(false);
  const [editingColumnAliasOriginal, setEditingColumnAliasOriginal] = useState('');

  // Track if aliases have been generated for current tables to prevent duplicate API calls
  const generatedTablesRef = useRef('');
  const isInitialMount = useRef(true);

  // Create stable key from selectedTables to detect actual changes
  const selectedTablesKey = selectedTables.map(t => t.key).sort().join('|');

  useEffect(() => {
    // Only generate aliases if tables actually changed (not just reference change)
    if (selectedTables.length > 0 && selectedTablesKey !== generatedTablesRef.current) {
      generatedTablesRef.current = selectedTablesKey;
      generateAliases();
    } else if (selectedTables.length === 0) {
      // Clear aliases if no tables selected
      setAliasesData([]);
      generatedTablesRef.current = '';
    }
  }, [selectedTablesKey]);

  // Helper function to check if at least one column is selected across all tables
  const hasSelectedColumns = () => {
    return Object.values(selectedColumns).some(tableColumns =>
      Object.values(tableColumns).some(isSelected => isSelected)
    );
  };

  useEffect(() => {
    // Skip initial mount to prevent calling onDataChange before data is ready
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }

    // Pass data to parent component including validation state
    onDataChange({
      aliases: aliasesData,
      selectedColumns: selectedColumns,
      columnAliases: columnAliases,
      primaryAliases: primaryAliases,
      hasSelectedColumns: hasSelectedColumns(),
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [aliasesData, selectedColumns, columnAliases, primaryAliases]);

  const generateAliases = async () => {
    setLoading(true);
    setError(null);
    try {
      // Prepare tables data for API call
      const tablesForAPI = selectedTables.map(table => ({
        connectionId: table.connectionId,
        databaseName: table.databaseName,
        tableName: table.tableName,
        columns: [], // We'll load columns separately
      }));

      // Call LLM to generate aliases
      const response = await generateTableAliases({ tables: tablesForAPI });

      if (response.data.success) {
        const aliasesWithKeys = response.data.data.map(item => ({
          ...item,
          key: `${item.connectionId}:${item.databaseName}:${item.tableName}`,
          aliasString: item.aliases.join(', '),
          // Store confidence data if available
          aliasesWithConfidence: item.aliasesWithConfidence || item.aliases.map(alias => ({
            alias: alias,
            confidence: 0.8 // Default confidence for backward compatibility
          }))
        }));
        setAliasesData(aliasesWithKeys);

        // Set first alias as primary by default for each table
        const defaultPrimaryAliases = {};
        aliasesWithKeys.forEach(item => {
          if (item.aliases && item.aliases.length > 0) {
            defaultPrimaryAliases[item.key] = item.aliases[0];
          }
        });
        setPrimaryAliases(defaultPrimaryAliases);
      }
    } catch (err) {
      console.error('Error generating aliases:', err);
      const isNetworkError = err.code === 'ERR_NETWORK' || err.message === 'Network Error' || !err.response;
      setError({
        type: isNetworkError ? 'network' : 'server',
        message: isNetworkError
          ? 'Unable to connect to the backend server'
          : err.response?.data?.detail || 'Failed to generate aliases'
      });
    } finally {
      setLoading(false);
    }
  };

  const generateAllAliases = async () => {
    setLoading(true);
    try {
      // Step 1: Generate table aliases
      const tablesForAPI = selectedTables.map(table => ({
        connectionId: table.connectionId,
        databaseName: table.databaseName,
        tableName: table.tableName,
        columns: [],
      }));

      const tableResponse = await generateTableAliases({ tables: tablesForAPI });

      if (tableResponse.data.success) {
        const aliasesWithKeys = tableResponse.data.data.map(item => ({
          ...item,
          key: `${item.connectionId}:${item.databaseName}:${item.tableName}`,
          aliasString: item.aliases.join(', '),
          // Store confidence data if available
          aliasesWithConfidence: item.aliasesWithConfidence || item.aliases.map(alias => ({
            alias: alias,
            confidence: 0.8 // Default confidence for backward compatibility
          }))
        }));
        setAliasesData(aliasesWithKeys);

        // Set first alias as primary by default for each table
        const defaultPrimaryAliases = {};
        aliasesWithKeys.forEach(item => {
          if (item.aliases && item.aliases.length > 0) {
            defaultPrimaryAliases[item.key] = item.aliases[0];
          }
        });
        setPrimaryAliases(defaultPrimaryAliases);

        // Step 2: Load columns for all tables and generate column aliases
        const allColumnsData = {};
        const allColumnAliases = {};
        const allSelectedColumns = {};

        for (const row of aliasesWithKeys) {
          try {
            const columnsResponse = await getTableColumns(
              row.connectionId,
              row.databaseName,
              row.tableName
            );

            const columns = columnsResponse.data.columns || [];
            allColumnsData[row.key] = columns;

            // Initialize column selections
            const columnSelections = {};
            columns.forEach(col => {
              columnSelections[col.name] = false;
            });
            allSelectedColumns[row.key] = columnSelections;

            // Initialize column aliases as empty arrays
            const columnAliasesInit = {};
            columns.forEach(col => {
              columnAliasesInit[col.name] = [];
            });
            allColumnAliases[row.key] = columnAliasesInit;
          } catch (error) {
            console.error(`Error loading columns for ${row.tableName}:`, error);
          }
        }

        setColumnsData(allColumnsData);
        setSelectedColumns(allSelectedColumns);
        setColumnAliases(allColumnAliases);

        // Step 3: Generate column aliases for all columns
        const columnsForAliasGeneration = [];
        for (const tableKey in allColumnsData) {
          const columns = allColumnsData[tableKey];
          const tableInfo = aliasesWithKeys.find(t => t.key === tableKey);
          if (tableInfo) {
            columns.forEach(col => {
              columnsForAliasGeneration.push({
                tableName: tableInfo.tableName,
                columnName: col.name,
                columnType: col.type || '',
              });
            });
          }
        }

        if (columnsForAliasGeneration.length > 0) {
          const columnAliasResponse = await generateColumnAliases({
            columns: columnsForAliasGeneration,
          });

          if (columnAliasResponse.data.success) {
            // Populate column aliases
            const updatedColumnAliases = { ...allColumnAliases };
            columnAliasResponse.data.data.forEach(result => {
              // Find the table key for this column
              for (const tableKey in allColumnsData) {
                const tableInfo = aliasesWithKeys.find(t => t.key === tableKey);
                if (tableInfo && tableInfo.tableName === result.tableName) {
                  if (updatedColumnAliases[tableKey]) {
                    updatedColumnAliases[tableKey][result.columnName] = result.aliases;
                  }
                  break;
                }
              }
            });
            setColumnAliases(updatedColumnAliases);
          }
        }
      }
    } catch (error) {
      console.error('Error generating all aliases:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEditStart = (row) => {
    setEditingRow(row.key);
    setEditValue(row.aliasString);
  };

  const handleEditSave = (key) => {
    const updatedAliases = aliasesData.map(item => {
      if (item.key === key) {
        const newAliases = editValue.split(',').map(a => a.trim()).filter(a => a);
        return {
          ...item,
          aliases: newAliases,
          aliasString: newAliases.join(', '),
        };
      }
      return item;
    });
    setAliasesData(updatedAliases);
    setEditingRow(null);
    setEditValue('');
  };

  const handleEditCancel = () => {
    setEditingRow(null);
    setEditValue('');
  };

  const handleDelete = (key) => {
    setAliasesData(aliasesData.filter(item => item.key !== key));
  };

  // Open dialog to add new alias
  const handleOpenDialog = (tableKey) => {
    setCurrentTableKey(tableKey);
    setNewAliasInput('');
    setIsEditMode(false);
    setEditingAliasOriginal('');
    setDialogOpen(true);
  };

  // Open dialog to edit existing alias
  const handleEditAlias = (tableKey, aliasName) => {
    setCurrentTableKey(tableKey);
    setNewAliasInput(aliasName);
    setIsEditMode(true);
    setEditingAliasOriginal(aliasName);
    setDialogOpen(true);
  };

  // Close dialog
  const handleCloseDialog = () => {
    setDialogOpen(false);
    setCurrentTableKey(null);
    setNewAliasInput('');
    setIsEditMode(false);
    setEditingAliasOriginal('');
  };

  // Add new alias or update existing alias from dialog
  const handleAddAlias = () => {
    const trimmedAlias = newAliasInput.trim();

    // Validate that alias is not empty
    if (!trimmedAlias) {
      return;
    }

    const updatedAliases = aliasesData.map(item => {
      if (item.key === currentTableKey) {
        if (isEditMode) {
          // Edit mode: replace the old alias with the new one
          const newAliases = item.aliases.map(alias =>
            alias === editingAliasOriginal ? trimmedAlias : alias
          );
          return {
            ...item,
            aliases: newAliases,
            aliasString: newAliases.join(', '),
          };
        } else {
          // Add mode: check if alias already exists
          if (item.aliases.includes(trimmedAlias)) {
            return item;
          }

          const newAliases = [...item.aliases, trimmedAlias];
          return {
            ...item,
            aliases: newAliases,
            aliasString: newAliases.join(', '),
          };
        }
      }
      return item;
    });

    setAliasesData(updatedAliases);

    // If editing the primary alias, update it
    if (isEditMode && primaryAliases[currentTableKey] === editingAliasOriginal) {
      setPrimaryAliases(prev => ({
        ...prev,
        [currentTableKey]: trimmedAlias
      }));
    }
    // If this is the first alias being added, set it as primary
    else if (!isEditMode) {
      const tableData = updatedAliases.find(item => item.key === currentTableKey);
      if (tableData && tableData.aliases.length === 1) {
        setPrimaryAliases(prev => ({
          ...prev,
          [currentTableKey]: trimmedAlias
        }));
      }
    }

    setNewAliasInput('');
    handleCloseDialog();
  };

  // Delete individual alias from chip
  const handleDeleteAlias = (tableKey, aliasToDelete) => {
    const updatedAliases = aliasesData.map(item => {
      if (item.key === tableKey) {
        const newAliases = item.aliases.filter(alias => alias !== aliasToDelete);
        return {
          ...item,
          aliases: newAliases,
          aliasString: newAliases.join(', '),
        };
      }
      return item;
    });
    setAliasesData(updatedAliases);

    // If the deleted alias was the primary, set the first remaining alias as primary
    if (primaryAliases[tableKey] === aliasToDelete) {
      const tableData = updatedAliases.find(item => item.key === tableKey);
      if (tableData && tableData.aliases.length > 0) {
        setPrimaryAliases(prev => ({
          ...prev,
          [tableKey]: tableData.aliases[0]
        }));
      } else {
        // No aliases left, remove primary alias
        setPrimaryAliases(prev => {
          const newPrimary = { ...prev };
          delete newPrimary[tableKey];
          return newPrimary;
        });
      }
    }
  };

  // Handle primary alias selection
  const handlePrimaryAliasChange = (tableKey, aliasValue) => {
    setPrimaryAliases(prev => ({
      ...prev,
      [tableKey]: aliasValue
    }));
  };

  const handleRowExpand = async (row) => {
    const isExpanded = expandedRows[row.key];

    if (!isExpanded && !columnsData[row.key]) {
      // Load columns for this table
      try {
        const response = await getTableColumns(
          row.connectionId,
          row.databaseName,
          row.tableName
        );

        const columns = response.data.columns || [];
        setColumnsData(prev => ({
          ...prev,
          [row.key]: columns,
        }));

        // Initialize all columns as unselected by default
        const columnSelections = {};
        columns.forEach(col => {
          columnSelections[col.name] = false;
        });

        setSelectedColumns(prev => ({
          ...prev,
          [row.key]: columnSelections,
        }));

        // Initialize column aliases as empty arrays
        const columnAliasesInit = {};
        columns.forEach(col => {
          columnAliasesInit[col.name] = [];
        });

        setColumnAliases(prev => ({
          ...prev,
          [row.key]: columnAliasesInit,
        }));
      } catch (error) {
        console.error(`Error loading columns for ${row.tableName}:`, error);
      }
    }

    setExpandedRows(prev => ({
      ...prev,
      [row.key]: !isExpanded,
    }));
  };

  const handleColumnToggle = (tableKey, columnName) => {
    setSelectedColumns(prev => ({
      ...prev,
      [tableKey]: {
        ...prev[tableKey],
        [columnName]: !prev[tableKey]?.[columnName],
      },
    }));
  };

  const handleSelectAllColumns = (tableKey, selectAll) => {
    const columns = columnsData[tableKey] || [];
    const columnSelections = {};
    columns.forEach(col => {
      columnSelections[col.name] = selectAll;
    });

    setSelectedColumns(prev => ({
      ...prev,
      [tableKey]: columnSelections,
    }));
  };

  const getSelectedColumnCount = (tableKey) => {
    const selections = selectedColumns[tableKey] || {};
    return Object.values(selections).filter(Boolean).length;
  };

  // Column alias handlers
  const handleOpenColumnDialog = (tableKey, columnName) => {
    setCurrentColumnTableKey(tableKey);
    setCurrentColumnName(columnName);
    setNewColumnAliasInput('');
    setIsColumnEditMode(false);
    setEditingColumnAliasOriginal('');
    setColumnDialogOpen(true);
  };

  const handleEditColumnAlias = (tableKey, columnName, aliasName) => {
    setCurrentColumnTableKey(tableKey);
    setCurrentColumnName(columnName);
    setNewColumnAliasInput(aliasName);
    setIsColumnEditMode(true);
    setEditingColumnAliasOriginal(aliasName);
    setColumnDialogOpen(true);
  };

  const handleCloseColumnDialog = () => {
    setColumnDialogOpen(false);
    setCurrentColumnTableKey(null);
    setCurrentColumnName(null);
    setNewColumnAliasInput('');
    setIsColumnEditMode(false);
    setEditingColumnAliasOriginal('');
  };

  const handleAddColumnAlias = () => {
    const trimmedAlias = newColumnAliasInput.trim();

    if (!trimmedAlias) {
      return;
    }

    setColumnAliases(prev => {
      const tableAliases = prev[currentColumnTableKey] || {};
      const columnAliasesList = tableAliases[currentColumnName] || [];

      if (isColumnEditMode) {
        // Edit mode: replace the old alias with the new one
        const newAliases = columnAliasesList.map(alias =>
          alias === editingColumnAliasOriginal ? trimmedAlias : alias
        );
        return {
          ...prev,
          [currentColumnTableKey]: {
            ...tableAliases,
            [currentColumnName]: newAliases,
          },
        };
      } else {
        // Add mode: check if alias already exists
        if (columnAliasesList.includes(trimmedAlias)) {
          return prev;
        }

        return {
          ...prev,
          [currentColumnTableKey]: {
            ...tableAliases,
            [currentColumnName]: [...columnAliasesList, trimmedAlias],
          },
        };
      }
    });

    setNewColumnAliasInput('');
    handleCloseColumnDialog();
  };

  const handleDeleteColumnAlias = (tableKey, columnName, aliasToDelete) => {
    setColumnAliases(prev => {
      const tableAliases = prev[tableKey] || {};
      const columnAliasesList = tableAliases[columnName] || [];
      const newAliases = columnAliasesList.filter(alias => alias !== aliasToDelete);

      return {
        ...prev,
        [tableKey]: {
          ...tableAliases,
          [columnName]: newAliases,
        },
      };
    });
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: 300,
          gap: 2,
        }}
      >
        <CircularProgress size={48} sx={{ color: '#5B6FE5' }} />
        <Typography variant="body1" sx={{ color: '#6B7280' }}>
          Generating entity aliases, please wait...
        </Typography>
      </Box>
    );
  }

  if (selectedTables.length === 0) {
    return (
      <Alert severity="info" sx={{ mt: 2 }}>
        No entities selected. Please go back and select entities first.
      </Alert>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      {/* ERROR BANNER */}
      {error && (
        <Alert
          severity={error.type === 'network' ? 'warning' : 'error'}
          icon={error.type === 'network' ? <CloudOffIcon /> : undefined}
          sx={{
            mb: 2,
            borderRadius: 1.5,
            '& .MuiAlert-message': {
              width: '100%'
            }
          }}
          onClose={() => setError(null)}
        >
          <AlertTitle sx={{ fontWeight: 600, fontSize: '0.875rem' }}>
            {error.type === 'network' ? 'Backend Server Not Running' : 'Error'}
          </AlertTitle>
          <Typography sx={{ fontSize: '0.8125rem' }}>
            {error.message}
          </Typography>
        </Alert>
      )}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="h6" sx={{ color: '#1F2937', fontWeight: 600 }}>
            Entity Aliases & Column Selection
          </Typography>
          <Tooltip
            title={
              <Box>
                <Typography variant="body2" sx={{ fontSize: '0.8125rem' }}>
                  AI-generated aliases help make your entities more recognizable. You can edit them or add more aliases separated by commas.
                  Click on a row to select which columns to include.
                </Typography>
              </Box>
            }
            arrow
            placement="left"
          >
            <IconButton size="small" sx={{ color: '#6B7280', '&:hover': { color: '#5B6FE5' } }}>
              <InfoIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>

        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Tooltip title="Generate aliases for both entities and columns">
            <Button
              onClick={generateAllAliases}
              disabled={loading || error !== null}
              variant="contained"
              size="small"
              startIcon={<AutoAwesomeIcon />}
              sx={{
                bgcolor: '#10B981',
                color: '#FFFFFF',
                '&:hover': {
                  bgcolor: '#059669',
                },
              }}
            >
              Generate All Aliases
            </Button>
          </Tooltip>

          <Tooltip title="Regenerate entity aliases only">
            <IconButton onClick={generateAliases} size="small" sx={{ color: '#5B6FE5' }} disabled={loading || error !== null}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Confidence Score Legend */}
      <Box sx={{
        mt: 2,
        p: 1.5,
        bgcolor: '#F9FAFB',
        border: '1px solid #E5E7EB',
        borderRadius: 1,
        display: 'flex',
        alignItems: 'center',
        gap: 2
      }}>
        <Typography variant="body2" sx={{ fontSize: '0.75rem', fontWeight: 600, color: '#6B7280' }}>
          Confidence Indicators:
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#10B981' }} />
            <Typography variant="body2" sx={{ fontSize: '0.7rem', color: '#6B7280' }}>
              High (≥90%)
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#F59E0B' }} />
            <Typography variant="body2" sx={{ fontSize: '0.7rem', color: '#6B7280' }}>
              Medium (70-89%)
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#EF4444' }} />
            <Typography variant="body2" sx={{ fontSize: '0.7rem', color: '#6B7280' }}>
              Low (&lt;70%)
            </Typography>
          </Box>
        </Box>
        <Typography variant="body2" sx={{ fontSize: '0.7rem', color: '#9CA3AF', fontStyle: 'italic', ml: 'auto' }}>
          Only aliases with ≥70% confidence are shown
        </Typography>
      </Box>

      {/* Informational message about column selection requirement */}
      {!hasSelectedColumns() && !error && (
        <Alert
          severity="info"
          sx={{
            mb: 2,
            bgcolor: '#EEF2FF',
            color: '#3730A3',
            border: '1px solid #C7D2FE',
            '& .MuiAlert-icon': {
              color: '#5B6FE5',
            },
          }}
        >
          <Typography variant="body2" sx={{ fontSize: '0.875rem' }}>
            <strong>Required:</strong> Please expand at least one entity and select at least one column before proceeding to the next step.
          </Typography>
        </Alert>
      )}

      <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #E5E7EB' }}>
        <Table>
          <TableHead>
            <TableRow sx={{ bgcolor: '#F9FAFB' }}>
              <TableCell sx={{ width: 50, py: 0.75 }} />
              <TableCell sx={{ fontWeight: 600, color: '#1F2937', py: 0.75 }}>Schema</TableCell>
              <TableCell sx={{ fontWeight: 600, color: '#1F2937', py: 0.75 }}>Entity Name</TableCell>
              <TableCell sx={{ fontWeight: 600, color: '#1F2937', minWidth: 300, py: 0.75 }}>Aliases</TableCell>
              <TableCell sx={{ fontWeight: 600, color: '#1F2937', width: 120, py: 0.75 }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {aliasesData.map((row) => (
              <React.Fragment key={row.key}>
                <TableRow
                  hover
                  sx={{
                    '& > *': { borderBottom: expandedRows[row.key] ? 'none !important' : undefined },
                  }}
                >
                  <TableCell sx={{ py: 0.75 }}>
                    <IconButton
                      size="small"
                      onClick={() => handleRowExpand(row)}
                      sx={{ color: '#6B7280' }}
                    >
                      {expandedRows[row.key] ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                    </IconButton>
                  </TableCell>
                  <TableCell sx={{ py: 0.75 }}>
                    <Chip
                      label={row.databaseName}
                      size="small"
                      sx={{
                        height: 22,
                        fontSize: '0.75rem',
                        bgcolor: '#F3F4F6',
                        color: '#6B7280',
                      }}
                    />
                  </TableCell>
                  <TableCell sx={{ py: 0.75 }}>
                    <Typography variant="body2" sx={{ fontWeight: 500, color: '#1F2937' }}>
                      {row.tableName}
                    </Typography>
                  </TableCell>
                  <TableCell sx={{ py: 0.75 }}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      {/* Primary Alias Label */}
                      <Typography variant="caption" sx={{ color: '#6B7280', fontSize: '0.7rem', fontWeight: 500 }}>
                        Select Primary Alias:
                      </Typography>

                      {/* Aliases with Radio Buttons and Confidence Scores */}
                      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', alignItems: 'center' }}>
                        {row.aliases.map((alias, idx) => {
                          const isPrimary = primaryAliases[row.key] === alias;
                          // Get confidence score for this alias
                          const aliasWithConf = row.aliasesWithConfidence?.find(a => a.alias === alias);
                          const confidence = aliasWithConf?.confidence || 0.8;
                          const confidencePercent = Math.round(confidence * 100);

                          // Determine confidence color
                          let confidenceColor = '#10B981'; // Green for high confidence (>=90%)
                          if (confidence < 0.9 && confidence >= 0.7) {
                            confidenceColor = '#F59E0B'; // Amber for medium confidence (70-89%)
                          } else if (confidence < 0.7) {
                            confidenceColor = '#EF4444'; // Red for low confidence (<70%)
                          }

                          return (
                            <Box key={idx} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                              <Tooltip title="Select as primary alias" arrow placement="top">
                                <Radio
                                  checked={isPrimary}
                                  onChange={() => handlePrimaryAliasChange(row.key, alias)}
                                  size="small"
                                  sx={{
                                    padding: '2px',
                                    color: '#D1D5DB',
                                    '&.Mui-checked': { color: '#5B6FE5' },
                                  }}
                                />
                              </Tooltip>
                              <Tooltip
                                title={
                                  <Box>
                                    <div>Click to edit, or click X to delete</div>
                                    <div style={{ marginTop: '4px', fontSize: '0.75rem' }}>
                                      Confidence: {confidencePercent}%
                                    </div>
                                  </Box>
                                }
                                arrow
                                placement="top"
                              >
                                <Chip
                                  label={
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                      <span>{alias}</span>
                                      <Box
                                        sx={{
                                          width: 6,
                                          height: 6,
                                          borderRadius: '50%',
                                          bgcolor: confidenceColor,
                                          flexShrink: 0,
                                        }}
                                      />
                                    </Box>
                                  }
                                  size="small"
                                  onClick={() => handleEditAlias(row.key, alias)}
                                  onDelete={() => handleDeleteAlias(row.key, alias)}
                                  deleteIcon={
                                    <CloseIcon
                                      sx={{
                                        fontSize: '16px !important',
                                        '&:hover': { color: '#EF4444 !important' }
                                      }}
                                    />
                                  }
                                  sx={{
                                    bgcolor: isPrimary ? '#5B6FE5' : '#EEF2FF',
                                    color: isPrimary ? '#FFFFFF' : '#5B6FE5',
                                    border: isPrimary ? '1px solid #5B6FE5' : '1px solid #C7D2FE',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s ease',
                                    fontWeight: isPrimary ? 600 : 400,
                                    '&:hover': {
                                      bgcolor: isPrimary ? '#4C5FD5' : '#DDD6FE',
                                      borderColor: isPrimary ? '#4C5FD5' : '#A5B4FC',
                                      transform: 'translateY(-1px)',
                                      boxShadow: '0 2px 4px rgba(91, 111, 229, 0.2)',
                                    },
                                    '& .MuiChip-deleteIcon': {
                                      color: isPrimary ? '#FFFFFF' : '#5B6FE5',
                                      fontSize: '16px',
                                      '&:hover': {
                                        color: '#EF4444',
                                      },
                                    },
                                  }}
                                />
                              </Tooltip>
                            </Box>
                          );
                        })}
                        <Tooltip title="Add new alias" arrow>
                          <IconButton
                            size="small"
                            onClick={() => handleOpenDialog(row.key)}
                            sx={{
                              color: '#10B981',
                              bgcolor: '#F0FDF4',
                              border: '1px solid #BBF7D0',
                              width: 28,
                              height: 28,
                              '&:hover': {
                                bgcolor: '#DCFCE7',
                                borderColor: '#86EFAC',
                              },
                            }}
                          >
                            <AddIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell sx={{ py: 0.75 }}>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      <Tooltip title="Delete entity" arrow>
                        <IconButton
                          size="small"
                          onClick={() => handleDelete(row.key)}
                          sx={{ color: '#EF4444' }}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>

                {/* Expanded Row - Column Selection */}
                <TableRow>
                  <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={5}>
                    <Collapse in={expandedRows[row.key]} timeout="auto" unmountOnExit>
                      <Box sx={{ margin: 1, my: 1.5 }}>
                        <Box sx={{ mb: 1 }}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1F2937', fontSize: '0.8125rem' }}>
                            Select Columns ({getSelectedColumnCount(row.key)} / {columnsData[row.key]?.length || 0})
                          </Typography>
                        </Box>

                        <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #E5E7EB' }}>
                          <Table size="small">
                            <TableHead>
                              <TableRow sx={{ bgcolor: '#F9FAFB' }}>
                                <TableCell padding="checkbox" sx={{ py: 0.5 }}>
                                  <Checkbox
                                    size="small"
                                    checked={
                                      columnsData[row.key]?.length > 0 &&
                                      getSelectedColumnCount(row.key) === columnsData[row.key]?.length
                                    }
                                    indeterminate={
                                      getSelectedColumnCount(row.key) > 0 &&
                                      getSelectedColumnCount(row.key) < columnsData[row.key]?.length
                                    }
                                    onChange={(e) => handleSelectAllColumns(row.key, e.target.checked)}
                                    sx={{
                                      color: '#D1D5DB',
                                      '&.Mui-checked': { color: '#5B6FE5' },
                                      '&.MuiCheckbox-indeterminate': { color: '#5B6FE5' },
                                    }}
                                  />
                                </TableCell>
                                <TableCell sx={{ fontWeight: 600, fontSize: '0.75rem', py: 0.5 }}>Column Name</TableCell>
                                <TableCell sx={{ fontWeight: 600, fontSize: '0.75rem', py: 0.5, minWidth: 200 }}>Aliases</TableCell>
                                <TableCell sx={{ fontWeight: 600, fontSize: '0.75rem', py: 0.5 }}>Type</TableCell>
                                <TableCell sx={{ fontWeight: 600, fontSize: '0.75rem', py: 0.5 }}>Nullable</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {columnsData[row.key]?.map((column) => (
                                <TableRow
                                  key={column.name}
                                  hover
                                  sx={{ cursor: 'pointer' }}
                                >
                                  <TableCell
                                    padding="checkbox"
                                    sx={{ py: 0.5 }}
                                    onClick={() => handleColumnToggle(row.key, column.name)}
                                  >
                                    <Checkbox
                                      size="small"
                                      checked={selectedColumns[row.key]?.[column.name] || false}
                                      sx={{
                                        color: '#D1D5DB',
                                        '&.Mui-checked': { color: '#5B6FE5' },
                                      }}
                                    />
                                  </TableCell>
                                  <TableCell
                                    sx={{ fontSize: '0.75rem', py: 0.5 }}
                                    onClick={() => handleColumnToggle(row.key, column.name)}
                                  >
                                    {column.name}
                                  </TableCell>
                                  <TableCell sx={{ fontSize: '0.75rem', py: 0.5 }}>
                                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', alignItems: 'center' }}>
                                      {(columnAliases[row.key]?.[column.name] || []).map((alias, idx) => (
                                        <Tooltip key={idx} title="Click to edit, or click X to delete" arrow placement="top">
                                          <Chip
                                            label={alias}
                                            size="small"
                                            onClick={(e) => {
                                              e.stopPropagation();
                                              handleEditColumnAlias(row.key, column.name, alias);
                                            }}
                                            onDelete={(e) => {
                                              e.stopPropagation();
                                              handleDeleteColumnAlias(row.key, column.name, alias);
                                            }}
                                            deleteIcon={
                                              <CloseIcon
                                                sx={{
                                                  fontSize: '14px !important',
                                                  '&:hover': { color: '#EF4444 !important' }
                                                }}
                                              />
                                            }
                                            sx={{
                                              height: 20,
                                              fontSize: '0.65rem',
                                              bgcolor: '#EEF2FF',
                                              color: '#5B6FE5',
                                              border: '1px solid #C7D2FE',
                                              cursor: 'pointer',
                                              transition: 'all 0.2s ease',
                                              '&:hover': {
                                                bgcolor: '#DDD6FE',
                                                borderColor: '#A5B4FC',
                                                transform: 'translateY(-1px)',
                                                boxShadow: '0 2px 4px rgba(91, 111, 229, 0.2)',
                                              },
                                              '& .MuiChip-deleteIcon': {
                                                color: '#5B6FE5',
                                                fontSize: '14px',
                                                '&:hover': {
                                                  color: '#EF4444',
                                                },
                                              },
                                            }}
                                          />
                                        </Tooltip>
                                      ))}
                                      <Tooltip title="Add column alias" arrow>
                                        <IconButton
                                          size="small"
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            handleOpenColumnDialog(row.key, column.name);
                                          }}
                                          sx={{
                                            color: '#10B981',
                                            bgcolor: '#F0FDF4',
                                            border: '1px solid #BBF7D0',
                                            width: 22,
                                            height: 22,
                                            '&:hover': {
                                              bgcolor: '#DCFCE7',
                                              borderColor: '#86EFAC',
                                            },
                                          }}
                                        >
                                          <AddIcon sx={{ fontSize: '0.875rem' }} />
                                        </IconButton>
                                      </Tooltip>
                                    </Box>
                                  </TableCell>
                                  <TableCell
                                    sx={{ fontSize: '0.75rem', py: 0.5 }}
                                    onClick={() => handleColumnToggle(row.key, column.name)}
                                  >
                                    <Chip
                                      label={column.type}
                                      size="small"
                                      sx={{
                                        height: 18,
                                        fontSize: '0.65rem',
                                        bgcolor: '#F3F4F6',
                                        color: '#6B7280',
                                      }}
                                    />
                                  </TableCell>
                                  <TableCell
                                    sx={{ fontSize: '0.75rem', py: 0.5 }}
                                    onClick={() => handleColumnToggle(row.key, column.name)}
                                  >
                                    {column.nullable ? (
                                      <Chip
                                        label="Yes"
                                        size="small"
                                        sx={{
                                          height: 18,
                                          fontSize: '0.65rem',
                                          bgcolor: '#FEF3C7',
                                          color: '#92400E',
                                        }}
                                      />
                                    ) : (
                                      <Chip
                                        label="No"
                                        size="small"
                                        sx={{
                                          height: 18,
                                          fontSize: '0.65rem',
                                          bgcolor: '#DBEAFE',
                                          color: '#1E40AF',
                                        }}
                                      />
                                    )}
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </Box>
                    </Collapse>
                  </TableCell>
                </TableRow>
              </React.Fragment>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {aliasesData.length === 0 && (
        <Alert severity="warning" sx={{ mt: 2 }}>
          No aliases generated. Click the refresh button to try again.
        </Alert>
      )}

      {/* Add/Edit Alias Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 2,
          }
        }}
      >
        <DialogTitle sx={{
          bgcolor: '#F9FAFB',
          borderBottom: '1px solid #E5E7EB',
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}>
          {isEditMode ? (
            <EditIcon sx={{ color: '#5B6FE5' }} />
          ) : (
            <AddIcon sx={{ color: '#5B6FE5' }} />
          )}
          <Typography variant="h6" sx={{ fontWeight: 600, color: '#1F2937' }}>
            {isEditMode ? 'Edit Alias' : 'Add New Alias'}
          </Typography>
        </DialogTitle>

        <DialogContent sx={{ pt: 3, pb: 2 }}>
          <Alert severity="info" sx={{ mb: 2, fontSize: '0.875rem' }}>
            {isEditMode
              ? 'Update the alias name for this entity.'
              : 'Enter a new alias name for this entity. Aliases help make your entities more recognizable.'
            }
          </Alert>

          <TextField
            autoFocus
            fullWidth
            label="Alias Name"
            placeholder="Enter alias name"
            value={newAliasInput}
            onChange={(e) => setNewAliasInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && newAliasInput.trim()) {
                handleAddAlias();
              }
            }}
            helperText="Press Enter to save quickly"
          />
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 2, gap: 1 }}>
          <Button
            onClick={handleCloseDialog}
            variant="outlined"
            sx={{
              color: '#6B7280',
              borderColor: '#D1D5DB',
              '&:hover': {
                borderColor: '#9CA3AF',
                bgcolor: '#F9FAFB',
              },
            }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleAddAlias}
            variant="contained"
            disabled={!newAliasInput.trim()}
            sx={{
              bgcolor: '#5B6FE5',
              '&:hover': {
                bgcolor: '#4C5FD5',
              },
              '&:disabled': {
                bgcolor: '#D1D5DB',
                color: '#9CA3AF',
              },
            }}
          >
            {isEditMode ? 'Save Changes' : 'Add Alias'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add/Edit Column Alias Dialog */}
      <Dialog
        open={columnDialogOpen}
        onClose={handleCloseColumnDialog}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 2,
          }
        }}
      >
        <DialogTitle sx={{
          bgcolor: '#F9FAFB',
          borderBottom: '1px solid #E5E7EB',
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}>
          {isColumnEditMode ? (
            <EditIcon sx={{ color: '#5B6FE5' }} />
          ) : (
            <AddIcon sx={{ color: '#5B6FE5' }} />
          )}
          <Typography variant="h6" sx={{ fontWeight: 600, color: '#1F2937' }}>
            {isColumnEditMode ? 'Edit Column Alias' : 'Add Column Alias'}
          </Typography>
        </DialogTitle>

        <DialogContent sx={{ pt: 3, pb: 2 }}>
          <Alert severity="info" sx={{ mb: 2, fontSize: '0.875rem' }}>
            {isColumnEditMode
              ? `Update the alias name for column "${currentColumnName}".`
              : `Enter a new alias name for column "${currentColumnName}". Aliases help make your columns more recognizable.`
            }
          </Alert>

          <TextField
            autoFocus
            fullWidth
            label="Column Alias Name"
            placeholder="Enter column alias name"
            value={newColumnAliasInput}
            onChange={(e) => setNewColumnAliasInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && newColumnAliasInput.trim()) {
                handleAddColumnAlias();
              }
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                '&.Mui-focused fieldset': {
                  borderColor: '#5B6FE5',
                },
              },
              '& .MuiInputLabel-root.Mui-focused': {
                color: '#5B6FE5',
              },
            }}
            helperText="Press Enter to save quickly"
          />
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 2, gap: 1 }}>
          <Button
            onClick={handleCloseColumnDialog}
            variant="outlined"
            sx={{
              color: '#6B7280',
              borderColor: '#D1D5DB',
              '&:hover': {
                borderColor: '#9CA3AF',
                bgcolor: '#F9FAFB',
              },
            }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleAddColumnAlias}
            variant="contained"
            disabled={!newColumnAliasInput.trim()}
            sx={{
              bgcolor: '#5B6FE5',
              '&:hover': {
                bgcolor: '#4C5FD5',
              },
              '&:disabled': {
                bgcolor: '#D1D5DB',
                color: '#9CA3AF',
              },
            }}
          >
            {isColumnEditMode ? 'Save Changes' : 'Add Alias'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default AliasesStep;

