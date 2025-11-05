import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Tab,
  Tabs,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  Alert,
  Snackbar,
  CircularProgress,
  Chip,
  TextField,
  InputAdornment
} from '@mui/material';
import {
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Save as SaveIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  AutoAwesome as AutoAwesomeIcon
} from '@mui/icons-material';
import {
  getAllHints,
  getHintsStatistics,
  searchHints,
  createHintsVersion,
  bulkGenerateHints,
  exportHints
} from '../services/api';
import TableHintsView from '../components/TableHintsView';
import HintsSearch from '../components/HintsSearch';
import HintsStatistics from '../components/HintsStatistics';

function HintsManagement() {
  const [tabValue, setTabValue] = useState(0);
  const [allHints, setAllHints] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [hintsResponse, statsResponse] = await Promise.all([
        getAllHints(),
        getHintsStatistics()
      ]);

      setAllHints(hintsResponse.data.data);
      setStatistics(statsResponse.data.data);

      // Select first table by default
      const tables = hintsResponse.data.data?.tables || {};
      const firstTable = Object.keys(tables)[0];
      if (firstTable && !selectedTable) {
        setSelectedTable(firstTable);
      }
    } catch (error) {
      console.error('Error loading hints:', error);
      showSnackbar('Failed to load hints data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      const response = await searchHints({
        search_term: searchTerm,
        limit: 50
      });
      setSearchResults(response.data.data);
      setTabValue(2); // Switch to search tab
    } catch (error) {
      console.error('Error searching hints:', error);
      showSnackbar('Search failed', 'error');
    }
  };

  const handleCreateVersion = async () => {
    const versionName = prompt('Enter version name (e.g., v1.1):');
    if (!versionName) return;

    const comment = prompt('Enter version comment (optional):') || '';

    try {
      await createHintsVersion({
        version_name: versionName,
        user: 'web-user',
        comment: comment
      });
      showSnackbar(`Version ${versionName} created successfully`, 'success');
    } catch (error) {
      console.error('Error creating version:', error);
      showSnackbar('Failed to create version', 'error');
    }
  };

  const handleBulkGenerate = async () => {
    if (!selectedTable) {
      showSnackbar('Please select a table first', 'warning');
      return;
    }

    if (!window.confirm(`Generate hints for all columns in "${selectedTable}"? This may take a few minutes.`)) {
      return;
    }

    setGenerating(true);
    try {
      const response = await bulkGenerateHints({
        table_name: selectedTable,
        schema_path: 'schemas/newdqschemanov.json',
        user: 'web-user',
        overwrite_existing: false
      });

      const data = response.data.data;
      showSnackbar(
        `Generated ${data.generated} hints, skipped ${data.skipped} existing`,
        'success'
      );
      await loadData();
    } catch (error) {
      console.error('Error generating hints:', error);
      showSnackbar('Bulk generation failed', 'error');
    } finally {
      setGenerating(false);
    }
  };

  const handleExport = async () => {
    try {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      await exportHints(`schemas/hints/export_${timestamp}.json`);
      showSnackbar('Hints exported successfully', 'success');
    } catch (error) {
      console.error('Error exporting hints:', error);
      showSnackbar('Export failed', 'error');
    }
  };

  const showSnackbar = (message, severity = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleTableSelect = (tableName) => {
    setSelectedTable(tableName);
    setTabValue(1); // Switch to editor tab
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  const tables = allHints?.tables || {};
  const tableNames = Object.keys(tables);

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Column Hints Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage business-friendly names and metadata for database columns
        </Typography>
      </Box>

      {/* Search Bar */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Search hints by business name, alias, or term..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Box display="flex" gap={1} flexWrap="wrap">
              <Button
                variant="contained"
                startIcon={<SearchIcon />}
                onClick={handleSearch}
              >
                Search
              </Button>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={loadData}
              >
                Refresh
              </Button>
              <Button
                variant="outlined"
                startIcon={<SaveIcon />}
                onClick={handleCreateVersion}
              >
                Save Version
              </Button>
              <Button
                variant="outlined"
                startIcon={<AutoAwesomeIcon />}
                onClick={handleBulkGenerate}
                disabled={!selectedTable || generating}
              >
                {generating ? 'Generating...' : 'Generate Hints'}
              </Button>
              <Button
                variant="outlined"
                startIcon={<DownloadIcon />}
                onClick={handleExport}
              >
                Export
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Statistics Cards */}
      {statistics && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total Tables
                </Typography>
                <Typography variant="h4">{statistics.total_tables}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total Columns
                </Typography>
                <Typography variant="h4">{statistics.total_columns}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Auto-Generated
                </Typography>
                <Typography variant="h4">{statistics.auto_generated}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Manual Verified
                </Typography>
                <Typography variant="h4">{statistics.manual_verified}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Main Content */}
      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={tabValue}
          onChange={(e, newValue) => setTabValue(newValue)}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="Tables Overview" />
          <Tab label="Edit Hints" disabled={!selectedTable} />
          <Tab label="Search Results" />
        </Tabs>

        {/* Tab Panels */}
        <Box sx={{ p: 3 }}>
          {/* Tables Overview Tab */}
          {tabValue === 0 && (
            <Grid container spacing={2}>
              {tableNames.map((tableName) => {
                const tableData = tables[tableName];
                const columnCount = Object.keys(tableData.columns || {}).length;
                const tableHints = tableData.table_hints || {};

                return (
                  <Grid item xs={12} sm={6} md={4} key={tableName}>
                    <Card
                      sx={{
                        cursor: 'pointer',
                        '&:hover': { boxShadow: 3 },
                        border: selectedTable === tableName ? 2 : 0,
                        borderColor: 'primary.main'
                      }}
                      onClick={() => handleTableSelect(tableName)}
                    >
                      <CardContent>
                        <Typography variant="h6" gutterBottom noWrap>
                          {tableHints.business_name || tableName}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {tableName}
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 2 }}>
                          {tableHints.description || 'No description'}
                        </Typography>
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Chip label={`${columnCount} columns`} size="small" />
                          {tableHints.category && (
                            <Chip label={tableHints.category} size="small" color="primary" variant="outlined" />
                          )}
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                );
              })}
            </Grid>
          )}

          {/* Edit Hints Tab */}
          {tabValue === 1 && selectedTable && (
            <TableHintsView
              tableName={selectedTable}
              tableData={tables[selectedTable]}
              onUpdate={loadData}
              showSnackbar={showSnackbar}
            />
          )}

          {/* Search Results Tab */}
          {tabValue === 2 && (
            <HintsSearch
              searchResults={searchResults}
              onSelectColumn={(tableName) => handleTableSelect(tableName)}
            />
          )}
        </Box>
      </Paper>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
}

export default HintsManagement;
