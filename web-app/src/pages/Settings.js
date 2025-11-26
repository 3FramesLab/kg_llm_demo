import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Alert,
  Snackbar,
  CircularProgress,
  Fade,
  Divider,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import {
  listDatabaseConnections,
  removeDatabaseConnection,
  listDatabasesFromConnection,
  testDatabaseConnection,
} from '../services/api';
import AddConnectionDialog from '../components/AddConnectionDialog';

/**
 * Settings Page Component
 * Manage data source connections
 */
function Settings() {
  const theme = useTheme();
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [databases, setDatabases] = useState({});

  useEffect(() => {
    loadConnections();
  }, []);

  const loadConnections = async () => {
    setLoading(true);
    try {
      const response = await listDatabaseConnections();
      const connectionsData = response.data.connections || [];
      setConnections(connectionsData);

      // Load databases for each connection (skip Excel connections)
      for (const conn of connectionsData) {
        if (conn.status === 'connected' && conn.type !== 'excel') {
          loadDatabasesForConnection(conn.id);
        }
      }
    } catch (error) {
      console.error('Error loading connections:', error);
      showSnackbar('Error loading connections', 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadDatabasesForConnection = async (connectionId) => {
    try {
      const response = await listDatabasesFromConnection(connectionId);
      setDatabases((prev) => ({
        ...prev,
        [connectionId]: response.data.databases || [],
      }));
    } catch (error) {
      console.error(`Error loading databases for connection ${connectionId}:`, error);
    }
  };

  const handleTestConnection = async (connection) => {
    try {
      const testPayload = {
        name: connection.name,
        type: connection.type,
        host: connection.host,
        port: connection.port,
        database: connection.database,
        username: connection.username,
        password: connection.password,
        service_name: connection.service_name || '',
      };

      const response = await testDatabaseConnection(testPayload);
      if (response.data.success) {
        showSnackbar('Connection test successful!', 'success');
      } else {
        showSnackbar('Connection test failed: ' + (response.data.message || 'Unknown error'), 'error');
      }
    } catch (error) {
      showSnackbar('Error testing connection: ' + (error.response?.data?.detail || error.message), 'error');
    }
  };

  const handleRemoveConnection = async (connectionId) => {
    try {
      await removeDatabaseConnection(connectionId);
      showSnackbar('Connection removed successfully!', 'success');
      loadConnections();
    } catch (error) {
      showSnackbar('Error removing connection: ' + (error.response?.data?.detail || error.message), 'error');
    }
  };

  const showSnackbar = (message, severity) => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const getStatusChip = (status) => {
    if (status === 'connected') {
      return <Chip icon={<CheckCircleIcon />} label="Connected" color="success" size="small" />;
    }
    return <Chip icon={<ErrorIcon />} label="Disconnected" color="error" size="small" />;
  };

  return (
    <Box sx={{ p: 2 }}>
      <Container maxWidth="auto" disableGutters>
        {/* Settings Page with Enhanced Animation */}
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
                  Settings
                </Typography>

                <Typography
                  variant="body2"
                  sx={{
                    color: '#6B7280',
                    fontSize: '0.875rem',
                    lineHeight: 1.5,
                  }}
                >
                  Manage your data source connections
                </Typography>
              </Box>
              <Divider sx={{ mb: 3 }} />

              {/* Connections Section */}
              <Box
                sx={{
                  flex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                }}
              >
                {/* Add Connection Button */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography
                    variant="subtitle2"
                    sx={{
                      fontWeight: 600,
                      color: '#1F2937',
                      fontSize: '0.875rem',
                    }}
                  >
                    Data Source Connections
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => setDialogOpen(true)}
                    size="small"
                  >
                    Add New Connection
                  </Button>
                </Box>

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
                  {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flex: 1 }}>
                      <CircularProgress size={32} sx={{ color: '#5B6FE5' }} />
                    </Box>
                  ) : connections.length === 0 ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flex: 1 }}>
                      <Alert
                        severity="info"
                        sx={{
                          py: 1.5,
                          bgcolor: '#E8F4FD',
                          color: '#1F2937',
                          border: '1px solid #BFDBFE',
                          '& .MuiAlert-icon': {
                            color: '#3B82F6',
                          },
                        }}
                      >
                        No connections configured yet. Click <strong>"Add New Connection"</strong> to get started.
                      </Alert>
                    </Box>
                  ) : (
                    <TableContainer sx={{ flex: 1, overflow: 'auto' }}>
                      <Table>
                        <TableHead>
                          <TableRow sx={{ bgcolor: '#F9FAFB' }}>
                            <TableCell sx={{ fontWeight: 600, color: '#1F2937', fontSize: '0.875rem', py: 0.75 }}>Connection Name</TableCell>
                            <TableCell sx={{ fontWeight: 600, color: '#1F2937', fontSize: '0.875rem', py: 0.75 }}>Type</TableCell>
                            <TableCell sx={{ fontWeight: 600, color: '#1F2937', fontSize: '0.875rem', py: 0.75 }}>Host</TableCell>
                            <TableCell sx={{ fontWeight: 600, color: '#1F2937', fontSize: '0.875rem', py: 0.75 }}>Status</TableCell>
                            <TableCell sx={{ fontWeight: 600, color: '#1F2937', fontSize: '0.875rem', py: 0.75 }}>Databases</TableCell>
                            <TableCell sx={{ fontWeight: 600, color: '#1F2937', fontSize: '0.875rem', py: 0.75 }} align="right">Actions</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {connections.map((connection) => (
                            <TableRow key={connection.id} sx={{ '&:hover': { bgcolor: '#F3F4F6' } }}>
                              <TableCell sx={{ color: '#1F2937', fontSize: '0.875rem', py: 0.75 }}>{connection.name}</TableCell>
                              <TableCell sx={{ color: '#6B7280', fontSize: '0.875rem', py: 0.75 }}>{connection.type.toUpperCase()}</TableCell>
                              <TableCell sx={{ color: '#6B7280', fontSize: '0.875rem', py: 0.75 }}>{connection.host}</TableCell>
                              <TableCell sx={{ py: 0.75 }}>{getStatusChip(connection.status)}</TableCell>
                              <TableCell sx={{ color: '#6B7280', fontSize: '0.875rem', py: 0.75 }}>
                                {databases[connection.id]?.length || 0}
                              </TableCell>
                              <TableCell align="right" sx={{ py: 0.75 }}>
                                {/* Only show Test Connection and Refresh for database connections, not Excel */}
                                {connection.type !== 'excel' && (
                                  <>
                                    <IconButton
                                      size="small"
                                      onClick={() => handleTestConnection(connection)}
                                      title="Test Connection"
                                      sx={{
                                        p: 0.5,
                                        color: '#3B82F6',
                                        '&:hover': {
                                          bgcolor: '#DBEAFE',
                                          color: '#1E40AF',
                                        },
                                      }}
                                    >
                                      <CheckCircleIcon fontSize="small" />
                                    </IconButton>
                                    <IconButton
                                      size="small"
                                      onClick={() => loadDatabasesForConnection(connection.id)}
                                      title="Refresh"
                                      sx={{
                                        p: 0.5,
                                        color: '#6B7280',
                                        '&:hover': {
                                          bgcolor: '#F3F4F6',
                                          color: '#1F2937',
                                        },
                                      }}
                                    >
                                      <RefreshIcon fontSize="small" />
                                    </IconButton>
                                  </>
                                )}
                                <IconButton
                                  size="small"
                                  onClick={() => handleRemoveConnection(connection.id)}
                                  title="Remove"
                                  sx={{
                                    p: 0.5,
                                    color: '#EF4444',
                                    '&:hover': {
                                      bgcolor: '#FEE2E2',
                                    },
                                  }}
                                >
                                  <DeleteIcon fontSize="small" />
                                </IconButton>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  )}
                </Box>
              </Box>

              {/* Action Buttons - Compact Design */}
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'flex-end',
                  mt: 1.5,
                  pt: 1,
                }}
              >
                <Button
                  onClick={loadConnections}
                  variant="outlined"
                  size="small"
                >
                  ↻ Refresh All
                </Button>
              </Box>
            </Paper>
          </Box>
        </Fade>
      </Container>

      {/* Add Connection Dialog */}
      <AddConnectionDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onConnectionAdded={loadConnections}
        onShowSnackbar={showSnackbar}
      />

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default Settings;

