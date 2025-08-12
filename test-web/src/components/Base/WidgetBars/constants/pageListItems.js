import HomeIcon from '@mui/icons-material/Home';
import DataThresholdingIcon from '@mui/icons-material/DataThresholding';
import TroubleshootIcon from '@mui/icons-material/Troubleshoot';
import StackedLineChartIcon from '@mui/icons-material/StackedLineChart';
import GroupIcon from '@mui/icons-material/Group';
import ScienceIcon from '@mui/icons-material/Science';
import PsychologyIcon from '@mui/icons-material/Psychology';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { path } from 'd3';

const pageListItems = [
  {
    label: '홈',
    icon: <HomeIcon sx={{ fontSize: 30 }} />,
    path: '/Home',
    hasSubmenu: false,
  },
  {
    label: '데이터관리',
    icon: <DataThresholdingIcon sx={{ fontSize: 30 }} />,
    path: '/Data',
    hasSubmenu: true,
    submenu: [
      {
        label: '데이터등록',
        path: '/DataRegister',
      },
      {
        label: '대시보드',
        path: '/DashBoard',
      },
      {
        label: '통계분석',
        path: '/Stats',
      },
    ],
  },
  {
    label: 'AI 학습',
    icon: <PsychologyIcon sx={{ fontSize: 30 }} />,
    path: '/Learning/RGB',
    hasSubmenu: true,
    submenu: [
      {
        label: 'RGB',
        path: '/Learning/RGB',
      },
      {
        label: 'MSI',
        path  : '/Learning',
      },
    ],
  },
  {
    label: '예측하기',
    icon: <AutoAwesomeIcon sx={{ fontSize: 30 }} />,
    path: '/Predict/RGB',
    hasSubmenu: true,
    submenu: [
      {
        label: 'RGB',
        path: '/Predict/RGB',
      },
      {
        label: 'MSI',
        path  : '/Predict',
      },
    ],
  },
  {
    label: '사용자관리',
    icon: <GroupIcon sx={{ fontSize: 30 }} />,
    path: '/UserManagement',
    hasSubmenu: false,
  },
];

export default pageListItems;
