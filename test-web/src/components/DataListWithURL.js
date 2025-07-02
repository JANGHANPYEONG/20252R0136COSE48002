import React from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';

const navy = '#0F3659';

const DataList = ({ columns, data, title }) => {
  return (
    <Box sx={{ marginTop: 2 }}>
      <h3 style={{ marginBottom: 8, color: navy }}>{title}</h3>
      <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              {columns.map((col, idx) => (
                <TableCell
                  key={idx}
                  sx={{ backgroundColor: '#f5f5f5', fontWeight: 'bold', color: navy }}
                >
                  {col}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {data.length > 0 ? (
              data.map((row, ridx) => (
                <TableRow key={ridx}>
                  {columns.map((col, cidx) => {
                    const cell = row[col] ?? '';
                    // 이미지/일련번호 컬럼 클릭 시 팝업
                    if ((col === '이미지 파일명' || col === '일련번호 파일명') && cell) {
                      const urlKey = col === '이미지 파일명' ? '이미지URL' : '일련번호URL';
                      const url = row[urlKey];
                      return (
                        <TableCell
                          key={cidx}
                          sx={{ color: navy, cursor: 'pointer', textDecoration: 'underline' }}
                          onClick={() => url && window.open(url, '_blank', 'width=600,height=400')}
                        >
                          {cell}
                        </TableCell>
                      );
                    }
                    return (
                      <TableCell key={cidx}>
                        {cell || '-'}
                      </TableCell>
                    );
                  })}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} align="center">
                  데이터가 없습니다.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default DataList;