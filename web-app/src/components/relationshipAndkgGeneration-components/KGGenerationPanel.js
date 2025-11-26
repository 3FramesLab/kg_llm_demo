import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  FormControlLabel,
  Checkbox,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Chip,
  Grid,
  LinearProgress,
} from '@mui/material';
import { PlayArrow } from '@mui/icons-material';
import { generateKG } from '../../services/api';
import KnowledgeGraphEditor from '../KnowledgeGraphEditor';

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

export default function KGGenerationPanel({ schemaConfig, relationships, onKGGenerated }) {
  const [kgName, setKgName] = useState('');
  const [useLLM, setUseLLM] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [generationProgress, setGenerationProgress] = useState(0);

  // State for generated KG data
  const [generatedKGName, setGeneratedKGName] = useState(null);
  const [generatedNodes, setGeneratedNodes] = useState([]);
  const [generatedRelationships, setGeneratedRelationships] = useState([]);

  const handleGenerateKG = async () => {
    if (!kgName.trim()) {
      setError('Please enter a knowledge graph name');
      return;
    }

    if (!schemaConfig || !schemaConfig.tables || schemaConfig.tables.length === 0) {
      setError('No schema configuration available');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);
    setGenerationProgress(0);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setGenerationProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const payload = {
        schema_names: schemaConfig.tables.map(t => t.databaseName),
        schema_id: schemaConfig.id || null,
        schema_name: schemaConfig.schemaName || null,
        kg_name: kgName,
        use_llm_enhancement: useLLM,
        backends: ['graphiti'],
        relationship_pairs: relationships
          .filter(rel => !rel.is_placeholder) // Exclude placeholder rows
          .map(rel => ({
            source_table: rel.source_table || '',
            source_column: rel.source_column || '',
            target_table: rel.target_table || '',
            target_column: rel.target_column || '',
            relationship_type: rel.relationship_type || 'MATCHES',
            confidence: typeof rel.confidence === 'number' ? rel.confidence : 0.8,
            bidirectional: typeof rel.bidirectional === 'boolean' ? rel.bidirectional : true,
            _comment: rel._comment || '',
          })),
      };

      // Log schema metadata for debugging
      if (schemaConfig.id || schemaConfig.schemaName) {
        console.log('Including schema metadata:', {
          schema_id: schemaConfig.id,
          schema_name: schemaConfig.schemaName,
        });
      }

      const response = await generateKG(payload);
      clearInterval(progressInterval);
      setGenerationProgress(100);

      if (response.data.success) {
        setSuccess(`Knowledge graph "${kgName}" generated successfully!`);

        // Capture the generated KG data for visualization
        setGeneratedKGName(response.data.kg_name || kgName);
        setGeneratedNodes(response.data.nodes || []);
        setGeneratedRelationships(response.data.relationships || []);

        console.log('Generated KG Data:', {
          kg_name: response.data.kg_name,
          nodes_count: response.data.nodes_count,
          relationships_count: response.data.relationships_count,
          nodes: response.data.nodes,
          relationships: response.data.relationships,
        });

        setKgName('');
        // Don't call onKGGenerated() immediately - let user view the graph first
      } else {
        setError(response.data.message || 'Failed to generate knowledge graph');
      }
    } catch (err) {
      const errorMessage = err.code === 'ERR_NETWORK' || err.message === 'Network Error'
        ? 'Unable to connect to the backend server. Please ensure the backend is running on http://localhost:8000'
        : err.response?.data?.detail || 'Error generating knowledge graph';
      setError(errorMessage);
      console.error('Error:', err);
    } finally {
      setLoading(false);
      setTimeout(() => setGenerationProgress(0), 1000);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: 0 }}>
      {/* Alerts */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      {/* Configuration and Settings Grid */}
      <Grid container spacing={1.5} sx={{ mb: 2 }}>
        {/* Configuration Summary */}
        <Grid item xs={12} md={6}>
          <Paper
            elevation={0}
            sx={{
              p: 1.5,
              border: '1px solid #E5E7EB',
              borderRadius: 1,
              bgcolor: '#FFFFFF',
            }}
          >
            <Typography
              variant="subtitle2"
              sx={{
                fontWeight: 600,
                color: '#1F2937',
                fontSize: '0.9rem',
                mb: 1.5,
              }}
            >
              Configuration Summary
            </Typography>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography
                  variant="body2"
                  sx={{
                    color: '#6B7280',
                    fontSize: '0.8125rem',
                  }}
                >
                  Tables:
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: 600,
                    color: '#1F2937',
                    fontSize: '0.8125rem',
                  }}
                >
                  {schemaConfig?.tables?.length || 0}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography
                  variant="body2"
                  sx={{
                    color: '#6B7280',
                    fontSize: '0.8125rem',
                  }}
                >
                  Relationships:
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: 600,
                    color: '#1F2937',
                    fontSize: '0.8125rem',
                  }}
                >
                  {relationships?.length || 0}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography
                  variant="body2"
                  sx={{
                    color: '#6B7280',
                    fontSize: '0.8125rem',
                  }}
                >
                  LLM Enhancement:
                </Typography>
                <Box
                  component="span"
                  sx={{
                    display: 'inline-block',
                    px: 1,
                    py: 0.25,
                    bgcolor: useLLM ? '#DBEAFE' : '#F3F4F6',
                    color: useLLM ? '#0369A1' : '#6B7280',
                    borderRadius: '4px',
                    fontSize: '0.75rem',
                    fontWeight: 500,
                  }}
                >
                  {useLLM ? 'Enabled' : 'Disabled'}
                </Box>
              </Box>
            </Box>

            <Box sx={{ mt: 1.5, pt: 1.5, borderTop: '1px solid #E5E7EB' }}>
              <Typography
                variant="body2"
                sx={{
                  fontWeight: 600,
                  color: '#1F2937',
                  fontSize: '0.8125rem',
                  mb: 1,
                }}
              >
                Tables Included:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.75 }}>
                {schemaConfig?.tables?.map(t => (
                  <Chip
                    key={t.tableName}
                    label={getTableDisplayName(t)}
                    size="small"
                    sx={{
                      height: '24px',
                      fontSize: '0.75rem',
                      bgcolor: '#EEF2FF',
                      color: '#5B6FE5',
                    }}
                  />
                ))}
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Generation Settings */}
        <Grid item xs={12} md={6}>
          <Paper
            elevation={0}
            sx={{
              p: 1.5,
              border: '1px solid #E5E7EB',
              borderRadius: 1,
              bgcolor: '#FFFFFF',
            }}
          >
            <Typography
              variant="subtitle2"
              sx={{
                fontWeight: 600,
                color: '#1F2937',
                fontSize: '0.9rem',
                mb: 1.5,
              }}
            >
              Generation Settings
            </Typography>

            <TextField
              fullWidth
              label="Knowledge Graph Name"
              value={kgName}
              onChange={(e) => setKgName(e.target.value)}
              placeholder="e.g., my_kg_v1"
              disabled={loading}
              sx={{
                mb: 1.5,
              }}
            />

            <FormControlLabel
              control={
                <Checkbox
                  checked={useLLM}
                  onChange={(e) => setUseLLM(e.target.checked)}
                  disabled={loading}
                  sx={{
                    color: '#CBD5E1',
                    '&.Mui-checked': {
                      color: '#5B6FE5',
                    },
                  }}
                />
              }
              label={
                <Typography sx={{ fontSize: '0.8125rem', color: '#6B7280' }}>
                  Use LLM Enhancement for relationship detection
                </Typography>
              }
              sx={{ mb: 1.5 }}
            />

            {loading && (
              <Box sx={{ mb: 1.5 }}>
                <LinearProgress
                  variant="determinate"
                  value={generationProgress}
                  sx={{
                    height: '6px',
                    borderRadius: '3px',
                    bgcolor: '#E5E7EB',
                    '& .MuiLinearProgress-bar': {
                      bgcolor: '#5B6FE5',
                    },
                  }}
                />
                <Typography
                  variant="caption"
                  sx={{
                    mt: 0.75,
                    display: 'block',
                    color: '#6B7280',
                    fontSize: '0.75rem',
                  }}
                >
                  Generating... {generationProgress}%
                </Typography>
              </Box>
            )}

            <Button
              fullWidth
              variant="contained"
              startIcon={loading ? <CircularProgress size={16} sx={{ mr: 0.5 }} /> : <PlayArrow />}
              onClick={handleGenerateKG}
              disabled={loading || !kgName.trim()}
              size="small"
            >
              {loading ? 'Generating...' : 'Generate Knowledge Graph'}
            </Button>
          </Paper>
        </Grid>
      </Grid>

      {/* Relationships Preview */}
      {relationships && relationships.length > 0 && (
        <Paper
          elevation={0}
          sx={{
            flex: 1,
            overflow: 'auto',
            border: '1px solid #E5E7EB',
            borderRadius: 1,
            bgcolor: '#FFFFFF',
          }}
        >
          <Box sx={{ p: 1.5, borderBottom: '1px solid #E5E7EB' }}>
            <Typography
              variant="subtitle2"
              sx={{
                fontWeight: 600,
                color: '#1F2937',
                fontSize: '0.9rem',
              }}
            >
              Relationships to be Used ({relationships.length})
            </Typography>
          </Box>
          <Box sx={{ p: 1.5, display: 'flex', flexDirection: 'column', gap: 1 }}>
            {relationships.map((rel, idx) => (
              <Card
                key={idx}
                sx={{
                  border: '1px solid #E5E7EB',
                  bgcolor: idx % 2 === 0 ? '#FFFFFF' : '#F9FAFB',
                  '&:hover': {
                    bgcolor: '#F5F7FF',
                  },
                }}
              >
                <CardContent sx={{ p: 1, '&:last-child': { pb: 1 } }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                    <Typography
                      variant="body2"
                      sx={{
                        fontSize: '0.8125rem',
                        color: '#1F2937',
                      }}
                    >
                      <strong>
                        {(() => {
                          const sourceTable = schemaConfig?.tables?.find(t => t.tableName === rel.source_table);
                          return sourceTable ? getTableDisplayName(sourceTable) : rel.source_table;
                        })()}
                      </strong>
                      <span sx={{ color: '#9CA3AF' }}>.{rel.source_column}</span>
                    </Typography>
                    <Typography
                      sx={{
                        fontSize: '0.8125rem',
                        color: '#9CA3AF',
                      }}
                    >
                      →
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        fontSize: '0.8125rem',
                        color: '#1F2937',
                      }}
                    >
                      <strong>
                        {(() => {
                          const targetTable = schemaConfig?.tables?.find(t => t.tableName === rel.target_table);
                          return targetTable ? getTableDisplayName(targetTable) : rel.target_table;
                        })()}
                      </strong>
                      <span sx={{ color: '#9CA3AF' }}>.{rel.target_column}</span>
                    </Typography>
                    <Chip
                      label={rel.relationship_type}
                      size="small"
                      sx={{
                        height: '20px',
                        fontSize: '0.7rem',
                        bgcolor: '#EEF2FF',
                        color: '#5B6FE5',
                        ml: 'auto',
                      }}
                    />
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Box>
        </Paper>
      )}

      {/* Generated Knowledge Graph Visualization */}
      {generatedKGName && generatedNodes.length > 0 && (
        <Paper
          elevation={0}
          sx={{
            mt: 2,
            border: '1px solid #E5E7EB',
            borderRadius: 1,
            bgcolor: '#FFFFFF',
            overflow: 'hidden',
          }}
        >
          <Box
            sx={{
              p: 1.5,
              borderBottom: '1px solid #E5E7EB',
              bgcolor: '#F9FAFB',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <Typography
              variant="subtitle2"
              sx={{
                fontWeight: 600,
                color: '#1F2937',
                fontSize: '0.9rem',
              }}
            >
              Generated Knowledge Graph: {generatedKGName}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Chip
                label={`${generatedNodes.length} Nodes`}
                size="small"
                sx={{
                  bgcolor: '#EEF2FF',
                  color: '#5B6FE5',
                  fontSize: '0.7rem',
                  fontWeight: 600,
                }}
              />
              <Chip
                label={`${generatedRelationships.length} Relationships`}
                size="small"
                sx={{
                  bgcolor: '#F0FDF4',
                  color: '#16A34A',
                  fontSize: '0.7rem',
                  fontWeight: 600,
                }}
              />
            </Box>
          </Box>
          <Box sx={{ height: '600px', bgcolor: '#FAFAFA' }}>
            <KnowledgeGraphEditor
              kgName={generatedKGName}
              entities={generatedNodes}
              relationships={generatedRelationships}
              onRefresh={() => {
                // Optional: Add refresh logic if needed
                console.log('Refresh requested for generated KG');
              }}
            />
          </Box>
        </Paper>
      )}
    </Box>
  );
}

