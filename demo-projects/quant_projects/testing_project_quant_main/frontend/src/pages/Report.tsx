import React, { useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Grid from '@mui/material/Grid';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import DownloadIcon from '@mui/icons-material/Download';
import Plot from 'react-plotly.js';
import { getReport } from '../api/client';

const Report: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getReport().then(setData).finally(() => setLoading(false));
  }, []);

  const handleExport = () => {
    // Generate a simple HTML export from the current page
    const html = document.documentElement.outerHTML;
    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report_${new Date().toISOString().slice(0, 10)}.html`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;
  }

  if (data?.error) {
    return (
      <Box>
        <Typography variant="h5" sx={{ mb: 3 }}>绩效报告</Typography>
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 5 }}>
            <Typography color="text.secondary">暂无报告数据，请先运行回测</Typography>
          </CardContent>
        </Card>
      </Box>
    );
  }

  const metrics = data?.metrics || {};
  const navSeries = data?.nav_series || [];
  const drawdownSeries = data?.drawdown_series || [];
  const tradeLog = data?.trade_log || [];
  const factorExposures = data?.factor_exposures || [];

  const metricItems = [
    { label: '年化收益', value: `${((metrics.annual_return || 0) * 100).toFixed(1)}%` },
    { label: '夏普比率', value: (metrics.sharpe_ratio || 0).toFixed(2) },
    { label: '最大回撤', value: `${((metrics.max_drawdown || 0) * 100).toFixed(1)}%` },
    { label: '卡尔玛比率', value: (metrics.calmar_ratio || 0).toFixed(2) },
    { label: '胜率', value: `${((metrics.win_rate || 0) * 100).toFixed(1)}%` },
    { label: '盈亏比', value: (metrics.profit_loss_ratio || 0).toFixed(2) },
    { label: '年化波动率', value: `${((metrics.annual_volatility || 0) * 100).toFixed(1)}%` },
    { label: '总成本', value: `¥${(metrics.total_costs || 0).toLocaleString()}` },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">绩效报告</Typography>
        <Button variant="outlined" startIcon={<DownloadIcon />} onClick={handleExport}>
          导出 HTML
        </Button>
      </Box>

      {/* Metrics grid */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {metricItems.map((m) => (
          <Grid size={{ xs: 6, md: 3 }} key={m.label}>
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 2 }}>
                <Typography variant="h5" fontWeight={600}>{m.value}</Typography>
                <Typography variant="caption" color="text.secondary">{m.label}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* NAV chart */}
      {navSeries.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 1 }}>净值曲线</Typography>
            <Plot
              data={[{
                x: navSeries.map((d: any) => d.date),
                y: navSeries.map((d: any) => d.nav / navSeries[0].nav),
                type: 'scatter', mode: 'lines', name: '策略',
                line: { color: '#1976d2', width: 2 },
              }]}
              layout={{
                height: 300, margin: { t: 10, r: 20, b: 40, l: 60 },
                yaxis: { title: '净值' },
                paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
              }}
              config={{ responsive: true }}
              style={{ width: '100%' }}
            />
          </CardContent>
        </Card>
      )}

      {/* Drawdown chart */}
      {drawdownSeries.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 1 }}>回撤走势</Typography>
            <Plot
              data={[{
                x: drawdownSeries.map((d: any) => d.date),
                y: drawdownSeries.map((d: any) => d.drawdown * 100),
                type: 'scatter', fill: 'tozeroy',
                fillcolor: 'rgba(211,47,47,0.2)',
                line: { color: '#d32f2f', width: 1 },
              }]}
              layout={{
                height: 200, margin: { t: 10, r: 20, b: 40, l: 50 },
                yaxis: { title: '回撤 (%)' },
                paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
              }}
              config={{ responsive: true, displayModeBar: false }}
              style={{ width: '100%' }}
            />
          </CardContent>
        </Card>
      )}

      {/* Factor heatmap */}
      {factorExposures.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 1 }}>因子暴露</Typography>
            {(() => {
              const symbols = factorExposures.map((r: any) => r.symbol);
              const fNames = Object.keys(factorExposures[0]).filter(k => k !== 'symbol');
              const z = factorExposures.map((row: any) => fNames.map(f => row[f] || 0));
              return (
                <Plot
                  data={[{ z, x: fNames, y: symbols, type: 'heatmap', colorscale: 'RdBu', reversescale: true }]}
                  layout={{
                    height: Math.max(300, symbols.length * 25),
                    margin: { t: 10, r: 20, b: 100, l: 100 },
                    xaxis: { tickangle: -45 },
                    paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
                  }}
                  config={{ responsive: true }}
                  style={{ width: '100%' }}
                />
              );
            })()}
          </CardContent>
        </Card>
      )}

      {/* Trade log */}
      {tradeLog.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>交易记录</Typography>
            <TableContainer sx={{ maxHeight: 300 }}>
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
    </Box>
  );
};

export default Report;
