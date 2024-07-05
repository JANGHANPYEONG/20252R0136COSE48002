import ArrowDownOnSquareIcon from '@heroicons/react/24/solid/ArrowDownOnSquareIcon';
import { Box, Button, SvgIcon } from '@mui/material';

const navy = '#0F3659';

// 통계 export 버튼 컴포넌트
function StatsExport() {
  return (
    <Box>
      <Button
        style={{
          color: navy,
          backgroundColor: 'white',
          border: `1px solid ${navy}`,
          height: '35px',
          borderRadius: '10px',
        }}
        onClick={() => {}}
      >
        <div style={{ display: 'flex' }}>
          <SvgIcon fontSize="small">
            <ArrowDownOnSquareIcon />
          </SvgIcon>
          <span>Export</span>
        </div>
      </Button>
    </Box>
  );
}

export default StatsExport;
