const navy = '#0F3659';

const style = {
  fixed: {
    zIndex: 1,
    borderRadius: '0',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center', // Add this line to vertically align items
    backgroundColor: 'white',
    margin: '10px 0px',
    minWidth: '720px', // 특정 픽셀 이하로 줄어들지 않도록 설정
  },
  fixedTab: {
    right: '0',
    left: '0px',
    borderRadius: '0',
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: '30px',
    borderBottom: 'solid rgba(0, 0, 0, 0.12)',
    borderBottomWidth: 'thin',
    minWidth: '720px', // 특정 픽셀 이하로 줄어들지 않도록 설정
  },
  tabBtn: {
    border: 'none',
    color: navy,
  },
  tabBtnCilcked: {
    border: `1px solid ${navy}`,
    color: navy,
  },
  titleFont: {},
};

export default style;
