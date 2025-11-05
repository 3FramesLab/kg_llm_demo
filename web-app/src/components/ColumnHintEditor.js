import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  TextField,
  Button,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Divider,
  Paper,
  IconButton
} from '@mui/material';
import {
  Save as SaveIcon,
  Cancel as CancelIcon,
  Add as AddIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { updateColumnHints } from '../services/api';

const SEMANTIC_TYPES = ['identifier', 'measure', 'dimension', 'date', 'flag', 'description', 'attribute'];
const ROLES = ['primary_key', 'foreign_key', 'attribute', 'calculated'];
const PRIORITIES = ['high', 'medium', 'low'];

function ColumnHintEditor({ tableName, columnName, columnHints, onUpdate, showSnackbar }) {
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState(columnHints || {});
  const [newAlias, setNewAlias] = useState('');
  const [newTerm, setNewTerm] = useState('');
  const [newExample, setNewExample] = useState('');
  const [newRule, setNewRule] = useState('');

  const handleSave = async () => {
    try {
      await updateColumnHints({
        table_name: tableName,
        column_name: columnName,
        user: 'web-user',
        hints: {
          ...form,
          manual_verified: true
        }
      });
      showSnackbar(`Updated hints for ${columnName}`, 'success');
      setEditing(false);
      onUpdate();
    } catch (error) {
      console.error('Error updating column hints:', error);
      showSnackbar(`Failed to update ${columnName}`, 'error');
    }
  };

  const handleCancel = () => {
    setForm(columnHints || {});
    setEditing(false);
  };

  const handleAddItem = (field, value, setValue) => {
    if (!value.trim()) return;
    const current = form[field] || [];
    setForm({ ...form, [field]: [...current, value.trim()] });
    setValue('');
  };

  const handleRemoveItem = (field, index) => {
    const current = form[field] || [];
    setForm({ ...form, [field]: current.filter((_, i) => i !== index) });
  };

  if (!editing) {
    return (
      <Box>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Column Details</Typography>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={() => setEditing(true)}
          >
            Edit
          </Button>
        </Box>

        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" color="text.secondary">Business Name</Typography>
            <Typography variant="body1">{form.business_name || <em>Not set</em>}</Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" color="text.secondary">Data Type</Typography>
            <Typography variant="body1" fontFamily="monospace">{form.data_type || 'N/A'}</Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2" color="text.secondary">Description</Typography>
            <Typography variant="body1">{form.description || <em>No description</em>}</Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle2" color="text.secondary">Semantic Type</Typography>
            <Chip label={form.semantic_type || 'attribute'} size="small" />
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle2" color="text.secondary">Role</Typography>
            <Chip label={form.role || 'attribute'} size="small" />
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle2" color="text.secondary">Priority</Typography>
            <Chip label={form.priority || 'medium'} size="small" />
          </Grid>

          {form.aliases && form.aliases.length > 0 && (
            <Grid item xs={12}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>Aliases</Typography>
              <Box display="flex" gap={0.5} flexWrap="wrap">
                {form.aliases.map((alias, idx) => (
                  <Chip key={idx} label={alias} size="small" />
                ))}
              </Box>
            </Grid>
          )}

          {form.common_terms && form.common_terms.length > 0 && (
            <Grid item xs={12}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>Common Terms</Typography>
              <Box display="flex" gap={0.5} flexWrap="wrap">
                {form.common_terms.map((term, idx) => (
                  <Chip key={idx} label={term} size="small" variant="outlined" />
                ))}
              </Box>
            </Grid>
          )}

          {form.examples && form.examples.length > 0 && (
            <Grid item xs={12}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>Examples</Typography>
              <Typography variant="body2" fontFamily="monospace">
                {form.examples.join(', ')}
              </Typography>
            </Grid>
          )}

          {form.business_rules && form.business_rules.length > 0 && (
            <Grid item xs={12}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>Business Rules</Typography>
              {form.business_rules.map((rule, idx) => (
                <Typography key={idx} variant="body2">• {rule}</Typography>
              ))}
            </Grid>
          )}

          <Grid item xs={12} md={4}>
            <FormControlLabel
              control={<Switch checked={form.searchable || false} disabled />}
              label="Searchable"
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControlLabel
              control={<Switch checked={form.filterable || false} disabled />}
              label="Filterable"
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControlLabel
              control={<Switch checked={form.aggregatable || false} disabled />}
              label="Aggregatable"
            />
          </Grid>

          {form.user_notes && (
            <Grid item xs={12}>
              <Typography variant="subtitle2" color="text.secondary">User Notes</Typography>
              <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                {form.user_notes}
              </Typography>
            </Grid>
          )}
        </Grid>
      </Box>
    );
  }

  // Edit Mode
  return (
    <Box component={Paper} sx={{ p: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Edit Column Hints</Typography>
        <Box>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSave}
            sx={{ mr: 1 }}
          >
            Save
          </Button>
          <Button
            variant="outlined"
            startIcon={<CancelIcon />}
            onClick={handleCancel}
          >
            Cancel
          </Button>
        </Box>
      </Box>

      <Grid container spacing={2}>
        {/* Basic Info */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Business Name"
            value={form.business_name || ''}
            onChange={(e) => setForm({ ...form, business_name: e.target.value })}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Data Type"
            value={form.data_type || ''}
            onChange={(e) => setForm({ ...form, data_type: e.target.value })}
            disabled
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            multiline
            rows={2}
            label="Description"
            value={form.description || ''}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
        </Grid>

        {/* Dropdowns */}
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Semantic Type</InputLabel>
            <Select
              value={form.semantic_type || 'attribute'}
              label="Semantic Type"
              onChange={(e) => setForm({ ...form, semantic_type: e.target.value })}
            >
              {SEMANTIC_TYPES.map(type => (
                <MenuItem key={type} value={type}>{type}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Role</InputLabel>
            <Select
              value={form.role || 'attribute'}
              label="Role"
              onChange={(e) => setForm({ ...form, role: e.target.value })}
            >
              {ROLES.map(role => (
                <MenuItem key={role} value={role}>{role}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Priority</InputLabel>
            <Select
              value={form.priority || 'medium'}
              label="Priority"
              onChange={(e) => setForm({ ...form, priority: e.target.value })}
            >
              {PRIORITIES.map(priority => (
                <MenuItem key={priority} value={priority}>{priority}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        {/* Aliases */}
        <Grid item xs={12}>
          <Divider sx={{ my: 1 }} />
          <Typography variant="subtitle2" gutterBottom>Aliases</Typography>
          <Box display="flex" gap={1} mb={1}>
            <TextField
              fullWidth
              size="small"
              placeholder="Add alias..."
              value={newAlias}
              onChange={(e) => setNewAlias(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddItem('aliases', newAlias, setNewAlias)}
            />
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={() => handleAddItem('aliases', newAlias, setNewAlias)}
            >
              Add
            </Button>
          </Box>
          <Box display="flex" gap={0.5} flexWrap="wrap">
            {(form.aliases || []).map((alias, idx) => (
              <Chip
                key={idx}
                label={alias}
                size="small"
                onDelete={() => handleRemoveItem('aliases', idx)}
              />
            ))}
          </Box>
        </Grid>

        {/* Common Terms */}
        <Grid item xs={12}>
          <Typography variant="subtitle2" gutterBottom>Common Terms</Typography>
          <Box display="flex" gap={1} mb={1}>
            <TextField
              fullWidth
              size="small"
              placeholder="Add common term..."
              value={newTerm}
              onChange={(e) => setNewTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddItem('common_terms', newTerm, setNewTerm)}
            />
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={() => handleAddItem('common_terms', newTerm, setNewTerm)}
            >
              Add
            </Button>
          </Box>
          <Box display="flex" gap={0.5} flexWrap="wrap">
            {(form.common_terms || []).map((term, idx) => (
              <Chip
                key={idx}
                label={term}
                size="small"
                variant="outlined"
                onDelete={() => handleRemoveItem('common_terms', idx)}
              />
            ))}
          </Box>
        </Grid>

        {/* Examples */}
        <Grid item xs={12}>
          <Typography variant="subtitle2" gutterBottom>Examples</Typography>
          <Box display="flex" gap={1} mb={1}>
            <TextField
              fullWidth
              size="small"
              placeholder="Add example value..."
              value={newExample}
              onChange={(e) => setNewExample(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddItem('examples', newExample, setNewExample)}
            />
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={() => handleAddItem('examples', newExample, setNewExample)}
            >
              Add
            </Button>
          </Box>
          <Box display="flex" gap={0.5} flexWrap="wrap">
            {(form.examples || []).map((example, idx) => (
              <Chip
                key={idx}
                label={example}
                size="small"
                variant="outlined"
                onDelete={() => handleRemoveItem('examples', idx)}
              />
            ))}
          </Box>
        </Grid>

        {/* Business Rules */}
        <Grid item xs={12}>
          <Typography variant="subtitle2" gutterBottom>Business Rules</Typography>
          <Box display="flex" gap={1} mb={1}>
            <TextField
              fullWidth
              size="small"
              placeholder="Add business rule..."
              value={newRule}
              onChange={(e) => setNewRule(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddItem('business_rules', newRule, setNewRule)}
            />
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={() => handleAddItem('business_rules', newRule, setNewRule)}
            >
              Add
            </Button>
          </Box>
          {(form.business_rules || []).map((rule, idx) => (
            <Box key={idx} display="flex" alignItems="center" gap={1} mb={0.5}>
              <Typography variant="body2" sx={{ flex: 1 }}>• {rule}</Typography>
              <IconButton size="small" onClick={() => handleRemoveItem('business_rules', idx)}>
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Box>
          ))}
        </Grid>

        {/* Flags */}
        <Grid item xs={12} md={4}>
          <FormControlLabel
            control={
              <Switch
                checked={form.searchable || false}
                onChange={(e) => setForm({ ...form, searchable: e.target.checked })}
              />
            }
            label="Searchable"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <FormControlLabel
            control={
              <Switch
                checked={form.filterable || false}
                onChange={(e) => setForm({ ...form, filterable: e.target.checked })}
              />
            }
            label="Filterable"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <FormControlLabel
            control={
              <Switch
                checked={form.aggregatable || false}
                onChange={(e) => setForm({ ...form, aggregatable: e.target.checked })}
              />
            }
            label="Aggregatable"
          />
        </Grid>

        {/* User Notes */}
        <Grid item xs={12}>
          <TextField
            fullWidth
            multiline
            rows={2}
            label="User Notes"
            value={form.user_notes || ''}
            onChange={(e) => setForm({ ...form, user_notes: e.target.value })}
          />
        </Grid>
      </Grid>
    </Box>
  );
}

export default ColumnHintEditor;
