import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Chip,
  Alert,
  Skeleton,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Storage,
  AccountTree,
  Dashboard as DashboardIcon,
  TrendingUp,
  Speed,
} from '@mui/icons-material';
import { checkHealth, checkLLMStatus, listSchemas, listKGs } from '../services/api';

export default function Overview() {
  const [health, setHealth] = useState(null);
  const [llmStatus, setLlmStatus] = useState(null);
  const [stats, setStats] = useState({
    schemas: 0,
    knowledgeGraphs: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [healthRes, llmRes, schemasRes, kgsRes] = await Promise.all([
        checkHealth(),
        checkLLMStatus(),
        listSchemas(),
        listKGs(),
      ]);

      setHealth(healthRes.data);
      setLlmStatus(llmRes.data);
      setStats({
        schemas: schemasRes.data.count || 0,
        knowledgeGraphs: kgsRes.data.graphs?.length || 0,
      });
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 1.5  }}>
      {/* Enhanced Gradient Header with Stats */}
      <Box
        sx={{
          mb: 2,
          p: 1.5,
          borderRadius: 2,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          boxShadow: '0 4px 20px rgba(102, 126, 234, 0.3)',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
          <DashboardIcon sx={{ fontSize: 28 }} />
          <Box>
            <Typography variant="h5" fontWeight="700" sx={{ mb: 0.25, lineHeight: 1.2, fontSize: '1.15rem' }}>
              Overview
            </Typography>
            <Typography variant="body2" fontSize="0.8rem" sx={{ opacity: 0.95, fontWeight: 400 }}>
              Overview of Data Quality System Status and Statistics.
            </Typography>
          </Box>
        </Box>

        {/* Stats Row in Header */}
        {!loading && (
          <Box sx={{ display: 'flex', gap: 3, mt: 1.5, flexWrap: 'wrap' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Storage sx={{ fontSize: 18 }} />
              <Box>
                <Typography variant="h6" fontWeight="600" sx={{ lineHeight: 1.2, fontSize: '0.9rem' }}>
                  {stats.schemas}
                </Typography>
                <Typography variant="caption" sx={{ opacity: 0.9, fontSize: '0.65rem' }}>
                  Schemas
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <AccountTree sx={{ fontSize: 18 }} />
              <Box>
                <Typography variant="h6" fontWeight="600" sx={{ lineHeight: 1.2, fontSize: '0.9rem' }}>
                  {stats.knowledgeGraphs}
                </Typography>
                <Typography variant="caption" sx={{ opacity: 0.9, fontSize: '0.65rem' }}>
                  Knowledge Graphs
                </Typography>
              </Box>
            </Box>
          </Box>
        )}
      </Box>



      {/* System Status */}
      <Box>
            {/* System Health & LLM Status */}
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} md={6}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: 'divider',
                    height: '100%',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                      transform: 'translateY(-2px)',
                    },
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
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
                      <Speed sx={{ color: 'white', fontSize: 22 }} />
                    </Box>
                    <Typography variant="h6" fontWeight="700" fontSize="0.95rem">
                      System Health
                    </Typography>
                  </Box>

                  {loading ? (
                    <Box>
                      <Skeleton variant="text" width="60%" height={40} sx={{ mb: 1.5 }} />
                      <Skeleton variant="rectangular" width="100%" height={60} sx={{ borderRadius: 1 }} />
                    </Box>
                  ) : health ? (
                    <Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                        {health.status === 'healthy' ? (
                          <CheckCircle
                            sx={{
                              mr: 1.5,
                              fontSize: 24,
                              color: '#10b981',
                              animation: 'pulse 2s ease-in-out infinite',
                              '@keyframes pulse': {
                                '0%, 100%': { opacity: 1 },
                                '50%': { opacity: 0.6 },
                              },
                            }}
                          />
                        ) : (
                          <Error sx={{ mr: 1.5, fontSize: 24, color: '#f87171' }} />
                        )}
                        <Typography variant="h6" fontWeight="600" fontSize="0.9rem">
                          Status: <span style={{ color: health.status === 'healthy' ? '#047857' : '#dc2626' }}>{health.status}</span>
                        </Typography>
                      </Box>
                      {/* Status chips hidden as requested */}
                      {/* <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.75 }}>
                        <Chip
                          label={`FalkorDB: ${health.falkordb_connected ? 'Connected' : 'Disconnected'}`}
                          size="medium"
                          sx={{
                            fontWeight: 600,
                            justifyContent: 'flex-start',
                            bgcolor: health.falkordb_connected ? '#f0fdf9' : '#fef8f8',
                            color: health.falkordb_connected ? '#047857' : '#dc2626',
                            border: `1px solid ${health.falkordb_connected ? '#d1fae5' : '#fee2e2'}`,
                          }}
                        />
                        <Chip
                          label={`Graphiti: ${health.graphiti_available ? 'Available' : 'Unavailable'}`}
                          size="medium"
                          sx={{
                            fontWeight: 600,
                            justifyContent: 'flex-start',
                            bgcolor: health.graphiti_available ? '#f0fdf9' : '#fffcf5',
                            color: health.graphiti_available ? '#047857' : '#d97706',
                            border: `1px solid ${health.graphiti_available ? '#d1fae5' : '#fed7aa'}`,
                          }}
                        />
                        <Chip
                          label={`LLM: ${health.llm_enabled ? 'Enabled' : 'Disabled'}`}
                          size="medium"
                          sx={{
                            fontWeight: 600,
                            justifyContent: 'flex-start',
                            bgcolor: health.llm_enabled ? '#f0fdf9' : '#fffcf5',
                            color: health.llm_enabled ? '#047857' : '#d97706',
                            border: `1px solid ${health.llm_enabled ? '#d1fae5' : '#fed7aa'}`,
                          }}
                        />
                      </Box> */}
                    </Box>
                  ) : null}
                </Paper>
              </Grid>

              <Grid item xs={12} md={6}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: 'divider',
                    height: '100%',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                      transform: 'translateY(-2px)',
                    },
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
                    <Box
                      sx={{
                        p: 1,
                        borderRadius: 1.5,
                        background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <TrendingUp sx={{ color: 'white', fontSize: 22 }} />
                    </Box>
                    <Typography variant="h6" fontWeight="700" fontSize="0.95rem">
                      LLM Status
                    </Typography>
                  </Box>

                  {loading ? (
                    <Box>
                      <Skeleton variant="rectangular" width="100%" height={60} sx={{ borderRadius: 1, mb: 1.5 }} />
                      <Skeleton variant="text" width="80%" height={30} />
                      <Skeleton variant="text" width="60%" height={30} />
                    </Box>
                  ) : llmStatus ? (
                    <Box>
                      {llmStatus.enabled ? (
                        <Alert
                          severity="success"
                          icon={<CheckCircle sx={{ fontSize: 20, color: '#10b981' }} />}
                          sx={{
                            mb: 1.5,
                            borderRadius: 1.5,
                            fontWeight: 600,
                            bgcolor: '#f0fdf9',
                            color: '#047857',
                            border: '1px solid #d1fae5',
                            '& .MuiAlert-message': {
                              color: '#047857',
                            },
                          }}
                        >
                          LLM features are enabled and operational
                        </Alert>
                      ) : (
                        <Alert
                          severity="warning"
                          icon={<Error sx={{ fontSize: 20, color: '#f59e0b' }} />}
                          sx={{
                            mb: 1.5,
                            borderRadius: 1.5,
                            fontWeight: 600,
                            bgcolor: '#fffcf5',
                            color: '#d97706',
                            border: '1px solid #fed7aa',
                            '& .MuiAlert-message': {
                              color: '#d97706',
                            },
                          }}
                        >
                          LLM features are disabled
                        </Alert>
                      )}
                      {/* Model and Features section hidden as requested */}
                      {/* {llmStatus.enabled && (
                        <Box>
                          <Typography variant="body2" fontSize="0.8rem" sx={{ mb: 1, fontWeight: 600 }}>
                            <strong>Model:</strong> {llmStatus.model}
                          </Typography>
                          <Typography variant="body2" fontSize="0.8rem" sx={{ mb: 0.75, fontWeight: 600 }}>
                            Features:
                          </Typography>
                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.75 }}>
                            {llmStatus.features?.extraction && (
                              <Chip
                                label="Entity Extraction"
                                size="medium"
                                sx={{
                                  fontWeight: 600,
                                  justifyContent: 'flex-start',
                                  bgcolor: '#eff6ff',
                                  color: '#1e40af',
                                  border: '1px solid #dbeafe',
                                }}
                              />
                            )}
                            {llmStatus.features?.analysis && (
                              <Chip
                                label="Schema Analysis"
                                size="medium"
                                sx={{
                                  fontWeight: 600,
                                  justifyContent: 'flex-start',
                                  bgcolor: '#eff6ff',
                                  color: '#1e40af',
                                  border: '1px solid #dbeafe',
                                }}
                              />
                            )}
                            {llmStatus.features?.enhancement && (
                              <Chip
                                label="Relationship Enhancement"
                                size="medium"
                                sx={{
                                  fontWeight: 600,
                                  justifyContent: 'flex-start',
                                  bgcolor: '#eff6ff',
                                  color: '#1e40af',
                                  border: '1px solid #dbeafe',
                                }}
                              />
                            )}
                          </Box>
                        </Box>
                      )} */}
                    </Box>
                  ) : null}
                </Paper>
              </Grid>
            </Grid>

            {/* Enhanced Statistics Cards */}
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Card
                  elevation={0}
                  sx={{
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: 'divider',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 8px 24px rgba(102, 126, 234, 0.25)',
                    },
                  }}
                >
                  <CardContent sx={{ p: 2 }}>
                    {loading ? (
                      <Box>
                        <Skeleton variant="circular" width={56} height={56} sx={{ mb: 1.5 }} />
                        <Skeleton variant="text" width="50%" height={40} />
                        <Skeleton variant="text" width="80%" height={20} />
                      </Box>
                    ) : (
                      <>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                          <Box
                            sx={{
                              p: 1.5,
                              borderRadius: 2,
                              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              mr: 2,
                            }}
                          >
                            <Storage sx={{ color: 'white', fontSize: 28 }} />
                          </Box>
                          <Box>
                            <Typography variant="h6" fontWeight="700" fontSize="1.5rem" sx={{ color: '#667eea' }}>
                              {stats.schemas}
                            </Typography>
                            <Typography variant="body2" fontSize="0.8rem" color="text.secondary" fontWeight="600">
                              Schemas
                            </Typography>
                          </Box>
                        </Box>
                        <Typography variant="body2" fontSize="0.8rem" color="text.secondary">
                          Available database schemas for analysis
                        </Typography>
                      </>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card
                  elevation={0}
                  sx={{
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: 'divider',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 8px 24px rgba(67, 233, 123, 0.25)',
                    },
                  }}
                >
                  <CardContent sx={{ p: 2 }}>
                    {loading ? (
                      <Box>
                        <Skeleton variant="circular" width={56} height={56} sx={{ mb: 1.5 }} />
                        <Skeleton variant="text" width="60%" height={40} />
                        <Skeleton variant="text" width="80%" height={20} />
                      </Box>
                    ) : (
                      <>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                          <Box
                            sx={{
                              p: 1.5,
                              borderRadius: 2,
                              background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              mr: 2,
                            }}
                          >
                            <AccountTree sx={{ color: 'white', fontSize: 28 }} />
                          </Box>
                          <Box>
                            <Typography variant="h6" fontWeight="700" fontSize="1.5rem" sx={{ color: '#43e97b' }}>
                              {stats.knowledgeGraphs}
                            </Typography>
                            <Typography variant="body2" fontSize="0.8rem" color="text.secondary" fontWeight="600">
                              Knowledge Graphs
                            </Typography>
                          </Box>
                        </Box>
                        <Typography variant="body2" fontSize="0.8rem" color="text.secondary">
                          Generated knowledge graphs from schemas
                        </Typography>
                      </>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
    </Container>
  );
}
