import React, { useRef, useEffect } from 'react';
import { Paper, Typography, Box } from '@mui/material';
import ForceGraph2D from 'react-force-graph-2d';

export default function GraphVisualization({ entities, relationships }) {
  const fgRef = useRef();

  // Transform data for force graph
  const graphData = {
    nodes: entities.map((entity) => ({
      id: entity.id,
      name: entity.label || entity.id,
      type: entity.type,
      val: 10,
    })),
    links: relationships.map((rel) => ({
      source: rel.source_id,
      target: rel.target_id,
      type: rel.relationship_type,
    })),
  };

  useEffect(() => {
    if (fgRef.current && graphData.nodes.length > 0) {
      fgRef.current.zoomToFit(400, 50);
    }
  }, [graphData.nodes.length]);

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
      <Typography variant="h6" gutterBottom>
        Graph Visualization
      </Typography>
      <Box
        sx={{
          width: '100%',
          height: 600,
          border: '1px solid #e0e0e0',
          borderRadius: 1,
          overflow: 'hidden',
        }}
      >
        <ForceGraph2D
          ref={fgRef}
          graphData={graphData}
          nodeLabel="name"
          nodeAutoColorBy="type"
          linkLabel="type"
          linkDirectionalArrowLength={6}
          linkDirectionalArrowRelPos={1}
          linkCurvature={0.15}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const label = node.name;
            const fontSize = 12 / globalScale;
            ctx.font = `${fontSize}px Sans-Serif`;
            const textWidth = ctx.measureText(label).width;
            const bckgDimensions = [textWidth, fontSize].map((n) => n + fontSize * 0.2);

            ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
            ctx.fillRect(
              node.x - bckgDimensions[0] / 2,
              node.y - bckgDimensions[1] / 2,
              ...bckgDimensions
            );

            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = node.color;
            ctx.fillText(label, node.x, node.y);

            // Draw circle
            ctx.beginPath();
            ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false);
            ctx.fillStyle = node.color;
            ctx.fill();
          }}
          onNodeClick={(node) => {
            console.log('Node clicked:', node);
          }}
          onLinkClick={(link) => {
            console.log('Link clicked:', link);
          }}
        />
      </Box>
      <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box sx={{ width: 16, height: 16, bgcolor: '#1976d2', borderRadius: '50%' }} />
          <Typography variant="caption">Tables</Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box sx={{ width: 16, height: 16, bgcolor: '#dc004e', borderRadius: '50%' }} />
          <Typography variant="caption">Columns</Typography>
        </Box>
      </Box>
    </Paper>
  );
}
