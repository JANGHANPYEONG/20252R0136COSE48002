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
      {
        label: 'XAI',
        path: '/XAI',
      },
    ],
  },
  {
    label: 'AI 학습',
    icon: <PsychologyIcon sx={{ fontSize: 30 }} />,
    path: '/Learning',
    hasSubmenu: false,
  },
  {
    label: '예측하기',
    icon: <AutoAwesomeIcon sx={{ fontSize: 30 }} />,
    path: '/Predict',
    hasSubmenu: false,
  },
  {
    label: '사용자관리',
    icon: <GroupIcon sx={{ fontSize: 30 }} />,
    path: '/UserManagement',
    hasSubmenu: false,
  },
];

export default pageListItems;
