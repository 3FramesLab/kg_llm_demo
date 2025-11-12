import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Alert,
  Skeleton,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Storage,
  AccountTree,
  TrendingUp,
  Speed,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { checkHealth, checkLLMStatus, listSchemas, listKGs } from '../services/api';

// Reusable style constants
const GRADIENT_STYLES = {
  purple: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  green: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
};

const CARD_HOVER_EFFECT = {
  boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
  transform: 'translateY(-1px)',
};

const STAT_CARD_HOVER_EFFECT = {
  transform: 'translateY(-2px)',
};

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
    <Container sx={{ p: 0 }}>
      {/* Refresh Button */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1.5 }}>
        <Tooltip title="Refresh data">
          <IconButton
            onClick={loadDashboardData}
            disabled={loading}
            sx={{
              bgcolor: 'white',
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 1.5,
              '&:hover': {
                bgcolor: '#f3f4f6',
                borderColor: '#667eea',
              },
              '&:disabled': {
                bgcolor: '#f9fafb',
              },
            }}
          >
            <RefreshIcon
              sx={{
                fontSize: 20,
                color: loading ? '#9ca3af' : '#667eea',
                animation: loading ? 'spin 1s linear infinite' : 'none',
                '@keyframes spin': {
                  '0%': { transform: 'rotate(0deg)' },
                  '100%': { transform: 'rotate(360deg)' },
                },
              }}
            />
          </IconButton>
        </Tooltip>
      </Box>

      {/* System Status */}
      {/* System Health & LLM Status */}
      <Grid container spacing={1.5} sx={{ mb: 1.5 }}>
        <Grid item xs={12} md={6}>
          <Paper
            elevation={0}
            sx={{
              p: 1.25,
              borderRadius: 1,
              border: '1px solid',
              borderColor: 'divider',
              height: '100%',
              transition: 'all 0.2s ease',
              '&:hover': CARD_HOVER_EFFECT,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Box
                sx={{
                  p: 0.75,
                  borderRadius: 1,
                  background: GRADIENT_STYLES.purple,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Speed sx={{ color: 'white', fontSize: 18 }} />
              </Box>
              <Typography variant="h6" fontWeight="700" fontSize="0.875rem">
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
                  <Typography variant="body1" fontWeight="600" fontSize="0.875rem">
                    Status: <span style={{ color: health.status === 'healthy' ? '#047857' : '#dc2626' }}>{health.status}</span>
                  </Typography>
                </Box>
              </Box>
            ) : null}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper
            elevation={0}
            sx={{
              p: 1.25,
              borderRadius: 1,
              border: '1px solid',
              borderColor: 'divider',
              height: '100%',
              transition: 'all 0.2s ease',
              '&:hover': CARD_HOVER_EFFECT,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Box
                sx={{
                  p: 0.75,
                  borderRadius: 1,
                  background: GRADIENT_STYLES.green,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <TrendingUp sx={{ color: 'white', fontSize: 18 }} />
              </Box>
              <Typography variant="h6" fontWeight="700" fontSize="0.875rem">
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
              </Box>
            ) : null}
          </Paper>
        </Grid>
      </Grid>

      {/* Enhanced Statistics Cards */}
      <Grid container spacing={1.5}>
        <Grid item xs={12} md={6}>
          <Card
            elevation={0}
            sx={{
              borderRadius: 1,
              border: '1px solid',
              borderColor: 'divider',
              transition: 'all 0.2s ease',
              '&:hover': {
                ...STAT_CARD_HOVER_EFFECT,
                boxShadow: '0 4px 12px rgba(102, 126, 234, 0.15)',
              },
            }}
          >
            <CardContent sx={{ p: 1.25 }}>
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
                        background: GRADIENT_STYLES.purple,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mr: 1.5,
                      }}
                    >
                      <Storage sx={{ color: 'white', fontSize: 22 }} />
                    </Box>
                    <Box>
                      <Typography variant="h6" fontWeight="700" fontSize="1.25rem" sx={{ color: '#667eea' }}>
                        {stats.schemas}
                      </Typography>
                      <Typography variant="body2" fontSize="0.75rem" color="text.secondary" fontWeight="600">
                        Schemas
                      </Typography>
                    </Box>
                  </Box>
                  <Typography variant="body2" fontSize="0.75rem" color="text.secondary">
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
              borderRadius: 1,
              border: '1px solid',
              borderColor: 'divider',
              transition: 'all 0.2s ease',
              '&:hover': {
                ...STAT_CARD_HOVER_EFFECT,
                boxShadow: '0 4px 12px rgba(67, 233, 123, 0.15)',
              },
            }}
          >
            <CardContent sx={{ p: 1.25 }}>
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
                        background: GRADIENT_STYLES.green,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mr: 1.5,
                      }}
                    >
                      <AccountTree sx={{ color: 'white', fontSize: 22 }} />
                    </Box>
                    <Box>
                      <Typography variant="h6" fontWeight="700" fontSize="1.25rem" sx={{ color: '#43e97b' }}>
                        {stats.knowledgeGraphs}
                      </Typography>
                      <Typography variant="body2" fontSize="0.75rem" color="text.secondary" fontWeight="600">
                        Knowledge Graphs
                      </Typography>
                    </Box>
                  </Box>
                  <Typography variant="body2" fontSize="0.75rem" color="text.secondary">
                    Generated knowledge graphs from schemas
                  </Typography>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}
