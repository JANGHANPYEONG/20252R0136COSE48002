import { Stack, Button } from '@mui/material';
import PropTypes from 'prop-types';
//데이터 상태 컴포넌트
const OrderStatus = ({ status }) => {
  let color;
  let title;
  let backgroundColor;

  switch (status) {
    case 0:
      backgroundColor = '#ffcdd2';
      color = '#e53935';
      title = '반려';
      break;
    case 1:
      backgroundColor = '#b9f6ca';
      color = '#00e676';
      title = '승인';
      break;
    case 2:
      backgroundColor = '#bcaaa4';
      color = '#5d4037';
      title = '대기';
      break;
    default:
      color = 'primary';
      title = 'None';
  }

  return (
    <Stack direction="row" spacing={1} alignItems="center">
      <Button
        style={{
          backgroundColor: backgroundColor,
          height: '30px',
          width: '35px',
          borderRadius: '10px',
        }}
      >
        <span
          style={{
            color: color,
            fontSize: '15px',
            fontWeight: '600',
            padding: '5px',
          }}
        >
          {title}
        </span>
      </Button>
    </Stack>
  );
};

OrderStatus.propTypes = {
  status: PropTypes.number,
};
export default OrderStatus;
