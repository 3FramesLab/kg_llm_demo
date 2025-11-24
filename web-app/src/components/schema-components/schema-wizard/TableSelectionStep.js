import { useState, useEffect, useMemo, useCallback, memo } from 'react';
import { List as FixedSizeList } from 'react-window';
import {
  Box,
  Checkbox,
  Chip,
  CircularProgress,
  TextField,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  InputAdornment,
  Tooltip,
  IconButton,
  Badge,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  Paper,
  Pagination,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Search as SearchIcon,
  CheckBox as CheckBoxIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  Clear as ClearIcon,
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
} from '@mui/icons-material';
import { listTablesFromDatabase } from '../../../services/api';

/**
 * Custom hook for debouncing values
 */
function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * Memoized Table Row Component for better performance
 */
const TableRowMemoized = memo(({
  table,
  connectionId,
  dbName,
  connData,
  isSelected,
  onToggle
}) => {
  return (
    <Tooltip
      title={`Click to ${isSelected ? 'deselect' : 'select'} ${table.name}`}
      arrow
      placement="left"
    >
      <TableRow
        hover
        onClick={() => onToggle(connectionId, dbName, table)}
        sx={{
          cursor: 'pointer',
          bgcolor: isSelected ? '#F5F7FF' : 'inherit',
          transition: 'all 0.15s',
          '&:hover': {
            bgcolor: isSelected ? '#EEF2FF' : '#F9FAFB',
          },
          '& td': {
            borderBottom: '1px solid #F3F4F6',
          },
        }}
      >
        <TableCell padding="checkbox">
          <Checkbox
            checked={isSelected}
            sx={{
              color: '#D1D5DB',
              '&.Mui-checked': {
                color: '#5B6FE5',
              },
            }}
          />
        </TableCell>
        <TableCell>
          <Typography
            variant="body2"
            sx={{
              fontWeight: isSelected ? 600 : 500,
              color: isSelected ? '#5B6FE5' : '#1F2937',
              fontSize: '0.875rem',
            }}
          >
            {table.name}
          </Typography>
        </TableCell>
        <TableCell>
          <Typography
            variant="body2"
            sx={{
              color: '#6B7280',
              fontSize: '0.875rem',
            }}
          >
            {table.row_count !== undefined
              ? table.row_count.toLocaleString()
              : '-'}
          </Typography>
        </TableCell>
        <TableCell>
          <Chip
            label={dbName}
            size="small"
            sx={{
              height: 22,
              fontSize: '0.75rem',
              fontWeight: 500,
              bgcolor: '#F3F4F6',
              color: '#6B7280',
            }}
          />
        </TableCell>
        <TableCell>
          <Chip
            label={connData.connectionName}
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
        </TableCell>
      </TableRow>
    </Tooltip>
  );
});

TableRowMemoized.displayName = 'TableRowMemoized';

/**
 * Virtualized Table Component for very large datasets
 * Uses react-window for efficient rendering
 */
const VirtualizedTableBody = memo(({
  tables,
  connectionId,
  dbName,
  connData,
  isTableSelected,
  handleTableToggle
}) => {
  const ROW_HEIGHT = 53; // Height of each table row in pixels
  const MAX_HEIGHT = 600; // Maximum height of the virtualized list

  const Row = useCallback(({ index, style }) => {
    const table = tables[index];
    const isSelected = isTableSelected(connectionId, dbName, table.name);

    return (
      <div style={style}>
        <TableRowMemoized
          table={table}
          connectionId={connectionId}
          dbName={dbName}
          connData={connData}
          isSelected={isSelected}
          onToggle={handleTableToggle}
        />
      </div>
    );
  }, [tables, connectionId, dbName, connData, isTableSelected, handleTableToggle]);

  Row.displayName = 'VirtualizedRow';

  const listHeight = Math.min(tables.length * ROW_HEIGHT, MAX_HEIGHT);

  return (
    <FixedSizeList
      height={listHeight}
      itemCount={tables.length}
      itemSize={ROW_HEIGHT}
      width="100%"
      overscanCount={5}
    >
      {Row}
    </FixedSizeList>
  );
});

VirtualizedTableBody.displayName = 'VirtualizedTableBody';

/**
 * TableSelectionStep Component
 * Step 2: Entities - Select tables from connected databases
 */
function TableSelectionStep({ connections, selectedTables, setSelectedTables, onDataChange }) {
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [tablesData, setTablesData] = useState({});
  const [expandedPanels, setExpandedPanels] = useState({});
  const [sortConfig, setSortConfig] = useState({ key: 'tableName', direction: 'asc' });
  const [currentPage, setCurrentPage] = useState(1);
  const [lazyLoadedConnections, setLazyLoadedConnections] = useState({});
  const [useVirtualization, setUseVirtualization] = useState(false);

  // Debounce search query to reduce filter operations
  const debouncedSearchQuery = useDebounce(searchQuery, 300);

  // Pagination settings
  const ITEMS_PER_PAGE = 100;
  const VIRTUALIZATION_THRESHOLD = 200; // Use virtualization for tables > 200 rows

  // Initialize connection metadata without loading tables (lazy loading)
  const initializeConnections = useCallback(() => {
    const allTablesData = {};

    for (const connection of connections) {
      if (connection.status === 'connected' && connection.database) {
        const dbName = connection.database;
        allTablesData[connection.id] = {
          connectionName: connection.name,
          connectionType: connection.type,
          databases: {
            [dbName]: [] // Empty initially, will be loaded on demand
          },
        };
      }
    }

    setTablesData(allTablesData);
  }, [connections]);

  useEffect(() => {
    // Initialize connection metadata without loading tables
    initializeConnections();
  }, [initializeConnections]);

  useEffect(() => {
    onDataChange(selectedTables);
  }, [selectedTables, onDataChange]);

  // Reset pagination when search or sort changes
  useEffect(() => {
    setCurrentPage(1);
  }, [debouncedSearchQuery, sortConfig]);

  // Load tables for a specific connection (lazy loading)
  const loadTablesForConnection = useCallback(async (connectionId) => {
    // Skip if already loaded
    if (lazyLoadedConnections[connectionId]) {
      return;
    }

    const connection = connections.find(c => c.id === connectionId);
    if (!connection || connection.status !== 'connected' || !connection.database) {
      return;
    }

    try {
      const dbName = connection.database;
      const tablesResponse = await listTablesFromDatabase(connectionId, dbName);
      const tables = tablesResponse.data.tables || [];

      // Normalize tables to objects with name property
      const normalizedTables = tables.map(table =>
        typeof table === 'string' ? { name: table } : table
      );

      setTablesData(prev => ({
        ...prev,
        [connectionId]: {
          ...prev[connectionId],
          databases: {
            ...prev[connectionId].databases,
            [dbName]: normalizedTables
          }
        }
      }));

      setLazyLoadedConnections(prev => ({
        ...prev,
        [connectionId]: true
      }));
    } catch (error) {
      console.error(`Error loading tables for connection ${connection.name}:`, error);
      // Set empty array on error
      setTablesData(prev => ({
        ...prev,
        [connectionId]: {
          ...prev[connectionId],
          databases: {
            ...prev[connectionId].databases,
            [connection.database]: []
          }
        }
      }));
    }
  }, [connections, lazyLoadedConnections]);

  // Refresh all tables (reload all connections)
  const handleRefresh = useCallback(() => {
    setLazyLoadedConnections({});
    initializeConnections();
    // Reload expanded connections
    Object.keys(expandedPanels).forEach(connectionId => {
      if (expandedPanels[connectionId]) {
        loadTablesForConnection(connectionId);
      }
    });
  }, [initializeConnections, expandedPanels, loadTablesForConnection]);

  const handleTableToggle = useCallback((connectionId, databaseName, table) => {
    const tableKey = `${connectionId}:${databaseName}:${table.name}`;
    const isSelected = selectedTables.some((t) => t.key === tableKey);

    if (isSelected) {
      setSelectedTables(selectedTables.filter((t) => t.key !== tableKey));
    } else {
      setSelectedTables([
        ...selectedTables,
        {
          key: tableKey,
          connectionId,
          databaseName,
          tableName: table.name,
          rowCount: table.row_count,
          connectionName: tablesData[connectionId]?.connectionName,
        },
      ]);
    }
  }, [selectedTables, setSelectedTables, tablesData]);

  const handleSort = useCallback((columnKey) => {
    let direction = 'asc';
    if (sortConfig.key === columnKey && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key: columnKey, direction });
  }, [sortConfig]);

  const sortTables = useCallback((tables, connectionId, databaseName, connectionName) => {
    const tableRows = tables.map((table) => ({
      ...table,
      connectionId,
      databaseName,
      connectionName,
    }));

    return tableRows.sort((a, b) => {
      let aValue, bValue;

      switch (sortConfig.key) {
        case 'tableName':
          aValue = a.name?.toLowerCase() || '';
          bValue = b.name?.toLowerCase() || '';
          break;
        case 'rowCount':
          aValue = a.row_count || 0;
          bValue = b.row_count || 0;
          break;
        case 'database':
          aValue = a.databaseName?.toLowerCase() || '';
          bValue = b.databaseName?.toLowerCase() || '';
          break;
        case 'connection':
          aValue = a.connectionName?.toLowerCase() || '';
          bValue = b.connectionName?.toLowerCase() || '';
          break;
        default:
          return 0;
      }

      if (aValue < bValue) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortConfig.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });
  }, [sortConfig]);

  const matchesSearch = useCallback((tableName) => {
    if (!tableName) return false;
    if (!debouncedSearchQuery) return true;
    return tableName.toLowerCase().includes(debouncedSearchQuery.toLowerCase());
  }, [debouncedSearchQuery]);

  const isTableSelected = useCallback((connectionId, databaseName, tableName) => {
    const tableKey = `${connectionId}:${databaseName}:${tableName}`;
    return selectedTables.some((t) => t.key === tableKey);
  }, [selectedTables]);

  const handlePanelChange = useCallback((panelId) => (_event, isExpanded) => {
    setExpandedPanels({
      ...expandedPanels,
      [panelId]: isExpanded,
    });

    // Lazy load tables when accordion is expanded
    if (isExpanded) {
      loadTablesForConnection(panelId);
    }
  }, [expandedPanels, loadTablesForConnection]);

  const totalTableCount = useMemo(() => {
    let count = 0;
    Object.values(tablesData).forEach((connData) => {
      Object.values(connData.databases).forEach((tables) => {
        count += tables.length;
      });
    });
    return count;
  }, [tablesData]);

  const filteredTableCount = useMemo(() => {
    if (!debouncedSearchQuery) return totalTableCount;
    let count = 0;
    Object.values(tablesData).forEach((connData) => {
      Object.values(connData.databases).forEach((tables) => {
        count += tables.filter((table) => matchesSearch(table.name)).length;
      });
    });
    return count;
  }, [tablesData, debouncedSearchQuery, totalTableCount, matchesSearch]);

  if (connections.length === 0) {
    return (
      <Alert severity="warning">
        No database connections available. Please add connections in the Sources step.
      </Alert>
    );
  }

  return (
    <Box sx={{ bgcolor: '#FFFFFF', p: 2, borderRadius: 1.5 }}>
      <Box sx={{ mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
          <Box>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 600,
                fontSize: '1.125rem',
                color: '#1F2937',
                mb: 0.5,
              }}
            >
              Entities
            </Typography>
            <Typography
              variant="body2"
              sx={{
                color: '#6B7280',
                fontSize: '0.875rem',
                lineHeight: 1.5,
              }}
            >
              Choose entities from your connected sources to include in your knowledge graph.
            </Typography>
          </Box>
          <Tooltip title="Refresh entity list" arrow>
            <IconButton
              size="small"
              onClick={handleRefresh}
              disabled={loading}
              sx={{
                color: '#6B7280',
                '&:hover': {
                  bgcolor: '#F3F4F6',
                  color: '#1F2937',
                },
              }}
            >
              <RefreshIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>

        {/* Selection Summary */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1.5,
            p: 1.5,
            bgcolor: selectedTables.length > 0 ? '#EEF2FF' : '#F9FAFB',
            borderRadius: 1,
            border: selectedTables.length > 0 ? '1px solid #C7D2FE' : '1px solid #E5E7EB',
            transition: 'all 0.2s',
          }}
        >
          <Badge
            badgeContent={selectedTables.length}
            color="primary"
            max={999}
            sx={{
              '& .MuiBadge-badge': {
                bgcolor: '#5B6FE5',
                color: '#FFFFFF',
                fontWeight: 600,
              },
            }}
          >
            <CheckBoxIcon sx={{ color: selectedTables.length > 0 ? '#5B6FE5' : '#9CA3AF' }} />
          </Badge>
          <Box sx={{ flex: 1 }}>
            <Typography
              variant="body2"
              sx={{
                fontWeight: 600,
                color: '#1F2937',
                fontSize: '0.875rem',
              }}
            >
              {selectedTables.length} {selectedTables.length === 1 ? 'entity' : 'entities'} selected
            </Typography>
            <Typography
              variant="caption"
              sx={{
                color: '#6B7280',
                fontSize: '0.75rem',
              }}
            >
              {searchQuery
                ? `${filteredTableCount} entities match your search`
                : `${totalTableCount} total entities available`}
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Search Bar */}
      <Box sx={{ mb: 2 }}>
        <TextField
          placeholder="Search entities by name..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          fullWidth
          size="small"
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: '#6B7280', fontSize: 16 }} />
              </InputAdornment>
            ),
            endAdornment: searchQuery && (
              <InputAdornment position="end">
                <Tooltip title="Clear search" arrow>
                  <IconButton
                    size="small"
                    onClick={() => setSearchQuery('')}
                    sx={{
                      padding: 0.25,
                      color: '#9CA3AF',
                      '&:hover': {
                        color: '#6B7280',
                      },
                    }}
                  >
                    <ClearIcon sx={{ fontSize: 14 }} />
                  </IconButton>
                </Tooltip>
              </InputAdornment>
            ),
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              bgcolor: '#FFFFFF',
              fontSize: '0.8125rem',
              '& fieldset': {
                borderColor: '#E5E7EB',
              },
              '&:hover fieldset': {
                borderColor: '#5B6FE5',
              },
              '&.Mui-focused fieldset': {
                borderColor: '#5B6FE5',
                borderWidth: '1px',
              },
              '& input': {
                py: 0.75
              }
            },
          }}
        />
        {searchQuery && (
          <Typography
            variant="caption"
            sx={{
              display: 'block',
              mt: 0.5,
              color: '#6B7280',
              fontSize: '0.75rem',
            }}
          >
            Showing {filteredTableCount} of {totalTableCount} entities
          </Typography>
        )}
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress size={32} sx={{ color: '#5B6FE5' }} />
        </Box>
      ) : Object.keys(tablesData).length === 0 ? (
        <Alert
          severity="info"
          sx={{
            py: 1.5,
            bgcolor: '#E8F4FD',
            color: '#1F2937',
            border: '1px solid #BFDBFE',
            '& .MuiAlert-icon': {
              color: '#3B82F6',
            },
          }}
        >
          No entities found. Make sure your source connections are active.
        </Alert>
      ) : (
        <Box>
          {Object.entries(tablesData).map(([connectionId, connData]) => {
            const totalTablesInConnection = Object.values(connData.databases).reduce(
              (sum, tables) => sum + tables.filter((t) => matchesSearch(t.name)).length,
              0
            );
            const selectedTablesInConnection = Object.entries(connData.databases).reduce(
              (sum, [dbName, tables]) =>
                sum + tables.filter((t) => matchesSearch(t.name) && isTableSelected(connectionId, dbName, t.name)).length,
              0
            );

            return (
              <Accordion
                key={connectionId}
                expanded={expandedPanels[connectionId] === true}
                onChange={handlePanelChange(connectionId)}
                sx={{
                  mb: 1.5,
                  '&:before': { display: 'none' },
                  border: selectedTablesInConnection > 0 ? '2px solid #C7D2FE' : '1px solid #E5E7EB',
                  borderRadius: '8px !important',
                  bgcolor: selectedTablesInConnection > 0 ? '#FAFBFF' : '#FFFFFF',
                  transition: 'all 0.2s',
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
                    bgcolor: selectedTablesInConnection > 0 ? '#F5F7FF' : '#F9FAFB',
                    borderRadius: '8px',
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, width: '100%' }}>
                    <Badge
                      badgeContent={selectedTablesInConnection}
                      color="primary"
                      max={999}
                      invisible={selectedTablesInConnection === 0}
                      sx={{
                        '& .MuiBadge-badge': {
                          bgcolor: '#5B6FE5',
                          color: '#FFFFFF',
                          fontWeight: 600,
                          fontSize: '0.7rem',
                        },
                      }}
                    >
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
                    </Badge>
                    <Chip
                      label={connData.connectionType.toUpperCase()}
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
                    <Chip
                      label={`${Object.keys(connData.databases).length} schema(s)`}
                      size="small"
                      sx={{
                        height: 22,
                        fontSize: '0.75rem',
                        fontWeight: 500,
                        bgcolor: '#F3F4F6',
                        color: '#6B7280',
                      }}
                    />
                    {selectedTablesInConnection > 0 && (
                      <Chip
                        label={`${selectedTablesInConnection}/${totalTablesInConnection} selected`}
                        size="small"
                        sx={{
                          height: 22,
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          bgcolor: '#5B6FE5',
                          color: '#FFFFFF',
                        }}
                      />
                    )}
                  </Box>
                </AccordionSummary>
                <AccordionDetails sx={{ p: 0, bgcolor: '#FFFFFF' }}>
                  {!lazyLoadedConnections[connectionId] ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 4 }}>
                      <CircularProgress size={32} sx={{ color: '#5B6FE5' }} />
                      <Typography variant="body2" sx={{ ml: 2, color: '#6B7280' }}>
                        Loading entities...
                      </Typography>
                    </Box>
                  ) : (
                    Object.entries(connData.databases).map(([dbName, tables]) => {
                      const filteredTables = tables.filter((table) => matchesSearch(table.name));
                      const sortedTables = sortTables(filteredTables, connectionId, dbName, connData.connectionName);

                      if (filteredTables.length === 0 && tables.length === 0) {
                        return (
                          <Box key={dbName} sx={{ p: 2 }}>
                            <Alert
                              severity="info"
                              icon={<InfoIcon />}
                              sx={{
                                py: 1,
                                bgcolor: '#F9FAFB',
                                color: '#6B7280',
                                border: '1px solid #E5E7EB',
                                '& .MuiAlert-icon': {
                                  color: '#9CA3AF',
                                },
                              }}
                            >
                              No entities found in schema: {dbName}
                            </Alert>
                          </Box>
                        );
                      }

                      if (filteredTables.length === 0) {
                        return (
                          <Box key={dbName} sx={{ p: 2 }}>
                            <Alert
                              severity="info"
                              icon={<InfoIcon />}
                              sx={{
                                py: 1,
                                bgcolor: '#F9FAFB',
                                color: '#6B7280',
                                border: '1px solid #E5E7EB',
                                '& .MuiAlert-icon': {
                                  color: '#9CA3AF',
                                },
                              }}
                            >
                              No entities match your search criteria in schema: {dbName}
                            </Alert>
                          </Box>
                        );
                      }

                    return (
                      <Box key={dbName} sx={{ mb: 0, '&:last-child': { mb: 0 } }}>
                        <TableContainer component={Paper} elevation={0} sx={{ border: 'none' }}>
                          <Table size="small" sx={{ minWidth: 650 }}>
                            <TableHead>
                              <TableRow sx={{ bgcolor: '#F9FAFB' }}>
                                <TableCell padding="checkbox" sx={{ width: 50, borderBottom: '2px solid #E5E7EB' }}>
                                  <Tooltip title="Select/Deselect entity" arrow>
                                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                      <CheckBoxIcon sx={{ fontSize: 18, color: '#9CA3AF' }} />
                                    </Box>
                                  </Tooltip>
                                </TableCell>
                                <TableCell sx={{ fontWeight: 600, color: '#1F2937', borderBottom: '2px solid #E5E7EB' }}>
                                  <TableSortLabel
                                    active={sortConfig.key === 'tableName'}
                                    direction={sortConfig.key === 'tableName' ? sortConfig.direction : 'asc'}
                                    onClick={() => handleSort('tableName')}
                                    sx={{
                                      '&.MuiTableSortLabel-root': {
                                        color: '#1F2937',
                                        fontWeight: 600,
                                      },
                                      '&.MuiTableSortLabel-root:hover': {
                                        color: '#5B6FE5',
                                      },
                                      '&.Mui-active': {
                                        color: '#5B6FE5',
                                      },
                                      '& .MuiTableSortLabel-icon': {
                                        color: '#5B6FE5 !important',
                                      },
                                    }}
                                  >
                                    Entity Name
                                  </TableSortLabel>
                                </TableCell>
                                <TableCell sx={{ fontWeight: 600, color: '#1F2937', borderBottom: '2px solid #E5E7EB' }}>
                                  <TableSortLabel
                                    active={sortConfig.key === 'rowCount'}
                                    direction={sortConfig.key === 'rowCount' ? sortConfig.direction : 'asc'}
                                    onClick={() => handleSort('rowCount')}
                                    sx={{
                                      '&.MuiTableSortLabel-root': {
                                        color: '#1F2937',
                                        fontWeight: 600,
                                      },
                                      '&.MuiTableSortLabel-root:hover': {
                                        color: '#5B6FE5',
                                      },
                                      '&.Mui-active': {
                                        color: '#5B6FE5',
                                      },
                                      '& .MuiTableSortLabel-icon': {
                                        color: '#5B6FE5 !important',
                                      },
                                    }}
                                  >
                                    Row Count
                                  </TableSortLabel>
                                </TableCell>
                                <TableCell sx={{ fontWeight: 600, color: '#1F2937', borderBottom: '2px solid #E5E7EB' }}>
                                  <TableSortLabel
                                    active={sortConfig.key === 'database'}
                                    direction={sortConfig.key === 'database' ? sortConfig.direction : 'asc'}
                                    onClick={() => handleSort('database')}
                                    sx={{
                                      '&.MuiTableSortLabel-root': {
                                        color: '#1F2937',
                                        fontWeight: 600,
                                      },
                                      '&.MuiTableSortLabel-root:hover': {
                                        color: '#5B6FE5',
                                      },
                                      '&.Mui-active': {
                                        color: '#5B6FE5',
                                      },
                                      '& .MuiTableSortLabel-icon': {
                                        color: '#5B6FE5 !important',
                                      },
                                    }}
                                  >
                                    Schema
                                  </TableSortLabel>
                                </TableCell>
                                <TableCell sx={{ fontWeight: 600, color: '#1F2937', borderBottom: '2px solid #E5E7EB' }}>
                                  <TableSortLabel
                                    active={sortConfig.key === 'connection'}
                                    direction={sortConfig.key === 'connection' ? sortConfig.direction : 'asc'}
                                    onClick={() => handleSort('connection')}
                                    sx={{
                                      '&.MuiTableSortLabel-root': {
                                        color: '#1F2937',
                                        fontWeight: 600,
                                      },
                                      '&.MuiTableSortLabel-root:hover': {
                                        color: '#5B6FE5',
                                      },
                                      '&.Mui-active': {
                                        color: '#5B6FE5',
                                      },
                                      '& .MuiTableSortLabel-icon': {
                                        color: '#5B6FE5 !important',
                                      },
                                    }}
                                  >
                                    Connection
                                  </TableSortLabel>
                                </TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {(() => {
                                // Calculate pagination
                                const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
                                const endIndex = startIndex + ITEMS_PER_PAGE;
                                const paginatedTables = sortedTables.slice(startIndex, endIndex);
                                const totalPages = Math.ceil(sortedTables.length / ITEMS_PER_PAGE);

                                return (
                                  <>
                                    {paginatedTables.map((table) => {
                                      const isSelected = isTableSelected(connectionId, dbName, table.name);
                                      return (
                                        <TableRowMemoized
                                          key={table.name}
                                          table={table}
                                          connectionId={connectionId}
                                          dbName={dbName}
                                          connData={connData}
                                          isSelected={isSelected}
                                          onToggle={handleTableToggle}
                                        />
                                      );
                                    })}
                                    {totalPages > 1 && (
                                      <TableRow>
                                        <TableCell colSpan={5} sx={{ borderBottom: 'none', pt: 2, pb: 2 }}>
                                          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 2 }}>
                                            <Typography variant="caption" sx={{ color: '#6B7280' }}>
                                              Showing {startIndex + 1}-{Math.min(endIndex, sortedTables.length)} of {sortedTables.length} entities
                                            </Typography>
                                            <Pagination
                                              count={totalPages}
                                              page={currentPage}
                                              onChange={(_e, page) => setCurrentPage(page)}
                                              size="small"
                                              sx={{
                                                '& .MuiPaginationItem-root': {
                                                  color: '#6B7280',
                                                },
                                                '& .Mui-selected': {
                                                  bgcolor: '#5B6FE5 !important',
                                                  color: '#FFFFFF',
                                                },
                                              }}
                                            />
                                          </Box>
                                        </TableCell>
                                      </TableRow>
                                    )}
                                  </>
                                );
                              })()}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </Box>
                    );
                  })
                  )}
                </AccordionDetails>
              </Accordion>
            );
          })}
        </Box>
      )}
    </Box>
  );
}

export default TableSelectionStep;

