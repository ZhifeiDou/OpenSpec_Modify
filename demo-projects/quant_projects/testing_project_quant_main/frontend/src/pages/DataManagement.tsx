import React, { useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Chip from '@mui/material/Chip';
import RefreshIcon from '@mui/icons-material/Refresh';
import { getDataStatus, updateData } from '../api/client';

const CATEGORIES = ['stock', 'futures', 'macro', 'flow'];
const CATEGORY_LABELS: Record<string, string> = {
  stock: '股票日线',
  futures: '期货日线',
  macro: '宏观指标',
  flow: '资金流向',
};

const DataManagement: React.FC = () => {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState<string | null>(null);

  const fetchStatus = () => {
    setLoading(true);
    getDataStatus().then(setStatus).finally(() => setLoading(false));
  };

  useEffect(() => { fetchStatus(); }, []);

  const handleUpdate = async (categories: string[]) => {
    const label = categories[0] === 'all' ? 'all' : categories.join(',');
    setUpdating(label);
    try {
      await updateData(categories);
      fetchStatus();
    } finally {
      setUpdating(null);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">数据管理</Typography>
        <Button
          variant="contained"
          startIcon={updating === 'all' ? <CircularProgress size={18} color="inherit" /> : <RefreshIcon />}
          onClick={() => handleUpdate(['all'])}
          disabled={!!updating}
        >
          全部更新
        </Button>
      </Box>

      <Card>
        <CardContent>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}><CircularProgress /></Box>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>数据类别</TableCell>
                    <TableCell>最后更新</TableCell>
                    <TableCell align="right">记录数</TableCell>
                    <TableCell align="right">操作</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {CATEGORIES.map((cat) => {
                    const info = status?.[cat] || {};
                    return (
                      <TableRow key={cat}>
                        <TableCell>
                          <Typography variant="body2" fontWeight={500}>
                            {CATEGORY_LABELS[cat]}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={info.last_updated || '未更新'}
                            size="small"
                            color={info.last_updated ? 'success' : 'default'}
                          />
                        </TableCell>
                        <TableCell align="right">{(info.rows || 0).toLocaleString()}</TableCell>
                        <TableCell align="right">
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => handleUpdate([cat])}
                            disabled={!!updating}
                            startIcon={updating === cat ? <CircularProgress size={14} /> : null}
                          >
                            更新
                          </Button>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default DataManagement;
