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
  Tooltip,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Checkbox,
  FormControlLabel,
  Chip,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Assessment as AssessmentIcon,
  ShowChart as ShowChartIcon,
  Close as CloseIcon,
  Download as DownloadIcon,
  Person as PersonIcon,
  Search as SearchIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { VegaEmbed } from 'react-vega';

// Service Dependencies
import { API_BASE_URL, getKPIExecutions } from '../services/api';

/**
 * Helper function to determine background color based on record count
 * Returns color similar to the reference image
 */
const getRecordCountColor = (count) => {
  if (count === 0) {
    return '#86efac'; // Green for 0
  } else if (count < 10) {
    return '#fde047'; // Yellow for low counts
  } else if (count < 100) {
    return '#fcd34d'; // Darker yellow
  } else if (count < 1000) {
    return '#fbbf24'; // Orange-yellow
  } else {
    return '#fb923c'; // Orange for high counts
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
 * @param {string} props.title - Custom title for the dashboard (default: "Dashboard Trends")
 * @param {string} props.subtitle - Custom subtitle (default: "Monitor and track your key performance indicators")
 * @param {string} props.maxWidth - Maximum width of the container (default: "xl")
 * @param {Object} props.containerSx - Custom styles for the container
 * @param {boolean} props.showHeader - Whether to show the header section (default: true)
 * @param {boolean} props.showRefreshButton - Whether to show the refresh button (default: true)
 * @param {Function} props.onRefresh - Callback function when refresh is triggered
 * @param {Function} props.onKPIClick - Callback function when a KPI card is clicked. Receives (kpi, action) where action is 'view-results' or 'view-trend'
 * @param {string} props.emptyStateRedirectUrl - URL for the "Go to KPI Management" button (default: "/landing-kpi")
 * @param {number} props.gridSpacing - Spacing between grid items (default: 1)
 * @param {Object} props.gridItemProps - Custom props for grid items (default: {xs: 12, sm: 6, md: 4, lg: 3})
 *
 * @example
 * // Basic usage
 * <DashboardTrendsWidget />
 *
 * @example
 * // With customization
 * <DashboardTrendsWidget
 *   title="My Dashboard"
 *   subtitle="Custom subtitle"
 *   onKPIClick={(kpi, action) => console.log(kpi, action)}
 *   onRefresh={() => console.log('Refreshed')}
 * />
 */
const DashboardTrendsWidget = ({
  title = "Dashboard Trends",
  subtitle = "Monitor and track your key performance indicators",
  maxWidth = "xl",
  containerSx = {},
  showHeader = true,
  showRefreshButton = true,
  onRefresh,
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

  // Owner filter state
  const [selectedOwners, setSelectedOwners] = useState([]);
  const [availableOwners, setAvailableOwners] = useState([]);
  const [loadingOwners, setLoadingOwners] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

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
    setLoadingOwners(true);
    try {
      const response = await fetch(`${API_BASE_URL}/landing-kpi/dashboard`);
      const data = await response.json();
      setDashboardData(data);

      // Extract unique owners from all KPIs in all groups
      const ownersSet = new Set();
      if (data.groups) {
        data.groups.forEach(group => {
          if (group.kpis) {
            group.kpis.forEach(kpi => {
              if (kpi.created_by) {
                ownersSet.add(kpi.created_by);
              } else {
                ownersSet.add('Unassigned');
              }
            });
          }
        });
      }
      setAvailableOwners(Array.from(ownersSet).sort());
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setDashboardData({ groups: [] });
      setAvailableOwners([]);
    } finally {
      setLoading(false);
      setLoadingOwners(false);
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

  const handleRefresh = () => {
    fetchDashboardData();
    if (onRefresh) {
      onRefresh();
    }
  };

  const handleOwnerToggle = (owner) => {
    setSelectedOwners(prev => {
      if (prev.includes(owner)) {
        return prev.filter(o => o !== owner);
      } else {
        return [...prev, owner];
      }
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
  };

  if (loading) {
    return (
      <Container maxWidth={maxWidth} sx={{ p: 0, ...containerSx }}>
        {/* Header Skeleton */}
        {showHeader && (
          <Paper
            elevation={0}
            sx={{
              mb: 1.5,
              p: 1.25,
              borderRadius: 2,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              boxShadow: '0 2px 8px rgba(102, 126, 234, 0.2)',
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 1.5 }}>
              <Box sx={{ flex: '1 1 auto', minWidth: '200px' }}>
                <Skeleton variant="text" width={200} height={32} sx={{ bgcolor: 'rgba(255,255,255,0.2)' }} />
                <Skeleton variant="text" width={150} height={20} sx={{ bgcolor: 'rgba(255,255,255,0.15)', mt: 0.25 }} />
              </Box>
            </Box>
          </Paper>
        )}

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
  const allGroups = dashboardData?.groups || [];
  const groups = selectedOwners.length > 0
    ? allGroups.map(group => ({
        ...group,
        kpis: group.kpis.filter(kpi =>
          selectedOwners.includes(kpi.created_by) ||
          (selectedOwners.includes('Unassigned') && !kpi.created_by)
        )
      })).filter(group => group.kpis.length > 0)
    : allGroups;

  const totalKPIs = groups.reduce((sum, group) => sum + group.kpis.length, 0);

  if (totalKPIs === 0) {
    return (
      <Container maxWidth={maxWidth} sx={{ p: 0, ...containerSx }}>
        {/* Header */}
        {showHeader && (
          <Paper
            elevation={0}
            sx={{
              mb: 1.5,
              p: 1.25,
              borderRadius: 2,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              boxShadow: '0 2px 8px rgba(102, 126, 234, 0.2)',
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 1.5 }}>
              <Box sx={{ flex: '1 1 auto', minWidth: '200px' }}>
                <Typography variant="h5" fontWeight="700" sx={{ mb: 0.25, lineHeight: 1.2, fontSize: '1.25rem', letterSpacing: '-0.02em' }}>
                  {title}
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 500, fontSize: '0.875rem', opacity: 0.95 }}>
                  {subtitle}
                </Typography>
              </Box>
            </Box>
          </Paper>
        )}

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
        display: 'flex',
        width: '100%',
        minHeight: '100vh',
        bgcolor: '#f9fafb',
        gap: 2,
        p: 2,
      }}
    >
      {/* Left Sidebar - 15% */}
      <Box
        sx={{
          width: '15%',
          minWidth: '180px',
          display: { xs: 'none', lg: 'block' },
        }}
      >
        <Paper
          elevation={0}
          sx={{
            height: '100%',
            borderRadius: 2,
            border: '1px solid #e5e7eb',
            p: 2,
            bgcolor: 'white',
          }}
        >
          <Typography
            variant="subtitle2"
            sx={{
              color: '#9ca3af',
              fontWeight: 600,
              fontSize: '0.75rem',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              mb: 2,
            }}
          >
            Reserved Space
          </Typography>
          <Typography
            variant="body2"
            sx={{
              color: '#6b7280',
              fontSize: '0.875rem',
              fontStyle: 'italic',
            }}
          >
            Available for future features
          </Typography>
        </Paper>
      </Box>

      {/* Center Area - 70% */}
      <Box
        sx={{
          flex: 1,
          width: { xs: '100%', lg: '70%' },
          minWidth: 0,
        }}
      >
        <Container maxWidth={maxWidth} sx={{ p: 0, ...containerSx }}>
      {/* Header Section */}
      {showHeader && (
        <Paper
          elevation={0}
          sx={{
            mb: 1.5,
            p: 1.25,
            borderRadius: 2,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            boxShadow: '0 2px 8px rgba(102, 126, 234, 0.2)',
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 1.5 }}>
            {/* Left Side - Title and Subtitle */}
            <Box sx={{ flex: '1 1 auto', minWidth: '200px' }}>
              <Typography variant="h5" fontWeight="700" sx={{ mb: 0.25, lineHeight: 1.2, fontSize: '1.125rem' }}>
                {title}
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 500, fontSize: '0.875rem', opacity: 0.95 }}>
                {subtitle}
              </Typography>
            </Box>

            {/* Right Side - Refresh Icon */}
            {showRefreshButton && (
              <Tooltip title="Refresh Dashboard">
                <IconButton
                  onClick={handleRefresh}
                  disabled={loading}
                  size="small"
                  sx={{
                    color: 'white',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    },
                    '&:disabled': {
                      color: 'rgba(255, 255, 255, 0.5)',
                    },
                  }}
                >
                  <RefreshIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        </Paper>
      )}

      {/* KPI Cards - Grouped Card Layout */}
      <Grid container spacing={1.5}>
        {groups.map((group, groupIndex) => (
          <Grid item xs={12} md={6} key={groupIndex}>
            <Card
              elevation={0}
              sx={{
                height: '100%',
                borderRadius: 1.5,
                border: '1.5px solid #e5e7eb',
                overflow: 'hidden',
                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
                  borderColor: '#84cc16',
                },
              }}
            >
              {/* Group Header */}
              <Box
                sx={{
                  background: 'linear-gradient(135deg, #84cc16 0%, #65a30d 100%)',
                  color: 'white',
                  px: 1.5,
                  py: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 700,
                    fontSize: '0.9375rem',
                    letterSpacing: '-0.01em',
                  }}
                >
                  {group.group_name}
                </Typography>
                <Button
                  size="small"
                  variant="outlined"
                  sx={{
                    color: 'white',
                    borderColor: 'rgba(255, 255, 255, 0.5)',
                    textTransform: 'none',
                    fontWeight: 600,
                    fontSize: '0.6875rem',
                    px: 1,
                    py: 0.25,
                    minWidth: 'auto',
                    minHeight: 'auto',
                    '&:hover': {
                      borderColor: 'white',
                      bgcolor: 'rgba(255, 255, 255, 0.1)',
                    },
                  }}
                >
                  Trends
                </Button>
              </Box>

              {/* KPIs List */}
              <CardContent sx={{ p: 0 }}>
                {group.kpis.map((kpi, kpiIndex) => (
                  <Box
                    key={kpi.id}
                    onClick={() => handleRecordsClick(kpi)}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      px: 1.5,
                      py: 1,
                      borderBottom: kpiIndex < group.kpis.length - 1 ? '1px solid #f3f4f6' : 'none',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                      '&:hover': {
                        bgcolor: '#f9fafb',
                        '& .kpi-name': {
                          color: '#84cc16',
                        },
                        '& .record-count': {
                          transform: 'scale(1.05)',
                        },
                      },
                    }}
                  >
                    {/* KPI Name */}
                    <Box sx={{ flex: 1, pr: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
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
                          cursor: 'pointer',
                          transition: 'all 0.15s ease',
                          '&:hover': {
                            transform: 'scale(1.15)',
                          },
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
                          fontWeight: 500,
                          lineHeight: 1.3,
                          transition: 'color 0.15s ease',
                        }}
                      >
                        {kpi.name}
                      </Typography>
                    </Box>

                    {/* Record Count Badge */}
                    {kpi.latest_execution ? (
                      <Box
                        className="record-count"
                        sx={{
                          minWidth: 50,
                          px: 1.5,
                          py: 0.5,
                          borderRadius: 1,
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
                            lineHeight: 1,
                          }}
                        >
                          {kpi.latest_execution.record_count.toLocaleString()}
                        </Typography>
                      </Box>
                    ) : (
                      <Box
                        sx={{
                          minWidth: 50,
                          px: 1.5,
                          py: 0.5,
                          borderRadius: 1,
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
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                  Query Results ({results.record_count || 0} records)
                </Typography>
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
                          {results.result_data
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
                    <TablePagination
                      rowsPerPageOptions={[5, 10, 25, 50]}
                      component="div"
                      count={results.result_data.length}
                      rowsPerPage={rowsPerPage}
                      page={page}
                      onPageChange={handleChangePage}
                      onRowsPerPageChange={handleChangeRowsPerPage}
                    />
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

      {/* Right Sidebar - 15% */}
      <Box
        sx={{
          width: '15%',
          minWidth: '180px',
          display: { xs: 'none', lg: 'block' },
        }}
      >
        <Paper
          elevation={0}
          sx={{
            height: 'fit-content',
            maxHeight: 'calc(100vh - 32px)',
            overflowY: 'auto',
            borderRadius: 2,
            border: '1px solid #e5e7eb',
            bgcolor: 'white',
            position: 'sticky',
            top: 16,
          }}
        >
          {/* Header */}
          <Box
            sx={{
              p: 2,
              borderBottom: '1px solid #e5e7eb',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              borderRadius: '8px 8px 0 0',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
              <PersonIcon sx={{ fontSize: 20, color: 'white' }} />
              <Typography
                variant="h6"
                sx={{
                  color: 'white',
                  fontWeight: 700,
                  fontSize: '0.9375rem',
                  letterSpacing: '-0.01em',
                }}
              >
                Filters
              </Typography>
            </Box>
            <Typography
              variant="caption"
              sx={{
                color: 'rgba(255, 255, 255, 0.9)',
                fontSize: '0.75rem',
              }}
            >
              {loadingOwners ? 'Loading...' : `Filter KPIs by planner`}
            </Typography>
          </Box>

          {/* Owner Filter Section */}
          <Box sx={{ p: 1.5 }}>
            {loadingOwners ? (
              // Loading skeleton
              <>
                {[1, 2, 3].map((i) => (
                  <Box key={i} sx={{ mb: 1 }}>
                    <Skeleton variant="rectangular" width="100%" height={32} sx={{ borderRadius: 1 }} />
                  </Box>
                ))}
              </>
            ) : availableOwners.length > 0 ? (
              <>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1.5 }}>
                  <PersonIcon sx={{ fontSize: 16, color: '#6b7280' }} />
                  <Typography
                    variant="subtitle2"
                    sx={{
                      color: '#6b7280',
                      fontWeight: 600,
                      fontSize: '0.75rem',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                    }}
                  >
                    Filter by Planner
                  </Typography>
                </Box>

                {/* Search Input */}
                <TextField
                  size="small"
                  placeholder="Search planners..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  sx={{
                    mb: 1.5,
                    '& .MuiOutlinedInput-root': {
                      fontSize: '0.8125rem',
                      borderRadius: 1,
                      bgcolor: '#f9fafb',
                      '&:hover': {
                        bgcolor: '#f3f4f6',
                      },
                      '&.Mui-focused': {
                        bgcolor: 'white',
                      },
                    },
                    '& .MuiOutlinedInput-input': {
                      py: 0.75,
                    },
                  }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon sx={{ fontSize: 18, color: '#9ca3af' }} />
                      </InputAdornment>
                    ),
                    endAdornment: searchQuery && (
                      <InputAdornment position="end">
                        <IconButton
                          size="small"
                          onClick={() => setSearchQuery('')}
                          sx={{
                            p: 0.5,
                            '&:hover': {
                              bgcolor: '#f3f4f6',
                            },
                          }}
                        >
                          <ClearIcon sx={{ fontSize: 16, color: '#9ca3af' }} />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />

                <Box sx={{ maxHeight: '400px', overflowY: 'auto' }}>
                  {(() => {
                    const filteredOwners = availableOwners.filter(owner =>
                      owner.toLowerCase().includes(searchQuery.toLowerCase())
                    );

                    if (filteredOwners.length === 0) {
                      return (
                        <Box
                          sx={{
                            textAlign: 'center',
                            py: 3,
                            px: 2,
                          }}
                        >
                          <SearchIcon sx={{ fontSize: 40, color: '#d1d5db', mb: 1 }} />
                          <Typography
                            variant="body2"
                            sx={{
                              color: '#6b7280',
                              fontSize: '0.8125rem',
                            }}
                          >
                            No planners found
                          </Typography>
                          <Typography
                            variant="caption"
                            sx={{
                              color: '#9ca3af',
                              fontSize: '0.75rem',
                            }}
                          >
                            Try a different search term
                          </Typography>
                        </Box>
                      );
                    }

                    return filteredOwners.map((owner) => (
                      <FormControlLabel
                        key={owner}
                        control={
                          <Checkbox
                            checked={selectedOwners.includes(owner)}
                            onChange={() => handleOwnerToggle(owner)}
                            size="small"
                            sx={{
                              py: 0.25,
                              '&.Mui-checked': {
                                color: '#6366f1',
                              },
                            }}
                          />
                        }
                        label={
                          <Typography
                            variant="body2"
                            sx={{
                              fontSize: '0.8125rem',
                              color: '#374151',
                            }}
                          >
                            {owner}
                          </Typography>
                        }
                        sx={{
                          display: 'flex',
                          ml: 0,
                          mb: 0.25,
                          '&:hover': {
                            bgcolor: '#f9fafb',
                            borderRadius: 1,
                          },
                        }}
                      />
                    ));
                  })()}
                </Box>
                {selectedOwners.length > 0 && (
                  <Box sx={{ mt: 1.5 }}>
                    <Chip
                      label={`${selectedOwners.length} selected`}
                      size="small"
                      onDelete={() => setSelectedOwners([])}
                      sx={{
                        height: 20,
                        fontSize: '0.6875rem',
                        bgcolor: '#e0e7ff',
                        color: '#4f46e5',
                        fontWeight: 600,
                        '& .MuiChip-deleteIcon': {
                          fontSize: '0.875rem',
                          color: '#4f46e5',
                          '&:hover': {
                            color: '#3730a3',
                          },
                        },
                      }}
                    />
                  </Box>
                )}
              </>
            ) : (
              // Empty state
              <Box
                sx={{
                  textAlign: 'center',
                  py: 4,
                  px: 2,
                }}
              >
                <PersonIcon sx={{ fontSize: 48, color: '#d1d5db', mb: 1 }} />
                <Typography
                  variant="body2"
                  sx={{
                    color: '#6b7280',
                    fontSize: '0.8125rem',
                  }}
                >
                  No planners available
                </Typography>
              </Box>
            )}
          </Box>
        </Paper>
      </Box>
    </Box>
  );
};

DashboardTrendsWidget.propTypes = {
  title: PropTypes.string,
  subtitle: PropTypes.string,
  maxWidth: PropTypes.string,
  containerSx: PropTypes.object,
  showHeader: PropTypes.bool,
  showRefreshButton: PropTypes.bool,
  onRefresh: PropTypes.func,
  onKPIClick: PropTypes.func,
  emptyStateRedirectUrl: PropTypes.string,
};

export default DashboardTrendsWidget;

