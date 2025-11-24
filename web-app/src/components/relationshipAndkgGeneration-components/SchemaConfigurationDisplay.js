import { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  Button,
  List,
  ListItem,
  ListItemButton,
  Collapse,
  Divider,
} from '@mui/material';
import {
  Refresh,
  ExpandMore,
  ExpandLess,
  Storage,
  TableChart,
  ViewColumn,
  Link as LinkIcon,
  CheckCircle,
} from '@mui/icons-material';
import { getSchemaConfigurations } from '../../services/api';

/**
 * Get the display name for a table.
 * Returns the primary alias if available, otherwise returns the actual table name.
 * @param {Object} table - The table object from schema configuration
 * @returns {string} - The display name to show to users
 */
const getTableDisplayName = (table) => {
  // First check for primaryAlias
  if (table.primaryAlias && table.primaryAlias.trim()) {
    return table.primaryAlias;
  }
  // Fall back to first alias in tableAliases array
  if (table.tableAliases && table.tableAliases.length > 0 && table.tableAliases[0].trim()) {
    return table.tableAliases[0];
  }
  // Fall back to actual table name
  return table.tableName;
};

export default function SchemaConfigurationDisplay({ onSchemaLoaded }) {
  const [configurations, setConfigurations] = useState([]);
  const [selectedConfigId, setSelectedConfigId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedConfigs, setExpandedConfigs] = useState({}); // Level 1: Schema Configuration
  const [expandedEntities, setExpandedEntities] = useState({}); // Level 2: Entities/Tables

  useEffect(() => {
    fetchConfigurations();
  }, []);

  const fetchConfigurations = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getSchemaConfigurations();
      const configs = response.data.configurations || [];
      setConfigurations(configs);
      // Do NOT automatically select the first configuration
      // User must manually select one
      setSelectedConfigId(null);
      // Notify parent component that selection has been cleared
      onSchemaLoaded(null);
    } catch (err) {
      const errorMessage = err.code === 'ERR_NETWORK' || err.message === 'Network Error'
        ? 'Unable to connect to the backend server. Please ensure the backend is running on http://localhost:8000'
        : err.response?.data?.detail || 'Failed to load schema configurations';
      setError(errorMessage);
      console.error('Error fetching configurations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectConfig = (config, configIndex) => {
    // Single-selection behavior: only one schema can be selected at a time
    setSelectedConfigId(config.id);
    onSchemaLoaded(config);

    // Auto-expand the selected configuration
    setExpandedConfigs({ [configIndex]: true });
  };

  const handleToggleConfig = (configIndex, event) => {
    // Prevent triggering selection when toggling expand/collapse
    event.stopPropagation();
    setExpandedConfigs((prev) => ({
      ...prev,
      [configIndex]: !prev[configIndex],
    }));
  };

  const handleToggleEntity = (entityKey) => {
    setExpandedEntities((prev) => ({
      ...prev,
      [entityKey]: !prev[entityKey],
    }));
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (configurations.length === 0) {
    return (
      <Alert severity="info">
        No schema configurations found. Please create one using the Schema Wizard.
      </Alert>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header with Refresh Button */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography
          variant="subtitle1"
          sx={{
            fontWeight: 600,
            color: '#1F2937',
            fontSize: '0.95rem',
          }}
        >
          Schema Configurations
        </Typography>
        <Button
          startIcon={<Refresh />}
          onClick={fetchConfigurations}
          size="small"
          variant="outlined"
          sx={{
            px: 1.5,
            py: 0.5,
            minWidth: 'auto',
            color: '#64748B',
            borderColor: '#CBD5E1',
            fontSize: '0.8125rem',
            textTransform: 'none',
            borderRadius: '8px',
            '&:hover': {
              bgcolor: '#F8FAFC',
              borderColor: '#94A3B8',
              color: '#475569',
            },
          }}
        >
          Refresh
        </Button>
      </Box>

      {/* Three-Level Hierarchical Accordion */}
      <Paper
        elevation={0}
        sx={{
          flex: 1,
          border: '1px solid #E5E7EB',
          borderRadius: 1,
          overflow: 'auto',
        }}
      >
        <List disablePadding>
          {configurations.map((config, configIndex) => {
            const configName = config.schemaName || config.id;
            return (
              <Box key={configIndex}>
                {/* Level 1: Schema Configuration */}
                <ListItem
                  disablePadding
                  sx={{
                    borderBottom: '1px solid #E5E7EB',
                  }}
                >
                  <ListItemButton
                    onClick={() => handleSelectConfig(config, configIndex)}
                    selected={selectedConfigId === config.id}
                    sx={{
                      py: 1.5,
                      px: 2,
                      bgcolor: selectedConfigId === config.id ? '#EEF2FF' : '#F9FAFB',
                      borderLeft: selectedConfigId === config.id ? '4px solid #5B6FE5' : '4px solid transparent',
                      '&:hover': {
                        bgcolor: selectedConfigId === config.id ? '#E0E7FF' : '#F3F4F6',
                      },
                      '&.Mui-selected': {
                        bgcolor: '#EEF2FF',
                        '&:hover': {
                          bgcolor: '#E0E7FF',
                        },
                      },
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, width: '100%' }}>
                      {selectedConfigId === config.id ? (
                        <CheckCircle sx={{ fontSize: '1.5rem', color: '#5B6FE5' }} />
                      ) : (
                        <Storage sx={{ fontSize: '1.5rem', color: '#5B6FE5' }} />
                      )}
                      <Box sx={{ flex: 1 }}>
                        <Typography
                          sx={{
                            fontWeight: 600,
                            fontSize: '0.95rem',
                            color: '#1F2937',
                          }}
                        >
                          {configName}
                        </Typography>
                        <Typography
                          sx={{
                            fontSize: '0.75rem',
                            color: '#6B7280',
                            mt: 0.25,
                          }}
                        >
                          {config.id}
                        </Typography>
                      </Box>
                      <Chip
                        label={`${config.tables.length} ${config.tables.length === 1 ? 'entity' : 'entities'}`}
                        size="small"
                        sx={{
                          height: '22px',
                          fontSize: '0.7rem',
                          bgcolor: '#E0E7FF',
                          color: '#4F46E5',
                          fontWeight: 600,
                        }}
                      />
                      {selectedConfigId === config.id && (
                        <Box
                          onClick={(e) => handleToggleConfig(configIndex, e)}
                          sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 0.5,
                            cursor: 'pointer',
                            '&:hover': {
                              opacity: 0.7,
                            },
                          }}
                        >
                          {expandedConfigs[configIndex] ? (
                            <ExpandLess sx={{ fontSize: '1.3rem', color: '#5B6FE5' }} />
                          ) : (
                            <ExpandMore sx={{ fontSize: '1.3rem', color: '#5B6FE5' }} />
                          )}
                        </Box>
                      )}
                    </Box>
                  </ListItemButton>
                </ListItem>

                {/* Level 2: Entities/Tables - Only show when schema is selected */}
                <Collapse in={selectedConfigId === config.id && expandedConfigs[configIndex]} timeout="auto" unmountOnExit>
                  <List disablePadding sx={{ bgcolor: '#FFFFFF' }}>
                    {config.tables.map((table, tableIndex) => {
                      const entityKey = `${configIndex}-${tableIndex}`;
                      return (
                        <Box key={entityKey}>
                        <ListItem
                          disablePadding
                          sx={{
                            borderBottom: '1px solid #F3F4F6',
                          }}
                        >
                          <ListItemButton
                            onClick={() => handleToggleEntity(entityKey)}
                            sx={{
                              py: 1.25,
                              px: 2,
                              pl: 6,
                              '&:hover': {
                                bgcolor: '#F9FAFB',
                              },
                            }}
                          >
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, width: '100%' }}>
                              {expandedEntities[entityKey] ? (
                                <ExpandLess sx={{ fontSize: '1.3rem', color: '#6B7280' }} />
                              ) : (
                                <ExpandMore sx={{ fontSize: '1.3rem', color: '#6B7280' }} />
                              )}
                              <TableChart sx={{ fontSize: '1.3rem', color: '#7C8FE5' }} />
                              <Box sx={{ flex: 1 }}>
                                <Typography
                                  sx={{
                                    fontWeight: 600,
                                    fontSize: '0.875rem',
                                    color: '#1F2937',
                                  }}
                                >
                                  {getTableDisplayName(table)}
                                </Typography>
                                {/* Show actual table name if it differs from display name */}
                                {getTableDisplayName(table) !== table.tableName && (
                                  <Typography
                                    sx={{
                                      fontSize: '0.7rem',
                                      color: '#9CA3AF',
                                      mt: 0.25,
                                      fontStyle: 'italic',
                                    }}
                                  >
                                    Table: {table.tableName}
                                  </Typography>
                                )}
                              </Box>
                              <Chip
                                label={`${table.columns.length} columns`}
                                size="small"
                                sx={{
                                  height: '22px',
                                  fontSize: '0.7rem',
                                  bgcolor: '#EEF2FF',
                                  color: '#5B6FE5',
                                }}
                              />
                            </Box>
                          </ListItemButton>
                        </ListItem>


                        {/* Level 3: Columns */}
                        <Collapse in={expandedEntities[entityKey]} timeout="auto" unmountOnExit>
                          <List disablePadding sx={{ bgcolor: '#F9FAFB' }}>
                            {table.columns.map((column, columnIndex) => (
                              <ListItem
                                key={columnIndex}
                                sx={{
                                  py: 1,
                                  px: 2,
                                  pl: 10,
                                  borderBottom: columnIndex < table.columns.length - 1 ? '1px solid #F3F4F6' : 'none',
                                  '&:hover': {
                                    bgcolor: '#F5F7FF',
                                  },
                                }}
                              >
                                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5, width: '100%' }}>
                                  <ViewColumn sx={{ fontSize: '1.1rem', color: '#9CA3AF', mt: 0.25 }} />
                                  <Box sx={{ flex: 1 }}>
                                    <Typography
                                      sx={{
                                        fontWeight: 500,
                                        fontSize: '0.8125rem',
                                        color: '#1F2937',
                                      }}
                                    >
                                      {column.name}
                                    </Typography>

                                    {/* Column Aliases */}
                                    {column.aliases && column.aliases.length > 0 && (
                                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75, mt: 0.5 }}>
                                        <Typography
                                          sx={{
                                            fontSize: '0.7rem',
                                            color: '#6B7280',
                                          }}
                                        >
                                          Aliases:
                                        </Typography>
                                        {column.aliases.map((alias, aliasIdx) => (
                                          <Chip
                                            key={aliasIdx}
                                            label={alias}
                                            size="small"
                                            sx={{
                                              height: '18px',
                                              fontSize: '0.65rem',
                                              bgcolor: '#F0F4FF',
                                              color: '#7C8FE5',
                                            }}
                                          />
                                        ))}
                                      </Box>
                                    )}

                                    {/* Column Relationships */}
                                    {column.relationships && column.relationships.length > 0 && (
                                      <Box sx={{ mt: 0.75 }}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                                          <LinkIcon sx={{ fontSize: '0.9rem', color: '#10B981' }} />
                                          <Typography
                                            sx={{
                                              fontSize: '0.7rem',
                                              color: '#059669',
                                              fontWeight: 600,
                                            }}
                                          >
                                            Relationships:
                                          </Typography>
                                        </Box>
                                        {column.relationships.map((rel, relIdx) => (
                                          <Box
                                            key={relIdx}
                                            sx={{
                                              display: 'flex',
                                              alignItems: 'center',
                                              gap: 0.75,
                                              mt: 0.5,
                                              pl: 1.5,
                                            }}
                                          >
                                            <Typography
                                              sx={{
                                                fontSize: '0.7rem',
                                                color: '#6B7280',
                                              }}
                                            >
                                              →
                                            </Typography>
                                            <Chip
                                              label={(() => {
                                                // Find the target table to get its display name
                                                const targetTable = config.tables.find(t => t.tableName === rel.targetTable);
                                                const targetDisplayName = targetTable ? getTableDisplayName(targetTable) : rel.targetTable;
                                                return `${targetDisplayName}.${rel.targetColumn}`;
                                              })()}
                                              size="small"
                                              sx={{
                                                height: '18px',
                                                fontSize: '0.65rem',
                                                bgcolor: '#D1FAE5',
                                                color: '#065F46',
                                                fontWeight: 500,
                                              }}
                                            />
                                            {rel.relationshipType && (
                                              <Typography
                                                sx={{
                                                  fontSize: '0.65rem',
                                                  color: '#9CA3AF',
                                                  fontStyle: 'italic',
                                                }}
                                              >
                                                ({rel.relationshipType})
                                              </Typography>
                                            )}
                                          </Box>
                                        ))}
                                      </Box>
                                    )}
                                  </Box>
                                </Box>
                              </ListItem>
                            ))}
                          </List>
                        </Collapse>
                      </Box>
                    );
                  })}
                </List>
              </Collapse>
              <Divider />
            </Box>
            );
          })}
        </List>
      </Paper>
    </Box>
  );
}

