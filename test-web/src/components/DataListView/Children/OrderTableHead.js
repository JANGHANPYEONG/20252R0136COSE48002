import PropTypes from 'prop-types';
import { TableHead, TableRow, TableCell, Checkbox, Button, Divider } from '@mui/material';

// 테이블 헤더 컴포넌트
const OrderTableHead = ({
  pageProp,
  order,
  orderBy,
  headCells,
  meatList,
  checkItems,
  totalPages,
  handleAllCheck,
  handleTableHeaderDeleteBtn,
}) => {
  return (
    <TableHead>
      {pageProp === 'reject' && (
        <TableRow
          style={{
            padding: '0px',
            display: 'flex',
            alignItems: 'center',
            width: '100%',
          }}
        >
          <div
            key={'checkbox'}
            align="center"
            padding="none"
            style={{
              padding: '0px',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <Checkbox
              checked={checkItems.length === meatList.length}
              label="전체선택"
              labelPlacement="top"
              onChange={(e) => handleAllCheck(e.target.checked)}
              inputProps={{ 'aria-label': 'controlled' }}
              style={style.tableDelHeader}
            />
            <span style={{ fontSize: '12px', fontWeight: '600' }}>
              전체선택 &#40;{checkItems.length}/{totalPages}&#41;
            </span>
          </div>
          <Divider
            orientation="vertical"
            flexItem
            variant="middle"
            style={{
              background: 'black',
              width: '2px',
              margin: '7px 10px',
            }}
          />
          <div style={{ padding: '0px' }}>
            <Button
              onClick={handleTableHeaderDeleteBtn}
              style={style.tableDelHeader}
            >
              <span style={{ fontSize: '12px', fontWeight: '600' }}>
                선택삭제
              </span>
            </Button>
          </div>
        </TableRow>
      )}
      <TableRow>
        {pageProp === 'reject' && (
          <TableCell
            key={'checkbox'}
            align="center"
            padding="none"
            style={{}}
          ></TableCell>
        )}
        {headCells.map((headCell) => (
          <TableCell
            key={headCell.meatId}
            align={headCell.align}
            padding={headCell.disablePadding ? 'none' : 'none'}
            sortDirection={orderBy === headCell.meatId ? order : false}
          >
            <div key={headCell.meatId} style={style.tableHeader}>
              {headCell.label}
            </div>
          </TableCell>
        ))}
      </TableRow>
    </TableHead>
  );
};

OrderTableHead.propTypes = {
  pageProp: PropTypes.string.isRequired,
  order: PropTypes.string,
  orderBy: PropTypes.string,
  headCells: PropTypes.array.isRequired,
  meatList: PropTypes.array.isRequired,
  checkItems: PropTypes.array.isRequired,
  totalPages: PropTypes.number.isRequired,
  handleAllCheck: PropTypes.func.isRequired,
  handleTableHeaderDeleteBtn: PropTypes.func.isRequired,
};

export default OrderTableHead;

const style = {
  tableDelHeader: {
    display: 'flex',
    alignItems: 'center',
    padding: '6px',
    fontWeight: '600',
    color: 'black',
  },
  tableHeader: {
    display: 'flex',
    alignItems: 'center',
    padding: '6px',
    fontWeight: '600',
    color: '#90a4ae',
  },
};
