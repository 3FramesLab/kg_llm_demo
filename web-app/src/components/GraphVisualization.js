import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Paper, Typography, Box, Button, ButtonGroup, Tooltip } from '@mui/material';
import ForceGraph2D from 'react-force-graph-2d';
import { ZoomIn, ZoomOut, CenterFocusStrong } from '@mui/icons-material';

export default function GraphVisualization({ entities, relationships }) {
  const fgRef = useRef();
  const [highlightNodes, setHighlightNodes] = useState(new Set());
  const [highlightLinks, setHighlightLinks] = useState(new Set());
  const [hoverNode, setHoverNode] = useState(null);

  // Calculate node sizes based on connections
  const connectionCounts = {};
  relationships.forEach((rel) => {
    connectionCounts[rel.source_id] = (connectionCounts[rel.source_id] || 0) + 1;
    connectionCounts[rel.target_id] = (connectionCounts[rel.target_id] || 0) + 1;
  });

  // Transform data for force graph
  const graphData = {
    nodes: entities.map((entity) => {
      const connections = connectionCounts[entity.id] || 1;
      return {
        id: entity.id,
        name: entity.label || entity.id,
        type: entity.type,
        val: Math.max(15, Math.min(connections * 8, 50)), // Dynamic size based on connections
        connections: connections,
      };
    }),
    links: relationships.map((rel) => ({
      source: rel.source_id,
      target: rel.target_id,
      type: rel.relationship_type,
    })),
  };

  useEffect(() => {
    if (fgRef.current && graphData.nodes.length > 0) {
      // Give time for nodes to settle before zooming
      setTimeout(() => {
        fgRef.current.zoomToFit(800, 80);
      }, 100);
    }
  }, [graphData.nodes.length]);

  // Handle node hover for highlighting
  const handleNodeHover = useCallback((node) => {
    setHoverNode(node);
    if (node) {
      const newHighlightNodes = new Set();
      const newHighlightLinks = new Set();

      newHighlightNodes.add(node.id);

      graphData.links.forEach((link) => {
        if (link.source.id === node.id || link.target.id === node.id) {
          newHighlightLinks.add(link);
          newHighlightNodes.add(link.source.id);
          newHighlightNodes.add(link.target.id);
        }
      });

      setHighlightNodes(newHighlightNodes);
      setHighlightLinks(newHighlightLinks);
    } else {
      setHighlightNodes(new Set());
      setHighlightLinks(new Set());
    }
  }, [graphData.links]);

  // Zoom controls
  const handleZoomIn = () => {
    if (fgRef.current) {
      fgRef.current.zoom(fgRef.current.zoom() * 1.5, 400);
    }
  };

  const handleZoomOut = () => {
    if (fgRef.current) {
      fgRef.current.zoom(fgRef.current.zoom() / 1.5, 400);
    }
  };

  const handleZoomToFit = () => {
    if (fgRef.current) {
      fgRef.current.zoomToFit(400, 80);
    }
  };

  if (entities.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          No graph data to display
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Graph Visualization
        </Typography>
        <ButtonGroup variant="outlined" size="small">
          <Tooltip title="Zoom In">
            <Button onClick={handleZoomIn}>
              <ZoomIn />
            </Button>
          </Tooltip>
          <Tooltip title="Zoom Out">
            <Button onClick={handleZoomOut}>
              <ZoomOut />
            </Button>
          </Tooltip>
          <Tooltip title="Fit to Screen">
            <Button onClick={handleZoomToFit}>
              <CenterFocusStrong />
            </Button>
          </Tooltip>
        </ButtonGroup>
      </Box>
      <Box
        sx={{
          width: '100%',
          height: 700,
          border: '1px solid #e0e0e0',
          borderRadius: 1,
          overflow: 'hidden',
          bgcolor: '#fafafa',
        }}
      >
        <ForceGraph2D
          ref={fgRef}
          graphData={graphData}
          nodeLabel={(node) => `${node.name}\nType: ${node.type || 'N/A'}\nConnections: ${node.connections}`}
          nodeAutoColorBy="type"
          linkLabel={(link) => link.type}
          linkDirectionalArrowLength={8}
          linkDirectionalArrowRelPos={1}
          linkCurvature={0.2}
          linkWidth={(link) => (highlightLinks.has(link) ? 3 : 1)}
          linkColor={(link) => (highlightLinks.has(link) ? '#ff6b6b' : '#999999')}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const label = node.name;
            const fontSize = Math.max(14, 16 / globalScale);
            const nodeSize = Math.sqrt(node.val) * 2;
            const isHighlighted = highlightNodes.has(node.id);
            const isHovered = hoverNode?.id === node.id;

            // Draw larger circle for node
            ctx.beginPath();
            ctx.arc(node.x, node.y, nodeSize, 0, 2 * Math.PI, false);
            ctx.fillStyle = node.color;
            ctx.fill();

            // Add highlight ring if highlighted or hovered
            if (isHighlighted || isHovered) {
              ctx.strokeStyle = isHovered ? '#ff6b6b' : '#ffeb3b';
              ctx.lineWidth = 3;
              ctx.stroke();
            } else {
              ctx.strokeStyle = '#ffffff';
              ctx.lineWidth = 2;
              ctx.stroke();
            }

            // Draw label with better background
            ctx.font = `bold ${fontSize}px Arial, Sans-Serif`;
            const textWidth = ctx.measureText(label).width;
            const padding = fontSize * 0.4;
            const bckgDimensions = [textWidth + padding * 2, fontSize + padding];

            ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
            ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
            ctx.shadowBlur = 4;
            ctx.shadowOffsetX = 2;
            ctx.shadowOffsetY = 2;
            ctx.fillRect(
              node.x - bckgDimensions[0] / 2,
              node.y + nodeSize + 4,
              ...bckgDimensions
            );
            ctx.shadowColor = 'transparent';

            // Draw label text
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';
            ctx.fillStyle = isHighlighted || isHovered ? '#000000' : '#333333';
            ctx.fillText(label, node.x, node.y + nodeSize + 4 + padding / 2);
          }}
          onNodeHover={handleNodeHover}
          onNodeClick={(node) => {
            console.log('Node clicked:', node);
            // You can add more interaction here
          }}
          onLinkClick={(link) => {
            console.log('Link clicked:', link);
          }}
          cooldownTicks={100}
          d3VelocityDecay={0.3}
          d3AlphaDecay={0.01}
        />
      </Box>
      <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
        <Typography variant="caption" color="text.secondary" sx={{ mr: 2 }}>
          Node size represents number of connections. Hover over nodes to highlight connections.
        </Typography>
      </Box>
    </Paper>
  );
}
