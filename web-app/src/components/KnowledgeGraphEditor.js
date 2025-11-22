import { useEffect, useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { Box, Paper, Typography, IconButton, Chip, Tooltip } from '@mui/material';
import { ZoomIn, ZoomOut, CenterFocusStrong } from '@mui/icons-material';

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
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });

  // Teal color palette matching the reference image - using consistent teal for better visibility
  const colorPalette = [
    '#5B8A7D', // Primary Teal (matching reference)
    '#5B8A7D', // Primary Teal
    '#5B8A7D', // Primary Teal
    '#5B8A7D', // Primary Teal
    '#5B8A7D', // Primary Teal
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
        val: 10, // Increased for better visibility
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

    // Detect and consolidate bidirectional relationships
    const linkMap = new Map();

    validRelationships.forEach((rel) => {
      const sourceEntity = entityIdMap.get(rel.source_id);
      const targetEntity = entityIdMap.get(rel.target_id);
      const sourceId = sourceEntity?.id || rel.source_id;
      const targetId = targetEntity?.id || rel.target_id;

      // Create a unique key for this pair (order-independent)
      const pairKey = [sourceId, targetId].sort().join('|');

      if (!linkMap.has(pairKey)) {
        linkMap.set(pairKey, {
          source: sourceId,
          target: targetId,
          forwardType: rel.relationship_type,
          reverseType: null,
          isBidirectional: false,
        });
      } else {
        const existing = linkMap.get(pairKey);

        // Detect reverse direction
        if (
          (existing.source === sourceId && existing.target === targetId) ||
          (existing.source === targetId && existing.target === sourceId)
        ) {
          existing.reverseType = rel.relationship_type;
          existing.isBidirectional = true;

          // If same type both ways → use only one
          if (existing.forwardType === rel.relationship_type) {
            existing.type = existing.forwardType;
          } else {
            existing.type = `${existing.forwardType} ⇄ ${rel.relationship_type}`;
          }
        }
      }

    });

    const links = Array.from(linkMap.values()).map((link) => ({
      ...link.originalRel,
      source: link.source,
      target: link.target,
      type: link.type,
      forwardType: link.forwardType,
      reverseType: link.reverseType,
      isBidirectional: link.isBidirectional,
    }));

    console.log(`Graph data: ${nodes.length} nodes, ${links.length} links (${validRelationships.length - links.length} bidirectional pairs consolidated)`);
    setGraphData({ nodes, links });
  }, [entities, relationships]);

  const handleNodeClick = (node) => {
    setSelectedNode(node);
    onNodeClick?.(node);
  };

  const handleLinkClick = (link) => {
    onLinkClick?.(link);
  };

  const handleNodeHover = (node) => {
    if (fgRef.current) {
      fgRef.current.d3Force('charge').strength(node ? -200 : -150);
    }
  };

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
    <Box sx={{ width: '100%' }}>
      {/* Graph Visualization */}
      <Paper
        elevation={0}
        sx={{
          height: 'calc(100vh - 250px)',
          borderRadius: 1.5,
          overflow: 'hidden',
          position: 'relative',
          border: '2px solid',
          borderColor: 'divider',
          bgcolor: '#ffffff',
          boxShadow: 'none',
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
              onNodeClick={handleNodeClick}
              onLinkClick={handleLinkClick}

              /* === Physics tuned for organic layout like reference === */
              d3AlphaDecay={0.015} // Slightly faster settling
              d3VelocityDecay={0.3} // More damping for stable layout
              warmupTicks={150}
              cooldownTicks={200}
              nodeRelSize={8} // Increased for better node sizing

              width={window.innerWidth * 0.95}
              height={window.innerHeight * 0.85}

              /* STRAIGHT links with arrows - matching reference image */
              linkCurvature={0} // NO CURVE - straight lines like reference
              linkColor={() => "#BBBBBB"} // Light gray for subtle appearance
              linkWidth={1.2} // Slightly thicker for visibility
              linkDirectionalArrowLength={6} // Small arrows like reference
              linkDirectionalArrowRelPos={1} // Arrow at the end
              linkDirectionalArrowColor={() => "#BBBBBB"} // Match link color

              /* Link labels with arrows - styled to match reference image */
              linkCanvasObjectMode={() => "after"}
              linkCanvasObject={(link, ctx, scale) => {
                const start = link.source;
                const end = link.target;
                if (!start || !end) return;

                // Calculate positions
                const dx = end.x - start.x;
                const dy = end.y - start.y;
                const angle = Math.atan2(dy, dx);
                const distance = Math.sqrt(dx * dx + dy * dy);

                // Draw arrow at the end of the link
                const arrowLength = 8;
                const arrowWidth = 4;
                const nodeRadius = 30; // Match the node radius

                // Position arrow just before the target node
                const arrowPos = distance - nodeRadius - 5;
                const arrowX = start.x + Math.cos(angle) * arrowPos;
                const arrowY = start.y + Math.sin(angle) * arrowPos;

                ctx.save();
                ctx.translate(arrowX, arrowY);
                ctx.rotate(angle);

                // Draw arrow triangle
                ctx.beginPath();
                ctx.moveTo(arrowLength, 0);
                ctx.lineTo(0, arrowWidth);
                ctx.lineTo(0, -arrowWidth);
                ctx.closePath();
                ctx.fillStyle = "#999999";
                ctx.fill();

                ctx.restore();

                // Draw label if exists
                const label = link.type || "";
                if (!label) return;

                // Calculate midpoint
                const mx = (start.x + end.x) / 2;
                const my = (start.y + end.y) / 2;

                // Calculate text angle (keep readable)
                let textAngle = angle;
                if (textAngle > Math.PI / 2) textAngle -= Math.PI;
                if (textAngle < -Math.PI / 2) textAngle += Math.PI;

                // Font styling - larger for better readability
                const fontSize = 8 / scale; // Increased from 7 to 10
                ctx.font = `${fontSize}px Arial`;

                // Measure text for background box
                const textMetrics = ctx.measureText(label);
                const textWidth = textMetrics.width;
                const textHeight = fontSize;
                const padding = 3; // Slightly more padding for larger text

                ctx.save();
                ctx.translate(mx, my);
                ctx.rotate(textAngle);

                // Draw white/light background box for label (like reference)
                ctx.fillStyle = "rgba(255, 255, 255, 0.9)";
                ctx.fillRect(
                  -textWidth / 2 - padding,
                  -textHeight / 2 - padding,
                  textWidth + padding * 2,
                  textHeight + padding * 2
                );

                // Draw text on top
                ctx.fillStyle = "#555555"; // Dark gray text
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText(label, 0, 0);

                ctx.restore();
              }}

              /* Node bubbles - styled to match reference image */
              nodeCanvasObject={(node, ctx, scale) => {
                const R = 30; // Larger radius to match reference

                // Draw node circle with teal color matching reference
                ctx.beginPath();
                ctx.arc(node.x, node.y, R, 0, 2 * Math.PI);
                ctx.fillStyle = node.color || "#5B8A7D"; // Teal color from reference
                ctx.fill();

                // Add subtle border for definition
                ctx.strokeStyle = "rgba(0, 0, 0, 0.15)";
                ctx.lineWidth = 1.5;
                ctx.stroke();

                // Draw label inside the circle
                const label = (node.name || "").replace(/_/g, " ");
                const fontSize = 10 / scale;
                ctx.font = `${fontSize}px Arial`;
                ctx.fillStyle = "#ffffff"; // White text like reference
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
  );
}

