import { useEffect, useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { Box, Paper, Typography, Button, IconButton, Chip, Tooltip, Zoom } from '@mui/material';
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

  // Enhanced color mapping for entity types with gradients
  const typeColors = {
    'Entity': '#667eea',
    'Person': '#764ba2',
    'Organization': '#f093fb',
    'Location': '#4facfe',
    'Product': '#43e97b',
    'Order': '#fa709a',
    'Supplier': '#30cfd0',
    'Warehouse': '#a8edea',
    'Category': '#fed6e3',
    'Unknown': '#999999',
  };

  // Convert entities and relationships to graph format
  useEffect(() => {
    const nodes = entities.map((entity) => ({
      id: entity.id,
      name: entity.label || entity.id,
      type: entity.type || 'Unknown',
      val: 15,
      color: typeColors[entity.type] || typeColors['Unknown'],
      ...entity,
    }));

    // Create a set of valid entity IDs for validation
    const validEntityIds = new Set(entities.map((e) => e.id));

    // Filter relationships to only include those with valid source and target nodes
    const validRelationships = relationships.filter((rel) => {
      const isValid = validEntityIds.has(rel.source_id) && validEntityIds.has(rel.target_id);
      if (!isValid) {
        console.warn(
          `Skipping relationship: ${rel.source_id} -> ${rel.target_id} (node not found)`
        );
      }
      return isValid;
    });

    const links = validRelationships.map((rel) => ({
      source: rel.source_id,
      target: rel.target_id,
      type: rel.relationship_type,
      ...rel,
    }));

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
              nodeColor={(node) => (selectedNode?.id === node.id ? '#ff6b6b' : node.color)}
              nodeVal={(node) => (selectedNode?.id === node.id ? 20 : 15)}
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
                const fontSize = 2;
                ctx.font = `${fontSize}px Arial`;
                const textWidth = ctx.measureText(label).width;
                const bckgDimensions = [textWidth, fontSize].map((n) => n + fontSize * 0.05);
 
                ctx.fillStyle = node.color;
                ctx.beginPath();
                ctx.arc(node.x, node.y, node.val, 0, 2 * Math.PI);
                ctx.fill();
 
                if (selectedNode?.id === node.id) {
                  ctx.strokeStyle = '#ff6b6b';
                  ctx.lineWidth = 3;
                  ctx.beginPath();
                  ctx.arc(node.x, node.y, node.val + 1, 0, 2 * Math.PI);
                  ctx.stroke();
                }
 
                ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
                ctx.fillRect(
                  node.x - bckgDimensions[0] / 2,
                  node.y - bckgDimensions[1] / 2,
                  ...bckgDimensions
                );
 
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
    </Box>
  );
}

