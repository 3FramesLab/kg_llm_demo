import { useState, useEffect, useRef } from 'react';
import {
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Button,
  Box,
  CircularProgress,
} from '@mui/material';
import { testDatabaseConnection, addDatabaseConnection } from '../services/api';

/**
 * AddConnectionDialog Component
 * Reusable dialog for adding new database connections
 */
function AddConnectionDialog({ open, onClose, onConnectionAdded, onShowSnackbar }) {
  const [loading, setLoading] = useState(false);
  const [testingConnection, setTestingConnection] = useState(false);
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
  const prevTypeRef = useRef(formData.type);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
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

  useEffect(() => {
    if (formData.type && formData.type !== prevTypeRef.current) {
      const defaultPort = getDefaultPort(formData.type);
      setFormData(prev => ({ ...prev, port: defaultPort }));
      prevTypeRef.current = formData.type;
    }
  }, [formData.type]);

  const handleTestConnection = async () => {
    setTestingConnection(true);
    try {
      const response = await testDatabaseConnection(formData);
      if (response.data.success) {
        onShowSnackbar('Connection successful!', 'success');
      } else {
        onShowSnackbar('Connection failed: ' + response.data.message, 'error');
      }
    } catch (error) {
      onShowSnackbar('Connection test failed: ' + (error.response?.data?.detail || error.message), 'error');
    } finally {
      setTestingConnection(false);
    }
  };

  const handleAddConnection = async () => {
    setLoading(true);
    try {
      const response = await addDatabaseConnection(formData);
      if (response.data.success) {
        onShowSnackbar('Connection added successfully!', 'success');
        handleClose();
        onConnectionAdded();
      }
    } catch (error) {
      onShowSnackbar('Error adding connection: ' + (error.response?.data?.detail || error.message), 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
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
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
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
          color: '#5B6FE5',
        }}
      >
        Add New Source Connection
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
              '& .MuiInputLabel-root': { fontSize: '0.875rem', color: '#6B7280' },
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: '#D1D5DB' },
                '&:hover fieldset': { borderColor: '#9CA3AF' },
                '&.Mui-focused fieldset': { borderColor: '#5B6FE5' },
              },
            }}
          />
          <FormControl fullWidth required size="small">
            <InputLabel sx={{ fontSize: '0.875rem', color: '#6B7280' }}>Source Type</InputLabel>
            <Select
              name="type"
              value={formData.type}
              onChange={handleInputChange}
              label="Source Type"
              sx={{
                '& .MuiOutlinedInput-root': {
                  '& fieldset': { borderColor: '#D1D5DB' },
                  '&:hover fieldset': { borderColor: '#9CA3AF' },
                  '&.Mui-focused fieldset': { borderColor: '#5B6FE5' },
                },
              }}
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
              '& .MuiInputLabel-root': { fontSize: '0.875rem', color: '#6B7280' },
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: '#D1D5DB' },
                '&:hover fieldset': { borderColor: '#9CA3AF' },
                '&.Mui-focused fieldset': { borderColor: '#5B6FE5' },
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
              '& .MuiInputLabel-root': { fontSize: '0.875rem', color: '#6B7280' },
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: '#D1D5DB' },
                '&:hover fieldset': { borderColor: '#9CA3AF' },
                '&.Mui-focused fieldset': { borderColor: '#5B6FE5' },
              },
            }}
          />
          <TextField
            label="Source Database Name"
            name="database"
            value={formData.database}
            onChange={handleInputChange}
            fullWidth
            required
            size="small"
            sx={{
              '& .MuiInputLabel-root': { fontSize: '0.875rem', color: '#6B7280' },
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: '#D1D5DB' },
                '&:hover fieldset': { borderColor: '#9CA3AF' },
                '&.Mui-focused fieldset': { borderColor: '#5B6FE5' },
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
              '& .MuiInputLabel-root': { fontSize: '0.875rem', color: '#6B7280' },
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: '#D1D5DB' },
                '&:hover fieldset': { borderColor: '#9CA3AF' },
                '&.Mui-focused fieldset': { borderColor: '#5B6FE5' },
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
              '& .MuiInputLabel-root': { fontSize: '0.875rem', color: '#6B7280' },
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: '#D1D5DB' },
                '&:hover fieldset': { borderColor: '#9CA3AF' },
                '&.Mui-focused fieldset': { borderColor: '#5B6FE5' },
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
                '& .MuiInputLabel-root': { fontSize: '0.875rem', color: '#6B7280' },
                '& .MuiOutlinedInput-root': {
                  '& fieldset': { borderColor: '#D1D5DB' },
                  '&:hover fieldset': { borderColor: '#9CA3AF' },
                  '&.Mui-focused fieldset': { borderColor: '#5B6FE5' },
                },
                '& .MuiFormHelperText-root': { fontSize: '0.75rem', color: '#6B7280' },
              }}
            />
          )}
        </Box>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2.5, pt: 1.5 }}>
        <Button
          onClick={handleClose}
          variant="outlined"
          size="small"
          sx={{
            px: 1.5,
            py: 0.5,
            minWidth: 'auto',
            color: '#64748B',
            borderColor: '#CBD5E1',
            fontSize: '0.8125rem',
            textTransform: 'none',
            borderRadius: '8px',
            '&:hover': {
              bgcolor: '#F8FAFC',
              borderColor: '#94A3B8',
              color: '#475569',
            },
          }}
        >
          Cancel
        </Button>
        <Button
          onClick={handleTestConnection}
          disabled={testingConnection}
          variant="outlined"
          startIcon={testingConnection ? <CircularProgress size={16} /> : null}
          size="small"
          sx={{
            px: 1.5,
            py: 0.5,
            minWidth: 'auto',
            color: '#64748B',
            borderColor: '#CBD5E1',
            fontSize: '0.8125rem',
            textTransform: 'none',
            borderRadius: '8px',
            '&:hover': {
              bgcolor: '#F8FAFC',
              borderColor: '#94A3B8',
              color: '#475569',
            },
            '&:disabled': {
              color: '#D1D5DB',
              borderColor: '#E5E7EB',
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
            px: 2,
            py: 0.5,
            minHeight: 'auto',
            bgcolor: '#5B6FE5',
            color: '#FFFFFF',
            fontSize: '0.8125rem',
            fontWeight: 500,
            textTransform: 'none',
            borderRadius: '8px',
            boxShadow: '0 1px 3px 0 rgba(91, 111, 229, 0.2)',
            '&:hover': {
              bgcolor: '#4C5FD5',
              boxShadow: '0 2px 6px 0 rgba(91, 111, 229, 0.3)',
            },
            '&:disabled': {
              bgcolor: '#E5E7EB',
              color: '#9CA3AF',
              boxShadow: 'none',
            },
          }}
        >
          {loading ? (
            <>
              <CircularProgress size={16} sx={{ color: '#FFFFFF', mr: 1 }} />
              Adding...
            </>
          ) : (
            'Add Connection'
          )}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default AddConnectionDialog;

