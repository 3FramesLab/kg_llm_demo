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
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Storage,
  AccountTree,
  CompareArrows,
} from '@mui/icons-material';
import { checkHealth, checkLLMStatus, listSchemas, listKGs, listRulesets } from '../services/api';

export default function Dashboard() {
  const [health, setHealth] = useState(null);
  const [llmStatus, setLlmStatus] = useState(null);
  const [stats, setStats] = useState({
    schemas: 0,
    knowledgeGraphs: 0,
    rulesets: 0,
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [healthRes, llmRes, schemasRes, kgsRes, rulesetsRes] = await Promise.all([
        checkHealth(),
        checkLLMStatus(),
        listSchemas(),
        listKGs(),
        listRulesets(),
      ]);

      setHealth(healthRes.data);
      setLlmStatus(llmRes.data);
      setStats({
        schemas: schemasRes.data.count || 0,
        knowledgeGraphs: kgsRes.data.graphs?.length || 0,
        rulesets: rulesetsRes.data.rulesets?.length || 0,
      });
    } catch (error) {
      console.error('Error loading dashboard:', error);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Overview of DQ-POC System Status and Statistics
        </Typography>
      </Box>

      {/* System Health */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              System Health
            </Typography>
            {health && (
              <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  {health.status === 'healthy' ? (
                    <CheckCircle color="success" sx={{ mr: 1 }} />
                  ) : (
                    <Error color="error" sx={{ mr: 1 }} />
                  )}
                  <Typography variant="body1">
                    Status: <strong>{health.status}</strong>
                  </Typography>
                </Box>
                <Box sx={{ mt: 2 }}>
                  <Chip
                    label={`FalkorDB: ${health.falkordb_connected ? 'Connected' : 'Disconnected'}`}
                    color={health.falkordb_connected ? 'success' : 'error'}
                    size="small"
                    sx={{ mr: 1, mb: 1 }}
                  />
                  <Chip
                    label={`Graphiti: ${health.graphiti_available ? 'Available' : 'Unavailable'}`}
                    color={health.graphiti_available ? 'success' : 'warning'}
                    size="small"
                    sx={{ mr: 1, mb: 1 }}
                  />
                  <Chip
                    label={`LLM: ${health.llm_enabled ? 'Enabled' : 'Disabled'}`}
                    color={health.llm_enabled ? 'success' : 'warning'}
                    size="small"
                    sx={{ mb: 1 }}
                  />
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              LLM Status
            </Typography>
            {llmStatus && (
              <Box>
                {llmStatus.enabled ? (
                  <Alert severity="success" sx={{ mb: 2 }}>
                    LLM features are enabled and operational
                  </Alert>
                ) : (
                  <Alert severity="warning" sx={{ mb: 2 }}>
                    LLM features are disabled
                  </Alert>
                )}
                {llmStatus.enabled && (
                  <Box>
                    <Typography variant="body2">
                      <strong>Model:</strong> {llmStatus.model}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Features:</strong>
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      {llmStatus.features?.extraction && (
                        <Chip label="Entity Extraction" size="small" sx={{ mr: 1, mb: 1 }} />
                      )}
                      {llmStatus.features?.analysis && (
                        <Chip label="Schema Analysis" size="small" sx={{ mr: 1, mb: 1 }} />
                      )}
                      {llmStatus.features?.enhancement && (
                        <Chip label="Relationship Enhancement" size="small" sx={{ mb: 1 }} />
                      )}
                    </Box>
                  </Box>
                )}
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Statistics */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Storage color="primary" sx={{ fontSize: 40, mr: 2 }} />
                <Box>
                  <Typography variant="h4">{stats.schemas}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Schemas
                  </Typography>
                </Box>
              </Box>
              <Typography variant="body2">
                Available database schemas for analysis
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AccountTree color="primary" sx={{ fontSize: 40, mr: 2 }} />
                <Box>
                  <Typography variant="h4">{stats.knowledgeGraphs}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Knowledge Graphs
                  </Typography>
                </Box>
              </Box>
              <Typography variant="body2">
                Generated knowledge graphs from schemas
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <CompareArrows color="primary" sx={{ fontSize: 40, mr: 2 }} />
                <Box>
                  <Typography variant="h4">{stats.rulesets}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Reconciliation Rulesets
                  </Typography>
                </Box>
              </Box>
              <Typography variant="body2">
                Generated reconciliation rulesets
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Quick Guide */}
      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Quick Start Guide
        </Typography>
        <Typography variant="body2" component="div">
          <ol>
            <li>
              <strong>Schemas:</strong> View and manage available database schemas
            </li>
            <li>
              <strong>Knowledge Graph:</strong> Generate knowledge graphs from schemas
            </li>
            <li>
              <strong>Natural Language:</strong> Add custom relationships using plain English
            </li>
            <li>
              <strong>Reconciliation:</strong> Generate rules for data matching
            </li>
            <li>
              <strong>Execution:</strong> Execute reconciliation rules and view results
            </li>
          </ol>
        </Typography>
      </Paper>
    </Container>
  );
}
