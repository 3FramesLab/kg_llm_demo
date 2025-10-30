import { useEffect, useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { Box, Paper, Typography, Button, IconButton, Chip, Tooltip, Zoom, Dialog, DialogTitle, DialogContent, DialogActions, TextField } from '@mui/material';
import { Close, Edit, Delete, ZoomIn, ZoomOut, CenterFocusStrong } from '@mui/icons-material';

/**
 * KnowledgeGraphEditor Component
 * Renders a force-directed graph visualization with clustering support
 *
 * Props:
 * - entities: Array of entity objects with id, label, type
 * - relationships: Array of relationship objects with source_id, target_id, relationship_type
 * - onNodeClick: Callback when a node is clicked
 * - onLinkClick: Callback when a link is clicked
 * - onDeleteEntity: Callback to delete an entity
 * - onDeleteRelationship: Callback to delete a relationship
 */
export default function KnowledgeGraphEditor({
  entities = [],
  relationships = [],
  onNodeClick,
  onLinkClick,
  onDeleteEntity,
  onDeleteRelationship,
}) {
  const fgRef = useRef();
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedLink, setSelectedLink] = useState(null);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editFormData, setEditFormData] = useState({ label: '', type: '' });

  // Color palette for unique entity colors
  const colorPalette = [
    '#667eea', // Blue
    '#764ba2', // Purple
    '#f093fb', // Pink
    '#4facfe', // Light Blue
    '#43e97b', // Green
    '#fa709a', // Red
    '#30cfd0', // Cyan
    '#a8edea', // Light Cyan
    '#fed6e3', // Light Pink
    '#ffa502', // Orange
    '#ff6b6b', // Coral
    '#845ef7', // Violet
    '#748ffc', // Indigo
    '#15aabf', // Teal
    '#20c997', // Mint
  ];

  // Function to generate a consistent color for an entity based on its ID
  const getEntityColor = (entityId) => {
    let hash = 0;
    for (let i = 0; i < entityId.length; i++) {
      const char = entityId.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    const index = Math.abs(hash) % colorPalette.length;
    return colorPalette[index];
  };

  // Convert entities and relationships to graph format
  useEffect(() => {
    const nodes = entities.map((entity) => {
      // Handle both direct type and nested properties.type
      const entityType = entity.type || entity.properties?.type || 'Unknown';
      // Use unique color based on entity ID, with fallback to index-based color
      const uniqueColor = getEntityColor(entity.id);
      return {
        id: entity.id,
        name: entity.label || entity.id,
        type: entityType,
        val: 8,
        color: uniqueColor,
        ...entity,
      };
    });

    // Create a map of entity IDs for flexible matching
    const entityIdMap = new Map();
    entities.forEach((e) => {
      entityIdMap.set(e.id, e);
      // Also map shortened IDs (e.g., "hana_material_master" -> "table_hana_material_master")
      if (e.id.includes('_')) {
        const shortId = e.id.split('_').slice(1).join('_');
        entityIdMap.set(shortId, e);
      }
    });

    // Filter relationships to only include those with valid source and target nodes
    const validRelationships = relationships.filter((rel) => {
      const sourceExists = entityIdMap.has(rel.source_id);
      const targetExists = entityIdMap.has(rel.target_id);
      const isValid = sourceExists && targetExists;
      if (!isValid) {
        console.warn(
          `Skipping relationship: ${rel.source_id} -> ${rel.target_id} (source: ${sourceExists}, target: ${targetExists})`
        );
      }
      return isValid;
    });

    const links = validRelationships.map((rel) => {
      // Map shortened IDs to full entity IDs
      const sourceEntity = entityIdMap.get(rel.source_id);
      const targetEntity = entityIdMap.get(rel.target_id);
      return {
        source: sourceEntity?.id || rel.source_id,
        target: targetEntity?.id || rel.target_id,
        type: rel.relationship_type,
        ...rel,
      };
    });

    console.log(`Graph data: ${nodes.length} nodes, ${links.length} links`);
    setGraphData({ nodes, links });
  }, [entities, relationships]);

  const handleNodeClick = (node) => {
    setSelectedNode(node);
    setSelectedLink(null);
    onNodeClick?.(node);
  };

  const handleLinkClick = (link) => {
    setSelectedLink(link);
    setSelectedNode(null);
    onLinkClick?.(link);
  };

  const handleNodeHover = (node) => {
    if (fgRef.current) {
      fgRef.current.d3Force('charge').strength(node ? -30 : -5);
    }
  };

  const handleEditClick = () => {
    if (selectedNode) {
      setEditFormData({
        label: selectedNode.name || '',
        type: selectedNode.type || '',
      });
      setEditDialogOpen(true);
    }
  };

  const handleEditSave = () => {
    if (selectedNode) {
      // Update the selected node with new values
      const updatedNode = {
        ...selectedNode,
        name: editFormData.label,
        label: editFormData.label,
        type: editFormData.type,
      };
      setSelectedNode(updatedNode);
      setEditDialogOpen(false);
    }
  };

  const handleEditCancel = () => {
    setEditDialogOpen(false);
    setEditFormData({ label: '', type: '' });
  };

  return (
    <Box sx={{ display: 'flex', gap: 2, width: '100%', flexDirection: { xs: 'column', lg: 'row' } }}>
      {/* Graph Visualization */}
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Paper
          elevation={0}
          sx={{
            height: 480,
            borderRadius: 1.5,
            overflow: 'hidden',
            position: 'relative',
            border: '2px solid',
            borderColor: 'divider',
            bgcolor: '#fafafa',
            boxShadow: 'inset 0 1px 6px rgba(0,0,0,0.05)',
          }}
        >
          {graphData.nodes.length > 0 ? (
            <>
              {/* Zoom Controls */}
              <Box
                sx={{
                  position: 'absolute',
                  top: 10,
                  right: 10,
                  zIndex: 10,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 0.5,
                }}
              >
                <Tooltip title="Zoom In" placement="left">
                  <IconButton
                    size="small"
                    onClick={() => fgRef.current?.zoom(fgRef.current.zoom() * 1.2, 400)}
                    sx={{
                      bgcolor: 'white',
                      boxShadow: 1,
                      width: 32,
                      height: 32,
                      '&:hover': {
                        bgcolor: 'grey.100',
                      },
                    }}
                  >
                    <ZoomIn sx={{ fontSize: 18 }} />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Zoom Out" placement="left">
                  <IconButton
                    size="small"
                    onClick={() => fgRef.current?.zoom(fgRef.current.zoom() / 1.2, 400)}
                    sx={{
                      bgcolor: 'white',
                      boxShadow: 1,
                      width: 32,
                      height: 32,
                      '&:hover': {
                        bgcolor: 'grey.100',
                      },
                    }}
                  >
                    <ZoomOut sx={{ fontSize: 18 }} />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Center View" placement="left">
                  <IconButton
                    size="small"
                    onClick={() => fgRef.current?.zoomToFit(400)}
                    sx={{
                      bgcolor: 'white',
                      boxShadow: 1,
                      width: 32,
                      height: 32,
                      '&:hover': {
                        bgcolor: 'grey.100',
                      },
                    }}
                  >
                    <CenterFocusStrong sx={{ fontSize: 18 }} />
                  </IconButton>
                </Tooltip>
              </Box>

              {/* Graph Stats Overlay */}
              <Box
                sx={{
                  position: 'absolute',
                  top: 12,
                  left: 12,
                  zIndex: 10,
                  display: 'flex',
                  gap: 0.75,
                }}
              >
                <Chip
                  label={`${graphData.nodes.length} Nodes`}
                  size="small"
                  sx={{
                    bgcolor: 'white',
                    fontWeight: 600,
                    fontSize: '0.7rem',
                    height: 24,
                    boxShadow: 1,
                  }}
                />
                <Chip
                  label={`${graphData.links.length} Links`}
                  size="small"
                  sx={{
                    bgcolor: 'white',
                    fontWeight: 600,
                    fontSize: '0.7rem',
                    height: 24,
                    boxShadow: 1,
                  }}
                />
              </Box>

              <ForceGraph2D
                ref={fgRef}
                graphData={graphData}
                nodeLabel={(node) => `${node.name} (${node.type})`}
                nodeColor={(node) => node.color}
                nodeVal={(node) => (selectedNode?.id === node.id ? 10 : 8)}
                linkColor={() => '#999'}
                linkWidth={(link) => (selectedLink === link ? 3 : 1)}
                linkLabel={(link) => link.type}
                onNodeClick={handleNodeClick}
                onNodeHover={handleNodeHover}
                onLinkClick={handleLinkClick}
                cooldownTicks={100}
                onEngineStop={() => fgRef.current?.zoomToFit(400)}
                width={typeof window !== 'undefined' ? window.innerWidth * 0.55 : 600}
                height={500}
                nodeCanvasObject={(node, ctx) => {
                  const label = node.name;
                  const fontSize = 1;
                  const nodeRadius = node.val || 8; // Fallback to 8 if val is undefined

                  ctx.font = `${fontSize}px Arial`;
                  const textWidth = ctx.measureText(label).width;
                  const bckgDimensions = [textWidth, fontSize].map((n) => n + fontSize * 0.05);

                  // Draw glow effect for selected node
                  if (selectedNode?.id === node.id && isFinite(nodeRadius) && isFinite(node.x) && isFinite(node.y)) {
                    try {
                      // Create gradient for glow effect
                      const gradient = ctx.createRadialGradient(node.x, node.y, nodeRadius, node.x, node.y, nodeRadius + 4);
                      gradient.addColorStop(0, 'rgba(255, 215, 0, 0.4)');
                      gradient.addColorStop(0.5, 'rgba(255, 215, 0, 0.2)');
                      gradient.addColorStop(1, 'rgba(255, 215, 0, 0)');

                      ctx.fillStyle = gradient;
                      ctx.beginPath();
                      ctx.arc(node.x, node.y, nodeRadius + 4, 0, 2 * Math.PI);
                      ctx.fill();

                      // Draw golden ring border
                      ctx.strokeStyle = 'rgba(255, 215, 0, 0.8)';
                      ctx.lineWidth = 2.5;
                      ctx.beginPath();
                      ctx.arc(node.x, node.y, nodeRadius + 0.5, 0, 2 * Math.PI);
                      ctx.stroke();
                    } catch (e) {
                      console.warn('Error drawing glow effect:', e);
                    }
                  }

                  // Draw main node circle
                  ctx.fillStyle = node.color;
                  ctx.beginPath();
                  ctx.arc(node.x, node.y, nodeRadius, 0, 2 * Math.PI);
                  ctx.fill();

                  // Draw text background
                  ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
                  ctx.fillRect(
                    node.x - bckgDimensions[0] / 2,
                    node.y - bckgDimensions[1] / 2,
                    ...bckgDimensions
                  );

                  // Draw text label
                  ctx.textAlign = 'center';
                  ctx.textBaseline = 'middle';
                  ctx.fillStyle = '#000';
                  ctx.fillText(label, node.x, node.y);
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

      {/* Details Panel */}
      <Box sx={{ width: { xs: '100%', lg: 300 }, flexShrink: 0 }}>
        <Paper
          elevation={0}
          sx={{
            borderRadius: 1.5,
            overflow: 'hidden',
            height: 480,
            display: 'flex',
            flexDirection: 'column',
            border: '2px solid',
            borderColor: 'divider',
          }}
        >
          {selectedNode ? (
            <Zoom in={!!selectedNode}>
              <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                <Box
                  sx={{
                    p: 1.5,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    flexShrink: 0,
                  }}
                >
                  <Typography variant="body2" fontWeight="700" fontSize="0.85rem">Entity Details</Typography>
                  <IconButton
                    size="small"
                    sx={{
                      color: 'white',
                      '&:hover': {
                        bgcolor: 'rgba(255, 255, 255, 0.2)',
                      },
                    }}
                    onClick={() => setSelectedNode(null)}
                  >
                    <Close />
                  </IconButton>
                </Box>
                <Box sx={{ flex: 1, overflowY: 'auto', p: 1.5 }}>
                  <Box sx={{ mb: 1.5 }}>
                    <Typography variant="caption" color="text.secondary" fontWeight={600} sx={{ textTransform: 'uppercase', letterSpacing: 0.5, fontSize: '0.65rem' }}>
                      ID
                    </Typography>
                    <Paper
                      elevation={0}
                      sx={{
                        p: 0.75,
                        mt: 0.5,
                        bgcolor: 'grey.100',
                        borderRadius: 0.75,
                        fontFamily: 'monospace',
                        fontSize: '0.75rem',
                        wordBreak: 'break-all',
                      }}
                    >
                      {selectedNode.id}
                    </Paper>
                  </Box>
                  <Box sx={{ mb: 1.5 }}>
                    <Typography variant="caption" color="text.secondary" fontWeight={600} sx={{ textTransform: 'uppercase', letterSpacing: 0.5, fontSize: '0.65rem' }}>
                      Label
                    </Typography>
                    <Typography variant="body2" fontWeight={700} sx={{ mt: 0.5, fontSize: '0.85rem' }}>
                      {selectedNode.name}
                    </Typography>
                  </Box>
                  <Box sx={{ mb: 1.5 }}>
                    <Typography variant="caption" color="text.secondary" fontWeight={600} sx={{ textTransform: 'uppercase', letterSpacing: 0.5, mb: 0.5, display: 'block', fontSize: '0.65rem' }}>
                      Type
                    </Typography>
                    <Chip
                      label={selectedNode.type}
                      size="small"
                      sx={{
                        bgcolor: selectedNode.color,
                        color: 'white',
                        fontWeight: 700,
                        fontSize: '0.75rem',
                        px: 0.5,
                        height: 24,
                      }}
                    />
                  </Box>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.75, mt: 2 }}>
                    <Button
                      variant="outlined"
                      startIcon={<Edit sx={{ fontSize: 16 }} />}
                      fullWidth
                      size="small"
                      onClick={handleEditClick}
                      sx={{
                        borderRadius: 1,
                        textTransform: 'none',
                        fontWeight: 600,
                        fontSize: '0.75rem',
                        py: 0.5,
                        borderWidth: 2,
                        '&:hover': {
                          borderWidth: 2,
                        },
                      }}
                    >
                      Edit Entity
                    </Button>
                    <Button
                      variant="outlined"
                      color="error"
                      startIcon={<Delete sx={{ fontSize: 16 }} />}
                      fullWidth
                      size="small"
                      onClick={() => {
                        onDeleteEntity?.(selectedNode.id);
                        setSelectedNode(null);
                      }}
                      sx={{
                        borderRadius: 1,
                        textTransform: 'none',
                        fontWeight: 600,
                        fontSize: '0.75rem',
                        py: 0.5,
                        borderWidth: 2,
                        '&:hover': {
                          borderWidth: 2,
                        },
                      }}
                    >
                      Delete Entity
                    </Button>
                  </Box>
                </Box>
              </Box>
            </Zoom>
          ) : selectedLink ? (
            <Zoom in={!!selectedLink}>
              <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                <Box
                  sx={{
                    p: 1.5,
                    background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
                    color: 'white',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    flexShrink: 0,
                  }}
                >
                  <Typography variant="body2" fontWeight="700" fontSize="0.85rem">Relationship Details</Typography>
                  <IconButton
                    size="small"
                    sx={{
                      color: 'white',
                      '&:hover': {
                        bgcolor: 'rgba(255, 255, 255, 0.2)',
                      },
                    }}
                    onClick={() => setSelectedLink(null)}
                  >
                    <Close />
                  </IconButton>
                </Box>
                <Box sx={{ flex: 1, overflowY: 'auto', p: 1.5 }}>
                  <Box sx={{ mb: 1.5 }}>
                    <Typography variant="caption" color="text.secondary" fontWeight={600} sx={{ textTransform: 'uppercase', letterSpacing: 0.5, fontSize: '0.65rem' }}>
                      Source
                    </Typography>
                    <Paper
                      elevation={0}
                      sx={{
                        p: 0.75,
                        mt: 0.5,
                        bgcolor: 'grey.100',
                        borderRadius: 0.75,
                        fontFamily: 'monospace',
                        fontSize: '0.75rem',
                        wordBreak: 'break-all',
                      }}
                    >
                      {selectedLink.source}
                    </Paper>
                  </Box>
                  <Box sx={{ mb: 1.5 }}>
                    <Typography variant="caption" color="text.secondary" fontWeight={600} sx={{ textTransform: 'uppercase', letterSpacing: 0.5, fontSize: '0.65rem' }}>
                      Target
                    </Typography>
                    <Paper
                      elevation={0}
                      sx={{
                        p: 0.75,
                        mt: 0.5,
                        bgcolor: 'grey.100',
                        borderRadius: 0.75,
                        fontFamily: 'monospace',
                        fontSize: '0.75rem',
                        wordBreak: 'break-all',
                      }}
                    >
                      {selectedLink.target}
                    </Paper>
                  </Box>
                  <Box sx={{ mb: 1.5 }}>
                    <Typography variant="caption" color="text.secondary" fontWeight={600} sx={{ textTransform: 'uppercase', letterSpacing: 0.5, mb: 0.5, display: 'block', fontSize: '0.65rem' }}>
                      Relationship Type
                    </Typography>
                    <Chip
                      label={selectedLink.type}
                      size="small"
                      sx={{
                        bgcolor: '#764ba2',
                        color: 'white',
                        fontWeight: 700,
                        fontSize: '0.75rem',
                        px: 0.5,
                        height: 24,
                      }}
                    />
                  </Box>
                  <Button
                    variant="outlined"
                    color="error"
                    startIcon={<Delete sx={{ fontSize: 16 }} />}
                    fullWidth
                    size="small"
                    onClick={() => {
                      onDeleteRelationship?.(selectedLink);
                      setSelectedLink(null);
                    }}
                    sx={{
                      borderRadius: 1,
                      textTransform: 'none',
                      fontWeight: 600,
                      fontSize: '0.75rem',
                      py: 0.5,
                      mt: 2,
                      borderWidth: 2,
                      '&:hover': {
                        borderWidth: 2,
                      },
                    }}
                  >
                    Delete Relationship
                  </Button>
                </Box>
              </Box>
            </Zoom>
          ) : (
            <Box sx={{ p: 3, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: 1.5 }}>
              <Box
                sx={{
                  p: 2,
                  borderRadius: '50%',
                  bgcolor: 'action.hover',
                }}
              >
                <Typography variant="h2" sx={{ opacity: 0.3, fontSize: '3rem' }}>👆</Typography>
              </Box>
              <Typography variant="body1" color="text.secondary" fontWeight={600} fontSize="0.95rem">
                Select an Element
              </Typography>
              <Typography variant="body2" color="text.secondary" textAlign="center" fontSize="0.85rem">
                Click on a node or link in the graph to view its details
              </Typography>
            </Box>
          )}
        </Paper>
      </Box>

      {/* Edit Entity Dialog */}
      <Dialog open={editDialogOpen} onClose={handleEditCancel} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 700, fontSize: '1rem' }}>
          Edit Entity
        </DialogTitle>
        <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
          <TextField
            label="Label"
            fullWidth
            size="small"
            value={editFormData.label}
            onChange={(e) => setEditFormData({ ...editFormData, label: e.target.value })}
            placeholder="Enter entity label"
          />
          <TextField
            label="Type"
            fullWidth
            size="small"
            value={editFormData.type}
            onChange={(e) => setEditFormData({ ...editFormData, type: e.target.value })}
            placeholder="Enter entity type"
          />
        </Box>
        <Box sx={{ p: 2, display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
          <Button
            variant="outlined"
            onClick={handleEditCancel}
            sx={{
              borderRadius: 1,
              textTransform: 'none',
              fontWeight: 600,
            }}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleEditSave}
            sx={{
              borderRadius: 1,
              textTransform: 'none',
              fontWeight: 600,
            }}
          >
            Save Changes
          </Button>
        </Box>
      </Dialog>
    </Box>
  );
}

