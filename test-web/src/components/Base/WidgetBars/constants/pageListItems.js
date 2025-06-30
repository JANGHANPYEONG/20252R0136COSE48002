import HomeIcon from '@mui/icons-material/Home';
import DataThresholdingIcon from '@mui/icons-material/DataThresholding';
import TroubleshootIcon from '@mui/icons-material/Troubleshoot';
import StackedLineChartIcon from '@mui/icons-material/StackedLineChart';
import GroupIcon from '@mui/icons-material/Group';
import ScienceIcon from '@mui/icons-material/Science';
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
    label: '일반데이터',
    icon: <DataThresholdingIcon sx={{ fontSize: 30 }} />,
    path: '/normal',
    hasSubmenu: true,
    submenu: [
      {
        label: '대시보드',
        path: '/DataManage',
      },
      {
        label: '통계분석',
        path: '/stats',
      },
      {
        label: '데이터예측',
        path: '/PA',
      },
    ],
  },
  {
    label: '분광데이터',
    icon: <ScienceIcon sx={{ fontSize: 30 }} />,
    path: '/spectro',
    hasSubmenu: true,
    submenu: [
      {
        label: '데이터패턴분석',
        path: '/spectro/pattern',
      },
      {
        label: '분광데이터학습',
        path: '/spectro/train',
      },
      {
        label: '예측하기',
        path: '/spectro/predict',
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
