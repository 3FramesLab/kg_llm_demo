import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
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
        knowledgeGraphs: kgsRes.data.count || 0,
      });
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container sx={{ p: 2 }}>
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
              display: 'flex',
              alignItems: 'center',
              gap: 1,
            }}
          >
            <DashboardIcon sx={{ fontSize: '1.5rem' }} />
            Overview
          </Typography>

          <Typography
            variant="body2"
            sx={{
              color: '#6B7280',
              fontSize: '0.875rem',
              lineHeight: 1.5,
            }}
          >
            Overview of Data Quality System Status and Statistics.
          </Typography>
        </Box>
        <Box sx={{ borderBottom: '1px solid #E5E7EB', mb: 2 }} />

        {/* System Health & LLM Status */}
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={12} md={6}>
            <Paper
              elevation={0}
              sx={{
                p: 1.5,
                borderRadius: 1.5,
                border: '1px solid #E5E7EB',
                height: '100%',
                transition: 'all 0.2s ease',
                '&:hover': {
                  boxShadow: '0 2px 6px rgba(91, 111, 229, 0.1)',
                  transform: 'translateY(-1px)',
                },
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
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
                  <Speed sx={{ color: 'white', fontSize: 20 }} />
                </Box>
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 600,
                    fontSize: '1rem',
                    color: '#1F2937',
                  }}
                >
                  System Health
                </Typography>
              </Box>

              {loading ? (
                <Box>
                  <Skeleton variant="text" width="60%" height={32} sx={{ mb: 1 }} />
                  <Skeleton variant="rectangular" width="100%" height={50} sx={{ borderRadius: 1 }} />
                </Box>
              ) : health ? (
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    {health.status === 'healthy' ? (
                      <CheckCircle
                        sx={{
                          mr: 1,
                          fontSize: 20,
                          color: '#10b981',
                          animation: 'pulse 2s ease-in-out infinite',
                          '@keyframes pulse': {
                            '0%, 100%': { opacity: 1 },
                            '50%': { opacity: 0.6 },
                          },
                        }}
                      />
                    ) : (
                      <Error sx={{ mr: 1, fontSize: 20, color: '#f87171' }} />
                    )}
                    <Typography
                      variant="body1"
                      sx={{
                        fontWeight: 600,
                        fontSize: '0.875rem',
                        color: '#1F2937',
                      }}
                    >
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
                p: 1.5,
                borderRadius: 1.5,
                border: '1px solid #E5E7EB',
                height: '100%',
                transition: 'all 0.2s ease',
                '&:hover': {
                  boxShadow: '0 2px 6px rgba(91, 111, 229, 0.1)',
                  transform: 'translateY(-1px)',
                },
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
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
                  <TrendingUp sx={{ color: 'white', fontSize: 20 }} />
                </Box>
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 600,
                    fontSize: '1rem',
                    color: '#1F2937',
                  }}
                >
                  LLM Status
                </Typography>
              </Box>

              {loading ? (
                <Box>
                  <Skeleton variant="rectangular" width="100%" height={50} sx={{ borderRadius: 1, mb: 1 }} />
                  <Skeleton variant="text" width="80%" height={24} />
                  <Skeleton variant="text" width="60%" height={24} />
                </Box>
              ) : llmStatus ? (
                <Box>
                  {llmStatus.enabled ? (
                    <Alert
                      severity="success"
                      icon={<CheckCircle sx={{ fontSize: 18, color: '#10b981' }} />}
                      sx={{
                        mb: 1,
                        py: 0.5,
                        borderRadius: 1,
                        fontWeight: 600,
                        fontSize: '0.8125rem',
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

        {/* Statistics Cards */}
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Paper
              elevation={0}
              sx={{
                p: 1.5,
                borderRadius: 1.5,
                border: '1px solid #E5E7EB',
                transition: 'all 0.2s ease',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: '0 2px 6px rgba(91, 111, 229, 0.15)',
                },
              }}
            >
              {loading ? (
                <Box>
                  <Skeleton variant="circular" width={44} height={44} sx={{ mb: 1 }} />
                  <Skeleton variant="text" width="50%" height={40} />
                  <Skeleton variant="text" width="80%" height={20} />
                </Box>
              ) : (
                <>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Box
                      sx={{
                        p: 1,
                        borderRadius: 1,
                        backgroundColor: '#5B6FE5',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mr: 1.5,
                      }}
                    >
                      <Storage sx={{ color: 'white', fontSize: 22 }} />
                    </Box>
                    <Box>
                      <Typography
                        variant="h6"
                        sx={{
                          fontWeight: 700,
                          fontSize: '1.5rem',
                          color: '#5B6FE5',
                          lineHeight: 1.2,
                        }}
                      >
                        {stats.schemas}
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{
                          fontSize: '0.875rem',
                          color: '#6B7280',
                          fontWeight: 600,
                        }}
                      >
                        Schemas
                      </Typography>
                    </Box>
                  </Box>
                  <Typography
                    variant="body2"
                    sx={{
                      fontSize: '0.8125rem',
                      color: '#6B7280',
                    }}
                  >
                    Available database schemas for analysis
                  </Typography>
                </>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper
              elevation={0}
              sx={{
                p: 1.5,
                borderRadius: 1.5,
                border: '1px solid #E5E7EB',
                transition: 'all 0.2s ease',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: '0 2px 6px rgba(91, 111, 229, 0.15)',
                },
              }}
            >
              {loading ? (
                <Box>
                  <Skeleton variant="circular" width={44} height={44} sx={{ mb: 1 }} />
                  <Skeleton variant="text" width="60%" height={32} />
                  <Skeleton variant="text" width="80%" height={18} />
                </Box>
              ) : (
                <>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Box
                      sx={{
                        p: 1,
                        borderRadius: 1,
                        backgroundColor: '#5B6FE5',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mr: 1.5,
                      }}
                    >
                      <AccountTree sx={{ color: 'white', fontSize: 22 }} />
                    </Box>
                    <Box>
                      <Typography
                        variant="h6"
                        sx={{
                          fontWeight: 700,
                          fontSize: '1.5rem',
                          color: '#5B6FE5',
                          lineHeight: 1.2,
                        }}
                      >
                        {stats.knowledgeGraphs}
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{
                          fontSize: '0.875rem',
                          color: '#6B7280',
                          fontWeight: 600,
                        }}
                      >
                        Knowledge Graphs
                      </Typography>
                    </Box>
                  </Box>
                  <Typography
                    variant="body2"
                    sx={{
                      fontSize: '0.8125rem',
                      color: '#6B7280',
                    }}
                  >
                    Generated knowledge graphs from schemas
                  </Typography>
                </>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
}
