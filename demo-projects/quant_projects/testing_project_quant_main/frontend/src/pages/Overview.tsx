import React, { useEffect, useState } from 'react';
import Grid from '@mui/material/Grid';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import Plot from 'react-plotly.js';
import { getDataStatus, getLatestBacktest, getRisk } from '../api/client';

const MetricCard: React.FC<{ label: string; value: string; color?: string }> = ({ label, value, color }) => (
  <Card>
    <CardContent sx={{ textAlign: 'center', py: 3 }}>
      <Typography variant="h4" sx={{ fontWeight: 600, color: color || 'text.primary' }}>
        {value}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
        {label}
      </Typography>
    </CardContent>
  </Card>
);

const Overview: React.FC = () => {
  const [dataStatus, setDataStatus] = useState<any>(null);
  const [backtest, setBacktest] = useState<any>(null);
  const [riskData, setRiskData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([getDataStatus(), getLatestBacktest(), getRisk()])
      .then(([ds, bt, rk]) => {
        if (ds.status === 'fulfilled') setDataStatus(ds.value);
        if (bt.status === 'fulfilled' && !bt.value.error) setBacktest(bt.value);
        if (rk.status === 'fulfilled' && !rk.value.error) setRiskData(rk.value);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;
  }

  const metrics = backtest?.metrics;
  const navData = backtest?.nav_series || [];

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>系统总览</Typography>

      {/* Data freshness */}
      <Typography variant="h6" sx={{ mb: 2 }}>数据状态</Typography>
      <Grid container spacing={2} sx={{ mb: 4 }}>
        {dataStatus && Object.entries(dataStatus).map(([cat, info]: [string, any]) => (
          <Grid size={{ xs: 6, md: 3 }} key={cat}>
            <Card>
              <CardContent>
                <Typography variant="subtitle2" color="text.secondary">{cat}</Typography>
                <Chip
                  label={info.last_updated || '未更新'}
                  size="small"
                  color={info.last_updated ? 'success' : 'default'}
                  sx={{ mt: 1 }}
                />
                <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                  {info.rows.toLocaleString()} 条记录
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Key metrics */}
      {metrics && (
        <>
          <Typography variant="h6" sx={{ mb: 2 }}>绩效指标</Typography>
          <Grid container spacing={2} sx={{ mb: 4 }}>
            <Grid size={{ xs: 6, md: 3 }}>
              <MetricCard label="年化收益" value={`${(metrics.annual_return * 100).toFixed(1)}%`}
                color={metrics.annual_return >= 0 ? '#d32f2f' : '#388e3c'} />
            </Grid>
            <Grid size={{ xs: 6, md: 3 }}>
              <MetricCard label="夏普比率" value={metrics.sharpe_ratio?.toFixed(2) || 'N/A'} />
            </Grid>
            <Grid size={{ xs: 6, md: 3 }}>
              <MetricCard label="最大回撤" value={`${(metrics.max_drawdown * 100).toFixed(1)}%`} color="#f57c00" />
            </Grid>
            <Grid size={{ xs: 6, md: 3 }}>
              <MetricCard label="胜率" value={`${(metrics.win_rate * 100).toFixed(1)}%`} />
            </Grid>
          </Grid>
        </>
      )}

      {/* Risk status */}
      {riskData && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 1 }}>风控状态</Typography>
            <Chip
              label={riskData.alerts?.length > 0 ? `${riskData.alerts.length} 个预警` : '一切正常'}
              color={riskData.alerts?.length > 0 ? 'warning' : 'success'}
            />
            <Typography variant="body2" sx={{ mt: 1 }}>
              当前回撤: {((riskData.drawdown || 0) * 100).toFixed(2)}%
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Mini NAV chart */}
      {navData.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 1 }}>净值走势</Typography>
            <Plot
              data={[{
                x: navData.map((d: any) => d.date),
                y: navData.map((d: any) => d.nav / navData[0].nav),
                type: 'scatter',
                mode: 'lines',
                line: { color: '#1976d2', width: 2 },
              }]}
              layout={{
                height: 300,
                margin: { t: 10, r: 20, b: 40, l: 60 },
                xaxis: { title: '' },
                yaxis: { title: '净值' },
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
              }}
              config={{ responsive: true, displayModeBar: false }}
              style={{ width: '100%' }}
            />
          </CardContent>
        </Card>
      )}

      {!metrics && !navData.length && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 5 }}>
            <Typography variant="h6" color="text.secondary">尚无回测数据</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              前往"回测"页面运行回测，或先在"数据管理"中更新数据
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default Overview;
