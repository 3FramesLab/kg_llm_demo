import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  Container,
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Paper,
  Skeleton,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  ShowChart as ShowChartIcon,
  Close as CloseIcon,
  Download as DownloadIcon,
  Search as SearchIcon,
} from '@mui/icons-material';
import { VegaEmbed } from 'react-vega';

// Service Dependencies
import { API_BASE_URL, getKPIExecutions } from '../services/api';

/**
 * Helper function to determine background color based on record count
 * Returns color matching the reference image
 */
const getRecordCountColor = (count) => {
  if (count === 0) {
    return '#8bc34a'; // Green for 0
  } else if (count < 10) {
    return '#fdd835'; // Yellow for low counts (1-9)
  } else if (count < 50) {
    return '#ffca28'; // Amber for 10-49
  } else if (count < 100) {
    return '#ff9800'; // Orange for 50-99
  } else if (count < 1000) {
    return '#ff6f00'; // Dark orange for 100-999
  } else {
    return '#e53935'; // Red for 1000+
  }
};

/**
 * DashboardTrendsWidget - A reusable, self-contained component for displaying KPI trends
 *
 * This component handles its own data fetching, state management, and error handling.
 * It can be easily integrated into any part of the application.
 *
 * @component
 *
 * @requires KPIResultsViewDialog - Component for displaying detailed KPI execution results
 * @requires API_BASE_URL - API base URL from services/api
 * @requires getKPIExecutions - API function from services/api for fetching execution history
 *
 * @param {Object} props - Component props
 * @param {string} props.maxWidth - Maximum width of the container (default: "xl")
 * @param {Object} props.containerSx - Custom styles for the container
 * @param {Function} props.onKPIClick - Callback function when a KPI card is clicked. Receives (kpi, action) where action is 'view-results' or 'view-trend'
 * @param {string} props.emptyStateRedirectUrl - URL for the "Go to KPI Management" button (default: "/landing-kpi")
 *
 * @example
 * // Basic usage
 * <DashboardTrendsWidget />
 *
 * @example
 * // With customization
 * <DashboardTrendsWidget
 *   onKPIClick={(kpi, action) => console.log(kpi, action)}
 * />
 */
const DashboardTrendsWidget = ({
  maxWidth = "xl",
  containerSx = {},
  onKPIClick,
  emptyStateRedirectUrl = "/landing-kpi",
}) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedKPI, setSelectedKPI] = useState(null);
  const [resultsDialogOpen, setResultsDialogOpen] = useState(false);
  const [trendChartDialogOpen, setTrendChartDialogOpen] = useState(false);
  const [selectedKPIForChart, setSelectedKPIForChart] = useState(null);
  const [detailedTrendData, setDetailedTrendData] = useState([]);

  // Results dialog state
  const [results, setResults] = useState(null);
  const [resultsLoading, setResultsLoading] = useState(false);
  const [resultsError, setResultsError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchFilter, setSearchFilter] = useState('');

  // Vega-Lite specification for the trend chart
  const getVegaSpec = (data) => ({
    $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
    width: 'container',
    height: 350,
    data: { values: data },
    layer: [
      {
        // Line and points layer
        mark: {
          type: 'line',
          point: {
            filled: true,
            fill: '#6366f1',
            size: 100
          },
          color: '#6366f1',
          strokeWidth: 3,
          interpolate: 'linear',
          tooltip: true
        },
        encoding: {
          x: {
            field: 'date',
            type: 'ordinal',
            axis: {
              title: null,
              labelAngle: 0,
              labelFontSize: 12,
              labelColor: '#6b7280'
            }
          },
          y: {
            field: 'records',
            type: 'quantitative',
            scale: {
              domain: {
                unionWith: [
                  { expr: 'floor(domain("y")[0] * 0.95)' },
                  { expr: 'ceil(domain("y")[1] * 1.05)' }
                ]
              }
            },
            axis: {
              title: 'Record Count',
              titleFontSize: 14,
              titleColor: '#6b7280',
              labelFontSize: 12,
              labelColor: '#6b7280',
              grid: true,
              gridColor: '#e5e7eb',
              gridDash: [3, 3]
            }
          },
          tooltip: [
            { field: 'date', type: 'ordinal', title: 'Date' },
            { field: 'records', type: 'quantitative', title: 'Records', format: ',' }
          ]
        }
      },
      {
        // Text labels layer
        mark: {
          type: 'text',
          align: 'center',
          baseline: 'bottom',
          dy: -10,
          fontSize: 12,
          fontWeight: 600,
          color: '#111827'
        },
        encoding: {
          x: {
            field: 'date',
            type: 'ordinal'
          },
          y: {
            field: 'records',
            type: 'quantitative'
          },
          text: {
            field: 'records',
            type: 'quantitative',
            format: ','
          }
        }
      }
    ],
    config: {
      view: {
        stroke: 'transparent'
      },
      axis: {
        domainColor: '#e5e7eb'
      }
    }
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/landing-kpi/dashboard`);
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setDashboardData({ groups: [] });
    } finally {
      setLoading(false);
    }
  };

  const handleViewResults = async (kpi) => {
    setSelectedKPI(kpi);
    setResultsDialogOpen(true);

    if (onKPIClick) {
      onKPIClick(kpi, 'view-results');
    }

    // Fetch results
    try {
      setResultsLoading(true);
      setResultsError(null);
      const response = await fetch(`${API_BASE_URL}/landing-kpi/${kpi.id}/latest-results`);

      if (!response.ok) {
        throw new Error(`Failed to fetch results: ${response.statusText}`);
      }

      const data = await response.json();
      setResults(data.results);
      setPage(0);
    } catch (err) {
      console.error('Error fetching results:', err);
      setResultsError(err.message);
    } finally {
      setResultsLoading(false);
    }
  };

  const handleSparklineClick = async (kpi) => {
    setSelectedKPIForChart(kpi);
    setTrendChartDialogOpen(true);

    if (onKPIClick) {
      onKPIClick(kpi, 'view-trend');
    }

    // Fetch execution data when sparkline is clicked
    try {
      const result = await getKPIExecutions(kpi.id);

      if (result.data.success && result.data.executions) {
        // Get last 10 executions and extract record counts
        const executions = result.data.executions
          .filter(exec => exec.execution_status === 'success' && exec.number_of_records != null)
          .slice(0, 10)
          .reverse(); // Oldest to newest for chart

        const chartData = executions.map((exec) => ({
          date: new Date(exec.execution_timestamp).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric'
          }),
          records: exec.number_of_records,
          fullDate: exec.execution_timestamp
        }));
        setDetailedTrendData(chartData);
      } else {
        setDetailedTrendData([]);
      }
    } catch (error) {
      console.error('Error fetching execution data:', error);
      setDetailedTrendData([]);
    }
  };

  const handleRecordsClick = (kpi) => {
    // Same action as View Results button
    handleViewResults(kpi);
  };

  const handleChangePage = (_event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleDownloadCSV = () => {
    if (!results?.result_data || results.result_data.length === 0) return;

    const headers = results.column_names || [];
    const rows = results.result_data.map((row) =>
      headers.map((header) => {
        const value = row[header];
        // Escape quotes and wrap in quotes if contains comma
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      })
    );

    const csv = [
      headers.join(','),
      ...rows.map((row) => row.join(',')),
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedKPI.name}-results.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const handleCloseResultsDialog = () => {
    setResultsDialogOpen(false);
    setResults(null);
    setResultsError(null);
    setPage(0);
    setSearchFilter('');
  };

  // Filter results based on search term
  const getFilteredResults = () => {
    if (!results?.result_data || !searchFilter.trim()) {
      return results?.result_data || [];
    }

    const searchLower = searchFilter.toLowerCase();
    return results.result_data.filter((row) => {
      return results.column_names?.some((col) => {
        const value = row[col];
        return String(value ?? '').toLowerCase().includes(searchLower);
      });
    });
  };

  if (loading) {
    return (
      <Container maxWidth={maxWidth} sx={{ p: 0, ...containerSx }}>
        {/* Content Skeletons */}
        <Grid container spacing={1.5}>
          {[1, 2, 3, 4].map((i) => (
            <Grid item xs={12} md={6} key={i}>
              <Skeleton
                variant="rectangular"
                height={250}
                sx={{ borderRadius: 1.5, boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}
              />
            </Grid>
          ))}
        </Grid>
      </Container>
    );
  }

  // Filter groups based on selected owners
  const groups = dashboardData?.groups || [];

  const totalKPIs = groups.reduce((sum, group) => sum + group.kpis.length, 0);

  if (totalKPIs === 0) {
    return (
      <Container maxWidth={maxWidth} sx={{ p: 0, ...containerSx }}>
        {/* Empty State */}
        <Paper
          elevation={0}
          sx={{
            p: 3,
            textAlign: 'center',
            borderRadius: 2,
            border: '2px dashed #e5e7eb',
            bgcolor: '#fafbfc',
            boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
          }}
        >
          <Box
            sx={{
              width: 60,
              height: 60,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1rem',
              boxShadow: '0 4px 12px rgba(99, 102, 241, 0.2)'
            }}
          >
            <AssessmentIcon sx={{ fontSize: 32, color: 'white' }} />
          </Box>
          <Typography variant="h6" fontWeight="700" sx={{ mb: 0.75, color: '#111827', fontSize: '1.125rem', letterSpacing: '-0.01em' }}>
            No KPIs Available
          </Typography>
          <Typography variant="body2" fontSize="0.875rem" sx={{ mb: 2, maxWidth: 450, mx: 'auto', lineHeight: 1.5, color: '#6b7280' }}>
            Get started by creating your first KPI to monitor and track your key performance indicators.
          </Typography>
          <Button
            variant="contained"
            href={emptyStateRedirectUrl}
            size="small"
            sx={{
              py: 0.75,
              px: 2,
              borderRadius: 1.5,
              fontSize: '0.8125rem',
              fontWeight: 600,
              textTransform: 'none',
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              boxShadow: '0 2px 8px rgba(99, 102, 241, 0.2)',
              '&:hover': {
                background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
                boxShadow: '0 4px 12px rgba(99, 102, 241, 0.3)',
                transform: 'translateY(-1px)'
              },
              transition: 'all 0.2s ease-in-out'
            }}
          >
            Go to KPI Management
          </Button>
        </Paper>
      </Container>
    );
  }

  return (
    <Box
      sx={{
        width: '100%',
        height: 'calc(100vh - 100px)',
        bgcolor: '#f9fafb',
        p: 2,
        overflow: 'auto',
        boxSizing: 'border-box',
      }}
    >
        <Container maxWidth={maxWidth} sx={{ p: 0, ...containerSx }}>
          {/* KPI Cards - Grouped Card Layout */}
          <Grid container>
            {groups.map((group, groupIndex) => (
              <Grid item xs={12} md={6} key={groupIndex}>
                <Card
                  elevation={0}
                  sx={{
                    height: '100%',
                    borderRadius: 3,
                    border: '1px solid #c5c5c5ff',
                    overflow: 'hidden',
                    bgcolor: 'white',
                  }}
                >
                  {/* Group Header */}
                  <Box
                    sx={{
                      bgcolor: '#7cb342',
                      color: 'white',
                      px: 1.5,
                      py: 0.625,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      position: 'relative',
                    }}
                  >
                    <Typography
                      variant="h6"
                      sx={{
                        fontWeight: 700,
                        fontSize: '0.9375rem',
                        letterSpacing: '0.02em',
                      }}
                    >
                      {group.group_name}
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        color: 'white',
                        bgcolor: '#7cb342',
                        borderColor: 'white',
                        borderWidth: '1.5px',
                        textTransform: 'none',
                        fontWeight: 500,
                        fontSize: '0.8125rem',
                        px: 1,
                        py: 0.125,
                        pr:2,
                        minWidth: 'auto',
                        minHeight: 'auto',
                        borderRadius: 0.5,
                        boxShadow: 'none',
                        position: 'absolute',
                        right: 3,
                      }}
                    >
                      Trends
                    </Typography>
                  </Box>

                  {/* KPIs List */}
                  <CardContent sx={{ p: 0, mt: 2, borderTop: '1px solid #e0e0e0', mx: 1.5, mr: 2.5 }}>
                    {group.kpis.map((kpi) => (
                      <Box
                        key={kpi.id}
                        onClick={() => handleRecordsClick(kpi)}
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          px: 1.25,
                          pr: 0,
                          borderBottom: '1px solid #e0e0e0',
                          cursor: 'pointer',
                          '&:last-child': {
                            borderBottom: 'none',
                          },
                        }}
                      >
                        {/* KPI Name */}
                        <Box sx={{ flex: 1, pr: 1 }}>
                          <Typography
                            variant="body2"
                            sx={{
                              color: '#616161',
                              fontSize: '0.8125rem',
                              fontWeight: 400,
                              lineHeight: 1.4,
                            }}
                          >
                            {kpi.name}
                          </Typography>
                        </Box>
                        
                        {/* Sparkline */}
                        {kpi.latest_execution && (
                          <Box
                            onClick={(e) => {
                              e.stopPropagation();
                              handleSparklineClick(kpi);
                            }}
                            sx={{
                              width: 60,
                              height: 24,
                              mr: 1,
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              '&:hover': {
                                opacity: 0.7,
                              },
                            }}
                          >
                            <ShowChartIcon
                              sx={{
                                fontSize: 20,
                                color: '#6366f1',
                              }}
                            />
                          </Box>
                        )}
                        {/* Record Count Badge */}
                        {kpi.latest_execution ? (
                          <Box
                            sx={{
                              minWidth: 50,
                              maxWidth: 50,
                              px: 0.875,
                              py: 0.25,
                              borderRadius: 0.375,
                              bgcolor: getRecordCountColor(kpi.latest_execution.record_count),
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'flex-end',
                            }}
                          >
                            <Typography
                              variant="body2"
                              sx={{
                                fontSize: '0.8125rem',
                                fontWeight: 700,
                                color: '#212121',
                                lineHeight: 1.2,
                              }}
                            >
                              {kpi.latest_execution.record_count.toLocaleString()}
                            </Typography>
                          </Box>
                        ) : (
                          <Box
                            sx={{
                              minWidth: 35,
                              px: 0.875,
                              py: 0.25,
                              borderRadius: 0.375,
                              bgcolor: '#e0e0e0',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'flex-end',
                            }}
                          >
                            <Typography
                              variant="body2"
                              sx={{
                                fontSize: '0.8125rem',
                                fontWeight: 700,
                                color: '#757575',
                                lineHeight: 1.2,
                              }}
                            >
                              N/A
                            </Typography>
                          </Box>
                        )}
                      </Box>
                    ))}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Results Dialog */}
          <Dialog
            open={resultsDialogOpen}
            onClose={handleCloseResultsDialog}
            maxWidth="lg"
            fullWidth
            PaperProps={{
              sx: {
                borderRadius: 2,
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)'
              }
            }}
          >
            <DialogTitle
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                pb: 2,
                borderBottom: '1px solid #e5e7eb'
              }}
            >
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 700, color: '#111827' }}>
                  {selectedKPI?.name || 'KPI'} - Results
                </Typography>
              </Box>
              <IconButton
                onClick={handleCloseResultsDialog}
                sx={{
                  color: '#6b7280',
                  '&:hover': {
                    bgcolor: '#f3f4f6'
                  }
                }}
              >
                <CloseIcon />
              </IconButton>
            </DialogTitle>

            <DialogContent sx={{ pt: 3, pb: 2 }}>
              {resultsLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                  <CircularProgress />
                </Box>
              ) : resultsError ? (
                <Alert severity="error">{resultsError}</Alert>
              ) : !results ? (
                <Alert severity="info">No results available</Alert>
              ) : (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                  {/* Results Table Section */}
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                        Query Results ({results.record_count || 0} records)
                      </Typography>
                      <TextField
                        size="small"
                        placeholder="Search in results..."
                        value={searchFilter}
                        onChange={(e) => {
                          setSearchFilter(e.target.value);
                          setPage(0); // Reset to first page when searching
                        }}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <SearchIcon sx={{ color: '#9ca3af', fontSize: 20 }} />
                            </InputAdornment>
                          ),
                        }}
                        sx={{
                          width: 300,
                          '& .MuiOutlinedInput-root': {
                            borderRadius: 1.5,
                            bgcolor: '#f9fafb',
                            '&:hover': {
                              bgcolor: '#f3f4f6',
                            },
                            '&.Mui-focused': {
                              bgcolor: 'white',
                            }
                          }
                        }}
                      />
                    </Box>
                    {results.result_data && results.result_data.length > 0 ? (
                      <>
                        <TableContainer component={Paper}>
                          <Table size="small">
                            <TableHead>
                              <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                                {results.column_names?.map((col) => (
                                  <TableCell key={col} sx={{ fontWeight: 'bold' }}>
                                    {col}
                                  </TableCell>
                                ))}
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {getFilteredResults()
                                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                                .map((row, idx) => (
                                  <TableRow key={idx}>
                                    {results.column_names?.map((col) => (
                                      <TableCell key={`${idx}-${col}`}>
                                        {String(row[col] ?? '')}
                                      </TableCell>
                                    ))}
                                  </TableRow>
                                ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                        {getFilteredResults().length === 0 ? (
                          <Alert severity="info" sx={{ mt: 2 }}>
                            No results match your search criteria
                          </Alert>
                        ) : (
                          <TablePagination
                            rowsPerPageOptions={[5, 10, 25, 50]}
                            component="div"
                            count={getFilteredResults().length}
                            rowsPerPage={rowsPerPage}
                            page={page}
                            onPageChange={handleChangePage}
                            onRowsPerPageChange={handleChangeRowsPerPage}
                          />
                        )}
                      </>
                    ) : (
                      <Alert severity="info">No data returned from query</Alert>
                    )}
                  </Box>
                </Box>
              )}
            </DialogContent>

            <DialogActions sx={{ px: 3, py: 2, borderTop: '1px solid #e5e7eb' }}>
              <Button
                startIcon={<DownloadIcon />}
                onClick={handleDownloadCSV}
                disabled={!results?.result_data || results.result_data.length === 0}
                sx={{
                  textTransform: 'none',
                  fontWeight: 600
                }}
              >
                Download CSV
              </Button>
              <Button
                onClick={handleCloseResultsDialog}
                variant="contained"
                sx={{
                  bgcolor: '#6366f1',
                  color: 'white',
                  textTransform: 'none',
                  fontWeight: 600,
                  px: 3,
                  '&:hover': {
                    bgcolor: '#4f46e5'
                  }
                }}
              >
                Close
              </Button>
            </DialogActions>
          </Dialog>

          {/* Trend Chart Dialog */}
          <Dialog
            open={trendChartDialogOpen}
            onClose={() => setTrendChartDialogOpen(false)}
            maxWidth="md"
            fullWidth
            PaperProps={{
              sx: {
                borderRadius: 2,
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)'
              }
            }}
          >
            <DialogTitle
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                pb: 2,
                borderBottom: '1px solid #e5e7eb'
              }}
            >
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 700, color: '#111827', mb: 0.5 }}>
                  {selectedKPIForChart?.name || 'KPI'} - Trend Analysis
                </Typography>
                <Typography variant="body2" sx={{ color: '#6b7280', fontSize: '0.875rem' }}>
                  Last 7 days execution history
                </Typography>
              </Box>
              <IconButton
                onClick={() => setTrendChartDialogOpen(false)}
                sx={{
                  color: '#6b7280',
                  '&:hover': {
                    bgcolor: '#f3f4f6'
                  }
                }}
              >
                <CloseIcon />
              </IconButton>
            </DialogTitle>

            <DialogContent sx={{ pt: 3, pb: 2 }}>
              {detailedTrendData.length > 0 ? (
                <Box sx={{ width: '100%', height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <VegaEmbed
                    spec={getVegaSpec(detailedTrendData)}
                    actions={false}
                    style={{ width: '100%' }}
                  />
                </Box>
              ) : (
                <Box
                  sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    height: 300,
                    color: '#9ca3af'
                  }}
                >
                  <ShowChartIcon sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
                  <Typography variant="body1" sx={{ fontWeight: 600 }}>
                    No trend data available
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Execute this KPI to start collecting trend data
                  </Typography>
                </Box>
              )}
            </DialogContent>

            <DialogActions sx={{ px: 3, py: 2, borderTop: '1px solid #e5e7eb' }}>
              <Button
                onClick={() => setTrendChartDialogOpen(false)}
                variant="contained"
                sx={{
                  bgcolor: '#6366f1',
                  color: 'white',
                  textTransform: 'none',
                  fontWeight: 600,
                  px: 3,
                  '&:hover': {
                    bgcolor: '#4f46e5'
                  }
                }}
              >
                Close
              </Button>
            </DialogActions>
          </Dialog>
        </Container>
      </Box>
  );
};

DashboardTrendsWidget.propTypes = {
  maxWidth: PropTypes.string,
  containerSx: PropTypes.object,
  onKPIClick: PropTypes.func,
  emptyStateRedirectUrl: PropTypes.string,
};

export default DashboardTrendsWidget;

