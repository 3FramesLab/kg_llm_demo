import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Schemas from './pages/Schemas';
import KnowledgeGraph from './pages/KnowledgeGraph';
import Reconciliation from './pages/Reconciliation';
import NaturalLanguage from './pages/NaturalLanguage';
import Execution from './pages/Execution';
import KPIManagement from './pages/KPIManagement';
import KPIResults from './pages/KPIResults';

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
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/schemas" element={<Schemas />} />
            <Route path="/knowledge-graph" element={<KnowledgeGraph />} />
            <Route path="/reconciliation" element={<Reconciliation />} />
            <Route path="/natural-language" element={<NaturalLanguage />} />
            <Route path="/execution" element={<Execution />} />
            <Route path="/kpi-management" element={<KPIManagement />} />
            <Route path="/kpi-results" element={<KPIResults />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
