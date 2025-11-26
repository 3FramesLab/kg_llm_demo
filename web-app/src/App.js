import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Layout from './components/Layout';
import Overview from './pages/Overview';
import Schemas from './pages/Schemas';
import KnowledgeGraph from './pages/KnowledgeGraph';
import RelationshipAndKGGeneration from './pages/RelationshipAndKGGeneration';
import LandingKPIManagement from './pages/LandingKPIManagement';
import DashboardTrends from './pages/DashboardTrends';
import HintsManagement from './pages/HintsManagement';
import KPIExecutionHistoryPage from './pages/KPIExecutionHistoryPage';
import Settings from './pages/Settings';
import MasterPage from './pages/MasterPage';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 500,
    },
  },
  components: {
    MuiContainer: {
      styleOverrides: {
        root: {
          // Remove max-width constraint for all breakpoints
          maxWidth: 'none !important',
          // Set padding to 16px for screens >= 600px
          '@media (min-width: 600px)': {
            paddingLeft: '14px',
            paddingRight: '14px',
          },
        },
      },
    },
    // Standardized TextField styling
    MuiTextField: {
      defaultProps: {
        size: 'small',
      },
      styleOverrides: {
        root: {
          '& .MuiInputLabel-root': {
            fontSize: '0.875rem',
            color: '#6B7280',
            '&.Mui-focused': {
              color: '#5B6FE5',
            },
          },
          '& .MuiOutlinedInput-root': {
            fontSize: '0.875rem',
            backgroundColor: '#FFFFFF',
            '& fieldset': {
              borderColor: '#E5E7EB',
            },
            '&:hover fieldset': {
              borderColor: '#D1D5DB',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#5B6FE5',
              borderWidth: '1px',
            },
            '& input': {
              padding: '8.5px 14px',
              color: '#1F2937',
            },
            '& textarea': {
              padding: '8.5px 14px',
              color: '#1F2937',
            },
          },
          '& .MuiFormHelperText-root': {
            fontSize: '0.75rem',
            color: '#6B7280',
            marginLeft: '2px',
            marginTop: '4px',
          },
          '& .MuiInputBase-input::placeholder': {
            color: '#9CA3AF',
            opacity: 1,
          },
        },
      },
    },
    // Standardized Select styling
    MuiSelect: {
      defaultProps: {
        size: 'small',
      },
      styleOverrides: {
        root: {
          fontSize: '0.875rem',
          '& .MuiOutlinedInput-notchedOutline': {
            borderColor: '#E5E7EB',
          },
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: '#D1D5DB',
          },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderColor: '#5B6FE5',
            borderWidth: '1px',
          },
        },
        select: {
          padding: '8.5px 14px',
          color: '#1F2937',
          backgroundColor: '#FFFFFF',
        },
      },
    },
    // Standardized FormControl styling
    MuiFormControl: {
      defaultProps: {
        size: 'small',
      },
      styleOverrides: {
        root: {
          '& .MuiInputLabel-root': {
            fontSize: '0.875rem',
            color: '#6B7280',
            '&.Mui-focused': {
              color: '#5B6FE5',
            },
          },
        },
      },
    },
    // Standardized Autocomplete styling
    MuiAutocomplete: {
      defaultProps: {
        size: 'small',
      },
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            fontSize: '0.875rem',
            backgroundColor: '#FFFFFF',
            padding: '2px 9px',
            '& fieldset': {
              borderColor: '#E5E7EB',
            },
            '&:hover fieldset': {
              borderColor: '#D1D5DB',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#5B6FE5',
              borderWidth: '1px',
            },
            '& input': {
              padding: '6.5px 5px',
              color: '#1F2937',
            },
          },
        },
        inputRoot: {
          '&[class*="MuiOutlinedInput-root"]': {
            padding: '2px 9px',
          },
        },
      },
    },
    // Standardized InputLabel styling
    MuiInputLabel: {
      styleOverrides: {
        root: {
          fontSize: '0.875rem',
          color: '#6B7280',
          '&.Mui-focused': {
            color: '#5B6FE5',
          },
        },
      },
    },
    // Standardized Button styling
    MuiButton: {
      defaultProps: {
        disableElevation: true,
      },
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: '8px',
          fontSize: '0.875rem',
          padding: '8px 16px',
          height: '36px',
          minHeight: 'unset',
          lineHeight: 1.2,
          transition: 'all 0.2s ease-in-out',
          '& .MuiButton-startIcon': {
            marginRight: '6px',
            marginLeft: '-2px',
            '& > *:nth-of-type(1)': {
              fontSize: '18px',
            },
          },
          '& .MuiButton-endIcon': {
            marginLeft: '6px',
            marginRight: '-2px',
            '& > *:nth-of-type(1)': {
              fontSize: '18px',
            },
          },
        },
        // Size variants
        sizeSmall: {
          fontSize: '0.8125rem',
          padding: '6px 12px',
          height: '32px',
          minHeight: 'unset',
          lineHeight: 1.2,
          '& .MuiButton-startIcon': {
            marginRight: '6px',
            marginLeft: '-2px',
            '& > *:nth-of-type(1)': {
              fontSize: '16px',
            },
          },
          '& .MuiButton-endIcon': {
            marginLeft: '6px',
            marginRight: '-2px',
            '& > *:nth-of-type(1)': {
              fontSize: '16px',
            },
          },
        },
        sizeMedium: {
          fontSize: '0.875rem',
          padding: '8px 16px',
          height: '36px',
          minHeight: 'unset',
          lineHeight: 1.2,
        },
        sizeLarge: {
          fontSize: '0.9375rem',
          padding: '10px 20px',
          height: '40px',
          minHeight: 'unset',
          lineHeight: 1.2,
        },
        // Contained variant (Primary buttons)
        contained: {
          backgroundColor: '#5B6FE5',
          color: '#FFFFFF',
          boxShadow: '0 1px 3px 0 rgba(91, 111, 229, 0.2)',
          '&:hover': {
            backgroundColor: '#4C5FD5',
            boxShadow: '0 2px 6px 0 rgba(91, 111, 229, 0.3)',
          },
          '&:active': {
            backgroundColor: '#3D4EC5',
          },
          '&:disabled': {
            backgroundColor: '#E5E7EB',
            color: '#9CA3AF',
            boxShadow: 'none',
          },
        },
        // Outlined variant (Secondary buttons)
        outlined: {
          borderColor: '#E5E7EB',
          color: '#6B7280',
          backgroundColor: 'transparent',
          '&:hover': {
            backgroundColor: '#F9FAFB',
            borderColor: '#D1D5DB',
            color: '#1F2937',
          },
          '&:active': {
            backgroundColor: '#F3F4F6',
          },
          '&:disabled': {
            borderColor: '#E5E7EB',
            color: '#D1D5DB',
          },
        },
        // Text variant (Tertiary buttons)
        text: {
          color: '#6B7280',
          padding: '6px 12px',
          '&:hover': {
            backgroundColor: '#F9FAFB',
            color: '#1F2937',
          },
          '&:active': {
            backgroundColor: '#F3F4F6',
          },
          '&:disabled': {
            color: '#D1D5DB',
          },
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/schemas" element={<Schemas />} />
            <Route path="/knowledge-graph" element={<KnowledgeGraph />} />
            <Route path="/relationship-kg-generation" element={<RelationshipAndKGGeneration />} />
            <Route path="/landing-kpi" element={<LandingKPIManagement />} />
            <Route path="/landing-kpi/:kpiId/history" element={<KPIExecutionHistoryPage />} />
            <Route path="/dashboard-trends" element={<DashboardTrends />} />
            <Route path="/hints-management" element={<HintsManagement />} />
            <Route path="/master-page" element={<MasterPage />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
