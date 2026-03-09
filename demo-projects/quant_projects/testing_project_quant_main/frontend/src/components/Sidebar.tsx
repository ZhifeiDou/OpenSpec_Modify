import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import DashboardIcon from '@mui/icons-material/Dashboard';
import StorageIcon from '@mui/icons-material/Storage';
import GroupWorkIcon from '@mui/icons-material/GroupWork';
import InsightsIcon from '@mui/icons-material/Insights';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import ShieldIcon from '@mui/icons-material/Shield';
import TimelineIcon from '@mui/icons-material/Timeline';
import AssessmentIcon from '@mui/icons-material/Assessment';

const navItems = [
  { label: '总览', path: '/', icon: <DashboardIcon /> },
  { label: '数据管理', path: '/data', icon: <StorageIcon /> },
  { label: '股票池', path: '/universe', icon: <GroupWorkIcon /> },
  { label: '因子分析', path: '/factors', icon: <InsightsIcon /> },
  { label: '交易信号', path: '/signals', icon: <TrendingUpIcon /> },
  { label: '风控监控', path: '/risk', icon: <ShieldIcon /> },
  { label: '回测', path: '/backtest', icon: <TimelineIcon /> },
  { label: '报告', path: '/report', icon: <AssessmentIcon /> },
];

const Sidebar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <List sx={{ pt: 1 }}>
      {navItems.map((item) => (
        <ListItemButton
          key={item.path}
          selected={location.pathname === item.path}
          onClick={() => navigate(item.path)}
          sx={{
            mx: 1,
            borderRadius: 2,
            mb: 0.5,
            '&.Mui-selected': {
              backgroundColor: 'primary.main',
              color: 'white',
              '& .MuiListItemIcon-root': { color: 'white' },
              '&:hover': { backgroundColor: 'primary.dark' },
            },
          }}
        >
          <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
          <ListItemText primary={item.label} />
        </ListItemButton>
      ))}
    </List>
  );
};

export default Sidebar;
