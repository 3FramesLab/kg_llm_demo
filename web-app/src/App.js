import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Layout from './components/Layout';
import Overview from './pages/Overview';
import Schemas from './pages/Schemas';
import KnowledgeGraph from './pages/KnowledgeGraph';
import Execution from './pages/Execution';
import KPIManagement from './pages/KPIManagement';
import KPIResults from './pages/KPIResults';
import LandingKPIManagement from './pages/LandingKPIManagement';
import KPIDashboardPage from './pages/KPIDashboardPage';
import DashboardTrends from './pages/DashboardTrends';
import HintsManagement from './pages/HintsManagement';
import Relationships from './pages/Relationships';
import KPIExecutionHistoryPage from './pages/KPIExecutionHistoryPage';
import TableAliasesManagement from './pages/TableAliasesManagement';

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
            <Route path="/relationships" element={<Relationships />} />
            <Route path="/execution" element={<Execution />} />
            <Route path="/kpi-management" element={<KPIManagement />} />
            <Route path="/kpi-results" element={<KPIResults />} />
            <Route path="/landing-kpi" element={<LandingKPIManagement />} />
            <Route path="/landing-kpi/:kpiId/history" element={<KPIExecutionHistoryPage />} />
            <Route path="/kpi-dashboard" element={<KPIDashboardPage />} />

            <Route path="/table-aliases" element={<TableAliasesManagement />} />
            <Route path="/dashboard-trends" element={<DashboardTrends />} />
            <Route path="/hints-management" element={<HintsManagement />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
