import React, { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  TextField,
  Box,
  CircularProgress,
  Alert,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as PlayArrowIcon,
  History as HistoryIcon,
} from '@mui/icons-material';
import { listKPIs, deleteKPI } from '../services/api';

const KPIList = ({ onEdit, onExecute, onViewHistory, refreshTrigger }) => {
  const [kpis, setKpis] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [groupFilter, setGroupFilter] = useState('');
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [selectedKPI, setSelectedKPI] = useState(null);

  // Fetch KPIs
  useEffect(() => {
    fetchKPIs();
  }, [refreshTrigger]);

  const fetchKPIs = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        is_active: true,
      };
      if (groupFilter) {
        params.group_name = groupFilter;
      }
      if (searchTerm) {
        params.search = searchTerm;
      }

      const response = await listKPIs(params);
      setKpis(response.data.kpis || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch KPIs');
      console.error('Error fetching KPIs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (kpi) => {
    setSelectedKPI(kpi);
    setDeleteConfirmOpen(true);
  };

  const handleDeleteConfirm = async () => {
    try {
      await deleteKPI(selectedKPI.id);
      setDeleteConfirmOpen(false);
      setSelectedKPI(null);
      fetchKPIs();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete KPI');
    }
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleGroupFilterChange = (e) => {
    setGroupFilter(e.target.value);
  };

  const handleApplyFilters = () => {
    fetchKPIs();
  };

  const getGroupColor = (group) => {
    const colors = {
      'Data Quality': 'primary',
      'Reconciliation': 'secondary',
      'Performance': 'success',
      'Compliance': 'warning',
      'Other': 'default',
    };
    return colors[group] || 'default';
  };

  if (loading && kpis.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Filters */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <TextField
          label="Search KPIs"
          variant="outlined"
          size="small"
          value={searchTerm}
          onChange={handleSearch}
          placeholder="Search by name or description"
          sx={{ flex: 1, minWidth: '200px' }}
        />
        <TextField
          label="Filter by Group"
          variant="outlined"
          size="small"
          value={groupFilter}
          onChange={handleGroupFilterChange}
          placeholder="e.g., Data Quality"
          sx={{ flex: 1, minWidth: '200px' }}
        />
        <Button variant="contained" onClick={handleApplyFilters}>
          Apply Filters
        </Button>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* KPI Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Name</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Alias</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Group</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Description</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>NL Definition</TableCell>
              <TableCell sx={{ fontWeight: 'bold', textAlign: 'center' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {kpis.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 3 }}>
                  No KPIs found. Create one to get started!
                </TableCell>
              </TableRow>
            ) : (
              kpis.map((kpi) => (
                <TableRow key={kpi.id} hover>
                  <TableCell sx={{ fontWeight: 500 }}>{kpi.name}</TableCell>
                  <TableCell>
                    {kpi.alias_name ? (
                      <Chip label={kpi.alias_name} size="small" variant="outlined" />
                    ) : (
                      <span style={{ color: '#999' }}>-</span>
                    )}
                  </TableCell>
                  <TableCell>
                    {kpi.group_name ? (
                      <Chip
                        label={kpi.group_name}
                        size="small"
                        color={getGroupColor(kpi.group_name)}
                        variant="outlined"
                      />
                    ) : (
                      <span style={{ color: '#999' }}>-</span>
                    )}
                  </TableCell>
                  <TableCell sx={{ maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {kpi.description || '-'}
                  </TableCell>
                  <TableCell sx={{ maxWidth: '250px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {kpi.nl_definition}
                  </TableCell>
                  <TableCell align="center">
                    <Tooltip title="Execute">
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => onExecute(kpi)}
                      >
                        <PlayArrowIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="History">
                      <IconButton
                        size="small"
                        color="info"
                        onClick={() => onViewHistory(kpi)}
                      >
                        <HistoryIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Edit">
                      <IconButton
                        size="small"
                        color="warning"
                        onClick={() => onEdit(kpi)}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDeleteClick(kpi)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmOpen} onClose={() => setDeleteConfirmOpen(false)}>
        <DialogTitle>Delete KPI</DialogTitle>
        <DialogContent>
          Are you sure you want to delete the KPI "{selectedKPI?.name}"?
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirmOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Loading Indicator */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
          <CircularProgress size={30} />
        </Box>
      )}
    </Box>
  );
};

export default KPIList;

