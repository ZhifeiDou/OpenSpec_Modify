import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme';
import Layout from './components/Layout';
import Overview from './pages/Overview';
import DataManagement from './pages/DataManagement';
import Universe from './pages/Universe';
import Factors from './pages/Factors';
import Signals from './pages/Signals';
import Risk from './pages/Risk';
import Backtest from './pages/Backtest';
import Report from './pages/Report';

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/data" element={<DataManagement />} />
            <Route path="/universe" element={<Universe />} />
            <Route path="/factors" element={<Factors />} />
            <Route path="/signals" element={<Signals />} />
            <Route path="/risk" element={<Risk />} />
            <Route path="/backtest" element={<Backtest />} />
            <Route path="/report" element={<Report />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </ThemeProvider>
  );
};

export default App;
