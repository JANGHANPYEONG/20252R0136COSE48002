import React, { useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Link,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Checkbox,
  IconButton,
} from '@mui/material';
import { FaRegTrashAlt } from 'react-icons/fa';
import DelWarningModal from './Children/DelWarningModal';
import OrderTableHead from './Children/OrderTableHead'; // 분리된 컴포넌트 임포트
import OrderStatus from './Children/OrderStatus';
import style from './style/dataliststyle';
import headCells from './constants/headCells';

const DataList = ({
  meatList,
  pageProp,
  offset,
  count,
  totalPages,
  startDate,
  endDate,
  pageOffset,
}) => {
  const [isDelClick, setIsDelClick] = useState(false);
  const [checkItems, setCheckItems] = useState([]);
  const [selected] = useState([]);
  const isSelected = (trackingNo) => selected.indexOf(trackingNo) !== -1;

  const handleTableCellDelete = (id) => {
    let idArr = [];
    idArr.push(id);
    setCheckItems(idArr);
    setIsDelClick(true);
  };

  const handleTableHeaderDeleteBtn = () => {
    setIsDelClick(true);
  };

  const handleSingleCheck = (checked, id) => {
    if (checked) {
      setCheckItems([...checkItems, id]);
    } else {
      setCheckItems(checkItems.filter((el) => el !== id));
    }
  };

  const handleAllCheck = (checked) => {
    if (checked) {
      const idArray = [];
      meatList.forEach((el) => idArray.push(el.meatId));
      setCheckItems(idArray);
    } else {
      setCheckItems([]);
    }
  };

  return (
    <Box
      style={{ backgroundColor: 'white', borderRadius: '5px', height: '100%' }}
    >
      <TableContainer
        sx={{
          width: '100%',
          overflowX: 'auto',
          position: 'relative',
          display: 'block',
          maxWidth: '100%',
          '& td, & th': { whiteSpace: 'nowrap' },
          padding: '10px',
          boxShadow: 1,
          borderRadius: '5px',
          height: 'auto',
        }}
      >
        <Table
          aria-labelledby="tableTitle"
          sx={{
            '& .MuiTableCell-root:first-of-type': { pl: 2 },
            '& .MuiTableCell-root:last-of-type': { pr: 3 },
          }}
        >
          <OrderTableHead
            pageProp={pageProp}
            order="asc"
            orderBy="trackingNo"
            headCells={headCells}
            meatList={meatList}
            checkItems={checkItems}
            totalPages={totalPages}
            handleAllCheck={handleAllCheck}
            handleTableHeaderDeleteBtn={handleTableHeaderDeleteBtn}
          />

          <TableBody>
            {meatList.map((content, index) => {
              const isItemSelected = isSelected(content);
              const labelId = `enhanced-table-checkbox-${index}`;
              return (
                <TableRow
                  hover
                  role="checkbox"
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                  aria-checked={isItemSelected}
                  tabIndex={-1}
                  key={index}
                  selected={isItemSelected}
                >
                  {pageProp === 'reject' && (
                    <TableCell style={style.tableCell}>
                      <Checkbox
                        value={content.meatId}
                        key={content.meatId}
                        checked={checkItems.includes(content.meatId)}
                        onChange={(e) =>
                          handleSingleCheck(e.target.checked, content.meatId)
                        }
                        inputProps={{ 'aria-label': 'controlled' }}
                      />
                    </TableCell>
                  )}
                  <TableCell
                    component="th"
                    id={labelId}
                    scope="row"
                    align="center"
                    style={style.tableCell}
                  >
                    {index + 1 + offset * count}
                  </TableCell>
                  <TableCell style={style.tableCell}>
                    <Link
                      color="#000000"
                      component={RouterLink}
                      style={{ textDecorationLine: 'none' }}
                      to={
                        pageProp === 'pa'
                          ? {
                              pathname: `/dataPA/${content.meatId}`,
                              search: `?pageOffset=${offset}&start=${startDate}&end=${endDate}`,
                            }
                          : (pageProp === 'list' || 'reject') &&
                              (content.statusType === '대기중' ||
                                content.statusType === '반려')
                            ? {
                                pathname: `/DataConfirm/${content.meatId}`,
                                search: `?pageOffset=${offset}&start=${startDate}&end=${endDate}`,
                              }
                            : {
                                pathname: `/dataView/${content.meatId}`,
                                search: `?pageOffset=${offset}&start=${startDate}&end=${endDate}`,
                              }
                      }
                    >
                      {content.meatId}
                    </Link>
                  </TableCell>
                  <TableCell style={style.tableCell}>
                    {content.farmAddr ? content.farmAddr : '-'}
                  </TableCell>
                  <TableCell style={style.tableCell}>
                    {content.userName}
                  </TableCell>
                  <TableCell style={style.tableCell}>
                    {' '}
                    {content.userType}{' '}
                  </TableCell>
                  <TableCell style={style.tableCell}>
                    {' '}
                    {content.company}{' '}
                  </TableCell>
                  <TableCell style={style.tableCell}>
                    {' '}
                    {content.createdAt.replace('T', ' ')}{' '}
                  </TableCell>
                  <TableCell style={style.tableCell}>
                    {content.statusType === '반려' && (
                      <OrderStatus status={0} />
                    )}
                    {content.statusType === '승인' && (
                      <OrderStatus status={1} />
                    )}
                    {content.statusType === '대기중' && (
                      <OrderStatus status={2} />
                    )}
                  </TableCell>
                  <TableCell style={style.tableCell}>
                    <IconButton
                      aria-label="delete"
                      color="#90a4ae"
                      onClick={() => handleTableCellDelete(content.meatId)}
                    >
                      <FaRegTrashAlt />
                    </IconButton>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
      {isDelClick && (
        <DelWarningModal
          idArr={checkItems}
          setIsDelClick={setIsDelClick}
          pageOffset={pageOffset}
          startDate={startDate}
          endDate={endDate}
        />
      )}
    </Box>
  );
};

export default DataList;
