import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Chip,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
  Grid
} from '@mui/material';
import {
  Add as AddIcon,
  Schedule as ScheduleIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  AccessTime as TimeIcon,
  Timeline as TimelineIcon,
  TrendingUp as TriggerIcon
} from '@mui/icons-material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import ScheduleExecutionHistory from './ScheduleExecutionHistory';

const ScheduleManagement = ({ kpiId, kpiName }) => {
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState(null);
  const [historyDialogOpen, setHistoryDialogOpen] = useState(false);
  const [selectedSchedule, setSelectedSchedule] = useState(null);
  const [formData, setFormData] = useState({
    schedule_name: '',
    schedule_type: 'daily',
    cron_expression: '',
    timezone: 'UTC',
    start_date: new Date(),
    end_date: null,
    schedule_config: {
      retry_count: 3,
      retry_delay: 300,
      timeout: 3600,
      email_notifications: []
    }
  });

  useEffect(() => {
    if (kpiId) {
      fetchSchedules();
    }
  }, [kpiId]);

  const fetchSchedules = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/v1/kpi-schedules/kpi/${kpiId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setSchedules(data);
      
    } catch (err) {
      console.error('Error fetching schedules:', err);
      setError('Failed to load schedules');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSchedule = () => {
    setEditingSchedule(null);
    setFormData({
      schedule_name: `${kpiName} - Daily Schedule`,
      schedule_type: 'daily',
      cron_expression: '',
      timezone: 'UTC',
      start_date: new Date(),
      end_date: null,
      schedule_config: {
        retry_count: 3,
        retry_delay: 300,
        timeout: 3600,
        email_notifications: []
      }
    });
    setDialogOpen(true);
  };

  const handleEditSchedule = (schedule) => {
    setEditingSchedule(schedule);
    setFormData({
      schedule_name: schedule.schedule_name,
      schedule_type: schedule.schedule_type,
      cron_expression: schedule.cron_expression || '',
      timezone: schedule.timezone,
      start_date: new Date(schedule.start_date),
      end_date: schedule.end_date ? new Date(schedule.end_date) : null,
      schedule_config: schedule.schedule_config || {
        retry_count: 3,
        retry_delay: 300,
        timeout: 3600,
        email_notifications: []
      }
    });
    setDialogOpen(true);
  };

  const handleSaveSchedule = async () => {
    try {
      setLoading(true);
      
      const payload = {
        ...formData,
        kpi_id: kpiId,
        start_date: formData.start_date.toISOString(),
        end_date: formData.end_date ? formData.end_date.toISOString() : null
      };

      const url = editingSchedule 
        ? `/v1/kpi-schedules/${editingSchedule.id}`
        : '/v1/kpi-schedules/';
      
      const method = editingSchedule ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save schedule');
      }

      await fetchSchedules();
      setDialogOpen(false);
      
    } catch (err) {
      console.error('Error saving schedule:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSchedule = async (scheduleId) => {
    if (!window.confirm('Are you sure you want to delete this schedule?')) {
      return;
    }

    try {
      setLoading(true);
      
      const response = await fetch(`/v1/kpi-schedules/${scheduleId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete schedule');
      }

      await fetchSchedules();
      
    } catch (err) {
      console.error('Error deleting schedule:', err);
      setError('Failed to delete schedule');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleSchedule = async (scheduleId) => {
    try {
      setLoading(true);
      
      const response = await fetch(`/v1/kpi-schedules/${scheduleId}/toggle`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to toggle schedule');
      }

      await fetchSchedules();
      
    } catch (err) {
      console.error('Error toggling schedule:', err);
      setError('Failed to toggle schedule');
    } finally {
      setLoading(false);
    }
  };

  const handleViewHistory = (schedule) => {
    setSelectedSchedule(schedule);
    setHistoryDialogOpen(true);
  };

  const handleTriggerManually = async (scheduleId) => {
    try {
      setLoading(true);

      const response = await fetch(`/v1/kpi-schedules/${scheduleId}/trigger`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to trigger schedule');
      }

      // Refresh schedules after triggering
      setTimeout(() => {
        fetchSchedules();
      }, 2000);

    } catch (err) {
      console.error('Error triggering schedule:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getScheduleTypeDisplay = (type) => {
    const types = {
      daily: 'Daily',
      weekly: 'Weekly',
      monthly: 'Monthly',
      cron: 'Custom (Cron)'
    };
    return types[type] || type;
  };

  const getStatusColor = (status) => {
    const colors = {
      success: 'success',
      failed: 'error',
      running: 'info',
      pending: 'warning'
    };
    return colors[status] || 'default';
  };

  const formatNextExecution = (nextExecution) => {
    if (!nextExecution) return 'Not scheduled';

    const date = new Date(nextExecution);
    const now = new Date();
    const diffMs = date - now;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) {
      return `In ${diffDays} day${diffDays > 1 ? 's' : ''}`;
    } else if (diffHours > 0) {
      return `In ${diffHours} hour${diffHours > 1 ? 's' : ''}`;
    } else if (diffMs > 0) {
      return 'Soon';
    } else {
      return 'Overdue';
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ScheduleIcon />
          Schedule Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateSchedule}
          disabled={loading}
          size="small"
        >
          Create Schedule
        </Button>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Loading */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Schedules List */}
      {!loading && (
        <Grid container spacing={2}>
          {schedules.length === 0 ? (
            <Grid item xs={12}>
              <Card>
                <CardContent sx={{ textAlign: 'center', py: 4 }}>
                  <ScheduleIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No Schedules Configured
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Create a schedule to automatically execute this KPI at regular intervals.
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={handleCreateSchedule}
                    size="small"
                  >
                    Create First Schedule
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ) : (
            schedules.map((schedule) => (
              <Grid item xs={12} md={6} key={schedule.id}>
                <Card>
                  <CardContent>
                    {/* Schedule Header */}
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box>
                        <Typography variant="h6" gutterBottom>
                          {schedule.schedule_name}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                          <Chip
                            label={getScheduleTypeDisplay(schedule.schedule_type)}
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                          <Chip
                            label={schedule.is_active ? 'Active' : 'Inactive'}
                            size="small"
                            color={schedule.is_active ? 'success' : 'default'}
                          />
                          {schedule.last_execution_status && (
                            <Chip
                              label={schedule.last_execution_status}
                              size="small"
                              color={getStatusColor(schedule.last_execution_status)}
                            />
                          )}
                        </Box>
                      </Box>

                      {/* Action Buttons */}
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <Tooltip title="View Execution History">
                          <IconButton
                            size="small"
                            onClick={() => handleViewHistory(schedule)}
                            color="info"
                          >
                            <TimelineIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Trigger Manually">
                          <IconButton
                            size="small"
                            onClick={() => handleTriggerManually(schedule.id)}
                            color="primary"
                            disabled={!schedule.is_active}
                          >
                            <TriggerIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title={schedule.is_active ? 'Pause Schedule' : 'Resume Schedule'}>
                          <IconButton
                            size="small"
                            onClick={() => handleToggleSchedule(schedule.id)}
                            color={schedule.is_active ? 'warning' : 'success'}
                          >
                            {schedule.is_active ? <PauseIcon /> : <PlayIcon />}
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Edit Schedule">
                          <IconButton
                            size="small"
                            onClick={() => handleEditSchedule(schedule)}
                          >
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete Schedule">
                          <IconButton
                            size="small"
                            onClick={() => handleDeleteSchedule(schedule.id)}
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </Box>

                    {/* Schedule Details */}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <TimeIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary">
                        Next execution: {formatNextExecution(schedule.next_execution)}
                      </Typography>
                    </Box>

                    {schedule.schedule_type === 'cron' && schedule.cron_expression && (
                      <Typography variant="body2" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
                        Cron: {schedule.cron_expression}
                      </Typography>
                    )}

                    <Typography variant="body2" color="text.secondary">
                      Created: {new Date(schedule.created_at).toLocaleDateString()}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))
          )}
        </Grid>
      )}

      {/* Create/Edit Schedule Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingSchedule ? 'Edit Schedule' : 'Create New Schedule'}
        </DialogTitle>
        <DialogContent>
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 2 }}>
              {/* Schedule Name */}
              <TextField
                label="Schedule Name"
                value={formData.schedule_name}
                onChange={(e) => setFormData({ ...formData, schedule_name: e.target.value })}
                fullWidth
                required
              />

              {/* Schedule Type */}
              <FormControl fullWidth required>
                <InputLabel>Schedule Type</InputLabel>
                <Select
                  value={formData.schedule_type}
                  label="Schedule Type"
                  onChange={(e) => setFormData({ ...formData, schedule_type: e.target.value })}
                >
                  <MenuItem value="daily">Daily</MenuItem>
                  <MenuItem value="weekly">Weekly</MenuItem>
                  <MenuItem value="monthly">Monthly</MenuItem>
                  <MenuItem value="cron">Custom (Cron Expression)</MenuItem>
                </Select>
              </FormControl>

              {/* Cron Expression (only for cron type) */}
              {formData.schedule_type === 'cron' && (
                <TextField
                  label="Cron Expression"
                  value={formData.cron_expression}
                  onChange={(e) => setFormData({ ...formData, cron_expression: e.target.value })}
                  fullWidth
                  required
                  placeholder="0 9 * * * (daily at 9 AM)"
                  helperText="Format: minute hour day month weekday"
                />
              )}

              {/* Timezone */}
              <FormControl fullWidth>
                <InputLabel>Timezone</InputLabel>
                <Select
                  value={formData.timezone}
                  label="Timezone"
                  onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
                >
                  <MenuItem value="UTC">UTC</MenuItem>
                  <MenuItem value="America/New_York">Eastern Time</MenuItem>
                  <MenuItem value="America/Chicago">Central Time</MenuItem>
                  <MenuItem value="America/Denver">Mountain Time</MenuItem>
                  <MenuItem value="America/Los_Angeles">Pacific Time</MenuItem>
                  <MenuItem value="Europe/London">London</MenuItem>
                  <MenuItem value="Asia/Tokyo">Tokyo</MenuItem>
                </Select>
              </FormControl>

              {/* Start Date */}
              <DateTimePicker
                label="Start Date & Time"
                value={formData.start_date}
                onChange={(newValue) => setFormData({ ...formData, start_date: newValue })}
                renderInput={(params) => <TextField {...params} fullWidth required />}
              />

              {/* End Date (Optional) */}
              <DateTimePicker
                label="End Date & Time (Optional)"
                value={formData.end_date}
                onChange={(newValue) => setFormData({ ...formData, end_date: newValue })}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />

              {/* Advanced Configuration */}
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Advanced Configuration
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={4}>
                    <TextField
                      label="Retry Count"
                      type="number"
                      value={formData.schedule_config.retry_count}
                      onChange={(e) => setFormData({
                        ...formData,
                        schedule_config: {
                          ...formData.schedule_config,
                          retry_count: parseInt(e.target.value) || 0
                        }
                      })}
                      inputProps={{ min: 0, max: 10 }}
                      fullWidth
                    />
                  </Grid>
                  <Grid item xs={4}>
                    <TextField
                      label="Retry Delay (seconds)"
                      type="number"
                      value={formData.schedule_config.retry_delay}
                      onChange={(e) => setFormData({
                        ...formData,
                        schedule_config: {
                          ...formData.schedule_config,
                          retry_delay: parseInt(e.target.value) || 300
                        }
                      })}
                      inputProps={{ min: 60, max: 3600 }}
                      fullWidth
                    />
                  </Grid>
                  <Grid item xs={4}>
                    <TextField
                      label="Timeout (seconds)"
                      type="number"
                      value={formData.schedule_config.timeout}
                      onChange={(e) => setFormData({
                        ...formData,
                        schedule_config: {
                          ...formData.schedule_config,
                          timeout: parseInt(e.target.value) || 3600
                        }
                      })}
                      inputProps={{ min: 300, max: 7200 }}
                      fullWidth
                    />
                  </Grid>
                </Grid>
              </Box>

              {/* Email Notifications */}
              <TextField
                label="Email Notifications (comma-separated)"
                value={formData.schedule_config.email_notifications.join(', ')}
                onChange={(e) => setFormData({
                  ...formData,
                  schedule_config: {
                    ...formData.schedule_config,
                    email_notifications: e.target.value.split(',').map(email => email.trim()).filter(email => email)
                  }
                })}
                fullWidth
                placeholder="user1@example.com, user2@example.com"
                helperText="Enter email addresses to receive notifications on execution failures"
              />
            </Box>
          </LocalizationProvider>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)} size="small">Cancel</Button>
          <Button
            onClick={handleSaveSchedule}
            variant="contained"
            disabled={loading || !formData.schedule_name}
            size="small"
          >
            {editingSchedule ? 'Update' : 'Create'} Schedule
          </Button>
        </DialogActions>
      </Dialog>

      {/* Execution History Dialog */}
      <Dialog
        open={historyDialogOpen}
        onClose={() => setHistoryDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TimelineIcon />
          Execution History
        </DialogTitle>
        <DialogContent>
          {selectedSchedule && (
            <ScheduleExecutionHistory
              scheduleId={selectedSchedule.id}
              scheduleName={selectedSchedule.schedule_name}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setHistoryDialogOpen(false)} size="small">Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ScheduleManagement;
