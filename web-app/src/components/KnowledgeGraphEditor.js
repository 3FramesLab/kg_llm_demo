import { useEffect, useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { Box, Paper, Typography, IconButton, Chip, Tooltip, Snackbar, Alert, CircularProgress, Divider } from '@mui/material';
import {
  ZoomIn,
  ZoomOut,
  CenterFocusStrong,
  Add as AddIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  AddLink as AddLinkIcon,
  Palette as PaletteIcon,
  Fullscreen as FullscreenIcon,
  FullscreenExit as FullscreenExitIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import NodeDetailsDialog from './NodeDetailsDialog';
import AddNodeDialog from './AddNodeDialog';
import CreateRelationshipDialog from './CreateRelationshipDialog';
import { createEntity, createRelationship } from '../services/api';

/**
 * KnowledgeGraphEditor Component
 * Renders a force-directed graph visualization with Neo4j-style data model support
 * Now supports full backend integration for node and relationship creation
 *
 * Props:
 * - kgName: Name of the knowledge graph (required for backend API calls)
 * - entities: Array of entity objects with:
 *   - id: unique identifier
 *   - label/name: display name
 *   - type: single type (backward compatibility) OR
 *   - labels: array of labels (Neo4j style) e.g., ['Person', 'Employee']
 *   - properties: object with all node properties
 * - relationships: Array of relationship objects with:
 *   - source_id: source node id
 *   - target_id: target node id
 *   - relationship_type/type: relationship type
 *   - properties: object with all relationship properties
 * - onNodeClick: Callback when a node is clicked
 * - onLinkClick: Callback when a link is clicked
 * - onRefresh: Callback to refresh entities and relationships after mutations
 */
export default function KnowledgeGraphEditor({
  kgName,
  entities = [],
  relationships = [],
  onNodeClick,
  onLinkClick,
  onRefresh,
}) {
  const fgRef = useRef();
  const [selectedNode, setSelectedNode] = useState(null);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [graphWidth, setGraphWidth] = useState(window.innerWidth * 0.95);

  // State for node details panel
  const [panelOpen, setPanelOpen] = useState(false);
  const [panelNode, setPanelNode] = useState(null);

  // State for dialogs
  const [addNodeDialogOpen, setAddNodeDialogOpen] = useState(false);
  const [createRelationshipDialogOpen, setCreateRelationshipDialogOpen] = useState(false);
  const [relationshipSourceNode, setRelationshipSourceNode] = useState(null);

  // State for notifications and loading
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [loading, setLoading] = useState(false);

  // State for UI features
  const [showLegend, setShowLegend] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Panel width constants
  const PANEL_WIDTH = 300;

  // Colors extracted from the reference image
  // These match the exact colors shown in the Knowledge Graph visualization
  const DEPARTMENT_COLOR = 'rgb(95, 158, 160)'; // Teal/cyan for Department nodes (center node)
  const EMPLOYEE_COLOR = 'rgb(255, 160, 140)'; // Coral/peach for Employee nodes (surrounding nodes)
  const PROJECT_COLOR = 'rgb(0, 200, 220)'; // Bright cyan for Project nodes (from legend)
  const SELECTION_BORDER_COLOR = 'rgb(64, 227, 241)'; // Bright cyan for selected nodes

  // Color palette using only the colors from the reference image
  const colorPalette = [
    EMPLOYEE_COLOR,    // Default: Employee color (most common)
    DEPARTMENT_COLOR,  // Department color
    PROJECT_COLOR,     // Project color
  ];

  // Function to generate a consistent color based on label/type
  const getColorForLabel = (label) => {
    let hash = 0;
    for (let i = 0; i < label.length; i++) {
      const char = label.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    const index = Math.abs(hash) % colorPalette.length;
    return colorPalette[index];
  };

  // Function to determine node color based on node type/label and relationships
  // Colors match the reference image exactly:
  // - Department nodes (or central/hub nodes) → Teal/Cyan (rgb(95, 158, 160))
  // - Employee nodes (or leaf/peripheral nodes) → Coral/Peach (rgb(255, 160, 140))
  // - Project nodes → Bright Cyan (rgb(0, 200, 220))
  const getNodeColorByRelationship = (nodeId, relationships, primaryLabel, allLabels) => {
    // Check all labels (not just primary) to determine node type
    const labels = allLabels || [primaryLabel];
    const labelsLower = labels.map(l => l.toLowerCase());

    // First, check for explicit node types from the reference image
    if (labelsLower.some(l => l.includes('department') || l.includes('dept'))) {
      return DEPARTMENT_COLOR;
    }

    if (labelsLower.some(l => l.includes('employee') || l.includes('person') || l.includes('user'))) {
      return EMPLOYEE_COLOR;
    }

    if (labelsLower.some(l => l.includes('project') || l.includes('proj'))) {
      return PROJECT_COLOR;
    }

    // For table nodes or generic nodes, determine color based on connectivity
    // Nodes with more connections (hub nodes) get Department color (teal)
    // Nodes with fewer connections (leaf nodes) get Employee color (coral)
    let connectionCount = 0;
    const normalizedNodeId = nodeId.startsWith('table_') ? nodeId.substring(6) : nodeId;

    relationships.forEach((rel) => {
      const sourceId = rel.source_id || rel.source_table;
      const targetId = rel.target_id || rel.target_table;
      const normalizedSourceId = sourceId?.startsWith('table_') ? sourceId.substring(6) : sourceId;
      const normalizedTargetId = targetId?.startsWith('table_') ? targetId.substring(6) : targetId;

      if (sourceId === nodeId || targetId === nodeId ||
        normalizedSourceId === normalizedNodeId || normalizedTargetId === normalizedNodeId) {
        connectionCount++;
      }
    });

    // Hub nodes (3+ connections) get Department color (teal)
    // Leaf nodes (1-2 connections) get Employee color (coral)
    if (connectionCount >= 3) {
      return DEPARTMENT_COLOR; // Hub/central node
    } else {
      return EMPLOYEE_COLOR; // Leaf/peripheral node
    }
  };

  // Function to get primary label from node (supports both old and new format)
  const getPrimaryLabel = (entity) => {
    // New format: labels array
    if (entity.labels && Array.isArray(entity.labels) && entity.labels.length > 0) {
      return entity.labels[0];
    }
    // Old format: single type property
    if (entity.type) {
      return entity.type;
    }
    // Fallback to properties.type
    if (entity.properties?.type) {
      return entity.properties.type;
    }
    return 'Unknown';
  };

  // Function to get all labels from node
  const getAllLabels = (entity) => {
    // New format: labels array
    if (entity.labels && Array.isArray(entity.labels) && entity.labels.length > 0) {
      return entity.labels;
    }
    // Old format: single type
    const type = entity.type || entity.properties?.type;
    return type ? [type] : ['Unknown'];
  };

  // Simplified relationship styling (1-2 colors for clarity)
  // Primary relationships: #9CA3AF (Cool Gray)
  // Important relationships: #FF5630 (Red-Orange)
  const relationshipStyles = {
    // Important/Critical relationships - Red-Orange
    'MATCHES': { color: '#FF5630', width: 2, dashArray: [] },
    'MATCHED_BY': { color: '#FF5630', width: 2, dashArray: [] },
    'PRIMARY_KEY': { color: '#FF5630', width: 2, dashArray: [] },
    'FOREIGN_KEY': { color: '#FF5630', width: 2, dashArray: [] },

    // All other relationships - Cool Gray (primary)
    'SEMANTIC_REFERENCE': { color: '#9CA3AF', width: 1.5, dashArray: [] },
    'SEMANTIC_REFERENCED_BY': { color: '#9CA3AF', width: 1.5, dashArray: [] },
    'PARENT_OF': { color: '#9CA3AF', width: 1.5, dashArray: [] },
    'CHILD_OF': { color: '#9CA3AF', width: 1.5, dashArray: [] },
    'RELATED_TO': { color: '#9CA3AF', width: 1.5, dashArray: [] },
    'ASSOCIATED_WITH': { color: '#9CA3AF', width: 1.5, dashArray: [] },

    // Default style - Cool Gray
    'DEFAULT': { color: '#9CA3AF', width: 1.5, dashArray: [] },
  };

  // Function to get relationship style
  const getRelationshipStyle = (relationshipType) => {
    return relationshipStyles[relationshipType] || relationshipStyles['DEFAULT'];
  };

  // Handlers for adding nodes and relationships (with backend API integration)
  const handleAddNode = async (nodeData) => {
    if (!kgName) {
      setSnackbar({
        open: true,
        message: 'No knowledge graph selected',
        severity: 'error'
      });
      return;
    }

    setLoading(true);
    try {
      // Prepare entity data for backend API
      const entityData = {
        name: nodeData.name,
        labels: nodeData.labels,
        properties: nodeData.properties,
        source_table: nodeData.source_table,
        source_column: nodeData.source_column,
      };

      // Call backend API to create entity
      const response = await createEntity(kgName, entityData);

      if (response.data.success) {
        setSnackbar({
          open: true,
          message: `Node "${nodeData.name}" added successfully!`,
          severity: 'success'
        });

        // Refresh graph data from backend
        if (onRefresh) {
          await onRefresh();
        }
      }
    } catch (error) {
      console.error('Error creating entity:', error);
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Failed to create node',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAddRelationship = async (relationshipData) => {
    if (!kgName) {
      setSnackbar({
        open: true,
        message: 'No knowledge graph selected',
        severity: 'error'
      });
      return;
    }

    setLoading(true);
    try {
      // Prepare relationship data for backend API
      const relData = {
        source_id: relationshipData.source_id,
        target_id: relationshipData.target_id,
        relationship_type: relationshipData.relationship_type,
        properties: relationshipData.properties,
        source_column: relationshipData.source_column,
        target_column: relationshipData.target_column,
      };

      // Call backend API to create relationship
      const response = await createRelationship(kgName, relData);

      if (response.data.success) {
        setSnackbar({
          open: true,
          message: 'Relationship created successfully!',
          severity: 'success'
        });

        // Refresh graph data from backend
        if (onRefresh) {
          await onRefresh();
        }
      }
    } catch (error) {
      console.error('Error creating relationship:', error);
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Failed to create relationship',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleOpenAddRelationshipDialog = (sourceNode) => {
    setRelationshipSourceNode(sourceNode);
    setCreateRelationshipDialogOpen(true);
  };

  const handleRefresh = async () => {
    if (onRefresh) {
      setLoading(true);
      try {
        await onRefresh();
        setSnackbar({
          open: true,
          message: 'Graph refreshed successfully!',
          severity: 'success'
        });
      } catch (error) {
        setSnackbar({
          open: true,
          message: 'Failed to refresh graph',
          severity: 'error'
        });
      } finally {
        setLoading(false);
      }
    }
  };

  const handleToggleLegend = () => {
    setShowLegend(!showLegend);
  };

  const handleToggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
        setIsFullscreen(false);
      }
    }
  };

  const handleExportGraph = () => {
    const exportData = {
      nodes: entities,
      relationships: relationships,
      metadata: {
        exported_at: new Date().toISOString(),
        total_nodes: entities.length,
        total_relationships: relationships.length,
      }
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `knowledge-graph-${kgName || 'export'}-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    setSnackbar({
      open: true,
      message: 'Graph exported successfully!',
      severity: 'success'
    });
  };

  // Convert entities and relationships to graph format
  useEffect(() => {
    // Use entities directly from backend
    const allEntities = entities;

    // First pass: create nodes with type-based colors from reference image
    const nodes = allEntities.map((entity) => {
      // Get primary label and all labels
      const primaryLabel = getPrimaryLabel(entity);
      const allLabels = getAllLabels(entity);

      // Color based on node type/label (Department, Employee, Project)
      const nodeColor = getNodeColorByRelationship(entity.id, relationships, primaryLabel, allLabels);

      // Prefer primary_alias from properties, then name, then label, then id
      const displayName = entity.properties?.primary_alias || entity.name || entity.label || entity.id;

      // Extract all properties (merge explicit properties with top-level properties)
      const nodeProperties = {
        ...(entity.properties || {}),
        // Include top-level properties that aren't structural
        ...(entity.type && { type: entity.type }),
      };

      // Calculate node size based on properties (if importance/degree/size property exists)
      const nodeSize = nodeProperties.importance || nodeProperties.degree || nodeProperties.size || 10;

      return {
        id: entity.id,
        name: displayName,
        labels: allLabels, // Array of labels (Neo4j style)
        primaryLabel: primaryLabel, // Primary label for display
        type: primaryLabel, // Backward compatibility
        properties: nodeProperties, // All node properties
        val: nodeSize, // Node size
        color: nodeColor,
        // Keep original entity data
        originalEntity: entity,
      };
    });

    // Create a map of entity IDs for flexible matching
    const entityIdMap = new Map();
    entities.forEach((e) => {
      entityIdMap.set(e.id, e);

      // Also map shortened IDs (e.g., "table_hana_material_master" -> "hana_material_master")
      if (e.id.startsWith('table_') && e.id.includes('_')) {
        const shortId = e.id.substring(6); // Remove "table_" prefix
        entityIdMap.set(shortId, e);
      }

      // Also map with "table_" prefix added (e.g., "hana_material_master" -> "table_hana_material_master")
      if (!e.id.startsWith('table_')) {
        const prefixedId = `table_${e.id}`;
        entityIdMap.set(prefixedId, e);
      }
    });

    // Use relationships directly from backend
    const allRelationships = relationships;

    // Filter relationships to only include those with valid source and target nodes
    const validRelationships = allRelationships.filter((rel) => {
      // Support both old format (source_id/target_id) and standardized format (source_table/target_table)
      const sourceId = rel.source_id || rel.source_table;
      const targetId = rel.target_id || rel.target_table;

      const sourceExists = entityIdMap.has(sourceId);
      const targetExists = entityIdMap.has(targetId);
      const isValid = sourceExists && targetExists;
      if (!isValid) {
        console.warn(
          `Skipping relationship: ${sourceId} -> ${targetId} (source: ${sourceExists}, target: ${targetExists})`
        );
        console.warn('Available entity IDs:', Array.from(entityIdMap.keys()));
      }
      return isValid;
    });

    // Create single-directional links (one link per relationship, source → target only)
    // Even if the underlying data has bidirectional: true, we display only one arrow
    const linkMap = new Map();

    validRelationships.forEach((rel) => {
      const sourceEntity = entityIdMap.get(rel.source_id || rel.source_table);
      const targetEntity = entityIdMap.get(rel.target_id || rel.target_table);
      const sourceId = sourceEntity?.id || rel.source_id || rel.source_table;
      const targetId = targetEntity?.id || rel.target_id || rel.target_table;

      // Get relationship type (support both relationship_type and type)
      const relType = rel.relationship_type || rel.type || 'RELATED_TO';

      // Extract relationship properties - support standardized format
      // Standardized format has fields at top level: confidence, bidirectional, _comment
      const relProperties = {
        ...(rel.properties || {}),
        // Include standardized fields if they exist at top level
        ...(rel.confidence !== undefined && { confidence: rel.confidence }),
        ...(rel.bidirectional !== undefined && { bidirectional: rel.bidirectional }),
        ...(rel._comment !== undefined && { _comment: rel._comment }),
        ...(rel.source_column !== undefined && { source_column: rel.source_column }),
        ...(rel.target_column !== undefined && { target_column: rel.target_column }),
        ...(rel.source_table !== undefined && { source_table: rel.source_table }),
        ...(rel.target_table !== undefined && { target_table: rel.target_table }),
      };

      // Create a unique key for this relationship (directional: source → target)
      // This ensures we only create one link per unique source-target pair
      const linkKey = `${sourceId}→${targetId}`;

      // Only add if we haven't seen this exact direction before
      if (!linkMap.has(linkKey)) {
        linkMap.set(linkKey, {
          source: sourceId,
          target: targetId,
          type: relType,
          properties: relProperties,
          originalRel: rel,
        });
      }
    });

    const links = Array.from(linkMap.values()).map((link) => ({
      source: link.source,
      target: link.target,
      type: link.type,
      properties: link.properties,
      originalRel: link.originalRel,
    }));

    console.log(`Graph data: ${nodes.length} nodes, ${links.length} single-directional links`);
    setGraphData({ nodes, links });
  }, [entities, relationships]);

  const handleNodeClick = (node) => {
    setSelectedNode(node);

    // Open the node details panel
    setPanelNode(node);
    setPanelOpen(true);

    onNodeClick?.(node);
  };

  const handleLinkClick = (link) => {
    onLinkClick?.(link);
  };

  // Panel handlers
  const handlePanelClose = () => {
    setPanelOpen(false);
    setPanelNode(null);
  };

  // Calculate graph width based on panel state and window size
  useEffect(() => {
    const calculateWidth = () => {
      const baseWidth = window.innerWidth * 0.95;
      if (panelOpen) {
        // Subtract panel width on desktop/tablet, keep full on mobile
        const panelWidth = window.innerWidth >= 600 ? PANEL_WIDTH : 0;
        setGraphWidth(baseWidth - panelWidth);
      } else {
        setGraphWidth(baseWidth);
      }
    };

    calculateWidth();
    window.addEventListener('resize', calculateWidth);
    return () => window.removeEventListener('resize', calculateWidth);
  }, [panelOpen]);



  // Configure force simulation to match reference image layout
  useEffect(() => {
    if (fgRef.current) {
      // Import d3-force for collision
      const d3 = require('d3-force');

      // Configure charge force for organic, spread-out layout like reference
      const chargeForce = fgRef.current.d3Force('charge');
      if (chargeForce) {
        chargeForce
          .strength(-800) // Stronger repulsion to prevent overlap
          .distanceMin(80) // Increased minimum distance
          .distanceMax(500);
      }

      // Configure link force with varied distances for organic layout
      const linkForce = fgRef.current.d3Force('link');
      if (linkForce) {
        linkForce
          .distance((link) => {
            // Varied distances create more organic layout
            if (link.type === "SEMANTIC_REFERENCE" || link.type === "SEMANTIC_REFERENCED_BY") {
              return 200; // Increased distance
            }
            if (link.type === "MATCHES") {
              return 160; // Increased distance
            }
            return 180; // Increased distance
          })
          .strength(0.6); // Slightly stronger for better spacing
      }

      // Add/configure collision force to prevent node overlap
      // Force add it if it doesn't exist
      fgRef.current.d3Force('collide', d3.forceCollide()
        .radius(45) // Node radius (30px) + padding (15px)
        .strength(1.0) // Maximum collision strength
        .iterations(3) // More iterations for better collision detection
      );

      // Weak centering force for natural spread
      const centerForce = fgRef.current.d3Force('center');
      if (centerForce) {
        centerForce.strength(0.15);
      }

      // Reheat the simulation to apply new forces
      fgRef.current.d3ReheatSimulation();
    }
  }, [graphData]);

  return (
    <Box
      sx={{
        width: '100%',
        display: 'flex',
        gap: 0,
        height: 'calc(100vh - 250px)',
      }}
    >
      {/* Left Column: Graph Visualization */}
      <Box
        sx={{
          flex: panelOpen ? { xs: '0 0 100%', sm: '1 1 auto' } : '1 1 auto',
          transition: 'flex 225ms cubic-bezier(0.4, 0, 0.6, 1)',
          minWidth: 0,
          display: panelOpen ? { xs: 'none', sm: 'block' } : 'block',
        }}
      >
        <Paper
          elevation={0}
          sx={{
            height: '100%',
            borderRadius: 1.5,
            overflow: 'hidden',
            position: 'relative',
            border: '2px solid',
            borderColor: 'divider',
            bgcolor: '#F5F6F6',
            boxShadow: 'none',
          }}
        >
          {graphData.nodes.length > 0 ? (
            <>
              {/* Enhanced Zoom Controls */}
              <Box
                sx={{
                  position: 'absolute',
                  bottom: 24,
                  right: 24,
                  zIndex: 10,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 0.5,
                  bgcolor: 'white',
                  borderRadius: 2,
                  p: 0.75,
                  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                  border: '1px solid #E5E7EB',
                }}
              >
                <Tooltip title="Zoom In" placement="left">
                  <IconButton
                    size="small"
                    onClick={() => fgRef.current?.zoom(fgRef.current.zoom() * 1.2, 400)}
                    sx={{
                      width: 36,
                      height: 36,
                      color: '#6B7280',
                      '&:hover': {
                        bgcolor: '#F9FAFB',
                        color: '#5B6FE5',
                      },
                    }}
                  >
                    <ZoomIn sx={{ fontSize: 20 }} />
                  </IconButton>
                </Tooltip>

                <Box sx={{ width: '100%', height: 1, bgcolor: '#E5E7EB', my: 0.25 }} />

                <Tooltip title="Zoom Out" placement="left">
                  <IconButton
                    size="small"
                    onClick={() => fgRef.current?.zoom(fgRef.current.zoom() / 1.2, 400)}
                    sx={{
                      width: 36,
                      height: 36,
                      color: '#6B7280',
                      '&:hover': {
                        bgcolor: '#F9FAFB',
                        color: '#5B6FE5',
                      },
                    }}
                  >
                    <ZoomOut sx={{ fontSize: 20 }} />
                  </IconButton>
                </Tooltip>

                <Box sx={{ width: '100%', height: 1, bgcolor: '#E5E7EB', my: 0.25 }} />

                <Tooltip title="Fit to View" placement="left">
                  <IconButton
                    size="small"
                    onClick={() => fgRef.current?.zoomToFit(400)}
                    sx={{
                      width: 36,
                      height: 36,
                      color: '#6B7280',
                      '&:hover': {
                        bgcolor: '#F9FAFB',
                        color: '#5B6FE5',
                      },
                    }}
                  >
                    <CenterFocusStrong sx={{ fontSize: 20 }} />
                  </IconButton>
                </Tooltip>
              </Box>

              {/* Enhanced Toolbar with Better Layout and Styling */}
              <Box
                sx={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 16,
                  zIndex: 10,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  pointerEvents: 'none', // Allow clicks through the container
                }}
              >
                {/* Left Section: Stats and Primary Actions */}
                <Box
                  sx={{
                    display: 'flex',
                    gap: 1,
                    alignItems: 'center',
                    bgcolor: 'white',
                    borderRadius: 2,
                    p: 0.25,
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                    border: '1px solid #E5E7EB',
                    pointerEvents: 'auto',
                  }}
                >
                  {/* Stats Group - De-emphasized for better visual hierarchy */}
                  <Box sx={{ display: 'flex', gap: 0.75, alignItems: 'center' }}>
                    <Chip
                      label={`${graphData.nodes.length} Nodes`}
                      size="small"
                      sx={{
                        bgcolor: 'transparent',
                        color: '#6B7280',
                        fontWeight: 500,
                        fontSize: '0.75rem',
                        height: 32,
                        border: 'none',
                        '& .MuiChip-label': {
                          px: 1,
                        },
                      }}
                    />
                    <Chip
                      label={`${graphData.links.length} Links`}
                      size="small"
                      sx={{
                        bgcolor: 'transparent',
                        color: '#6B7280',
                        fontWeight: 500,
                        fontSize: '0.75rem',
                        height: 32,
                        border: 'none',
                        '& .MuiChip-label': {
                          px: 1,
                        },
                      }}
                    />
                  </Box>

                  {/* Divider */}
                  <Box sx={{ width: 1, height: 24, bgcolor: '#E5E7EB' }} />

                  {/* Primary Actions Group - Hidden as per requirement */}
                  {/* <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center' }}>
                  <Tooltip title="Add a new node to the graph" placement="bottom">
                    <span>
                      <IconButton
                        size="small"
                        onClick={() => setAddNodeDialogOpen(true)}
                        disabled={loading || !kgName}
                        sx={{
                          width: 32,
                          height: 32,
                          color: '#6B7280',
                          '&:hover': {
                            bgcolor: '#F9FAFB',
                            color: '#5B6FE5',
                          },
                          '&:disabled': {
                            color: '#9CA3AF',
                          },
                        }}
                      >
                        <AddIcon sx={{ fontSize: 18 }} />
                      </IconButton>
                    </span>
                  </Tooltip>

                  <Tooltip
                    title={
                      !kgName
                        ? "Select a knowledge graph first"
                        : entities.length < 2
                          ? "Need at least 2 nodes to create a link"
                          : "Create a relationship between nodes"
                    }
                    placement="bottom"
                  >
                    <span>
                      <IconButton
                        size="small"
                        onClick={() => setCreateRelationshipDialogOpen(true)}
                        disabled={loading || !kgName || entities.length < 2}
                        sx={{
                          width: 32,
                          height: 32,
                          color: '#6B7280',
                          '&:hover': {
                            bgcolor: '#F9FAFB',
                            color: '#5B6FE5',
                          },
                          '&:disabled': {
                            color: '#9CA3AF',
                          },
                        }}
                      >
                        <AddLinkIcon sx={{ fontSize: 18 }} />
                      </IconButton>
                    </span>
                  </Tooltip>
                </Box> */}

                  {/* Divider - Hidden since Primary Actions are hidden */}
                  {/* <Box sx={{ width: 1, height: 24, bgcolor: '#E5E7EB' }} /> */}

                  {/* Secondary Actions Group */}
                  <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center' }}>
                    <Tooltip title="Refresh graph data" placement="bottom">
                      <span>
                        <IconButton
                          size="small"
                          onClick={handleRefresh}
                          disabled={loading || !kgName}
                          sx={{
                            width: 32,
                            height: 32,
                            color: '#6B7280',
                            '&:hover': {
                              bgcolor: '#F9FAFB',
                              color: '#5B6FE5',
                            },
                            '&:disabled': {
                              color: '#9CA3AF',
                            },
                          }}
                        >
                          <RefreshIcon sx={{ fontSize: 18 }} />
                        </IconButton>
                      </span>
                    </Tooltip>

                    <Tooltip title="Show color legend" placement="bottom">
                      <IconButton
                        size="small"
                        onClick={handleToggleLegend}
                        sx={{
                          width: 32,
                          height: 32,
                          color: showLegend ? '#5B6FE5' : '#6B7280',
                          bgcolor: showLegend ? '#EEF2FF' : 'transparent',
                          '&:hover': {
                            bgcolor: '#F9FAFB',
                            color: '#5B6FE5',
                          },
                        }}
                      >
                        <PaletteIcon sx={{ fontSize: 18 }} />
                      </IconButton>
                    </Tooltip>

                    <Tooltip title="Export graph as JSON" placement="bottom">
                      <span>
                        <IconButton
                          size="small"
                          onClick={handleExportGraph}
                          disabled={loading || entities.length === 0}
                          sx={{
                            width: 32,
                            height: 32,
                            color: '#6B7280',
                            '&:hover': {
                              bgcolor: '#F9FAFB',
                              color: '#5B6FE5',
                            },
                            '&:disabled': {
                              color: '#9CA3AF',
                            },
                          }}
                        >
                          <DownloadIcon sx={{ fontSize: 18 }} />
                        </IconButton>
                      </span>
                    </Tooltip>

                    <Tooltip title={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"} placement="bottom">
                      <IconButton
                        size="small"
                        onClick={handleToggleFullscreen}
                        sx={{
                          width: 32,
                          height: 32,
                          color: '#6B7280',
                          '&:hover': {
                            bgcolor: '#F9FAFB',
                            color: '#5B6FE5',
                          },
                        }}
                      >
                        {isFullscreen ? (
                          <FullscreenExitIcon sx={{ fontSize: 18 }} />
                        ) : (
                          <FullscreenIcon sx={{ fontSize: 18 }} />
                        )}
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>

                {/* Right Section: Loading Indicator */}
                {loading && (
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1,
                      bgcolor: 'white',
                      borderRadius: 2,
                      p: 1,
                      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                      border: '1px solid #E5E7EB',
                      pointerEvents: 'auto',
                    }}
                  >
                    <CircularProgress size={16} sx={{ color: '#5B6FE5' }} />
                    <Typography variant="caption" sx={{ color: '#6B7280', fontWeight: 600, fontSize: '0.75rem' }}>
                      Loading...
                    </Typography>
                  </Box>
                )}
              </Box>

              {/* Legend Overlay */}
              {showLegend && graphData.nodes.length > 0 && (
                <Box
                  sx={{
                    position: 'absolute',
                    top: 80,
                    left: 16,
                    zIndex: 10,
                    bgcolor: 'white',
                    borderRadius: 2,
                    p: 2,
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                    border: '1px solid #E5E7EB',
                    maxWidth: 250,
                    maxHeight: 400,
                    overflow: 'auto',
                  }}
                >
                  {/* Legend Header with Close Button */}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#1F2937', fontSize: '0.875rem' }}>
                      Node Types
                    </Typography>
                    <Tooltip title="Close legend" placement="left">
                      <IconButton
                        size="small"
                        onClick={handleToggleLegend}
                        sx={{
                          width: 24,
                          height: 24,
                          color: '#6B7280',
                          '&:hover': {
                            bgcolor: '#F9FAFB',
                            color: '#5B6FE5',
                          },
                        }}
                      >
                        <CloseIcon sx={{ fontSize: 16 }} />
                      </IconButton>
                    </Tooltip>
                  </Box>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {Array.from(new Set(graphData.nodes.map(n => n.primaryLabel || n.type || 'Unknown')))
                      .sort()
                      .map((label) => {
                        const color = getColorForLabel(label);
                        const count = graphData.nodes.filter(n => (n.primaryLabel || n.type) === label).length;
                        return (
                          <Box
                            key={label}
                            sx={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: 1,
                              p: 0.75,
                              borderRadius: 1,
                              '&:hover': {
                                bgcolor: '#F9FAFB',
                              },
                            }}
                          >
                            <Box
                              sx={{
                                width: 16,
                                height: 16,
                                borderRadius: '50%',
                                bgcolor: color,
                                flexShrink: 0,
                                border: '2px solid white',
                                boxShadow: '0 0 0 1px rgba(0,0,0,0.1)',
                              }}
                            />
                            <Typography variant="caption" sx={{ flex: 1, color: '#1F2937', fontSize: '0.75rem', fontWeight: 500 }}>
                              {label}
                            </Typography>
                            <Chip
                              label={count}
                              size="small"
                              sx={{
                                height: 20,
                                fontSize: '0.7rem',
                                bgcolor: '#F9FAFB',
                                color: '#6B7280',
                                fontWeight: 600,
                                '& .MuiChip-label': {
                                  px: 0.75,
                                },
                              }}
                            />
                          </Box>
                        );
                      })}
                  </Box>
                </Box>
              )}

              <ForceGraph2D
                ref={fgRef}
                graphData={graphData}
                onNodeClick={handleNodeClick}
                onLinkClick={handleLinkClick}

                /* === Physics tuned for organic layout like reference === */
                d3AlphaDecay={0.015} // Slightly faster settling
                d3VelocityDecay={0.3} // More damping for stable layout
                warmupTicks={150}
                cooldownTicks={200}
                nodeRelSize={8} // Increased for better node sizing

                width={graphWidth}
                height={window.innerHeight * 0.85}

                /* STRAIGHT links with arrows - with dynamic styling based on relationship type */
                linkCurvature={0} // NO CURVE - straight lines like reference
                linkColor={(link) => {
                  const style = getRelationshipStyle(link.type);
                  return style.color;
                }}
                linkWidth={(link) => {
                  const style = getRelationshipStyle(link.type);
                  return style.width;
                }}
                linkDirectionalArrowLength={0} // Disable built-in arrows - using custom canvas arrows only
                linkLineDash={(link) => {
                  const style = getRelationshipStyle(link.type);
                  return style.dashArray;
                }}

                /* Link labels with unidirectional arrows - styled to match reference image */
                linkCanvasObjectMode={() => "after"}
                linkCanvasObject={(link, ctx, scale) => {
                  const start = link.source;
                  const end = link.target;
                  if (!start || !end) return;

                  const relStyle = getRelationshipStyle(link.type);

                  const dx = end.x - start.x;
                  const dy = end.y - start.y;
                  const angle = Math.atan2(dy, dx);
                  const distance = Math.sqrt(dx * dx + dy * dy);

                  const arrowLength = 8;
                  const arrowWidth = 4;
                  const nodeRadius = 30;

                  const arrowPos = distance - nodeRadius - 6;
                  const arrowX = start.x + Math.cos(angle) * arrowPos;
                  const arrowY = start.y + Math.sin(angle) * arrowPos;

                  /* === CLEANLY ALIGNED ARROW === */
                  ctx.save();
                  ctx.translate(arrowX, arrowY);
                  ctx.rotate(angle);
                  ctx.beginPath();
                  ctx.moveTo(arrowLength, 0);
                  ctx.lineTo(0, arrowWidth);
                  ctx.lineTo(0, -arrowWidth);
                  ctx.closePath();
                  ctx.fillStyle = relStyle.color;
                  ctx.fill();
                  ctx.restore();

                  const label = link.type || "";
                  if (!label) return;

                  /* === PERFECT LABEL ALIGNMENT WITH OFFSET === */
                  const mx = (start.x + end.x) / 2;
                  const my = (start.y + end.y) / 2;

                  // Perpendicular offset so text NEVER overlaps the line
                  // ✅ Pull label CLOSER to the link (reduce visual gap)
                  const OFFSET = 6; // smaller = closer to the link
                  const offsetX = Math.sin(angle) * OFFSET;
                  const offsetY = -Math.cos(angle) * OFFSET;

                  const labelX = mx + offsetX;
                  const labelY = my + offsetY;

                  let textAngle = angle;
                  if (textAngle > Math.PI / 2) textAngle -= Math.PI;
                  if (textAngle < -Math.PI / 2) textAngle += Math.PI;

                  const fontSize = 9 / scale;
                  ctx.font = `${fontSize}px Arial`;

                  ctx.save();
                  ctx.translate(labelX, labelY);
                  ctx.rotate(textAngle);

                  ctx.fillStyle = "#6B7280";
                  ctx.textAlign = "center";
                  ctx.textBaseline = "middle";
                  ctx.fillText(label, 0, 0);

                  ctx.restore();
                }}


                /* Node bubbles - styled with matching border colors and black text */
                nodeCanvasObject={(node, ctx, scale) => {
                  const R = 30; // Node radius
                  const isSelected = selectedNode && selectedNode.id === node.id;
                  const nodeColor = node.color || "#5B6FE5"; // Get node color
                  const selectionGap = 5; // Gap between node and selection border (in pixels)

                  // Draw selection highlight border FIRST (as outer ring) if node is selected
                  // This creates a "halo" effect with visible spacing from the node
                  if (isSelected) {
                    ctx.beginPath();
                    ctx.arc(node.x, node.y, R + selectionGap, 0, 2 * Math.PI);
                    ctx.strokeStyle = SELECTION_BORDER_COLOR; // Bright cyan for selection
                    ctx.lineWidth = 2; // Thinner border for selection
                    ctx.stroke();
                  }

                  // Draw node circle with color based on relationships or primary label
                  ctx.beginPath();
                  ctx.arc(node.x, node.y, R, 0, 2 * Math.PI);
                  ctx.fillStyle = nodeColor;
                  ctx.fill();

                  // Add border that matches the node color
                  ctx.strokeStyle = nodeColor; // Border matches node background color
                  ctx.lineWidth = 2;
                  ctx.stroke();

                  // Draw main label inside the circle
                  // Black text for readability on lighter node colors
                  const label = (node.name || "").replace(/_/g, " ");
                  const fontSize = 10 / scale;
                  ctx.font = `${fontSize}px Arial`;
                  ctx.fillStyle = "#1F2937"; // Design system text primary (dark) for readability
                  ctx.textAlign = "center";
                  ctx.textBaseline = "middle";

                  // Word wrap for long labels
                  const maxWidth = R * 1.6;
                  const words = label.split(" ");
                  const lines = [];
                  let line = "";

                  words.forEach(word => {
                    const test = line ? line + " " + word : word;
                    if (ctx.measureText(test).width < maxWidth) {
                      line = test;
                    } else {
                      if (line) lines.push(line);
                      line = word;
                    }
                  });
                  if (line) lines.push(line);

                  // Draw text lines centered in the circle
                  const lineHeight = fontSize * 1.2;
                  const totalHeight = lines.length * lineHeight;
                  let y = node.y - totalHeight / 2 + lineHeight / 2;

                  lines.forEach(l => {
                    ctx.fillText(l, node.x, y);
                    y += lineHeight;
                  });

                  // Draw multiple labels as badges below the node (if more than one label)
                  if (node.labels && node.labels.length > 1) {
                    const labelFontSize = 6 / scale;
                    ctx.font = `${labelFontSize}px Arial`;

                    // Join labels with separator
                    const labelsText = node.labels.join(' • ');
                    const labelsWidth = ctx.measureText(labelsText).width;
                    const labelsPadding = 4 / scale;
                    const labelsHeight = labelFontSize + labelsPadding * 2;

                    // Position below the node
                    const badgeY = node.y + R + 8 / scale;

                    // Draw background badge with design system colors
                    ctx.fillStyle = "rgba(255, 255, 255, 0.95)";
                    ctx.strokeStyle = node.color || "#5B6FE5"; // Design system primary color
                    ctx.lineWidth = 1 / scale;

                    const badgeRadius = 3 / scale;
                    const badgeX = node.x - labelsWidth / 2 - labelsPadding;
                    const badgeWidth = labelsWidth + labelsPadding * 2;

                    // Rounded rectangle for badge
                    ctx.beginPath();
                    ctx.moveTo(badgeX + badgeRadius, badgeY);
                    ctx.lineTo(badgeX + badgeWidth - badgeRadius, badgeY);
                    ctx.quadraticCurveTo(badgeX + badgeWidth, badgeY, badgeX + badgeWidth, badgeY + badgeRadius);
                    ctx.lineTo(badgeX + badgeWidth, badgeY + labelsHeight - badgeRadius);
                    ctx.quadraticCurveTo(badgeX + badgeWidth, badgeY + labelsHeight, badgeX + badgeWidth - badgeRadius, badgeY + labelsHeight);
                    ctx.lineTo(badgeX + badgeRadius, badgeY + labelsHeight);
                    ctx.quadraticCurveTo(badgeX, badgeY + labelsHeight, badgeX, badgeY + labelsHeight - badgeRadius);
                    ctx.lineTo(badgeX, badgeY + badgeRadius);
                    ctx.quadraticCurveTo(badgeX, badgeY, badgeX + badgeRadius, badgeY);
                    ctx.closePath();
                    ctx.fill();
                    ctx.stroke();

                    // Draw labels text with node color for consistency
                    ctx.fillStyle = node.color || "#5B6FE5"; // Design system primary color
                    ctx.textAlign = "center";
                    ctx.textBaseline = "middle";
                    ctx.fillText(labelsText, node.x, badgeY + labelsHeight / 2);
                  }
                }}

                nodePointerAreaPaint={(node, color, ctx) => {
                  const R = 42; // Match the node radius + small buffer
                  ctx.beginPath();
                  ctx.arc(node.x, node.y, R, 0, 2 * Math.PI);
                  ctx.fillStyle = color;
                  ctx.fill();
                }}
              />
            </>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: 1 }}>
              <Box
                sx={{
                  p: 1.5,
                  borderRadius: '50%',
                  bgcolor: 'action.hover',
                }}
              >
                <Typography variant="h2" sx={{ opacity: 0.3, fontSize: '2.5rem' }}>📊</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" fontWeight={600} fontSize="0.85rem">
                No nodes to visualize
              </Typography>
              <Typography variant="caption" color="text.secondary" fontSize="0.75rem">
                Generate a knowledge graph to see the visualization
              </Typography>
            </Box>
          )}
        </Paper>
      </Box>

      {/* Right Column: Node Details Panel */}
      {panelOpen && (
        <Box
          sx={{
            width: { xs: '100%', sm: '400px' },
            flexShrink: 0,
            height: '100%',
            display: { xs: 'block', sm: 'block' },
          }}
        >
          <NodeDetailsDialog
            open={panelOpen}
            node={panelNode}
            allNodes={graphData.nodes}
            relationships={graphData.links}
            relationshipStyles={relationshipStyles}
            onClose={handlePanelClose}
            onAddRelationship={handleOpenAddRelationshipDialog}
          />
        </Box>
      )}

      {/* Add Node Dialog */}
      <AddNodeDialog
        open={addNodeDialogOpen}
        onClose={() => setAddNodeDialogOpen(false)}
        existingEntities={entities}
        onAddNode={handleAddNode}
        kgName={kgName}
        onRefresh={onRefresh}
      />

      {/* Create Relationship Dialog */}
      <CreateRelationshipDialog
        open={createRelationshipDialogOpen}
        onClose={() => {
          setCreateRelationshipDialogOpen(false);
          setRelationshipSourceNode(null);
        }}
        allNodes={entities}
        sourceNode={relationshipSourceNode}
        onCreateRelationship={handleAddRelationship}
        kgName={kgName}
        onRefresh={onRefresh}
        existingRelationships={relationships}
      />

      {/* Success/Error Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

