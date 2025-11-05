import React from 'react';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  Alert
} from '@mui/material';
import { OpenInNew as OpenInNewIcon } from '@mui/icons-material';

function HintsSearch({ searchResults, onSelectColumn }) {
  if (!searchResults || searchResults.length === 0) {
    return (
      <Box textAlign="center" py={4}>
        <Typography variant="h6" color="text.secondary">
          No search results
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Try searching for business names, aliases, or common terms
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Alert severity="info" sx={{ mb: 2 }}>
        Found {searchResults.length} matching columns
      </Alert>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Table</strong></TableCell>
              <TableCell><strong>Column</strong></TableCell>
              <TableCell><strong>Business Name</strong></TableCell>
              <TableCell><strong>Match Type</strong></TableCell>
              <TableCell><strong>Type</strong></TableCell>
              <TableCell><strong>Priority</strong></TableCell>
              <TableCell align="right"><strong>Actions</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {searchResults.map((result, index) => {
              const hints = result.hints || {};

              return (
                <TableRow key={index} hover>
                  <TableCell>{result.table_name}</TableCell>
                  <TableCell>
                    <Typography variant="body2" fontFamily="monospace">
                      {result.column_name}
                    </Typography>
                  </TableCell>
                  <TableCell>{hints.business_name || <em>Not set</em>}</TableCell>
                  <TableCell>
                    <Chip
                      label={result.match_type}
                      size="small"
                      color={
                        result.match_type === 'business_name' ? 'primary' :
                        result.match_type === 'alias' ? 'success' :
                        'default'
                      }
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={hints.semantic_type || 'attribute'}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={hints.priority || 'medium'}
                      size="small"
                      color={
                        hints.priority === 'high' ? 'error' :
                        hints.priority === 'medium' ? 'warning' :
                        'default'
                      }
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Button
                      size="small"
                      startIcon={<OpenInNewIcon />}
                      onClick={() => onSelectColumn(result.table_name)}
                    >
                      View
                    </Button>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Expanded view of matches */}
      <Box mt={3}>
        {searchResults.map((result, index) => {
          const hints = result.hints || {};

          return (
            <Paper key={index} sx={{ p: 2, mb: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                {result.table_name}.{result.column_name}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {hints.description || 'No description'}
              </Typography>

              {hints.aliases && hints.aliases.length > 0 && (
                <Box mt={1}>
                  <Typography variant="caption" color="text.secondary">Aliases:</Typography>
                  <Box display="flex" gap={0.5} flexWrap="wrap" mt={0.5}>
                    {hints.aliases.map((alias, idx) => (
                      <Chip key={idx} label={alias} size="small" />
                    ))}
                  </Box>
                </Box>
              )}

              {hints.common_terms && hints.common_terms.length > 0 && (
                <Box mt={1}>
                  <Typography variant="caption" color="text.secondary">Common Terms:</Typography>
                  <Box display="flex" gap={0.5} flexWrap="wrap" mt={0.5}>
                    {hints.common_terms.map((term, idx) => (
                      <Chip key={idx} label={term} size="small" variant="outlined" />
                    ))}
                  </Box>
                </Box>
              )}
            </Paper>
          );
        })}
      </Box>
    </Box>
  );
}

export default HintsSearch;
