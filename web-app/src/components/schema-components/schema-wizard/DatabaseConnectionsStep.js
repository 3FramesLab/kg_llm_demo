import { useState, useEffect, useMemo } from "react";
import {
  Box,
  Typography,
  Alert,
  Checkbox,
  TextField,
  Card,
  Chip,
  CircularProgress,
  InputAdornment,
  IconButton,
  AlertTitle
} from "@mui/material";
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  CheckCircle as CheckCircleIcon,
  Storage as StorageIcon,
  TableChart as TableChartIcon,
  CloudOff as CloudOffIcon
} from "@mui/icons-material";
import {
  listDatabaseConnections,
  listDatabasesFromConnection,
  listTablesFromDatabase
} from "../../../services/api";

function DatabaseConnectionsStep({
  connections,
  setConnections,
  onDataChange,
  selectedSchemaTables,
  setSelectedSchemaTables,
  onTableDataChange
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [schemasByConn, setSchemasByConn] = useState({});
  const [tablesData, setTablesData] = useState({});
  const [loadedSchemas, setLoadedSchemas] = useState({});

  const [selectedSource, setSelectedSource] = useState(null);
  const [selectedSchema, setSelectedSchema] = useState(null);

  const [searchSchema, setSearchSchema] = useState("");
  const [searchTables, setSearchTables] = useState("");
  const [searchSelected, setSearchSelected] = useState("");

  /* ============================
    LOAD CONNECTIONS
  ============================ */
  useEffect(() => {
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await listDatabaseConnections();
        const list = res.data.connections || [];

        setConnections(list);
        onDataChange({ connections: list });

        list
          .filter((c) => c.status === "connected")
          .forEach((c) => loadSchemas(c.id));
      } catch (err) {
        console.error('Error loading connections:', err);
        const isNetworkError = err.code === 'ERR_NETWORK' || err.message === 'Network Error' || !err.response;
        setError({
          type: isNetworkError ? 'network' : 'server',
          message: isNetworkError
            ? 'Unable to connect to the backend server. Please ensure the backend is running on http://localhost:8000'
            : err.response?.data?.detail || 'Failed to load database connections'
        });
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  /* ============================
    LOAD SCHEMAS
  ============================ */
  const loadSchemas = async (connectionId) => {
    const res = await listDatabasesFromConnection(connectionId);
    const databases = res.data.databases || [];

    // For Excel connections with no databases, use connection name as temporary database
    if (databases.length === 0 && res.data.message === "Excel files do not have databases") {
      const connection = connections.find(c => c.id === connectionId);
      if (connection) {
        // Use connection name as the temporary database name
        const tempDatabaseName = connection.name;
        setSchemasByConn((prev) => ({
          ...prev,
          [connectionId]: [tempDatabaseName]
        }));
        return;
      }
    }

    setSchemasByConn((prev) => ({
      ...prev,
      [connectionId]: databases
    }));
  };

  /* ============================
    LOAD TABLES (Lazy)
  ============================ */
  const loadTablesForSchema = async (connectionId, schema) => {
    const key = `${connectionId}:${schema}`;

    if (loadedSchemas[key]) return;

    const res = await listTablesFromDatabase(connectionId, schema);
    const tables = (res.data.tables || []).map((t) => ({
      key: `${connectionId}:${schema}:${typeof t === "string" ? t : t.name}`,
      name: typeof t === "string" ? t : t.name,
      row_count: t.row_count
    }));

    setTablesData((p) => ({ ...p, [key]: tables }));
    setLoadedSchemas((p) => ({ ...p, [key]: true }));
  };

  /* ============================
    TOGGLE TABLE (FULL FIX)
  ============================ */
  const toggleTable = (connectionId, connectionName, schema, table) => {
    const exists = selectedSchemaTables.some((t) => t.key === table.key);

    const updated = exists
      ? selectedSchemaTables.filter((t) => t.key !== table.key)
      : [
        ...selectedSchemaTables,
        {
          key: table.key,
          connectionId,
          connectionName,
          databaseName: schema,
          tableName: table.name,
          rowCount: table.row_count
        }
      ];
    console.log("updated:", updated)
    setSelectedSchemaTables(updated)
    onTableDataChange({ selectedTables: updated });

  };

  /* ============================
    FILTERS
  ============================ */
  const schemaList = useMemo(() => {
    if (!selectedSource) return [];
    return (schemasByConn[selectedSource] || []).filter((s) =>
      s.toLowerCase().includes(searchSchema.toLowerCase())
    );
  }, [schemasByConn, selectedSource, searchSchema]);

  const tablesForSchema = useMemo(() => {
    if (!selectedSource || !selectedSchema) return [];
    const key = `${selectedSource}:${selectedSchema}`;
    return (tablesData[key] || []).filter((t) =>
      t.name.toLowerCase().includes(searchTables.toLowerCase())
    );
  }, [tablesData, selectedSource, selectedSchema, searchTables]);

  const selectedTableList = useMemo(
    () =>
      selectedSchemaTables.filter((t) =>
        t.tableName.toLowerCase().includes(searchSelected.toLowerCase())
      ),
    [selectedSchemaTables, searchSelected]
  );

  /* ============================
      UI SECTION
  ============================ */
  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* ERROR BANNER */}
      {error && (
        <Alert
          severity={error.type === 'network' ? 'warning' : 'error'}
          icon={error.type === 'network' ? <CloudOffIcon /> : undefined}
          sx={{
            mb: 1.5,
            borderRadius: 1.5,
            '& .MuiAlert-message': {
              width: '100%'
            }
          }}
          onClose={() => setError(null)}
        >
          <AlertTitle sx={{ fontWeight: 600, fontSize: '0.875rem' }}>
            {error.type === 'network' ? 'Backend Server Not Running' : 'Error Loading Data'}
          </AlertTitle>
          <Typography sx={{ fontSize: '0.8125rem', mb: 1 }}>
            {error.message}
          </Typography>
          {error.type === 'network' && (
            <Typography sx={{ fontSize: '0.75rem', color: '#6B7280', fontStyle: 'italic' }}>
              💡 Tip: Start the backend server with: <code style={{
                backgroundColor: '#F3F4F6',
                padding: '2px 6px',
                borderRadius: '4px',
                fontFamily: 'monospace'
              }}>python -m kg_builder.main</code>
            </Typography>
          )}
        </Alert>
      )}

      {/* SOURCE SELECT */}
      <Box
        sx={{
          mb: 1.5,
          display: "flex",
          alignItems: "center",
          gap: 1.5,
          p: 1.5,
          bgcolor: '#FFFFFF',
          borderRadius: 1.5,
          border: '1px solid #E5E7EB',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
          <StorageIcon sx={{ color: '#5B6FE5', fontSize: 20 }} />
          <Typography
            variant="subtitle1"
            sx={{
              fontWeight: 600,
              color: '#1F2937',
              fontSize: '0.9375rem'
            }}
          >
            Select Source
          </Typography>
        </Box>

        <TextField
          select
          size="small"
          value={selectedSource || ""}
          SelectProps={{ native: true }}
          onChange={(e) => {
            setSelectedSource(e.target.value);
            setSelectedSchema(null);
          }}
          disabled={error !== null}
          sx={{
            minWidth: 240,
            '& .MuiOutlinedInput-root': {
              bgcolor: '#FFFFFF',
              '& fieldset': {
                borderColor: '#E5E7EB',
              },
              '&:hover fieldset': {
                borderColor: '#5B6FE5',
              },
              '&.Mui-focused fieldset': {
                borderColor: '#5B6FE5',
                borderWidth: '2px',
              },
            },
          }}
        >
          <option value="">-- Select a Source --</option>
          {connections
            .filter((c) => c.status === "connected")
            .map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
        </TextField>

        {loading && (
          <CircularProgress size={20} sx={{ color: '#5B6FE5' }} />
        )}
      </Box>

      {/* 3 COLUMN LAYOUT */}
      <Box sx={{ display: "flex", gap: 1.5, flex: 1, minHeight: 0 }}>

        {/* ================= SCHEMAS ================= */}
        <Card
          elevation={0}
          sx={{
            flex: 1.2,
            display: "flex",
            flexDirection: "column",
            border: '1px solid #E5E7EB',
            borderRadius: 1.5,
            overflow: 'hidden',
            minHeight: 0
          }}
        >
          <Box sx={{
            p: 1.25,
            pb: 0.75,
            bgcolor: '#F9FAFB',
            borderBottom: '1px solid #E5E7EB'
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.75 }}>
              <Box
                sx={{
                  width: 26,
                  height: 26,
                  borderRadius: 1,
                  bgcolor: '#5B6FE5',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <StorageIcon sx={{ color: '#FFFFFF', fontSize: 15 }} />
              </Box>
              <Typography
                sx={{
                  fontWeight: 600,
                  color: '#1F2937',
                  fontSize: '0.875rem'
                }}
              >
                Schemas
              </Typography>
              {selectedSource && schemaList.length > 0 && (
                <Chip
                  label={`${schemaList.length}`}
                  size="small"
                  sx={{
                    height: 16,
                    fontSize: '0.625rem',
                    bgcolor: '#EEF2FF',
                    color: '#5B6FE5',
                    fontWeight: 500,
                    '& .MuiChip-label': {
                      px: 0.75
                    }
                  }}
                />
              )}
            </Box>

            <TextField
              size="small"
              placeholder="Search..."
              fullWidth
              value={searchSchema}
              onChange={(e) => setSearchSchema(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon sx={{ color: '#6B7280', fontSize: 16 }} />
                  </InputAdornment>
                ),
                endAdornment: searchSchema && (
                  <InputAdornment position="end">
                    <IconButton
                      size="small"
                      onClick={() => setSearchSchema('')}
                      sx={{ padding: 0.25 }}
                    >
                      <ClearIcon sx={{ fontSize: 14 }} />
                    </IconButton>
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
          </Box>

          <Box
            sx={{
              flex: 1,
              overflowY: "auto",
              p: 0.75,
              maxHeight: 'calc(100vh - 52vh)',
              '&::-webkit-scrollbar': {
                width: '8px',
              },
              '&::-webkit-scrollbar-track': {
                bgcolor: '#F9FAFB',
              },
              '&::-webkit-scrollbar-thumb': {
                bgcolor: '#D1D5DB',
                borderRadius: '4px',
                '&:hover': {
                  bgcolor: '#9CA3AF',
                },
              },
            }}
          >
            {error ? (
              <Alert
                severity="info"
                sx={{
                  fontSize: '0.8125rem',
                  '& .MuiAlert-icon': { fontSize: 18 }
                }}
              >
                Unable to load schemas. Please check the backend connection.
              </Alert>
            ) : !selectedSource ? (
              <Alert
                severity="info"
                sx={{
                  fontSize: '0.8125rem',
                  '& .MuiAlert-icon': { fontSize: 18 }
                }}
              >
                Please select a source first
              </Alert>
            ) : schemaList.length === 0 ? (
              <Alert
                severity="warning"
                sx={{
                  fontSize: '0.8125rem',
                  '& .MuiAlert-icon': { fontSize: 18 }
                }}
              >
                No schemas found
              </Alert>
            ) : (
              schemaList.map((schema) => (
                <Box
                  key={schema}
                  onClick={() => {
                    setSelectedSchema(schema);
                    loadTablesForSchema(selectedSource, schema);
                  }}
                  sx={{
                    p: 0.75,
                    mb: 0.5,
                    borderRadius: 0.75,
                    cursor: "pointer",
                    fontSize: '0.8125rem',
                    color: '#1F2937',
                    bgcolor: selectedSchema === schema ? '#EEF2FF' : '#FFFFFF',
                    border: selectedSchema === schema ? '1px solid #5B6FE5' : '1px solid #E5E7EB',
                    transition: 'all 0.2s ease',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    "&:hover": {
                      bgcolor: selectedSchema === schema ? '#EEF2FF' : '#F9FAFB',
                      borderColor: '#5B6FE5',
                      transform: 'translateX(2px)'
                    }
                  }}
                >
                  <Typography
                    sx={{
                      fontSize: '0.8125rem',
                      fontWeight: 500,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}
                  >
                    {schema}
                  </Typography>
                  {selectedSchema === schema && (
                    <CheckCircleIcon sx={{ color: '#5B6FE5', fontSize: 16, flexShrink: 0, ml: 0.5 }} />
                  )}
                </Box>
              ))
            )}
          </Box>
        </Card>

        {/* ================= TABLES ================= */}
        <Card
          elevation={0}
          sx={{
            flex: 2,
            display: "flex",
            flexDirection: "column",
            border: '1px solid #E5E7EB',
            borderRadius: 1.5,
            overflow: 'hidden',
            minHeight: 0
          }}
        >
          <Box sx={{
            p: 1.25,
            pb: 0.75,
            bgcolor: '#F9FAFB',
            borderBottom: '1px solid #E5E7EB'
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.75 }}>
              <Box
                sx={{
                  width: 26,
                  height: 26,
                  borderRadius: 1,
                  bgcolor: '#5B6FE5',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <TableChartIcon sx={{ color: '#FFFFFF', fontSize: 15 }} />
              </Box>
              <Typography
                sx={{
                  fontWeight: 600,
                  color: '#1F2937',
                  fontSize: '0.875rem'
                }}
              >
                Entities
              </Typography>
              {selectedSchema && tablesForSchema.length > 0 && (
                <Chip
                  label={`${tablesForSchema.length}`}
                  size="small"
                  sx={{
                    height: 16,
                    fontSize: '0.625rem',
                    bgcolor: '#EEF2FF',
                    color: '#5B6FE5',
                    fontWeight: 500,
                    '& .MuiChip-label': {
                      px: 0.75
                    }
                  }}
                />
              )}
            </Box>

            <TextField
              size="small"
              placeholder="Search..."
              fullWidth
              value={searchTables}
              onChange={(e) => setSearchTables(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon sx={{ color: '#6B7280', fontSize: 16 }} />
                  </InputAdornment>
                ),
                endAdornment: searchTables && (
                  <InputAdornment position="end">
                    <IconButton
                      size="small"
                      onClick={() => setSearchTables('')}
                      sx={{ padding: 0.25 }}
                    >
                      <ClearIcon sx={{ fontSize: 14 }} />
                    </IconButton>
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
          </Box>

          <Box
            sx={{
              flex: 1,
              overflowY: "auto",
              p: 0.75,
              maxHeight: 'calc(100vh - 52vh)',
              '&::-webkit-scrollbar': {
                width: '8px',
              },
              '&::-webkit-scrollbar-track': {
                bgcolor: '#F9FAFB',
              },
              '&::-webkit-scrollbar-thumb': {
                bgcolor: '#D1D5DB',
                borderRadius: '4px',
                '&:hover': {
                  bgcolor: '#9CA3AF',
                },
              },
            }}
          >
            {error ? (
              <Alert
                severity="info"
                sx={{
                  fontSize: '0.8125rem',
                  '& .MuiAlert-icon': { fontSize: 18 }
                }}
              >
                Unable to load tables. Please check the backend connection.
              </Alert>
            ) : !selectedSchema ? (
              <Alert
                severity="info"
                sx={{
                  fontSize: '0.8125rem',
                  '& .MuiAlert-icon': { fontSize: 18 }
                }}
              >
                Select a schema to view tables
              </Alert>
            ) : tablesForSchema.length === 0 ? (
              <Alert
                severity="warning"
                sx={{
                  fontSize: '0.8125rem',
                  '& .MuiAlert-icon': { fontSize: 18 }
                }}
              >
                No tables found in this schema
              </Alert>
            ) : (
              tablesForSchema.map((t) => {
                const conn = connections.find((c) => c.id == selectedSource);
                const isSelected = selectedSchemaTables.some((u) => u.key === t.key);

                return (
                  <Box
                    key={t.key}
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      p: 0.75,
                      mb: 0.5,
                      borderRadius: 0.75,
                      border: '1px solid #E5E7EB',
                      bgcolor: isSelected ? '#F0FDF4' : '#FFFFFF',
                      cursor: "pointer",
                      transition: 'all 0.2s ease',
                      "&:hover": {
                        bgcolor: isSelected ? '#F0FDF4' : '#F9FAFB',
                        borderColor: '#5B6FE5',
                        transform: 'translateX(2px)'
                      }
                    }}
                    onClick={() =>
                      toggleTable(selectedSource, conn?.name, selectedSchema, t)
                    }
                  >
                    <Box sx={{ display: "flex", alignItems: "center", gap: 0.75, flex: 1, minWidth: 0 }}>
                      <Checkbox
                        checked={isSelected}
                        onChange={() =>
                          toggleTable(selectedSource, conn?.name, selectedSchema, t)
                        }
                        onClick={(e) => e.stopPropagation()}
                        sx={{
                          color: '#D1D5DB',
                          padding: '2px',
                          '&.Mui-checked': {
                            color: '#5B6FE5',
                          },
                        }}
                      />
                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography
                          sx={{
                            fontSize: '0.8125rem',
                            fontWeight: 500,
                            color: '#1F2937',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                          }}
                        >
                          {t.name}
                        </Typography>
                        {t.row_count !== undefined && (
                          <Typography
                            sx={{
                              fontSize: '0.6875rem',
                              color: '#6B7280',
                              mt: 0
                            }}
                          >
                            {t.row_count.toLocaleString()} rows
                          </Typography>
                        )}
                      </Box>
                    </Box>
                    <Chip
                      label={selectedSchema}
                      size="small"
                      sx={{
                        height: 18,
                        fontSize: '0.625rem',
                        bgcolor: '#EEF2FF',
                        color: '#5B6FE5',
                        border: 'none',
                        fontWeight: 500,
                        flexShrink: 0,
                        ml: 0.5,
                        '& .MuiChip-label': {
                          px: 0.75
                        }
                      }}
                    />
                  </Box>
                );
              })
            )}
          </Box>
        </Card>

        {/* ================= SELECTED TABLES ================= */}
        <Card
          elevation={0}
          sx={{
            flex: 1.8,
            display: "flex",
            flexDirection: "column",
            border: '1px solid #E5E7EB',
            borderRadius: 1.5,
            overflow: 'hidden',
            minHeight: 0
          }}
        >
          <Box sx={{
            p: 1.25,
            pb: 0.75,
            bgcolor: '#F9FAFB',
            borderBottom: '1px solid #E5E7EB'
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.75 }}>
              <Box
                sx={{
                  width: 26,
                  height: 26,
                  borderRadius: 1,
                  bgcolor: '#10B981',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <CheckCircleIcon sx={{ color: '#FFFFFF', fontSize: 15 }} />
              </Box>
              <Typography
                sx={{
                  fontWeight: 600,
                  color: '#1F2937',
                  fontSize: '0.875rem'
                }}
              >
                Selected Entities
              </Typography>
              {selectedTableList.length > 0 && (
                <Chip
                  label={`${selectedTableList.length}`}
                  size="small"
                  sx={{
                    height: 16,
                    fontSize: '0.625rem',
                    bgcolor: '#D1FAE5',
                    color: '#059669',
                    fontWeight: 500,
                    '& .MuiChip-label': {
                      px: 0.75
                    }
                  }}
                />
              )}
            </Box>

            <TextField
              size="small"
              placeholder="Search..."
              fullWidth
              value={searchSelected}
              onChange={(e) => setSearchSelected(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon sx={{ color: '#6B7280', fontSize: 16 }} />
                  </InputAdornment>
                ),
                endAdornment: searchSelected && (
                  <InputAdornment position="end">
                    <IconButton
                      size="small"
                      onClick={() => setSearchSelected('')}
                      sx={{ padding: 0.25 }}
                    >
                      <ClearIcon sx={{ fontSize: 14 }} />
                    </IconButton>
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
                    borderColor: '#10B981',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#10B981',
                    borderWidth: '1px',
                  },
                  '& input': {
                    py: 0.75
                  }
                },
              }}
            />
          </Box>

          <Box
            sx={{
              flex: 1,
              overflowY: "auto",
              p: 0.75,
              maxHeight: 'calc(100vh - 52vh)',
              '&::-webkit-scrollbar': {
                width: '8px',
              },
              '&::-webkit-scrollbar-track': {
                bgcolor: '#F9FAFB',
              },
              '&::-webkit-scrollbar-thumb': {
                bgcolor: '#D1D5DB',
                borderRadius: '4px',
                '&:hover': {
                  bgcolor: '#9CA3AF',
                },
              },
            }}
          >
            {selectedTableList.length === 0 ? (
              <Alert
                severity="info"
                sx={{
                  fontSize: '0.8125rem',
                  '& .MuiAlert-icon': { fontSize: 18 }
                }}
              >
                No tables selected yet. Select tables from the middle panel.
              </Alert>
            ) : (
              selectedTableList.map((t) => (
                <Box
                  key={t.key}
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    p: 0.75,
                    mb: 0.5,
                    borderRadius: 0.75,
                    border: '1px solid #D1FAE5',
                    bgcolor: '#F0FDF4',
                    transition: 'all 0.2s ease',
                    "&:hover": {
                      bgcolor: '#ECFDF5',
                      borderColor: '#10B981',
                      transform: 'translateX(-2px)'
                    }
                  }}
                >
                  <Box sx={{ flex: 1, minWidth: 0 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 0.75 }}>
                      <Typography
                        sx={{
                          fontSize: '0.8125rem',
                          fontWeight: 500,
                          color: '#1F2937',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}
                      >
                        {t.tableName}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, flexShrink: 0 }}>
                        <Chip
                          label={t.connectionName}
                          size="small"
                          sx={{
                            height: 18,
                            fontSize: '0.625rem',
                            bgcolor: '#EEF2FF',
                            color: '#5B6FE5',
                            border: 'none',
                            fontWeight: 500,
                            '& .MuiChip-label': {
                              px: 0.75
                            }
                          }}
                        />
                        <Chip
                          label={t.databaseName}
                          size="small"
                          sx={{
                            height: 18,
                            fontSize: '0.625rem',
                            bgcolor: '#D1FAE5',
                            color: '#059669',
                            border: 'none',
                            fontWeight: 500,
                            '& .MuiChip-label': {
                              px: 0.75
                            }
                          }}
                        />
                      </Box>
                    </Box>
                  </Box>
                </Box>
              ))
            )}
          </Box>
        </Card>

      </Box>
    </Box>
  );

}

export default DatabaseConnectionsStep;
