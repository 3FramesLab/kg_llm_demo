import { useState, useEffect } from 'react';
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
  MenuItem,
  Chip,
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  ShowChart as ShowChartIcon,
  Close as CloseIcon,
  Download as DownloadIcon,
  Search as SearchIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { VegaEmbed } from 'react-vega';

// Service Dependencies
import { getDashboardData, getLatestResults, getKPIExecutions, getUniqueOpsPlanner } from '../services/api';

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
 * Helper function to generate Vega-Lite specification for trend chart
 * @param {Array} data - Array of data points with date and records fields
 * @returns {Object} Vega-Lite specification object
 */
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

  // OPS Planner filter state
  const [selectedOpsPlanner, setSelectedOpsPlanner] = useState('');
  const [availableOpsPlanner, setAvailableOpsPlanner] = useState([]);
  const [loadingOpsPlanner, setLoadingOpsPlanner] = useState(true);
  const [opsSearchQuery, setOpsSearchQuery] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setLoadingOpsPlanner(true);
    try {
      const response = await getDashboardData();
      const data = 
      setDashboardData(data);

      // Fetch unique OPS Planners from hana master
      try {
        const opsResponse = await getUniqueOpsPlanner();
        if (opsResponse.data && opsResponse.data.success) {
          setAvailableOpsPlanner(opsResponse.data.data || []);
        } else {
          setAvailableOpsPlanner([]);
        }
      } catch (opsError) {
        console.error('Error fetching OPS Planners:', opsError);
        setAvailableOpsPlanner([]);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setDashboardData({ groups: [] });
      setAvailableOpsPlanner([]);
    } finally {
      setLoading(false);
      setLoadingOpsPlanner(false);
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
      const response = await getLatestResults(kpi.id);

      // getLatestResults uses axios, so response.data contains the parsed JSON
      const data = response.data;
      console.log('🔍 Latest results response:', data);

      // Handle different response formats
      let resultsData = null;
      if (data.success && data.results) {
        resultsData = data.results;
      } else if (data.results) {
        resultsData = data.results;
      } else if (data.success && data.data) {
        resultsData = data.data;
      }

      console.log('📊 Processed results data:', resultsData);
      setResults(resultsData);
      setPage(0);
    } catch (err) {
      console.error('Error fetching results:', err);

      // Handle specific error cases gracefully
      let errorMessage = err.message;

      // Check if it's a 404 error (no execution results found)
      if (err.response?.status === 404) {
        const errorDetail = err.response?.data?.detail || err.response?.data?.error || err.message;
        if (errorDetail.includes('No execution results found')) {
          errorMessage = `No execution results found for this KPI. The KPI may not have been executed yet or may not have any successful executions with data.`;
        } else {
          errorMessage = errorDetail;
        }
      }
      // Check if it's a network error
      else if (err.code === 'NETWORK_ERROR' || err.message.includes('Network Error')) {
        errorMessage = 'Unable to connect to the server. Please check your connection and try again.';
      }
      // Check for other HTTP errors
      else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.response?.data?.error) {
        errorMessage = err.response.data.error;
      }

      setResultsError(errorMessage);
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

      // Handle different response formats from getKPIExecutions
      let executions = [];
      if (result.data) {
        if (result.data.success && result.data.executions) {
          executions = result.data.executions;
        } else if (result.data.executions) {
          executions = result.data.executions;
        } else if (Array.isArray(result.data)) {
          executions = result.data;
        }
      }

      if (executions.length > 0) {
        // Get last 10 executions and extract record counts
        const filteredExecutions = executions
          .filter(exec => exec.execution_status === 'success' && exec.number_of_records != null)
          .slice(0, 10)
          .reverse(); // Oldest to newest for chart

        const chartData = filteredExecutions.map((exec) => ({
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

      // Log specific error details for debugging
      if (error.response?.status === 404) {
        console.log(`ℹ️ No execution history found for KPI ${kpi.id}`);
      }

      setDetailedTrendData([]);
    }
  };

  const handleRecordsClick = (kpi) => {
    // Same action as View Results button
    handleViewResults(kpi);
  };

  const handleOpsplannerChange = (event) => {
    setSelectedOpsPlanner(event.target.value);
  };

  // Function to filter results data based on ops_planner
  const filterResultsByOpsPlanner = (resultData, columnNames) => {
    if (!selectedOpsPlanner || !resultData || !Array.isArray(resultData)) {
      return resultData;
    }

    // Check if ops_planner column exists (case insensitive)
    const opsColumnName = columnNames?.find(col =>
      col.toLowerCase().includes('ops_planner') ||
      col.toLowerCase().includes('ops planner') ||
      col.toLowerCase() === 'ops_planner'
    );

    if (!opsColumnName) {
      // No ops_planner column found, return original data
      return resultData;
    }

    // Filter data based on selected ops_planner
    return resultData.filter(row => {
      const opsValue = row[opsColumnName];
      return opsValue && opsValue.toString().toLowerCase().includes(selectedOpsPlanner.toLowerCase());
    });
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
    a.download = `${selectedKPI.alias_name || selectedKPI.name}-results.csv`;
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
    // Reset OPS planner filter when dialog closes
    setSelectedOpsPlanner('');
    setOpsSearchQuery('');
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

  // Define custom group order based on the reference image
  const customGroupOrder = [
    'GPU Product Master vs RBP',
    'NBU Product Master vs RBP',
    'GPU Master Product List Quality',
    'NBU Master Product List Quality',
    'GPU Product Master List vs SKU/IFNR',
    'NBU Product Master List vs SKU/IFNR',
    'GPU Product Master List vs SAR > 0 (total incoming supply)',
    'NBU Product Master List vs SAR > 0 (total incoming supply)',
  ];

  // Sort groups based on custom order
  const sortGroupsByCustomOrder = (groups) => {
    return [...groups].sort((a, b) => {
      const indexA = customGroupOrder.indexOf(a.group_name);
      const indexB = customGroupOrder.indexOf(b.group_name);

      // If both groups are in the custom order, sort by their position
      if (indexA !== -1 && indexB !== -1) {
        return indexA - indexB;
      }

      // If only one group is in the custom order, prioritize it
      if (indexA !== -1) return -1;
      if (indexB !== -1) return 1;

      // If neither group is in the custom order, sort alphabetically
      return a.group_name.localeCompare(b.group_name);
    });
  };

  // Filter groups based on selected owners and apply custom ordering
  const rawGroups = dashboardData?.groups || [];
  const groups = sortGroupsByCustomOrder(rawGroups);

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
        gap: 1,
        p: 2,
      }}
    >
      {/* Main Content Area */}
      <Box
        sx={{
          flex: 1,
          minWidth: 0,
          marginRight: { xs: 0, lg: '200px' }, // Reserve space for right sidebar
        }}
      >
        <Container maxWidth={maxWidth} sx={{ p: 0, ...containerSx }}>
          {/* KPI Cards - Grouped Card Layout */}
          <Grid container spacing={2}>
            {groups.map((group, groupIndex) => (
              <Grid item xs={12} md={6} key={groupIndex}>
                <Card
                  elevation={0}
                  sx={{
                    height: '100%',
                    borderRadius: 1.5,
                    border: '1px solid #c5c5c5',
                    overflow: 'hidden',
                    bgcolor: 'white',
                    boxShadow: 'none',
                  }}
                >
                  {/* Group Header */}
                  <Box
                    sx={{
                      bgcolor: '#7cb342',
                      color: 'white',
                      px: 1.5,
                      pr: 0,
                      py: 0.5,
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
                        border: '1px solid white',
                        borderRadius: 1,
                        textTransform: 'none',
                        fontWeight: 500,
                        fontSize: '0.8125rem',
                        px: 1,
                        py: 0.125,

                        mr: 2,
                        minWidth: 'auto',
                        minHeight: 'auto',
                        boxShadow: 'none',
                        position: 'absolute',
                        right: 0,

                      }}
                    >
                      Trends
                    </Typography>
                  </Box>

                  {/* KPIs List */}
                  <CardContent sx={{ p: 0, mt: 3, borderTop: '1px solid #f2f2f2', mr: 1.5 }}>
                    {group.kpis.map((kpi) => (
                      <Box
                        key={kpi.id}
                        onClick={() => handleRecordsClick(kpi)}
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          px: 1.5,
                          pr: 0,
                          cursor: 'pointer',
                          borderBottom: '1px solid #f2f2f2',
                        }}
                      >
                        {/* KPI Name */}
                        <Box sx={{ flex: 1, pr: 1.5, display: 'flex', alignItems: 'center', gap: 1, }}>
                          {/* Sparkline Icon */}
                          <Box
                            onClick={(e) => {
                              e.stopPropagation();
                              handleSparklineClick(kpi);
                            }}
                            sx={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              cursor: 'pointer'
                            }}
                          >
                            <ShowChartIcon
                              sx={{
                                fontSize: 18,
                                color: '#6366f1',
                                opacity: 1,
                                fontWeight: 700,
                              }}
                            />
                          </Box>

                          <Typography
                            className="kpi-name"
                            variant="body2"
                            sx={{
                              color: '#4b5563',
                              fontSize: '0.875rem',
                              transition: 'color 0.15s ease',
                            }}
                          >
                            {kpi.alias_name || kpi.name}
                          </Typography>
                        </Box>

                        {/* Record Count Badge */}
                        {kpi.latest_execution ? (
                          <Box
                            className="record-count"
                            sx={{
                              minWidth: 100,
                              maxWidth: 100,
                              px: 1.5,
                              borderRadius: 0.5,
                              bgcolor: getRecordCountColor(kpi.latest_execution.record_count),
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              transition: 'transform 0.15s ease',
                            }}
                          >
                            <Typography
                              variant="h6"
                              sx={{
                                fontSize: '1rem',
                                fontWeight: 700,
                                color: '#1f2937',
                              }}
                            >
                              {kpi.latest_execution.record_count.toLocaleString()}
                            </Typography>
                          </Box>
                        ) : (
                          <Box
                            sx={{
                              minWidth: 100,
                              maxWidth: 100,
                              px: 1.5,
                              borderRadius: 0.5,
                              bgcolor: '#f3f4f6',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                            }}
                          >
                            <Typography
                              variant="body2"
                              sx={{
                                fontSize: '0.6875rem',
                                fontWeight: 600,
                                color: '#9ca3af',
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
                  {selectedKPI?.alias_name || selectedKPI?.name || 'KPI'} - Results
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
              {/* OPS Planner Filter Section - Only show when results are available */}
              {!resultsLoading && !resultsError && results?.result_data && (
                <Box sx={{ mb: 3, p: 2, bgcolor: '#f8fafc', borderRadius: 2, border: '1px solid #e2e8f0' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <AssessmentIcon sx={{ fontSize: 20, color: '#6366f1' }} />
                    <Typography
                      variant="subtitle2"
                      sx={{
                        color: '#374151',
                        fontWeight: 600,
                        fontSize: '0.875rem',
                      }}
                    >
                      Filter Results by OPS Planner
                    </Typography>
                  </Box>

                  {loadingOpsPlanner ? (
                    <Skeleton variant="rectangular" width="100%" height={40} sx={{ borderRadius: 1 }} />
                  ) : availableOpsPlanner.length > 0 ? (
                    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
                      {/* OPS Planner Dropdown */}
                      <TextField
                        select
                        size="small"
                        value={selectedOpsPlanner}
                        onChange={handleOpsplannerChange}
                        placeholder="Select OPS Planner"
                        sx={{
                          minWidth: 200,
                          '& .MuiOutlinedInput-root': {
                            fontSize: '0.875rem',
                            borderRadius: 1,
                            bgcolor: selectedOpsPlanner ? '#e0e7ff' : 'white',
                            '&:hover': {
                              bgcolor: selectedOpsPlanner ? '#ddd6fe' : '#f9fafb',
                            },
                          },
                        }}
                      >
                        <MenuItem value="">
                          <em>All OPS Planners</em>
                        </MenuItem>
                        {(() => {
                          const filteredPlanners = availableOpsPlanner.filter(planner =>
                            planner.toLowerCase().includes(opsSearchQuery.toLowerCase())
                          );

                          return filteredPlanners.map((planner) => (
                            <MenuItem key={planner} value={planner}>
                              {planner}
                            </MenuItem>
                          ));
                        })()}
                      </TextField>

                      {/* Search Input for OPS Planner */}
                      <TextField
                        size="small"
                        placeholder="Search planners..."
                        value={opsSearchQuery}
                        onChange={(e) => setOpsSearchQuery(e.target.value)}
                        sx={{
                          minWidth: 150,
                          '& .MuiOutlinedInput-root': {
                            fontSize: '0.875rem',
                            borderRadius: 1,
                            bgcolor: 'white',
                          },
                        }}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <SearchIcon sx={{ fontSize: 18, color: '#9ca3af' }} />
                            </InputAdornment>
                          ),
                          endAdornment: opsSearchQuery && (
                            <InputAdornment position="end">
                              <IconButton
                                size="small"
                                onClick={() => setOpsSearchQuery('')}
                                sx={{ p: 0.5 }}
                              >
                                <ClearIcon sx={{ fontSize: 16, color: '#9ca3af' }} />
                              </IconButton>
                            </InputAdornment>
                          ),
                        }}
                      />

                      {/* Filter Status Chip */}
                      {selectedOpsPlanner && (
                        <Chip
                          label={`Filtered by: ${selectedOpsPlanner}`}
                          size="small"
                          onDelete={() => setSelectedOpsPlanner('')}
                          sx={{
                            bgcolor: '#e0e7ff',
                            color: '#4f46e5',
                            fontWeight: 600,
                            '& .MuiChip-deleteIcon': {
                              color: '#4f46e5',
                              '&:hover': {
                                color: '#3730a3',
                              },
                            },
                          }}
                        />
                      )}
                    </Box>
                  ) : (
                    <Alert severity="info" sx={{ fontSize: '0.875rem' }}>
                      No OPS planners available for filtering
                    </Alert>
                  )}

                  {/* Filter Info */}
                  {(() => {
                    const hasOpsColumn = results?.column_names?.find(col =>
                      col.toLowerCase().includes('ops_planner') ||
                      col.toLowerCase().includes('ops planner') ||
                      col.toLowerCase() === 'ops_planner'
                    );

                    if (!hasOpsColumn) {
                      return (
                        <Alert severity="info" sx={{ mt: 2, fontSize: '0.875rem' }}>
                          This KPI result doesn't include an OPS Planner column. Filter will have no effect.
                        </Alert>
                      );
                    }

                    return null;
                  })()}
                </Box>
              )}

              {resultsLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                  <CircularProgress />
                </Box>
              ) : resultsError ? (
                <Alert
                  severity={resultsError.includes('No execution results found') ? 'info' : 'error'}
                  sx={{ mb: 2 }}
                >
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
                      {resultsError.includes('No execution results found') ? 'No Results Available' : 'Error Loading Results'}
                    </Typography>
                    <Typography variant="body2">
                      {resultsError}
                    </Typography>
                    {resultsError.includes('No execution results found') && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="body2" sx={{ fontStyle: 'italic', color: 'text.secondary' }}>
                          💡 To see results here:
                        </Typography>
                        <Typography variant="body2" sx={{ ml: 2, color: 'text.secondary' }}>
                          • Execute this KPI from the KPI Management page
                        </Typography>
                        <Typography variant="body2" sx={{ ml: 2, color: 'text.secondary' }}>
                          • Ensure the execution completes successfully
                        </Typography>
                        <Typography variant="body2" sx={{ ml: 2, color: 'text.secondary' }}>
                          • Results will appear here after successful execution
                        </Typography>
                      </Box>
                    )}
                  </Box>
                </Alert>
              ) : !results ? (
                <Alert severity="info">No results available</Alert>
              ) : (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                  {/* Results Table Section */}
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                      Query Results ({(() => {
                        const filteredResults = filterResultsByOpsPlanner(results?.result_data, results?.column_names);
                        const originalCount = results?.number_of_records || results?.record_count || 0;
                        const filteredCount = filteredResults?.length || 0;

                        if (selectedOpsPlanner && filteredCount !== originalCount) {
                          return `${filteredCount} of ${originalCount} records (filtered by OPS Planner)`;
                        }
                        return `${originalCount} records`;
                      })()} )
                    </Typography>

                    {(() => {
                      // Apply ops_planner filter to results
                      const filteredResults = filterResultsByOpsPlanner(
                        results?.result_data,
                        results?.column_names
                      );

                      return filteredResults && filteredResults.length > 0 ? (
                        <>
                          <TableContainer component={Paper}>
                            <Table size="small">
                              <TableHead>
                                <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                                  {results.column_names?.map((col) => (
                                    <TableCell key={col} sx={{ fontWeight: 'bold' }}>
                                      {col}
                                      {/* Add filter indicator for ops_planner column */}
                                      {selectedOpsPlanner && (
                                        col.toLowerCase().includes('ops_planner') ||
                                        col.toLowerCase().includes('ops planner') ||
                                        col.toLowerCase() === 'ops_planner'
                                      ) && (
                                          <Chip
                                            label={`Filtered: ${selectedOpsPlanner}`}
                                            size="small"
                                            color="primary"
                                            sx={{ ml: 1, fontSize: '0.6rem', height: '16px' }}
                                          />
                                        )}
                                    </TableCell>
                                  )) || (
                                      // Fallback: use keys from first row if column_names not available
                                      filteredResults[0] && Object.keys(filteredResults[0]).map((col) => (
                                        <TableCell key={col} sx={{ fontWeight: 'bold' }}>
                                          {col}
                                          {/* Add filter indicator for ops_planner column */}
                                          {selectedOpsPlanner && (
                                            col.toLowerCase().includes('ops_planner') ||
                                            col.toLowerCase().includes('ops planner') ||
                                            col.toLowerCase() === 'ops_planner'
                                          ) && (
                                              <Chip
                                                label={`Filtered: ${selectedOpsPlanner}`}
                                                size="small"
                                                color="primary"
                                                sx={{ ml: 1, fontSize: '0.6rem', height: '16px' }}
                                              />
                                            )}
                                        </TableCell>
                                      ))
                                    )}
                                </TableRow>
                              </TableHead>
                              <TableBody>
                                {filteredResults
                                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                                  .map((row, idx) => (
                                    <TableRow key={idx}>
                                      {(results.column_names || Object.keys(row))?.map((col) => (
                                        <TableCell key={`${idx}-${col}`}>
                                          {String(row[col] ?? '')}
                                        </TableCell>
                                      ))}
                                    </TableRow>
                                  ))}
                              </TableBody>
                            </Table>
                          </TableContainer>
                          <TablePagination
                            rowsPerPageOptions={[5, 10, 25, 50]}
                            component="div"
                            count={filteredResults.length}
                            rowsPerPage={rowsPerPage}
                            page={page}
                            onPageChange={handleChangePage}
                            onRowsPerPageChange={handleChangeRowsPerPage}
                          />
                        </>
                      ) : results ? (
                        <Box>
                          <Alert severity="info" sx={{ mb: 2 }}>
                            No result_data found in response
                          </Alert>
                          <Box sx={{ p: 2, bgcolor: '#f9f9f9', borderRadius: 1 }}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                              Raw Response Data:
                            </Typography>
                            <pre style={{ fontSize: '0.8rem', overflow: 'auto', maxHeight: '200px' }}>
                              {JSON.stringify(results, null, 2)}
                            </pre>
                          </Box>
                        </Box>
                      ) : (
                        <Alert severity="info">No results available</Alert>
                      );
                    })()}
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
                  {selectedKPIForChart?.alias_name || selectedKPIForChart?.name || 'KPI'} - Trend Analysis
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
                  <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
                    Execute this KPI multiple times to start collecting trend data
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1, textAlign: 'center', fontSize: '0.875rem', fontStyle: 'italic' }}>
                    Trend charts show execution history over time
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

