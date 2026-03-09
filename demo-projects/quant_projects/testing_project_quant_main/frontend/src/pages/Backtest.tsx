import React, { useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import CircularProgress from '@mui/material/CircularProgress';
import Grid from '@mui/material/Grid';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Plot from 'react-plotly.js';
import { runBacktest, getLatestBacktest } from '../api/client';

const MetricCard: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <Card>
    <CardContent sx={{ textAlign: 'center', py: 2 }}>
      <Typography variant="h5" fontWeight={600}>{value}</Typography>
      <Typography variant="caption" color="text.secondary">{label}</Typography>
    </CardContent>
  </Card>
);

const Backtest: React.FC = () => {
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2025-12-31');
  const [capital, setCapital] = useState('1000000');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [initialLoad, setInitialLoad] = useState(true);

  useEffect(() => {
    getLatestBacktest()
      .then((data) => { if (!data.error) setResult(data); })
      .finally(() => setInitialLoad(false));
  }, []);

  const handleRun = async () => {
    setLoading(true);
    try {
      const data = await runBacktest(startDate, endDate, parseFloat(capital));
      if (!data.error) setResult(data);
    } finally {
      setLoading(false);
    }
  };

  if (initialLoad) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;
  }

  const metrics = result?.metrics;
  const navData = result?.nav_series || [];
  const tradeLog = result?.trade_log || [];

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>回测</Typography>

      {/* Parameters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>回测参数</Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'end' }}>
            <TextField label="开始日期" type="date" value={startDate} onChange={e => setStartDate(e.target.value)}
              size="small" InputLabelProps={{ shrink: true }} />
            <TextField label="结束日期" type="date" value={endDate} onChange={e => setEndDate(e.target.value)}
              size="small" InputLabelProps={{ shrink: true }} />
            <TextField label="初始资金" value={capital} onChange={e => setCapital(e.target.value)}
              size="small" sx={{ width: 150 }} />
            <Button variant="contained" onClick={handleRun} disabled={loading}
              startIcon={loading ? <CircularProgress size={18} color="inherit" /> : null}>
              {loading ? '运行中...' : '运行回测'}
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Results */}
      {metrics && (
        <>
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid size={{ xs: 6, md: 3 }}><MetricCard label="年化收益" value={`${(metrics.annual_return * 100).toFixed(1)}%`} /></Grid>
            <Grid size={{ xs: 6, md: 3 }}><MetricCard label="夏普比率" value={metrics.sharpe_ratio?.toFixed(2)} /></Grid>
            <Grid size={{ xs: 6, md: 3 }}><MetricCard label="最大回撤" value={`${(metrics.max_drawdown * 100).toFixed(1)}%`} /></Grid>
            <Grid size={{ xs: 6, md: 3 }}><MetricCard label="胜率" value={`${(metrics.win_rate * 100).toFixed(1)}%`} /></Grid>
          </Grid>

          {/* NAV chart */}
          {navData.length > 0 && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 1 }}>净值曲线</Typography>
                <Plot
                  data={[{
                    x: navData.map((d: any) => d.date),
                    y: navData.map((d: any) => d.nav / navData[0].nav),
                    type: 'scatter',
                    mode: 'lines',
                    name: '策略净值',
                    line: { color: '#1976d2', width: 2 },
                  }]}
                  layout={{
                    height: 350,
                    margin: { t: 10, r: 20, b: 40, l: 60 },
                    yaxis: { title: '净值' },
                    paper_bgcolor: 'transparent',
                    plot_bgcolor: 'transparent',
                    showlegend: true,
                    legend: { x: 0, y: 1 },
                  }}
                  config={{ responsive: true }}
                  style={{ width: '100%' }}
                />
              </CardContent>
            </Card>
          )}

          {/* Trade log */}
          {tradeLog.length > 0 && (
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>交易记录</Typography>
                <TableContainer sx={{ maxHeight: 400 }}>
                  <Table size="small" stickyHeader>
                    <TableHead>
                      <TableRow>
                        <TableCell>日期</TableCell>
                        <TableCell>代码</TableCell>
                        <TableCell>操作</TableCell>
                        <TableCell align="right">价格</TableCell>
                        <TableCell align="right">数量</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {tradeLog.map((t: any, i: number) => (
                        <TableRow key={i} hover>
                          <TableCell>{t.date}</TableCell>
                          <TableCell>{t.symbol}</TableCell>
                          <TableCell>{t.action}</TableCell>
                          <TableCell align="right">{t.price?.toFixed(2)}</TableCell>
                          <TableCell align="right">{t.quantity}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          )}
        </>
      )}

      {!metrics && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 5 }}>
            <Typography color="text.secondary">设置参数并点击"运行回测"开始</Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default Backtest;
