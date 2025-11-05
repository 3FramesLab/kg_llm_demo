import React, { useState } from 'react';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
  Collapse,
  TextField,
  Button,
  Grid,
  Divider,
  Tooltip
} from '@mui/material';
import {
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  AutoAwesome as AutoAwesomeIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import { updateTableHints, updateColumnHints, generateColumnHints } from '../services/api';
import ColumnHintEditor from './ColumnHintEditor';

function TableHintsView({ tableName, tableData, onUpdate, showSnackbar }) {
  const [editingTableHints, setEditingTableHints] = useState(false);
  const [tableHintsForm, setTableHintsForm] = useState(tableData?.table_hints || {});
  const [expandedColumn, setExpandedColumn] = useState(null);
  const [generating, setGenerating] = useState({});

  const columns = tableData?.columns || {};
  const columnNames = Object.keys(columns);

  const handleSaveTableHints = async () => {
    try {
      await updateTableHints({
        table_name: tableName,
        user: 'web-user',
        hints: tableHintsForm
      });
      showSnackbar('Table hints updated successfully', 'success');
      setEditingTableHints(false);
      onUpdate();
    } catch (error) {
      console.error('Error updating table hints:', error);
      showSnackbar('Failed to update table hints', 'error');
    }
  };

  const handleGenerateColumnHint = async (columnName, columnType) => {
    setGenerating({ ...generating, [columnName]: true });
    try {
      await generateColumnHints({
        table_name: tableName,
        column_name: columnName,
        column_type: columnType,
        user: 'web-user'
      });
      showSnackbar(`Generated hints for ${columnName}`, 'success');
      onUpdate();
    } catch (error) {
      console.error('Error generating hints:', error);
      showSnackbar(`Failed to generate hints for ${columnName}`, 'error');
    } finally {
      setGenerating({ ...generating, [columnName]: false });
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'default';
      default: return 'default';
    }
  };

  return (
    <Box>
      {/* Table-Level Hints */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Table Information</Typography>
          {!editingTableHints ? (
            <IconButton onClick={() => setEditingTableHints(true)}>
              <EditIcon />
            </IconButton>
          ) : (
            <Box>
              <IconButton color="primary" onClick={handleSaveTableHints}>
                <SaveIcon />
              </IconButton>
              <IconButton onClick={() => {
                setEditingTableHints(false);
                setTableHintsForm(tableData?.table_hints || {});
              }}>
                <CancelIcon />
              </IconButton>
            </Box>
          )}
        </Box>

        {editingTableHints ? (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Business Name"
                value={tableHintsForm.business_name || ''}
                onChange={(e) => setTableHintsForm({ ...tableHintsForm, business_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="Description"
                value={tableHintsForm.description || ''}
                onChange={(e) => setTableHintsForm({ ...tableHintsForm, description: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Aliases (comma-separated)"
                value={(tableHintsForm.aliases || []).join(', ')}
                onChange={(e) => setTableHintsForm({
                  ...tableHintsForm,
                  aliases: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
                })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Category"
                value={tableHintsForm.category || ''}
                onChange={(e) => setTableHintsForm({ ...tableHintsForm, category: e.target.value })}
                placeholder="master_data, transaction, reference"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="User Notes"
                value={tableHintsForm.user_notes || ''}
                onChange={(e) => setTableHintsForm({ ...tableHintsForm, user_notes: e.target.value })}
              />
            </Grid>
          </Grid>
        ) : (
          <Box>
            <Typography variant="subtitle1" gutterBottom>
              <strong>Business Name:</strong> {tableHintsForm.business_name || tableName}
            </Typography>
            <Typography variant="body2" gutterBottom>
              <strong>Description:</strong> {tableHintsForm.description || 'No description'}
            </Typography>
            {tableHintsForm.aliases && tableHintsForm.aliases.length > 0 && (
              <Box mt={1}>
                <Typography variant="body2" gutterBottom><strong>Aliases:</strong></Typography>
                <Box display="flex" gap={0.5} flexWrap="wrap">
                  {tableHintsForm.aliases.map((alias, idx) => (
                    <Chip key={idx} label={alias} size="small" />
                  ))}
                </Box>
              </Box>
            )}
            {tableHintsForm.category && (
              <Typography variant="body2" sx={{ mt: 1 }}>
                <strong>Category:</strong> {tableHintsForm.category}
              </Typography>
            )}
            {tableHintsForm.user_notes && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                <em>{tableHintsForm.user_notes}</em>
              </Typography>
            )}
          </Box>
        )}
      </Paper>

      {/* Columns List */}
      <Typography variant="h6" gutterBottom>
        Columns ({columnNames.length})
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell width={50}></TableCell>
              <TableCell><strong>Column</strong></TableCell>
              <TableCell><strong>Business Name</strong></TableCell>
              <TableCell><strong>Type</strong></TableCell>
              <TableCell><strong>Priority</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
              <TableCell align="right"><strong>Actions</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {columnNames.map((columnName) => {
              const columnHints = columns[columnName];
              const isExpanded = expandedColumn === columnName;

              return (
                <React.Fragment key={columnName}>
                  <TableRow hover>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => setExpandedColumn(isExpanded ? null : columnName)}
                      >
                        {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                      </IconButton>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontFamily="monospace">
                        {columnName}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {columnHints.business_name || <em>Not set</em>}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={columnHints.semantic_type || 'attribute'}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={columnHints.priority || 'medium'}
                        size="small"
                        color={getPriorityColor(columnHints.priority)}
                      />
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={0.5}>
                        {columnHints.manual_verified && (
                          <Tooltip title="Manually verified">
                            <CheckCircleIcon fontSize="small" color="success" />
                          </Tooltip>
                        )}
                        {columnHints.auto_generated && !columnHints.manual_verified && (
                          <Tooltip title="Auto-generated">
                            <AutoAwesomeIcon fontSize="small" color="info" />
                          </Tooltip>
                        )}
                        {!columnHints.business_name && (
                          <Tooltip title="Needs review">
                            <WarningIcon fontSize="small" color="warning" />
                          </Tooltip>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="Generate with AI">
                        <IconButton
                          size="small"
                          onClick={() => handleGenerateColumnHint(columnName, columnHints.data_type)}
                          disabled={generating[columnName]}
                        >
                          <AutoAwesomeIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell colSpan={7} sx={{ py: 0, border: 0 }}>
                      <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                        <Box sx={{ p: 2, bgcolor: 'grey.50' }}>
                          <ColumnHintEditor
                            tableName={tableName}
                            columnName={columnName}
                            columnHints={columnHints}
                            onUpdate={onUpdate}
                            showSnackbar={showSnackbar}
                          />
                        </Box>
                      </Collapse>
                    </TableCell>
                  </TableRow>
                </React.Fragment>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default TableHintsView;
