import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  List,
  ListItem,
  ListItemText,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Fade,
  IconButton,
  Tooltip,
} from '@mui/material';
import { Refresh, Description, Storage, Info, CheckCircle } from '@mui/icons-material';
import { listSchemas } from '../services/api';

export default function Schemas() {
  const [schemas, setSchemas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadSchemas();
  }, []);

  const loadSchemas = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await listSchemas();
      setSchemas(response.data.schemas || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 1.5 }}>
      {/* Enhanced Gradient Header */}
      <Box
        sx={{
          mb: 3,
          p: 2,
          borderRadius: 2,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          boxShadow: '0 4px 20px rgba(102, 126, 234, 0.3)',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Storage sx={{ fontSize: 28 }} />
            <Box>
              <Typography variant="h5" fontWeight="700" sx={{ lineHeight: 1.2, fontSize: '1.15rem' }}>
                Database Schemas ({schemas.length})
              </Typography>
            </Box>
          </Box>
          <Tooltip title="Refresh Schemas">
            <IconButton
              onClick={loadSchemas}
              disabled={loading}
              sx={{
                color: 'white',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                },
                '&:disabled': {
                  color: 'rgba(255, 255, 255, 0.5)',
                },
              }}
            >
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Loading State */}
      {loading && (
        <Fade in={loading}>
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', my: 6 }}>
            <CircularProgress size={48} thickness={4} />
          </Box>
        </Fade>
      )}

      {/* Error State */}
      {error && (
        <Fade in={!!error}>
          <Alert
            severity="error"
            sx={{
              mb: 3,
              borderRadius: 2,
              border: '1px solid',
              borderColor: 'error.light',
              fontWeight: 600,
            }}
          >
            Error loading schemas: {error}
          </Alert>
        </Fade>
      )}

      {/* Empty State */}
      {!loading && schemas.length === 0 && !error && (
        <Fade in={!loading && schemas.length === 0}>
          <Paper
            elevation={0}
            sx={{
              p: 4,
              borderRadius: 2,
              border: '2px dashed',
              borderColor: 'divider',
              textAlign: 'center',
              background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.03) 0%, rgba(118, 75, 162, 0.03) 100%)',
            }}
          >
            <Storage sx={{ fontSize: 64, color: 'text.secondary', mb: 2, opacity: 0.5 }} />
            <Typography variant="h6" fontWeight="700" fontSize="0.95rem" gutterBottom>
              No Schemas Found
            </Typography>
            <Typography variant="body2" fontSize="0.8rem" color="text.secondary">
              Place JSON schema files in the <code style={{
                padding: '2px 6px',
                borderRadius: '4px',
                background: 'rgba(0,0,0,0.05)',
                fontWeight: 600,
              }}>schemas/</code> directory to get started.
            </Typography>
          </Paper>
        </Fade>
      )}

      {/* Schemas List */}
      {!loading && schemas.length > 0 && (
        <Fade in={!loading && schemas.length > 0}>
          <Paper
            elevation={0}
            sx={{
              borderRadius: 2,
              border: '1px solid',
              borderColor: 'divider',
              overflow: 'hidden',
            }}
          >
            <List sx={{ p: 0 }}>
              {schemas.map((schema, index) => (
                <ListItem
                  key={index}
                  divider={index < schemas.length - 1}
                  sx={{
                    py: 2,
                    px: 2.5,
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      backgroundColor: 'rgba(102, 126, 234, 0.04)',
                      transform: 'translateX(4px)',
                    },
                  }}
                  secondaryAction={
                    <Chip
                      icon={<Description sx={{ fontSize: 18 }} />}
                      label="JSON Schema"
                      size="medium"
                      color="primary"
                      variant="outlined"
                      sx={{
                        fontWeight: 600,
                        borderRadius: 1.5,
                        borderWidth: 2,
                      }}
                    />
                  }
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1, mr: 2 }}>
                    <Box
                      sx={{
                        p: 1.5,
                        borderRadius: 1.5,
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        minWidth: 48,
                      }}
                    >
                      <Storage sx={{ color: 'white', fontSize: 24 }} />
                    </Box>
                    <ListItemText
                      primary={
                        <Typography variant="h6" fontWeight="700" fontSize="0.95rem" component="span" sx={{ mb: 0.5 }}>
                          {schema}
                        </Typography>
                      }
                      secondary={
                        <Typography variant="body2" fontSize="0.8rem" color="text.secondary" sx={{ mt: 0.5 }}>
                          Location: <code style={{
                            padding: '2px 6px',
                            borderRadius: '4px',
                            background: 'rgba(0,0,0,0.05)',
                            fontWeight: 600,
                            fontSize: '0.75rem',
                          }}>schemas/{schema}.json</code>
                        </Typography>
                      }
                    />
                  </Box>
                </ListItem>
              ))}
            </List>
          </Paper>
        </Fade>
      )}

      {/* About Section */}
      <Paper
        elevation={0}
        sx={{
          p: 3,
          mt: 3,
          borderRadius: 2,
          border: '1px solid',
          borderColor: 'divider',
          background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.03) 0%, rgba(118, 75, 162, 0.03) 100%)',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
          <Box
            sx={{
              p: 1,
              borderRadius: 1.5,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Info sx={{ color: 'white', fontSize: 22 }} />
          </Box>
          <Typography variant="h6" fontWeight="700" fontSize="0.95rem">
            About Database Schemas
          </Typography>
        </Box>

        <Typography variant="body2" fontSize="0.8rem" paragraph sx={{ mb: 2, lineHeight: 1.6 }}>
          Database schemas define the structure of your databases including tables, columns, and
          relationships. These schemas are used to generate knowledge graphs and reconciliation
          rules.
        </Typography>

        <Box
          sx={{
            p: 2.5,
            borderRadius: 1.5,
            background: 'white',
            border: '1px solid',
            borderColor: 'divider',
          }}
        >
          <Typography variant="body2" fontSize="0.85rem" fontWeight="700" sx={{ mb: 2 }}>
            To add a new schema:
          </Typography>
          <Box component="ol" sx={{ pl: 2.5, m: 0 }}>
            <Box component="li" sx={{ mb: 1.5 }}>
              <Typography variant="body2" fontSize="0.8rem" sx={{ lineHeight: 1.6 }}>
                Export your database schema as JSON format
              </Typography>
            </Box>
            <Box component="li" sx={{ mb: 1.5 }}>
              <Typography variant="body2" fontSize="0.8rem" sx={{ lineHeight: 1.6 }}>
                Place the file in the <code style={{
                  padding: '2px 6px',
                  borderRadius: '4px',
                  background: 'rgba(102, 126, 234, 0.1)',
                  fontWeight: 600,
                  color: '#667eea',
                }}>schemas/</code> directory
              </Typography>
            </Box>
            <Box component="li" sx={{ mb: 1.5 }}>
              <Typography variant="body2" fontSize="0.8rem" sx={{ lineHeight: 1.6 }}>
                Refresh this page to see the new schema
              </Typography>
            </Box>
            <Box component="li">
              <Typography variant="body2" fontSize="0.8rem" sx={{ lineHeight: 1.6 }}>
                Navigate to <strong style={{ color: '#667eea' }}>Knowledge Graph</strong> to generate a graph from the schema
              </Typography>
            </Box>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
}
