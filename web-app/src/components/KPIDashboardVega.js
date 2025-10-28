import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Button,
  Alert,
  Paper,
  Skeleton,
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
  TablePagination,
  TableRow,
  CircularProgress,
  Chip,
  Grid,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import VegaEmbed from 'vega-embed';
import { API_BASE_URL } from '../services/api';

// Vega Chart Component with Click Handler
const VegaChart = ({ spec, onBarClick, kpis }) => {
  const chartRef = React.useRef(null);
  const [chartError, setChartError] = React.useState(null);

  React.useEffect(() => {
    if (chartRef.current && spec) {
      setChartError(null);
      VegaEmbed(chartRef.current, spec, {
        actions: {
          export: true,
          source: false,
          compiled: false,
          editor: false,
        },
      })
        .then((result) => {
          // Add click event listener to the Vega view
          if (result && result.view) {
            result.view.addEventListener('click', (event, item) => {
              if (item && item.datum) {
                // Find the KPI object that matches the clicked bar
                const clickedKPI = kpis.find(kpi => kpi.id === item.datum.id);
                if (clickedKPI && onBarClick) {
                  onBarClick(clickedKPI);
                }
              }
            });
          }
        })
        .catch((err) => {
          console.error('Vega chart error:', err);
          setChartError(err.message);
        });
    }
  }, [spec, onBarClick, kpis]);

  if (chartError) {
    return (
      <Box sx={{ p: 2, backgroundColor: '#fff3cd', borderRadius: 1, color: '#856404' }}>
        <Typography variant="body2">Chart rendering error: {chartError}</Typography>
      </Box>
    );
  }

  return <div ref={chartRef} style={{ width: '100%', height: '300px', cursor: 'pointer' }} />;
};

const KPIDashboardVega = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [drilldownOpen, setDrilldownOpen] = useState(false);
  const [selectedKPI, setSelectedKPI] = useState(null);
  const [drilldownData, setDrilldownData] = useState(null);
  const [drilldownLoading, setDrilldownLoading] = useState(false);
  const [drilldownError, setDrilldownError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchFilter, setSearchFilter] = useState('');
  const [copiedSQL, setCopiedSQL] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE_URL}/landing-kpi/dashboard`);

      if (!response.ok) {
        throw new Error(`Failed to fetch dashboard data: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Dashboard API Response:', data);

      // Transform data if needed
      let transformedData = data;
      if (data.kpis && !data.groups) {
        // If API returns flat list of KPIs, group them by group_name
        const groupedByName = {};
        data.kpis.forEach(kpi => {
          const groupName = kpi.group || 'Ungrouped';
          if (!groupedByName[groupName]) {
            groupedByName[groupName] = [];
          }
          groupedByName[groupName].push(kpi);
        });
        transformedData = {
          groups: Object.entries(groupedByName).map(([name, kpis]) => ({
            group_name: name,
            kpis: kpis,
          })),
        };
      }

      setDashboardData(transformedData);
    } catch (err) {
      console.error('Error fetching dashboard:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchDrilldownData = async (kpiId) => {
    try {
      setDrilldownLoading(true);
      setDrilldownError(null);
      setPage(0);
      const response = await fetch(`${API_BASE_URL}/landing-kpi/${kpiId}/latest-results`);

      if (!response.ok) {
        throw new Error(`Failed to fetch drill-down data: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Drilldown API Response:', data);

      // Transform API response to match component expectations
      if (data.success && data.results) {
        const transformedData = {
          sql: data.results.sql_query,
          records: data.results.result_data || []
        };
        setDrilldownData(transformedData);
      } else {
        throw new Error('Invalid response structure from API');
      }
    } catch (err) {
      console.error('Error fetching drill-down data:', err);
      setDrilldownError(err.message);
    } finally {
      setDrilldownLoading(false);
    }
  };

  const handleBarClick = (kpi) => {
    setSelectedKPI(kpi);
    setDrilldownOpen(true);
    fetchDrilldownData(kpi.id);
  };

  const handleKPICardClick = (kpi) => {
    handleBarClick(kpi);
  };

  const handleCloseDrilldown = () => {
    setDrilldownOpen(false);
    setSelectedKPI(null);
    setDrilldownData(null);
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const exportToCSV = () => {
    if (!drilldownData?.records || drilldownData.records.length === 0) return;

    const headers = Object.keys(drilldownData.records[0]);
    const csvContent = [
      headers.join(','),
      ...drilldownData.records.map(row =>
        headers.map(header => {
          const value = row[header];
          return typeof value === 'string' && value.includes(',') ? `"${value}"` : value;
        }).join(',')
      ),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedKPI?.name || 'kpi'}_results.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const handleCopySQL = () => {
    if (drilldownData?.sql) {
      navigator.clipboard.writeText(drilldownData.sql);
      setCopiedSQL(true);
      setTimeout(() => setCopiedSQL(false), 2000);
    }
  };

  const getFilteredRecords = () => {
    if (!drilldownData?.records) return [];
    if (!searchFilter) return drilldownData.records;

    return drilldownData.records.filter(record =>
      Object.values(record).some(value =>
        String(value).toLowerCase().includes(searchFilter.toLowerCase())
      )
    );
  };

  const filteredRecords = getFilteredRecords();
  const paginatedRecords = filteredRecords.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
          KPI Dashboard
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} variant="rectangular" height={400} />
          ))}
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
          KPI Dashboard
        </Typography>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button variant="contained" startIcon={<RefreshIcon />} onClick={fetchDashboardData}>
          Retry
        </Button>
      </Container>
    );
  }

  const groups = dashboardData?.groups || [];
  const totalKPIs = groups.reduce((sum, group) => sum + group.kpis.length, 0);

  if (totalKPIs === 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
          KPI Dashboard
        </Typography>
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="body1" color="textSecondary" sx={{ mb: 2 }}>
            No KPIs found. Create your first KPI to get started.
          </Typography>
          <Button variant="contained" href="/landing-kpi">
            Go to KPI Management
          </Button>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
            KPI Dashboard
          </Typography>
          <Typography variant="body2" color="textSecondary">
            {totalKPIs} KPI{totalKPIs !== 1 ? 's' : ''} across {groups.length} group{groups.length !== 1 ? 's' : ''}
          </Typography>
        </Box>
        <Button variant="outlined" startIcon={<RefreshIcon />} onClick={fetchDashboardData}>
          Refresh
        </Button>
      </Box>

      {/* Group Sections with Charts */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {groups.map((group) => (
          <Paper key={group.group_name} sx={{ p: 3, backgroundColor: '#fafafa' }}>
            {/* Group Header */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                {group.group_name}
              </Typography>
            </Box>

            {/* Bar Chart */}
            <Box sx={{ backgroundColor: 'white', p: 2, borderRadius: 1, mb: 2 }}>
              <VegaChart
                spec={{
                  $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
                  description: `KPI metrics for ${group.group_name}`,
                  data: {
                    values: group.kpis.map(kpi => ({
                      name: kpi.name,
                      records: kpi.latest_execution?.record_count || 0,
                      id: kpi.id,
                      definition: kpi.definition || 'No definition available',
                    })),
                  },
                  layer: [
                    {
                      mark: { type: 'bar', cursor: 'pointer', tooltip: true },
                      encoding: {
                        x: {
                          field: 'name',
                          type: 'nominal',
                          axis: { labelAngle: 0, labelLimit: 200, labelFontSize: 14, labelFontWeight: 'bold' },
                          title: 'KPI Name',
                        },
                        y: {
                          field: 'records',
                          type: 'quantitative',
                          title: 'Record Count',
                        },
                        color: {
                          field: 'name',
                          type: 'nominal',
                          scale: { scheme: 'category20' },
                          legend: null,
                        },
                        tooltip: [
                          { field: 'definition', type: 'nominal', title: 'Definition' },
                        ],
                      },
                    },
                    {
                      mark: { type: 'text', align: 'center', baseline: 'bottom', dy: -5, fontSize: 12, fontWeight: 'bold' },
                      encoding: {
                        x: {
                          field: 'name',
                          type: 'nominal',
                        },
                        y: {
                          field: 'records',
                          type: 'quantitative',
                        },
                        text: { field: 'records', type: 'quantitative' },
                      },
                    },
                  ],
                  width: 'container',
                  height: 300,
                  config: {
                    mark: { tooltip: true },
                    axis: { minExtent: 30 },
                  },
                }}
                onBarClick={handleBarClick}
                kpis={group.kpis}
              />
              {/* KPI Cards Below Chart for Click Interaction */}
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 2 }}>
                {group.kpis.map((kpi) => (
                  <Chip
                    key={kpi.id}
                    label={`${kpi.name} (${kpi.latest_execution?.record_count || 0})`}
                    onClick={() => handleKPICardClick(kpi)}
                    color={kpi.latest_execution?.status === 'success' ? 'success' : 'default'}
                    variant="outlined"
                    sx={{ cursor: 'pointer', '&:hover': { backgroundColor: 'action.hover' } }}
                  />
                ))}
              </Box>
            </Box>
          </Paper>
        ))}
      </Box>

      {/* Drill-down Dialog */}
      <Dialog open={drilldownOpen} onClose={handleCloseDrilldown} maxWidth="lg" fullWidth>
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h6">{selectedKPI?.name}</Typography>
            {selectedKPI?.definition && (
              <Typography variant="caption" sx={{ fontStyle: 'italic', color: 'text.secondary' }}>
                {selectedKPI.definition}
              </Typography>
            )}
          </Box>
          <Button onClick={handleCloseDrilldown} size="small">
            <CloseIcon />
          </Button>
        </DialogTitle>

        <DialogContent sx={{ pt: 2 }}>
          {drilldownLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : drilldownError ? (
            <Alert severity="error">{drilldownError}</Alert>
          ) : drilldownData ? (
            <Box>
              {/* Summary Stats */}
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={12} sm={6}>
                  <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#e3f2fd' }}>
                    <Typography variant="body2" color="textSecondary">
                      Total Records
                    </Typography>
                    <Typography variant="h5" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                      {drilldownData.records?.length || 0}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#f3e5f5' }}>
                    <Typography variant="body2" color="textSecondary">
                      Columns
                    </Typography>
                    <Typography variant="h5" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                      {drilldownData.records?.[0] ? Object.keys(drilldownData.records[0]).length : 0}
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>

              {/* Search Filter */}
              <TextField
                fullWidth
                size="small"
                placeholder="Search records..."
                value={searchFilter}
                onChange={(e) => {
                  setSearchFilter(e.target.value);
                  setPage(0);
                }}
                sx={{ mb: 2 }}
              />

              {/* Data Table */}
              {drilldownData.records && drilldownData.records.length > 0 ? (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                        {Object.keys(drilldownData.records[0]).map((header) => (
                          <TableCell key={header} sx={{ fontWeight: 'bold' }}>
                            {header}
                          </TableCell>
                        ))}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {paginatedRecords.map((record, idx) => (
                        <TableRow key={idx} hover>
                          {Object.values(record).map((value, cellIdx) => (
                            <TableCell key={cellIdx}>
                              {value !== null && value !== undefined ? String(value) : '-'}
                            </TableCell>
                          ))}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                  <TablePagination
                    rowsPerPageOptions={[5, 10, 25, 50]}
                    component="div"
                    count={filteredRecords.length}
                    rowsPerPage={rowsPerPage}
                    page={page}
                    onPageChange={handleChangePage}
                    onRowsPerPageChange={handleChangeRowsPerPage}
                  />
                </TableContainer>
              ) : (
                <Alert severity="info">No records found</Alert>
              )}
            </Box>
          ) : null}
        </DialogContent>

        <DialogActions>
          <Button
            onClick={handleCopySQL}
            disabled={!drilldownData?.sql}
            variant={copiedSQL ? 'contained' : 'text'}
            color={copiedSQL ? 'success' : 'primary'}
          >
            {copiedSQL ? 'Copied!' : 'Copy SQL'}
          </Button>
          <Button onClick={exportToCSV} startIcon={<DownloadIcon />} disabled={!drilldownData?.records || drilldownData.records.length === 0}>
            Export CSV
          </Button>
          <Button onClick={handleCloseDrilldown}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default KPIDashboardVega;

