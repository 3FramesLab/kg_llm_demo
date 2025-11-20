import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Chip,
  IconButton,
  Typography,
  CircularProgress,
  Alert,
  Snackbar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import {
  listDatabaseConnections,
  removeDatabaseConnection,
  listDatabasesFromConnection,
} from '../../services/api';

/**
 * DatabaseConnectionsStep Component
 * Step 1: Sources - Select from existing database connections
 */
function DatabaseConnectionsStep({ connections, setConnections, onDataChange }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
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

  const handleNavigateToSettings = () => {
    navigate('/settings');
  };

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
          Sources
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
          Connect to your data sources to begin building your knowledge graph. Select from existing connections to extract entities and relationships across multiple sources.
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography
            variant="subtitle2"
            sx={{
              fontWeight: 600,
              color: '#1F2937',
              fontSize: '0.875rem',
            }}
          >
            Available Sources
          </Typography>
          <IconButton
            size="small"
            onClick={loadConnections}
            title="Refresh All Connections"
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
        </Box>
      </Box>

      {/* Info Alert about Settings Page */}
      <Alert
        severity="info"
        icon={<SettingsIcon />}
        sx={{
          display: 'flex', flexDirection: 'row', alignItems: 'center',
          py: 0.5,
          mb: 2,
          bgcolor: '#F0F9FF',
          color: '#1F2937',
          border: '1px solid #BFDBFE',
          '& .MuiAlert-icon': {
            color: '#3B82F6',
          },
        }}
      >
        Manage connections in the <strong>Settings</strong>.
        <Button
          size="small"
          onClick={handleNavigateToSettings}
          sx={{
            ml: 1,
            textTransform: 'none',
            fontWeight: 600,
            color: '#3B82F6',
            '&:hover': {
              bgcolor: 'rgba(59, 130, 246, 0.1)',
            },
          }}
        >
          Go to Settings →
        </Button>
      </Alert>

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
          No sources available. Please add a connection in the <strong>Settings page</strong> first.
        </Alert>
      ) : (
        <TableContainer sx={{ border: '1px solid #E5E7EB', borderRadius: 1 }}>
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
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

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

