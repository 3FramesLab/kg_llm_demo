import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Alert,
  CircularProgress,
  useMediaQuery,
  useTheme,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  FormHelperText,
} from '@mui/material';
import { createKPI, updateKPI, listGroups, listDashboards } from '../../services/api';

const KPIForm = ({ open, kpi, onClose, onSuccess, fullScreen }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [formData, setFormData] = useState({
    name: '',
    alias_name: '',
    group_name: '',
    description: '',
    nl_definition: '',
    group_id: '',
    dashboard_id: '',
    dashboard_name: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [groups, setGroups] = useState([]);
  const [dashboards, setDashboards] = useState([]);
  const [loadingDropdowns, setLoadingDropdowns] = useState(false);



  // Fetch groups and dashboards when dialog opens
  useEffect(() => {
    const fetchDropdownData = async () => {
      if (!open) return;

      setLoadingDropdowns(true);
      try {
        const [groupsResponse, dashboardsResponse] = await Promise.all([
          listGroups(),
          listDashboards()
        ]);

        setGroups(groupsResponse.data || []);
        setDashboards(dashboardsResponse.data || []);
      } catch (err) {
        console.error('Error fetching dropdown data:', err);
        setError('Failed to load groups and dashboards');
      } finally {
        setLoadingDropdowns(false);
      }
    };

    fetchDropdownData();
  }, [open]);

  // Initialize form with KPI data if editing
  useEffect(() => {
    if (kpi) {
      setFormData({
        name: kpi.name || '',
        alias_name: kpi.alias_name || '',
        group_name: kpi.group_name || '',
        description: kpi.description || '',
        nl_definition: kpi.nl_definition || '',
        group_id: kpi.group_id || '',
        dashboard_id: kpi.dashboard_id || '',
        dashboard_name: kpi.dashboard_name || '',
      });
    } else {
      setFormData({
        name: '',
        alias_name: '',
        group_name: '',
        description: '',
        nl_definition: '',
        group_id: '',
        dashboard_id: '',
        dashboard_name: '',
      });
    }
    setError(null);
  }, [kpi, open]);

  const handleChange = (e) => {
    const { name, value } = e.target;

    // When group_id changes, also update group_name
    if (name === 'group_id') {
      const selectedGroup = groups.find(g => g.id === value);
      setFormData((prev) => ({
        ...prev,
        group_id: value,
        group_name: selectedGroup ? selectedGroup.name : '',
      }));
    }
    // When dashboard_id changes, also update dashboard_name
    else if (name === 'dashboard_id') {
      const selectedDashboard = dashboards.find(d => d.id === value);
      setFormData((prev) => ({
        ...prev,
        dashboard_id: value,
        dashboard_name: selectedDashboard ? selectedDashboard.name : '',
      }));
    }
    // For all other fields
    else {
      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));
    }
  };

  const handleSubmit = async () => {
    // Validation
    if (!formData.name.trim()) {
      setError('KPI name is required');
      return;
    }
    if (!formData.nl_definition.trim()) {
      setError('Natural language definition is required');
      return;
    }
    if (!formData.group_id) {
      setError('Group selection is required');
      return;
    }
    if (!formData.dashboard_id) {
      setError('Dashboard selection is required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      if (kpi) {
        // Update existing KPI
        await updateKPI(kpi.id, formData);
      } else {
        // Create new KPI
        await createKPI(formData);
      }
      onSuccess();
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save KPI');
      console.error('Error saving KPI:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
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
        {kpi ? 'Edit KPI' : 'Create New KPI'}
      </DialogTitle>
      <DialogContent sx={{ px: 3 }}>
        <Box sx={{ pt: 1.5, display: 'flex', flexDirection: 'column', gap: 2 }}>
          {error && (
            <Alert
              severity="error"
              sx={{
                mb: 0,
                borderRadius: 1.5,
                '& .MuiAlert-message': {
                  fontSize: '0.875rem',
                },
              }}
              onClose={() => setError(null)}
            >
              {error}
            </Alert>
          )}

          {/* KPI Name */}
          <TextField
            label="KPI Name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            fullWidth
            required
            size="small"
            placeholder="e.g., Product Match Rate"
            disabled={loading || (kpi ? true : false)}
            helperText={kpi ? 'Name cannot be changed' : ''}
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

          {/* Alias Name */}
          <TextField
            label="Alias Name (Optional)"
            name="alias_name"
            value={formData.alias_name}
            onChange={handleChange}
            fullWidth
            size="small"
            placeholder="e.g., PMR"
            disabled={loading}
            helperText="Business-friendly short name"
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

          {/* Group Dropdown */}
          <FormControl
            fullWidth
            size="small"
            disabled={loading || loadingDropdowns}
            required
            error={!formData.group_id && error === 'Group selection is required'}
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
            <InputLabel>Group *</InputLabel>
            <Select
              name="group_id"
              value={formData.group_id}
              onChange={handleChange}
              label="Group *"
            >
              <MenuItem value="">
                <em>Select a group</em>
              </MenuItem>
              {groups.map((group) => (
                <MenuItem key={group.id} value={group.id}>
                  {group.name}
                </MenuItem>
              ))}
            </Select>
            <FormHelperText sx={{ fontSize: '0.75rem', color: '#6B7280' }}>
              Select the group from Master Page
            </FormHelperText>
          </FormControl>

          {/* Dashboard Dropdown */}
          <FormControl
            fullWidth
            size="small"
            disabled={loading || loadingDropdowns}
            required
            error={!formData.dashboard_id && error === 'Dashboard selection is required'}
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
            <InputLabel>Dashboard *</InputLabel>
            <Select
              name="dashboard_id"
              value={formData.dashboard_id}
              onChange={handleChange}
              label="Dashboard *"
            >
              <MenuItem value="">
                <em>Select a dashboard</em>
              </MenuItem>
              {dashboards.map((dashboard) => (
                <MenuItem key={dashboard.id} value={dashboard.id}>
                  {dashboard.name}
                </MenuItem>
              ))}
            </Select>
            <FormHelperText sx={{ fontSize: '0.75rem', color: '#6B7280' }}>
              Select the dashboard from Master Page
            </FormHelperText>
          </FormControl>

          {/* Description */}
          <TextField
            label="Description (Optional)"
            name="description"
            value={formData.description}
            onChange={handleChange}
            fullWidth
            size="small"
            multiline
            rows={2}
            placeholder="Detailed description of what this KPI measures"
            disabled={loading}
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

          {/* NL Definition */}
          <TextField
            label="Natural Language Definition"
            name="nl_definition"
            value={formData.nl_definition}
            onChange={handleChange}
            fullWidth
            required
            size="small"
            multiline
            rows={3}
            placeholder="e.g., Show me all products in RBP that are not in OPS"
            disabled={loading}
            helperText="The natural language query that defines this KPI"
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
        </Box>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2.5, pt: 1.5 }}>
        <Button
          onClick={onClose}
          disabled={loading}
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
          onClick={handleSubmit}
          variant="contained"
          disabled={loading}
          size="small"
          startIcon={loading ? <CircularProgress size={16} /> : null}
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
          {loading ? 'Saving...' : kpi ? 'Update' : 'Create'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default KPIForm;

