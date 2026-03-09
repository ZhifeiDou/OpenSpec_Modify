import React, { useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import Chip from '@mui/material/Chip';
import Grid from '@mui/material/Grid';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Plot from 'react-plotly.js';
import { getRisk, getReport } from '../api/client';

const Risk: React.FC = () => {
  const [riskData, setRiskData] = useState<any>(null);
  const [reportData, setReportData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([getRisk(), getReport()])
      .then(([rk, rp]) => {
        if (rk.status === 'fulfilled' && !rk.value.error) setRiskData(rk.value);
        if (rp.status === 'fulfilled' && !rp.value.error) setReportData(rp.value);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;
  }

  const alerts = riskData?.alerts || [];
  const positions = riskData?.positions || [];
  const drawdownSeries = reportData?.drawdown_series || [];

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>风控监控</Typography>

      {/* Status badge */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="h6">风控状态</Typography>
            <Chip
              label={alerts.length > 0 ? `${alerts.length} 个预警` : '一切正常'}
              color={alerts.length > 0 ? 'warning' : 'success'}
              size="medium"
            />
          </Box>
          {riskData && (
            <Typography variant="body1" sx={{ mt: 1 }}>
              当前组合回撤: <strong>{((riskData.drawdown || 0) * 100).toFixed(2)}%</strong>
            </Typography>
          )}
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {/* Alerts */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>风险预警</Typography>
              {alerts.length > 0 ? (
                alerts.map((a: any, i: number) => (
                  <Alert
                    key={i}
                    severity={a.severity === 'critical' ? 'error' : 'warning'}
                    sx={{ mb: 1 }}
                  >
                    <AlertTitle>{a.type === 'stop_loss' ? '止损预警' : '金属急跌'}</AlertTitle>
                    {typeof a.detail === 'string' ? a.detail : JSON.stringify(a.detail)}
                  </Alert>
                ))
              ) : (
                <Alert severity="success">所有指标正常，无风险预警</Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Drawdown chart */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 1 }}>回撤走势</Typography>
              {drawdownSeries.length > 0 ? (
                <Plot
                  data={[{
                    x: drawdownSeries.map((d: any) => d.date),
                    y: drawdownSeries.map((d: any) => d.drawdown * 100),
                    type: 'scatter',
                    fill: 'tozeroy',
                    fillcolor: 'rgba(211,47,47,0.2)',
                    line: { color: '#d32f2f', width: 1 },
                  }]}
                  layout={{
                    height: 250,
                    margin: { t: 10, r: 20, b: 40, l: 50 },
                    yaxis: { title: '回撤 (%)' },
                    paper_bgcolor: 'transparent',
                    plot_bgcolor: 'transparent',
                  }}
                  config={{ responsive: true, displayModeBar: false }}
                  style={{ width: '100%' }}
                />
              ) : (
                <Typography color="text.secondary">暂无回撤数据</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Position risk table */}
      {positions.length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>持仓风险</Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>代码</TableCell>
                    <TableCell align="right">权重</TableCell>
                    <TableCell align="right">止损价</TableCell>
                    <TableCell align="right">距止损</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {positions.map((p: any, i: number) => (
                    <TableRow key={i} hover>
                      <TableCell>{p.symbol}</TableCell>
                      <TableCell align="right">{(p.weight * 100).toFixed(1)}%</TableCell>
                      <TableCell align="right">{p.stop_price?.toFixed(2)}</TableCell>
                      <TableCell align="right">{p.distance_to_stop?.toFixed(2)}%</TableCell>
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

export default Risk;
