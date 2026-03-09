import React, { useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Plot from 'react-plotly.js';
import { getFactors, computeFactors } from '../api/client';

const Factors: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [computing, setComputing] = useState(false);

  const fetchFactors = () => {
    setLoading(true);
    getFactors().then(setData).finally(() => setLoading(false));
  };

  useEffect(() => { fetchFactors(); }, []);

  const handleCompute = async () => {
    setComputing(true);
    try {
      await computeFactors();
      fetchFactors();
    } finally {
      setComputing(false);
    }
  };

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;
  }

  const matrix = data?.matrix || [];
  const categories = data?.categories || {};

  // Build heatmap data
  const symbols = matrix.map((r: any) => r.symbol);
  const factorNames = matrix.length > 0
    ? Object.keys(matrix[0]).filter(k => k !== 'symbol')
    : [];
  const zValues = matrix.map((row: any) =>
    factorNames.map(f => typeof row[f] === 'number' ? row[f] : null)
  );

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">因子分析</Typography>
        <Button
          variant="contained"
          onClick={handleCompute}
          disabled={computing}
          startIcon={computing ? <CircularProgress size={18} color="inherit" /> : null}
        >
          {computing ? '计算中...' : '计算因子'}
        </Button>
      </Box>

      {/* Category summary */}
      {Object.keys(categories).length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 1 }}>类别均值</Typography>
            <Plot
              data={[{
                x: Object.keys(categories),
                y: Object.values(categories),
                type: 'bar',
                marker: { color: '#1976d2' },
              }]}
              layout={{
                height: 200,
                margin: { t: 10, r: 20, b: 40, l: 60 },
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
              }}
              config={{ responsive: true, displayModeBar: false }}
              style={{ width: '100%' }}
            />
          </CardContent>
        </Card>
      )}

      {/* Factor heatmap */}
      {matrix.length > 0 ? (
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 1 }}>因子热力图</Typography>
            <Plot
              data={[{
                z: zValues,
                x: factorNames,
                y: symbols,
                type: 'heatmap',
                colorscale: 'RdBu',
                reversescale: true,
              }]}
              layout={{
                height: Math.max(400, symbols.length * 25),
                margin: { t: 10, r: 20, b: 100, l: 100 },
                xaxis: { tickangle: -45 },
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
              }}
              config={{ responsive: true }}
              style={{ width: '100%' }}
            />
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 5 }}>
            <Typography color="text.secondary">暂无因子数据，点击"计算因子"开始</Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default Factors;
