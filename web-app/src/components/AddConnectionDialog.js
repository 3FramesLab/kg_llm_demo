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
  Typography,
  IconButton,
  Alert,
  LinearProgress,
  alpha,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Description as DescriptionIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { testDatabaseConnection, addDatabaseConnection, uploadExcelFile } from '../services/api';

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
    workspace_url: '',
    http_path: '',
    access_token: '',
  });
  const prevTypeRef = useRef(formData.type);

  // Excel upload state
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);

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
      databricks: '443',
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
      workspace_url: '',
      http_path: '',
      access_token: '',
    });
    setSelectedFile(null);
    setUploadLoading(false);
    // Reset file input
    const fileInput = document.getElementById('excel-file-input-dialog');
    if (fileInput) fileInput.value = '';
    onClose();
  };

  // Excel file upload handlers
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (!file) {
      setSelectedFile(null);
      return;
    }

    // Validate file type
    const validTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
      'application/vnd.ms-excel', // .xls
    ];
    const validExtensions = ['.xlsx', '.xls'];
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

    if (!validTypes.includes(file.type) && !validExtensions.includes(fileExtension)) {
      onShowSnackbar('Invalid file type. Please select an Excel file (.xlsx or .xls)', 'error');
      event.target.value = ''; // Reset input
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      onShowSnackbar('Please select a file to upload', 'warning');
      return;
    }

    if (!formData.name.trim()) {
      onShowSnackbar('Please enter a connection name', 'warning');
      return;
    }

    setUploadLoading(true);
    try {
      // Create FormData for file upload
      const uploadFormData = new FormData();
      uploadFormData.append('file', selectedFile);
      uploadFormData.append('name', formData.name.trim());

      // Make API call to upload Excel file
      const response = await uploadExcelFile(uploadFormData);

      if (response.data && response.data.success) {
        onShowSnackbar(response.data.message || 'Excel file uploaded successfully!', 'success');
        handleClose();
        onConnectionAdded();
      } else {
        onShowSnackbar(response.data?.message || 'Failed to upload Excel file', 'error');
      }
    } catch (error) {
      console.error('Error uploading Excel file:', error);
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || error.message;
      onShowSnackbar('Error uploading Excel file: ' + errorMessage, 'error');
    } finally {
      setUploadLoading(false);
    }
  };

  const handleClearFile = () => {
    setSelectedFile(null);
    const fileInput = document.getElementById('excel-file-input-dialog');
    if (fileInput) fileInput.value = '';
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
          />
          <FormControl fullWidth required>
            <InputLabel>Source Type</InputLabel>
            <Select
              name="type"
              value={formData.type}
              onChange={handleInputChange}
              label="Source Type"
            >
              <MenuItem value="mysql">MySQL</MenuItem>
              <MenuItem value="postgresql">PostgreSQL</MenuItem>
              <MenuItem value="oracle">Oracle</MenuItem>
              <MenuItem value="sqlserver">SQL Server</MenuItem>
              <MenuItem value="databricks">Databricks</MenuItem>
              <MenuItem value="excel">Excel</MenuItem>
            </Select>
          </FormControl>

          {/* Conditional rendering based on source type */}
          {formData.type === 'excel' ? (
            // Excel Upload UI
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
              {/* File Input Section */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                <input
                  accept=".xlsx,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel"
                  style={{ display: 'none' }}
                  id="excel-file-input-dialog"
                  type="file"
                  onChange={handleFileSelect}
                  disabled={uploadLoading}
                />
                <label htmlFor="excel-file-input-dialog">
                  <Button
                    variant="outlined"
                    component="span"
                    startIcon={<DescriptionIcon />}
                    disabled={uploadLoading}
                    size="small"
                    sx={{
                      borderColor: '#E5E7EB',
                      color: '#1F2937',
                      '&:hover': {
                        borderColor: '#5B6FE5',
                        bgcolor: alpha('#5B6FE5', 0.04),
                      },
                    }}
                  >
                    Choose File
                  </Button>
                </label>

                {/* Selected File Display */}
                {selectedFile && (
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1,
                      px: 1.5,
                      py: 0.75,
                      bgcolor: '#FFFFFF',
                      border: '1px solid #E5E7EB',
                      borderRadius: 1,
                      flex: 1,
                      minWidth: 200,
                    }}
                  >
                    <DescriptionIcon sx={{ fontSize: 18, color: '#5B6FE5' }} />
                    <Typography
                      variant="body2"
                      sx={{
                        color: '#1F2937',
                        fontSize: '0.875rem',
                        flex: 1,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {selectedFile.name}
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{
                        color: '#6B7280',
                        fontSize: '0.75rem',
                      }}
                    >
                      ({(selectedFile.size / 1024).toFixed(1)} KB)
                    </Typography>
                    <IconButton
                      size="small"
                      onClick={handleClearFile}
                      disabled={uploadLoading}
                      sx={{
                        p: 0.5,
                        color: '#6B7280',
                        '&:hover': {
                          bgcolor: '#F3F4F6',
                          color: '#EF4444',
                        },
                      }}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Box>
                )}
              </Box>

              {/* Upload Progress */}
              {uploadLoading && (
                <Box sx={{ width: '100%' }}>
                  <LinearProgress
                    sx={{
                      bgcolor: '#E5E7EB',
                      '& .MuiLinearProgress-bar': {
                        bgcolor: '#5B6FE5',
                      },
                    }}
                  />
                </Box>
              )}

              {/* Help Text */}
              <Alert
                severity="info"
                sx={{
                  py: 0.75,
                  bgcolor: '#E8F4FD',
                  color: '#1F2937',
                  border: '1px solid #BFDBFE',
                  fontSize: '0.813rem',
                  '& .MuiAlert-icon': {
                    color: '#3B82F6',
                  },
                }}
              >
                Supported formats: Excel files (.xlsx, .xls). Maximum file size: 10MB
              </Alert>
            </Box>
          ) : formData.type === 'databricks' ? (
            // Databricks Connection Fields
            <>
              <TextField
                label="Workspace URL"
                name="workspace_url"
                value={formData.workspace_url}
                onChange={handleInputChange}
                fullWidth
                required
                placeholder="https://your-workspace.cloud.databricks.com"
                helperText="Your Databricks workspace URL (e.g., https://your-workspace.cloud.databricks.com)"
              />
              <TextField
                label="HTTP Path"
                name="http_path"
                value={formData.http_path}
                onChange={handleInputChange}
                fullWidth
                required
                placeholder="/sql/1.0/warehouses/xxxxx"
                helperText="SQL warehouse HTTP path (found in Connection Details)"
              />
              <TextField
                label="Access Token"
                name="access_token"
                type="password"
                value={formData.access_token}
                onChange={handleInputChange}
                fullWidth
                required
                helperText="Personal access token for authentication"
              />
              <TextField
                label="Catalog (Optional)"
                name="database"
                value={formData.database}
                onChange={handleInputChange}
                fullWidth
                placeholder="main"
                helperText="Databricks catalog name (optional, defaults to 'main')"
              />
            </>
          ) : (
            // Database Connection Fields
            <>
              <TextField
                label="Host"
                name="host"
                value={formData.host}
                onChange={handleInputChange}
                fullWidth
                required
              />
              <TextField
                label="Port"
                name="port"
                value={formData.port}
                onChange={handleInputChange}
                fullWidth
                required
              />
              <TextField
                label="Source Database Name"
                name="database"
                value={formData.database}
                onChange={handleInputChange}
                fullWidth
                required
              />
              <TextField
                label="Username"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                fullWidth
                required
              />
              <TextField
                label="Password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleInputChange}
                fullWidth
                required
              />
              {formData.type === 'oracle' && (
                <TextField
                  label="Service Name (Optional)"
                  name="service_name"
                  value={formData.service_name}
                  onChange={handleInputChange}
                  fullWidth
                  helperText="Oracle service name (e.g., ORCLPDB). Leave empty to use SID."
                />
              )}
            </>
          )}
        </Box>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2.5, pt: 1.5 }}>
        <Button
          onClick={handleClose}
          variant="outlined"
          size="small"
        >
          Cancel
        </Button>

        {formData.type === 'excel' ? (
          // Excel Upload Button
          <Button
            onClick={handleFileUpload}
            variant="contained"
            disabled={!selectedFile || uploadLoading || !formData.name}
            size="small"
            startIcon={uploadLoading ? <CircularProgress size={16} sx={{ color: '#FFFFFF' }} /> : <CloudUploadIcon />}
            sx={{
              bgcolor: '#5B6FE5',
              '&:hover': {
                bgcolor: '#4C5FD5',
              },
              '&:disabled': {
                bgcolor: '#E5E7EB',
                color: '#9CA3AF',
              },
            }}
          >
            {uploadLoading ? 'Uploading...' : 'Upload Excel'}
          </Button>
        ) : (
          // Database Connection Buttons
          <>
            <Button
              onClick={handleTestConnection}
              disabled={testingConnection}
              variant="outlined"
              startIcon={testingConnection ? <CircularProgress size={16} /> : null}
              size="small"
            >
              Test Connection
            </Button>
            <Button
              onClick={handleAddConnection}
              variant="contained"
              disabled={
                loading ||
                !formData.name ||
                (formData.type === 'databricks'
                  ? (!formData.workspace_url || !formData.http_path || !formData.access_token)
                  : !formData.host
                )
              }
              size="small"
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
          </>
        )}
      </DialogActions>
    </Dialog>
  );
}

export default AddConnectionDialog;

