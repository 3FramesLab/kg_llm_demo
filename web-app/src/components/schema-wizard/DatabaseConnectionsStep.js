import { useState, useEffect, useRef } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  Grid,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
  CircularProgress,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import {
  testDatabaseConnection,
  addDatabaseConnection,
  listDatabaseConnections,
  removeDatabaseConnection,
  listDatabasesFromConnection,
} from '../../services/api';

/**
 * DatabaseConnectionsStep Component
 * Step 1: Manage database connections
 */
function DatabaseConnectionsStep({ connections, setConnections, onDataChange }) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [testingConnection, setTestingConnection] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [formData, setFormData] = useState({
    name: '',
    type: 'mysql',
    host: '',
    port: '',
    database: '',
    username: '',
    password: '',
    service_name: '',
  });
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
      onDataChange(connectionsData);
      
      // Load databases for each connection
      for (const conn of connectionsData) {
        if (conn.status === 'connected') {
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

  const handleOpenDialog = () => {
    setFormData({
      name: '',
      type: 'mysql',
      host: '',
      port: '',
      database: '',
      username: '',
      password: '',
      service_name: '',
    });
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleTestConnection = async () => {
    setTestingConnection(true);
    try {
      const response = await testDatabaseConnection(formData);
      if (response.data.success) {
        showSnackbar('Connection successful!', 'success');
      } else {
        showSnackbar('Connection failed: ' + response.data.message, 'error');
      }
    } catch (error) {
      showSnackbar('Connection test failed: ' + (error.response?.data?.detail || error.message), 'error');
    } finally {
      setTestingConnection(false);
    }
  };

  const handleAddConnection = async () => {
    setLoading(true);
    try {
      const response = await addDatabaseConnection(formData);
      if (response.data.success) {
        showSnackbar('Connection added successfully!', 'success');
        handleCloseDialog();
        loadConnections();
      }
    } catch (error) {
      showSnackbar('Error adding connection: ' + (error.response?.data?.detail || error.message), 'error');
    } finally {
      setLoading(false);
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

  const getDefaultPort = (type) => {
    const ports = {
      mysql: '3306',
      postgresql: '5432',
      oracle: '1521',
      sqlserver: '1433',
      mongodb: '27017',
    };
    return ports[type] || '';
  };

  // Track previous type to avoid infinite loop
  const prevTypeRef = useRef(formData.type);

  useEffect(() => {
    // Only update port if type actually changed (not on initial render or formData updates)
    if (formData.type && formData.type !== prevTypeRef.current) {
      const defaultPort = getDefaultPort(formData.type);
      setFormData(prev => ({ ...prev, port: defaultPort }));
      prevTypeRef.current = formData.type;
    }
  }, [formData.type]);

  return (
    <Box sx={{ bgcolor: '#FFFFFF', p: 2, borderRadius: 1.5 }}>
      <Box sx={{ mb: 2 }}>
        <Typography
          variant="h6"
          sx={{
            fontWeight: 600,
            fontSize: '1.125rem',
            color: '#1F2937',
            mb: 0.5,
          }}
        >
          Load Database Sources
        </Typography>
        <Typography
          variant="body2"
          sx={{
            color: '#6B7280',
            fontSize: '0.875rem',
            lineHeight: 1.5,
            mb: 1.5,
          }}
        >
          Connect to one or more database sources to build your knowledge graph. You can add multiple sources to create relationships across different databases.
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography
          variant="subtitle2"
          sx={{
            fontWeight: 600,
            color: '#1F2937',
            fontSize: '0.875rem',
          }}
        >
          Connected Sources
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleOpenDialog}
          size="small"
          sx={{
            px: 2.5,
            bgcolor: '#5B6FE5',
            textTransform: 'none',
            fontWeight: 500,
            fontSize: '0.875rem',
            borderRadius: '8px',
            '&:hover': {
              bgcolor: '#4C5FD5',
            },
          }}
        >
          New Connection
        </Button>
      </Box>

      {loading && connections.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress size={32} sx={{ color: '#5B6FE5' }} />
        </Box>
      ) : connections.length === 0 ? (
        <Alert
          severity="info"
          icon={<InfoIcon />}
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
          No database sources loaded yet. Click <strong>"New Connection"</strong> to add a source.
        </Alert>
      ) : (
        <Grid container spacing={2}>
          {connections.map((connection) => (
            <Grid item xs={12} md={6} key={connection.id}>
              <Card
                variant="outlined"
                sx={{
                  border: '1px solid #E5E7EB',
                  borderRadius: 1.5,
                  '&:hover': {
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  },
                }}
              >
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box sx={{ flex: 1 }}>
                      <Typography
                        variant="subtitle2"
                        sx={{
                          fontWeight: 600,
                          mb: 1,
                          color: '#1F2937',
                          fontSize: '0.9375rem',
                        }}
                      >
                        {connection.name}
                      </Typography>
                      <Typography
                        variant="caption"
                        display="block"
                        sx={{
                          mb: 0.5,
                          color: '#6B7280',
                          fontSize: '0.8125rem',
                        }}
                      >
                        <strong>Type:</strong> {connection.type.toUpperCase()}
                      </Typography>
                      <Typography
                        variant="caption"
                        display="block"
                        sx={{
                          mb: 0.5,
                          color: '#6B7280',
                          fontSize: '0.8125rem',
                        }}
                      >
                        <strong>Host:</strong> {connection.host}:{connection.port}
                      </Typography>
                      <Typography
                        variant="caption"
                        display="block"
                        sx={{
                          mb: 1,
                          color: '#6B7280',
                          fontSize: '0.8125rem',
                        }}
                      >
                        <strong>Database:</strong> {connection.database}
                      </Typography>
                      <Box>
                        <Chip
                          icon={connection.status === 'connected' ? <CheckCircleIcon /> : <ErrorIcon />}
                          label={connection.status === 'connected' ? 'Connected' : 'Disconnected'}
                          color={connection.status === 'connected' ? 'success' : 'error'}
                          size="small"
                          sx={{
                            height: 22,
                            fontSize: '0.75rem',
                            fontWeight: 500,
                          }}
                        />
                      </Box>
                      {databases[connection.id] && databases[connection.id].length > 0 && (
                        <Box sx={{ mt: 1 }}>
                          <Typography
                            variant="caption"
                            sx={{
                              color: '#6B7280',
                              fontSize: '0.75rem',
                            }}
                          >
                            Available Databases: {databases[connection.id].length}
                          </Typography>
                        </Box>
                      )}
                    </Box>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
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
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Add Connection Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 2,
          },
        }}
      >
        <DialogTitle
          sx={{
            pb: 1,
            pt: 2.5,
            px: 3,
            fontWeight: 600,
            fontSize: '1.125rem',
            color: '#1F2937',
          }}
        >
          Add New Database Connection
        </DialogTitle>
        <DialogContent sx={{ px: 3 }}>
          <Box sx={{ pt: 1.5, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Connection Name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              fullWidth
              required
              size="small"
              sx={{
                '& .MuiInputLabel-root': {
                  fontSize: '0.875rem',
                  color: '#6B7280',
                },
                '& .MuiOutlinedInput-root': {
                  '& fieldset': {
                    borderColor: '#D1D5DB',
                  },
                  '&:hover fieldset': {
                    borderColor: '#9CA3AF',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#5B6FE5',
                  },
                },
              }}
            />
            <FormControl
              fullWidth
              required
              size="small"
              sx={{
                '& .MuiInputLabel-root': {
                  fontSize: '0.875rem',
                  color: '#6B7280',
                },
                '& .MuiOutlinedInput-root': {
                  '& fieldset': {
                    borderColor: '#D1D5DB',
                  },
                  '&:hover fieldset': {
                    borderColor: '#9CA3AF',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#5B6FE5',
                  },
                },
              }}
            >
              <InputLabel>Database Type</InputLabel>
              <Select
                name="type"
                value={formData.type}
                onChange={handleInputChange}
                label="Database Type"
              >
                <MenuItem value="mysql">MySQL</MenuItem>
                <MenuItem value="postgresql">PostgreSQL</MenuItem>
                <MenuItem value="oracle">Oracle</MenuItem>
                <MenuItem value="sqlserver">SQL Server</MenuItem>
                <MenuItem value="mongodb">MongoDB</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Host"
              name="host"
              value={formData.host}
              onChange={handleInputChange}
              fullWidth
              required
              size="small"
              sx={{
                '& .MuiInputLabel-root': {
                  fontSize: '0.875rem',
                  color: '#6B7280',
                },
                '& .MuiOutlinedInput-root': {
                  '& fieldset': {
                    borderColor: '#D1D5DB',
                  },
                  '&:hover fieldset': {
                    borderColor: '#9CA3AF',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#5B6FE5',
                  },
                },
              }}
            />
            <TextField
              label="Port"
              name="port"
              value={formData.port}
              onChange={handleInputChange}
              fullWidth
              required
              size="small"
              sx={{
                '& .MuiInputLabel-root': {
                  fontSize: '0.875rem',
                  color: '#6B7280',
                },
                '& .MuiOutlinedInput-root': {
                  '& fieldset': {
                    borderColor: '#D1D5DB',
                  },
                  '&:hover fieldset': {
                    borderColor: '#9CA3AF',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#5B6FE5',
                  },
                },
              }}
            />
            <TextField
              label="Database Name"
              name="database"
              value={formData.database}
              onChange={handleInputChange}
              fullWidth
              required
              size="small"
              sx={{
                '& .MuiInputLabel-root': {
                  fontSize: '0.875rem',
                  color: '#6B7280',
                },
                '& .MuiOutlinedInput-root': {
                  '& fieldset': {
                    borderColor: '#D1D5DB',
                  },
                  '&:hover fieldset': {
                    borderColor: '#9CA3AF',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#5B6FE5',
                  },
                },
              }}
            />
            <TextField
              label="Username"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              fullWidth
              required
              size="small"
              sx={{
                '& .MuiInputLabel-root': {
                  fontSize: '0.875rem',
                  color: '#6B7280',
                },
                '& .MuiOutlinedInput-root': {
                  '& fieldset': {
                    borderColor: '#D1D5DB',
                  },
                  '&:hover fieldset': {
                    borderColor: '#9CA3AF',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#5B6FE5',
                  },
                },
              }}
            />
            <TextField
              label="Password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleInputChange}
              fullWidth
              required
              size="small"
              sx={{
                '& .MuiInputLabel-root': {
                  fontSize: '0.875rem',
                  color: '#6B7280',
                },
                '& .MuiOutlinedInput-root': {
                  '& fieldset': {
                    borderColor: '#D1D5DB',
                  },
                  '&:hover fieldset': {
                    borderColor: '#9CA3AF',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#5B6FE5',
                  },
                },
              }}
            />
            {formData.type === 'oracle' && (
              <TextField
                label="Service Name (Optional)"
                name="service_name"
                value={formData.service_name}
                onChange={handleInputChange}
                fullWidth
                size="small"
                helperText="Oracle service name (e.g., ORCLPDB). Leave empty to use SID."
                sx={{
                  '& .MuiInputLabel-root': {
                    fontSize: '0.875rem',
                    color: '#6B7280',
                  },
                  '& .MuiOutlinedInput-root': {
                    '& fieldset': {
                      borderColor: '#D1D5DB',
                    },
                    '&:hover fieldset': {
                      borderColor: '#9CA3AF',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#5B6FE5',
                    },
                  },
                  '& .MuiFormHelperText-root': {
                    fontSize: '0.75rem',
                    color: '#6B7280',
                  },
                }}
              />
            )}
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2.5, pt: 1.5 }}>
          <Button
            onClick={handleCloseDialog}
            size="small"
            sx={{
              color: '#6B7280',
              textTransform: 'none',
              fontWeight: 500,
              borderRadius: '8px',
              '&:hover': {
                bgcolor: '#F3F4F6',
              },
            }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleTestConnection}
            disabled={testingConnection}
            startIcon={testingConnection ? <CircularProgress size={16} /> : null}
            size="small"
            sx={{
              color: '#6B7280',
              textTransform: 'none',
              fontWeight: 500,
              borderRadius: '8px',
              '&:hover': {
                bgcolor: '#F3F4F6',
              },
            }}
          >
            Test Connection
          </Button>
          <Button
            onClick={handleAddConnection}
            variant="contained"
            disabled={loading || !formData.name || !formData.host}
            size="small"
            sx={{
              bgcolor: '#5B6FE5',
              textTransform: 'none',
              fontWeight: 500,
              borderRadius: '8px',
              '&:hover': {
                bgcolor: '#4C5FD5',
              },
              '&:disabled': {
                bgcolor: '#D1D5DB',
                color: '#9CA3AF',
              },
            }}
          >
            Add Connection
          </Button>
        </DialogActions>
      </Dialog>

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

export default DatabaseConnectionsStep;

