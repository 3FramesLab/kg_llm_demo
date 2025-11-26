import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Tabs,
  Tab,
  Chip,
  TextField,
  InputAdornment,
  Paper,
  Tooltip,
} from '@mui/material';
import {
  Close as CloseIcon,
  Search as SearchIcon,
  AddLink as AddLinkIcon,
} from '@mui/icons-material';

export default function NodeDetailsDialog({
  open,
  node,
  allNodes = [],
  relationships = [],
  relationshipStyles = {},
  onClose,
  onAddRelationship, // New prop for adding relationships
}) {
  const [activeTab, setActiveTab] = useState(0);

  // Reset state when panel closes
  useEffect(() => {
    if (!open) {
      setActiveTab(0);
    }
  }, [open]);

  const handleTabChange = (_event, newValue) => {
    setActiveTab(newValue);
  };

  const handleAddRelationship = () => {
    if (onAddRelationship) {
      onAddRelationship(node);
    }
  };

  if (!open || !node) return null;

  return (
    <Paper
      elevation={0}
      sx={{
        height: '100%',
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderLeft: '1px solid #E5E7EB',
        borderRadius: 0,
        overflow: 'hidden',
      }}
    >
      <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Box
          sx={{
            px: 1.5,
            py: 1,
            borderBottom: '1px solid #E5E7EB',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            bgcolor: '#F9FAFB',
          }}
        >
          <Typography variant="h6" sx={{ fontWeight: 700, color: '#1F2937', fontSize: '0.95rem' }}>
            {node.name || node.id}
          </Typography>
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            {/* Add Relationship button hidden as per requirement */}
            {/* {onAddRelationship && (
              <Tooltip title="Add Relationship" placement="left">
                <IconButton
                  onClick={handleAddRelationship}
                  size="small"
                  sx={{
                    color: '#5B6FE5',
                    '&:hover': {
                      bgcolor: '#EEF2FF',
                    },
                  }}
                >
                  <AddLinkIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )} */}
            <IconButton onClick={onClose} size="small">
              <CloseIcon />
            </IconButton>
          </Box>
        </Box>

        {/* Tabs Navigation */}
        <Box sx={{ borderBottom: '1px solid #E5E7EB', py: 0 }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="fullWidth"
            sx={{
              minHeight: 32,
              '& .MuiTab-root': {
                color: '#6B7280',
                fontSize: '0.8125rem',
                fontWeight: 600,
                textTransform: 'none',
                minHeight: 32,
                py: 0.5,
                px: 1,
              },
              '& .Mui-selected': {
                color: '#5B6FE5',
              },
              '& .MuiTabs-indicator': {
                backgroundColor: '#5B6FE5',
              },
            }}
          >
            <Tab label="Summary" />
            <Tab label="Properties" />
            <Tab label="Relationships" />
          </Tabs>
        </Box>

        {/* Content Area */}
        <Box sx={{ flex: 1, overflow: 'auto', px: 1.5, py: 1.5 }}>
          {activeTab === 0 && <StepSummary node={node} />}
          {activeTab === 1 && <StepProperties node={node} />}
          {activeTab === 2 && (
            <StepRelationships
              node={node}
              relationships={relationships}
              allNodes={allNodes}
              relationshipStyles={relationshipStyles}
            />
          )}
        </Box>
      </Box>
    </Paper>
  );
}

// Step 1: Summary (Read-only overview - Compact Table Format)
function StepSummary({ node }) {
  if (!node) return null;

  const properties = node.properties || {};

  // Get source table name from node
  const sourceTableName = node.originalEntity?.source_table || properties.source_table || node.label || 'N/A';

  // Get aliases - check multiple possible locations
  // 1. Check if aliases are stored in properties
  // 2. Check if primary_alias exists
  // 3. Check node name
  const aliases = [];
  if (properties.primary_alias) {
    aliases.push(properties.primary_alias);
  }
  if (node.name && node.name !== sourceTableName && !aliases.includes(node.name)) {
    aliases.push(node.name);
  }
  // If no aliases found, show a default message
  const aliasesDisplay = aliases.length > 0 ? aliases.join(', ') : 'No aliases available';

  // Count columns/properties
  const columns = Array.isArray(properties.columns) ? properties.columns : [];
  const propertyCount = columns.length;

  // Table row style
  const tableRowStyle = {
    display: 'flex',
    alignItems: 'flex-start',
    py: 1,
    px: 1.5,
    borderBottom: '1px solid #E5E7EB',
    '&:last-child': {
      borderBottom: 'none',
    },
  };

  const labelStyle = {
    fontWeight: 700,
    color: '#1F2937',
    fontSize: '0.8125rem',
    minWidth: '140px',
    flex: '0 0 140px',
    pt: 0.25,
  };

  const valueStyle = {
    color: '#6B7280',
    fontSize: '0.8125rem',
    flex: 1,
    wordBreak: 'break-word',
  };

  return (
    <Box>
      {/* Source Table Name Row */}
      <Box sx={tableRowStyle}>
        <Typography sx={labelStyle}>Source Table Name</Typography>
        <Typography sx={valueStyle}>{sourceTableName}</Typography>
      </Box>

      {/* Aliases Row */}
      <Box sx={tableRowStyle}>
        <Typography sx={labelStyle}>Aliases</Typography>
        <Typography sx={valueStyle}>{aliasesDisplay}</Typography>
      </Box>

      {/* Properties Count Row */}
      <Box sx={tableRowStyle}>
        <Typography sx={labelStyle}>Properties</Typography>
        <Typography sx={valueStyle}>
          {propertyCount === 0 ? 'No properties' : `${propertyCount} ${propertyCount === 1 ? 'property' : 'properties'}`}
        </Typography>
      </Box>
    </Box>
  );
}

// Step 2: Properties (Read-only display - Key-Value Pairs)
function StepProperties({ node }) {
  const [searchQuery, setSearchQuery] = useState('');

  if (!node) return null;

  const properties = node.properties || {};

  // Extract columns array from properties
  const columns = Array.isArray(properties.columns) ? properties.columns : [];

  // Filter columns based on search query
  const filteredColumns = columns.filter((column) => {
    const searchLower = searchQuery.toLowerCase();
    const nameMatch = (column.name || '').toLowerCase().includes(searchLower);
    return nameMatch;
  });

  // Table row style (matching Summary tab)
  const tableRowStyle = {
    display: 'flex',
    alignItems: 'center',
    py: 0.75,
    px: 1,
    borderTop: '0.5px solid #E5E7EB',
    borderBottom: '0.5px solid #E5E7EB',
  };

  const labelStyle = {
    fontWeight: 600,
    color: '#6B7280',
    fontSize: '0.75rem',
    minWidth: '100px',
    flex: '0 0 100px',
  };

  return (
    <Box>
      {/* Search Bar */}
      <TextField
        fullWidth
        placeholder="Search..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon sx={{ color: '#9CA3AF', fontSize: '1.2rem' }} />
            </InputAdornment>
          ),
        }}
        sx={{
          mb: 1.5,
          '& .MuiOutlinedInput-root': {
            bgcolor: '#F9FAFB',
          },
        }}
      />

      {/* Properties List */}
      {filteredColumns.length > 0 ? (
        <Box>
          {filteredColumns.map((column, index) => (
            <Box key={index} sx={tableRowStyle}>
              <Typography sx={labelStyle}>
                {column.name || 'N/A'}
              </Typography>
            </Box>
          ))}
        </Box>
      ) : columns.length > 0 ? (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            py: 6,
          }}
        >
          <Typography variant="body2" sx={{ color: '#9CA3AF', fontStyle: 'italic' }}>
            No columns match your search
          </Typography>
        </Box>
      ) : (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            py: 4,
          }}
        >
          <Typography variant="body2" sx={{ color: '#9CA3AF', fontStyle: 'italic', fontSize: '0.8125rem' }}>
            No columns available
          </Typography>
        </Box>
      )}
    </Box>
  );
}

// Step 3: Relationships (Read-only display - List Format with Column-Level Details)
function StepRelationships({ node, relationships, allNodes, relationshipStyles = {} }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTypes, setSelectedTypes] = useState(['All']); // Filter by relationship types

  // Color palette matching KnowledgeGraphEditor node colors
  const DEPARTMENT_COLOR = 'rgb(95, 158, 160)'; // Teal/cyan for Department nodes (center node)
  const EMPLOYEE_COLOR = 'rgb(255, 160, 140)'; // Coral/peach for Employee nodes (surrounding nodes)
  const PROJECT_COLOR = 'rgb(0, 200, 220)'; // Bright cyan for Project nodes (from legend)

  const colorPalette = [
    EMPLOYEE_COLOR,    // Default: Employee color (most common)
    DEPARTMENT_COLOR,  // Department color
    PROJECT_COLOR,     // Project color
  ];

  // Function to generate a consistent color based on table name (matches KnowledgeGraphEditor)
  const getColorForTableName = (tableName) => {
    let hash = 0;
    for (let i = 0; i < tableName.length; i++) {
      const char = tableName.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    const index = Math.abs(hash) % colorPalette.length;
    return colorPalette[index];
  };

  if (!node) return null;

  // Filter relationships to show ONLY those connected to the selected node
  // Include relationships where the node is either the source OR the target
  const nodeRelationships = relationships.filter((rel) => {
    const sourceId = typeof rel.source === 'object' ? rel.source?.id : rel.source;
    const targetId = typeof rel.target === 'object' ? rel.target?.id : rel.target;
    return sourceId === node.id || targetId === node.id;
  });

  // Remove duplicate bidirectional relationships
  // If a relationship exists between Node A and Node B, show it only once
  const uniqueRelationships = [];
  const seenPairs = new Set();

  nodeRelationships.forEach((rel) => {
    const sourceId = typeof rel.source === 'object' ? rel.source?.id : rel.source;
    const targetId = typeof rel.target === 'object' ? rel.target?.id : rel.target;

    // Create a normalized key that's the same regardless of direction
    const pairKey = [sourceId, targetId].sort().join('↔');

    // Only add if we haven't seen this pair before
    if (!seenPairs.has(pairKey)) {
      seenPairs.add(pairKey);
      uniqueRelationships.push(rel);
    }
  });

  // Get unique relationship types from unique relationships only
  const uniqueRelTypes = [...new Set(uniqueRelationships.map(rel => rel.type || rel.label || 'RELATED_TO'))];

  // Handle type filter toggle
  const handleTypeToggle = (type) => {
    if (type === 'All') {
      setSelectedTypes(['All']);
    } else {
      const newSelection = selectedTypes.includes('All')
        ? [type]
        : selectedTypes.includes(type)
        ? selectedTypes.filter(t => t !== type)
        : [...selectedTypes, type];

      setSelectedTypes(newSelection.length === 0 ? ['All'] : newSelection);
    }
  };

  // Helper function to get node names
  const getNodeName = (nodeIdOrObject) => {
    // Handle both node ID (string) and node object
    const nodeId = typeof nodeIdOrObject === 'object' ? nodeIdOrObject?.id : nodeIdOrObject;
    const foundNode = allNodes.find((n) => n.id === nodeId);
    return foundNode?.name || nodeId || 'Unknown';
  };

  // Filter by selected types and search query
  const filteredRelationships = uniqueRelationships.filter((rel) => {
    const relType = rel.type || rel.label || 'RELATED_TO';
    const sourceName = getNodeName(rel.source);
    const targetName = getNodeName(rel.target);
    const searchLower = searchQuery.toLowerCase();

    // Get column information from relationship properties or originalRel
    const sourceColumn = rel.originalRel?.source_column || rel.properties?.source_column || rel.source_column || '';
    const targetColumn = rel.originalRel?.target_column || rel.properties?.target_column || rel.target_column || '';

    // Type filter
    const typeMatch = selectedTypes.includes('All') || selectedTypes.includes(relType);

    // Search filter - now includes column names
    const searchMatch = searchQuery === '' ||
      relType.toLowerCase().includes(searchLower) ||
      (sourceName && sourceName.toLowerCase().includes(searchLower)) ||
      (targetName && targetName.toLowerCase().includes(searchLower)) ||
      (sourceColumn && sourceColumn.toLowerCase().includes(searchLower)) ||
      (targetColumn && targetColumn.toLowerCase().includes(searchLower));

    return typeMatch && searchMatch;
  });

  return (
    <Box>
      {/* Search Bar */}
      <TextField
        fullWidth
        placeholder="Search relationships..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon sx={{ color: '#9CA3AF', fontSize: '1.2rem' }} />
            </InputAdornment>
          ),
        }}
        sx={{
          mb: 1.5,
          '& .MuiOutlinedInput-root': {
            bgcolor: '#F9FAFB',
          },
        }}
      />

      {/* Relationship Type Filter */}
      {uniqueRelTypes.length > 0 && (
        <Box sx={{ mb: 1.5 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.75 }}>
            <Typography variant="caption" sx={{ color: '#6B7280', fontWeight: 600 }}>
              Filter by Type:
            </Typography>
            {uniqueRelationships.length > 0 && (
              <Chip
                label={`${filteredRelationships.length} of ${uniqueRelationships.length}`}
                size="small"
                sx={{
                  bgcolor: '#F3F4F6',
                  color: '#6B7280',
                  fontWeight: 600,
                  fontSize: '0.65rem',
                  height: 20,
                  border: '1px solid #E5E7EB',
                }}
              />
            )}
          </Box>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.75 }}>
            {/* All filter chip */}
            <Chip
              label="All"
              size="small"
              onClick={() => handleTypeToggle('All')}
              sx={{
                bgcolor: selectedTypes.includes('All') ? '#5B6FE5' : '#F9FAFB',
                color: selectedTypes.includes('All') ? 'white' : '#6B7280',
                fontWeight: 600,
                fontSize: '0.7rem',
                height: 24,
                cursor: 'pointer',
                border: selectedTypes.includes('All') ? 'none' : '1px solid #E5E7EB',
                '&:hover': {
                  bgcolor: selectedTypes.includes('All') ? '#4C5FD5' : '#E5E7EB',
                },
              }}
            />

            {/* Individual relationship type chips */}
            {uniqueRelTypes.map((relType) => {
              const style = relationshipStyles[relType] || relationshipStyles['DEFAULT'] || { color: '#BBBBBB' };
              const isSelected = selectedTypes.includes(relType);

              return (
                <Chip
                  key={relType}
                  label={relType}
                  size="small"
                  onClick={() => handleTypeToggle(relType)}
                  sx={{
                    bgcolor: isSelected ? style.color : '#F9FAFB',
                    color: isSelected ? 'white' : '#6B7280',
                    fontWeight: 600,
                    fontSize: '0.7rem',
                    height: 24,
                    cursor: 'pointer',
                    border: isSelected ? 'none' : `1px solid ${style.color}`,
                    '&:hover': {
                      bgcolor: isSelected ? style.color : '#E5E7EB',
                      opacity: isSelected ? 0.9 : 1,
                    },
                  }}
                />
              );
            })}
          </Box>
        </Box>
      )}

      {/* Relationships List */}
      {filteredRelationships.length > 0 ? (
        <Box>
          {filteredRelationships.map((rel, index) => {
            const relType = rel.type || rel.label || 'RELATED_TO';
            const sourceId = typeof rel.source === 'object' ? rel.source?.id : rel.source;
            const targetId = typeof rel.target === 'object' ? rel.target?.id : rel.target;
            const sourceName = String(getNodeName(rel.source));
            const targetName = String(getNodeName(rel.target));

            // Get column information from relationship
            const sourceColumn = rel.originalRel?.source_column || rel.properties?.source_column || rel.source_column || '';
            const targetColumn = rel.originalRel?.target_column || rel.properties?.target_column || rel.target_column || '';

            // Determine if current node is source or target
            const isSource = sourceId === node.id;
            const isTarget = targetId === node.id;

            // Determine display order based on current node position
            const displaySourceTable = isSource ? node.name : sourceName;
            const displayTargetTable = isSource ? targetName : (isTarget ? node.name : targetName);
            const displaySourceColumn = isSource ? sourceColumn : (isTarget ? targetColumn : sourceColumn);
            const displayTargetColumn = isSource ? targetColumn : (isTarget ? sourceColumn : targetColumn);

            // Get relationship style
            const style = relationshipStyles[relType] || relationshipStyles['DEFAULT'] || { color: '#5B6FE5' };

            return (
              <Box
                key={index}
                sx={{
                  py: 1,
                  px: 1.5,
                  borderBottom: '1px solid #E5E7EB',
                  '&:last-child': {
                    borderBottom: 'none',
                  },
                }}
              >
                {/* Header Row: Table-Level Relationship */}
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 0.75,
                    mb: 0.75,
                  }}
                >
                  <Typography
                    sx={{
                      fontSize: '0.8125rem',
                      color: getColorForTableName(displaySourceTable),
                      fontWeight: 700,
                    }}
                  >
                    {displaySourceTable}
                  </Typography>
                  <Typography
                    sx={{
                      fontSize: '0.8125rem',
                      color: '#9CA3AF',
                      fontWeight: 600,
                    }}
                  >
                    →
                  </Typography>
                  <Typography
                    sx={{
                      fontSize: '0.8125rem',
                      color: getColorForTableName(displayTargetTable),
                      fontWeight: 700,
                    }}
                  >
                    {displayTargetTable}
                  </Typography>
                </Box>

                {/* Detail Rows: Column-Level Relationships */}
                {(displaySourceColumn && displayTargetColumn) ? (
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 0.75,
                      flexWrap: 'wrap',
                    }}
                  >
                    {/* Source Column */}
                    <Typography
                      sx={{
                        fontSize: '0.75rem',
                        color: '#6B7280',
                        fontWeight: 500,
                        fontFamily: 'monospace',
                        bgcolor: '#F9FAFB',
                        px: 0.75,
                        py: 0.25,
                        borderRadius: 0.5,
                        border: '1px solid #E5E7EB',
                      }}
                    >
                      {displaySourceColumn}
                    </Typography>

                    {/* Relationship Type Badge */}
                    <Chip
                      label={relType}
                      size="small"
                      sx={{
                        bgcolor: style.color,
                        color: 'white',
                        fontWeight: 600,
                        fontSize: '0.65rem',
                        height: 20,
                        '& .MuiChip-label': {
                          px: 0.75,
                        },
                      }}
                    />

                    {/* Arrow */}
                    <Typography
                      sx={{
                        fontSize: '0.75rem',
                        color: '#9CA3AF',
                      }}
                    >
                      →
                    </Typography>

                    {/* Target Column */}
                    <Typography
                      sx={{
                        fontSize: '0.75rem',
                        color: '#6B7280',
                        fontWeight: 500,
                        fontFamily: 'monospace',
                        bgcolor: '#F9FAFB',
                        px: 0.75,
                        py: 0.25,
                        borderRadius: 0.5,
                        border: '1px solid #E5E7EB',
                      }}
                    >
                      {displayTargetColumn}
                    </Typography>
                  </Box>
                ) : (
                  /* Fallback: Show relationship type only if no column info */
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
                    <Chip
                      label={relType}
                      size="small"
                      sx={{
                        bgcolor: style.color,
                        color: 'white',
                        fontWeight: 600,
                        fontSize: '0.65rem',
                        height: 20,
                        '& .MuiChip-label': {
                          px: 0.75,
                        },
                      }}
                    />
                    <Typography
                      sx={{
                        fontSize: '0.7rem',
                        color: '#9CA3AF',
                        fontStyle: 'italic',
                      }}
                    >
                      (Table-level)
                    </Typography>
                  </Box>
                )}
              </Box>
            );
          })}
        </Box>
      ) : uniqueRelationships.length > 0 ? (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            py: 6,
          }}
        >
          <Typography variant="body2" sx={{ color: '#9CA3AF', fontStyle: 'italic', fontSize: '0.8125rem' }}>
            No relationships match your search
          </Typography>
        </Box>
      ) : (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            py: 4,
          }}
        >
          <Typography variant="body2" sx={{ color: '#9CA3AF', fontStyle: 'italic', fontSize: '0.8125rem' }}>
            No relationships available
          </Typography>
        </Box>
      )}
    </Box>
  );
}

