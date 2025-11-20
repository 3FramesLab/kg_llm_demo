import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Alert,
  CircularProgress,
  Chip,
  MenuItem,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { listDashboards, createDashboard, updateDashboard, deleteDashboard } from '../services/api';

const DashboardsManagement = ({ refreshTrigger, onRefresh }) => {
  const [dashboards, setDashboards] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingDashboard, setEditingDashboard] = useState(null);
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    description: '',
    is_active: true,
  });

  useEffect(() => {
    loadData();
  }, [refreshTrigger]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');
      const dashboardsRes = await listDashboards();
      setDashboards(dashboardsRes.data.dashboards || []);
    } catch (err) {
      setError('Failed to load data: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (dashboard = null) => {
    if (dashboard) {
      setEditingDashboard(dashboard);
      setFormData({
        code: dashboard.code || '',
        name: dashboard.name,
        description: dashboard.description || '',
        is_active: dashboard.is_active,
      });
    } else {
      setEditingDashboard(null);
      setFormData({
        code: '',
        name: '',
        description: '',
        is_active: true,
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingDashboard(null);
  };

  const handleSave = async () => {
    try {
      setError('');
      if (!formData.code.trim()) {
        setError('Dashboard code is required');
        return;
      }
      if (!formData.name.trim()) {
        setError('Dashboard name is required');
        return;
      }

      if (editingDashboard) {
        await updateDashboard(editingDashboard.id, formData);
        setSuccess('Dashboard updated successfully');
      } else {
        await createDashboard(formData);
        setSuccess('Dashboard created successfully');
      }

      handleCloseDialog();
      loadData();
    } catch (err) {
      setError('Failed to save dashboard: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDelete = async (dashboardId) => {
    if (window.confirm('Are you sure you want to delete this dashboard?')) {
      try {
        setError('');
        await deleteDashboard(dashboardId);
        setSuccess('Dashboard deleted successfully');
        loadData();
      } catch (err) {
        setError('Failed to delete dashboard: ' + (err.response?.data?.detail || err.message));
      }
    }
  };

  return (
    <Box>
      {error && <Alert severity="error" sx={{ mb: 1.5 }} onClose={() => setError('')}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 1.5 }} onClose={() => setSuccess('')}>{success}</Alert>}

      <Box sx={{ display: 'flex', gap: 1.5, mb: 2 }}>
        <Button
          variant="contained"
          size="small"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
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
          }}
        >
          Add Dashboard
        </Button>
        <Button
          variant="outlined"
          size="small"
          startIcon={<RefreshIcon />}
          onClick={loadData}
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
          Refresh
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
              <TableRow>
                <TableCell><strong>Code</strong></TableCell>
                <TableCell><strong>Name</strong></TableCell>
                <TableCell><strong>Description</strong></TableCell>
                <TableCell><strong>Status</strong></TableCell>
                <TableCell align="right"><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {dashboards.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 3 }}>
                    No dashboards found
                  </TableCell>
                </TableRow>
              ) : (
                dashboards.map((dashboard) => (
                  <TableRow key={dashboard.id} hover>
                    <TableCell>{dashboard.code || '-'}</TableCell>
                    <TableCell>{dashboard.name}</TableCell>
                    <TableCell>{dashboard.description || '-'}</TableCell>
                    <TableCell>
                      <Chip
                        label={dashboard.is_active ? 'Active' : 'Inactive'}
                        color={dashboard.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={() => handleOpenDialog(dashboard)}
                        title="Edit"
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(dashboard.id)}
                        title="Delete"
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ pb: 1, pt: 2 }}>
          {editingDashboard ? 'Edit Dashboard' : 'Create New Dashboard'}
        </DialogTitle>
        <DialogContent sx={{ pt: 1, pb: 2 }}>
          <TextField
            fullWidth
            label="Dashboard Code"
            value={formData.code}
            onChange={(e) => setFormData({ ...formData, code: e.target.value })}
            margin="dense"
            size="small"
            required
            helperText="Unique identifier for the dashboard"
          />
          <TextField
            fullWidth
            label="Dashboard Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            margin="dense"
            size="small"
            required
          />
          <TextField
            fullWidth
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            margin="dense"
            size="small"
            multiline
            rows={2}
          />
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2, pt: 1 }}>
          <Button
            onClick={handleCloseDialog}
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
            }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            variant="contained"
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
            }}
          >
            {editingDashboard ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DashboardsManagement;

