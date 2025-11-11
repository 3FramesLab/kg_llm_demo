import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  Box,
  IconButton,
  Alert,
  Snackbar,
  Fab,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  TableChart as TableIcon,
  Label as AliasIcon,
} from '@mui/icons-material';
import {
  getAllTableAliases,
  createTableAlias,
  updateTableAlias,
  deleteTableAlias,
  listKGs,
  listSchemas,
  getSchemaTable
} from '../services/api';

const TableAliasesManagement = () => {
  const [aliases, setAliases] = useState([]);
  const [kgs, setKgs] = useState([]);
  const [schemas, setSchemas] = useState([]);
  const [tables, setTables] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingAlias, setEditingAlias] = useState(null);
  const [formData, setFormData] = useState({
    kg_name: '',
    schema_name: '',
    table_name: '',
    aliases: []
  });
  const [newAlias, setNewAlias] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [aliasesResponse, kgsResponse, schemasResponse] = await Promise.all([
        getAllTableAliases(),
        listKGs(),
        listSchemas()
      ]);

      console.log('KGs Response:', kgsResponse.data);
      console.log('Schemas Response:', schemasResponse.data);

      setAliases(aliasesResponse.data.data || []);
      setKgs(kgsResponse.data.data || []);
      setSchemas(schemasResponse.data.schemas || []);
    } catch (error) {
      console.error('Error loading data:', error);
      showSnackbar('Error loading data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const loadTables = async (schemaName) => {
    try {
      console.log('Loading tables for schema:', schemaName);
      const response = await getSchemaTable(schemaName);
      console.log('Tables response:', response.data);
      setTables(response.data.data || []);
    } catch (error) {
      console.error('Error loading tables:', error);
      setTables([]);
      showSnackbar('Error loading tables', 'error');
    }
  };

  const handleOpenDialog = (alias = null) => {
    if (alias) {
      setEditingAlias(alias);
      setFormData({
        kg_name: alias.kg_name,
        schema_name: '',
        table_name: alias.table_name,
        aliases: [...alias.aliases]
      });
    } else {
      setEditingAlias(null);
      setFormData({
        kg_name: '',
        schema_name: '',
        table_name: '',
        aliases: []
      });
    }
    setTables([]);
    setNewAlias('');
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingAlias(null);
    setFormData({ kg_name: '', schema_name: '', table_name: '', aliases: [] });
    setNewAlias('');
    setTables([]);
  };

  const handleAddAlias = () => {
    if (newAlias.trim() && !formData.aliases.includes(newAlias.trim())) {
      setFormData(prev => ({
        ...prev,
        aliases: [...prev.aliases, newAlias.trim()]
      }));
      setNewAlias('');
    }
  };

  const handleRemoveAlias = (aliasToRemove) => {
    setFormData(prev => ({
      ...prev,
      aliases: prev.aliases.filter(alias => alias !== aliasToRemove)
    }));
  };

  const handleSave = async () => {
    try {
      if (!formData.kg_name || !formData.table_name) {
        showSnackbar('Please select Knowledge Graph and Table Name', 'error');
        return;
      }

      const aliasData = {
        table_name: formData.table_name,
        aliases: formData.aliases
      };

      if (editingAlias) {
        await updateTableAlias(formData.kg_name, formData.table_name, aliasData);
        showSnackbar('Table aliases updated successfully');
      } else {
        await createTableAlias(formData.kg_name, aliasData);
        showSnackbar('Table aliases created successfully');
      }

      handleCloseDialog();
      loadData();
    } catch (error) {
      console.error('Error saving alias:', error);
      showSnackbar('Error saving table aliases', 'error');
    }
  };

  const handleDelete = async (alias) => {
    if (window.confirm(`Are you sure you want to delete aliases for table "${alias.table_name}"?`)) {
      try {
        await deleteTableAlias(alias.kg_name, alias.table_name);
        showSnackbar('Table aliases deleted successfully');
        loadData();
      } catch (error) {
        console.error('Error deleting alias:', error);
        showSnackbar('Error deleting table aliases', 'error');
      }
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TableIcon color="primary" />
          Table Aliases Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
          size="large"
        >
          Add Table Alias
        </Button>
      </Box>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AliasIcon />
            Table Aliases ({aliases.length})
          </Typography>

          {aliases.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" color="text.secondary">
                No table aliases found. Create your first table alias to get started.
              </Typography>
            </Box>
          ) : (
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Knowledge Graph</strong></TableCell>
                    <TableCell><strong>Table Name</strong></TableCell>
                    <TableCell><strong>Aliases</strong></TableCell>
                    <TableCell align="center"><strong>Actions</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {aliases.map((alias) => (
                    <TableRow key={alias.id} hover>
                      <TableCell>
                        <Chip
                          label={alias.kg_name}
                          color="primary"
                          variant="outlined"
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {alias.table_name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {alias.aliases.map((aliasName, index) => (
                            <Chip
                              key={index}
                              label={aliasName}
                              size="small"
                              color="secondary"
                              variant="outlined"
                            />
                          ))}
                          {alias.aliases.length === 0 && (
                            <Typography variant="body2" color="text.secondary" fontStyle="italic">
                              No aliases
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell align="center">
                        <Tooltip title="Edit">
                          <IconButton
                            color="primary"
                            onClick={() => handleOpenDialog(alias)}
                            size="small"
                          >
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton
                            color="error"
                            onClick={() => handleDelete(alias)}
                            size="small"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Add/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingAlias ? 'Edit Table Aliases' : 'Add Table Aliases'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Knowledge Graph</InputLabel>
                <Select
                  value={formData.kg_name}
                  label="Knowledge Graph"
                  onChange={(e) => setFormData(prev => ({ ...prev, kg_name: e.target.value }))}
                  disabled={!!editingAlias}
                >
                  {kgs.map((kg) => (
                    <MenuItem key={kg.name} value={kg.name}>
                      {kg.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Schema</InputLabel>
                <Select
                  value={formData.schema_name}
                  label="Schema"
                  onChange={(e) => {
                    const schemaName = e.target.value;
                    setFormData(prev => ({ ...prev, schema_name: schemaName, table_name: '' }));
                    if (schemaName) {
                      loadTables(schemaName);
                    } else {
                      setTables([]);
                    }
                  }}
                  disabled={!!editingAlias}
                >
                  {schemas.map((schema) => (
                    <MenuItem key={schema} value={schema}>
                      {schema}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Table Name</InputLabel>
                <Select
                  value={formData.table_name}
                  label="Table Name"
                  onChange={(e) => setFormData(prev => ({ ...prev, table_name: e.target.value }))}
                  disabled={!!editingAlias || !formData.schema_name}
                >
                  {tables.map((table) => (
                    <MenuItem key={table.name} value={table.name}>
                      {table.name} ({table.columns_count} columns)
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Aliases
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <TextField
                  fullWidth
                  size="small"
                  label="Add new alias"
                  value={newAlias}
                  onChange={(e) => setNewAlias(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddAlias()}
                  placeholder="e.g., RBP, RBP GPU"
                />
                <Button
                  variant="outlined"
                  onClick={handleAddAlias}
                  disabled={!newAlias.trim()}
                >
                  Add
                </Button>
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {formData.aliases.map((alias, index) => (
                  <Chip
                    key={index}
                    label={alias}
                    onDelete={() => handleRemoveAlias(alias)}
                    color="secondary"
                    variant="outlined"
                  />
                ))}
                {formData.aliases.length === 0 && (
                  <Typography variant="body2" color="text.secondary" fontStyle="italic">
                    No aliases added yet
                  </Typography>
                )}
              </Box>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} startIcon={<CancelIcon />}>
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            variant="contained"
            startIcon={<SaveIcon />}
            disabled={!formData.kg_name || !formData.table_name}
          >
            {editingAlias ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
      >
        <Alert
          onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default TableAliasesManagement;
