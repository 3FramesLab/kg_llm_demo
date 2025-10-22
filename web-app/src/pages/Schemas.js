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
} from '@mui/material';
import { Refresh, Description } from '@mui/icons-material';
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
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Database Schemas
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Available database schemas for knowledge graph generation
        </Typography>
      </Box>

      <Box sx={{ mb: 2 }}>
        <Button
          variant="contained"
          startIcon={<Refresh />}
          onClick={loadSchemas}
          disabled={loading}
        >
          Refresh Schemas
        </Button>
      </Box>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Error loading schemas: {error}
        </Alert>
      )}

      {!loading && schemas.length === 0 && (
        <Alert severity="info">
          No schemas found. Place JSON schema files in the <code>schemas/</code> directory.
        </Alert>
      )}

      {!loading && schemas.length > 0 && (
        <Paper>
          <List>
            {schemas.map((schema, index) => (
              <ListItem
                key={index}
                divider={index < schemas.length - 1}
                secondaryAction={
                  <Chip
                    icon={<Description />}
                    label="JSON Schema"
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                }
              >
                <ListItemText
                  primary={
                    <Typography variant="h6" component="span">
                      {schema}
                    </Typography>
                  }
                  secondary={`Location: schemas/${schema}.json`}
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          About Database Schemas
        </Typography>
        <Typography variant="body2" paragraph>
          Database schemas define the structure of your databases including tables, columns, and
          relationships. These schemas are used to generate knowledge graphs and reconciliation
          rules.
        </Typography>
        <Typography variant="body2" paragraph>
          <strong>To add a new schema:</strong>
        </Typography>
        <ol>
          <li>
            <Typography variant="body2">
              Export your database schema as JSON format
            </Typography>
          </li>
          <li>
            <Typography variant="body2">
              Place the file in the <code>schemas/</code> directory
            </Typography>
          </li>
          <li>
            <Typography variant="body2">
              Refresh this page to see the new schema
            </Typography>
          </li>
          <li>
            <Typography variant="body2">
              Navigate to <strong>Knowledge Graph</strong> to generate a graph from the schema
            </Typography>
          </li>
        </ol>
      </Paper>
    </Container>
  );
}
