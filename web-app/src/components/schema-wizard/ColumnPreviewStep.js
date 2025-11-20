import { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  TextField,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  InputAdornment,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Search as SearchIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { getTableColumns } from '../../services/api';

/**
 * ColumnPreviewStep Component
 * Step 4: Preview - Preview selected columns from tables
 */
function ColumnPreviewStep({ selectedTables, selectedColumns = {}, tableAliases = [], columnAliases = {}, onDataChange }) {
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [columnsData, setColumnsData] = useState({});
  const [expandedPanels, setExpandedPanels] = useState({});
  const [schemaName, setSchemaName] = useState('');

  // Track loaded tables to prevent duplicate API calls
  const loadedTablesRef = useRef('');
  const isInitialMount = useRef(true);

  // Create stable key from selectedTables to detect actual changes
  const selectedTablesKey = selectedTables.map(t => t.key).sort().join('|');

  useEffect(() => {
    // Only load columns if tables actually changed (not just reference change)
    if (selectedTables.length > 0 && selectedTablesKey !== loadedTablesRef.current) {
      loadedTablesRef.current = selectedTablesKey;
      loadAllColumns();
    } else if (selectedTables.length === 0) {
      // Clear columns if no tables selected
      setColumnsData({});
      loadedTablesRef.current = '';
    }
  }, [selectedTablesKey]);

  useEffect(() => {
    // Skip initial mount to prevent calling onDataChange before data is ready
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }

    onDataChange({
      columnsData,
      schemaName,
    });
  }, [columnsData, schemaName, onDataChange]);

  const loadAllColumns = async () => {
    if (selectedTables.length === 0) return;

    setLoading(true);
    const allColumnsData = {};

    try {
      for (const table of selectedTables) {
        try {
          const response = await getTableColumns(
            table.connectionId,
            table.databaseName,
            table.tableName
          );
          
          const key = `${table.connectionId}:${table.databaseName}:${table.tableName}`;
          allColumnsData[key] = {
            ...table,
            columns: response.data.columns || [],
          };
        } catch (error) {
          console.error(`Error loading columns for ${table.tableName}:`, error);
          const key = `${table.connectionId}:${table.databaseName}:${table.tableName}`;
          allColumnsData[key] = {
            ...table,
            columns: [],
            error: error.response?.data?.detail || error.message,
          };
        }
      }

      setColumnsData(allColumnsData);
    } catch (error) {
      console.error('Error loading columns:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePanelChange = (panelId) => (_event, isExpanded) => {
    setExpandedPanels({
      ...expandedPanels,
      [panelId]: isExpanded,
    });
  };

  const matchesSearch = (columnName) => {
    return columnName.toLowerCase().includes(searchQuery.toLowerCase());
  };

  // Filter columns based on selection from AliasesStep
  const getSelectedColumnsForTable = (tableKey, allColumns) => {
    const tableSelections = selectedColumns[tableKey];

    // If no selections exist for this table, return empty array
    if (!tableSelections) {
      return [];
    }

    // Filter columns where selection is true
    return allColumns.filter(column => tableSelections[column.name] === true);
  };

  const getTotalColumnCount = () => {
    let count = 0;
    Object.entries(columnsData).forEach(([tableKey, tableData]) => {
      const selectedCols = getSelectedColumnsForTable(tableKey, tableData.columns);
      count += selectedCols.length;
    });
    return count;
  };

  const groupByConnection = () => {
    const grouped = {};
    Object.entries(columnsData).forEach(([_key, tableData]) => {
      const connKey = `${tableData.connectionId}:${tableData.connectionName}`;
      if (!grouped[connKey]) {
        grouped[connKey] = {
          connectionId: tableData.connectionId,
          connectionName: tableData.connectionName,
          databases: {},
        };
      }

      if (!grouped[connKey].databases[tableData.databaseName]) {
        grouped[connKey].databases[tableData.databaseName] = [];
      }

      grouped[connKey].databases[tableData.databaseName].push(tableData);
    });
    return grouped;
  };

  // Get aliases for a specific table
  const getTableAliasesForKey = (tableKey) => {
    const aliasData = tableAliases.find(a => a.key === tableKey);
    return aliasData?.aliases || [];
  };

  // Get aliases for a specific column
  const getColumnAliasesForKey = (tableKey, columnName) => {
    return columnAliases?.[tableKey]?.[columnName] || [];
  };

  if (selectedTables.length === 0) {
    return (
      <Alert severity="warning">
        No entities selected. Please select entities in the Entities step.
      </Alert>
    );
  }

  const groupedData = groupByConnection();

  return (
    <Box sx={{ bgcolor: '#FFFFFF', p: 2, borderRadius: 1.5 }}>
      <Box sx={{ mb: 2 }}>
        <Typography
          variant="h6"
          sx={{
            fontWeight: 600,
            fontSize: '1.125rem',
            color: '#1F2937',
            mb: 0.5,
          }}
        >
          Column Preview
        </Typography>
        <Typography
          variant="body2"
          sx={{
            color: '#6B7280',
            fontSize: '0.875rem',
            lineHeight: 1.5,
          }}
        >
          Review selected columns from <strong>{selectedTables.length}</strong> entit{selectedTables.length !== 1 ? 'ies' : 'y'}. Total selected columns: <strong>{getTotalColumnCount()}</strong>
        </Typography>
      </Box>

      <Box sx={{ mb: 2, display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 2 }}>
        <Box>
          <TextField
            placeholder="Search entities by name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            fullWidth
            size="small"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" sx={{ color: '#9CA3AF' }} />
                </InputAdornment>
              ),
              endAdornment: searchQuery && (
                <InputAdornment position="end">
                  <Tooltip title="Clear search" arrow>
                    <IconButton
                      size="small"
                      onClick={() => setSearchQuery('')}
                      sx={{
                        p: 0.5,
                        color: '#9CA3AF',
                        '&:hover': {
                          color: '#6B7280',
                        },
                      }}
                    >
                      <ClearIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </InputAdornment>
              ),
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: '#F9FAFB',
                color: '#1F2937',
                '& fieldset': {
                  borderColor: '#E5E7EB',
                },
                '&:hover fieldset': {
                  borderColor: '#D1D5DB',
                },
                '&.Mui-focused': {
                  bgcolor: '#FFFFFF',
                  '& fieldset': {
                    borderColor: '#5B6FE5',
                  },
                },
              },
              '& .MuiOutlinedInput-input': {
                color: '#1F2937',
                '&::placeholder': {
                  color: '#9CA3AF',
                  opacity: 1,
                },
              },
            }}
          />
        </Box>
        <Box>
          <TextField
            label="Schema Name"
            placeholder="Enter schema name..."
            value={schemaName}
            onChange={(e) => setSchemaName(e.target.value)}
            fullWidth
            size="small"
            required
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: '#F9FAFB',
                color: '#1F2937',
                '& fieldset': {
                  borderColor: '#E5E7EB',
                },
                '&:hover fieldset': {
                  borderColor: '#D1D5DB',
                },
                '&.Mui-focused': {
                  bgcolor: '#FFFFFF',
                  '& fieldset': {
                    borderColor: '#5B6FE5',
                  },
                },
              },
              '& .MuiOutlinedInput-input': {
                color: '#1F2937',
                '&::placeholder': {
                  color: '#9CA3AF',
                  opacity: 1,
                },
              },
              '& .MuiInputBase-input:required:invalid + fieldset': {
                borderColor: '#EF4444',
              },
              '& .MuiFormLabel-root': {
                color: '#6B7280',
                fontSize: '0.875rem',
                '&.Mui-focused': {
                  color: '#5B6FE5',
                },
              },
            }}
          />
        </Box>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress size={32} sx={{ color: '#5B6FE5' }} />
        </Box>
      ) : (
        <Box>
          {Object.entries(groupedData).map(([connKey, connData]) => (
            <Accordion
              key={connKey}
              expanded={expandedPanels[connKey] === true}
              onChange={handlePanelChange(connKey)}
              sx={{
                mb: 1.5,
                '&:before': { display: 'none' },
                border: '1px solid #E5E7EB',
                borderRadius: '8px !important',
                '&:first-of-type': {
                  borderRadius: '8px !important',
                },
                '&:last-of-type': {
                  borderRadius: '8px !important',
                },
              }}
            >
              <AccordionSummary
                expandIcon={<ExpandMoreIcon sx={{ color: '#6B7280' }} />}
                sx={{
                  minHeight: 48,
                  '&.Mui-expanded': { minHeight: 48 },
                  bgcolor: '#F9FAFB',
                  borderRadius: '8px',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, width: '100%' }}>
                  <Typography
                    variant="body2"
                    sx={{
                      fontWeight: 600,
                      color: '#1F2937',
                      fontSize: '0.9375rem',
                    }}
                  >
                    {connData.connectionName}
                  </Typography>
                  <Chip
                    label={`${Object.keys(connData.databases).length} database(s)`}
                    size="small"
                    sx={{
                      height: 22,
                      fontSize: '0.75rem',
                      fontWeight: 500,
                      bgcolor: '#F3F4F6',
                      color: '#6B7280',
                    }}
                  />
                </Box>
              </AccordionSummary>
              <AccordionDetails sx={{ p: 2, bgcolor: '#FFFFFF' }}>
                {Object.entries(connData.databases).map(([dbName, tables]) => (
                  <Box key={dbName} sx={{ mb: 2, '&:last-child': { mb: 0 } }}>
                    <Typography
                      variant="caption"
                      sx={{
                        color: '#5B6FE5',
                        fontWeight: 600,
                        fontSize: '0.8125rem',
                        mb: 1.5,
                        display: 'block',
                      }}
                    >
                      Schema: {dbName}
                    </Typography>
                    {tables.map((tableData) => {
                      const selectedColumnsForTable = getSelectedColumnsForTable(tableData.key, tableData.columns);

                      // Skip tables with no selected columns
                      if (selectedColumnsForTable.length === 0) {
                        return null;
                      }

                      return (
                        <Card
                          key={tableData.key}
                          variant="outlined"
                          sx={{
                            mb: 2,
                            '&:last-child': { mb: 0 },
                            border: '1px solid #E5E7EB',
                            borderRadius: 1.5,
                          }}
                        >
                          <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5, flexWrap: 'wrap' }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Typography
                                  variant="body2"
                                  sx={{
                                    fontWeight: 600,
                                    color: '#1F2937',
                                    fontSize: '0.9375rem',
                                  }}
                                >
                                  {tableData.tableName}
                                </Typography>
                                {getTableAliasesForKey(tableData.key).length > 0 && (
                                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                    {getTableAliasesForKey(tableData.key).map((alias, idx) => (
                                      <Chip
                                        key={idx}
                                        label={alias}
                                        size="small"
                                        sx={{
                                          height: 20,
                                          fontSize: '0.7rem',
                                          fontWeight: 500,
                                          bgcolor: '#FEF3C7',
                                          color: '#92400E',
                                          border: '1px solid #FCD34D',
                                        }}
                                      />
                                    ))}
                                  </Box>
                                )}
                              </Box>
                              <Chip
                                label={`${selectedColumnsForTable.length} selected column${selectedColumnsForTable.length !== 1 ? 's' : ''}`}
                                size="small"
                                sx={{
                                  height: 22,
                                  fontSize: '0.75rem',
                                  fontWeight: 500,
                                  bgcolor: '#EEF2FF',
                                  color: '#5B6FE5',
                                  border: '1px solid #C7D2FE',
                                }}
                              />
                              {tableData.rowCount !== undefined && (
                                <Chip
                                  label={`${tableData.rowCount.toLocaleString()} rows`}
                                  size="small"
                                  sx={{
                                    height: 22,
                                    fontSize: '0.75rem',
                                    fontWeight: 500,
                                    bgcolor: '#F3F4F6',
                                    color: '#6B7280',
                                    border: '1px solid #E5E7EB',
                                  }}
                                />
                              )}
                            </Box>

                            {tableData.error ? (
                              <Alert
                                severity="error"
                                sx={{
                                  py: 1,
                                  fontSize: '0.8125rem',
                                }}
                              >
                                Error loading columns: {tableData.error}
                              </Alert>
                            ) : selectedColumnsForTable.length === 0 ? (
                              <Alert
                                severity="info"
                                sx={{
                                  py: 1,
                                  fontSize: '0.8125rem',
                                  bgcolor: '#E8F4FD',
                                  color: '#1F2937',
                                  border: '1px solid #BFDBFE',
                                  '& .MuiAlert-icon': {
                                    color: '#3B82F6',
                                  },
                                }}
                              >
                                No columns selected for this entity.
                              </Alert>
                            ) : (
                              <TableContainer
                                component={Paper}
                                variant="outlined"
                                sx={{
                                  border: '1px solid #E5E7EB',
                                  borderRadius: 1,
                                }}
                              >
                              <Table size="small">
                                <TableHead>
                                  <TableRow sx={{ bgcolor: '#F9FAFB' }}>
                                    <TableCell
                                      sx={{
                                        py: 1,
                                        fontSize: '0.8125rem',
                                        fontWeight: 600,
                                        color: '#1F2937',
                                        borderBottom: '1px solid #E5E7EB',
                                      }}
                                    >
                                      Column Name
                                    </TableCell>
                                    <TableCell
                                      sx={{
                                        py: 1,
                                        fontSize: '0.8125rem',
                                        fontWeight: 600,
                                        color: '#1F2937',
                                        borderBottom: '1px solid #E5E7EB',
                                      }}
                                    >
                                      Data Type
                                    </TableCell>
                                    <TableCell
                                      align="center"
                                      sx={{
                                        py: 1,
                                        fontSize: '0.8125rem',
                                        fontWeight: 600,
                                        color: '#1F2937',
                                        borderBottom: '1px solid #E5E7EB',
                                      }}
                                    >
                                      Nullable
                                    </TableCell>
                                    <TableCell
                                      sx={{
                                        py: 1,
                                        fontSize: '0.8125rem',
                                        fontWeight: 600,
                                        color: '#1F2937',
                                        borderBottom: '1px solid #E5E7EB',
                                      }}
                                    >
                                      Key
                                    </TableCell>
                                  </TableRow>
                                </TableHead>
                                <TableBody>
                                  {selectedColumnsForTable
                                    .filter((col) => matchesSearch(col.name))
                                    .map((column, index) => (
                                      <TableRow
                                        key={index}
                                        sx={{
                                          '&:nth-of-type(odd)': {
                                            bgcolor: '#F9FAFB',
                                          },
                                          '&:hover': {
                                            bgcolor: '#F3F4F6',
                                          },
                                        }}
                                      >
                                        <TableCell
                                          sx={{
                                            py: 1,
                                            borderBottom: '1px solid #F3F4F6',
                                          }}
                                        >
                                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75, flexWrap: 'wrap' }}>
                                            <Typography
                                              variant="caption"
                                              sx={{
                                                fontWeight: 500,
                                                color: '#1F2937',
                                                fontSize: '0.8125rem',
                                              }}
                                            >
                                              {column.name}
                                            </Typography>
                                            {getColumnAliasesForKey(tableData.key, column.name).length > 0 && (
                                              <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                                {getColumnAliasesForKey(tableData.key, column.name).map((alias, idx) => (
                                                  <Chip
                                                    key={idx}
                                                    label={alias}
                                                    size="small"
                                                    sx={{
                                                      height: 18,
                                                      fontSize: '0.65rem',
                                                      fontWeight: 500,
                                                      bgcolor: '#DBEAFE',
                                                      color: '#0C4A6E',
                                                      border: '1px solid #7DD3FC',
                                                    }}
                                                  />
                                                ))}
                                              </Box>
                                            )}
                                          </Box>
                                        </TableCell>
                                        <TableCell
                                          sx={{
                                            py: 1,
                                            borderBottom: '1px solid #F3F4F6',
                                          }}
                                        >
                                          <Chip
                                            label={column.data_type || column.type}
                                            size="small"
                                            sx={{
                                              height: 20,
                                              fontSize: '0.75rem',
                                              fontWeight: 500,
                                              bgcolor: '#F3F4F6',
                                              color: '#6B7280',
                                              border: '1px solid #E5E7EB',
                                            }}
                                          />
                                        </TableCell>
                                        <TableCell
                                          align="center"
                                          sx={{
                                            py: 1,
                                            borderBottom: '1px solid #F3F4F6',
                                          }}
                                        >
                                          {column.nullable || column.is_nullable ? (
                                            <CheckCircleIcon sx={{ fontSize: 18, color: '#10B981' }} />
                                          ) : (
                                            <CancelIcon sx={{ fontSize: 18, color: '#EF4444' }} />
                                          )}
                                        </TableCell>
                                        <TableCell
                                          sx={{
                                            py: 1,
                                            borderBottom: '1px solid #F3F4F6',
                                          }}
                                        >
                                          {column.is_primary_key && (
                                            <Chip
                                              label="PK"
                                              size="small"
                                              sx={{
                                                height: 20,
                                                fontSize: '0.7rem',
                                                fontWeight: 600,
                                                bgcolor: '#EEF2FF',
                                                color: '#5B6FE5',
                                                border: '1px solid #C7D2FE',
                                              }}
                                            />
                                          )}
                                          {column.is_foreign_key && (
                                            <Chip
                                              label="FK"
                                              size="small"
                                              sx={{
                                                ml: 0.5,
                                                height: 20,
                                                fontSize: '0.7rem',
                                                fontWeight: 600,
                                                bgcolor: '#FEF3C7',
                                                color: '#D97706',
                                                border: '1px solid #FDE68A',
                                              }}
                                            />
                                          )}
                                        </TableCell>
                                      </TableRow>
                                    ))}
                                </TableBody>
                              </Table>
                            </TableContainer>
                            )}
                          </CardContent>
                        </Card>
                      );
                    })}
                  </Box>
                ))}
              </AccordionDetails>
            </Accordion>
          ))}
        </Box>
      )}
    </Box>
  );
}

export default ColumnPreviewStep;
