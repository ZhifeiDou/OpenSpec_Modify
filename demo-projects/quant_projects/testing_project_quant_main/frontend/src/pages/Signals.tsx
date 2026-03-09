import React, { useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Chip from '@mui/material/Chip';
import Collapse from '@mui/material/Collapse';
import IconButton from '@mui/material/IconButton';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import Plot from 'react-plotly.js';
import { getSignals } from '../api/client';

const signalColor: Record<string, 'success' | 'default' | 'error'> = {
  buy: 'success',
  hold: 'default',
  sell: 'error',
};
const signalLabel: Record<string, string> = {
  buy: '买入',
  hold: '持有',
  sell: '卖出',
};

const SignalRow: React.FC<{ sig: any }> = ({ sig }) => {
  const [open, setOpen] = useState(false);
  const contributions = sig.factor_contributions || {};
  const contribKeys = Object.keys(contributions);

  return (
    <>
      <TableRow hover>
        <TableCell>
          {contribKeys.length > 0 && (
            <IconButton size="small" onClick={() => setOpen(!open)}>
              {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
            </IconButton>
          )}
        </TableCell>
        <TableCell>{sig.symbol}</TableCell>
        <TableCell>{sig.name}</TableCell>
        <TableCell align="right">{sig.score?.toFixed(3)}</TableCell>
        <TableCell>
          <Chip label={signalLabel[sig.signal] || sig.signal} size="small" color={signalColor[sig.signal] || 'default'} />
        </TableCell>
        <TableCell align="right">{(sig.target_weight * 100).toFixed(1)}%</TableCell>
        <TableCell>{sig.sentiment_label || '-'}</TableCell>
      </TableRow>
      {contribKeys.length > 0 && (
        <TableRow>
          <TableCell colSpan={7} sx={{ py: 0, borderBottom: open ? undefined : 'none' }}>
            <Collapse in={open} timeout="auto" unmountOnExit>
              <Box sx={{ py: 2, px: 4 }}>
                <Plot
                  data={[{
                    y: contribKeys,
                    x: contribKeys.map(k => contributions[k]),
                    type: 'bar',
                    orientation: 'h',
                    marker: {
                      color: contribKeys.map(k => contributions[k] >= 0 ? '#1976d2' : '#d32f2f'),
                    },
                  }]}
                  layout={{
                    height: Math.max(150, contribKeys.length * 25),
                    margin: { t: 5, r: 20, b: 20, l: 150 },
                    paper_bgcolor: 'transparent',
                    plot_bgcolor: 'transparent',
                  }}
                  config={{ responsive: true, displayModeBar: false }}
                  style={{ width: '100%' }}
                />
              </Box>
            </Collapse>
          </TableCell>
        </TableRow>
      )}
    </>
  );
};

const Signals: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSignals().then(setData).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;
  }

  const signals = data?.signals || [];

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>交易信号</Typography>
      <Card>
        <CardContent>
          {signals.length > 0 ? (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell width={50} />
                    <TableCell>代码</TableCell>
                    <TableCell>名称</TableCell>
                    <TableCell align="right">综合得分</TableCell>
                    <TableCell>信号</TableCell>
                    <TableCell align="right">目标权重</TableCell>
                    <TableCell>情绪</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {signals.map((sig: any) => (
                    <SignalRow key={sig.symbol} sig={sig} />
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Box sx={{ textAlign: 'center', py: 5 }}>
              <Typography color="text.secondary">暂无交易信号，请先生成信号</Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default Signals;
