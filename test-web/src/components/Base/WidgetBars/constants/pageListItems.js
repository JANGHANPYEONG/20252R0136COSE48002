import HomeIcon from '@mui/icons-material/Home';
import DataThresholdingIcon from '@mui/icons-material/DataThresholding';
import TroubleshootIcon from '@mui/icons-material/Troubleshoot';
import StackedLineChartIcon from '@mui/icons-material/StackedLineChart';
import GroupIcon from '@mui/icons-material/Group';

const pageListItems = [
  {
    label: '홈',
    icon: <HomeIcon sx={{ fontSize: 30 }} />,
    path: '/Home',
  },
  {
    label: '대시보드',
    icon: <DataThresholdingIcon sx={{ fontSize: 30 }} />,
    path: '/DataManage',
  },
  {
    label: '데이터 예측',
    icon: <TroubleshootIcon style={{ fontSize: 30 }} />,
    path: '/PA',
  },
  {
    label: '통계 분석',
    icon: <StackedLineChartIcon sx={{ fontSize: 30 }} />,
    path: '/stats',
  },
  {
    label: '사용자 관리',
    icon: <GroupIcon sx={{ fontSize: 30 }} />,
    path: '/UserManagement',
  },
];

export default pageListItems;
