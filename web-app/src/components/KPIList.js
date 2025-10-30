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





  if (loading && kpis.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>


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
              <TableCell sx={{ fontWeight: 'bold', minWidth: '150px' }}>Group</TableCell>
              <TableCell sx={{ fontWeight: 'bold', width: '40%' }}>NL Definition</TableCell>
              <TableCell sx={{ fontWeight: 'bold', textAlign: 'center', minWidth: '200px' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {kpis.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center" sx={{ py: 3 }}>
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
                    {kpi.group_name || <span style={{ color: '#999' }}>-</span>}
                  </TableCell>
                  <TableCell sx={{ maxWidth: '400px', overflow: 'hidden', textOverflow: 'ellipsis', wordBreak: 'break-word' }}>
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

