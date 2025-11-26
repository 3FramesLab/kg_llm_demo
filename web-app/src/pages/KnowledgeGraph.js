import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Button,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Chip,
  Tabs,
  Tab,
  Fade,
  Backdrop,
  Divider,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Refresh,
  Delete,
  Download,
  AccountTree,
  Hub,
  Visibility,
} from '@mui/icons-material';
import {
  listKGs,
  getKGEntities,
  getKGRelationships,
  exportKG,
  deleteKG,
} from '../services/api';
import KnowledgeGraphEditor from '../components/KnowledgeGraphEditor';


export default function KnowledgeGraph() {
  const theme = useTheme();
  const [tabValue, setTabValue] = useState(0);
  const [knowledgeGraphs, setKnowledgeGraphs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Selected KG details
  const [selectedKG, setSelectedKG] = useState(null);
  const [kgEntities, setKgEntities] = useState([]);
  const [kgRelationships, setKgRelationships] = useState([]);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const kgsRes = await listKGs();

      console.log('KGs Response:', kgsRes.data); // Debug log

      setKnowledgeGraphs(kgsRes.data.data || []); // Fixed: changed from 'graphs' to 'data'
    } catch (err) {
      console.error('Error loading data:', err);
      console.error('Full error details:', err.response || err);
    }
  };

  const handleLoadKG = async (kgName) => {
    setLoading(true);
    try {
      const [entitiesRes, relationshipsRes] = await Promise.all([
        getKGEntities(kgName),
        getKGRelationships(kgName),
      ]);

      setSelectedKG(kgName);
      setKgEntities(entitiesRes.data.entities || []);
      setKgRelationships(relationshipsRes.data.relationships || []);
      setTabValue(1);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to load KG';
      setError(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
      console.error('Load KG Error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Refresh KG data after mutations (for backend integration)
  const handleRefreshKG = async () => {
    if (!selectedKG) return;

    try {
      const [entitiesRes, relationshipsRes] = await Promise.all([
        getKGEntities(selectedKG),
        getKGRelationships(selectedKG),
      ]);

      setKgEntities(entitiesRes.data.entities || []);
      setKgRelationships(relationshipsRes.data.relationships || []);
    } catch (err) {
      console.error('Error refreshing KG:', err);
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to refresh KG';
      setError(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
    }
  };

  const handleExport = async (kgName) => {
    try {
      const response = await exportKG(kgName);
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${kgName}_export.json`;
      a.click();
      setSuccess(`Knowledge graph "${kgName}" exported successfully!`);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    }
  };

  const handleDelete = async (kgName) => {
    if (!window.confirm(`Are you sure you want to delete "${kgName}"?`)) {
      return;
    }

    try {
      await deleteKG(kgName);
      setSuccess(`Knowledge graph "${kgName}" deleted successfully!`);
      loadInitialData();
      if (selectedKG === kgName) {
        setSelectedKG(null);
        setKgEntities([]);
        setKgRelationships([]);
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to delete KG';
      setError(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
      console.error('Delete KG Error:', err);
    }
  };

  return (
    <Box sx={{ p: 2 }}>
      <Container maxWidth="auto" disableGutters>
        <Fade in timeout={600}>
          <Box
            sx={{
              position: 'relative',
              '&::before': {
                content: '""',
                position: 'absolute',
                top: -8,
                left: -8,
                right: -8,
                bottom: -8,
                borderRadius: '16px',
                background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.05)} 0%, ${alpha(theme.palette.secondary.main, 0.05)} 100%)`,
                opacity: 0,
                transition: 'opacity 0.3s ease-in-out',
                pointerEvents: 'none',
                zIndex: -1,
              },
              '&:hover::before': {
                opacity: 1,
              },
            }}
          >
            <Paper
              elevation={0}
              sx={{
                height: '100%',
                minHeight: 'calc(100vh - 64px)',
                p: 2,
                bgcolor: '#FFFFFF',
                border: '1px solid #E5E7EB',
                borderRadius: 4,
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              {/* Header Section */}
              <Box sx={{ mb: 1.5 }}>
                <Typography
                  variant="h5"
                  sx={{
                    mb: 0.5,
                    fontWeight: 600,
                    fontSize: '1.25rem',
                    color: '#5B6FE5',
                    lineHeight: 1.3,
                  }}
                >
                  Knowledge Graph Builder
                </Typography>

                <Typography
                  variant="body2"
                  sx={{
                    color: '#6B7280',
                    fontSize: '0.875rem',
                    lineHeight: 1.5,
                  }}
                >
                  Generate and visualize knowledge graphs from database schemas
                </Typography>
              </Box>
              <Divider sx={{ mb: 2 }} />

              {/* Alerts */}
              {error && (
                <Alert
                  severity="error"
                  onClose={() => setError(null)}
                  sx={{ mb: 1.5 }}
                >
                  {typeof error === 'string' ? error : JSON.stringify(error)}
                </Alert>
              )}

              {success && (
                <Alert
                  severity="success"
                  onClose={() => setSuccess(null)}
                  sx={{ mb: 1.5 }}
                >
                  {success}
                </Alert>
              )}

              {/* Tabs Navigation */}
              <Tabs
                value={tabValue}
                onChange={(e, newValue) => setTabValue(newValue)}
                sx={{
                  mb: 1.5,
                  '& .MuiTab-root': {
                    fontSize: '0.875rem',
                    fontWeight: 600,
                    textTransform: 'none',
                    minHeight: 48,
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      color: 'primary.main',
                      bgcolor: 'rgba(25, 118, 210, 0.04)',
                    },
                    '&.Mui-selected': {
                      color: 'primary.main',
                    },
                  },
                  '& .MuiTabs-indicator': {
                    height: 3,
                    borderRadius: '3px 3px 0 0',
                  },
                }}
              >
                <Tab
                  icon={<AccountTree sx={{ fontSize: 20, mb: 0.5 }} />}
                  iconPosition="start"
                  label="Manage KGs"
                />
                <Tab
                  icon={<Visibility sx={{ fontSize: 20, mb: 0.5 }} />}
                  iconPosition="start"
                  label="View KG"
                />
              </Tabs>

              {/* Content Area */}
              <Box
                sx={{
                  flex: 1,
                  bgcolor: '#F9FAFB',
                  p: 1.5,
                  borderRadius: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  minHeight: 300,
                }}
              >
                {/* Tab 1: Manage */}
                {tabValue === 0 && (
                  <Fade in={tabValue === 0}>
                    <Grid
                      container
                      spacing={1.5}
                      role="tabpanel"
                      id="tabpanel-0"
                      aria-labelledby="tab-0"
                    >
                      <Grid item xs={12}>
                        <Box sx={{ mb: 1.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 1 }}>
                          <Box>
                            <Typography variant="h6" fontWeight="700" gutterBottom sx={{ mb: 0.25, fontSize: '0.95rem' }}>
                              Manage Knowledge Graphs
                            </Typography>
                            <Typography variant="body2" color="text.secondary" fontSize="0.75rem">
                              View, export, and manage your knowledge graphs
                            </Typography>
                          </Box>
                          <Button
                            variant="outlined"
                            size="small"
                            startIcon={<Refresh sx={{ fontSize: 18 }} />}
                            onClick={loadInitialData}
                            sx={{
                              px: 1.5,
                              py: 0.5,
                              borderRadius: '8px',
                              textTransform: 'none',
                              fontWeight: 600,
                              fontSize: '0.8125rem',
                              color: '#64748B',
                              borderColor: '#CBD5E1',
                              '&:hover': {
                                bgcolor: '#F8FAFC',
                                borderColor: '#94A3B8',
                                color: '#475569',
                              },
                            }}
                          >
                            Refresh List
                          </Button>
                        </Box>
                      </Grid>

                      {knowledgeGraphs.length === 0 ? (
                        <Grid item xs={12}>
                          <Paper
                            elevation={0}
                            sx={{
                              p: 3,
                              borderRadius: 1,
                              border: '1px solid #E5E7EB',
                              bgcolor: '#FFFFFF',
                              textAlign: 'center',
                            }}
                          >
                            <Box
                              sx={{
                                display: 'inline-flex',
                                p: 1.5,
                                borderRadius: '50%',
                                bgcolor: 'action.hover',
                                mb: 1,
                              }}
                            >
                              <AccountTree sx={{ fontSize: 36, color: 'text.secondary' }} />
                            </Box>
                            <Typography variant="body2" fontWeight="600" gutterBottom fontSize="0.85rem">
                              No Knowledge Graphs Found
                            </Typography>
                            <Typography variant="caption" color="text.secondary" sx={{ mb: 1.5 }} fontSize="0.75rem">
                              No knowledge graphs available. Create one to get started.
                            </Typography>
                          </Paper>
                        </Grid>
                      ) : (
                        knowledgeGraphs.map((kg) => (
                          <Grid item xs={12} md={6} lg={4} key={kg.name}>
                            <Card
                              elevation={0}
                              sx={{
                                height: '100%',
                                borderRadius: 1,
                                border: '1px solid #E5E7EB',
                                bgcolor: '#FFFFFF',
                              }}
                            >
                              <CardContent sx={{ p: 1.5 }}>
                                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 1 }}>
                                  <Box
                                    sx={{
                                      p: 0.75,
                                      borderRadius: 1,
                                      backgroundColor: '#5B6FE5',
                                      display: 'flex',
                                      alignItems: 'center',
                                      justifyContent: 'center',
                                    }}
                                  >
                                    <Hub sx={{ color: 'white', fontSize: 18 }} />
                                  </Box>
                                  <Box sx={{ flex: 1, minWidth: 0 }}>
                                    <Typography variant="body2" fontWeight="700" gutterBottom noWrap fontSize="0.85rem" sx={{ mb: 0.25 }}>
                                      {kg.name}
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary" fontSize="0.65rem">
                                      {kg.created_at ? new Date(kg.created_at).toLocaleString('en-US', {
                                        year: 'numeric',
                                        month: 'short',
                                        day: 'numeric',
                                        hour: '2-digit',
                                        minute: '2-digit',
                                        timeZoneName: 'short'
                                      }) : 'Unknown date'}
                                    </Typography>
                                  </Box>
                                </Box>

                                <Box sx={{ mb: 1.5, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                  {kg.backends?.map((backend) => (
                                    <Chip
                                      key={backend}
                                      label={backend}
                                      size="small"
                                      sx={{
                                        fontWeight: 600,
                                        fontSize: '0.65rem',
                                        height: 20,
                                        bgcolor: 'rgba(102, 126, 234, 0.1)',
                                        color: '#667eea',
                                        borderRadius: 0.75,
                                      }}
                                    />
                                  ))}
                                </Box>

                                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                                  <Button
                                    fullWidth
                                    variant="contained"
                                    size="small"
                                    startIcon={<Visibility sx={{ fontSize: 16 }} />}
                                    onClick={() => handleLoadKG(kg.name)}
                                    sx={{
                                      px: 2,
                                      py: 0.5,
                                      borderRadius: '8px',
                                      textTransform: 'none',
                                      fontWeight: 600,
                                      fontSize: '0.8125rem',
                                      bgcolor: '#5B6FE5',
                                      boxShadow: '0 1px 3px 0 rgba(91, 111, 229, 0.2)',
                                      '&:hover': {
                                        bgcolor: '#4A5FD4',
                                        boxShadow: '0 2px 6px 0 rgba(91, 111, 229, 0.3)',
                                      },
                                    }}
                                  >
                                    View Graph
                                  </Button>
                                  <Box sx={{ display: 'flex', gap: 0.75 }}>
                                    <Button
                                      fullWidth
                                      size="small"
                                      variant="outlined"
                                      startIcon={<Download sx={{ fontSize: 16 }} />}
                                      onClick={() => handleExport(kg.name)}
                                      sx={{
                                        px: 1.5,
                                        py: 0.5,
                                        borderRadius: '8px',
                                        textTransform: 'none',
                                        fontWeight: 600,
                                        fontSize: '0.8125rem',
                                        color: '#64748B',
                                        borderColor: '#CBD5E1',
                                        '&:hover': {
                                          bgcolor: '#F8FAFC',
                                          borderColor: '#94A3B8',
                                          color: '#475569',
                                        },
                                      }}
                                    >
                                      Export
                                    </Button>
                                    <Button
                                      fullWidth
                                      size="small"
                                      variant="outlined"
                                      color="error"
                                      startIcon={<Delete sx={{ fontSize: 16 }} />}
                                      onClick={() => handleDelete(kg.name)}
                                      sx={{
                                        px: 1.5,
                                        py: 0.5,
                                        borderRadius: '8px',
                                        textTransform: 'none',
                                        fontWeight: 600,
                                        fontSize: '0.8125rem',
                                      }}
                                    >
                                      Delete
                                    </Button>
                                  </Box>
                                </Box>
                              </CardContent>
                            </Card>
                          </Grid>
                        ))
                      )}
                    </Grid>
                  </Fade>
                )}

                {/* Tab 2: View */}
                {tabValue === 1 && (
                  <Fade in={tabValue === 1}>
                    <Grid
                      container
                      spacing={1.5}
                      role="tabpanel"
                      id="tabpanel-1"
                      aria-labelledby="tab-1"
                    >
                      <Grid item xs={12}>


                        {selectedKG ? (
                          <>


                            {/* Force-Directed Graph Visualization */}
                            <Paper
                              elevation={0}
                              sx={{
                                p: 2,
                                borderRadius: 1,
                                mb: 2,
                                border: '1px solid #E5E7EB',
                                bgcolor: '#FFFFFF',
                              }}
                            >
                              <KnowledgeGraphEditor
                                kgName={selectedKG}
                                entities={kgEntities}
                                relationships={kgRelationships}
                                onRefresh={handleRefreshKG}
                              />
                            </Paper>
                          </>
                        ) : (
                          <Paper
                            elevation={0}
                            sx={{
                              p: 4,
                              borderRadius: 2,
                              border: '2px dashed',
                              borderColor: 'divider',
                              textAlign: 'center',
                              display: 'flex',
                              flexDirection: 'column',
                              alignItems: 'center',
                              justifyContent: 'center',
                              minHeight: 400,
                            }}
                          >
                            <Box
                              sx={{
                                display: 'inline-flex',
                                p: 2,
                                borderRadius: '50%',
                                bgcolor: 'action.hover',
                                mb: 2,
                              }}
                            >
                              <AccountTree sx={{ fontSize: 48, color: 'text.secondary' }} />
                            </Box>
                            <Typography variant="h6" fontWeight="700" gutterBottom sx={{ mb: 1 }}>
                              No Knowledge Graph Selected
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 3, maxWidth: 400 }}>
                              Select a knowledge graph from the "Manage KGs" tab to view its details.
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', justifyContent: 'center' }}>
                              <Button
                                variant="outlined"
                                startIcon={<AccountTree sx={{ fontSize: 18 }} />}
                                onClick={() => setTabValue(0)}
                                sx={{
                                  px: 1.5,
                                  py: 0.5,
                                  borderRadius: '8px',
                                  textTransform: 'none',
                                  fontWeight: 600,
                                  fontSize: '0.8125rem',
                                  color: '#64748B',
                                  borderColor: '#CBD5E1',
                                  '&:hover': {
                                    bgcolor: '#F8FAFC',
                                    borderColor: '#94A3B8',
                                    color: '#475569',
                                  },
                                }}
                              >
                                Manage KGs
                              </Button>
                            </Box>
                          </Paper>
                        )}
                      </Grid>
                    </Grid>
                  </Fade>
                )}
              </Box>

              {/* Overlay Loader */}
              <Backdrop
                sx={{
                  color: '#fff',
                  zIndex: (theme) => theme.zIndex.drawer + 1,
                  backdropFilter: 'blur(4px)',
                  backgroundColor: 'rgba(0, 0, 0, 0.7)',
                }}
                open={loading}
              >
                <Box
                  sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: 2,
                  }}
                >
                  <CircularProgress
                    size={60}
                    thickness={4}
                    sx={{
                      color: '#5B6FE5',
                    }}
                  />
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h6" fontWeight="600" sx={{ mb: 0.5 }}>
                      Generating Knowledge Graph...
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      This may take a few moments
                    </Typography>
                  </Box>
                </Box>
              </Backdrop>
            </Paper>
          </Box>
        </Fade>
      </Container>
    </Box>
  );
}
