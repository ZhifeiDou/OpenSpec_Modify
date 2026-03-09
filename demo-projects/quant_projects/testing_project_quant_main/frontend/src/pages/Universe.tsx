import React, { useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import CircularProgress from '@mui/material/CircularProgress';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Grid from '@mui/material/Grid';
import Plot from 'react-plotly.js';
import { getUniverse } from '../api/client';

const Universe: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    getUniverse().then(setData).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;
  }

  const stocks = data?.stocks || [];
  const subsectorCounts = data?.subsector_counts || {};
  const filtered = stocks.filter((s: any) =>
    s.symbol?.includes(filter) || s.name?.includes(filter) || s.subsector?.includes(filter)
  );

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>股票池</Typography>

      <Grid container spacing={3}>
        {/* Pie chart */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 1 }}>子行业分布</Typography>
              {Object.keys(subsectorCounts).length > 0 ? (
                <Plot
                  data={[{
                    labels: Object.keys(subsectorCounts),
                    values: Object.values(subsectorCounts),
                    type: 'pie',
                    hole: 0.4,
                    textinfo: 'label+value',
                  }]}
                  layout={{
                    height: 300,
                    margin: { t: 10, r: 10, b: 10, l: 10 },
                    showlegend: false,
                    paper_bgcolor: 'transparent',
                  }}
                  config={{ responsive: true, displayModeBar: false }}
                  style={{ width: '100%' }}
                />
              ) : (
                <Typography color="text.secondary">暂无数据</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Stock table */}
        <Grid size={{ xs: 12, md: 8 }}>
          <Card>
            <CardContent>
              <TextField
                placeholder="搜索股票代码、名称或子行业..."
                size="small"
                fullWidth
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                sx={{ mb: 2 }}
              />
              <TableContainer sx={{ maxHeight: 500 }}>
                <Table stickyHeader size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>代码</TableCell>
                      <TableCell>名称</TableCell>
                      <TableCell>子行业</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filtered.map((s: any) => (
                      <TableRow key={s.symbol} hover>
                        <TableCell>{s.symbol}</TableCell>
                        <TableCell>{s.name}</TableCell>
                        <TableCell>{s.subsector}</TableCell>
                      </TableRow>
                    ))}
                    {filtered.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={3} align="center">
                          <Typography color="text.secondary">无匹配结果</Typography>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                共 {filtered.length} / {stocks.length} 只股票
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Universe;
