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
