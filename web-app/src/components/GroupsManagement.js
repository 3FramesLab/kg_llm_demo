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
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { listGroups, createGroup, updateGroup, deleteGroup } from '../services/api';

const GroupsManagement = ({ refreshTrigger, onRefresh }) => {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingGroup, setEditingGroup] = useState(null);
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    description: '',
    color: '#1976d2',
    icon: 'dashboard',
    is_active: true,
  });

  useEffect(() => {
    loadGroups();
  }, [refreshTrigger]);

  const loadGroups = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await listGroups();
      setGroups(response.data.groups || []);
    } catch (err) {
      setError('Failed to load groups: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (group = null) => {
    if (group) {
      setEditingGroup(group);
      setFormData({
        code: group.code || '',
        name: group.name,
        description: group.description || '',
        color: group.color || '#1976d2',
        icon: group.icon || 'dashboard',
        is_active: group.is_active,
      });
    } else {
      setEditingGroup(null);
      setFormData({
        code: '',
        name: '',
        description: '',
        color: '#1976d2',
        icon: 'dashboard',
        is_active: true,
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingGroup(null);
  };

  const handleSave = async () => {
    try {
      setError('');
      if (!formData.code.trim()) {
        setError('Group code is required');
        return;
      }
      if (!formData.name.trim()) {
        setError('Group name is required');
        return;
      }

      if (editingGroup) {
        await updateGroup(editingGroup.id, formData);
        setSuccess('Group updated successfully');
      } else {
        await createGroup(formData);
        setSuccess('Group created successfully');
      }

      handleCloseDialog();
      loadGroups();
    } catch (err) {
      setError('Failed to save group: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDelete = async (groupId) => {
    if (window.confirm('Are you sure you want to delete this group?')) {
      try {
        setError('');
        await deleteGroup(groupId);
        setSuccess('Group deleted successfully');
        loadGroups();
      } catch (err) {
        setError('Failed to delete group: ' + (err.response?.data?.detail || err.message));
      }
    }
  };

  // Validation helper to check if all required fields are filled
  const isFormValid = () => {
    return formData.code.trim() !== '' && formData.name.trim() !== '';
  };

  return (
    <Box>
      {error && <Alert severity="error" sx={{ mb: 1 }} onClose={() => setError('')}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 1 }} onClose={() => setSuccess('')}>{success}</Alert>}

      <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1.5, mb: 1.5 }}>
        <Button
          variant="contained"
          size="small"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Group
        </Button>
        <Button
          variant="outlined"
          size="small"
          startIcon={<RefreshIcon />}
          onClick={loadGroups}
        >
          Refresh
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
              <TableRow>
                <TableCell sx={{ py: 0.75 }}><strong>Code</strong></TableCell>
                <TableCell sx={{ py: 0.75 }}><strong>Name</strong></TableCell>
                <TableCell sx={{ py: 0.75 }}><strong>Description</strong></TableCell>
                <TableCell sx={{ py: 0.75 }}><strong>Status</strong></TableCell>
                <TableCell align="right" sx={{ py: 0.75 }}><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {groups.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 2 }}>
                    No groups found
                  </TableCell>
                </TableRow>
              ) : (
                groups.map((group) => (
                  <TableRow key={group.id} hover>
                    <TableCell sx={{ py: 0.75 }}>{group.code || '-'}</TableCell>
                    <TableCell sx={{ py: 0.75 }}>{group.name}</TableCell>
                    <TableCell sx={{ py: 0.75 }}>{group.description || '-'}</TableCell>
                    <TableCell sx={{ py: 0.75 }}>
                      <Chip
                        label={group.is_active ? 'Active' : 'Inactive'}
                        color={group.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right" sx={{ py: 0.75 }}>
                      <IconButton
                        size="small"
                        onClick={() => handleOpenDialog(group)}
                        title="Edit"
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(group.id)}
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
        <DialogTitle sx={{ pb: 0.5, pt: 1.5 }}>
          {editingGroup ? 'Edit Group' : 'Create New Group'}
        </DialogTitle>
        <DialogContent sx={{ pt: 1, pb: 1.5 }}>
          <TextField
            fullWidth
            label="Group Code"
            value={formData.code}
            onChange={(e) => setFormData({ ...formData, code: e.target.value })}
            margin="dense"
            required
            helperText="Unique identifier for the group"
            size="small"
          />
          <TextField
            fullWidth
            label="Group Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            margin="dense"
            required
            size="small"
          />
          <TextField
            fullWidth
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            margin="dense"
            multiline
            rows={2}
            size="small"
          />
          <TextField
            fullWidth
            label="Color"
            type="color"
            value={formData.color}
            onChange={(e) => setFormData({ ...formData, color: e.target.value })}
            margin="dense"
            size="small"
          />
        </DialogContent>
        <DialogActions sx={{ px: 2, pb: 1.5, pt: 0.5 }}>
          <Button
            onClick={handleCloseDialog}
            size="small"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            variant="contained"
            size="small"
            disabled={!isFormValid()}
          >
            {editingGroup ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default GroupsManagement;

